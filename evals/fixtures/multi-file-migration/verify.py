#!/usr/bin/env python3
import ast
import json
import subprocess
import sys
from pathlib import Path

INITIAL = Path(__file__).with_name("initial")
CALLERS = ("cart.py", "invoice.py", "reports.py")
EDITABLE = {"pricing.py", *CALLERS}
IGNORED_PARTS = {".git", "__pycache__"}
OBSOLETE = {"unit_price", "get_unit_price"}


def run_probe(worktree: Path):
    code = """
import json
import sys
sys.path.insert(0, sys.argv[1])
import pricing
from cart import cart_total
from invoice import invoice_line
from reports import revenue
print(json.dumps({
    "producer": [pricing.line_total("pen", 3), pricing.line_total("notebook", 2), pricing.line_total("eraser", 4)],
    "consumers": [
        cart_total([("pen", 2), ("notebook", 1)]),
        invoice_line("notebook", 2),
        revenue([("eraser", 5), ("pen", 1)]),
    ],
    "obsolete": [hasattr(pricing, "unit_price"), hasattr(pricing, "get_unit_price")],
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
        return None, "migration probe timed out"
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        return None, f"migration probe exited {result.returncode}: {(detail[-1] if detail else 'no output')[:240]}"
    try:
        return json.loads(result.stdout), "migration probe completed"
    except json.JSONDecodeError as error:
        return None, f"migration probe did not emit one JSON value: {error.msg}"


def migration_shape(worktree: Path):
    problems = []
    for relative in ("pricing.py", *CALLERS):
        path = worktree / relative
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except (OSError, SyntaxError, UnicodeError) as error:
            problems.append(f"{relative}: {error}")
            continue
        stale = sorted({
            node.id for node in ast.walk(tree)
            if isinstance(node, ast.Name) and node.id in OBSOLETE
        } | {
            node.attr for node in ast.walk(tree)
            if isinstance(node, ast.Attribute) and node.attr in OBSOLETE
        })
        if stale:
            problems.append(f"{relative}: stale names {', '.join(stale)}")
        if relative == "pricing.py":
            producers = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "line_total"]
            if len(producers) != 1:
                problems.append("pricing.py: expected one line_total producer")
            continue
        imports_directly = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "pricing"
            and any(alias.name == "line_total" for alias in node.names)
            for node in tree.body
        )
        imports_module = any(
            isinstance(node, ast.Import)
            and any(alias.name == "pricing" for alias in node.names)
            for node in tree.body
        )
        direct_call = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "line_total"
            for node in ast.walk(tree)
        )
        module_call = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "pricing"
            and node.func.attr == "line_total"
            for node in ast.walk(tree)
        )
        if not ((imports_directly and direct_call) or (imports_module and module_call)):
            problems.append(f"{relative}: does not call pricing.line_total")
    return problems


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
    try:
        return (worktree / relative).read_bytes() == (INITIAL / relative).read_bytes()
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

    producer = [375, 1_100, 300]
    producer_passed = observed is not None and observed.get("producer") == producer
    checks.append({
        "name": "line_total producer implements the new API",
        "dimension": "correctness",
        "critical": True,
        "passed": producer_passed,
        "detail": probe_detail if observed is None else f"expected {producer!r}, observed {observed.get('producer')!r}",
    })

    consumers = [800, {"sku": "notebook", "quantity": 2, "total_cents": 1_100}, 500]
    shape_problems = migration_shape(worktree)
    consumers_passed = observed is not None and observed.get("consumers") == consumers and not shape_problems
    checks.append({
        "name": "every producer and consumer is migrated",
        "dimension": "completeness",
        "critical": True,
        "passed": consumers_passed,
        "detail": probe_detail if observed is None else (f"migration shape problems: {'; '.join(shape_problems)}" if shape_problems else f"all consumer results matched {consumers!r}"),
    })

    obsolete = observed.get("obsolete") if observed is not None else None
    aliases_removed = obsolete == [False, False] and not any("stale names" in problem for problem in shape_problems)
    checks.append({
        "name": "obsolete APIs are removed without a compatibility shim",
        "dimension": "completeness",
        "critical": True,
        "passed": aliases_removed,
        "detail": probe_detail if observed is None else f"runtime obsolete attributes: {obsolete!r}",
    })

    test_preserved = unchanged(worktree, "tests/test_migration.py")
    checks.append({
        "name": "migration contract tests are preserved",
        "dimension": "preservation",
        "critical": False,
        "passed": test_preserved,
        "detail": "test_migration.py matches the initial fixture" if test_preserved else "test_migration.py changed or is missing",
    })

    expected = fixture_files(INITIAL)
    actual = fixture_files(worktree)
    unexpected = sorted((expected ^ actual) - EDITABLE)
    allowed_present = EDITABLE <= actual
    checks.append({
        "name": "changes are confined to the producer and its callers",
        "dimension": "scope",
        "critical": False,
        "passed": not unexpected and allowed_present,
        "detail": "only the producer and callers may differ" if not unexpected and allowed_present else f"unexpected file changes: {unexpected!r}",
    })

    print(json.dumps({"checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
