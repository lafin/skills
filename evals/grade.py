#!/usr/bin/env python3
"""Status: Reusable. Grade captured OMP artifacts and report paired merge gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 3
HASH = re.compile(r"[0-9a-f]{64}")
POLICY_FLAGS = {"extensions": "disabled", "rules": "disabled", "sessions": "disabled"}


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
    if required - case.keys():
        raise ValueError(f"{location}: incomplete case schema")
    if case["kind"] not in {"behavior", "routing"} or case["split"] not in {"development", "holdout"}:
        raise ValueError(f"{location}: invalid kind or split")
    if not all(isinstance(case[name], str) and case[name] for name in ("id", "target_skill", "prompt")):
        raise ValueError(f"{location}: invalid case identity")
    for name in ("observable_success", "prohibited_outcomes"):
        values = case[name]
        if not isinstance(values, list) or not values or not all(isinstance(item, str) and item for item in values):
            raise ValueError(f"{location}: invalid {name}")
    if not isinstance(case["checks"], list) or not case["checks"]:
        raise ValueError(f"{location}: checks must be non-empty")
    for check in case["checks"]:
        if (
            not isinstance(check, dict)
            or set(check) - {"name", "op", "value", "field", "critical"}
            or {"name", "op", "value", "critical"} - check.keys()
            or check["op"] not in {"contains", "not_contains", "equals", "regex", "not_regex"}
            or not isinstance(check["value"], str)
            or not isinstance(check["critical"], bool)
        ):
            raise ValueError(f"{location}: invalid deterministic check")
        if check["op"] in {"regex", "not_regex"}:
            re.compile(check["value"])
    if case["kind"] == "behavior":
        fields = case.get("response_fields")
        if not isinstance(fields, list) or not fields or len(fields) != len(set(fields)):
            raise ValueError(f"{location}: invalid response_fields")
    else:
        skills = case.get("available_skills")
        if (
            not isinstance(skills, list)
            or not skills
            or len(skills) != len(set(skills))
            or case["target_skill"] not in skills
        ):
            raise ValueError(f"{location}: invalid available_skills")


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
    if case["kind"] == "behavior":
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
    expected_skill_flag = (
        "--no-skills"
        if case["kind"] == "behavior" and manifest["condition"] == "baseline"
        else f"--skills={case['target_skill']}"
        if case["kind"] == "behavior"
        else f"--skills={','.join(sorted(manifest.get('skill_files', {})))}"
    )
    if expected_skill_flag not in command:
        raise ValueError(f"{path}: command skill scope differs from manifest")
    requests = artifact.get("rpc_requests")
    descriptions = {
        name: record["description"] for name, record in manifest["skill_files"].items()
    }
    expected_messages = (
        [f"/skill:{case['target_skill']}", case_prompt(case, descriptions)]
        if case["kind"] == "behavior" and manifest["condition"] == "treatment"
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
        or not isinstance(artifact.get("elapsed_seconds"), (int, float))
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
        results.append(
            {
                "name": check.get("name", f"check_{number}"),
                "critical": check["critical"],
                "passed": passed,
                "detail": detail,
            }
        )
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
                    "candidate_a": {"id": ordered[0][0], "response": ordered[0][2]["response"]},
                    "candidate_b": {"id": ordered[1][0], "response": ordered[1][2]["response"]},
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
    votes: dict[tuple[str, int], dict[str, str]] = {}
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
        orders[pair["order"]] = condition
    scored = []
    for (case_id, attempt), ordered_votes in sorted(votes.items()):
        if set(ordered_votes) != {"forward", "swapped"}:
            raise ValueError(f"{case_id}:{attempt}: missing judge ordering")
        pair_votes = [ordered_votes["forward"], ordered_votes["swapped"]]
        verdict = pair_votes[0] if pair_votes[0] == pair_votes[1] else "position-sensitive"
        scored.append(
            {"case_id": case_id, "attempt": attempt, "votes": pair_votes, "verdict": verdict}
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


def paired_grade_counts(baseline: Path, treatment: Path, expected_split: str) -> dict[str, Any]:
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
    if expected_split == "holdout":
        non_routing = [
            f"{case_id}:{attempt}"
            for (case_id, attempt), grade in base.items()
            if grade["kind"] != "routing"
        ]
        if non_routing:
            raise ValueError(f"holdout gate requires routing cases: {', '.join(non_routing)}")
    regressions = [
        f"{case_id}:{attempt}"
        for (case_id, attempt), grade in base.items()
        if grade["critical_passed"] and not treat[(case_id, attempt)]["critical_passed"]
    ]
    return {
        "baseline_passed": sum(grade["passed"] for grade in base.values()),
        "treatment_passed": sum(grade["passed"] for grade in treat.values()),
        "total": len(base),
        "critical_regressions": regressions,
        "baseline_metrics": {
            name: sum_metric(base, name) for name in ("tokens", "tool_events", "questions")
        },
        "treatment_metrics": {
            name: sum_metric(treat, name) for name in ("tokens", "tool_events", "questions")
        },
    }


def merge_gate(args: argparse.Namespace) -> dict[str, Any]:
    development = paired_grade_counts(
        args.development_baseline, args.development_treatment, "development"
    )
    holdout = paired_grade_counts(args.holdout_baseline, args.holdout_treatment, "holdout")
    critical_regressions = development["critical_regressions"] + holdout["critical_regressions"]
    development_improved = development["treatment_passed"] > development["baseline_passed"]
    holdout_preserved = holdout["treatment_passed"] >= holdout["baseline_passed"]
    increased: list[str] = []
    unknown: list[str] = []
    for split, result in (("development", development), ("holdout", holdout)):
        for metric in ("tokens", "tool_events", "questions"):
            baseline_value = result["baseline_metrics"][metric]
            treatment_value = result["treatment_metrics"][metric]
            if baseline_value is None or treatment_value is None:
                unknown.append(f"{split}:{metric}")
            elif treatment_value > baseline_value:
                increased.append(f"{split}:{metric}")
    cost_justified = not unknown and (not increased or bool(args.correctness_benefit))
    passed = (
        not critical_regressions
        and development_improved
        and holdout_preserved
        and cost_justified
    )
    report = {
        "schema_version": SCHEMA_VERSION,
        "decision": "pass" if passed else "fail",
        "paired_evidence": True,
        "development": development,
        "holdout": holdout,
        "criteria": {
            "no_critical_regressions": not critical_regressions,
            "development_improved": development_improved,
            "holdout_preserved": holdout_preserved,
            "cost_metrics_known": not unknown,
            "increased_cost_has_correctness_benefit": cost_justified,
        },
        "increased_metrics": increased,
        "unknown_metrics": unknown,
        "correctness_benefit": args.correctness_benefit,
        "efficacy_claim": (
            "Treatment improved deterministic development results, preserved holdout routing, and introduced no undocumented critical or cost regression."
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
