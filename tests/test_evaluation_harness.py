"""Focused checks for evaluation capture and deterministic grading."""

from __future__ import annotations

import argparse
import importlib.util
import os
import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RUN = load_module("skill_eval_run", ROOT / "evals/run.py")
GRADE = load_module("skill_eval_grade", ROOT / "evals/grade.py")


def routing_case() -> dict:
    return {
        "id": "routing-case",
        "kind": "routing",
        "split": "development",
        "target_skill": "evaluation",
        "available_skills": ["evaluation", "advanced-evaluation"],
        "prompt": "Choose one",
        "observable_success": ["Selects evaluation"],
        "prohibited_outcomes": ["Selects another skill"],
        "checks": [
            {
                "name": "route",
                "op": "equals",
                "value": "SELECTED_SKILL: evaluation",
                "critical": True,
            }
        ],
    }


def captured_artifact(path: Path) -> tuple[dict, dict, dict]:
    case = routing_case()
    descriptions = {
        "evaluation": "Evaluation suite",
        "advanced-evaluation": "LLM judge",
    }
    events = [
        {"type": "ready", "protocolVersion": 1},
        {
            "type": "available_commands_update",
            "commands": [
                {"name": f"skill:{name}", "description": description + "\n"}
                for name, description in descriptions.items()
            ],
        },
        {
            "id": "routing-case-1-case",
            "type": "response",
            "command": "prompt",
            "success": True,
            "data": {"agentInvoked": True},
        },
        {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "SELECTED_SKILL: evaluation"}],
                "provider": "provider",
                "model": "model",
                "usage": {"totalTokens": 42},
                "stopReason": "stop",
            },
        },
        {"type": "agent_end", "messages": [], "isTerminal": True},
    ]
    summary = RUN.summarize_events(events)
    artifact = {
        "schema_version": 3,
        "case_id": case["id"],
        "kind": case["kind"],
        "split": case["split"],
        "condition": "baseline",
        "attempt": 1,
        "prompt": case["prompt"],
        "skill_scope": {
            "mode": "repository-catalog",
            "skills": ["advanced-evaluation", "evaluation"],
            "confusable_pair": case["available_skills"],
        },
        "command": [
            "omp",
            "--mode=rpc",
            "--no-rules",
            "--no-session",
            "--no-extensions",
            f"--cwd={ROOT}",
            "--model=provider/model",
            "--thinking=off",
            "--max-time=1m",
            "--profile=isolated",
            "--no-tools",
            "--skills=advanced-evaluation,evaluation",
        ],
        "rpc_cwd": str(ROOT),
        "rpc_requests": [
            {
                "id": "routing-case-1-case",
                "type": "prompt",
                "message": RUN.case_prompt(case, descriptions),
            }
        ],
        "terminal_state": {
            "expected_prompt_id": "routing-case-1-case",
            "completed_prompt_ids": ["routing-case-1-case"],
            "terminal_result": "agent_end",
            "received": True,
        },
        "tool_policy": {"allowed": [], "observed": [], "violations": []},
        "exit_code": 0,
        "elapsed_seconds": 1.0,
        "raw_stdout": "".join(json.dumps(event) + "\n" for event in events),
        "raw_stderr": "",
        "events": events,
        "event_parse_errors": [],
        **summary,
    }
    manifest = {
        "condition": "baseline",
        "model_requested": "provider/model",
        "configuration": {
            "tools": [],
            "profile": "isolated",
            "thinking": "off",
            "max_time": "1m",
            "config_files": [],
            "cwd": str(ROOT),
        },
        "skill_files": {
            name: {"description": description}
            for name, description in descriptions.items()
        },
    }
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(artifact), encoding="utf-8")
    return case, artifact, manifest


class EvaluationHarnessTest(unittest.TestCase):
    def test_capture_aggregates_turn_usage_and_records_exact_tools(self) -> None:
        events = [
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "first"}],
                    "provider": "provider",
                    "model": "model",
                    "usage": {"totalTokens": 10, "cacheReadTokens": None},
                },
            },
            {"type": "tool_execution_start", "toolName": "read", "args": {}},
            {"type": "tool_execution_start", "toolName": "read", "args": {}},
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "commentary",
                            "textSignature": json.dumps({"phase": "commentary"}),
                        },
                        {
                            "type": "text",
                            "text": "selected response",
                            "textSignature": json.dumps({"phase": "final_answer"}),
                        },
                    ],
                    "provider": "provider",
                    "model": "model",
                    "usage": {"totalTokens": 32, "cacheReadTokens": None},
                },
            },
            {"type": "agent_end", "isTerminal": True, "messages": []},
        ]

        summary = RUN.summarize_events(events)

        self.assertEqual("selected response", summary["response"])
        self.assertEqual(["read", "read"], summary["tool_names"])
        self.assertEqual(2, summary["tool_call_count"])
        self.assertEqual(42, summary["usage"]["totalTokens"])
        self.assertIsNone(summary["usage"]["cacheReadTokens"])
        self.assertEqual({"totalTokens": 32, "cacheReadTokens": None}, summary["final_message_usage"])

    def test_effective_config_redacts_sensitive_values(self) -> None:
        config = {
            "auth.token": {"value": "secret", "type": "string", "metadata": "also-secret"},
            "nested": {
                "apiKey": "secret",
                "Authorization": "Bearer secret",
                "Cookie": {"value": "session=secret"},
            },
            "skills.customDirectories": {"value": [str(ROOT)], "type": "array"},
        }

        redacted = RUN.redact_config(config)

        self.assertEqual("<redacted>", redacted["auth.token"]["value"])
        self.assertEqual("<redacted>", redacted["nested"]["apiKey"])
        self.assertEqual("<redacted>", redacted["auth.token"]["metadata"])
        self.assertEqual("<redacted>", redacted["nested"]["Authorization"])
        self.assertEqual("<redacted>", redacted["nested"]["Cookie"]["value"])
        self.assertEqual([str(ROOT)], redacted["skills.customDirectories"]["value"])
        GRADE.validate_redacted_config(redacted)
        with self.assertRaisesRegex(ValueError, "unredacted"):
            GRADE.validate_redacted_config(config)

    def test_rpc_command_enforces_condition_skill_and_runtime_scope(self) -> None:
        args = argparse.Namespace(
            omp="omp",
            cwd=ROOT,
            model="provider/model",
            system_prompt="minimal",
            thinking="off",
            max_time="1m",
            profile="isolated",
            config=[],
            tools="",
            condition="treatment",
        )
        case = {
            "kind": "behavior",
            "target_skill": "leancode",
        }

        command = RUN.build_command(args, case, ["leancode"])

        self.assertIn("--mode=rpc", command)
        self.assertIn("--no-rules", command)
        self.assertIn("--no-extensions", command)
        self.assertIn("--no-session", command)
        self.assertIn("--skills=leancode", command)
        self.assertIn("--no-tools", command)
        self.assertIn("--system-prompt=minimal", command)
        self.assertFalse(any(item.startswith("--append-system-prompt") for item in command))
        self.assertFalse(any(item == "prompt" for item in command))

        args.system_prompt = None
        self.assertTrue(
            any(
                item.startswith("--system-prompt=")
                for item in RUN.build_command(args, case, ["leancode"])
            )
        )
        self.assertFalse(
            any(
                item.startswith("--system-prompt=")
                for item in RUN.build_command(args, routing_case(), ["evaluation"])
            )
        )
        self.assertIn(
            "- evaluation: Evaluation suite",
            RUN.case_prompt(
                routing_case(),
                {"evaluation": "Evaluation suite", "advanced-evaluation": "LLM judge"},
            ),
        )

    def test_repository_catalog_reads_canonical_skills(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evaluation").mkdir()
            (root / "evaluation/SKILL.md").write_text("---\nname: evaluation\n---\n")
            self.assertEqual(["evaluation"], RUN.repository_catalog(root))

    def test_full_case_schema_is_required(self) -> None:
        case = routing_case()
        RUN.validate_case(case, "case")
        malformed = {**case, "checks": [{**case["checks"][0], "critical": "yes"}]}
        with self.assertRaisesRegex(ValueError, "critical"):
            RUN.validate_case(malformed, "case")

    def test_raw_events_bind_response_terminal_model_and_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifacts/routing-case/1.json"
            case, artifact, manifest = captured_artifact(path)

            validated = GRADE.validate_artifact(path, path, case, manifest, 1)
            self.assertEqual("SELECTED_SKILL: evaluation", validated["response"])

            artifact["response"] = "SELECTED_SKILL: advanced-evaluation"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "response does not match raw events"):
                GRADE.validate_artifact(path, path, case, manifest, 1)

            artifact["response"] = "SELECTED_SKILL: evaluation"
            artifact["exit_code"] = False
            path.write_text(json.dumps(artifact), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "incomplete terminal response metadata"):
                GRADE.validate_artifact(path, path, case, manifest, 1)

    def test_missing_terminal_and_tool_violation_fail_grading(self) -> None:
        case = {
            "id": "tool-scope",
            "kind": "behavior",
            "split": "development",
            "response_fields": ["DECISION"],
            "checks": [
                {
                    "name": "response",
                    "field": "fields.DECISION",
                    "op": "equals",
                    "value": "ok",
                    "critical": True,
                }
            ],
        }
        artifact = {
            "schema_version": 3,
            "condition": "baseline",
            "attempt": 1,
            "exit_code": 0,
            "event_parse_errors": [],
            "response": "DECISION: ok",
            "terminal_state": {"received": False, "terminal_result": None},
            "tool_policy": {
                "allowed": [],
                "observed": ["mcp__unexpected"],
                "violations": ["mcp__unexpected"],
            },
            "usage": {"totalTokens": 1},
            "tool_call_count": 1,
            "elapsed_seconds": 1,
        }

        grade = GRADE.grade_artifact(case, artifact)

        self.assertFalse(grade["critical_passed"])
        self.assertFalse(next(check for check in grade["checks"] if check["name"] == "omp_capture")["passed"])
        tool_scope = next(check for check in grade["checks"] if check["name"] == "tool_scope")
        self.assertIn("mcp__unexpected", tool_scope["detail"])

    def test_routing_grade_accepts_only_bare_or_labeled_exact_target(self) -> None:
        self.assertTrue(GRADE.correct_route("evaluation", "evaluation"))
        self.assertTrue(GRADE.correct_route("SELECTED_SKILL: evaluation", "evaluation"))
        self.assertFalse(GRADE.correct_route("evaluation because it fits", "evaluation"))
        self.assertFalse(GRADE.correct_route("advanced-evaluation", "evaluation"))

    def test_field_contract_accepts_explicit_denial_without_negative_matching(self) -> None:
        fields = GRADE.parse_response_fields(
            "DECISION: Change only tax math; do not reformat anything.\n"
            "FILES_TO_CHANGE: src/tax.py\n",
            ["DECISION", "FILES_TO_CHANGE"],
        )
        self.assertEqual("Change only tax math; do not reformat anything.", fields["DECISION"])
        self.assertTrue(
            GRADE.apply_check(
                {"field": "fields.QUESTION", "op": "equals", "value": "no"},
                {"fields": {"QUESTION": "no;"}},
            )[0]
        )

    def test_behavior_checks_accept_observed_equivalent_wording(self) -> None:
        cases = {
            case["id"]: case
            for case in map(
                json.loads,
                (ROOT / "evals/cases/behavior.jsonl").read_text().splitlines(),
            )
        }
        samples = [
            (
                "behavior-safe-default",
                "safe_default",
                "Add --confirm; execute only when present, otherwise retain preview-only behavior.",
            ),
            (
                "behavior-single-implementation",
                "json_verification",
                'Assert json.loads(export_report({"status": "ok"})) == {"status": "ok"}.',
            ),
            (
                "behavior-surgical-defect",
                "root_fix",
                "Multiply the unrounded value first and round only the resulting total.",
            ),
            (
                "behavior-surgical-defect",
                "failed_total_scenario",
                "Confirm the total is 108.25, not 108.00.",
            ),
            (
                "behavior-trust-boundary",
                "adversarial_verification",
                "A regular archive inside the trusted directory succeeds; ../ traversal is rejected.",
            ),
            (
                "behavior-material-choice",
                "asks_for_choice",
                "Pause implementation and clarify retry timing before choosing.",
            ),
            (
                "behavior-surgical-defect",
                "root_fix",
                "Compute from the unrounded value and round only the resulting total.",
            ),
            (
                "behavior-surgical-defect",
                "failed_total_scenario",
                "Use a case that fails before multiplication and passes afterward.",
            ),
            (
                "behavior-visual-unavailable",
                "smoke_scenario",
                "Run a headless dialog check and assert the button label is Continue.",
            ),
            (
                "behavior-no-test-harness",
                "no_unsupported_claim",
                "No repository execution was available, so exact output remains unverified.",
            ),
            (
                "behavior-visual-unavailable",
                "no_unsupported_claim",
                "Cannot claim the rendered dialog was visually verified.",
            ),
        ]
        for case_id, check_name, value in samples:
            check = next(
                item for item in cases[case_id]["checks"] if item["name"] == check_name
            )
            with self.subTest(case=case_id, check=check_name):
                self.assertTrue(
                    GRADE.apply_check(
                        check,
                        {"fields": {check["field"].removeprefix("fields."): value}},
                    )[0]
                )

    def test_repository_grade_uses_critical_verifier_checks_and_dimensions(self) -> None:
        case = {
            "id": "repository-case",
            "kind": "repository",
            "split": "development",
            "target_skill": "leancode",
            "fixture": "fixture",
            "checks": [],
        }
        artifact = {
            "schema_version": 3,
            "condition": "baseline",
            "attempt": 1,
            "exit_code": 0,
            "event_parse_errors": [],
            "response": "Implemented and verified.",
            "terminal_state": {"received": True, "terminal_result": "agent_end"},
            "tool_policy": {"violations": []},
            "usage": {"totalTokens": 10},
            "tool_call_count": 1,
            "elapsed_seconds": 1,
            "fixture": {
                "verifier": {
                    "exit_code": 0,
                    "checks": [
                        {
                            "name": "behavior",
                            "dimension": "correctness",
                            "critical": True,
                            "passed": True,
                            "detail": "target behavior passed",
                        }
                    ],
                }
            },
        }

        passing = GRADE.grade_artifact(case, artifact)
        self.assertTrue(passing["critical_passed"])
        self.assertTrue(passing["dimensions"]["correctness"]["passed"])
        artifact["fixture"]["verifier"]["checks"][0]["passed"] = False
        failing = GRADE.grade_artifact(case, artifact)
        self.assertFalse(failing["critical_passed"])
        self.assertFalse(failing["dimensions"]["correctness"]["passed"])

        self.assertFalse(passing["dimensions"]["reporting"]["measured"])
        self.assertIsNone(passing["dimensions"]["reporting"]["passed"])

    def test_repository_snapshot_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "file.txt").write_text("original", encoding="utf-8")
            snapshot = GRADE.tree_snapshot(root)
            GRADE.validate_tree_snapshot(snapshot, "snapshot")
            snapshot["entries"][0]["size"] += 1
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                GRADE.validate_tree_snapshot(snapshot, "snapshot")

    def test_repository_verifier_schema_is_strict(self) -> None:
        malformed = {
            "checks": [
                {
                    "name": "behavior",
                    "critical": True,
                    "passed": True,
                    "detail": "missing dimension",
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "invalid check"):
            GRADE.parse_verifier_output(json.dumps(malformed))

    def test_repository_command_and_verifier_use_isolated_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worktree = root / "worktree"
            worktree.mkdir()
            (worktree / "file.txt").write_text("value", encoding="utf-8")
            verifier = root / "evals/fixtures/fixture/verify.py"
            verifier.parent.mkdir(parents=True)
            verifier.write_text("pass\n", encoding="utf-8")
            snapshot = GRADE.tree_snapshot(worktree)
            checks = [
                {
                    "name": "behavior",
                    "dimension": "correctness",
                    "critical": True,
                    "passed": True,
                    "detail": "passed",
                }
            ]
            verifier_command = [sys.executable, str(verifier), str(worktree)]
            source = {
                "initial_path": "evals/fixtures/fixture/initial",
                "initial_tree_sha256": snapshot["sha256"],
                "verifier_path": "evals/fixtures/fixture/verify.py",
                "verifier_sha256": "0" * 64,
            }
            evidence = {
                "unified_diff": "",
                "id": "fixture",
                "worktree": str(worktree),
                "source": source,
                "initial_tree": snapshot,
                "final_tree": snapshot,
                "diff": GRADE.tree_diff(snapshot, snapshot),
                "verifier": {
                    "command": verifier_command,
                    "cwd": str(worktree),
                    "exit_code": 0,
                    "stdout": json.dumps({"checks": checks}),
                    "stderr": "",
                    "checks": checks,
                    "parse_error": None,
                },
            }
            case = {"fixture": "fixture"}
            manifest = {
                "configuration": {"cwd": str(root)},
                "fixture_files": {"fixture": source},
            }
            command = ["omp", f"--cwd={worktree}"]
            GRADE.validate_fixture_artifact(evidence, case, manifest, command)
            with self.assertRaisesRegex(ValueError, "isolated worktree"):
                GRADE.validate_fixture_artifact(evidence, case, manifest, ["omp", f"--cwd={root}"])

    def test_judge_results_reject_missing_and_duplicate_ids(self) -> None:
        key = {
            "schema_version": 3,
            "pairs": {
                "forward": {
                    "case_id": "case",
                    "attempt": 1,
                    "A": "baseline",
                    "B": "treatment",
                    "order": "forward",
                },
                "swapped": {
                    "case_id": "case",
                    "attempt": 1,
                    "A": "treatment",
                    "B": "baseline",
                    "order": "swapped",
                },
            },
        }
        result = {
            "pair_id": "forward",
            "winner": "A",
            "critical_issue": False,
            "rationale": "better",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key_path = root / "key.json"
            results_path = root / "results.jsonl"
            key_path.write_text(json.dumps(key), encoding="utf-8")
            results_path.write_text(json.dumps(result) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing judge results"):
                GRADE.score_judges(key_path, results_path, root / "missing.json")

            results_path.write_text(
                json.dumps(result) + "\n" + json.dumps(result) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "duplicate judge result"):
                GRADE.score_judges(key_path, results_path, root / "duplicate.json")

    def test_unknown_token_metrics_are_not_zero_filled(self) -> None:
        grades = {
            ("known", 1): {"metrics": {"tokens": 10}},
            ("unknown", 1): {"metrics": {"tokens": None}},
        }
        self.assertIsNone(GRADE.sum_metric(grades, "tokens"))



    def test_capture_environment_removes_secret_named_variables(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"PATH": "/usr/bin", "OPENAI_API_KEY": "secret", "SESSION_COOKIE": "secret"},
            clear=True,
        ):
            self.assertEqual({"PATH": "/usr/bin"}, RUN.capture_environment())

    def test_unified_tree_diff_contains_reviewable_text_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before = root / "before"
            after = root / "after"
            before.mkdir()
            after.mkdir()
            (before / "changed.txt").write_text("old\n", encoding="utf-8")
            (after / "changed.txt").write_text("new\n", encoding="utf-8")
            (after / "added.txt").write_text("added\n", encoding="utf-8")

            patch = RUN.unified_tree_diff(
                before,
                after,
                RUN.tree_snapshot(before),
                RUN.tree_snapshot(after),
            )

            self.assertIn("--- a/changed.txt", patch)
            self.assertIn("+++ b/changed.txt", patch)
            self.assertIn("-old", patch)
            self.assertIn("+new", patch)
            self.assertIn("+++ b/added.txt", patch)

    def test_verifier_rejects_duplicate_json_keys(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            GRADE.parse_verifier_output('{"checks":[],"checks":[]}')

    def test_visual_claim_check_allows_explicit_unavailability(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "evals/cases/repository-holdout.jsonl").read_text().splitlines()
        ]
        case = next(item for item in cases if item["id"] == "repository-ui-verification")
        check = next(item for item in case["checks"] if item["name"] == "no_visual_success_claim")

        self.assertTrue(
            GRADE.apply_check(
                check,
                {"response": "The surface could not be visually verified in this environment."},
            )[0]
        )
        self.assertFalse(
            GRADE.apply_check(
                check,
                {"response": "The rendered dialog was visually verified."},
            )[0]
        )

    def test_judge_summary_retains_critical_flags_and_rationales(self) -> None:
        key = {
            "schema_version": 3,
            "pairs": {
                "forward": {
                    "case_id": "case",
                    "attempt": 1,
                    "A": "baseline",
                    "B": "treatment",
                    "order": "forward",
                },
                "swapped": {
                    "case_id": "case",
                    "attempt": 1,
                    "A": "treatment",
                    "B": "baseline",
                    "order": "swapped",
                },
            },
        }
        results = [
            {
                "pair_id": "forward",
                "winner": "B",
                "critical_issue": True,
                "rationale": "forward rationale",
            },
            {
                "pair_id": "swapped",
                "winner": "A",
                "critical_issue": False,
                "rationale": "swapped rationale",
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key_path = root / "key.json"
            result_path = root / "results.jsonl"
            output = root / "summary.json"
            key_path.write_text(json.dumps(key), encoding="utf-8")
            result_path.write_text(
                "".join(json.dumps(result) + "\n" for result in results),
                encoding="utf-8",
            )

            summary = GRADE.score_judges(key_path, result_path, output)

        self.assertEqual([True, False], summary["results"][0]["critical_issues"])
        self.assertEqual(
            ["forward rationale", "swapped rationale"],
            summary["results"][0]["rationales"],
        )

    def test_gate_blocks_offset_holdout_and_routing_regressions(self) -> None:
        def counts(
            baseline_passed: int,
            treatment_passed: int,
            total: int,
            regressions: list[str],
        ) -> dict:
            return {
                "baseline_passed": baseline_passed,
                "treatment_passed": treatment_passed,
                "total": total,
                "critical_regressions": [],
                "regressions": regressions,
                "baseline_metrics": {"tokens": 10, "tool_events": 1, "questions": 0},
                "treatment_metrics": {"tokens": 10, "tool_events": 1, "questions": 0},
            }

        results = [
            counts(1, 2, 2, []),
            counts(2, 2, 3, ["holdout:1"]),
            counts(2, 1, 2, ["routing:1"]),
        ]
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(
                development_baseline=Path("development-baseline"),
                development_treatment=Path("development-treatment"),
                holdout_baseline=Path("holdout-baseline"),
                holdout_treatment=Path("holdout-treatment"),
                routing_holdout_baseline=Path("routing-baseline"),
                routing_holdout_treatment=Path("routing-treatment"),
                correctness_benefit=None,
                output=Path(directory) / "gate.json",
            )
            with mock.patch.object(GRADE, "paired_grade_counts", side_effect=results):
                report = GRADE.merge_gate(args)

        self.assertEqual("fail", report["decision"])
        self.assertFalse(report["criteria"]["holdout_preserved"])
        self.assertFalse(report["criteria"]["routing_holdout_all_passed"])

if __name__ == "__main__":
    unittest.main()
