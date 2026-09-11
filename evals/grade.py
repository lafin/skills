#!/usr/bin/env python3
"""Status: Reusable. Grade captured OMP artifacts and report paired merge gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 3
HASH = re.compile(r"[0-9a-f]{64}")
POLICY_FLAGS = {"extensions": "disabled", "rules": "disabled", "sessions": "disabled"}
SENSITIVE_CONFIG_KEY = re.compile(
    r"(?:auth(?:orization)?|bearer|cookie|token|secret|password|api.?key|access.?key|private.?key|credential)",
    re.IGNORECASE,
)
VERIFIER_DIMENSIONS = {
    "correctness",
    "completeness",
    "preservation",
    "scope",
    "security_compatibility",
    "verification",
    "reporting",
}


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def parse_json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=reject_duplicate_keys)


def read_json(path: Path) -> dict[str, Any]:
    value = parse_json(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = parse_json(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{number}: expected a JSON object")
            values.append(value)
    return values


def write_json(path: Path, value: Any) -> None:
    if path.exists():
        raise ValueError(f"{path}: output already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: list[dict[str, Any]]) -> None:
    if path.exists():
        raise ValueError(f"{path}: output already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(value, sort_keys=True) + "\n" for value in values),
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_snapshot(root: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []

    def visit(directory: Path, prefix: Path) -> None:
        with os.scandir(directory) as children:
            for child in sorted(children, key=lambda item: item.name):
                relative = (prefix / child.name).as_posix()
                info = child.stat(follow_symlinks=False)
                record: dict[str, Any] = {"path": relative, "mode": info.st_mode & 0o777}
                if child.is_symlink():
                    record.update(type="symlink", target=os.readlink(child.path))
                elif child.is_dir(follow_symlinks=False):
                    record["type"] = "directory"
                    entries.append(record)
                    visit(Path(child.path), prefix / child.name)
                    continue
                elif child.is_file(follow_symlinks=False):
                    record.update(type="file", size=info.st_size, sha256=sha256_file(Path(child.path)))
                else:
                    record.update(type="other", kind=info.st_mode & 0o170000)
                entries.append(record)

    visit(root, Path())
    entries.sort(key=lambda entry: entry["path"])
    encoded = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
    return {"sha256": hashlib.sha256(encoded).hexdigest(), "entries": entries}


def validate_tree_snapshot(value: Any, label: str) -> None:
    if not isinstance(value, dict) or set(value) != {"sha256", "entries"}:
        raise ValueError(f"{label}: invalid tree snapshot")
    require_hash(value["sha256"], label)
    entries = value["entries"]
    if not isinstance(entries, list):
        raise ValueError(f"{label}: entries must be an array")
    previous = ""
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ValueError(f"{label}: invalid tree entry")
        common = {"path", "mode", "type"}
        expected = (
            common | {"size", "sha256"}
            if entry.get("type") == "file"
            else common | {"target"}
            if entry.get("type") == "symlink"
            else common
            if entry.get("type") == "directory"
            else common | {"kind"}
            if entry.get("type") == "other"
            else set()
        )
        if (
            set(entry) != expected
            or not entry["path"]
            or entry["path"] <= previous
            or Path(entry["path"]).is_absolute()
            or ".." in Path(entry["path"]).parts
            or not isinstance(entry["mode"], int)
            or isinstance(entry["mode"], bool)
            or not 0 <= entry["mode"] <= 0o777
        ):
            raise ValueError(f"{label}: invalid tree entry")
        if entry["type"] == "file":
            if not isinstance(entry["size"], int) or isinstance(entry["size"], bool) or entry["size"] < 0:
                raise ValueError(f"{label}: invalid file size")
            require_hash(entry["sha256"], label)
        elif entry["type"] == "symlink" and not isinstance(entry["target"], str):
            raise ValueError(f"{label}: invalid symlink target")
        elif entry["type"] == "other" and (
            not isinstance(entry["kind"], int) or isinstance(entry["kind"], bool)
        ):
            raise ValueError(f"{label}: invalid special-file kind")
        previous = entry["path"]
    encoded = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(encoded).hexdigest() != value["sha256"]:
        raise ValueError(f"{label}: tree snapshot hash mismatch")


def tree_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, list[Any]]:
    old = {entry["path"]: entry for entry in before["entries"]}
    new = {entry["path"]: entry for entry in after["entries"]}
    return {
        "added": [new[path] for path in sorted(new.keys() - old.keys())],
        "removed": [old[path] for path in sorted(old.keys() - new.keys())],
        "changed": [
            {"before": old[path], "after": new[path]}
            for path in sorted(old.keys() & new.keys())
            if old[path] != new[path]
        ],
    }


def parse_verifier_output(stdout: str) -> list[dict[str, Any]]:
    document = parse_json(stdout)
    if not isinstance(document, dict) or set(document) != {"checks"}:
        raise ValueError("verifier output must be one object containing only checks")
    checks = document["checks"]
    if not isinstance(checks, list) or not checks:
        raise ValueError("verifier checks must be a non-empty array")
    names: set[str] = set()
    required = {"name", "dimension", "critical", "passed", "detail"}
    for check in checks:
        if (
            not isinstance(check, dict)
            or set(check) != required
            or not isinstance(check["name"], str)
            or not check["name"]
            or check["name"] in names
            or check["dimension"] not in VERIFIER_DIMENSIONS
            or not isinstance(check["critical"], bool)
            or not isinstance(check["passed"], bool)
            or not isinstance(check["detail"], str)
        ):
            raise ValueError("verifier returned an invalid check")
        names.add(check["name"])
    return checks


def require_hash(value: Any, label: str) -> None:
    if not isinstance(value, str) or HASH.fullmatch(value) is None:
        raise ValueError(f"{label}: expected a SHA-256 digest")


def validate_case(case: dict[str, Any], location: str) -> None:
    required = {
        "id",
        "kind",
        "split",
        "target_skill",
        "prompt",
        "observable_success",
        "prohibited_outcomes",
        "checks",
    }
    kind = case.get("kind")
    allowed = required | {"judge_criteria"} | (
        {"response_fields"}
        if kind == "behavior"
        else {"available_skills"}
        if kind == "routing"
        else {"fixture"}
        if kind == "repository"
        else set()
    )
    if required - case.keys() or case.keys() - allowed:
        raise ValueError(f"{location}: incomplete or unknown case schema")
    if kind not in {"behavior", "routing", "repository"} or case["split"] not in {"development", "holdout"}:
        raise ValueError(f"{location}: invalid kind or split")
    if not all(isinstance(case[name], str) and case[name] for name in ("id", "target_skill", "prompt")):
        raise ValueError(f"{location}: invalid case identity")
    for name in ("observable_success", "prohibited_outcomes"):
        values = case[name]
        if not isinstance(values, list) or not values or not all(isinstance(item, str) and item for item in values):
            raise ValueError(f"{location}: invalid {name}")
    criteria = case.get("judge_criteria")
    if criteria is not None and (
        not isinstance(criteria, list)
        or not criteria
        or not all(isinstance(item, str) and item for item in criteria)
    ):
        raise ValueError(f"{location}: invalid judge_criteria")
    if not isinstance(case["checks"], list) or (kind != "repository" and not case["checks"]):
        raise ValueError(f"{location}: invalid deterministic checks")
    names: set[str] = set()
    for check in case["checks"]:
        if (
            not isinstance(check, dict)
            or set(check) - {"name", "op", "value", "field", "critical", "dimension"}
            or {"name", "op", "value", "critical"} - check.keys()
            or not isinstance(check["name"], str)
            or not check["name"]
            or check["name"] in names
            or check["op"] not in {"contains", "not_contains", "equals", "regex", "not_regex"}
            or not isinstance(check["value"], str)
            or not isinstance(check["critical"], bool)
            or ("field" in check and (not isinstance(check["field"], str) or not check["field"]))
            or ("dimension" in check and check["dimension"] not in VERIFIER_DIMENSIONS)
        ):
            raise ValueError(f"{location}: invalid deterministic check")
        names.add(check["name"])
        if check["op"] in {"regex", "not_regex"}:
            re.compile(check["value"])
    if kind == "behavior":
        fields = case.get("response_fields")
        if (
            not isinstance(fields, list)
            or not fields
            or not all(isinstance(field, str) and field for field in fields)
            or len(fields) != len(set(fields))
        ):
            raise ValueError(f"{location}: invalid response_fields")
    elif kind == "routing":
        skills = case.get("available_skills")
        if (
            not isinstance(skills, list)
            or not skills
            or not all(isinstance(skill, str) and skill for skill in skills)
            or len(skills) != len(set(skills))
            or case["target_skill"] not in skills
        ):
            raise ValueError(f"{location}: invalid available_skills")
    elif (
        not isinstance(case.get("fixture"), str)
        or not case["fixture"]
        or not case["fixture"].replace("-", "").replace("_", "").isalnum()
    ):
        raise ValueError(f"{location}: invalid fixture")

def validate_redacted_config(value: Any, key: str = "") -> None:
    if SENSITIVE_CONFIG_KEY.search(key):
        redacted = value.get("value") if isinstance(value, dict) else value
        if redacted != "<redacted>":
            raise ValueError(f"effective OMP config contains unredacted sensitive key {key!r}")
        return
    if isinstance(value, dict):
        for name, item in value.items():
            validate_redacted_config(item, name)
    elif isinstance(value, list):
        for item in value:
            validate_redacted_config(item, key)

def validate_manifest(run: Path, manifest: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "run_id",
        "condition",
        "adapter",
        "omp_executable",
        "omp_version",
        "model_requested",
        "evaluator_files",
        "skill_files",
        "repository_commit",
        "repository_dirty",
        "repository_status",
        "configuration",
        "attempts",
        "case_ids",
        "case_snapshot",
    }
    if required - manifest.keys() or manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"{run}: unsupported or incomplete manifest schema")
    if manifest["condition"] not in {"baseline", "treatment"}:
        raise ValueError(f"{run}: invalid condition")
    if not isinstance(manifest["attempts"], int) or isinstance(manifest["attempts"], bool) or manifest["attempts"] < 1:
        raise ValueError(f"{run}: invalid attempt count")
    if (
        not isinstance(manifest["run_id"], str)
        or not manifest["run_id"]
        or not isinstance(manifest["model_requested"], str)
        or manifest["model_requested"].count("/") != 1
    ):
        raise ValueError(f"{run}: invalid run or model identity")
    provider, model = manifest["model_requested"].split("/")
    if not provider or not model:
        raise ValueError(f"{run}: model_requested must be exact provider/model")
    if (
        not isinstance(manifest["repository_commit"], str)
        or re.fullmatch(r"[0-9a-f]{40}", manifest["repository_commit"]) is None
        or not isinstance(manifest["repository_dirty"], bool)
        or not isinstance(manifest["repository_status"], list)
        or not all(isinstance(line, str) for line in manifest["repository_status"])
        or manifest["repository_dirty"] != bool(manifest["repository_status"])
    ):
        raise ValueError(f"{run}: invalid repository identity metadata")
    adapter = manifest["adapter"]
    if not isinstance(adapter, dict) or adapter.get("name") != "omp-rpc-jsonl" or adapter.get("protocol_version") != 1:
        raise ValueError(f"{run}: unsupported adapter")
    require_hash(adapter.get("sha256"), f"{run}: adapter")
    executable = manifest["omp_executable"]
    if not isinstance(executable, dict) or set(executable) != {"path", "sha256"} or not Path(executable["path"]).is_absolute():
        raise ValueError(f"{run}: invalid OMP executable metadata")
    require_hash(executable["sha256"], f"{run}: OMP executable")
    evaluators = manifest["evaluator_files"]
    if not isinstance(evaluators, dict) or set(evaluators) != {"run.py", "grade.py"}:
        raise ValueError(f"{run}: invalid evaluator metadata")
    for name, digest in evaluators.items():
        require_hash(digest, f"{run}: {name}")
    if adapter["sha256"] != evaluators["run.py"]:
        raise ValueError(f"{run}: adapter is not bound to run.py")
    if evaluators["grade.py"] != sha256_file(Path(__file__)):
        raise ValueError(f"{run}: captured grader hash differs from the active grader")
    skills = manifest["skill_files"]
    if not isinstance(skills, dict):
        raise ValueError(f"{run}: invalid skill metadata")
    expected_skill_fields = {
        "canonical_path",
        "canonical_sha256",
        "commit",
        "description",
    }
    for name, record in skills.items():
        if (
            not isinstance(name, str)
            or not name
            or not isinstance(record, dict)
            or set(record) != expected_skill_fields
            or record["canonical_path"] != f"{name}/SKILL.md"
            or not isinstance(record["description"], str)
            or not record["description"]
            or not isinstance(record["commit"], str)
            or re.fullmatch(r"[0-9a-f]{40}", record["commit"]) is None
        ):
            raise ValueError(f"{run}: invalid skill metadata for {name!r}")
        require_hash(record["canonical_sha256"], f"{run}: {name} canonical")
    config = manifest["configuration"]
    if not isinstance(config, dict) or any(config.get(key) != value for key, value in POLICY_FLAGS.items()):
        raise ValueError(f"{run}: rules, extensions, and sessions must be disabled")
    tools = config.get("tools")
    if (
        not isinstance(tools, list)
        or not all(isinstance(tool, str) and tool for tool in tools)
        or len(tools) != len(set(tools))
    ):
        raise ValueError(f"{run}: invalid explicit tool allowlist")
    if config.get("canonical_skill_root") != ".":
        raise ValueError(f"{run}: unexpected canonical skill root")
    config_files = config.get("config_files")
    if not isinstance(config_files, list):
        raise ValueError(f"{run}: invalid config file metadata")
    for item in config_files:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise ValueError(f"{run}: invalid config file record")
        require_hash(item["sha256"], f"{run}: config file")
    profile = config.get("profile")
    effective = config.get("effective_omp_config")
    if not isinstance(profile, str) or not profile:
        raise ValueError(f"{run}: an isolated OMP profile is required")
    if (
        not isinstance(effective, dict)
        or effective.get("exit_code") != 0
        or effective.get("mcp_configured") is not False
        or not isinstance(effective.get("profile_path"), str)
        or not Path(effective["profile_path"]).is_absolute()
        or not isinstance(effective.get("value"), dict)
    ):
        raise ValueError(f"{run}: invalid or contaminated OMP profile metadata")
    validate_redacted_config(effective["value"])
    fixtures = manifest.get("fixture_files", {})
    if not isinstance(fixtures, dict):
        raise ValueError(f"{run}: invalid fixture metadata")
    canonical_root = Path(config.get("cwd", ""))
    if fixtures and not canonical_root.is_absolute():
        raise ValueError(f"{run}: fixture metadata requires an absolute canonical cwd")
    fixture_fields = {
        "initial_path",
        "initial_tree_sha256",
        "verifier_path",
        "verifier_sha256",
    }
    for fixture_id, record in fixtures.items():
        expected_initial = f"evals/fixtures/{fixture_id}/initial"
        expected_verifier = f"evals/fixtures/{fixture_id}/verify.py"
        if (
            not isinstance(fixture_id, str)
            or not fixture_id.replace("-", "").replace("_", "").isalnum()
            or not isinstance(record, dict)
            or set(record) != fixture_fields
            or record["initial_path"] != expected_initial
            or record["verifier_path"] != expected_verifier
        ):
            raise ValueError(f"{run}: invalid fixture metadata for {fixture_id!r}")
        require_hash(record["initial_tree_sha256"], f"{run}: {fixture_id} initial tree")
        require_hash(record["verifier_sha256"], f"{run}: {fixture_id} verifier")
        initial_path = canonical_root / record["initial_path"]
        verifier_path = canonical_root / record["verifier_path"]
        if (
            not initial_path.is_dir()
            or tree_snapshot(initial_path)["sha256"] != record["initial_tree_sha256"]
        ):
            raise ValueError(f"{run}: {fixture_id} initial fixture hash mismatch")
        if (
            not verifier_path.is_file()
            or sha256_file(verifier_path) != record["verifier_sha256"]
        ):
            raise ValueError(f"{run}: {fixture_id} verifier hash mismatch")
    snapshot = manifest["case_snapshot"]
    if not isinstance(snapshot, dict) or snapshot.get("path") != "cases.jsonl":
        raise ValueError(f"{run}: case snapshot must be cases.jsonl")
    require_hash(snapshot.get("sha256"), f"{run}: case snapshot")
    if sha256_file(run / "cases.jsonl") != snapshot["sha256"]:
        raise ValueError(f"{run}: case snapshot hash mismatch")


def load_run(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    manifest = read_json(path / "manifest.json")
    validate_manifest(path, manifest)
    cases = read_jsonl(path / "cases.jsonl")
    by_id: dict[str, dict[str, Any]] = {}
    for number, case in enumerate(cases, 1):
        validate_case(case, f"{path}/cases.jsonl:{number}")
        if case["id"] in by_id:
            raise ValueError(f"{path}: duplicate case ids in snapshot")
        by_id[case["id"]] = case
    if manifest["case_ids"] != [case["id"] for case in cases]:
        raise ValueError(f"{path}: manifest case_ids differ from snapshot")
    expected_fixtures = {
        case["fixture"] for case in cases if case["kind"] == "repository"
    }
    if set(manifest.get("fixture_files", {})) != expected_fixtures:
        raise ValueError(f"{path}: fixture metadata differs from case snapshot")
    if expected_fixtures and not manifest["configuration"]["tools"]:
        raise ValueError(f"{path}: repository cases require an explicit non-empty tool allowlist")
    return manifest, by_id, cases


def expected_artifact_paths(run: Path, cases: dict[str, dict[str, Any]], attempts: int) -> dict[tuple[str, int], Path]:
    return {
        (case_id, attempt): run / "artifacts" / case_id / f"{attempt}.json"
        for case_id in cases
        for attempt in range(1, attempts + 1)
    }


def parse_events(stdout: str) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    for number, line in enumerate(stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = parse_json(line)
        except (json.JSONDecodeError, ValueError) as error:
            errors.append(f"line {number}: {error}")
            continue
        if isinstance(event, dict):
            events.append(event)
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
                phase = parse_json(signature).get("phase")
            except (json.JSONDecodeError, ValueError, AttributeError):
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


def observed_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    assistants = [
        event["message"]
        for event in events
        if event.get("type") == "message_end"
        and isinstance(event.get("message"), dict)
        and event["message"].get("role") == "assistant"
    ]
    final = assistants[-1] if assistants else {}
    usages = [message["usage"] for message in assistants if isinstance(message.get("usage"), dict)]
    tool_names = [
        event["toolName"]
        for event in events
        if event.get("type") == "tool_execution_start" and isinstance(event.get("toolName"), str)
    ]
    tool_trace = [
        event
        for event in events
        if isinstance(event.get("type"), str)
        and ("tool" in event["type"] or event.get("toolResults"))
    ]
    return {
        "response": text_content(final),
        "provider": final.get("provider"),
        "model": final.get("model"),
        "model_turns": [
            {"provider": message.get("provider"), "model": message.get("model")}
            for message in assistants
        ],
        "usage": sum_usage(usages) if usages else None,
        "turn_usages": usages,
        "final_message_usage": final.get("usage"),
        "stop_reason": final.get("stopReason"),
        "tool_call_count": len(tool_names),
        "tool_names": tool_names,
        "tool_trace": tool_trace,
        "prompt_results": [event for event in events if event.get("type") == "prompt_result"],
        "terminal_events": [
            event
            for event in events
            if event.get("type") == "agent_end" and event.get("isTerminal") is not False
        ],
    }


def expected_scope(case: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if case["kind"] in {"behavior", "repository"}:
        treatment = manifest["condition"] == "treatment"
        return {
            "mode": "target-only-command" if treatment else "none",
            "skills": [case["target_skill"]] if treatment else [],
            "invocation": f"/skill:{case['target_skill']}" if treatment else None,
        }
    return {
        "mode": "repository-catalog",
        "skills": sorted(manifest.get("skill_files", {})),
        "confusable_pair": case["available_skills"],
    }

def case_prompt(case: dict[str, Any], descriptions: dict[str, str]) -> str:
    if case["kind"] != "routing":
        return case["prompt"]
    candidates = "\n".join(
        f"- {name}: {descriptions[name]}" for name in case["available_skills"]
    )
    return f"{case['prompt']}\nCandidate skills:\n{candidates}\nUse one exact candidate name."


def validate_fixture_artifact(
    value: Any,
    case: dict[str, Any],
    manifest: dict[str, Any],
    command: list[str],
) -> None:
    required = {
        "id",
        "worktree",
        "source",
        "initial_tree",
        "final_tree",
        "diff",
        "unified_diff",
        "verifier",
    }
    if not isinstance(value, dict) or set(value) != required or value.get("id") != case["fixture"]:
        raise ValueError("invalid repository fixture evidence")
    worktree = value["worktree"]
    if (
        not isinstance(worktree, str)
        or not Path(worktree).is_absolute()
        or worktree == manifest["configuration"]["cwd"]
        or f"--cwd={worktree}" not in command
    ):
        raise ValueError("repository OMP command did not use an isolated worktree")
    validate_tree_snapshot(value["initial_tree"], "repository initial tree")
    validate_tree_snapshot(value["final_tree"], "repository final tree")
    record = manifest.get("fixture_files", {}).get(case["fixture"])
    if (
        not isinstance(record, dict)
        or value["source"] != record
        or value["initial_tree"]["sha256"] != record.get("initial_tree_sha256")
        or value["diff"] != tree_diff(value["initial_tree"], value["final_tree"])
    ):
        raise ValueError("repository tree evidence differs from fixture metadata")
    if not isinstance(value["unified_diff"], str):
        raise ValueError("repository unified diff is missing")
    verifier = value["verifier"]
    verifier_fields = {
        "command",
        "cwd",
        "exit_code",
        "stdout",
        "stderr",
        "checks",
        "parse_error",
    }
    verifier_path = Path(manifest["configuration"]["cwd"]) / record["verifier_path"]
    expected_command = [sys.executable, str(verifier_path), worktree]
    if (
        not isinstance(verifier, dict)
        or set(verifier) != verifier_fields
        or verifier.get("command") != expected_command
        or verifier.get("cwd") != worktree
        or not isinstance(verifier.get("exit_code"), int)
        or isinstance(verifier.get("exit_code"), bool)
        or not isinstance(verifier.get("stdout"), str)
        or not isinstance(verifier.get("stderr"), str)
        or verifier.get("parse_error") is not None
    ):
        raise ValueError("invalid or unlocked repository verifier evidence")
    checks = parse_verifier_output(verifier["stdout"])
    if verifier["checks"] != checks:
        raise ValueError("stored verifier checks differ from raw verifier output")


def validate_artifact(
    path: Path,
    expected_path: Path,
    case: dict[str, Any],
    manifest: dict[str, Any],
    attempt: int,
) -> dict[str, Any]:
    if path != expected_path:
        raise ValueError(f"{path}: artifact is stored at the wrong path")
    artifact = read_json(path)
    exact = {
        "schema_version": SCHEMA_VERSION,
        "case_id": case["id"],
        "kind": case["kind"],
        "split": case["split"],
        "condition": manifest["condition"],
        "attempt": attempt,
        "prompt": case["prompt"],
    }
    if any(artifact.get(key) != value for key, value in exact.items()):
        raise ValueError(f"{path}: artifact identity differs from manifest or case")
    if artifact.get("skill_scope") != expected_scope(case, manifest):
        raise ValueError(f"{path}: skill scope violates the condition policy")
    if (
        case["kind"] in {"behavior", "repository"}
        and manifest["condition"] == "treatment"
        and case["target_skill"] not in manifest["skill_files"]
    ):
        raise ValueError(f"{path}: treatment target skill is not bound to the manifest")
    command = artifact.get("command")
    if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
        raise ValueError(f"{path}: invalid command record")
    required_flags = {"--mode=rpc", "--no-rules", "--no-session", "--no-extensions"}
    if not required_flags.issubset(command) or any(item.startswith("--append-system-prompt") for item in command):
        raise ValueError(f"{path}: command does not enforce RPC isolation")
    tools = manifest["configuration"]["tools"]
    expected_tool_flag = f"--tools={','.join(tools)}" if tools else "--no-tools"
    if expected_tool_flag not in command:
        raise ValueError(f"{path}: command tool allowlist differs from manifest")
    expected_runtime_flags = {
        f"--profile={manifest['configuration']['profile']}",
        f"--model={manifest['model_requested']}",
        f"--thinking={manifest['configuration']['thinking']}",
        f"--max-time={manifest['configuration']['max_time']}",
    }
    expected_config_flags = {
        f"--config={record['path']}"
        for record in manifest["configuration"]["config_files"]
    }
    observed_config_flags = {item for item in command if item.startswith("--config=")}
    if (
        not expected_runtime_flags.issubset(command)
        or observed_config_flags != expected_config_flags
        or any(command.count(flag) != 1 for flag in expected_runtime_flags | expected_config_flags)
    ):
        raise ValueError(f"{path}: command runtime configuration differs from manifest")
    expected_skill_flag = (
        "--no-skills"
        if case["kind"] in {"behavior", "repository"} and manifest["condition"] == "baseline"
        else f"--skills={case['target_skill']}"
        if case["kind"] in {"behavior", "repository"}
        else f"--skills={','.join(sorted(manifest.get('skill_files', {})))}"
    )
    if expected_skill_flag not in command:
        raise ValueError(f"{path}: command skill scope differs from manifest")
    rpc_cwd = artifact.get("rpc_cwd")
    if case["kind"] == "repository":
        if not isinstance(rpc_cwd, str) or f"--cwd={rpc_cwd}" not in command:
            raise ValueError(f"{path}: repository command cwd differs from artifact")
        validate_fixture_artifact(artifact.get("fixture"), case, manifest, command)
        if rpc_cwd != artifact["fixture"]["worktree"]:
            raise ValueError(f"{path}: repository RPC cwd differs from its worktree")
    elif (
        not isinstance(rpc_cwd, str)
        or rpc_cwd != manifest["configuration"]["cwd"]
        or f"--cwd={rpc_cwd}" not in command
    ):
        raise ValueError(f"{path}: command cwd differs from artifact")
    requests = artifact.get("rpc_requests")
    descriptions = {
        name: record["description"] for name, record in manifest["skill_files"].items()
    }
    expected_messages = (
        [f"/skill:{case['target_skill']}", case_prompt(case, descriptions)]
        if case["kind"] in {"behavior", "repository"} and manifest["condition"] == "treatment"
        else [case_prompt(case, descriptions)]
    )
    if (
        not isinstance(requests, list)
        or [request.get("message") for request in requests if isinstance(request, dict)] != expected_messages
        or any(
            set(request) != {"id", "type", "message"}
            or request["type"] != "prompt"
            or not isinstance(request["id"], str)
            for request in requests
        )
    ):
        raise ValueError(f"{path}: invalid RPC request sequence")
    raw_stdout = artifact.get("raw_stdout")
    if not isinstance(raw_stdout, str) or not isinstance(artifact.get("raw_stderr"), str):
        raise ValueError(f"{path}: raw process output is missing")
    events, parse_errors = parse_events(raw_stdout)
    if case["kind"] == "routing":
        observed_descriptions = {
            command.get("name"): command.get("description")
            for event in events
            if event.get("type") == "available_commands_update"
            for command in event.get("commands", [])
            if isinstance(command, dict)
        }
        for name in case["available_skills"]:
            observed = observed_descriptions.get(f"skill:{name}")
            if not isinstance(observed, str) or observed.strip() != descriptions[name].strip():
                raise ValueError(f"{path}: runtime skill description differs for {name}")
    if artifact.get("events") != events or artifact.get("event_parse_errors") != parse_errors:
        raise ValueError(f"{path}: parsed events do not match exact raw stdout")
    summary = observed_summary(events)
    for key, value in summary.items():
        if artifact.get(key) != value:
            raise ValueError(f"{path}: {key} does not match raw events")
    terminal = artifact.get("terminal_state")
    if (
        not isinstance(terminal, dict)
        or terminal.get("expected_prompt_id") != requests[-1]["id"]
        or terminal.get("completed_prompt_ids") != [request["id"] for request in requests]
        or terminal.get("terminal_result") != "agent_end"
        or terminal.get("received") is not True
        or not summary["terminal_events"]
    ):
        raise ValueError(f"{path}: missing terminal agent result")
    prompt_responses = {
        event.get("id")
        for event in events
        if event.get("type") == "response"
        and event.get("command") == "prompt"
        and event.get("success") is True
    }
    if any(request["id"] not in prompt_responses for request in requests):
        raise ValueError(f"{path}: RPC prompt was not accepted")
    if (
        not isinstance(artifact.get("exit_code"), int)
        or isinstance(artifact.get("exit_code"), bool)
        or not isinstance(artifact.get("elapsed_seconds"), (int, float))
        or isinstance(artifact.get("elapsed_seconds"), bool)
        or not isinstance(summary["usage"], dict)
        or not isinstance(summary["final_message_usage"], dict)
        or not isinstance(summary["response"], str)
        or not summary["response"]
    ):
        raise ValueError(f"{path}: incomplete terminal response metadata")
    requested_provider, requested_model = manifest["model_requested"].split("/")
    expected_identity = {"provider": requested_provider, "model": requested_model}
    if (
        artifact.get("provider") != requested_provider
        or artifact.get("model") != requested_model
        or not summary["model_turns"]
        or any(identity != expected_identity for identity in summary["model_turns"])
    ):
        raise ValueError(f"{path}: observed provider/model differs from requested model")
    policy = artifact.get("tool_policy")
    violations = [name for name in summary["tool_names"] if name not in tools]
    if (
        not isinstance(policy, dict)
        or policy.get("allowed") != tools
        or policy.get("observed") != summary["tool_names"]
        or policy.get("violations") != violations
    ):
        raise ValueError(f"{path}: tool policy metadata is inconsistent")
    return artifact


def load_artifacts(
    run: Path, manifest: dict[str, Any], cases: dict[str, dict[str, Any]]
) -> dict[tuple[str, int], dict[str, Any]]:
    expected = expected_artifact_paths(run, cases, manifest["attempts"])
    actual_paths = set((run / "artifacts").rglob("*.json")) if (run / "artifacts").is_dir() else set()
    if actual_paths != set(expected.values()):
        missing = sorted(str(path.relative_to(run)) for path in set(expected.values()) - actual_paths)
        extra = sorted(str(path.relative_to(run)) for path in actual_paths - set(expected.values()))
        raise ValueError(f"{run}: artifact paths differ; missing={missing}, extra={extra}")
    artifacts: dict[tuple[str, int], dict[str, Any]] = {}
    for key, path in expected.items():
        artifact = validate_artifact(path, path, cases[key[0]], manifest, key[1])
        actual_key = (artifact["case_id"], artifact["attempt"])
        if actual_key in artifacts:
            raise ValueError(f"{run}: duplicate case-attempt {actual_key}")
        artifacts[actual_key] = artifact
    if artifacts.keys() != expected.keys():
        raise ValueError(f"{run}: missing or unexpected case-attempts")
    return artifacts


def field_value(value: dict[str, Any], field: str) -> str:
    current: Any = value
    for part in field.split("."):
        if not isinstance(current, dict) or part not in current:
            return ""
        current = current[part]
    return current if isinstance(current, str) else json.dumps(current, sort_keys=True)


def parse_response_fields(response: str, names: list[str]) -> dict[str, str] | None:
    lines = [line for line in response.strip().splitlines() if line.strip()]
    if len(lines) != len(names):
        return None
    values: dict[str, str] = {}
    for line, name in zip(lines, names):
        prefix = f"{name}:"
        if not line.startswith(prefix) or not line[len(prefix) :].strip():
            return None
        values[name] = line[len(prefix) :].strip()
    return values


def apply_check(check: dict[str, Any], artifact: dict[str, Any]) -> tuple[bool, str]:
    actual = field_value(artifact, check.get("field", "response"))
    expected = check["value"]
    op = check["op"]
    if op == "contains":
        passed = expected in actual
    elif op == "not_contains":
        passed = expected not in actual
    elif op == "equals":
        passed = actual.strip().rstrip(";.") == expected.strip().rstrip(";.")
    elif op == "regex":
        passed = re.search(expected, actual) is not None
    elif op == "not_regex":
        passed = re.search(expected, actual) is None
    else:
        raise ValueError(f"unsupported check operation: {op}")
    return passed, f"{op} {expected!r} in {check.get('field', 'response')}"

def correct_route(response: str, target: str) -> bool:
    value = response.strip().rstrip(";.")
    return value in {target, f"SELECTED_SKILL: {target}"}


def grade_artifact(case: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    if case["kind"] == "repository":
        verifier = (artifact.get("fixture") or {}).get("verifier") or {}
        results.append(
            {
                "name": "fixture_verifier",
                "dimension": "verification",
                "critical": True,
                "passed": verifier.get("exit_code") == 0,
                "detail": "Locked fixture verifier exited zero"
                if verifier.get("exit_code") == 0
                else f"Locked fixture verifier exited {verifier.get('exit_code')!r}",
            }
        )
        results.extend(verifier.get("checks") or [])
    capture_ok = (
        artifact.get("schema_version") == SCHEMA_VERSION
        and artifact.get("exit_code") == 0
        and not artifact.get("event_parse_errors")
        and bool(artifact.get("response"))
        and (artifact.get("terminal_state") or {}).get("received") is True
        and (artifact.get("terminal_state") or {}).get("terminal_result") == "agent_end"
    )
    results.append(
        {
            "name": "omp_capture",
            "critical": True,
            "passed": capture_ok,
            "detail": "OMP RPC exited zero with exact events and a terminal assistant response",
        }
    )
    tool_violations = (artifact.get("tool_policy") or {}).get("violations") or []
    results.append(
        {
            "name": "tool_scope",
            "critical": True,
            "passed": not tool_violations,
            "detail": "No tool outside the recorded allowlist was called"
            if not tool_violations
            else f"Unexpected tools: {', '.join(tool_violations)}",
        }
    )
    checked_artifact = dict(artifact)
    if case["kind"] == "behavior":
        fields = parse_response_fields(artifact.get("response", ""), case["response_fields"])
        results.append(
            {
                "name": "response_contract",
                "critical": True,
                "passed": fields is not None,
                "detail": "Response contains each required field exactly once and in order",
            }
        )
        checked_artifact["fields"] = fields or {}
    for number, check in enumerate(case["checks"], 1):
        if case["kind"] == "routing" and check["name"] == "correct_route":
            passed = correct_route(artifact.get("response", ""), case["target_skill"])
            detail = "Selected the exact target skill with no explanation"
        else:
            passed, detail = apply_check(check, checked_artifact)
        result = {
            "name": check.get("name", f"check_{number}"),
            "critical": check["critical"],
            "passed": passed,
            "detail": detail,
        }
        if "dimension" in check:
            result["dimension"] = check["dimension"]
        results.append(result)
    dimensions = {}
    for dimension in sorted(VERIFIER_DIMENSIONS):
        dimension_checks = [
            result for result in results if result.get("dimension") == dimension
        ]
        measured = bool(dimension_checks)
        dimensions[dimension] = {
            "measured": measured,
            "passed": all(result["passed"] for result in dimension_checks)
            if measured
            else None,
            "details": [
                f"{result['name']}: {result['detail']}" for result in dimension_checks
            ],
        }
    usage = artifact.get("usage") or {}
    passed = all(result["passed"] for result in results)
    critical_passed = all(result["passed"] for result in results if result["critical"])
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case["id"],
        "kind": case["kind"],
        "split": case["split"],
        "condition": artifact["condition"],
        "attempt": artifact["attempt"],
        "artifact": f"artifacts/{case['id']}/{artifact['attempt']}.json",
        "passed": passed,
        "critical_passed": critical_passed,
        "checks": results,
        "dimensions": dimensions,
        "metrics": {
            "tokens": usage.get("totalTokens"),
            "tool_events": artifact.get("tool_call_count"),
            "questions": len(re.findall(r"(?mi)^QUESTION:\s*yes\s*$", artifact.get("response", ""))),
            "elapsed_seconds": artifact.get("elapsed_seconds"),
        },
    }


def input_binding(run: Path, artifact_paths: list[Path]) -> dict[str, Any]:
    return {
        "manifest_sha256": sha256_file(run / "manifest.json"),
        "case_snapshot_sha256": sha256_file(run / "cases.jsonl"),
        "artifacts": {
            str(path.relative_to(run)): sha256_file(path)
            for path in sorted(artifact_paths)
        },
        "grader_sha256": sha256_file(Path(__file__)),
    }


def compute_grades(
    run: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[tuple[str, int], dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    manifest, cases, _ = load_run(run)
    artifacts = load_artifacts(run, manifest, cases)
    grades = [grade_artifact(cases[case_id], artifact) for (case_id, _), artifact in artifacts.items()]
    binding = input_binding(run, expected_artifact_paths(run, cases, manifest["attempts"]).values())
    summary = {
        "schema_version": SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "condition": manifest["condition"],
        "artifacts": len(grades),
        "passed": sum(grade["passed"] for grade in grades),
        "critical_passed": sum(grade["critical_passed"] for grade in grades),
        "all_passed": all(grade["passed"] for grade in grades),
        "deterministic_grades": "grades.jsonl",
        "input_binding": binding,
        "efficacy_claim": None,
        "reason": "A single condition cannot support an efficacy claim; pair it with the other condition.",
    }
    return manifest, cases, artifacts, grades, summary


def grade_run(run: Path) -> dict[str, Any]:
    _, _, _, grades, summary = compute_grades(run)
    write_jsonl(run / "grades.jsonl", grades)
    write_json(run / "grade-summary.json", summary)
    return summary


def comparison_signature(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "adapter": manifest["adapter"],
        "omp_executable": manifest["omp_executable"],
        "omp_version": manifest["omp_version"],
        "model_requested": manifest["model_requested"],
        "fixture_files": manifest.get("fixture_files", {}),
        "evaluator_files": manifest["evaluator_files"],
        "configuration": manifest["configuration"],
        "attempts": manifest["attempts"],
    }


def paired_runs(
    baseline: Path, treatment: Path
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[tuple[str, int], dict[str, Any]],
    dict[tuple[str, int], dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    base_manifest, base_cases, base_artifacts, _, _ = compute_grades(baseline)
    treat_manifest, treat_cases, treat_artifacts, _, _ = compute_grades(treatment)
    if base_manifest["condition"] != "baseline" or treat_manifest["condition"] != "treatment":
        raise ValueError("paired inputs must be baseline and treatment runs, in that order")
    if comparison_signature(base_manifest) != comparison_signature(treat_manifest):
        raise ValueError("baseline and treatment adapter/executable/evaluator/configuration differs")
    if base_cases != treat_cases:
        raise ValueError("baseline and treatment case snapshots differ")
    mutable_targets = {
        case["target_skill"]
        for case in base_cases.values()
        if case["kind"] in {"behavior", "repository"}
    }
    base_skills = base_manifest["skill_files"]
    treatment_skills = treat_manifest["skill_files"]
    for name in base_skills.keys() | treatment_skills.keys():
        if name not in mutable_targets and base_skills.get(name) != treatment_skills.get(name):
            raise ValueError(f"baseline and treatment non-target skill differs: {name}")
    if base_artifacts.keys() != treat_artifacts.keys():
        raise ValueError("baseline and treatment artifacts are not one-to-one paired")
    for key in base_artifacts:
        base = base_artifacts[key]
        treatment_value = treat_artifacts[key]
        if base["prompt"] != treatment_value["prompt"]:
            raise ValueError(f"prompt differs for paired artifact {key}")
        if (base["provider"], base["model"]) != (
            treatment_value["provider"],
            treatment_value["model"],
        ):
            raise ValueError(f"observed provider/model differs for paired artifact {key}")
        if base_cases[key[0]]["kind"] == "repository":
            base_fixture = base["fixture"]
            treatment_fixture = treatment_value["fixture"]
            if any(
                base_fixture[field] != treatment_fixture[field]
                for field in ("id", "source", "initial_tree")
            ):
                raise ValueError(f"fixture metadata differs for paired artifact {key}")
            if (
                base_fixture["verifier"]["command"][:2]
                != treatment_fixture["verifier"]["command"][:2]
            ):
                raise ValueError(f"verifier metadata differs for paired artifact {key}")
    return base_manifest, treat_manifest, base_artifacts, treat_artifacts, base_cases


def require_grades(run: Path) -> dict[tuple[str, int], dict[str, Any]]:
    if not (run / "grade-summary.json").is_file() or not (run / "grades.jsonl").is_file():
        raise ValueError(f"{run}: deterministic grades are required before comparison or judgment")
    _, _, _, recomputed, summary = compute_grades(run)
    stored = read_jsonl(run / "grades.jsonl")
    if stored != recomputed or read_json(run / "grade-summary.json") != summary:
        raise ValueError(f"{run}: deterministic grades or their input binding are stale or modified")
    result: dict[tuple[str, int], dict[str, Any]] = {}
    for grade in stored:
        key = (grade["case_id"], grade["attempt"])
        if key in result:
            raise ValueError(f"{run}: duplicate deterministic grade {key}")
        result[key] = grade
    return result


def opaque_id(*parts: str) -> str:
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()[:16]



def judge_candidate(candidate_id: str, artifact: dict[str, Any]) -> dict[str, Any]:
    candidate = {"id": candidate_id, "response": artifact["response"]}
    if artifact["kind"] == "repository":
        candidate["evidence"] = {
            "diff": artifact["fixture"]["unified_diff"],
            "tree_diff": artifact["fixture"]["diff"],
            "verifier": artifact["fixture"]["verifier"]["checks"],
        }
    return candidate

def judge_payloads(baseline: Path, treatment: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise ValueError(f"{output}: output already exists")
    base_manifest, treat_manifest, base_artifacts, treat_artifacts, cases = paired_runs(
        baseline, treatment
    )
    require_grades(baseline)
    require_grades(treatment)
    payloads: list[dict[str, Any]] = []
    key: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "pairs": {}}
    for case_attempt, base_artifact in base_artifacts.items():
        case_id, attempt = case_attempt
        criteria = cases[case_id].get("judge_criteria", [])
        if not criteria:
            continue
        candidates = [("baseline", base_artifact), ("treatment", treat_artifacts[case_attempt])]
        blind = [
            (
                opaque_id(
                    base_manifest["run_id"],
                    treat_manifest["run_id"],
                    case_id,
                    str(attempt),
                    condition,
                ),
                condition,
                artifact,
            )
            for condition, artifact in candidates
        ]
        for order, ordered in (("forward", blind), ("swapped", list(reversed(blind)))):
            pair_id = opaque_id(
                case_id,
                str(attempt),
                base_manifest["run_id"],
                treat_manifest["run_id"],
                order,
            )
            payloads.append(
                {
                    "pair_id": pair_id,
                    "task": cases[case_id]["prompt"],
                    "criteria": criteria,
                    "candidate_a": judge_candidate(ordered[0][0], ordered[0][2]),
                    "candidate_b": judge_candidate(ordered[1][0], ordered[1][2]),
                    "response_contract": {
                        "winner": "A | B | tie",
                        "critical_issue": "boolean",
                        "rationale": "string",
                    },
                }
            )
            key["pairs"][pair_id] = {
                "case_id": case_id,
                "attempt": attempt,
                "A": ordered[0][1],
                "B": ordered[1][1],
                "order": order,
            }
    output.mkdir(parents=True)
    write_jsonl(output / "judge-payloads.jsonl", payloads)
    write_json(output / "judge-key.json", key)
    report = {
        "schema_version": SCHEMA_VERSION,
        "payloads": len(payloads),
        "swapped_pairs": len(payloads) // 2,
        "deterministic_grade_summaries": [
            str(baseline / "grade-summary.json"),
            str(treatment / "grade-summary.json"),
        ],
        "efficacy_claim": None,
    }
    write_json(output / "judge-payload-summary.json", report)
    return report


def score_judges(key_path: Path, results_path: Path, output: Path) -> dict[str, Any]:
    key_document = read_json(key_path)
    if key_document.get("schema_version") != SCHEMA_VERSION or not isinstance(key_document.get("pairs"), dict):
        raise ValueError(f"{key_path}: unsupported judge key schema")
    key = key_document["pairs"]
    results = read_jsonl(results_path)
    by_id: dict[str, dict[str, Any]] = {}
    for result in results:
        pair_id = result.get("pair_id")
        if not isinstance(pair_id, str) or pair_id not in key:
            raise ValueError(f"unknown pair_id: {pair_id}")
        if pair_id in by_id:
            raise ValueError(f"duplicate judge result: {pair_id}")
        if set(result) != {"pair_id", "winner", "critical_issue", "rationale"}:
            raise ValueError(f"{pair_id}: invalid judge result schema")
        if result["winner"] not in {"A", "B", "tie"}:
            raise ValueError(f"{pair_id}: winner must be A, B, or tie")
        if not isinstance(result["critical_issue"], bool) or not isinstance(result["rationale"], str):
            raise ValueError(f"{pair_id}: invalid critical_issue or rationale")
        by_id[pair_id] = result
    missing = set(key) - by_id.keys()
    if missing:
        raise ValueError(f"missing judge results: {', '.join(sorted(missing))}")
    votes: dict[tuple[str, int], dict[str, dict[str, Any]]] = {}
    for pair_id, result in by_id.items():
        pair = key[pair_id]
        if pair.get("order") not in {"forward", "swapped"}:
            raise ValueError(f"{pair_id}: invalid judge key order")
        winner = result["winner"]
        condition = "tie" if winner == "tie" else pair[winner]
        case_attempt = (pair["case_id"], pair["attempt"])
        orders = votes.setdefault(case_attempt, {})
        if pair["order"] in orders:
            raise ValueError(f"{case_attempt}: duplicate judge ordering")
        orders[pair["order"]] = {
            "vote": condition,
            "critical_issue": result["critical_issue"],
            "rationale": result["rationale"],
        }
    scored = []
    for (case_id, attempt), ordered_votes in sorted(votes.items()):
        if set(ordered_votes) != {"forward", "swapped"}:
            raise ValueError(f"{case_id}:{attempt}: missing judge ordering")
        ordered = [ordered_votes["forward"], ordered_votes["swapped"]]
        pair_votes = [vote["vote"] for vote in ordered]
        verdict = pair_votes[0] if pair_votes[0] == pair_votes[1] else "position-sensitive"
        scored.append(
            {
                "case_id": case_id,
                "attempt": attempt,
                "votes": pair_votes,
                "critical_issues": [vote["critical_issue"] for vote in ordered],
                "rationales": [vote["rationale"] for vote in ordered],
                "verdict": verdict,
            }
        )
    summary = {
        "schema_version": SCHEMA_VERSION,
        "pairs_scored": len(scored),
        "results": scored,
        "efficacy_claim": None,
        "reason": "Judge output is optional evidence and cannot replace deterministic paired merge gates.",
    }
    write_json(output, summary)
    return summary


def sum_metric(grades: dict[tuple[str, int], dict[str, Any]], name: str) -> int | float | None:
    values = [grade["metrics"].get(name) for grade in grades.values()]
    if any(value is None for value in values):
        return None
    return sum(values)


def paired_grade_counts(
    baseline: Path,
    treatment: Path,
    expected_split: str,
    expected_kind: str | None = None,
) -> dict[str, Any]:
    paired_runs(baseline, treatment)
    base = require_grades(baseline)
    treat = require_grades(treatment)
    if base.keys() != treat.keys():
        raise ValueError("deterministic grades are not one-to-one paired")
    wrong_split = [
        f"{case_id}:{attempt}"
        for (case_id, attempt), grade in base.items()
        if grade["split"] != expected_split
    ]
    if wrong_split:
        raise ValueError(
            f"{expected_split} gate received cases from another split: {', '.join(wrong_split)}"
        )
    if expected_kind is not None:
        wrong_kind = [
            f"{case_id}:{attempt}"
            for (case_id, attempt), grade in base.items()
            if grade["kind"] != expected_kind
        ]
        if wrong_kind:
            raise ValueError(
                f"{expected_split} gate requires {expected_kind} cases: {', '.join(wrong_kind)}"
            )
    critical_regressions = [
        f"{case_id}:{attempt}"
        for (case_id, attempt), grade in base.items()
        if grade["critical_passed"] and not treat[(case_id, attempt)]["critical_passed"]
    ]
    regressions = [
        f"{case_id}:{attempt}"
        for (case_id, attempt), grade in base.items()
        if grade["passed"] and not treat[(case_id, attempt)]["passed"]
    ]
    return {
        "baseline_passed": sum(grade["passed"] for grade in base.values()),
        "treatment_passed": sum(grade["passed"] for grade in treat.values()),
        "total": len(base),
        "critical_regressions": critical_regressions,
        "regressions": regressions,
        "baseline_metrics": {
            name: sum_metric(base, name) for name in ("tokens", "tool_events", "questions")
        },
        "treatment_metrics": {
            name: sum_metric(treat, name) for name in ("tokens", "tool_events", "questions")
        },
    }


def merge_gate(args: argparse.Namespace) -> dict[str, Any]:
    development = paired_grade_counts(
        args.development_baseline,
        args.development_treatment,
        "development",
        "repository",
    )
    holdout = paired_grade_counts(
        args.holdout_baseline,
        args.holdout_treatment,
        "holdout",
        "repository",
    )
    routing_holdout = paired_grade_counts(
        args.routing_holdout_baseline,
        args.routing_holdout_treatment,
        "holdout",
        "routing",
    )
    critical_regressions = [
        *development["critical_regressions"],
        *holdout["critical_regressions"],
        *routing_holdout["critical_regressions"],
    ]
    development_improved = (
        development["treatment_passed"] > development["baseline_passed"]
    )
    holdout_preserved = (
        not holdout["regressions"]
        and holdout["treatment_passed"] >= holdout["baseline_passed"]
    )
    routing_holdout_passed = (
        not routing_holdout["regressions"]
        and routing_holdout["treatment_passed"] == routing_holdout["total"]
    )
    increased: list[str] = []
    unknown: list[str] = []
    for split, result in (
        ("development", development),
        ("holdout", holdout),
        ("routing_holdout", routing_holdout),
    ):
        for metric in ("tokens", "tool_events", "questions"):
            baseline_value = result["baseline_metrics"][metric]
            treatment_value = result["treatment_metrics"][metric]
            if baseline_value is None or treatment_value is None:
                unknown.append(f"{split}:{metric}")
            elif treatment_value > baseline_value:
                increased.append(f"{split}:{metric}")
    cost_justified = not unknown and (
        not increased or bool(args.correctness_benefit)
    )
    passed = (
        not critical_regressions
        and development_improved
        and holdout_preserved
        and routing_holdout_passed
        and cost_justified
    )
    report = {
        "schema_version": SCHEMA_VERSION,
        "decision": "pass" if passed else "fail",
        "paired_evidence": True,
        "development": development,
        "holdout": holdout,
        "routing_holdout": routing_holdout,
        "criteria": {
            "no_critical_regressions": not critical_regressions,
            "development_improved": development_improved,
            "holdout_preserved": holdout_preserved,
            "routing_holdout_all_passed": routing_holdout_passed,
            "cost_metrics_known": not unknown,
            "increased_cost_has_correctness_benefit": cost_justified,
        },
        "increased_metrics": increased,
        "unknown_metrics": unknown,
        "correctness_benefit": args.correctness_benefit,
        "efficacy_claim": (
            "Treatment improved deterministic development results, preserved every passing holdout result, passed routing holdout, and introduced no undocumented critical or cost regression."
            if passed
            else None
        ),
    }
    write_json(args.output, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministically grade captured OMP evaluation artifacts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="grade one captured condition")
    run_parser.add_argument("run", type=Path)
    judge_parser = subparsers.add_parser(
        "judge-payload", help="create blinded and order-swapped optional judge inputs"
    )
    judge_parser.add_argument("--baseline", type=Path, required=True)
    judge_parser.add_argument("--treatment", type=Path, required=True)
    judge_parser.add_argument("--output", type=Path, required=True)
    score_parser = subparsers.add_parser(
        "judge-score", help="score real judge results against the separate blind key"
    )
    score_parser.add_argument("--key", type=Path, required=True)
    score_parser.add_argument("--results", type=Path, required=True)
    score_parser.add_argument("--output", type=Path, required=True)
    gate_parser = subparsers.add_parser(
        "gate", help="report the paired development and holdout merge gate"
    )
    gate_parser.add_argument("--development-baseline", type=Path, required=True)
    gate_parser.add_argument("--development-treatment", type=Path, required=True)
    gate_parser.add_argument("--holdout-baseline", type=Path, required=True)
    gate_parser.add_argument("--holdout-treatment", type=Path, required=True)
    gate_parser.add_argument("--routing-holdout-baseline", type=Path, required=True)
    gate_parser.add_argument("--routing-holdout-treatment", type=Path, required=True)
    gate_parser.add_argument("--correctness-benefit")
    gate_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "run":
            report = grade_run(args.run)
        elif args.command == "judge-payload":
            report = judge_payloads(args.baseline, args.treatment, args.output)
        elif args.command == "judge-score":
            report = score_judges(args.key, args.results, args.output)
        else:
            report = merge_gate(args)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, re.error) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if args.command == "gate" and report["decision"] != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
