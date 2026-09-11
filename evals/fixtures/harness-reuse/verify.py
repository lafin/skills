#!/usr/bin/env python3
"""Deterministic verifier for reuse of the existing smoke harness."""

import json
import os
from pathlib import Path
import subprocess
import sys

ORIGINAL_SOURCE = '''"""Order pricing: quantities of 10 or more receive a 10% discount."""


def order_total_cents(quantity: int, unit_price_cents: int) -> int:
    if quantity < 1 or unit_price_cents < 0:
        raise ValueError("quantity must be positive and price cannot be negative")

    subtotal = quantity * unit_price_cents
    if quantity > 10:
        return subtotal * 90 // 100
    return subtotal
'''
EXPECTED_SOURCE = ORIGINAL_SOURCE.replace("if quantity > 10:", "if quantity >= 10:")
EXPECTED_SMOKE = '''"""Focused standard-library harness for the volume discount rule."""

import unittest

from discounts import order_total_cents


class VolumeDiscountSmoke(unittest.TestCase):
    def test_below_threshold_has_no_discount(self):
        self.assertEqual(order_total_cents(9, 100), 900)

    def test_threshold_receives_discount(self):
        self.assertEqual(order_total_cents(10, 100), 900)

    def test_above_threshold_receives_discount(self):
        self.assertEqual(order_total_cents(11, 100), 990)


if __name__ == "__main__":
    unittest.main()
'''
BLOCKED_NAMES = {
    "conftest.py",
    "package.json",
    "pipfile",
    "poetry.lock",
    "pyproject.toml",
    "pytest.ini",
    "requirements.txt",
    "setup.cfg",
    "setup.py",
    "tox.ini",
}


def result(name, dimension, critical, passed, detail):
    return {
        "name": name,
        "dimension": dimension,
        "critical": critical,
        "passed": bool(passed),
        "detail": detail,
    }


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        raise SystemExit(f"worktree is not a directory: {root}")

    checks = []
    source_text = read_text(root / "discounts.py")
    smoke_text = read_text(root / "smoke.py")
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    try:
        run = subprocess.run(
            [sys.executable, "smoke.py"],
            cwd=root,
            env=environment,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        harness_ok = run.returncode == 0 and "Ran 3 tests" in run.stderr and "OK" in run.stderr
        harness_detail = (
            "the existing unittest smoke harness passes all three pricing boundaries"
            if harness_ok else
            f"smoke harness exit={run.returncode}, stdout={run.stdout.strip()!r}, stderr={run.stderr.strip()!r}"
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        harness_ok = False
        harness_detail = f"smoke harness could not complete: {error}"
    checks.append(result(
        "existing_smoke_harness_passes",
        "correctness",
        True,
        harness_ok,
        harness_detail,
    ))

    source_ok = source_text == EXPECTED_SOURCE
    checks.append(result(
        "threshold_bug_fixed_surgically",
        "preservation",
        True,
        source_ok,
        "discounts.py changes only the exclusive threshold to an inclusive threshold"
        if source_ok else "discounts.py is missing the one-line threshold fix or contains unrelated changes",
    ))

    reused = smoke_text == EXPECTED_SMOKE
    checks.append(result(
        "standard_library_harness_reused",
        "verification",
        False,
        reused,
        "the existing unittest harness is preserved and used"
        if reused else "the existing unittest smoke harness was removed or modified",
    ))

    all_paths = [
        path
        for path in root.rglob("*")
        if (path.is_file() or path.is_symlink())
        and "__pycache__" not in path.relative_to(root).parts
        and path.suffix not in {".pyc", ".pyo"}
    ]
    relative_paths = {path.relative_to(root).as_posix() for path in all_paths}
    blocked = sorted(
        path.relative_to(root).as_posix()
        for path in all_paths
        if path.name.lower() in BLOCKED_NAMES
        or any(part.lower() in {"node_modules", ".venv"} for part in path.parts)
    )
    no_framework = not blocked
    checks.append(result(
        "no_dependency_or_framework_added",
        "scope",
        True,
        no_framework,
        "no dependency manifest, test framework configuration, or vendored environment was added"
        if no_framework else f"redundant dependency or framework files found: {blocked}",
    ))

    expected_paths = {"discounts.py", "smoke.py"}
    no_symlinks = not any(path.is_symlink() for path in all_paths)
    scope_ok = relative_paths == expected_paths and no_symlinks
    checks.append(result(
        "fixture_scope",
        "scope",
        False,
        scope_ok,
        "only the two original fixture files remain"
        if scope_ok else f"expected only {sorted(expected_paths)}; found {sorted(relative_paths)}",
    ))

    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()
