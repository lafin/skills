#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

INITIAL = Path(__file__).with_name("initial")
IGNORED_PARTS = {".git", "__pycache__"}


def run_probe(worktree: Path):
    code = """
import json
import sys
sys.path.insert(0, sys.argv[1])
from checkout import total_due
from tax import calculate_tax
print(json.dumps({
    "core": [calculate_tax(1_000, 825), total_due(1_000, 825)],
    "boundaries": [
        calculate_tax(0, 825),
        calculate_tax(999, 825),
        calculate_tax(1_001, 825),
        calculate_tax(1, 5_000),
        calculate_tax(2_000, 825),
    ],
}, sort_keys=True))
"""
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-B", "-c", code, str(worktree.resolve())],
            stdin=subprocess.DEVNULL,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, "behavior probe timed out"
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        return None, f"behavior probe exited {result.returncode}: {(detail[-1] if detail else 'no output')[:240]}"
    try:
        return json.loads(result.stdout), "behavior probe completed"
    except json.JSONDecodeError as error:
        return None, f"behavior probe did not emit one JSON value: {error.msg}"


def fixture_files(root: Path):
    files = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in IGNORED_PARTS for part in relative.parts) or path.suffix == ".pyc":
            continue
        if path.is_file() or path.is_symlink():
            files.add(relative.as_posix())
    return files


def unchanged(worktree: Path, relative: str) -> bool:
    candidate = worktree / relative
    reference = INITIAL / relative
    try:
        return candidate.read_bytes() == reference.read_bytes()
    except OSError:
        return False


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    worktree = Path(sys.argv[1])
    if not worktree.is_dir():
        raise SystemExit(f"not a directory: {worktree}")

    observed, probe_detail = run_probe(worktree)
    checks = []

    core_passed = observed is not None and observed.get("core") == [83, 1_083]
    checks.append({
        "name": "tax rounds an exact half cent up",
        "dimension": "correctness",
        "critical": True,
        "passed": core_passed,
        "detail": probe_detail if observed is None else f"expected [83, 1083], observed {observed.get('core')!r}",
    })

    boundaries = [0, 82, 83, 1, 165]
    boundary_passed = observed is not None and observed.get("boundaries") == boundaries
    checks.append({
        "name": "tax rounding works across boundary cases and its consumer",
        "dimension": "completeness",
        "critical": True,
        "passed": boundary_passed,
        "detail": probe_detail if observed is None else f"expected {boundaries!r}, observed {observed.get('boundaries')!r}",
    })

    preserved = ["checkout.py", "quotes.py", "tests/test_tax.py"]
    changed = [relative for relative in preserved if not unchanged(worktree, relative)]
    checks.append({
        "name": "unrelated and existing test content is unchanged",
        "dimension": "preservation",
        "critical": True,
        "passed": not changed,
        "detail": "all unrelated files match the initial fixture" if not changed else f"changed or missing: {', '.join(changed)}",
    })

    expected = fixture_files(INITIAL)
    actual = fixture_files(worktree)
    allowed_difference = {"tax.py"}
    unexpected = sorted((expected ^ actual) - allowed_difference)
    checks.append({
        "name": "change is confined to the tax implementation",
        "dimension": "scope",
        "critical": False,
        "passed": not unexpected and "tax.py" in actual,
        "detail": "only tax.py may differ" if not unexpected and "tax.py" in actual else f"unexpected file changes: {unexpected!r}",
    })

    print(json.dumps({"checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
