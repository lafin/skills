#!/usr/bin/env python3
"""Measure OMP's runtime skill catalog with matched no-skill controls."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable


def _load_runner():
    path = Path(__file__).with_name("run.py")
    spec = importlib.util.spec_from_file_location("catalog_probe_runner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{path}: cannot import RPC runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RUNNER = _load_runner()
DEFAULT_PROMPTS = (
    {
        "id": "catalog-routing-boundary",
        "prompt": "Choose the single best available skill for reducing context token cost without lowering answer quality. Respond only with the skill name.",
    },
)
INPUT_TOKEN_KEYS = ("inputTokens", "promptTokens", "input_tokens", "prompt_tokens")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def repository_catalog(root: Path) -> list[dict[str, str]]:
    records = [
        {
            "description": RUNNER.skill_description(path),
            "name": f"skill:{path.parent.name}",
        }
        for path in sorted(root.glob("*/SKILL.md"), key=lambda item: item.parent.name)
    ]
    if not records:
        raise ValueError(f"{root}: no root skill directories containing SKILL.md")
    return records


def serialize_catalog(records: list[dict[str, Any]]) -> str:
    if not records or any(not isinstance(item, dict) for item in records):
        raise ValueError("catalog: expected a non-empty array of command objects")
    return canonical_json(records)


def runtime_catalog(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    updates = [event.get("commands") for event in events if event.get("type") == "available_commands_update"]
    if not updates:
        raise ValueError("OMP RPC stream: missing available_commands_update catalog event")
    commands = updates[-1]
    if not isinstance(commands, list):
        raise ValueError("OMP RPC stream: available_commands_update.commands must be an array")
    catalog = [item for item in commands if isinstance(item, dict) and str(item.get("name", "")).startswith("skill:")]
    return catalog, serialize_catalog(catalog)


def request_payload_hash(
    prompt: dict[str, str], *, model: str, profile: str, thinking: str, max_time: str,
    tools: list[str], configs: list[str], system_prompt: str,
) -> str:
    payload = {
        "configs": configs,
        "max_time": max_time,
        "model": model,
        "profile": profile,
        "rpc_request": {"type": "prompt", "message": prompt["prompt"]},
        "system_prompt": system_prompt,
        "thinking": thinking,
        "tools": tools,
    }
    return sha256_text(canonical_json(payload))


def matched_payload_hash(full_hash: str, control_hash: str) -> str:
    if full_hash != control_hash:
        raise ValueError(
            "matched control: non-catalog request payload differs; use the same prompt, model, profile, tools, configs, thinking, max-time, and system prompt"
        )
    return full_hash


def input_tokens(usage: Any) -> int | None:
    if not isinstance(usage, dict):
        return None
    for key in INPUT_TOKEN_KEYS:
        value = usage.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    for value in usage.values():
        found = input_tokens(value)
        if found is not None:
            return found
    return None


def token_attribution(full_usage: Any, control_usage: Any, payloads_match: bool) -> dict[str, Any]:
    full = input_tokens(full_usage)
    control = input_tokens(control_usage)
    if not payloads_match:
        return {
            "status": "unavailable",
            "reason": "non-catalog request payload hashes differ",
            "full_input_tokens": full,
            "control_input_tokens": control,
            "catalog_input_tokens": None,
            "claim_eligible": False,
        }
    if full is None or control is None:
        return {
            "status": "unavailable",
            "reason": "OMP did not report attributable input-token usage for both requests",
            "full_input_tokens": full,
            "control_input_tokens": control,
            "catalog_input_tokens": None,
            "claim_eligible": False,
        }
    if full < control:
        return {
            "status": "unavailable",
            "reason": "reported full-request input tokens are smaller than the matched control",
            "full_input_tokens": full,
            "control_input_tokens": control,
            "catalog_input_tokens": None,
            "claim_eligible": False,
        }
    return {
        "status": "available",
        "reason": None,
        "full_input_tokens": full,
        "control_input_tokens": control,
        "catalog_input_tokens": full - control,
        "claim_eligible": True,
    }


def run_order(pair_count: int) -> list[str]:
    if pair_count < 1:
        raise ValueError("pair_count must be positive")
    return ["AB" if index % 2 == 0 else "BA" for index in range(pair_count)]


def bootstrap_median_ci(values: list[float], seed: int, resamples: int = 10_000) -> tuple[float, float]:
    if not values:
        raise ValueError("bootstrap values must not be empty")
    if resamples < 1:
        raise ValueError("bootstrap resamples must be positive")
    rng = random.Random(seed)
    size = len(values)
    medians = sorted(
        statistics.median(values[rng.randrange(size)] for _ in range(size))
        for _ in range(resamples)
    )
    lower = medians[int(0.025 * (resamples - 1))]
    upper = medians[int(0.975 * (resamples - 1))]
    return lower, upper


def git_revision(root: Path) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=False
    )
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and len(value) == 40 else None


def build_command(args: argparse.Namespace, root: Path, skills: list[str] | None) -> list[str]:
    command = [
        args.omp,
        "--mode=rpc",
        "--no-rules",
        "--no-session",
        "--no-extensions",
        f"--cwd={root}",
        f"--model={args.model}",
        f"--thinking={args.thinking}",
        f"--max-time={args.max_time}",
        f"--system-prompt={RUNNER.ROUTING_SYSTEM_PROMPT}",
        f"--profile={args.profile}",
        *(f"--config={path}" for path in args.config),
        f"--tools={args.tools}" if args.tools else "--no-tools",
    ]
    command.append(f"--skills={','.join(skills)}" if skills else "--no-skills")
    return command


def capture_once(
    args: argparse.Namespace,
    root: Path,
    prompt: dict[str, str],
    skills: list[str] | None,
    capture: Callable[..., tuple[int, str, str, list[dict[str, Any]], list[str], dict[str, Any]]] = RUNNER.rpc_capture,
) -> dict[str, Any]:
    request = {"id": f"probe-{prompt['id']}", "type": "prompt", "message": prompt["prompt"]}
    started = time.monotonic()
    code, _stdout, stderr, events, errors, terminal = capture(
        build_command(args, root, skills), root, [request], RUNNER.seconds(args.max_time) + 30
    )
    elapsed_ms = (time.monotonic() - started) * 1000
    if code or errors or not terminal.get("received"):
        detail = "; ".join(errors) or stderr.strip() or f"exit code {code}"
        raise RuntimeError(f"{root}: OMP RPC probe failed: {detail}")
    summary = RUNNER.summarize_events(events)
    catalog: list[dict[str, Any]] = []
    serialized = "[]"
    if skills is not None:
        catalog, serialized = runtime_catalog(events)
        observed = sorted(str(item.get("name", "")).removeprefix("skill:") for item in catalog)
        if observed != sorted(skills):
            raise ValueError(
                f"{root}: runtime catalog names {observed!r} do not match requested root inventory {sorted(skills)!r}; correct the profile/custom-directory configuration"
            )
    return {
        "elapsed_ms": elapsed_ms,
        "usage": summary["usage"],
        "catalog": catalog,
        "serialized_catalog": serialized,
        "catalog_sha256": sha256_text(serialized),
        "catalog_bytes": len(serialized.encode("utf-8")),
    }


def load_prompts(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return list(DEFAULT_PROMPTS)
    prompts: list[dict[str, str]] = []
    seen: set[str] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict) or set(value) != {"id", "prompt"} or not all(
            isinstance(value[name], str) and value[name] for name in ("id", "prompt")
        ):
            raise ValueError(f"{path}:{number}: expected exactly non-empty string fields id and prompt")
        if value["id"] in seen:
            raise ValueError(f"{path}:{number}: duplicate prompt id {value['id']!r}; use a unique id")
        seen.add(value["id"])
        prompts.append(value)
    if not prompts:
        raise ValueError(f"{path}: prompt set is empty")
    return prompts


def compare(args: argparse.Namespace) -> dict[str, Any]:
    roots = {"baseline": args.baseline_root.resolve(), "treatment": args.treatment_root.resolve()}
    inventories = {
        arm: [record["name"].removeprefix("skill:") for record in repository_catalog(root)]
        for arm, root in roots.items()
    }
    prompts = load_prompts(args.prompts)
    tools = [] if not args.tools else args.tools.split(",")
    payload_hashes = {
        prompt["id"]: request_payload_hash(
            prompt,
            model=args.model,
            profile=args.profile,
            thinking=args.thinking,
            max_time=args.max_time,
            tools=tools,
            configs=[str(path) for path in args.config],
            system_prompt=RUNNER.ROUTING_SYSTEM_PROMPT,
        )
        for prompt in prompts
    }
    report_prompts: list[dict[str, Any]] = []
    observed_catalogs: dict[str, dict[str, Any]] = {}
    for prompt_index, prompt in enumerate(prompts):
        phases: dict[str, list[dict[str, Any]]] = {"warmups": [], "measurements": []}
        for phase, count in (("warmups", args.warmups), ("measurements", args.samples)):
            for pair_index, order in enumerate(run_order(count)):
                arms: dict[str, Any] = {}
                for arm in (("baseline", "treatment") if order == "AB" else ("treatment", "baseline")):
                    full = capture_once(args, roots[arm], prompt, inventories[arm])
                    control = capture_once(args, roots[arm], prompt, None)
                    matched = matched_payload_hash(payload_hashes[prompt["id"]], payload_hashes[prompt["id"]])
                    attribution = token_attribution(full["usage"], control["usage"], matched == payload_hashes[prompt["id"]])
                    catalog_record = {
                        key: full[key]
                        for key in ("catalog", "serialized_catalog", "catalog_sha256", "catalog_bytes")
                    }
                    previous = observed_catalogs.setdefault(arm, catalog_record)
                    if previous != catalog_record:
                        raise ValueError(f"{roots[arm]}: runtime serialized catalog changed during the probe")
                    arms[arm] = {
                        "elapsed_ms": full["elapsed_ms"],
                        "control_elapsed_ms": control["elapsed_ms"],
                        "usage": attribution,
                    }
                phases[phase].append({"pair": pair_index + 1, "order": order, "arms": arms})
        deltas = [
            item["arms"]["treatment"]["elapsed_ms"] - item["arms"]["baseline"]["elapsed_ms"]
            for item in phases["measurements"]
        ]
        lower, upper = bootstrap_median_ci(deltas, args.seed + prompt_index)
        claim = "improvement" if upper < 0 else "regression" if lower > 0 else "unavailable"
        token_claim_eligible = all(
            item["arms"][arm]["usage"]["claim_eligible"]
            for item in phases["measurements"]
            for arm in ("baseline", "treatment")
        )
        report_prompts.append(
            {
                "id": prompt["id"],
                "prompt": prompt["prompt"],
                "request_payload_sha256": payload_hashes[prompt["id"]],
                **phases,
                "statistics": {
                    "sample_count": args.samples,
                    "paired_latency_delta_ms": "treatment_minus_baseline",
                    "paired_median_latency_delta_ms": statistics.median(deltas),
                    "bootstrap_seed": args.seed + prompt_index,
                    "bootstrap_resamples": 10_000,
                    "bootstrap_95_percent_ci_ms": [lower, upper],
                    "latency_claim": claim,
                    "token_claim_eligible": token_claim_eligible,
                    "token_claim_refusal_reason": None if token_claim_eligible else "attribution unavailable for one or more matched requests",
                },
            }
        )
    return {
        "schema_version": 1,
        "probe": {
            "path": "evals/catalog_probe.py",
            "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "repository_revision": git_revision(Path(__file__).resolve().parents[1]),
        },
        "catalogs": {
            arm: {
                "root": str(roots[arm]),
                "repository_revision": git_revision(roots[arm]),
                "inventory": inventories[arm],
                **observed_catalogs[arm],
            }
            for arm in ("baseline", "treatment")
        },
        "configuration": {
            "model": args.model,
            "profile": args.profile,
            "tools": tools,
            "thinking": args.thinking,
            "max_time": args.max_time,
            "configs": [str(path) for path in args.config],
            "warmups": args.warmups,
            "samples": args.samples,
        },
        "prompts": report_prompts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--treatment-root", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--prompts", type=Path, help="Optional JSONL prompt set with exact id and prompt fields")
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--samples", type=int, default=15)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--omp", default="omp")
    parser.add_argument("--config", type=Path, action="append", default=[])
    parser.add_argument("--tools", default="")
    parser.add_argument("--thinking", default="off")
    parser.add_argument("--max-time", default="10m")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.warmups < 3:
        parser.error("--warmups must be at least 3")
    if args.samples < 15:
        parser.error("--samples must be at least 15")
    try:
        report = compare(args)
        if args.output.exists():
            raise ValueError(f"{args.output}: output already exists; choose a new immutable artifact path")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"catalog probe failed: {error}", file=sys.stderr)
        return 1
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
