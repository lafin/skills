#!/usr/bin/env python3

import importlib.util
import inspect
import json
import sys
from pathlib import Path

EXPECTED_FILES = {"alerts.py", "consumer.py"}


def load(root, name):
    spec = importlib.util.spec_from_file_location(name, root / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def add(checks, name, probe):
    try:
        probe()
    except Exception as exc:
        checks.append({"name": name, "dimension": "interface_minimality", "critical": True, "passed": False, "detail": f"{type(exc).__name__}: {exc}"})
    else:
        checks.append({"name": name, "dimension": "interface_minimality", "critical": True, "passed": True, "detail": "observable contract satisfied"})


def equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"expected {expected!r}, got {actual!r}")


def invalid_severity(alerts):
    try:
        alerts.build_notice("Disk nearly full", severity="urgent")
    except ValueError as exc:
        equal(str(exc), "severity must be one of: info, warning, critical")
    else:
        raise AssertionError("invalid severity was accepted")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    root = Path(sys.argv[1]).resolve()
    alerts = load(root, "alerts")
    consumer = load(root, "consumer")
    checks = []

    add(checks, "old_consumer_contract", lambda: (equal(alerts.build_notice("Saved"), {"kind": "notice", "message": "Saved"}), equal(consumer.render("Saved"), "notice: Saved")))
    add(checks, "severity_contract", lambda: equal(alerts.build_notice("Disk nearly full", severity="warning"), {"kind": "notice", "message": "Disk nearly full", "severity": "warning"}))
    add(checks, "severity_validation", lambda: invalid_severity(alerts))
    add(checks, "direct_signature", lambda: equal(str(inspect.signature(alerts.build_notice)), "(message, severity=None)"))
    add(checks, "no_new_runtime_surface", lambda: equal({path.name for path in root.iterdir() if path.is_file() and path.suffix == ".py"}, EXPECTED_FILES))
    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()
