#!/usr/bin/env python3
"""Validate evaluation inventory, lifecycle, identity, coverage, and selection."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

STATUSES = {"proposal", "canonical", "independent-holdout", "release-only", "historical"}
KINDS = {"routing", "behavior", "repository"}
SPLITS = {"development", "holdout"}
ACTIVE_STATUSES = {"canonical", "independent-holdout", "release-only"}
MODES = {"normal", "holdout", "independent-holdout", "release", "proposal-baseline"}
CHECK_OPS = {"contains", "not_contains", "equals", "regex", "not_regex"}
COMMON_CASE_FIELDS = {
    "id", "kind", "split", "target_skill", "prompt", "observable_success",
    "prohibited_outcomes", "checks", "judge_criteria",
}
CASE_MANIFEST_LIST_FIELDS = {
    "source_facts", "protected_spans", "quoted_spans", "conditions_and_exceptions",
    "numbers_units_versions_status_codes", "expected_obligation_force",
    "permitted_rewrites", "required_structure", "ambiguity_traps",
    "prohibited_inventions",
}
CASE_MANIFEST_FIELDS = CASE_MANIFEST_LIST_FIELDS | {"artifact_family", "selected_profile"}
ENTRY_FIELDS = {
    "path",
    "kind",
    "split",
    "status",
    "suite",
    "frozen_sha256",
    "comparison_contract",
    "baseline_catalog_revision",
    "treatment_catalog_revision",
    "historical_reason",
}
CONTRACT_FIELDS = {
    "metric",
    "unit_of_analysis",
    "attempt_to_case_aggregation",
    "case_to_suite_aggregation",
    "non_inferiority_margin",
    "paired_comparison",
    "ties",
    "missing_or_failed_attempts",
    "timeout_policy",
    "judge_disagreement",
    "position_sensitivity",
    "execution_config",
    "baseline_catalog_revision",
    "treatment_catalog_revision",
}
TOP_FIELDS = {
    "schema_version",
    "base_catalog_revision",
    "admission_candidate",
    "retired_skills",
    "comparison_contracts",
    "routing_pair_exceptions",
    "case_files",
}
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}; remove the duplicate field")
        value[key] = item
    return value


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object)
    except json.JSONDecodeError as error:
        raise ValueError(f"{path}:{error.lineno}:{error.colno}: invalid JSON: {error.msg}; correct the JSON syntax") from error
    except ValueError as error:
        raise ValueError(f"{path}: {error}") from error


def load_manifest(path: Path) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: manifest must be a JSON object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_skills(root: Path) -> set[str]:
    return {path.parent.name for path in root.glob("*/SKILL.md") if path.is_file()}


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)


def revision_resolves(root: Path, revision: Any) -> bool:
    if not isinstance(revision, str) or not HEX40.fullmatch(revision):
        return False
    return _git(root, "cat-file", "-e", f"{revision}^{{commit}}").returncode == 0


def revision_skills(root: Path, revision: str) -> set[str]:
    if not revision_resolves(root, revision):
        raise ValueError(
            f"evals/suites.json:base_catalog_revision: {revision!r} is not a resolvable immutable commit; pin a full 40-character local commit"
        )
    completed = _git(root, "ls-tree", "-d", "--name-only", revision)
    if completed.returncode:
        raise ValueError(f"evals/suites.json:base_catalog_revision: cannot list roots at {revision}: {completed.stderr.strip()}")
    result: set[str] = set()
    for name in completed.stdout.splitlines():
        check = _git(root, "cat-file", "-e", f"{revision}:{name}/SKILL.md")
        if check.returncode == 0:
            result.add(name)
    return result


def root_matches_revision(root: Path, name: str, revision: str) -> bool:
    tracked = _git(root, "diff", "--quiet", revision, "--", name)
    untracked = _git(root, "ls-files", "--others", "--exclude-standard", "--", name)
    return tracked.returncode == 0 and not untracked.stdout.strip()


def _require(condition: bool, location: str, field: str, message: str, correction: str) -> None:
    if not condition:
        raise ValueError(f"{location}:{field}: {message}; {correction}")


def _strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)


def validate_row(row: Any, location: str, kind: str, split: str) -> dict[str, Any]:
    _require(isinstance(row, dict), location, "row", "must be an object", "write one JSON object per line")
    required = {"id", "kind", "split", "target_skill", "prompt", "observable_success", "prohibited_outcomes", "checks"}
    missing = required - row.keys()
    _require(not missing, location, "row", f"missing fields {sorted(missing)}", "add every required case field")
    allowed = COMMON_CASE_FIELDS | (
        {"available_skills", "evaluated_skills"}
        if kind == "routing"
        else {"response_fields", "case_manifest"}
        if kind == "behavior"
        else {"fixture"}
    )
    extra = row.keys() - allowed
    _require(not extra, location, "row", f"unknown fields {sorted(extra)}", "remove fields outside the registered case schema")
    _require(row["kind"] in KINDS, location, "kind", f"unsupported value {row['kind']!r}", "use routing, behavior, or repository")
    _require(row["kind"] == kind, location, "kind", f"row says {row['kind']!r} but manifest says {kind!r}", "make the row and manifest kind identical")
    _require(row["split"] in SPLITS, location, "split", f"unsupported value {row['split']!r}", "use development or holdout")
    _require(row["split"] == split, location, "split", f"row says {row['split']!r} but manifest says {split!r}", "make the row and manifest split identical")
    for field in ("id", "target_skill", "prompt"):
        _require(isinstance(row[field], str) and bool(row[field]), location, field, "must be a non-empty string", f"set {field} to a non-empty string")
    for field in ("observable_success", "prohibited_outcomes"):
        _require(_strings(row[field]), location, field, "must be a non-empty string array", f"add at least one non-empty {field} item")
    if "judge_criteria" in row:
        _require(_strings(row["judge_criteria"]), location, "judge_criteria", "must be a non-empty string array", "list the semantic judge criteria")
    checks = row["checks"]
    _require(isinstance(checks, list) and (kind == "repository" or bool(checks)), location, "checks", "must be a non-empty array outside repository cases", "add deterministic checks")
    check_names: set[str] = set()
    for number, check in enumerate(checks, 1):
        check_location = f"{location}:check[{number}]"
        _require(isinstance(check, dict), check_location, "check", "must be an object", "replace it with a check object")
        allowed_check = {"name", "op", "value", "field", "critical", "dimension"}
        _require(not (check.keys() - allowed_check), check_location, "fields", "contains unknown check fields", "remove fields outside the check schema")
        for field in ("name", "op", "value", "critical"):
            _require(field in check, check_location, field, "is required", f"add check.{field}")
        _require(isinstance(check["name"], str) and bool(check["name"]) and check["name"] not in check_names, check_location, "name", "must be a unique non-empty string", "use a unique check name")
        check_names.add(check["name"])
        _require(check["op"] in CHECK_OPS, check_location, "op", f"unsupported operation {check['op']!r}", f"use one of {sorted(CHECK_OPS)}")
        _require(isinstance(check["value"], str), check_location, "value", "must be a string", "set the comparison value")
        _require(isinstance(check["critical"], bool), check_location, "critical", "must be boolean", "use true or false")
        if check["op"] in {"regex", "not_regex"}:
            try:
                re.compile(check["value"])
            except re.error as error:
                raise ValueError(f"{check_location}:value: invalid regex {error}; correct the regular expression") from error
    if kind == "routing":
        for field in ("available_skills", "evaluated_skills"):
            _require(_strings(row.get(field)), location, field, "must be a non-empty string array", f"list the routing {field}")
            _require(len(row[field]) == len(set(row[field])), location, field, "contains a duplicate identity", "remove duplicate skill names")
        _require(row["target_skill"] in row["available_skills"], location, "target_skill", "is absent from available_skills", "add the target to available_skills")
        _require(set(row["evaluated_skills"]) <= set(row["available_skills"]), location, "evaluated_skills", "contains an unavailable skill", "make evaluated_skills a subset of available_skills")
    elif kind == "behavior":
        _require(_strings(row.get("response_fields")), location, "response_fields", "must be a non-empty string array", "list the expected response fields")
        _require(len(row["response_fields"]) == len(set(row["response_fields"])), location, "response_fields", "contains duplicates", "remove duplicate fields")
        if "case_manifest" in row:
            case_manifest = row["case_manifest"]
            _require(isinstance(case_manifest, dict) and set(case_manifest) == CASE_MANIFEST_FIELDS, location, "case_manifest", "does not contain the complete fixed schema", "record every case-manifest field exactly once")
            _require(isinstance(case_manifest["artifact_family"], str) and bool(case_manifest["artifact_family"]), location, "case_manifest.artifact_family", "must be non-empty", "name the artifact family")
            _require(case_manifest["selected_profile"] in {"strict", "engineering-default"}, location, "case_manifest.selected_profile", "must be strict or engineering-default", "use a registered profile")
            for field in CASE_MANIFEST_LIST_FIELDS:
                _require(isinstance(case_manifest[field], list) and all(isinstance(item, str) and item for item in case_manifest[field]), location, f"case_manifest.{field}", "must be an array of non-empty strings", "correct the case metadata")
            for field in ("source_facts", "permitted_rewrites", "required_structure"):
                _require(bool(case_manifest[field]), location, f"case_manifest.{field}", "must not be empty", "record at least one item")
    else:
        _require(isinstance(row.get("fixture"), str) and bool(row["fixture"]) and re.fullmatch(r"[A-Za-z0-9._-]+", row["fixture"]) is not None, location, "fixture", "must be a safe non-empty identifier", "use letters, digits, dot, underscore, or hyphen")
    return row


def load_rows(path: Path, kind: str, split: str) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line, object_pairs_hook=_object)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{number}:{error.colno}: invalid JSON: {error.msg}; correct this JSONL row") from error
        except ValueError as error:
            raise ValueError(f"{path}:{number}: {error}") from error
        rows.append((number, validate_row(value, f"{path}:{number}", kind, split)))
    _require(bool(rows), str(path), "rows", "file is empty", "add at least one case row or remove the manifest entry and file")
    return rows


def _validate_revision(root: Path, value: Any, location: str, field: str, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    _require(isinstance(value, str) and bool(HEX40.fullmatch(value)), location, field, "must be a full immutable 40-character commit", "pin a full commit hash")
    _require(revision_resolves(root, value), location, field, f"commit {value!r} is not resolvable", "retain or fetch the immutable commit before validation")


def validate_contracts(root: Path, manifest: dict[str, Any], manifest_path: Path) -> None:
    contracts = manifest["comparison_contracts"]
    _require(isinstance(contracts, dict) and bool(contracts), str(manifest_path), "comparison_contracts", "must be a non-empty object", "register each executable suite contract")
    for name, contract in contracts.items():
        location = f"{manifest_path}:comparison_contracts.{name}"
        _require(isinstance(name, str) and bool(name), location, "name", "must be non-empty", "use the suite name")
        _require(isinstance(contract, dict), location, "contract", "must be an object", "write the complete frozen comparison contract")
        _require(set(contract) == CONTRACT_FIELDS, location, "fields", f"expected exactly {sorted(CONTRACT_FIELDS)}", "add missing fields and remove unknown fields")
        metric = contract["metric"]
        _require(isinstance(metric, dict) and set(metric) == {"name", "favorable_direction"}, location, "metric", "must contain exactly name and favorable_direction", "freeze both metric fields")
        _require(metric["favorable_direction"] in {"higher", "lower"}, location, "metric.favorable_direction", "must be higher or lower", "state the favorable direction")
        for field in ("unit_of_analysis", "attempt_to_case_aggregation", "case_to_suite_aggregation", "ties", "missing_or_failed_attempts", "judge_disagreement", "position_sensitivity"):
            _require(isinstance(contract[field], str) and bool(contract[field]), location, field, "must be a non-empty frozen rule", f"record the {field} rule")
        _require(isinstance(contract["non_inferiority_margin"], (int, float)) and not isinstance(contract["non_inferiority_margin"], bool), location, "non_inferiority_margin", "must be numeric", "record the numeric margin")
        paired = contract["paired_comparison"]
        _require(isinstance(paired, dict) and set(paired) == {"method", "pass_inequality", "boundary_inclusive"}, location, "paired_comparison", "must contain method, pass_inequality, and boundary_inclusive", "freeze the exact paired decision")
        _require(paired["pass_inequality"] in {">", ">=", "<", "<="} and isinstance(paired["boundary_inclusive"], bool), location, "paired_comparison", "has an invalid inequality or boundary flag", "use an explicit inequality and boolean boundary")
        timeout = contract["timeout_policy"]
        _require(isinstance(timeout, dict) and set(timeout) == {"omp_max_time_seconds", "rpc_grace_seconds", "per_attempt_seconds", "overall"}, location, "timeout_policy", "must contain all timeout policy fields", "freeze effective per-attempt and overall timeout rules")
        _require(all(isinstance(timeout[field], (int, float)) and timeout[field] > 0 for field in ("omp_max_time_seconds", "rpc_grace_seconds", "per_attempt_seconds")), location, "timeout_policy", "numeric timeouts must be positive", "record positive seconds")
        _require(isinstance(timeout["overall"], str) and bool(timeout["overall"]), location, "timeout_policy.overall", "must be a non-empty rule", "record the overall timeout calculation")
        config = contract["execution_config"]
        _require(isinstance(config, dict) and set(config) == {"model", "profile", "tools", "thinking", "attempt_count", "system_prompt_sha256"}, location, "execution_config", "must freeze model, profile, tools, thinking, attempt_count, and system_prompt_sha256", "record the complete execution configuration")
        _require(all(isinstance(config[field], str) and config[field] for field in ("model", "profile", "thinking")), location, "execution_config", "model, profile, and thinking must be non-empty strings", "freeze exact runtime values")
        _require(isinstance(config["tools"], list) and all(isinstance(item, str) and item for item in config["tools"]), location, "execution_config.tools", "must be a string array", "freeze the exact tool allowlist")
        _require(isinstance(config["attempt_count"], int) and config["attempt_count"] > 0, location, "execution_config.attempt_count", "must be positive", "record the attempt count")
        _require(config["system_prompt_sha256"] is None or isinstance(config["system_prompt_sha256"], str) and bool(HEX64.fullmatch(config["system_prompt_sha256"])), location, "execution_config.system_prompt_sha256", "must be null or a SHA-256 hash", "pin the prompt hash when a custom prompt is used")
        _validate_revision(root, contract["baseline_catalog_revision"], location, "baseline_catalog_revision")
        _validate_revision(root, contract["treatment_catalog_revision"], location, "treatment_catalog_revision", nullable=True)


def _entry_revision(entry: dict[str, Any], contract: dict[str, Any], field: str) -> Any:
    return entry[field] if entry[field] is not None else contract[field]


def validate_repository(root: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    manifest_path = (manifest_path or root / "evals/suites.json").resolve()
    manifest = load_manifest(manifest_path)
    _require(set(manifest) == TOP_FIELDS, str(manifest_path), "fields", f"expected exactly {sorted(TOP_FIELDS)}", "add missing fields and remove unknown fields")
    _require(manifest["schema_version"] == 1, str(manifest_path), "schema_version", "must equal 1", "set schema_version to 1")
    _validate_revision(root, manifest["base_catalog_revision"], str(manifest_path), "base_catalog_revision")
    base_skills = revision_skills(root, manifest["base_catalog_revision"])
    skills = current_skills(root)
    validate_contracts(root, manifest, manifest_path)
    pair_exceptions: set[tuple[str, str, tuple[str, ...]]] = set()
    _require(isinstance(manifest["routing_pair_exceptions"], list), str(manifest_path), "routing_pair_exceptions", "must be an array", "use [] when no reviewed exceptions exist")
    for index, item in enumerate(manifest["routing_pair_exceptions"]):
        location = f"{manifest_path}:routing_pair_exceptions[{index}]"
        _require(isinstance(item, dict) and set(item) == {"status", "split", "available_skills", "reviewer", "reason"}, location, "fields", "must contain status, split, available_skills, reviewer, and reason", "record the complete reviewed exception")
        _require(item["status"] in ACTIVE_STATUSES and item["split"] in SPLITS, location, "status/split", "must identify an active lifecycle and split", "use an active status and valid split")
        _require(_strings(item["available_skills"]) and len(item["available_skills"]) == 2, location, "available_skills", "must name exactly two skills", "record the confusable pair")
        _require(all(isinstance(item[field], str) and item[field] for field in ("reviewer", "reason")), location, "reviewer/reason", "must be non-empty", "record the reviewer and rationale")
        pair_exceptions.add((item["status"], item["split"], tuple(sorted(item["available_skills"]))))

    retired: dict[str, dict[str, Any]] = {}
    _require(isinstance(manifest["retired_skills"], list), str(manifest_path), "retired_skills", "must be an array", "use [] when no identities are retired")
    for index, item in enumerate(manifest["retired_skills"]):
        location = f"{manifest_path}:retired_skills[{index}]"
        _require(isinstance(item, dict) and set(item) == {"name", "source_revision", "retirement_revision", "reason"}, location, "fields", "must contain exactly name, source_revision, retirement_revision, and reason", "record the complete retired identity")
        _require(isinstance(item["name"], str) and item["name"] not in retired, location, "name", "must be a unique non-empty identity", "remove duplicate retirement records")
        _require(item["name"] not in skills, location, "name", "is still an enabled root", "remove the retirement record or the enabled root")
        _validate_revision(root, item["source_revision"], location, "source_revision")
        _validate_revision(root, item["retirement_revision"], location, "retirement_revision")
        _require(isinstance(item["reason"], str) and bool(item["reason"]), location, "reason", "must be non-empty", "explain the retirement")
        retired[item["name"]] = item

    entries = manifest["case_files"]
    _require(isinstance(entries, list), str(manifest_path), "case_files", "must be an array", "list every evals/cases JSONL file")
    discovered = {path.relative_to(root).as_posix() for path in (root / "evals/cases").glob("*.jsonl")}
    listed: set[str] = set()
    rows_by_entry: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    active_ids: dict[str, tuple[str, int]] = {}
    historical_ids: defaultdict[str, list[str]] = defaultdict(list)
    coverage: defaultdict[tuple[str, str, str], set[str]] = defaultdict(set)
    behavior_coverage: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    routing_groups: defaultdict[tuple[str, str, tuple[str, ...]], set[str]] = defaultdict(set)
    proposal_roots: set[str] = set()
    proposal_roots_by_entry: dict[str, set[str]] = {}

    for index, entry in enumerate(entries):
        location = f"{manifest_path}:case_files[{index}]"
        _require(isinstance(entry, dict) and set(entry) == ENTRY_FIELDS, location, "fields", f"expected exactly {sorted(ENTRY_FIELDS)}", "add missing fields and remove unknown fields")
        rel = entry["path"]
        _require(isinstance(rel, str) and rel.startswith("evals/cases/") and rel.endswith(".jsonl"), location, "path", "must be a repository-relative JSONL path under evals/cases", "use evals/cases/<name>.jsonl")
        resolved = (root / rel).resolve()
        _require(resolved.parent == (root / "evals/cases").resolve(), location, "path", "escapes evals/cases or is nested", "use a direct file under evals/cases")
        _require(rel not in listed, location, "path", "is listed more than once", "keep exactly one manifest entry per case file")
        listed.add(rel)
        _require(resolved.is_file(), location, "path", "does not exist", "create the case file or remove its manifest entry")
        _require(entry["kind"] in KINDS, location, "kind", f"unsupported value {entry['kind']!r}", "use routing, behavior, or repository")
        _require(entry["split"] in SPLITS, location, "split", f"unsupported value {entry['split']!r}", "use development or holdout")
        _require(entry["status"] in STATUSES, location, "status", f"unsupported value {entry['status']!r}", f"use one of {sorted(STATUSES)}")
        _require(isinstance(entry["suite"], str) and bool(entry["suite"]), location, "suite", "must be non-empty", "name the owning suite")
        _require(isinstance(entry["frozen_sha256"], str) and bool(HEX64.fullmatch(entry["frozen_sha256"])), location, "frozen_sha256", "must be a SHA-256 hash", "record the exact case-file hash")
        _require(sha256_file(resolved) == entry["frozen_sha256"], location, "frozen_sha256", "does not match file content", "review the change and update the frozen hash in a separate evaluator change")
        _require(entry["comparison_contract"] in manifest["comparison_contracts"], location, "comparison_contract", "does not name a registered contract", "reference an existing frozen suite contract")
        contract = manifest["comparison_contracts"][entry["comparison_contract"]]
        _validate_revision(root, entry["baseline_catalog_revision"], location, "baseline_catalog_revision", nullable=True)
        _validate_revision(root, entry["treatment_catalog_revision"], location, "treatment_catalog_revision", nullable=True)
        if entry["status"] == "independent-holdout":
            _require(entry["split"] == "holdout", location, "split", "independent-holdout must be holdout", "set split to holdout")
        if entry["status"] == "release-only":
            _require(entry["split"] == "holdout", location, "split", "release-only must be holdout", "set split to holdout")
        if entry["status"] == "historical":
            _require(isinstance(entry["historical_reason"], str) and bool(entry["historical_reason"]), location, "historical_reason", "is required for historical evidence", "explain why the file is outside active validation")
            _require(entry["baseline_catalog_revision"] is not None or entry["treatment_catalog_revision"] is not None, location, "baseline_catalog_revision", "historical entry has no retained evaluated-catalog pin", "retain at least the immutable baseline or treatment revision")
        else:
            _require(entry["historical_reason"] is None, location, "historical_reason", "must be null outside historical status", "set historical_reason to null")
        if entry["split"] == "holdout" and entry["status"] != "historical":
            revision_fields = (
                ("baseline_catalog_revision",)
                if entry["status"] == "proposal"
                else ("baseline_catalog_revision", "treatment_catalog_revision")
            )
            for field in revision_fields:
                pin = _entry_revision(entry, contract, field)
                _validate_revision(root, pin, location, field)

        rows = load_rows(resolved, entry["kind"], entry["split"])
        rows_by_entry[rel] = rows
        file_proposal_roots: set[str] = set()
        for number, row in rows:
            row_location = f"{resolved}:{number}"
            identities = {row["target_skill"]}
            if row["kind"] == "routing":
                identities.update(row["available_skills"])
                identities.update(row["evaluated_skills"])
            if entry["status"] in ACTIVE_STATUSES:
                forbidden = identities & retired.keys()
                _require(not forbidden, row_location, "skill identities", f"active-validation row references retired identities {sorted(forbidden)}", "move immutable evidence to historical status or use current identities")
                unknown = identities - skills
                _require(not unknown, row_location, "skill identities", f"active-validation row references unknown roots {sorted(unknown)}", "use current root skill directory names")
                previous = active_ids.get(row["id"])
                _require(previous is None, row_location, "id", f"duplicates active case at {previous}", "make active case IDs globally unique")
                active_ids[row["id"]] = (rel, number)
            elif entry["status"] == "historical":
                missing = identities - skills
                undeclared = missing - retired.keys()
                _require(not undeclared, row_location, "skill identities", f"historical row references undeclared missing roots {sorted(undeclared)}", "declare each missing identity exactly once in retired_skills")
                historical_ids[row["id"]].append(rel)
            else:
                absent_base = identities - base_skills
                _require(len(absent_base) == 1, row_location, "skill identities", f"proposal must reference one root absent at base_catalog_revision, found {sorted(absent_base)}", "use the same single proposed root in every proposal row")
                proposal_roots.update(absent_base)
                file_proposal_roots.update(absent_base)

            if entry["status"] == "canonical":
                coverage[(entry["split"], "target", row["target_skill"])].add(rel)
                if row["kind"] == "routing":
                    exact_values = {
                        row["target_skill"],
                        f"SELECTED_SKILL: {row['target_skill']}",
                    }
                    exact = any(
                        check.get("critical") is True
                        and check.get("op") == "equals"
                        and check.get("value") in exact_values
                        for check in row["checks"]
                    )
                    _require(exact, row_location, "checks", "active routing case lacks a critical exact-route check", f"add a critical equals check for {row['target_skill']} or SELECTED_SKILL: {row['target_skill']}")
                    for skill in row["evaluated_skills"]:
                        coverage[(entry["split"], "evaluated", skill)].add(rel)
                    routing_groups[(entry["status"], entry["split"], tuple(sorted(row["available_skills"])))].add(row["target_skill"])
                else:
                    behavior_coverage[(entry["split"], row["target_skill"])].add(rel)
            elif entry["status"] in ACTIVE_STATUSES and row["kind"] == "routing":
                exact_values = {
                    row["target_skill"],
                    f"SELECTED_SKILL: {row['target_skill']}",
                }
                exact = any(
                    check.get("critical") is True
                    and check.get("op") == "equals"
                    and check.get("value") in exact_values
                    for check in row["checks"]
                )
                _require(exact, row_location, "checks", "active routing case lacks a critical exact-route check", f"add a critical equals check for {row['target_skill']} or SELECTED_SKILL: {row['target_skill']}")
                routing_groups[(entry["status"], entry["split"], tuple(sorted(row["available_skills"])))].add(row["target_skill"])
        if entry["status"] == "proposal":
            _require(len(file_proposal_roots) == 1, location, "skill identities", f"proposal rows do not consistently reference one root: {sorted(file_proposal_roots)}", "use the same single proposed root in every row")
            proposal_roots_by_entry[rel] = file_proposal_roots

    missing_files = discovered - listed
    extra_files = listed - discovered
    _require(not missing_files, str(manifest_path), "case_files", f"unclassified JSONL files {sorted(missing_files)}", "add each file exactly once")
    _require(not extra_files, str(manifest_path), "case_files", f"listed paths are not discovered case files {sorted(extra_files)}", "remove stale entries")
    for case_id, paths in historical_ids.items():
        if len(paths) > 1:
            _require(all(next(item for item in entries if item["path"] == path)["historical_reason"] for path in paths), str(manifest_path), "historical_reason", f"duplicate historical id {case_id!r} lacks lifecycle explanation", "explain every historical duplicate")
    for key, targets in routing_groups.items():
        _status, split, pair = key
        _require((len(pair) == 2 and targets == set(pair)) or key in pair_exceptions, str(manifest_path), f"routing pair {pair}", f"{split} A/B pair lacks its reverse target", "add the reverse case or a reviewed routing_pair_exceptions entry")

    candidate = manifest["admission_candidate"]
    candidate_name: str | None = None
    if candidate is not None:
        location = f"{manifest_path}:admission_candidate"
        _require(isinstance(candidate, dict) and set(candidate) == {"root", "treatment_catalog_revision"}, location, "fields", "must contain exactly root and treatment_catalog_revision", "record one candidate root and its immutable treatment revision")
        candidate_name = candidate["root"]
        _require(isinstance(candidate_name, str) and candidate_name in skills, location, "root", "must name exactly one current enabled root", "name the sole pending root")
        _require(candidate_name not in base_skills, location, "root", "was already present at base_catalog_revision", "clear admission_candidate or pin the correct older base revision")
        _validate_revision(root, candidate["treatment_catalog_revision"], location, "treatment_catalog_revision")
        _require(root_matches_revision(root, candidate_name, candidate["treatment_catalog_revision"]), location, "treatment_catalog_revision", "candidate root differs from the pinned revision", "freeze the candidate and pin that exact commit")
        _require(candidate_name in proposal_roots, location, "root", f"no proposal files refer to candidate {candidate_name!r}", "retain frozen proposal holdout entries for this candidate")
        candidate_proposals = [
            entry
            for entry in entries
            if entry["status"] == "proposal"
            and entry["split"] == "holdout"
            and proposal_roots_by_entry.get(entry["path"]) == {candidate_name}
        ]
        _require(bool(candidate_proposals), location, "root", "has no proposal holdout entries", "freeze proposal holdout routing and behavior files")
        for entry in candidate_proposals:
            pin = _entry_revision(entry, manifest["comparison_contracts"][entry["comparison_contract"]], "treatment_catalog_revision")
            _require(pin == candidate["treatment_catalog_revision"], f"{manifest_path}:{entry['path']}", "treatment_catalog_revision", "does not match admission_candidate", "pin the same frozen treatment revision")

    for skill in sorted(skills):
        required_splits = ("development",) if skill == candidate_name else ("development", "holdout")
        for split in required_splits:
            for role in ("target", "evaluated"):
                _require(bool(coverage[(split, role, skill)]), str(manifest_path), "canonical coverage", f"enabled skill {skill!r} lacks canonical {split} routing coverage as {role}", "add a canonical routing case in that split")
    new_skills = skills - base_skills
    for skill in sorted(new_skills):
        required_splits = ("development",) if skill == candidate_name else ("development", "holdout")
        for split in required_splits:
            _require(bool(behavior_coverage[(split, skill)]), str(manifest_path), "canonical behavior coverage", f"new enabled skill {skill!r} lacks canonical {split} behavior evidence", "add canonical behavior cases required by admission")
    if candidate is None:
        _require(not proposal_roots & skills, str(manifest_path), "admission_candidate", f"current proposed roots {sorted(proposal_roots & skills)} require pending candidate state", "set admission_candidate until full canonical holdout coverage is complete")

    return {
        "manifest": manifest,
        "entries": entries,
        "rows": rows_by_entry,
        "current_skills": skills,
        "base_skills": base_skills,
        "canonical_coverage": coverage,
    }


def select_case_files(
    manifest: dict[str, Any],
    repo_root: Path,
    *,
    mode: str = "normal",
    suite: str | None = None,
    case_paths: list[Path] | None = None,
    allow_historical: bool = False,
    historical_catalog: str | None = None,
    proposal_baseline: Path | None = None,
    condition: str | None = None,
) -> dict[str, Any]:
    _require(mode in MODES, "evals/suites.json", "mode", f"unsupported mode {mode!r}", f"use one of {sorted(MODES)}")
    _require(condition in {None, "baseline", "treatment"}, "evals/suites.json", "condition", f"unsupported condition {condition!r}", "use baseline or treatment")
    entries = manifest["case_files"]
    by_path = {entry["path"]: entry for entry in entries}
    requested: list[dict[str, Any]]
    if proposal_baseline is not None:
        _require(mode == "proposal-baseline" and suite is None and not case_paths, "evals/suites.json", "proposal_baseline", "cannot be combined with suite/case paths or another mode", "use only --proposal-baseline <path>")
        rel = proposal_baseline.resolve().relative_to(repo_root.resolve()).as_posix()
        _require(rel in by_path, "evals/suites.json", "proposal_baseline", f"path {rel!r} is absent from manifest", "register the proposal file")
        requested = [by_path[rel]]
    elif case_paths:
        _require(suite is None, "evals/suites.json", "selection", "suite and case_paths are mutually exclusive", "choose one selection form")
        requested = []
        for path in case_paths:
            try:
                rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
            except ValueError as error:
                raise ValueError(f"evals/suites.json:case_paths: {path} escapes the repository; choose a manifest case path") from error
            _require(rel in by_path, "evals/suites.json", "case_paths", f"path {rel!r} is absent from manifest", "register the file before selection")
            requested.append(by_path[rel])
    else:
        _require(suite is not None, "evals/suites.json", "suite", "is required without explicit case paths", "pass --suite or --cases")
        requested = [entry for entry in entries if entry["suite"] == suite]
        _require(bool(requested), "evals/suites.json", "suite", f"unknown suite {suite!r}", "choose a registered suite")

    if mode == "normal":
        selected = [entry for entry in requested if entry["status"] == "canonical" and entry["split"] == "development"]
        historical = [entry for entry in requested if entry["status"] == "historical"] if case_paths else []
        if historical:
            _require(allow_historical and historical_catalog in {"baseline", "treatment"}, "evals/suites.json", "historical selection", "historical development requires explicit low-level selection and a retained catalog side", "pass --allow-historical --historical-catalog baseline|treatment with --cases")
            _require(all(entry["split"] == "development" for entry in historical), "evals/suites.json", "historical selection", "normal mode cannot expose historical holdout", "use guarded holdout mode for holdout evidence")
            selected = historical
        rejected_holdout = [entry for entry in requested if entry["split"] == "holdout" and case_paths]
        _require(not rejected_holdout, "evals/suites.json", "split", "low-level development mode cannot expose holdout files", "use --mode holdout")
    elif mode == "proposal-baseline":
        selected = requested
        _require(len(selected) == 1 and selected[0]["status"] == "proposal" and selected[0]["split"] == "development", "evals/suites.json", "proposal_baseline", "must name one proposal development file", "select a frozen proposal development entry")
        _require(condition in {None, "baseline"}, "evals/suites.json", "condition", "proposal baseline cannot run treatment", "use --condition baseline")
    elif mode == "holdout":
        allowed = {"canonical", "proposal"} | ({"historical"} if case_paths else set())
        selected = [entry for entry in requested if entry["split"] == "holdout" and entry["status"] in allowed]
        _require(not case_paths or not any(entry["status"] in {"independent-holdout", "release-only"} for entry in requested), "evals/suites.json", "status", "independent or release-only holdout requires its dedicated mode", "use independent-holdout or release mode")
        if any(entry["status"] == "historical" for entry in selected):
            _require(allow_historical, "evals/suites.json", "allow_historical", "historical holdout is not enabled", "pass --allow-historical")
    elif mode == "independent-holdout":
        selected = [entry for entry in requested if entry["status"] == "independent-holdout" and entry["split"] == "holdout"]
    else:
        _require(manifest["admission_candidate"] is None, "evals/suites.json", "admission_candidate", "release is blocked while a candidate is pending", "canonicalize full holdout coverage and clear admission_candidate")
        selected = [entry for entry in requested if entry["status"] in {"canonical", "independent-holdout", "release-only"}]
    _require(bool(selected), "evals/suites.json", "selection", "no case files are eligible for this lifecycle mode", "choose a compatible suite, status, split, and mode")

    contracts = {entry["comparison_contract"] for entry in selected}
    _require(len(contracts) == 1, "evals/suites.json", "comparison_contract", f"selection spans contracts {sorted(contracts)}", "run one suite contract at a time")
    contract = manifest["comparison_contracts"][contracts.pop()]
    baselines = {entry["baseline_catalog_revision"] or contract["baseline_catalog_revision"] for entry in selected}
    treatments = {entry["treatment_catalog_revision"] or contract["treatment_catalog_revision"] for entry in selected}
    _require(len(baselines) == 1 and len(treatments) == 1, "evals/suites.json", "catalog revisions", "selection contains inconsistent comparison pins", "split files with different immutable pairs into separate suites or runs")
    baseline = baselines.pop()
    treatment = treatments.pop()
    for entry in selected:
        if entry["split"] == "holdout":
            _require(revision_resolves(repo_root, baseline) and revision_resolves(repo_root, treatment), f"evals/suites.json:{entry['path']}", "catalog revisions", "guarded holdout pins are missing or unresolvable", "retain both immutable baseline and treatment commits")
    guarded = any(entry["split"] == "holdout" for entry in selected)
    evaluated: str | None = None
    if any(entry["status"] == "historical" for entry in selected) and not guarded:
        field = f"{historical_catalog}_catalog_revision"
        evaluated = selected[0][field] or contract[field]
        _require(revision_resolves(repo_root, evaluated), f"evals/suites.json:{selected[0]['path']}", field, "selected historical pin is absent or unresolvable", "select a retained side or restore its commit")
    elif mode == "proposal-baseline":
        evaluated = baseline
    elif condition is not None:
        evaluated = baseline if condition == "baseline" else treatment
    return {
        "entries": selected,
        "comparison_contract": contract,
        "baseline_catalog_revision": baseline,
        "treatment_catalog_revision": treatment,
        "evaluated_catalog_revision": evaluated,
        "guarded_holdout": guarded,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    try:
        result = validate_repository(args.root, args.manifest)
    except (OSError, ValueError) as error:
        print(f"evaluation validation failed: {error}", file=sys.stderr)
        return 1
    print(f"validated {len(result['entries'])} case files; canonical coverage is derived from canonical rows only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
