"""Focused deterministic checks for the OMP catalog probe."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_probe():
    path = ROOT / "evals/catalog_probe.py"
    spec = importlib.util.spec_from_file_location("skill_catalog_probe", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PROBE = load_probe()


class CatalogProbeTest(unittest.TestCase):
    def test_catalog_serialization_is_exact_canonical_utf8(self) -> None:
        catalog = [
            {"name": "skill:zeta", "description": "Zed"},
            {"description": "Café", "name": "skill:alpha"},
        ]
        serialized = PROBE.serialize_catalog(catalog)
        self.assertEqual(
            '[{"description":"Zed","name":"skill:zeta"},{"description":"Café","name":"skill:alpha"}]',
            serialized,
        )
        self.assertEqual(len(serialized.encode("utf-8")), 88)
        self.assertEqual(PROBE.sha256_text(serialized), PROBE.sha256_text(PROBE.serialize_catalog(catalog)))

    def test_runtime_catalog_uses_the_last_real_omp_update(self) -> None:
        events = [
            {"type": "available_commands_update", "commands": [{"name": "help"}]},
            {
                "type": "available_commands_update",
                "commands": [
                    {"name": "help"},
                    {"name": "skill:alpha", "description": "Alpha\n"},
                ],
            },
        ]
        catalog, serialized = PROBE.runtime_catalog(events)
        self.assertEqual([{"name": "skill:alpha", "description": "Alpha\n"}], catalog)
        self.assertEqual('[{"description":"Alpha\\n","name":"skill:alpha"}]', serialized)

    def test_matched_control_rejects_non_catalog_payload_difference(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-catalog request payload differs"):
            PROBE.matched_payload_hash("full", "control")

    def test_usage_unavailable_refuses_token_claim(self) -> None:
        result = PROBE.token_attribution({"totalTokens": 50}, {"totalTokens": 20}, True)
        self.assertEqual("unavailable", result["status"])
        self.assertIsNone(result["catalog_input_tokens"])
        self.assertFalse(result["claim_eligible"])
        self.assertIn("did not report", result["reason"])

    def test_usage_derives_only_matched_reported_input_tokens(self) -> None:
        result = PROBE.token_attribution(
            {"inputTokens": 130, "outputTokens": 10},
            {"inputTokens": 90, "outputTokens": 10},
            True,
        )
        self.assertEqual(40, result["catalog_input_tokens"])
        self.assertTrue(result["claim_eligible"])

    def test_order_alternates_ab_and_ba(self) -> None:
        self.assertEqual(["AB", "BA", "AB", "BA", "AB"], PROBE.run_order(5))

    def test_seeded_bootstrap_confidence_interval_is_deterministic(self) -> None:
        values = [-8.0, -4.0, -3.0, -1.0, 2.0]
        first = PROBE.bootstrap_median_ci(values, seed=1729, resamples=500)
        second = PROBE.bootstrap_median_ci(values, seed=1729, resamples=500)
        self.assertEqual(first, second)
        self.assertEqual((-8.0, 2.0), first)


if __name__ == "__main__":
    unittest.main()
