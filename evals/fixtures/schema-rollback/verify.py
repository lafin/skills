#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path

PROFILE = {"display_name": "Ada Lovelace", "email": "ada@example.test"}
OLD_RECORD = {"version": 1, "name": "Ada Lovelace", "email": "ada@example.test"}
NEW_RECORD = {"version": 2, "profile": PROFILE}


def run_codec(root, *args):
    return subprocess.run(
        [sys.executable, str(root / "profile_codec.py"), *args],
        cwd=root,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )


def parsed_stdout(result):
    if result.returncode != 0:
        raise AssertionError(f"codec exited {result.returncode}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def add(checks, name, dimension, probe):
    try:
        probe()
    except Exception as exc:
        checks.append(
            {
                "name": name,
                "dimension": dimension,
                "critical": True,
                "passed": False,
                "detail": f"{type(exc).__name__}: {exc}",
            }
        )
    else:
        checks.append(
            {
                "name": name,
                "dimension": dimension,
                "critical": True,
                "passed": True,
                "detail": "observable contract satisfied",
            }
        )


def require_equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"expected {expected!r}, got {actual!r}")


def check_window(root):
    text = (root / "COMPATIBILITY.txt").read_text(encoding="utf-8")
    required = (
        "Release 4 introduces version 2",
        "Until the end of Release 5",
        "readers accept both version 1 and version 2",
        "rollback uses target_version=1",
    )
    missing = [phrase for phrase in required if phrase not in text]
    if missing:
        raise AssertionError(f"missing compatibility statement(s): {missing}")


def check_new_form(root):
    encoded = parsed_stdout(run_codec(root, "dump", PROFILE["display_name"], PROFILE["email"]))
    require_equal(encoded, NEW_RECORD)
    decoded = parsed_stdout(run_codec(root, "load", json.dumps(encoded, separators=(",", ":"))))
    require_equal(decoded, PROFILE)


def check_old_form(root):
    decoded = parsed_stdout(run_codec(root, "load", json.dumps(OLD_RECORD, separators=(",", ":"))))
    require_equal(decoded, PROFILE)


def check_rollback_form(root):
    encoded = parsed_stdout(
        run_codec(
            root,
            "dump",
            PROFILE["display_name"],
            PROFILE["email"],
            "--target-version",
            "1",
        )
    )
    require_equal(encoded, OLD_RECORD)
    legacy_profile = {"display_name": encoded["name"], "email": encoded["email"]}
    require_equal(legacy_profile, PROFILE)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    root = Path(sys.argv[1]).resolve()
    if not (root / "profile_codec.py").is_file():
        raise SystemExit("worktree does not contain profile_codec.py")

    checks = []
    add(checks, "compatibility_window_stated", "security_compatibility", lambda: check_window(root))
    add(checks, "new_version_round_trip", "security_compatibility", lambda: check_new_form(root))
    add(checks, "old_version_upgrade_read", "security_compatibility", lambda: check_old_form(root))
    add(checks, "rollback_version_downgrade", "security_compatibility", lambda: check_rollback_form(root))
    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()
