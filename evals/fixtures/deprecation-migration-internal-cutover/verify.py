#!/usr/bin/env python3
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

INITIAL = Path(__file__).with_name("initial")
EDITABLE = {"totals.py", "checkout.py", "receipt.py"}
OBSOLETE = "legacy_total_cents"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def python_files(root):
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def stale_references(worktree):
    found = []
    for path in python_files(worktree):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as error:
            found.append(f"{path.relative_to(worktree)}: {error}")
            continue
        for node in ast.walk(tree):
            names = []
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.append(node.name)
            elif isinstance(node, ast.Name):
                names.append(node.id)
            elif isinstance(node, ast.Attribute):
                names.append(node.attr)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                names.extend(alias.name for alias in node.names)
                names.extend(alias.asname for alias in node.names if alias.asname)
            if OBSOLETE in names:
                found.append(f"{path.relative_to(worktree)}:{getattr(node, 'lineno', '?')}")
    return found


def run_contract(worktree):
    code = """
import json
import totals
from checkout import checkout_total
from receipt import receipt_summary
items = [(250, 2), (125, 3)]
print(json.dumps({
    "producer": totals.calculate_total_cents(items),
    "checkout": checkout_total(items),
    "receipt": receipt_summary(items),
    "obsolete_present": hasattr(totals, "legacy_total_cents"),
}, sort_keys=True))
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code], cwd=worktree, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10,
        )
    except subprocess.TimeoutExpired:
        return None, "consumer contract timed out"
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        return None, f"consumer contract exited {result.returncode}: {(detail[-1] if detail else 'no output')[:240]}"
    try:
        return json.loads(result.stdout), "consumer contract completed"
    except json.JSONDecodeError as error:
        return None, f"consumer contract emitted invalid JSON: {error.msg}"


def changed_outside_scope(worktree):
    problems = []
    expected = {path.relative_to(INITIAL).as_posix() for path in INITIAL.rglob("*") if path.is_file()}
    actual = {path.relative_to(worktree).as_posix() for path in worktree.rglob("*") if path.is_file() and "__pycache__" not in path.parts}
    for relative in sorted(expected | actual):
        if relative in EDITABLE:
            continue
        source = INITIAL / relative
        target = worktree / relative
        if not source.is_file() or not target.is_file() or digest(source) != digest(target):
            problems.append(relative)
    return problems


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    worktree = Path(sys.argv[1])
    observed, detail = run_contract(worktree)
    expected = {
        "producer": 875,
        "checkout": 875,
        "receipt": {"item_count": 5, "total_cents": 875},
        "obsolete_present": False,
    }
    stale = stale_references(worktree)
    scope = changed_outside_scope(worktree)
    checks = [
        {
            "name": "replacement and consumers preserve observable totals",
            "dimension": "correctness",
            "critical": True,
            "passed": observed == expected,
            "detail": detail if observed is None else f"expected {expected!r}, observed {observed!r}",
        },
        {
            "name": "obsolete internal API is removed without an alias",
            "dimension": "completeness",
            "critical": True,
            "passed": observed is not None and observed.get("obsolete_present") is False and not stale,
            "detail": f"stale references: {stale!r}" if stale else "no obsolete definition, import, call, or runtime attribute remains",
        },
        {
            "name": "cutover changes stay within producer and callers",
            "dimension": "scope",
            "critical": False,
            "passed": not scope,
            "detail": f"out-of-scope changes: {scope!r}" if scope else "consumer contract test and unrelated files are unchanged",
        },
    ]
    print(json.dumps({"checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
