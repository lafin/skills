#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

PREFIX = """
import sys
sys.path.insert(0, sys.argv[1])
from metrics import billable_bytes
"""


def run(root, body):
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
        return None, "candidate check timed out"
    if result.returncode != 0:
        lines = (result.stderr or result.stdout).strip().splitlines()
        return None, lines[-1] if lines else f"candidate exited {result.returncode}"
    return result.stdout.strip().splitlines(), "behavior observed"


def check_assertion(root, body):
    output, detail = run(root, body)
    return output is not None, detail


def check_allocations(root):
    output, detail = run(
        root,
        """
import json
import tracemalloc
events = tuple(('ready' if number % 3 else 'dropped', number) for number in range(80_000))
expected = sum(number for number in range(80_000) if number % 3)
tracemalloc.start()
try:
    actual = billable_bytes(events)
    _, peak = tracemalloc.get_traced_memory()
finally:
    tracemalloc.stop()
print(json.dumps({'actual': actual, 'expected': expected, 'peak': peak}))
""",
    )
    if output is None:
        return False, detail
    try:
        observation = json.loads(output[-1])
    except (IndexError, json.JSONDecodeError, TypeError):
        return False, "allocation workload did not report a result"
    if observation.get("actual") != observation.get("expected"):
        return False, "hot-path result changed"
    peak = observation.get("peak")
    if not isinstance(peak, int):
        return False, "allocation workload did not report peak bytes"
    if peak >= 65_536:
        return False, f"hot path allocated {peak} bytes; limit is 65535"
    return True, f"hot path allocated {peak} bytes; limit is 65535"


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    root = Path(sys.argv[1]).resolve()
    behavior, behavior_detail = check_assertion(
        root,
        """
events = (('ready', 12), ('dropped', 100), ('ready', 8), ('ready', 0))
assert billable_bytes(events) == 20
assert billable_bytes(()) == 0
""",
    )
    iterable, iterable_detail = check_assertion(
        root,
        """
events = (('ready' if number % 2 else 'dropped', number) for number in range(10))
assert billable_bytes(events) == 25
""",
    )
    allocation, allocation_detail = check_allocations(root)
    checks = [
        {
            "name": "aggregation behavior preserved",
            "dimension": "correctness",
            "critical": True,
            "passed": behavior,
            "detail": behavior_detail,
        },
        {
            "name": "one-shot iterable support",
            "dimension": "completeness",
            "critical": True,
            "passed": iterable,
            "detail": iterable_detail,
        },
        {
            "name": "deterministic allocation ceiling",
            "dimension": "verification",
            "critical": True,
            "passed": allocation,
            "detail": allocation_detail,
        },
    ]
    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()
