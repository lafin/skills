"""Focused checks for evaluation lifecycle and manifest validation."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
REV = "a" * 40


def load_validator():
    path = ROOT / "evals/validate.py"
    spec = importlib.util.spec_from_file_location("skill_eval_validate", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALIDATE = load_validator()


def route(case_id: str, split: str, target: str, other: str) -> dict:
    return {
        "id": case_id,
        "kind": "routing",
        "split": split,
        "target_skill": target,
        "available_skills": [target, other],
        "evaluated_skills": [target, other],
        "prompt": "Choose one",
        "observable_success": [f"Selects {target}"],
        "prohibited_outcomes": [f"Selects {other}"],
        "checks": [
            {
                "name": "exact-route",
                "op": "equals",
                "value": f"SELECTED_SKILL: {target}",
                "critical": True,
            }
        ],
    }


def behavior(case_id: str, split: str, target: str) -> dict:
    return {
        "id": case_id,
        "kind": "behavior",
        "split": split,
        "target_skill": target,
        "prompt": "Do the task",
        "response_fields": ["RESULT"],
        "observable_success": ["Completes"],
        "prohibited_outcomes": ["Skips"],
        "checks": [{"name": "result", "op": "contains", "value": "RESULT", "critical": True}],
    }


def contract() -> dict:
    return {
        "metric": {"name": "exact_route_pass_rate", "favorable_direction": "higher"},
        "unit_of_analysis": "case-attempt pair",
        "attempt_to_case_aggregation": "all attempts complete and pass",
        "case_to_suite_aggregation": "all cases satisfy the rule",
        "non_inferiority_margin": 0,
        "paired_comparison": {
            "method": "treatment minus baseline",
            "pass_inequality": ">=",
            "boundary_inclusive": True,
        },
        "ties": "pass at boundary",
        "missing_or_failed_attempts": "INCONCLUSIVE",
        "timeout_policy": {
            "omp_max_time_seconds": 60,
            "rpc_grace_seconds": 30,
            "per_attempt_seconds": 90,
            "overall": "per_attempt_seconds * cases * attempts",
        },
        "judge_disagreement": "INCONCLUSIVE",
        "position_sensitivity": "INCONCLUSIVE",
        "execution_config": {
            "model": "provider/model",
            "profile": "isolated",
            "tools": [],
            "thinking": "off",
            "attempt_count": 3,
            "system_prompt_sha256": None,
        },
        "baseline_catalog_revision": REV,
        "treatment_catalog_revision": REV,
    }


class RepositoryFixture:
    def __init__(self, root: Path):
        self.root = root
        for skill in ("alpha", "beta"):
            path = root / skill
            path.mkdir(parents=True)
            (path / "SKILL.md").write_text(f"---\nname: {skill}\ndescription: {skill}\n---\n", encoding="utf-8")
        (root / "evals/cases").mkdir(parents=True)
        self.manifest = {
            "schema_version": 1,
            "base_catalog_revision": REV,
            "admission_candidate": None,
            "retired_skills": [],
            "routing_pair_exceptions": [],
            "comparison_contracts": {"routing": contract()},
            "case_files": [],
        }
        for split in ("development", "holdout"):
            self.add_file(
                f"routing-{split}.jsonl",
                "routing",
                split,
                "canonical",
                "routing",
                [route(f"{split}-alpha", split, "alpha", "beta"), route(f"{split}-beta", split, "beta", "alpha")],
            )
        self.save()

    def add_file(self, name: str, kind: str, split: str, status: str, suite: str, rows: list[dict], reason: str | None = None) -> dict:
        path = self.root / "evals/cases" / name
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        entry = {
            "path": f"evals/cases/{name}",
            "kind": kind,
            "split": split,
            "status": status,
            "suite": suite,
            "frozen_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "comparison_contract": suite,
            "baseline_catalog_revision": REV if status == "historical" else None,
            "treatment_catalog_revision": REV if status == "historical" else None,
            "historical_reason": reason,
        }
        self.manifest["case_files"].append(entry)
        return entry

    def rewrite(self, entry: dict, rows: list[dict]) -> None:
        path = self.root / entry["path"]
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        entry["frozen_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()

    def save(self) -> Path:
        path = self.root / "evals/suites.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        return path


class EvaluationValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.fixture = RepositoryFixture(self.root)
        self.patches = (
            mock.patch.object(VALIDATE, "revision_resolves", return_value=True),
            mock.patch.object(VALIDATE, "revision_skills", return_value={"alpha", "beta"}),
            mock.patch.object(VALIDATE, "root_matches_revision", return_value=True),
        )
        for patcher in self.patches:
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.temporary.cleanup)

    def validate(self):
        self.fixture.save()
        return VALIDATE.validate_repository(self.root)

    def assert_invalid(self, text: str) -> None:
        with self.assertRaisesRegex(ValueError, text):
            self.validate()

    def test_negative_route_can_target_an_adjacent_unevaluated_skill(self) -> None:
        row = route("negative", "development", "beta", "alpha")
        row["evaluated_skills"] = ["alpha"]

        self.assertIs(
            row,
            VALIDATE.validate_row(row, "case", "routing", "development"),
        )

    def test_valid_manifest_derives_canonical_coverage(self) -> None:
        result = self.validate()
        self.assertEqual({"alpha", "beta"}, result["current_skills"])
        self.assertTrue(result["canonical_coverage"][("holdout", "evaluated", "alpha")])

    def test_unclassified_and_duplicate_manifest_paths_fail(self) -> None:
        extra = self.root / "evals/cases/extra.jsonl"
        extra.write_text(json.dumps(route("extra", "development", "alpha", "beta")) + "\n")
        self.assert_invalid("unclassified JSONL")
        extra.unlink()
        self.fixture.manifest["case_files"].append(copy.deepcopy(self.fixture.manifest["case_files"][0]))
        self.assert_invalid("listed more than once")

    def test_missing_escaping_and_wrong_directory_paths_fail(self) -> None:
        self.fixture.manifest["case_files"][0]["path"] = "evals/cases/missing.jsonl"
        self.assert_invalid("does not exist")
        self.fixture.manifest["case_files"][0]["path"] = "evals/cases/../outside.jsonl"
        self.assert_invalid("escapes evals/cases")

    def test_invalid_json_and_kind_split_mismatch_name_row(self) -> None:
        entry = self.fixture.manifest["case_files"][0]
        path = self.root / entry["path"]
        path.write_text("{bad\n", encoding="utf-8")
        entry["frozen_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assert_invalid(r"routing-development\.jsonl:1:.*invalid JSON")
        self.fixture.rewrite(entry, [route("wrong-split", "holdout", "alpha", "beta")])
        self.assert_invalid("split.*manifest says 'development'")

    def test_duplicate_active_id_fails(self) -> None:
        holdout = self.fixture.manifest["case_files"][1]
        rows = [route("development-alpha", "holdout", "alpha", "beta"), route("holdout-beta", "holdout", "beta", "alpha")]
        self.fixture.rewrite(holdout, rows)
        self.assert_invalid("duplicates active case")

    def test_unknown_and_retired_active_identities_fail(self) -> None:
        entry = self.fixture.manifest["case_files"][0]
        self.fixture.rewrite(entry, [route("ghost-a", "development", "ghost", "alpha"), route("ghost-b", "development", "alpha", "ghost")])
        self.assert_invalid("unknown roots.*ghost")
        self.fixture.manifest["retired_skills"] = [{"name": "ghost", "source_revision": REV, "retirement_revision": REV, "reason": "removed"}]
        self.assert_invalid("retired identities.*ghost")

    def test_historical_unknown_requires_one_retirement_record_and_pin(self) -> None:
        self.fixture.manifest["comparison_contracts"]["history"] = contract()
        entry = self.fixture.add_file("history.jsonl", "routing", "development", "historical", "history", [route("old", "development", "ghost", "alpha")], "retained old evidence")
        self.assert_invalid("undeclared missing roots.*ghost")
        self.fixture.manifest["retired_skills"] = [{"name": "ghost", "source_revision": REV, "retirement_revision": REV, "reason": "rejected pilot"}]
        entry["baseline_catalog_revision"] = None
        entry["treatment_catalog_revision"] = None
        self.assert_invalid("no retained evaluated-catalog pin")

    def test_historical_duplicate_ids_are_legal_with_explanations(self) -> None:
        self.fixture.manifest["comparison_contracts"]["history"] = contract()
        self.fixture.add_file("history-a.jsonl", "routing", "development", "historical", "history", [route("old-id", "development", "alpha", "beta")], "superseded A")
        self.fixture.add_file("history-b.jsonl", "routing", "development", "historical", "history", [route("old-id", "development", "alpha", "beta")], "superseded B")
        self.validate()

    def test_canonical_routing_requires_exact_check(self) -> None:
        entry = self.fixture.manifest["case_files"][0]
        row = route("bad", "development", "alpha", "beta")
        row["checks"][0]["critical"] = False
        self.fixture.rewrite(entry, [row, route("reverse", "development", "beta", "alpha")])
        self.assert_invalid("lacks a critical exact-route check")

    def test_routing_pair_requires_reverse(self) -> None:
        entry = self.fixture.manifest["case_files"][0]
        self.fixture.rewrite(entry, [route("only-alpha", "development", "alpha", "beta")])
        self.assert_invalid("lacks its reverse target")

    def test_missing_skill_route_fails_pair_coverage(self) -> None:
        holdout = self.fixture.manifest["case_files"][1]
        self.fixture.rewrite(holdout, [route("holdout-alpha", "holdout", "alpha", "beta"), route("holdout-alpha-2", "holdout", "alpha", "beta")])
        self.assert_invalid("holdout A/B pair lacks its reverse target")

    def test_incomplete_comparison_contract_fails(self) -> None:
        del self.fixture.manifest["comparison_contracts"]["routing"]["ties"]
        self.assert_invalid("comparison_contracts.routing:fields")

    def test_holdout_requires_both_immutable_revisions(self) -> None:
        self.fixture.manifest["comparison_contracts"]["routing"]["treatment_catalog_revision"] = None
        self.assert_invalid("treatment_catalog_revision.*full immutable")

    def test_proposal_requires_one_consistent_root_absent_from_base(self) -> None:
        self.fixture.manifest["comparison_contracts"]["proposal"] = contract()
        rows = [route("proposal-a", "development", "gamma", "alpha"), route("proposal-b", "development", "alpha", "delta")]
        self.fixture.add_file("proposal.jsonl", "routing", "development", "proposal", "proposal", rows)
        self.assert_invalid("proposal rows do not consistently reference one root")

    def test_candidate_must_be_new_at_base_and_match_frozen_root(self) -> None:
        self.fixture.manifest["admission_candidate"] = {"root": "alpha", "treatment_catalog_revision": REV}
        self.assert_invalid("already present at base_catalog_revision")

    def test_cleared_candidate_requires_new_skill_behavior_holdout(self) -> None:
        (self.root / "gamma").mkdir()
        (self.root / "gamma/SKILL.md").write_text("---\nname: gamma\ndescription: gamma\n---\n")
        for split in ("development", "holdout"):
            entry = self.fixture.manifest["case_files"][0 if split == "development" else 1]
            rows = [route(f"{split}-alpha", split, "alpha", "gamma"), route(f"{split}-gamma", split, "gamma", "alpha"), route(f"{split}-beta-a", split, "beta", "alpha"), route(f"{split}-alpha-b", split, "alpha", "beta")]
            self.fixture.rewrite(entry, rows)
        self.assert_invalid("gamma.*lacks canonical development behavior evidence")

    def test_normal_low_level_holdout_is_rejected_and_guarded_mode_selects_pins(self) -> None:
        manifest = self.fixture.manifest
        holdout = self.root / manifest["case_files"][1]["path"]
        with self.assertRaisesRegex(ValueError, "cannot expose holdout"):
            VALIDATE.select_case_files(manifest, self.root, case_paths=[holdout], condition="baseline")
        selected = VALIDATE.select_case_files(manifest, self.root, mode="holdout", case_paths=[holdout], condition="treatment")
        self.assertTrue(selected["guarded_holdout"])
        self.assertEqual(REV, selected["evaluated_catalog_revision"])

    def test_independent_and_release_only_require_dedicated_modes(self) -> None:
        independent = copy.deepcopy(self.fixture.manifest["case_files"][1])
        independent["path"] = "evals/cases/independent.jsonl"
        independent["status"] = "independent-holdout"
        source = self.root / self.fixture.manifest["case_files"][1]["path"]
        target = self.root / independent["path"]
        target.write_bytes(source.read_bytes())
        independent["frozen_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        self.fixture.manifest["case_files"].append(independent)
        with self.assertRaisesRegex(ValueError, "dedicated mode"):
            VALIDATE.select_case_files(self.fixture.manifest, self.root, mode="holdout", case_paths=[target])
        selected = VALIDATE.select_case_files(self.fixture.manifest, self.root, mode="independent-holdout", suite="routing", condition="baseline")
        self.assertEqual([independent], selected["entries"])

    def test_proposal_baseline_requires_proposal_development(self) -> None:
        development = self.root / self.fixture.manifest["case_files"][0]["path"]
        with self.assertRaisesRegex(ValueError, "must name one proposal development"):
            VALIDATE.select_case_files(self.fixture.manifest, self.root, mode="proposal-baseline", proposal_baseline=development, condition="baseline")

    def test_historical_development_requires_explicit_pin_side(self) -> None:
        self.fixture.manifest["comparison_contracts"]["history"] = contract()
        entry = self.fixture.add_file("history.jsonl", "routing", "development", "historical", "history", [route("old", "development", "alpha", "beta")], "superseded")
        path = self.root / entry["path"]
        with self.assertRaisesRegex(ValueError, "retained catalog side"):
            VALIDATE.select_case_files(self.fixture.manifest, self.root, case_paths=[path])
        selected = VALIDATE.select_case_files(self.fixture.manifest, self.root, case_paths=[path], allow_historical=True, historical_catalog="baseline")
        self.assertEqual(REV, selected["evaluated_catalog_revision"])

    def test_release_rejects_pending_candidate(self) -> None:
        self.fixture.manifest["admission_candidate"] = {"root": "gamma", "treatment_catalog_revision": REV}
        with self.assertRaisesRegex(ValueError, "release is blocked"):
            VALIDATE.select_case_files(self.fixture.manifest, self.root, mode="release", suite="routing")


if __name__ == "__main__":
    unittest.main()
