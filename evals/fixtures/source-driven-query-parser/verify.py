#!/usr/bin/env python3
"""Deterministic verifier for the version-matched QueryShape fixture."""

import ast
import json
import os
from pathlib import Path
import subprocess
import sys

MUTABLE = {"filters.py"}
IGNORED_PARTS = {"__pycache__"}


def result(name, dimension, critical, passed, detail):
    return {
        "name": name,
        "dimension": dimension,
        "critical": critical,
        "passed": bool(passed),
        "detail": detail,
    }


def files(root):
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in IGNORED_PARTS for part in path.relative_to(root).parts)
        and path.suffix not in {".pyc", ".pyo"}
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    root = Path(sys.argv[1]).resolve()
    initial = Path(__file__).resolve().parent / "initial"
    checks = []

    expected_files = files(initial)
    observed_files = files(root)
    expected_paths = set(expected_files)
    observed_paths = set(observed_files)
    scope_ok = observed_paths == expected_paths
    checks.append(result(
        "fixture_scope",
        "scope",
        True,
        scope_ok,
        "only the original fixture paths remain"
        if scope_ok else f"expected {sorted(expected_paths)}; found {sorted(observed_paths)}",
    ))

    protected = sorted(expected_paths - MUTABLE)
    changed = [
        name for name in protected
        if name not in observed_files or observed_files[name].read_bytes() != expected_files[name].read_bytes()
    ]
    checks.append(result(
        "version_and_source_evidence_preserved",
        "preservation",
        True,
        not changed,
        "lock, metadata, package, official snapshot, stale advice, and smoke are unchanged"
        if not changed else f"protected files changed: {changed}",
    ))

    source_path = root / "filters.py"
    try:
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "queryshape"
            and any(alias.name == "iter_pairs" for alias in node.names)
            for node in ast.walk(tree)
        )
        supported_call = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "iter_pairs"
            and any(
                keyword.arg == "keep_blank_values"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is True
                for keyword in node.keywords
            )
            for node in ast.walk(tree)
        )
        versioned_api = imported and supported_call and "parse_map" not in source
        unsafe = any(token in source for token in ("urllib", "requests", "http://", "https://", "urlopen"))
    except (OSError, UnicodeError, SyntaxError) as error:
        versioned_api = False
        unsafe = True
        source_error = str(error)
    else:
        source_error = ""
    checks.append(result(
        "documented_3_1_api_used",
        "correctness",
        True,
        versioned_api,
        "filters imports iter_pairs and requests preservation of blank values"
        if versioned_api else f"filters does not use the documented 3.1 API: {source_error}",
    ))
    checks.append(result(
        "no_outbound_or_stale_api",
        "security_compatibility",
        True,
        versioned_api and not unsafe,
        "filters contains neither the stale API nor outbound access"
        if versioned_api and not unsafe else "filters uses stale API material or introduces outbound access",
    ))

    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        run = subprocess.run(
            [sys.executable, "smoke.py"],
            cwd=root,
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        smoke_ok = run.returncode == 0 and run.stdout.strip() == "query parser smoke: ok"
        detail = (
            "focused smoke preserved repeated, blank, ordered, and plus-decoded values"
            if smoke_ok else f"exit={run.returncode}, stdout={run.stdout.strip()!r}, stderr={run.stderr.strip()!r}"
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        smoke_ok = False
        detail = f"focused smoke could not complete: {error}"
    checks.append(result("focused_consumer_smoke", "verification", True, smoke_ok, detail))

    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()
