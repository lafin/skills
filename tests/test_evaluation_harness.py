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
        "evaluated_skills": ["evaluation"],
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
        "schema_version": 4,
        "case_id": case["id"],
        "kind": case["kind"],
        "split": case["split"],
        "condition": "baseline",
        "attempt": 1,
        "prompt": case["prompt"],
        "skill_scope": {
            "mode": "confusable-pair",
            "skills": ["evaluation", "advanced-evaluation"],
            "confusable_pair": case["available_skills"],
            "evaluated_skills": case["evaluated_skills"],
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
            f"--system-prompt={RUN.ROUTING_SYSTEM_PROMPT}",
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
            "behavior_system_prompt": RUN.BEHAVIOR_SYSTEM_PROMPT,
            "routing_system_prompt": RUN.ROUTING_SYSTEM_PROMPT,
            "repository_system_prompt": None,
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
        GRADE.validate_redacted_config(
            {
                "auth.broker.token": {
                    "description": "<redacted>",
                    "type": "<redacted>",
                }
            }
        )
        with self.assertRaisesRegex(ValueError, "unredacted"):
            GRADE.validate_redacted_config(config)

    def test_locked_contract_binds_configuration_and_effective_timeouts(self) -> None:
        args = argparse.Namespace(
            model="provider/model",
            profile="isolated",
            tools="",
            thinking="off",
            attempts=3,
            system_prompt=None,
            max_time="10m",
        )
        contract = {
            "execution_config": {
                "model": "provider/model",
                "profile": "isolated",
                "tools": [],
                "thinking": "off",
                "attempt_count": 3,
                "system_prompt_sha256": None,
            },
            "timeout_policy": {
                "omp_max_time_seconds": 600,
                "rpc_grace_seconds": 30,
                "per_attempt_seconds": 630,
                "overall": "per_attempt_seconds * attempt_count * case_count",
            },
        }

        timeouts = RUN.verify_locked_contract(
            contract, args, [routing_case()], []
        )

        self.assertEqual(630, timeouts["per_attempt_seconds"])
        self.assertEqual(1890, timeouts["overall_seconds"])
        args.attempts = 1
        with self.assertRaisesRegex(ValueError, "execution_config.attempt_count"):
            RUN.verify_locked_contract(contract, args, [routing_case()], [])

    def test_catalog_revision_is_materialized_without_working_tree_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for command in (
                ["git", "init"],
                ["git", "config", "user.email", "eval@example.invalid"],
                ["git", "config", "user.name", "Evaluation Test"],
                ["git", "config", "commit.gpgsign", "false"],
            ):
                code, _, stderr = RUN.run_text(command, root)
                self.assertEqual(0, code, stderr)
            (root / "catalog.txt").write_text("frozen\n", encoding="utf-8")
            for command in (
                ["git", "add", "catalog.txt"],
                ["git", "commit", "-m", "freeze catalog"],
            ):
                code, _, stderr = RUN.run_text(command, root)
                self.assertEqual(0, code, stderr)
            revision = RUN.git_value(root, "rev-parse", "HEAD")
            self.assertIsNotNone(revision)
            (root / "catalog.txt").write_text("editable\n", encoding="utf-8")

            temporary, record = RUN.materialize_catalog(
                root, revision, "baseline"
            )
            try:
                archived = Path(record["root"]) / "catalog.txt"
                self.assertEqual("frozen\n", archived.read_text(encoding="utf-8"))
                self.assertEqual(revision, record["revision"])
                self.assertNotEqual(root, Path(record["root"]))
            finally:
                temporary.cleanup()


    def test_runner_selector_keeps_holdouts_behind_the_guard(self) -> None:
        manifest = json.loads((ROOT / "evals/suites.json").read_text(encoding="utf-8"))
        select = RUN.evaluation_selector()

        development = select(
            manifest, ROOT, mode="normal", suite="routing", condition="treatment"
        )
        self.assertTrue(
            all(entry["split"] == "development" for entry in development["entries"])
        )
        with self.assertRaisesRegex(ValueError, "cannot expose holdout"):
            select(
                manifest,
                ROOT,
                mode="normal",
                case_paths=[ROOT / "evals/cases/routing-holdout.jsonl"],
                condition="baseline",
            )

        for mode, suite in (
            ("holdout", "routing"),
            ("independent-holdout", "see-behavior"),
            ("release", "see-routing"),
        ):
            with self.subTest(mode=mode):
                selected = select(
                    manifest,
                    ROOT,
                    mode=mode,
                    suite=suite,
                    condition="treatment",
                )
                self.assertTrue(selected["guarded_holdout"])
                self.assertEqual(
                    selected["treatment_catalog_revision"],
                    selected["evaluated_catalog_revision"],
                )

    def test_runner_selector_requires_explicit_historical_catalog(self) -> None:
        manifest = json.loads((ROOT / "evals/suites.json").read_text(encoding="utf-8"))
        select = RUN.evaluation_selector()
        path = ROOT / "evals/cases/see-behavior-development-v2.jsonl"

        with self.assertRaisesRegex(ValueError, "retained catalog side"):
            select(manifest, ROOT, mode="normal", case_paths=[path])
        selected = select(
            manifest,
            ROOT,
            mode="normal",
            case_paths=[path],
            allow_historical=True,
            historical_catalog="baseline",
            condition="baseline",
        )
        self.assertFalse(selected["guarded_holdout"])
        self.assertEqual(
            selected["baseline_catalog_revision"],
            selected["evaluated_catalog_revision"],
        )

    def test_runner_selector_uses_proposal_baseline_revision(self) -> None:
        manifest = json.loads((ROOT / "evals/suites.json").read_text(encoding="utf-8"))
        proposal = dict(
            next(
                entry
                for entry in manifest["case_files"]
                if entry["path"] == "evals/cases/routing-development.jsonl"
            ),
            status="proposal",
            baseline_catalog_revision=manifest["base_catalog_revision"],
        )
        manifest["case_files"] = [proposal]
        selected = RUN.evaluation_selector()(
            manifest,
            ROOT,
            mode="proposal-baseline",
            proposal_baseline=ROOT / proposal["path"],
            condition="baseline",
        )

        self.assertFalse(selected["guarded_holdout"])
        self.assertEqual(
            manifest["base_catalog_revision"],
            selected["evaluated_catalog_revision"],
        )

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
        routing_command = RUN.build_command(args, routing_case(), ["evaluation"])
        self.assertIn(
            f"--system-prompt={RUN.ROUTING_SYSTEM_PROMPT}",
            routing_command,
        )
        self.assertIn("--skills=advanced-evaluation,evaluation", routing_command)
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
        for malformed in (
            {**case, "checks": [{**case["checks"][0], "critical": "yes"}]},
            {key: value for key, value in case.items() if key != "evaluated_skills"},
        ):
            with self.assertRaises(ValueError):
                RUN.validate_case(malformed, "case")
    def test_see_case_manifest_and_exact_preservation_checks(self) -> None:
        case = {
            "id": "see-preservation",
            "kind": "behavior",
            "split": "development",
            "target_skill": "simplified-engineering-english",
            "prompt": "Rewrite",
            "response_fields": ["PROFILE", "REWRITE", "AMBIGUITIES"],
            "case_manifest": {
                "artifact_family": "requirement and contract",
                "selected_profile": "strict",
                "source_facts": ["The client has one obligation."],
                "protected_spans": ["`legacyFlag`"],
                "quoted_spans": ["\"and/or\""],
                "conditions_and_exceptions": ["unless recovery is complete"],
                "numbers_units_versions_status_codes": ["20 ms", "HTTP 409"],
                "expected_obligation_force": ["MUST NOT"],
                "permitted_rewrites": ["Split the sentence."],
                "required_structure": ["One atomic obligation."],
                "ambiguity_traps": ["Do not weaken the prohibition."],
                "prohibited_inventions": ["A retry count."],
            },
            "observable_success": ["Preserves exact technical values"],
            "prohibited_outcomes": ["Changes obligation force"],
            "checks": [
                {
                    "name": "profile",
                    "field": "fields.PROFILE",
                    "op": "equals",
                    "value": "strict",
                    "critical": True,
                }
            ],
        }
        RUN.validate_case(case, "case")
        GRADE.validate_case(case, "case")
        rewrite = (
            "The client MUST NOT set `legacyFlag` unless recovery is complete. "
            "The response is HTTP 409 after 20 ms. Preserve \"and/or\" verbatim. "
            "The identifier `legacyFlag` can appear again."
        )
        checks = GRADE.manifest_preservation_checks(case, rewrite)
        self.assertTrue(checks)
        self.assertTrue(all(check["passed"] for check in checks))
        self.assertFalse(
            any(
                check["name"].startswith("manifest_expected_obligation_force_")
                for check in checks
            )
        )
        self.assertFalse(
            any(
                check["name"].startswith("manifest_conditions_and_exceptions_")
                for check in checks
            )
        )
        mutations = {
            "protected_spans": ("`legacyFlag`", "`renamedFlag`"),
            "quoted_spans": ("\"and/or\"", "\"or\""),
            "numbers_units_versions_status_codes": ("20 ms", "25 ms"),
        }
        for field, (original, replacement) in mutations.items():
            missing = GRADE.manifest_preservation_checks(
                case, rewrite.replace(original, replacement)
            )
            self.assertFalse(
                next(
                    check
                    for check in missing
                    if check["name"] == f"manifest_{field}_1"
                )["passed"],
                field,
            )
        exempt = {
            **case,
            "case_manifest": {
                **case["case_manifest"],
                **{field: [] for field in GRADE.EXACT_PRESERVATION_FIELDS},
            },
        }
        self.assertEqual([], GRADE.manifest_preservation_checks(exempt, "Plain text."))
        malformed = {
            **case,
            "case_manifest": {
                key: value
                for key, value in case["case_manifest"].items()
                if key != "source_facts"
            },
        }
        with self.assertRaisesRegex(ValueError, "case_manifest"):
            RUN.validate_case(malformed, "case")
        contradictory = {
            **case,
            "checks": [
                *case["checks"],
                {
                    "name": "redact",
                    "field": "fields.REWRITE",
                    "op": "not_contains",
                    "value": "/private/781/debug.log",
                    "critical": True,
                },
            ],
            "case_manifest": {
                **case["case_manifest"],
                "numbers_units_versions_status_codes": ["781"],
            },
        }
        with self.assertRaisesRegex(ValueError, "conflicts with prohibited rewrite"):
            RUN.validate_case(contradictory, "case")

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
            "schema_version": 4,
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
                {"fields": {"QUESTION": "no"}},
            )[0]
        )
        self.assertFalse(
            GRADE.apply_check(
                {"field": "fields.QUESTION", "op": "equals", "value": "no"},
                {"fields": {"QUESTION": "no;"}},
            )[0]
        )

    def test_field_contract_rejects_blank_physical_lines(self) -> None:
        names = ["DECISION", "FILES_TO_CHANGE"]
        self.assertIsNone(
            GRADE.parse_response_fields(
                "\nDECISION: Change tax math.\nFILES_TO_CHANGE: src/tax.py",
                names,
            )
        )
        self.assertIsNone(
            GRADE.parse_response_fields(
                "DECISION: Change tax math.\n\nFILES_TO_CHANGE: src/tax.py",
                names,
            )
        )
        self.assertIsNone(
            GRADE.parse_response_fields(
                "DECISION:  Change tax math.\nFILES_TO_CHANGE: src/tax.py",
                names,
            )
        )
        self.assertIsNone(
            GRADE.parse_response_fields(
                "DECISION: Change tax math. \nFILES_TO_CHANGE: src/tax.py",
                names,
            )
        )

    def test_manifest_exact_spans_reject_embedded_tokens(self) -> None:
        self.assertTrue(GRADE.exact_span_present("Version 5.4.2.", "5.4.2"))
        self.assertTrue(GRADE.exact_span_present("Code 71; node NX-31.", "71"))
        self.assertTrue(GRADE.exact_span_present("Node R3. Status sealed.", "R3"))
        self.assertFalse(GRADE.exact_span_present("Code 171.", "71"))
        self.assertFalse(GRADE.exact_span_present("Node NX-310.", "NX-31"))
        self.assertFalse(GRADE.exact_span_present("Version 15.4.2.", "5.4.2"))
        self.assertFalse(GRADE.exact_span_present("Replica R3-standby.", "R3"))
        self.assertFalse(GRADE.exact_span_present("Progress 65%0.", "65%"))

    def test_see_semantic_regression_checks_reject_known_omissions(self) -> None:
        cases = {
            case["id"]: case
            for case in map(
                json.loads,
                (ROOT / "evals/cases/see-behavior-development.jsonl")
                .read_text()
                .splitlines(),
            )
        }
        relation = next(
            check
            for check in cases["see-explanation-ordinary"]["checks"]
            if check["name"] == "timeout_argument_relation"
        )
        cause = next(
            check
            for check in cases["see-error-ordinary"]["checks"]
            if check["name"] == "reports_unknown_cause"
        )
        retry = next(
            check
            for check in cases["see-error-ordinary"]["checks"]
            if check["name"] == "keeps_retry"
        )
        self.assertTrue(
            GRADE.apply_check(
                relation,
                {"fields": {"REWRITE": "The `timeout` parameter receives the `30s` argument."}},
            )[0]
        )
        self.assertFalse(
            GRADE.apply_check(
                relation,
                {"fields": {"REWRITE": "The `timeout` parameter is set to `30s`."}},
            )[0]
        )
        self.assertTrue(
            GRADE.apply_check(
                cause,
                {"response": "The operation and input are unspecified; the cause is unknown."},
            )[0]
        )
        self.assertFalse(
            GRADE.apply_check(
                cause,
                {"response": "The operation and input are unspecified."},
            )[0]
        )
        self.assertTrue(
            GRADE.apply_check(
                retry,
                {
                    "fields": {
                        "REWRITE": "Check the unspecified item, then try the unspecified operation again."
                    }
                },
            )[0]
        )
        self.assertFalse(
            GRADE.apply_check(
                retry,
                {"fields": {"REWRITE": "Check the unspecified item."}},
            )[0]
        )
        no_invented_ambiguity = next(
            check
            for check in cases["see-local-antecedent-regression"]["checks"]
            if check["name"] == "no_invented_ambiguity"
        )
        pressure_relation = next(
            check
            for check in cases["see-local-antecedent-regression"]["checks"]
            if check["name"] == "pressure_relation"
        )
        descriptive_copy = next(
            check
            for check in cases["see-descriptive-fact-regression"]["checks"]
            if check["name"] == "descriptive_copy_fact"
        )
        self.assertFalse(
            GRADE.apply_check(
                no_invented_ambiguity,
                {"fields": {"AMBIGUITIES": "The pressure could mean another pressure."}},
            )[0]
        )
        self.assertTrue(
            GRADE.apply_check(
                pressure_relation,
                {
                    "fields": {
                        "REWRITE": "Record the manifold pressure. When the manifold "
                        "pressure reaches 40 kPa, close valve V-19."
                    }
                },
            )[0]
        )
        self.assertTrue(
            GRADE.apply_check(
                descriptive_copy,
                {
                    "fields": {
                        "REWRITE": "The gateway copies that nonce into response header X-Orin-Nonce."
                    }
                },
            )[0]
        )
        self.assertFalse(
            GRADE.apply_check(
                descriptive_copy,
                {
                    "fields": {
                        "REWRITE": "The gateway SHALL copy that nonce into response header X-Orin-Nonce."
                    }
                },
            )[0]
        )
        authorization_case = cases["see-authorization-scope-regression"]
        preserved_authorization = {
            check["name"]: check
            for check in GRADE.manifest_preservation_checks(
                authorization_case,
                "Security authorizes replacing only the header value with "
                "[REDACTED-AUTHORIZED].",
            )
        }
        changed_authorization = {
            check["name"]: check
            for check in GRADE.manifest_preservation_checks(
                authorization_case,
                "Security authorized replacing the header value with "
                "[REDACTED-AUTHORIZED].",
            )
        }
        self.assertTrue(
            preserved_authorization["manifest_protected_spans_4"]["passed"]
        )
        self.assertFalse(
            changed_authorization["manifest_protected_spans_4"]["passed"]
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
            "schema_version": 4,
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
            "schema_version": 4,
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

    def test_materialized_catalog_paths_do_not_change_comparison_signature(self) -> None:
        def manifest(role: str, root: str) -> dict:
            generated = str(Path(root).parent / "catalog-root.yaml")
            return {
                "adapter": {"name": "omp-rpc-jsonl"},
                "omp_executable": {"path": "/bin/omp", "sha256": "same"},
                "omp_version": "omp/test",
                "model_requested": "provider/model",
                "fixture_files": {},
                "evaluator_files": {"run.py": "same", "grade.py": "same"},
                "attempts": 3,
                "evaluated_catalog": {
                    "role": role,
                    "revision": role * 40,
                    "root": root,
                    "tree": role * 40,
                },
                "configuration": {
                    "cwd": str(ROOT),
                    "canonical_skill_root": root,
                    "config_files": [{"path": generated, "sha256": role * 64}],
                    "profile": "isolated",
                    "tools": [],
                    "thinking": "off",
                    "effective_omp_config": {
                        "value": {"skills": {"customDirectories": [root]}}
                    },
                },
            }

        baseline = manifest("b", "/tmp/baseline/catalog")
        treatment = manifest("c", "/tmp/treatment/catalog")
        self.assertEqual(
            GRADE.comparison_signature(baseline),
            GRADE.comparison_signature(treatment),
        )
        treatment["configuration"]["tools"] = ["read"]
        self.assertNotEqual(
            GRADE.comparison_signature(baseline),
            GRADE.comparison_signature(treatment),
        )

    def test_non_repository_artifact_accepts_materialized_catalog_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "artifacts/routing-case/1.json"
            case, artifact, manifest = captured_artifact(path)
            catalog = str(root / "catalog")
            manifest["configuration"]["canonical_skill_root"] = catalog
            artifact["rpc_cwd"] = catalog
            artifact["command"] = [
                f"--cwd={catalog}" if item == f"--cwd={ROOT}" else item
                for item in artifact["command"]
            ]
            path.write_text(json.dumps(artifact), encoding="utf-8")

            validated = GRADE.validate_artifact(path, path, case, manifest, 1)
            self.assertEqual("SELECTED_SKILL: evaluation", validated["response"])

    def test_routing_pair_rejects_unchanged_evaluated_skill(self) -> None:
        case = routing_case()
        cases = {case["id"]: case}
        manifest = {
            "condition": "baseline",
            "skill_files": {
                "evaluation": {"sha256": "same"},
                "advanced-evaluation": {"sha256": "same"},
            },
        }
        artifact = {
            "prompt": case["prompt"],
            "provider": "provider",
            "model": "model",
        }
        computed = (
            manifest,
            cases,
            {(case["id"], 1): artifact},
            {},
            {},
        )
        treatment = (
            {**manifest, "condition": "treatment"},
            cases,
            {(case["id"], 1): artifact},
            {},
            {},
        )
        with (
            mock.patch.object(GRADE, "compute_grades", side_effect=[computed, treatment]),
            mock.patch.object(GRADE, "comparison_signature", return_value=("same",)),
            self.assertRaisesRegex(ValueError, "evaluated routing skills are unchanged"),
        ):
            GRADE.paired_runs(Path("baseline"), Path("treatment"))

    def test_routing_pair_accepts_candidate_description_change(self) -> None:
        case = routing_case()
        cases = {case["id"]: case}
        baseline_manifest = {
            "condition": "baseline",
            "skill_files": {
                "evaluation": {"sha256": "old"},
                "advanced-evaluation": {"sha256": "same"},
            },
        }
        treatment_manifest = {
            "condition": "treatment",
            "skill_files": {
                "evaluation": {"sha256": "new"},
                "advanced-evaluation": {"sha256": "same"},
            },
        }
        baseline_artifact = {
            "prompt": "baseline candidate descriptions",
            "provider": "provider",
            "model": "model",
        }
        treatment_artifact = {
            "prompt": "treatment candidate descriptions",
            "provider": "provider",
            "model": "model",
        }
        baseline = (
            baseline_manifest,
            cases,
            {(case["id"], 1): baseline_artifact},
            {},
            {},
        )
        treatment = (
            treatment_manifest,
            cases,
            {(case["id"], 1): treatment_artifact},
            {},
            {},
        )
        with (
            mock.patch.object(GRADE, "compute_grades", side_effect=[baseline, treatment]),
            mock.patch.object(GRADE, "comparison_signature", return_value=("same",)),
        ):
            GRADE.paired_runs(Path("baseline"), Path("treatment"))

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
            "schema_version": 4,
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
    def test_behavior_gate_requires_every_treatment_case_to_pass(self) -> None:
        def counts(baseline_passed: int, treatment_passed: int, total: int) -> dict:
            return {
                "baseline_passed": baseline_passed,
                "treatment_passed": treatment_passed,
                "total": total,
                "critical_regressions": [],
                "regressions": [],
                "baseline_metrics": {"tokens": 10, "tool_events": 0, "questions": 0},
                "treatment_metrics": {"tokens": 10, "tool_events": 0, "questions": 0},
            }

        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(
                case_kind="behavior",
                development_baseline=Path("development-baseline"),
                development_treatment=Path("development-treatment"),
                holdout_baseline=Path("holdout-baseline"),
                holdout_treatment=Path("holdout-treatment"),
                routing_holdout_baseline=Path("routing-baseline"),
                routing_holdout_treatment=Path("routing-treatment"),
                correctness_benefit=None,
                output=Path(directory) / "gate.json",
            )
            results = [
                counts(1, 2, 3),
                counts(1, 2, 3),
                counts(3, 3, 3),
            ]
            with mock.patch.object(GRADE, "paired_grade_counts", side_effect=results):
                report = GRADE.merge_gate(args)

        self.assertEqual("behavior", report["case_kind"])
        self.assertEqual("fail", report["decision"])
        self.assertFalse(report["criteria"]["development_improved"])
        self.assertFalse(report["criteria"]["holdout_preserved"])


if __name__ == "__main__":
    unittest.main()
