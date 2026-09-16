#!/usr/bin/env python3

import importlib.util
import json
import sys
import threading
from pathlib import Path


def load(root):
    spec = importlib.util.spec_from_file_location("payments", root / "payments.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["payments"] = module
    spec.loader.exec_module(module)
    return module


class Gateway:
    def __init__(self, block=False):
        self.calls = []
        self.block = block
        self.entered = threading.Event()
        self.release = threading.Event()

    def charge(self, order_id, amount_cents):
        self.calls.append((order_id, amount_cents))
        self.entered.set()
        if self.block and not self.release.wait(2):
            raise RuntimeError("gateway release timed out")
        return {"chargeId": f"ch-{len(self.calls)}", "orderId": order_id, "amountCents": amount_cents}


def add(checks, name, probe):
    try:
        probe()
    except Exception as exc:
        checks.append({"name": name, "dimension": "idempotency_contract", "critical": True, "passed": False, "detail": f"{type(exc).__name__}: {exc}"})
    else:
        checks.append({"name": name, "dimension": "idempotency_contract", "critical": True, "passed": True, "detail": "observable contract satisfied"})


def equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"expected {expected!r}, got {actual!r}")


def sequential(module):
    gateway = Gateway()
    api = module.PaymentAPI(gateway)
    first = api.post_charge("ord-7", 2500, "intent-7")
    second = api.post_charge("ord-7", 2500, "intent-7")
    equal(first, (201, {"chargeId": "ch-1", "orderId": "ord-7", "amountCents": 2500}))
    equal(second, first)
    equal(gateway.calls, [("ord-7", 2500)])


def changed_payload(module):
    gateway = Gateway()
    api = module.PaymentAPI(gateway)
    api.post_charge("ord-8", 1200, "intent-8")
    result = api.post_charge("ord-8", 1300, "intent-8")
    equal(result, (422, {"error": {"code": "IDEMPOTENCY_KEY_REUSED", "message": "Idempotency key reused with a different request"}}))
    equal(gateway.calls, [("ord-8", 1200)])


def concurrent(module):
    gateway = Gateway(block=True)
    api = module.PaymentAPI(gateway)
    results = {}

    def call(label):
        results[label] = api.post_charge("ord-9", 5000, "intent-9")

    first = threading.Thread(target=call, args=("first",), daemon=True)
    second = threading.Thread(target=call, args=("second",), daemon=True)
    first.start()
    if not gateway.entered.wait(1):
        raise AssertionError("first call did not reach gateway")
    second.start()
    try:
        second.join(1)
        if second.is_alive():
            raise AssertionError("in-flight duplicate did not return promptly")
        equal(results["second"], (409, {"error": {"code": "IDEMPOTENCY_IN_PROGRESS", "message": "A request with this idempotency key is in progress"}}))
    finally:
        gateway.release.set()
        first.join(1)
    if first.is_alive():
        raise AssertionError("first call did not complete")
    equal(results["first"][0], 201)
    equal(gateway.calls, [("ord-9", 5000)])
    equal(api.post_charge("ord-9", 5000, "intent-9"), results["first"])
    equal(gateway.calls, [("ord-9", 5000)])


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    module = load(Path(sys.argv[1]).resolve())
    checks = []
    add(checks, "sequential_retry_replays", lambda: sequential(module))
    add(checks, "changed_payload_rejected", lambda: changed_payload(module))
    add(checks, "concurrent_duplicate_conflicts", lambda: concurrent(module))
    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()
