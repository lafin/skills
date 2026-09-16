#!/usr/bin/env python3

import importlib.util
import inspect
import json
import sys
from pathlib import Path

EXPECTED_CONSUMER = '''from product_api import get_product


def display_price(sku):
    product = get_product(sku)
    return f'{product["name"]}: ${product["priceCents"] / 100:.2f}'
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
        checks.append({"name": name, "dimension": "compatibility_contract", "critical": True, "passed": False, "detail": f"{type(exc).__name__}: {exc}"})
    else:
        checks.append({"name": name, "dimension": "compatibility_contract", "critical": True, "passed": True, "detail": "observable contract satisfied"})


def equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"expected {expected!r}, got {actual!r}")


def unsupported(api):
    error_type = getattr(api, "UnsupportedSchemaVersion")
    try:
        api.get_product("A1", schema_version=3)
    except error_type as exc:
        equal(getattr(exc, "code", None), "UNSUPPORTED_SCHEMA_VERSION")
    else:
        raise AssertionError("unsupported schema version did not raise typed error")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    root = Path(sys.argv[1]).resolve()
    api = load(root, "product_api")
    consumer = load(root, "consumer")
    checks = []
    v1 = {"sku": "A1", "name": "Desk Lamp", "priceCents": 2500}
    v2 = {"schemaVersion": 2, "product": {"sku": "A1", "name": "Desk Lamp", "price": {"amount": 2500, "currency": "USD"}}, "availability": {"state": "IN_STOCK"}}

    add(checks, "default_v1_consumer_unchanged", lambda: (equal((root / "consumer.py").read_text(encoding="utf-8"), EXPECTED_CONSUMER), equal(api.get_product("A1"), v1), equal(consumer.display_price("A1"), "Desk Lamp: $25.00")))
    add(checks, "explicit_v1_unchanged", lambda: equal(api.get_product("A1", schema_version=1), v1))
    add(checks, "explicit_v2_contract", lambda: equal(api.get_product("A1", schema_version=2), v2))
    add(checks, "unsupported_version_typed_error", lambda: unsupported(api))
    add(checks, "version_parameter_is_optional", lambda: equal(inspect.signature(api.get_product).parameters["schema_version"].default, 1))
    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()
