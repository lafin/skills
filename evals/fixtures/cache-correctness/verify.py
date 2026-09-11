#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

PREFIX = """
import sys
sys.path.insert(0, sys.argv[1])
from catalog_service import CatalogService

class Clock:
    def __init__(self):
        self.now = 0
    def __call__(self):
        return self.now
"""

CASES = [
    (
        "catalog cache hit",
        "correctness",
        True,
        """
clock = Clock()
calls = []
def catalog(tenant, locale):
    calls.append((tenant, locale))
    return (tenant, locale, len(calls))
s = CatalogService(catalog, lambda *_: None, clock, ttl_seconds=10, max_entries=8)
assert s.handle('/catalog', 'acme', 'en') == s.handle('/catalog', 'acme', 'en')
assert calls == [('acme', 'en')]
""",
    ),
    (
        "tenant and locale isolation",
        "security_compatibility",
        True,
        """
clock = Clock()
calls = []
def catalog(tenant, locale):
    calls.append((tenant, locale))
    return (tenant, locale, len(calls))
s = CatalogService(catalog, lambda *_: None, clock, ttl_seconds=10, max_entries=8)
a = s.catalog('acme', 'en')
b = s.catalog('beta', 'en')
c = s.catalog('acme', 'fr')
assert len({a, b, c}) == 3
assert calls == [('acme', 'en'), ('beta', 'en'), ('acme', 'fr')]
""",
    ),
    (
        "freshness boundary",
        "correctness",
        True,
        """
clock = Clock()
calls = []
def catalog(tenant, locale):
    calls.append((tenant, locale))
    return len(calls)
s = CatalogService(catalog, lambda *_: None, clock, ttl_seconds=10, max_entries=8)
first = s.catalog('acme', 'en')
clock.now = 9
assert s.catalog('acme', 'en') == first
clock.now = 10
assert s.catalog('acme', 'en') != first
assert len(calls) == 2
""",
    ),
    (
        "targeted invalidation",
        "completeness",
        True,
        """
clock = Clock()
calls = []
def catalog(tenant, locale):
    calls.append((tenant, locale))
    return (tenant, locale, len(calls))
s = CatalogService(catalog, lambda *_: None, clock, ttl_seconds=10, max_entries=8)
ae = s.catalog('acme', 'en')
af = s.catalog('acme', 'fr')
be = s.catalog('beta', 'en')
s.invalidate('acme', 'en')
assert s.catalog('acme', 'en') != ae
assert s.catalog('acme', 'fr') == af
assert s.catalog('beta', 'en') == be
s.invalidate('acme')
assert s.catalog('acme', 'en') != ae
assert s.catalog('acme', 'fr') != af
assert s.catalog('beta', 'en') == be
""",
    ),
    (
        "bounded retention",
        "correctness",
        True,
        """
clock = Clock()
calls = []
def catalog(tenant, locale):
    calls.append((tenant, locale))
    return len(calls)
s = CatalogService(catalog, lambda *_: None, clock, ttl_seconds=10, max_entries=2)
keys = [('acme', 'en'), ('acme', 'fr'), ('beta', 'en')]
for key in keys:
    s.catalog(*key)
filled = len(calls)
for key in keys:
    s.catalog(*key)
assert len(calls) > filled
""",
    ),
    (
        "live route remains uncached",
        "correctness",
        True,
        """
clock = Clock()
calls = []
def live(tenant, locale):
    calls.append((tenant, locale))
    return len(calls)
s = CatalogService(lambda *_: None, live, clock, ttl_seconds=10, max_entries=8)
assert s.handle('/live-status', 'acme', 'en') == 1
assert s.handle('/live-status', 'acme', 'en') == 2
assert calls == [('acme', 'en'), ('acme', 'en')]
""",
    ),
]


def run_case(root, body):
    try:
        result = subprocess.run(
            [sys.executable, "-B", "-I", "-c", PREFIX + body, str(root)],
            stdin=subprocess.DEVNULL,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
            env={"PYTHONDONTWRITEBYTECODE": "1"},
        )
    except subprocess.TimeoutExpired:
        return False, "candidate check timed out"
    if result.returncode == 0:
        return True, "behavior observed"
    lines = (result.stderr or result.stdout).strip().splitlines()
    return False, lines[-1] if lines else f"candidate exited {result.returncode}"


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    root = Path(sys.argv[1]).resolve()
    checks = []
    source_path = root / "catalog_service.py"
    allowed_paths = {"catalog_service.py", "test_catalog_service.py"}
    actual_paths = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if (path.is_file() or path.is_symlink())
        and "__pycache__" not in path.relative_to(root).parts
        and path.suffix not in {".pyc", ".pyo"}
    }
    imports = []
    try:
        import ast

        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imports = [
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in (
                node.names
                if isinstance(node, ast.Import)
                else [ast.alias(name=node.module or "")]
            )
        ]
    except (OSError, SyntaxError):
        imports = ["<invalid-source>"]
    standard_library_only = actual_paths == allowed_paths and all(
        name in sys.stdlib_module_names for name in imports
    )
    checks.append(
        {
            "name": "standard library and fixture scope",
            "dimension": "scope",
            "critical": True,
            "passed": standard_library_only,
            "detail": (
                "only original fixture files and standard-library imports remain"
                if standard_library_only
                else f"paths={sorted(actual_paths)} imports={sorted(imports)}"
            ),
        }
    )
    for name, dimension, critical, body in CASES:
        passed, detail = run_case(root, body)
        checks.append(
            {
                "name": name,
                "dimension": dimension,
                "critical": critical,
                "passed": passed,
                "detail": detail,
            }
        )
    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()
