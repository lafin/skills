#!/usr/bin/env python3
"""Status: Reusable. Capture real OMP behavior and routing runs as artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import selectors
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = 3
CHECK_OPS = {"contains", "not_contains", "equals", "regex", "not_regex"}
BEHAVIOR_SYSTEM_PROMPT = (
    "You are a coding assistant. Answer the case directly. Emit exactly the requested "
    "newline-separated fields with no preamble or suffix. ABSTRACTION means a new "
    "abstraction, DEPENDENCIES means a new third-party dependency, and "
    "UNSUPPORTED_CLAIMS means an unsupported success claim. Use the single word none "
    "when the applicable item is absent; standard-library or existing code is none."
)
COMMON_CASE_FIELDS = {
    "id",
    "kind",
    "split",
    "target_skill",
    "prompt",
    "observable_success",
    "prohibited_outcomes",
    "checks",
    "judge_criteria",
}


def nonempty_strings(value: Any, label: str) -> None:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{label} must be a non-empty array of non-empty strings")


def validate_case(case: Any, location: str) -> dict[str, Any]:
    if not isinstance(case, dict):
        raise ValueError(f"{location}: case must be an object")
    kind = case.get("kind")
    allowed = COMMON_CASE_FIELDS | ({"response_fields"} if kind == "behavior" else {"available_skills"} if kind == "routing" else set())
    missing = {"id", "kind", "split", "target_skill", "prompt", "observable_success", "prohibited_outcomes", "checks"} - case.keys()
    extra = case.keys() - allowed
    if missing:
        raise ValueError(f"{location}: missing {', '.join(sorted(missing))}")
    if extra:
        raise ValueError(f"{location}: unknown fields: {', '.join(sorted(extra))}")
    if kind not in {"behavior", "routing"}:
        raise ValueError(f"{location}: kind must be behavior or routing")
    if case["split"] not in {"development", "holdout"}:
        raise ValueError(f"{location}: split must be development or holdout")
    for name in ("id", "target_skill", "prompt"):
        if not isinstance(case[name], str) or not case[name]:
            raise ValueError(f"{location}: {name} must be a non-empty string")
    safe_name(case["id"])
    nonempty_strings(case["observable_success"], f"{location}: observable_success")
    nonempty_strings(case["prohibited_outcomes"], f"{location}: prohibited_outcomes")
    if "judge_criteria" in case:
        nonempty_strings(case["judge_criteria"], f"{location}: judge_criteria")
    checks = case["checks"]
    if not isinstance(checks, list) or not checks:
        raise ValueError(f"{location}: checks must be a non-empty array")
    check_names: set[str] = set()
    for index, check in enumerate(checks, 1):
        check_location = f"{location}: check {index}"
        if not isinstance(check, dict):
            raise ValueError(f"{check_location} must be an object")
        unknown = check.keys() - {"name", "op", "value", "field", "critical"}
        missing_check = {"name", "op", "value", "critical"} - check.keys()
        if unknown or missing_check:
            raise ValueError(f"{check_location}: invalid fields")
        if not isinstance(check["name"], str) or not check["name"] or check["name"] in check_names:
            raise ValueError(f"{check_location}: name must be a unique non-empty string")
        check_names.add(check["name"])
        if check["op"] not in CHECK_OPS:
            raise ValueError(f"{check_location}: unsupported operation {check['op']!r}")
        if not isinstance(check["value"], str) or not isinstance(check["critical"], bool):
            raise ValueError(f"{check_location}: value must be a string and critical must be boolean")
        if "field" in check and (not isinstance(check["field"], str) or not check["field"]):
            raise ValueError(f"{check_location}: field must be a non-empty string")
        if check["op"] in {"regex", "not_regex"}:
            try:
                re.compile(check["value"])
            except re.error as error:
                raise ValueError(f"{check_location}: invalid regex: {error}") from error
    if kind == "behavior":
        nonempty_strings(case.get("response_fields"), f"{location}: response_fields")
        if len(set(case["response_fields"])) != len(case["response_fields"]):
            raise ValueError(f"{location}: response_fields must be unique")
    else:
        nonempty_strings(case.get("available_skills"), f"{location}: available_skills")
        if len(set(case["available_skills"])) != len(case["available_skills"]):
            raise ValueError(f"{location}: available_skills must be unique")
        if case["target_skill"] not in case["available_skills"]:
            raise ValueError(f"{location}: target_skill must be in available_skills")
    return case


def load_cases(paths: list[Path]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                case = validate_case(json.loads(line), f"{path}:{number}")
                if case["id"] in seen:
                    raise ValueError(f"duplicate case id: {case['id']}")
                seen.add(case["id"])
                cases.append(case)
    if not cases:
        raise ValueError("no cases loaded")
    return cases


def run_text(command: list[str], cwd: Path) -> tuple[int, str, str]:
    completed = subprocess.run(
        command, cwd=cwd, stdin=subprocess.DEVNULL, text=True, capture_output=True, check=False
    )
    return completed.returncode, completed.stdout, completed.stderr


def git_value(cwd: Path, *args: str) -> str | None:
    code, stdout, _ = run_text(["git", *args], cwd)
    return stdout.strip() if code == 0 else None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()

def skill_description(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    metadata = yaml.safe_load(text.split("---", 2)[1])
    description = metadata.get("description") if isinstance(metadata, dict) else None
    if not isinstance(description, str) or not description.strip():
        raise ValueError(f"{path}: missing frontmatter description")
    return description.strip()


def parse_events(stdout: str) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    for number, line in enumerate(stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"line {number}: {error.msg}")
            continue
        if isinstance(value, dict):
            events.append(value)
        else:
            errors.append(f"line {number}: event is not an object")
    return events, errors


def text_content(message: dict[str, Any]) -> str:
    parts = message.get("content", [])
    if isinstance(parts, str):
        return parts
    plain: list[str] = []
    final: list[str] = []
    for part in parts:
        if not isinstance(part, dict) or part.get("type") != "text":
            continue
        text = part.get("text", "")
        signature = part.get("textSignature")
        phase = None
        if isinstance(signature, str):
            try:
                phase = json.loads(signature).get("phase")
            except (json.JSONDecodeError, AttributeError):
                pass
        (final if phase == "final_answer" else plain).append(text)
    return "".join(final or plain)


def sum_usage(usages: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in sorted({key for usage in usages for key in usage}):
        values = [usage.get(key) for usage in usages]
        if all(isinstance(value, dict) for value in values):
            result[key] = sum_usage(values)
        elif all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
            result[key] = sum(values)
        else:
            result[key] = None
    return result


def summarize_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    assistant_messages: list[dict[str, Any]] = []
    tool_trace: list[dict[str, Any]] = []
    tool_names: list[str] = []
    prompt_results: list[dict[str, Any]] = []
    terminal_events: list[dict[str, Any]] = []
    for event in events:
        message = event.get("message")
        if (
            event.get("type") == "message_end"
            and isinstance(message, dict)
            and message.get("role") == "assistant"
        ):
            assistant_messages.append(message)
        event_type = event.get("type")
        if event_type == "tool_execution_start" and isinstance(event.get("toolName"), str):
            tool_names.append(event["toolName"])
        if isinstance(event_type, str) and ("tool" in event_type or event.get("toolResults")):
            tool_trace.append(event)
        if event_type == "prompt_result":
            prompt_results.append(event)
        if event_type == "agent_end" and event.get("isTerminal") is not False:
            terminal_events.append(event)
    final = assistant_messages[-1] if assistant_messages else {}
    usages = [message["usage"] for message in assistant_messages if isinstance(message.get("usage"), dict)]
    identities = [
        {"provider": message.get("provider"), "model": message.get("model")}
        for message in assistant_messages
    ]
    return {
        "response": text_content(final),
        "provider": final.get("provider"),
        "model": final.get("model"),
        "model_turns": identities,
        "usage": sum_usage(usages) if usages else None,
        "turn_usages": usages,
        "final_message_usage": final.get("usage"),
        "runtime": {
            key: final.get(key)
            for key in ("duration", "ttft")
            if final.get(key) is not None
        },
        "stop_reason": final.get("stopReason"),
        "tool_call_count": len(tool_names),
        "tool_names": tool_names,
        "tool_trace": tool_trace,
        "prompt_results": prompt_results,
        "terminal_events": terminal_events,
    }


def repository_catalog(cwd: Path) -> list[str]:
    catalog = sorted(path.parent.name for path in cwd.glob("*/SKILL.md"))
    if not catalog:
        raise ValueError(f"no repository skills found under {cwd}")
    return catalog


def skill_scope(case: dict[str, Any], condition: str, catalog: list[str] | None = None) -> dict[str, Any]:
    if case["kind"] == "behavior":
        return {
            "mode": "none" if condition == "baseline" else "target-only-command",
            "skills": [] if condition == "baseline" else [case["target_skill"]],
            "invocation": None if condition == "baseline" else f"/skill:{case['target_skill']}",
        }
    return {"mode": "repository-catalog", "skills": catalog or [], "confusable_pair": case["available_skills"]}

def case_prompt(case: dict[str, Any], descriptions: dict[str, str] | None = None) -> str:
    if case["kind"] != "routing":
        return case["prompt"]
    descriptions = descriptions or {}
    candidates = "\n".join(
        f"- {name}: {descriptions.get(name, '')}" for name in case["available_skills"]
    )
    return f"{case['prompt']}\nCandidate skills:\n{candidates}\nUse one exact candidate name."


def build_command(
    args: argparse.Namespace, case: dict[str, Any], catalog: list[str] | None = None
) -> list[str]:
    command = [
        args.omp,
        "--mode=rpc",
        "--no-rules",
        "--no-session",
        "--no-extensions",
        f"--cwd={args.cwd}",
        f"--model={args.model}",
        f"--thinking={args.thinking}",
        f"--max-time={args.max_time}",
    ]
    system_prompt = args.system_prompt
    if system_prompt is None and case["kind"] == "behavior":
        system_prompt = BEHAVIOR_SYSTEM_PROMPT
    if system_prompt:
        command.append(f"--system-prompt={system_prompt}")
    if args.profile:
        command.append(f"--profile={args.profile}")
    for config in args.config:
        command.append(f"--config={config}")
    command.append(f"--tools={args.tools}" if args.tools else "--no-tools")
    if case["kind"] == "behavior":
        command.append("--no-skills" if args.condition == "baseline" else f"--skills={case['target_skill']}")
    else:
        skills = catalog if catalog is not None else repository_catalog(args.cwd)
        command.append(f"--skills={','.join(skills)}")
    return command


def seconds(value: str) -> float:
    match = re.fullmatch(r"(\d+(?:[.]\d+)?)([smh]?)", value)
    if not match:
        raise ValueError("--max-time must be seconds or a number followed by s, m, or h")
    return float(match.group(1)) * {"": 1, "s": 1, "m": 60, "h": 3600}[match.group(2)]


def rpc_capture(
    command: list[str], cwd: Path, requests: list[dict[str, Any]], timeout: float
) -> tuple[int, str, str, list[dict[str, Any]], list[str], dict[str, Any]]:
    stdout_lines: list[str] = []
    events: list[dict[str, Any]] = []
    parse_errors: list[str] = []
    completed_ids: list[str] = []
    terminal_kind: str | None = None
    request_index = 0
    deadline = time.monotonic() + timeout
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as stderr_file:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=stderr_file,
            text=True,
            bufsize=1,
        )
        assert process.stdin is not None and process.stdout is not None
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)

        def send_request() -> None:
            nonlocal request_index
            process.stdin.write(json.dumps(requests[request_index], separators=(",", ":")) + "\n")
            process.stdin.flush()
            request_index += 1

        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                parse_errors.append("RPC capture timed out before a terminal result")
                break
            ready = selector.select(remaining)
            if not ready:
                parse_errors.append("RPC capture timed out before a terminal result")
                break
            line = process.stdout.readline()
            if not line:
                break
            stdout_lines.append(line)
            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                parse_errors.append(f"line {len(stdout_lines)}: {error.msg}")
                continue
            if not isinstance(event, dict):
                parse_errors.append(f"line {len(stdout_lines)}: event is not an object")
                continue
            events.append(event)
            if event.get("type") == "ready" and request_index == 0:
                send_request()
                continue
            if request_index == 0:
                continue
            current_id = requests[request_index - 1]["id"]
            local_result = (
                event.get("id") == current_id
                and (
                    (
                        event.get("type") == "response"
                        and event.get("command") == "prompt"
                        and (
                            event.get("success") is False
                            or (event.get("data") or {}).get("agentInvoked") is False
                        )
                    )
                    or (event.get("type") == "prompt_result" and event.get("agentInvoked") is False)
                )
            )
            agent_result = event.get("type") == "agent_end" and event.get("isTerminal") is not False
            if local_result or agent_result:
                completed_ids.append(current_id)
                if request_index < len(requests) and event.get("success") is not False:
                    send_request()
                else:
                    terminal_kind = "agent_end" if agent_result else "prompt_result"
                    break
        selector.close()
        process.stdin.close()
        try:
            code = process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                code = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                code = process.wait()
        stderr_file.seek(0)
        stderr = stderr_file.read()
    terminal_state = {
        "expected_prompt_id": requests[-1]["id"],
        "completed_prompt_ids": completed_ids,
        "terminal_result": terminal_kind,
        "received": completed_ids == [request["id"] for request in requests],
    }
    return code, "".join(stdout_lines), stderr, events, parse_errors, terminal_state


def effective_config(args: argparse.Namespace) -> dict[str, Any]:
    command = [args.omp]
    if args.profile:
        command.extend(["--profile", args.profile])
    command.extend(["config", "list", "--json"])
    code, stdout, stderr = run_text(command, args.cwd)
    try:
        parsed = json.loads(stdout) if code == 0 else None
    except json.JSONDecodeError:
        parsed = None
    return {
        "command": command,
        "exit_code": code,
        "value": parsed,
        "raw_stdout": "" if parsed is not None else stdout,
        "raw_stderr": stderr,
    }


def safe_name(case_id: str) -> str:
    if not case_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError(f"case id contains unsupported characters: {case_id}")
    return case_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Run JSONL evaluation cases through OMP RPC.")
    parser.add_argument("--cases", type=Path, action="append", required=True, help="JSONL case file; repeat to combine suites")
    parser.add_argument("--condition", choices=("baseline", "treatment"), required=True)
    parser.add_argument("--model", required=True, help="Exact provider/model selection used for every case")
    parser.add_argument("--output", type=Path, required=True, help="New immutable artifact directory for one condition")
    parser.add_argument("--cwd", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--omp", default="omp")
    parser.add_argument("--profile")
    parser.add_argument("--config", type=Path, action="append", default=[])
    parser.add_argument("--tools", default="read", help="Explicit comma-separated OMP tool allowlist; empty disables tools")
    parser.add_argument(
        "--system-prompt",
        help="Optional full OMP system-prompt override; omit to preserve skill discovery instructions",
    )
    parser.add_argument("--thinking", default="off")
    parser.add_argument("--max-time", default="10m")
    parser.add_argument("--attempts", type=int, default=1)
    args = parser.parse_args()

    args.cwd = args.cwd.resolve()
    args.cases = [path.resolve() for path in args.cases]
    args.config = [path.resolve() for path in args.config]
    if args.attempts < 1:
        parser.error("--attempts must be at least 1")
    if args.output.exists():
        parser.error("--output must not exist; run directories are immutable")
    try:
        cases = load_cases(args.cases)
        timeout = seconds(args.max_time) + 30
        catalog = repository_catalog(args.cwd)
        allowed_tools = [tool for tool in args.tools.split(",") if tool]
        if len(allowed_tools) != len(set(allowed_tools)) or any(tool.strip() != tool for tool in allowed_tools):
            raise ValueError("--tools must be a comma-separated list of unique exact tool names")
        for path in args.config:
            if not path.is_file():
                raise ValueError(f"config file does not exist: {path}")
        executable = Path(os.path.realpath(shutil.which(args.omp) or args.omp))
        version_code, omp_version, version_stderr = run_text([str(executable), "--version"], args.cwd)
        if version_code:
            raise ValueError(f"cannot execute OMP: {version_stderr.strip()}")
        executable_hash = sha256_file(executable)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    args.output.mkdir(parents=True)
    artifact_dir = args.output / "artifacts"
    artifact_dir.mkdir()
    commit = git_value(args.cwd, "rev-parse", "HEAD")
    dirty = git_value(args.cwd, "status", "--porcelain")
    case_files = [{"path": str(path), "sha256": sha256_file(path)} for path in args.cases]
    config_files = [{"path": str(path), "sha256": sha256_file(path)} for path in args.config]
    skill_names = {
        skill
        for case in cases
        for skill in skill_scope(case, args.condition, catalog).get("skills", [])
    }
    skill_files = {
        skill: {
            "canonical_path": f"{skill}/SKILL.md",
            "canonical_sha256": sha256_file(args.cwd / skill / "SKILL.md"),
            "commit": git_value(args.cwd, "log", "-1", "--format=%H", "--", f"{skill}/SKILL.md"),
            "description": skill_description(args.cwd / skill / "SKILL.md"),
        }
        for skill in sorted(skill_names)
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": args.output.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "condition": args.condition,
        "adapter": {
            "name": "omp-rpc-jsonl",
            "protocol_version": 1,
            "sha256": sha256_file(Path(__file__)),
        },
        "omp_executable": {"path": str(executable), "sha256": executable_hash},
        "omp_version": omp_version.strip(),
        "model_requested": args.model,
        "repository_commit": commit,
        "repository_dirty": bool(dirty),
        "repository_status": dirty.splitlines() if dirty else [],
        "skill_files": skill_files,
        "evaluator_files": {
            "run.py": sha256_file(Path(__file__)),
            "grade.py": sha256_file(Path(__file__).with_name("grade.py")),
        },
        "case_files": case_files,
        "configuration": {
            "cwd": str(args.cwd),
            "profile": args.profile,
            "config_files": config_files,
            "tools": allowed_tools,
            "thinking": args.thinking,
            "system_prompt": args.system_prompt,
            "behavior_system_prompt": args.system_prompt or BEHAVIOR_SYSTEM_PROMPT,
            "routing_system_prompt": args.system_prompt,
            "max_time": args.max_time,
            "extensions": "disabled",
            "rules": "disabled",
            "sessions": "disabled",
            "canonical_skill_root": ".",
            "effective_omp_config": effective_config(args),
        },
        "attempts": args.attempts,
        "case_ids": [case["id"] for case in cases],
    }
    case_snapshot = args.output / "cases.jsonl"
    case_snapshot.write_text(
        "".join(json.dumps(case, sort_keys=True) + "\n" for case in cases),
        encoding="utf-8",
    )
    manifest["case_snapshot"] = {"path": "cases.jsonl", "sha256": sha256_file(case_snapshot)}
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    failures = 0
    descriptions = {name: record["description"] for name, record in skill_files.items()}
    for case in cases:
        case_dir = artifact_dir / safe_name(case["id"])
        case_dir.mkdir()
        for attempt in range(1, args.attempts + 1):
            command = build_command(args, case, catalog)
            request_prefix = f"{safe_name(case['id'])}-{attempt}"
            requests = []
            if case["kind"] == "behavior" and args.condition == "treatment":
                requests.append(
                    {"id": f"{request_prefix}-skill", "type": "prompt", "message": f"/skill:{case['target_skill']}"}
                )
            requests.append(
                {
                    "id": f"{request_prefix}-case",
                    "type": "prompt",
                    "message": case_prompt(case, descriptions),
                }
            )
            started_at = datetime.now(timezone.utc).isoformat()
            started = time.monotonic()
            code, stdout, stderr, events, parse_errors, terminal_state = rpc_capture(
                command, args.cwd, requests, timeout
            )
            elapsed = time.monotonic() - started
            summary = summarize_events(events)
            tool_policy = {
                "allowed": allowed_tools,
                "observed": summary["tool_names"],
                "violations": [tool for tool in summary["tool_names"] if tool not in allowed_tools],
            }
            artifact = {
                "schema_version": SCHEMA_VERSION,
                "case_id": case["id"],
                "kind": case["kind"],
                "split": case["split"],
                "condition": args.condition,
                "attempt": attempt,
                "started_at": started_at,
                "elapsed_seconds": elapsed,
                "command": command,
                "rpc_requests": requests,
                "prompt": case["prompt"],
                "skill_scope": skill_scope(case, args.condition, catalog),
                "tool_policy": tool_policy,
                "terminal_state": terminal_state,
                "exit_code": code,
                "raw_stdout": stdout,
                "raw_stderr": stderr,
                "events": events,
                "event_parse_errors": parse_errors,
                **summary,
            }
            path = case_dir / f"{attempt}.json"
            path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            capture_ok = (
                code == 0
                and not parse_errors
                and bool(summary["response"])
                and isinstance(summary["provider"], str)
                and isinstance(summary["model"], str)
                and terminal_state["received"]
                and terminal_state["terminal_result"] == "agent_end"
                and not tool_policy["violations"]
            )
            failures += not capture_ok
            print(f"{case['id']} attempt {attempt}: exit={code} terminal={terminal_state['terminal_result']} response={bool(summary['response'])}")
    print(f"captured {len(cases) * args.attempts} artifacts in {args.output}; capture failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
