#!/usr/bin/env python3
"""Status: Reusable. Exercise the leancode hook through OMP RPC."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MARKER_PROMPT = 'Reply exactly LIFECYCLE_DONE while preserving this quoted data string: "[omp:leancode-state]".'
MODE_TASKS = (
    (
        "framework",
        "A user explicitly asks for a configurable plugin framework around one existing JSON "
        "exporter, and no second format is planned. Apply the current leancode intensity. "
        "Reply with exactly one line: DECISION: implement|simplify|challenge; REASON: <brief reason>.",
    ),
    (
        "cache",
        'A user explicitly asks: "Add a cache for these API responses." No profiling, freshness, '
        "invalidation, or tenant-key requirements are available. Apply the current leancode "
        "intensity. Reply with exactly one line: DECISION: implement|simplify|challenge; "
        "REASON: <brief reason>.",
    ),
)
MODES = ("lite", "full", "ultra", "off")


def load_capture_module():
    spec = importlib.util.spec_from_file_location("leancode_eval_run", ROOT / "evals/run.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load evals/run.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def rpc_command(args: argparse.Namespace) -> list[str]:
    command = [
        args.omp,
        "--mode=rpc",
        "--no-rules",
        "--no-session",
        "--no-skills",
        "--no-tools",
        f"--cwd={ROOT}",
        f"--profile={args.profile}",
        f"--model={args.model}",
        f"--thinking={args.thinking}",
        f"--max-time={args.max_time}",
        f"--extension={ROOT / '.omp/hooks/pre/leancode.ts'}",
    ]
    command.extend(f"--config={path}" for path in args.config)
    return command


def ui_record(event: dict[str, Any]) -> dict[str, Any] | None:
    if event.get("type") != "extension_ui_request":
        return None
    record = {key: event[key] for key in ("method", "statusKey", "statusText", "message", "notifyType") if key in event}
    args = event.get("args")
    if isinstance(args, dict):
        record.update({key: args[key] for key in ("statusKey", "statusText", "message", "notifyType") if key in args})
    return record


def rpc_lifecycle_capture(
    command: list[str],
    cwd: Path,
    requests: list[dict[str, Any]],
    timeout: float,
    environment: dict[str, str],
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
            env=environment,
        )
        assert process.stdin is not None and process.stdout is not None
        line_queue: queue.Queue[str | None] = queue.Queue()

        def read_stdout() -> None:
            for line in process.stdout:
                line_queue.put(line)
            line_queue.put(None)

        threading.Thread(target=read_stdout, daemon=True).start()

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
            try:
                line = line_queue.get(timeout=remaining)
            except queue.Empty:
                parse_errors.append("RPC capture timed out before a terminal result")
                break
            if line is None:
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
            if event.get("type") == "extension_ui_request" and isinstance(event.get("id"), str):
                process.stdin.write(
                    json.dumps(
                        {"type": "extension_ui_response", "id": event["id"], "cancelled": True},
                        separators=(",", ":"),
                    )
                    + "\n"
                )
                process.stdin.flush()
            if event.get("type") == "ready" and request_index == 0:
                send_request()
                continue
            if request_index == 0:
                continue
            current = requests[request_index - 1]
            local_result = (
                event.get("id") == current["id"]
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
                completed_ids.append(current["id"])
                if request_index < len(requests) and event.get("success") is not False:
                    send_request()
                else:
                    terminal_kind = "agent_end" if agent_result else "prompt_result"
                    break
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


def capture_process(
    capture: Any, args: argparse.Namespace, messages: list[str], label: str
) -> dict[str, Any]:
    requests = [
        {"id": f"{label}-{index}", "type": "prompt", "message": message}
        for index, message in enumerate(messages, 1)
    ]
    code, stdout, stderr, events, parse_errors, terminal = rpc_lifecycle_capture(
        rpc_command(args),
        ROOT,
        requests,
        capture.seconds(args.max_time) + 30,
        capture.capture_environment(),
    )
    ui = [record for event in events if (record := ui_record(event)) is not None]
    responses = [
        {
            "id": event.get("id"),
            "command": event.get("command"),
            "success": event.get("success"),
            "error": event.get("error"),
        }
        for event in events
        if event.get("type") == "response"
    ]
    return {
        "label": label,
        "command": rpc_command(args),
        "requests": requests,
        "exit_code": code,
        "raw_stdout": stdout,
        "raw_stderr": stderr,
        "event_parse_errors": parse_errors,
        "terminal_state": terminal,
        "ui": ui,
        "responses": responses,
        "summary": capture.summarize_events(events),
    }


def status_texts(run: dict[str, Any]) -> list[str]:
    return [
        record["statusText"]
        for record in run["ui"]
        if record.get("method") == "setStatus" and record.get("statusKey") == "leancode"
    ]


def notification_texts(run: dict[str, Any]) -> list[str]:
    return [record["message"] for record in run["ui"] if record.get("method") == "notify"]


def terminal_user_texts(run: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    for event in run["summary"]["terminal_events"]:
        for message in event.get("messages", []):
            if message.get("role") != "user":
                continue
            for part in message.get("content", []):
                if part.get("type") == "text" and isinstance(part.get("text"), str):
                    texts.append(part["text"])
    return texts

def terminal_leancode_reminders(run: dict[str, Any]) -> list[str]:
    return [
        part["text"]
        for event in run["summary"]["terminal_events"]
        for message in event.get("messages", [])
        if message.get("role") == "user" and message.get("attribution") == "agent"
        for part in message.get("content", [])
        if part.get("type") == "text"
        and isinstance(part.get("text"), str)
        and "[omp:leancode-state]" in part["text"]
    ]


def model_observed(run: dict[str, Any], requested: str) -> bool:
    provider, model = requested.split("/", 1)
    expected = {"provider": provider, "model": model}
    turns = run["summary"]["model_turns"]
    return bool(turns) and all(turn == expected for turn in turns)


def process_passed(run: dict[str, Any], requested_model: str) -> bool:
    return (
        run["exit_code"] == 0
        and not run["event_parse_errors"]
        and run["terminal_state"].get("received") is True
        and run["terminal_state"].get("terminal_result") == "agent_end"
        and all(response.get("success") is True for response in run["responses"])
        and model_observed(run, requested_model)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Exercise leancode modes, reload, and process reset through OMP RPC.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--config", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--omp", default="omp")
    parser.add_argument("--thinking", default="off")
    parser.add_argument("--max-time", default="3m")
    parser.add_argument("--behavior-attempts", type=int, default=0)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("--output must not exist")
    if args.behavior_attempts < 0:
        parser.error("--behavior-attempts must be non-negative")
    if args.model.count("/") != 1 or any(not part for part in args.model.split("/", 1)):
        parser.error("--model must be an exact provider/model name")

    args.config = [path.resolve() for path in args.config]
    for path in args.config:
        if not path.is_file():
            parser.error(f"config file does not exist: {path}")
    capture = load_capture_module()
    preflight_args = argparse.Namespace(
        omp=args.omp,
        profile=args.profile,
        config=args.config,
        cwd=ROOT,
    )
    try:
        profile_config = capture.effective_config(preflight_args)
        executable = Path(os.path.realpath(shutil.which(args.omp) or args.omp))
        version_code, omp_version, version_stderr = capture.run_text(
            [str(executable), "--version"], ROOT
        )
        if version_code:
            raise ValueError(f"cannot execute OMP: {version_stderr.strip()}")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    lifecycle = capture_process(
        capture,
        args,
        [
            "/leancode lite",
            "/leancode full",
            "/leancode ultra",
            "/leancode off",
            "/reload",
            "/leancode",
            MARKER_PROMPT,
        ],
        "lifecycle",
    )
    restarted = capture_process(
        capture,
        args,
        ["Reply exactly RESTART_DONE"],
        "restart",
    )
    mode_behaviors: list[dict[str, Any]] = []
    for task_id, task in MODE_TASKS:
        for mode in MODES:
            for attempt in range(1, args.behavior_attempts + 1):
                run = capture_process(
                    capture,
                    args,
                    [f"/leancode {mode}", task],
                    f"mode-{task_id}-{mode}-{attempt}",
                )
                mode_behaviors.append(
                    {"task": task_id, "mode": mode, "attempt": attempt, "run": run}
                )

    lifecycle_statuses = status_texts(lifecycle)
    lifecycle_notifications = notification_texts(lifecycle)
    restart_statuses = status_texts(restarted)
    lifecycle_user_texts = terminal_user_texts(lifecycle)
    checks = {
        "lifecycle_process_passed": process_passed(lifecycle, args.model),
        "mode_sequence_observed": lifecycle_statuses[:5]
        == ["lean:full", "lean:lite", "lean:full", "lean:ultra", "lean:off"],
        "restart_process_passed": process_passed(restarted, args.model),
        "mode_notifications_observed": lifecycle_notifications[:4]
        == ["leancode lite", "leancode full", "leancode ultra", "leancode off"],
        "fresh_process_defaults_full": restart_statuses[:1] == ["lean:full"],
        "reload_observation_recorded": any(
            response.get("id") == "lifecycle-5" and response.get("success") is True
            for response in lifecycle["responses"]
        ),
        "reload_preserved_off": lifecycle_notifications[4:5]
        == ["leancode: off (use lite|full|ultra|off)"],
        "quoted_marker_preserved": MARKER_PROMPT in lifecycle_user_texts,
    }
    if mode_behaviors:
        checks.update(
            {
                "mode_task_runs_passed": all(
                    process_passed(item["run"], args.model) for item in mode_behaviors
                ),
                "mode_task_selections_observed": all(
                    status_texts(item["run"])[-1:] == [f"lean:{item['mode']}"]
                    for item in mode_behaviors
                ),
                "mode_task_reminders_observed": all(
                    any(
                        ("Leancode is OFF" if item["mode"] == "off" else f"ACTIVE at {item['mode']}")
                        in reminder
                        for reminder in terminal_leancode_reminders(item["run"])
                    )
                    for item in mode_behaviors
                ),
                "mode_task_outputs_present": all(
                    bool(item["run"]["summary"]["response"].strip())
                    for item in mode_behaviors
                ),
            }
        )
    report = {
        "schema_version": 3,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "runtime": "omp-rpc",
        "model": args.model,
        "profile": args.profile,
        "thinking": args.thinking,
        "inputs": {
            "omp_executable": {
                "path": str(executable),
                "sha256": capture.sha256_file(executable),
            },
            "omp_version": omp_version.strip(),
            "hook": {
                "path": str(ROOT / ".omp/hooks/pre/leancode.ts"),
                "sha256": capture.sha256_file(ROOT / ".omp/hooks/pre/leancode.ts"),
            },
            "mode_smoke_sha256": capture.sha256_file(Path(__file__)),
            "run_py_sha256": capture.sha256_file(ROOT / "evals/run.py"),
            "config_files": [
                {"path": str(path), "sha256": capture.sha256_file(path)}
                for path in args.config
            ],
            "effective_omp_config": profile_config,
        },
        "lifecycle_statuses": lifecycle_statuses,
        "lifecycle_notifications": lifecycle_notifications,
        "lifecycle_user_texts": lifecycle_user_texts,
        "restart_statuses": restart_statuses,
        "checks": checks,
        "reload_effect": {
            "status_events_after_mode_sequence": lifecycle_statuses[5:],
            "mode_query_notification": (
                lifecycle_notifications[4] if len(lifecycle_notifications) > 4 else None
            ),
        },
        "mode_behavior": [
            {
                "task": item["task"],
                "mode": item["mode"],
                "attempt": item["attempt"],
                "response": item["run"]["summary"]["response"],
                "usage": item["run"]["summary"]["usage"],
                "runtime": item["run"]["summary"]["runtime"],
                "tool_call_count": item["run"]["summary"]["tool_call_count"],
            }
            for item in mode_behaviors
        ],
        "runs": [lifecycle, restarted, *(item["run"] for item in mode_behaviors)],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": checks}, sort_keys=True))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
