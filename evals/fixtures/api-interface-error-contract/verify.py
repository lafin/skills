#!/usr/bin/env python3

import importlib.util
import json
import sys
from pathlib import Path

EXPECTED_CONSUMER = '''from orders_api import get_order


def order_sku(order_id):
    status, body = get_order(order_id)
    if status != 200:
        return None
    return body["sku"]
'''


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
        checks.append({"name": name, "dimension": "interface_contract", "critical": True, "passed": False, "detail": f"{type(exc).__name__}: {exc}"})
    else:
        checks.append({"name": name, "dimension": "interface_contract", "critical": True, "passed": True, "detail": "observable contract satisfied"})


def equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"expected {expected!r}, got {actual!r}")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    root = Path(sys.argv[1]).resolve()
    api = load(root, "orders_api")
    consumer = load(root, "consumer")
    checks = []

    add(checks, "existing_success_contract", lambda: equal(api.get_order("ord-1"), (200, {"id": "ord-1", "sku": "lamp", "quantity": 1})))
    add(checks, "existing_consumer_unchanged", lambda: (equal((root / "consumer.py").read_text(encoding="utf-8"), EXPECTED_CONSUMER), equal(consumer.order_sku("ord-1"), "lamp")))
    add(checks, "not_found_error_contract", lambda: equal(api.get_order("missing"), (404, {"error": {"code": "ORDER_NOT_FOUND", "message": "Order not found", "details": {"orderId": "missing"}}})))
    add(checks, "validation_before_effect", lambda: (equal(api.create_order({}), (422, {"error": {"code": "VALIDATION_ERROR", "message": "Request validation failed", "details": {"sku": "required"}}})), equal(len(api.ORDERS), 1)))
    add(checks, "internal_error_redacted", lambda: equal(api.to_public_error(RuntimeError("db password hunter2")), (500, {"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}})))
    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()
