# Skill Set Improvement Plan

## 1. Purpose

Improve the full skill set without weakening its current strengths: OMP-native routing, exact provenance, portable skill-local references, deterministic validation, and live baseline-versus-treatment evaluation.

This plan fixes four classes of gap:

1. incomplete routing and behavior evidence;
2. weak evaluation-suite inventory and artifact governance;
3. inconsistent skill anatomy and oversized routing descriptions;
4. missing skills that have a distinct, evidence-backed unit of work.

The work is complete only when the repository can prove what is covered, what is not covered, and why each enabled skill belongs in the catalog.

## 2. Decision Summary

Execute in this order:

1. freeze the current catalog and evaluation baseline;
2. add a machine-readable evaluation-suite manifest and structural validator;
3. close the four canonical routing gaps;
4. document a flexible skill anatomy, audit and remediate catalog-wide conformance, and strengthen objective validation;
5. add behavior evidence in risk-ordered waves;
6. resolve the existing Simplified Engineering English release blockers;
7. measure description-density changes one family at a time;
8. pilot three narrowly scoped skills: source-driven development, API and interface design, and deprecation and migration;
9. admit security, debugging, observability, performance, or other lifecycle skills only after their demand gates pass.

Do not clone the upstream repository's catalog or runtime. Its useful practices are contributor guidance, progressive disclosure, explicit exclusions, routing evaluations, and pressure-tested workflows. Its always-on router, root-shared references, copied host adapters, personas, and command policies do not fit this repository.

## 3. Scope, Non-Goals, and Invariants

### 3.1 In scope

- all 25 existing skills;
- every JSONL file under `evals/cases/`;
- routing and behavior evaluation coverage;
- evaluation results, release reports, and durable evidence;
- repository validation and contributor guidance;
- routing-description cost and collision reduction;
- three proposed skills and four conditional gap investigations;
- provenance, licensing, reference portability, and README inventory accuracy.

### 3.2 Non-goals

- importing the upstream catalog wholesale;
- adding an always-on meta-router or session hook;
- replacing OMP's native skill discovery;
- moving references into a root-level shared directory;
- hand-maintaining command wrappers for multiple agent hosts;
- adopting upstream personas or lifecycle stages as repository architecture;
- requiring test-driven development, a full-suite run, a build, or a commit for every task;
- automatically committing user work;
- treating lexical similarity as proof of semantic routing failure;
- using rough character-to-token conversion as measured prompt cost;
- adding broad security, debugging, observability, or performance skills without evidence of a distinct recurring need.

### 3.3 Invariants

1. OMP remains the sole runtime router. Skills are discovered through `skill://<name>` and `/skill:<name>`.
2. References required by a skill remain inside that skill directory so a skill can be installed independently.
3. Adapted material retains exact source path, immutable source revision, adaptation type, license, and notice.
4. Deterministic checks run before model judges.
5. Treatment comparisons use the same model, profile, tools, and attempt count as their baselines.
6. Development prompts may guide iteration; holdout prompts stay frozen until a release decision.
7. No skill receives an efficacy claim without behavior evidence.
8. The harness, not an individual skill, owns global planning, delegation, verification, and user-ground-truth rules.
9. Evaluator or rubric changes are reviewed and frozen in a separate pre-treatment change from the skill change they measure.
10. Historical evidence is preserved even when it is no longer part of an active suite.

## 4. Baseline Evidence

Record these values in the first implementation change and regenerate them rather than copying them into future reports.

| Area | Current snapshot | Consequence |
|---|---:|---|
| Skills | 25 | The manifest and README must agree on 25 entries before additions. |
| Total `SKILL.md` lines | 5,531 | Whole-catalog rewrites would be high risk. |
| Median `SKILL.md` lines | 236 | Progressive disclosure should be targeted, not imposed mechanically. |
| Skill-local Markdown references | 48 | Portability is already strong and must be retained. |
| Python scripts | 12 | Script status and boundaries need one documented convention. |
| Derived context-engineering skills | 17 | Routing collisions are more likely within this family. |
| Leancode skills | 4 | This family produces all current high lexical-similarity warnings. |
| ML-system-design-derived skills | 3 | Provenance and domain overlap need continued validation. |
| Repository-original skills by frontmatter | 4 | Simplified Engineering English and three Leancode companion skills declare repository-original provenance. |
| Upstream skills at pinned comparison revision | 25 | Catalog size alone does not show equivalent coverage. |
| Upstream total `SKILL.md` lines | 7,805 | Importing it wholesale would increase prompt and maintenance load. |
| Evaluation case files | 25 | Every file needs an explicit lifecycle classification. |
| Evaluation rows | 276 | Counts must be derived by validator, not maintained manually. |
| Simplified Engineering English rows | 193 | This skill dominates the corpus; catalog-level evidence is uneven. |
| Leancode rows | 28 | Leancode has meaningful but narrower evidence. |
| Repository fixture rows | 10 | Most skills lack artifact-backed behavior cases. |
| Canonical routing coverage | 21 of 25 skills | Four enabled skills lack canonical development-and-holdout ownership evidence. |
| Total description characters | 10,600 | This is a serialization fact, not token or latency evidence. |
| Average description characters | 424 | Averages hide a few large descriptions. |

The four canonical routing gaps are:

- `bdi-mental-states`;
- `latent-briefing`;
- `long-horizon-prompting`;
- `lossless-doc-compress`.

The largest descriptions at this snapshot are `leancode` (937 characters), `long-horizon-prompting` (851), `self-improvement-loops` (740), `context-fundamentals` (688), and `simplified-engineering-english` (664). Measure actual serialized OMP input tokens and routing latency before changing them.

A warning-only TF-IDF diagnostic found these overlaps:

| Pair | Similarity |
|---|---:|
| `leancode` / `leancode-review` | 0.707 |
| `leancode` / `leancode-audit` | 0.626 |
| `leancode` / `leancode-debt` | 0.567 |

No pair crossed the diagnostic's 0.75 error threshold. These values prioritize evaluation; they do not justify description edits by themselves.

The current Simplified Engineering English release report is labeled **NO-GO**, but the missing required evidence below makes the decision **INCONCLUSIVE** under the evidence policy in Workstream D; regenerate the decision after remediation because:

1. its 26-pair, seven-dimension human-calibration packet has no reviewer scores;
2. its technical attestation lacks a named qualified authority and completed assessments;
3. raw evidence is local and Git-ignored rather than stored durably;
4. 30 of 78 swapped judge pairs were position-sensitive;
5. six pairs carried critical flags.

The comparison baseline is upstream revision `be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39`. Re-run the comparison before implementing new upstream-derived skills if that revision changes.

## 5. Target State

The target repository has these properties:

- every enabled skill has canonical development and holdout routing coverage;
- every new or materially changed skill has development and frozen-holdout behavior evidence;
- every case file is classified as proposal, canonical, independent holdout, release-only, or historical;
- suite membership, coverage, case IDs, and references are machine-validated;
- objective skill-format rules fail deterministically while semantic quality stays under review and live evaluation;
- description changes report measured token and latency effects, not character estimates;
- release reports link to durable, immutable evidence;
- every routing and behavior comparison uses a frozen, suite-specific decision contract;
- each skill states its owned unit of work, exclusions, process, failure modes, and exit evidence, and the existing catalog has been audited against that contract;
- new skills enter one at a time with provenance, local references, separately frozen evaluators and cases, routing cases, behavior cases, and rollback boundaries;
- multi-host packaging remains a separate product decision.

## 6. Workstream A: Evaluation Suite Manifest and Structural Validator

### 6.1 Problem

The [evaluation guide](../evals/README.md) describes nine canonical suites, but `evals/cases/` contains 25 JSONL files. Versioned, independent, final, and release files are not machine-classified. A contributor can accidentally omit a file, run historical data as active data, duplicate an ID, or report incomplete coverage.

### 6.2 Decision

Add a repository-owned manifest at `evals/suites.json` and a deterministic standard-library validator at `evals/validate.py`. Do not overload `scripts/validate_skills.py` with evaluation lifecycle policy.

Suggested manifest shape:

```json
{
  "schema_version": 1,
  "base_catalog_revision": "<immutable repository revision>",
  "admission_candidate": null,
  "retired_skills": [],
  "case_files": [
    {
      "path": "evals/cases/routing-development.jsonl",
      "kind": "routing",
      "split": "development",
      "status": "canonical",
      "suite": "routing"
    }
  ]
}
```

Lifecycle and selection are defined by this matrix:

| Status | Validation and ID scope | Active coverage | Normal `--suite` | Guarded holdout (`--mode holdout`) | Independent-holdout mode | Release mode | Proposal-baseline mode |
|---|---|---|---|---|---|---|---|
| `proposal` | proposal-specific structural and single-proposed-root checks; outside global active-ID uniqueness | no | no | yes: holdout only after the frozen treatment revision and comparison configuration are recorded | no | no | yes: development only after proposal freeze |
| `canonical` | current-root validation and global active-ID uniqueness | yes | development only | yes: holdout only | no | development normally; holdout through the guard | no |
| `independent-holdout` | current-root validation and global active-ID uniqueness | no | no | selected only through independent-holdout or release mode | yes, through the guard | yes, through the guard | no |
| `release-only` | current-root validation and global active-ID uniqueness | no | no | selected only through release mode when `split: holdout` | no | yes; every holdout selection goes through the guard | no |
| `historical` | historical and retired-identity checks; outside global active-ID uniqueness | no | no | holdout only with `--allow-historical` and both retained immutable revisions | no | no | no |

The active-validation set is `canonical`, `independent-holdout`, and `release-only`; active coverage is derived only from `canonical` rows. Normal suite selection is development-only. Every `split: holdout` file is unavailable while treatment content or comparison configuration remains editable, regardless of lifecycle status or selector. Independent-holdout and release selection delegate their holdout subset to the same guarded executor. Release-only data remains unavailable before the release gate.

A `retired_skills` item records `name`, source revision, retirement revision, and reason. It exists only to preserve immutable historical evidence after a rejected pilot is removed from the enabled catalog. A retired identity must not appear in an active-validation file.
The required top-level `admission_candidate` is normally `null`. During admission it may instead be `{ "root": "<root-directory-name>", "treatment_catalog_revision": "<immutable revision>" }`, naming exactly one root. This is a temporary manifest state, not a sixth case-file status and not an evaluated-skill list. The named root must be a current root absent at `base_catalog_revision`. It is the only enabled root exempt from full canonical coverage: it must already have canonical development coverage as both target and evaluated skill, while its frozen holdout files remain `proposal`, retain their frozen hashes, and pin the same treatment revision. Proposal holdout rows neither count as active coverage nor become available outside guarded holdout mode. Clearing the state requires making the candidate's development and holdout files canonical in the same transition; rejection instead removes the root and reclassifies its files as historical.

Do not add a manually maintained evaluated-skill list. Derive it from case rows. Derive new-skill identity from `base_catalog_revision`: resolve the root skill directories at that immutable revision, and classify a current enabled root as new only when it is absent from that resolved set.

### 6.3 Validator requirements

`evals/validate.py` must fail when:

1. a JSONL file under `evals/cases/` is absent from the manifest or listed more than once;
2. a manifest path does not exist, escapes the repository, or is not under `evals/cases/`;
3. a row is invalid JSON or lacks the fields required by its `kind`;
4. a manifest `kind` or `split` disagrees with a row;
5. case IDs are duplicated within the global active-ID scope;
6. an active-validation row references a `target_skill`, `available_skills`, or `evaluated_skills` entry that is not a current root skill directory;
7. a historical row references a missing skill that is not declared exactly once in `retired_skills`;
8. an active-validation file references a `retired_skills` identity;
9. a canonical routing case omits its target from `available_skills` or `evaluated_skills`;
10. an active-validation routing case lacks a critical exact-route check;
11. an A/B routing pair lacks its reverse case without an explicit, reviewed exception;
12. any enabled skill other than the manifest's sole `admission_candidate` lacks canonical development and holdout coverage as both a target and an evaluated skill, or the candidate lacks canonical development coverage in both roles;
13. a new enabled skill, defined as a current enabled root absent from the catalog at `base_catalog_revision`, lacks the canonical behavior cases required by its admission phase;
14. a file is selected outside the lifecycle matrix, including a historical file without `--allow-historical`, a proposal development file outside proposal-baseline mode, or any `split: holdout` file outside guarded holdout execution;
15. a routing or behavior suite selectable by an execution mode lacks a complete pre-registered comparison contract, or a holdout comparison lacks recorded immutable `baseline_catalog_revision` and `treatment_catalog_revision` values;
16. a proposal file references more than one root absent from the current catalog, or its rows do not consistently use the same single proposed root;
17. independent-holdout or release selection can execute a holdout without satisfying the guarded holdout preconditions;
18. `admission_candidate` is non-null but does not name exactly one current root absent at `base_catalog_revision`, its immutable treatment revision is missing or unresolvable, its current root differs from the root at that revision, or any of its proposal holdout entries is unfrozen or pins a different treatment revision;
19. `admission_candidate` is cleared without full canonical development and holdout coverage for that root, or release selection is attempted while it remains non-null;
20. a historical entry has lost all retained immutable evaluated-catalog revision pins, or a retained pin is unresolvable.

Historical duplicate IDs may remain only when all duplicates are outside the global active-ID scope and the manifest explains their status.

Store each pilot's development and holdout cases in pilot-specific files. Add and freeze them with their fixtures and evaluator logic under `proposal` status before the skill treatment. Freezing permits development proposal-baseline execution only; every proposal holdout attempt outside guarded holdout mode is invalid. During treatment, canonicalize only the development files. Once the treatment root is frozen, set `admission_candidate` to that root and revision; the validator then permits its canonical development coverage and matching frozen proposal holdout files while admission is pending. After the guarded pair passes, canonicalize the holdout files and clear `admission_candidate` in one transition, after which ordinary full-coverage validation applies. If admission fails, clear the state, remove the root, keep every pilot file byte-for-byte unchanged, reclassify the development and holdout files as `historical`, retain their immutable evaluated-catalog revision pins, add the retired identity, and remove the files from active suites. Do not put proposal cases into shared frozen files that would require row deletion during rollback.
Each proposal case-file entry records immutable `baseline_catalog_revision` and, before holdout execution, `treatment_catalog_revision` values for that pilot's actual pre-treatment and frozen treatment catalogs. It may use `base_catalog_revision` only when that revision is the pilot's pre-treatment catalog; later pilots must pin their own revision so previously admitted skills remain present. Proposal pilots may reuse these manifest pins in guarded holdout mode. When an entry becomes historical, preserve both pins when both exist and preserve whichever evaluated-catalog pin exists otherwise; never replace either with the working tree or retirement revision. Every other treatment must pre-register equivalent immutable revisions with its locked comparison configuration.

The validator must not call a model, infer semantic trigger quality, or declare a behavior correct from source text.

### 6.4 Runner changes

Extend `evals/run.py` with a suite-oriented entry point:

- normal `--suite <name>` selects only `split: development` files with `canonical` status and rejects any request that would expose a holdout;
- `--mode holdout` is the sole guarded holdout executor. Direct `--suite <name> --mode holdout` or `--cases <path> --mode holdout` entry verifies the locked comparison-contract hash and recorded immutable `baseline_catalog_revision` and `treatment_catalog_revision`, resolves both revisions to isolated catalog roots, runs the selected frozen cases only against those two roots, and never evaluates the working tree;
- `--suite <name> --mode independent-holdout` selects only `independent-holdout` files, and `--mode release` selects the eligible `canonical`, `independent-holdout`, and `release-only` files required by that suite. Both modes must dispatch every `split: holdout` selection to the same guarded holdout executor and fail if its preconditions are unmet;
- existing `--cases <path>` remains an explicit low-level development mode subject to the same lifecycle matrix. It rejects every `split: holdout` file unless combined with `--mode holdout`. A historical development file additionally requires `--allow-historical --historical-catalog baseline|treatment`; the runner selects the requested retained `baseline_catalog_revision` or `treatment_catalog_revision`, fails if that pin is absent or unresolvable, resolves it to an isolated catalog root, and never evaluates the working tree. When both pins exist, the explicit selector permits reproduction of either side;
- `--proposal-baseline <path>` is the only development execution path for a `proposal` file: it requires the manifest entry and frozen file hash, resolves that entry's `baseline_catalog_revision` to an isolated catalog root, and runs only its development cases against that pre-treatment catalog without activating the file, adding coverage, or making the proposed root available. Proposal holdout runs only through guarded holdout mode and may reuse the manifest-pinned baseline and treatment revisions;
- every result manifest records suite and mode, case-file paths and hashes, manifest schema version and hash, case-source revision, comparison-contract path and hash, model, profile, tool configuration, attempt count, effective per-attempt and overall timeout seconds, and each evaluated catalog revision and resolved root. A final holdout manifest always records both immutable baseline and treatment revisions and roots; changing either root or the locked configuration invalidates the pair.

Keep explicit case paths for forensic reproduction. The manifest is an inventory and safe default, not an abstraction that hides evidence.

### 6.5 Repository integration

- document statuses, fields, and commands in the [evaluation guide](../evals/README.md);
- add focused validator tests, preferably in a new `tests/test_eval_validation.py` rather than expanding the already large evaluation-harness test module;
- add runner-option tests to `tests/test_evaluation_harness.py` only where they exercise runner behavior;
- run `evals/validate.py` in `.github/workflows/validate-skills.yml` after skill validation;
- keep errors actionable: file, row, field, violated invariant, and repair direction.

### 6.6 Acceptance criteria

- all 25 current JSONL files appear exactly once in the manifest;
- status- and split-aware selection follows the lifecycle matrix: normal suites are development-only, and neither `--suite` nor low-level `--cases` can expose a holdout outside guarded holdout mode;
- the immutable base catalog and each proposal's actual pre-treatment catalog resolve from their pinned revisions; proposal files remain outside active coverage, proposal development runs only through proposal-baseline mode, and proposal holdout runs only through the guard after the treatment revision and configuration are frozen;
- coverage numbers are generated only from canonical rows; the sole pending `admission_candidate` validates with canonical development coverage and frozen proposal holdout entries pinned to its immutable treatment revision, but clearing the state and release both require full canonical development and holdout coverage;
- historical development execution requires an explicit retained baseline or treatment pin, resolves only that revision to an isolated root, and fails rather than using the working tree when the selected pin is missing or unresolvable;
- missing files, duplicate IDs in the active-ID scope, unknown or undeclared retired skills, active-validation references to retired skills, split mismatches, absent exact-route checks, invalid lifecycle selection or proposal baseline revision, holdout selection outside the guard, missing or mutable holdout revisions, invalid proposal identity, invalid or multiple admission candidates, candidate pin/root mismatch, candidate-state clearing without full canonical coverage, release with a pending candidate, missing or unresolvable historical pins, and incomplete comparison contracts each have a regression test. Runner regressions must cover early holdout rejection through both `--suite` and `--cases`, guarded delegation from independent-holdout and release modes, and baseline and treatment reproduction for a historical development case without working-tree fallback;
- validation performs no network or model calls.

## 7. Workstream B: Close the Four Canonical Routing Gaps

Add at least one distinct development pair and one frozen holdout pair for each missing skill. A pair contains the positive owner case and the nearest-neighbor negative case. Prompts must use user language rather than copied skill-description phrases.

| Target skill | Primary competitor | Positive boundary | Negative boundary |
|---|---|---|---|
| `bdi-mental-states` | `memory-systems` | beliefs, desires, intentions, rational traces, or RDF-to-belief transformation | persistence, retrieval, temporal memory, or entity consolidation without an agency-state model |
| `latent-briefing` | `context-optimization` | representation-level cross-agent compression with real KV/activation access | prompt, retrieval, partitioning, or token-budget optimization through ordinary APIs |
| `long-horizon-prompting` | `harness-engineering` | launch brief for an autonomous or parallel attack: exact success predicate, non-counting outcomes, persistence, stop/return contract, and adversarial audit | runtime loop controls, locked surfaces, logs, rollback, approvals, or execution governance |
| `lossless-doc-compress` | `simplified-engineering-english` | remove only provable redundancy while preserving every fact, qualifier, number, and caveat, with a removal log | rewrite engineering prose for actionability and lower ambiguity without a lossless-compression deliverable |

Each case must:

- name both competitors in `available_skills` and `evaluated_skills`;
- contain a critical exact-route check;
- contain a critical check against selecting the competitor where the boundary is exclusive;
- define observable success and prohibited outcomes;
- avoid vocabulary that makes the answer a string match;
- differ materially between development and holdout prompts;
- use the repository's existing routing schema rather than importing upstream-only fields.

Acceptance: generated canonical development-and-holdout routing coverage is 25 of 25, with no critical regression in existing routing cases.

## 8. Workstream C: Behavior Evidence for the Catalog

### 8.1 Evidence standard

Do not replace the live OMP RPC harness. Extend it consistently.

Every new or materially changed skill needs:

- at least one development behavior case;
- at least one frozen holdout behavior case;
- final holdout evidence produced only by guarded paired execution against recorded immutable baseline and treatment catalog roots;
- the same model, profile, tool configuration, attempt count, and effective per-attempt and overall timeouts in baseline and treatment;
- at least three attempts when the output can vary materially;
- deterministic checks before judge scoring;
- a repository fixture when the claimed result is a file or code change;
- a pressure condition that makes the common shortcut tempting;
- an explicit critical-failure definition.

A conversation-only artifact is acceptable only when the skill's deliverable is the conversation. Repository-mutating skills require fixture-backed output inspection.

Report catalog status using three evidence labels derived from active cases and results:

- `verified`: routing and behavior gates pass;
- `routing-only`: ownership is tested but task effectiveness is not;
- `unverified`: canonical ownership evidence is absent.

Do not maintain these labels by hand in the README.

**Pre-registered comparison contract**

Before any baseline or treatment run, freeze a versioned, suite-specific comparison contract in `evals/suites.json` or a file hash-pinned by it for every routing and behavior suite. It must state the metric and favorable direction, unit of analysis, attempt-to-case and case-to-suite aggregation, non-inferiority margin, exact paired comparison and pass inequality (including whether the boundary is inclusive), treatment of ties and missing or failed attempts, effective per-attempt and overall timeout policy, and handling of judge disagreement and position sensitivity. Before any holdout run, the same locked registration must also identify immutable baseline and treatment catalog revisions.

For complete evidence, compute each paired result and the suite decision exactly as registered; the gate passes only when the registered inequality is satisfied. The terms `non-inferior` and `unchanged or better` everywhere in this plan refer to this rule. A missing required attempt or an unregistered decision choice makes the result `INCONCLUSIVE`; no rule may be selected or changed after results are observed.

### 8.2 Wave 1: routing gaps and Leancode debt behavior

Add focused behavior cases for the four routing gaps immediately after their routing cases. Include `leancode-debt` in this behavior wave because its canonical routing pair already exists but behavior still needs direct evidence.

| Skill | Required observable behavior | Critical failure |
|---|---|---|
| `bdi-mental-states` | produces a valid BDI state or transformation and separates beliefs, desires, and intentions | substitutes a generic memory schema or conflates observed facts with intentions |
| `latent-briefing` | checks whether representation-level access exists, selects the method only when feasible, and gives an ordinary-context alternative otherwise | claims KV/activation compaction through an API that exposes only text |
| `long-horizon-prompting` | emits a launch brief with a precise success predicate, non-counting outcomes, persistence rules, stop/return conditions, approach registry, and adversarial audit | returns a generic checklist or omits the completion contract |
| `lossless-doc-compress` | preserves all facts, numbers, qualifiers, decisions, caveats, and obligation strength while producing a categorized removal log | silently changes or deletes information |
| `leancode-debt` | extracts only syntactically valid debt markers, including ceiling and revisit conditions, without editing source | treats ordinary TODOs as lean debt or modifies implementation |

### 8.3 Wave 2: high-confusion core

Prioritize the families most likely to route incorrectly:

1. `advanced-evaluation` versus `evaluation`;
2. `context-fundamentals`, `context-degradation`, `context-optimization`, and `context-compression`;
3. `filesystem-context` versus `memory-systems`;
4. `harness-engineering` versus `self-improvement-loops`;
5. `hosted-agents` versus `multi-agent-patterns`;
6. `project-development` versus `tool-design`.

For each family, include one task that should load exactly one owner and one task where two skills are legitimately complementary. This prevents an overfitted "always choose one" router.

### 8.4 Wave 3: review and output skills

Add or normalize behavior evidence for:

- `ai-stage-gate` and `ml-system-design-review`;
- `leancode-review` and `leancode-audit`;
- `simplified-engineering-english` and `lossless-doc-compress`;
- the remaining context and agent-infrastructure skills not covered in Wave 2.

Leancode and Simplified Engineering English retain their existing evidence. New cases fill missing catalog-level behavior; they do not discard the deeper skill-specific suites.

### 8.5 Gate

A wave passes only when:

- deterministic critical checks have zero regressions;
- frozen holdout performance, produced by the guarded paired executor against the recorded immutable roots, is non-inferior to its recorded baseline;
- judge disagreement and position sensitivity are reported rather than averaged away;
- any token or latency increase is measured and explained;
- result artifacts are stored durably under the policy in Workstream D.

## 9. Workstream D: Evidence and Release Governance

### 9.1 Resolve the existing Simplified Engineering English release blockers

Use the current [release report](../evals/results/see-improvement/release-report.md) as the authoritative blocker list.

1. Assign the 26-pair human-calibration packet to named reviewers.
2. Collect all seven dimension scores, reviewer confidence, and comments.
3. Adjudicate the 30 position-sensitive pairs; do not use only the favorable order.
4. Resolve or explicitly reject all six critical-flagged pairs.
5. Assign a named, qualified technical reviewer.
6. Complete the technical attestation with scope, reviewed artifacts, findings, and signature date.
7. Select a durable artifact store.
8. Upload complete baseline and treatment directories, including raw model responses, deterministic results, judge outputs, manifests, logs, and reports.
9. Record immutable URI, content hash, access policy, retention period, and responsible owner for each artifact set.
10. Regenerate the gate result from the completed inputs.

The plan deliberately does not choose the external artifact product. That is an operational decision. The storage contract above is mandatory regardless of product.

### 9.2 Repository-wide evidence policy

Every comparison report must identify:

- skill revision, case-source revision, and baseline and treatment evaluated catalog revisions and roots;
- case manifest and content hashes;
- comparison-contract path and content hash;
- model, profile, tools, attempts, baseline and treatment effective per-attempt and overall timeouts, and an explicit timeout-equality result;
- baseline and treatment artifact URIs and hashes;
- deterministic failures;
- judge configuration and ordering strategy;
- holdout status;
- human review status where required;
- final `GO`, `NO-GO`, or `INCONCLUSIVE` decision with failed gates.

`GO` requires complete evidence and every substantive gate to pass. `NO-GO` requires complete evidence and at least one failed substantive gate. `INCONCLUSIVE` is required whenever a required review, attempt, or artifact is missing or an attempt fails because of infrastructure; favorable automated metrics cannot replace the missing evidence.

### 9.3 Acceptance criteria

- the existing release report no longer points only to local Git-ignored evidence;
- named human and technical reviews are complete;
- position-sensitive and critical pairs have explicit dispositions;
- reports can be reproduced from immutable artifacts;
- no release claim depends on an unavailable local directory.

## 10. Workstream E: Skill Anatomy, Contributor Guidance, and Objective Validation

### 10.1 Add contributor documentation

Add `CONTRIBUTING.md` and `docs/skill-anatomy.md`, then link both from the [README](../README.md).

The anatomy is a content contract, not a mandatory heading template. Every skill must make these concepts easy to find:

1. purpose and owned unit of work;
2. positive triggers in user language;
3. exclusions and adjacent owners;
4. workflow or decision process;
5. failure modes, red flags, or shortcut rationalizations;
6. domain-specific exit evidence and output contract;
7. progressive-disclosure references;
8. status and boundary of executable scripts.

Existing headings may remain when they express the contract. Do not rewrite 25 skills to match one cosmetic outline.

### 10.2 Description guidance

A description must state:

- what unit of work the skill owns;
- when a user request should trigger it;
- the closest exclusions when routing would otherwise be ambiguous.

It should not summarize the full workflow. Details belong in the body or local references.

Description changes require routing evaluation. Character count is an objective bound; trigger quality is not.

### 10.3 Progressive disclosure

- keep the routing description short enough to scan as catalog metadata;
- keep core decisions and safety boundaries in `SKILL.md`;
- move deep examples, research notes, long rubrics, and reusable tables to skill-local references;
- keep each reference reachable directly from `SKILL.md`;
- avoid chains where one reference is discoverable only through another;
- treat a body above 500 lines as a review warning, not an automatic failure;
- split only when the extracted material is independently useful and the skill remains operable without loading every reference.

### 10.4 Cross-skill asset migration

Six current asset links make three skills depend on `project-development/references/case-studies.md`: `evaluation` has one, `multi-agent-patterns` has three, and `tool-design` has two. A standalone install of any of those skills loses cited evidence.

For each link, copy only the needed evidence into an owning skill-local reference, including the original source URL and date, or remove the claim. Do not create a root-shared evidence file. Bare references to another skill owner may remain, but a path such as `skill://other-skill/references/file.md` may not.

Extend the validator to reject cross-skill asset URIs while allowing `skill://<current-skill>/...` and bare owner references such as `skill://other-skill`. Inventory and remove all existing violations before making the rule a release gate.

### 10.5 Script convention

Executable helpers may remain Python. Each owning skill must document:

- **Status:** production helper, evaluator, or example;
- **Boundary:** what it validates or transforms and what it does not prove;
- **Run:** exact command and required inputs;
- **Output:** stable machine-readable or human-readable contract;
- **Failure:** non-zero conditions and repair direction.

Do not add empty `scripts/`, `references/`, or `assets/` directories.

### 10.6 Extend `scripts/validate_skills.py`

Add hard errors only for objective rules:

- directory and frontmatter `name` use lower-case kebab case;
- directory and frontmatter names match;
- description length is at most 1,024 characters;
- asset URIs may not traverse from one skill into another skill's files;
- existing provenance, revision, license, link, fragment, Python syntax, dependency, and README inventory checks continue to pass.

Add a warning, not an error, when `SKILL.md` exceeds 500 lines.

Do not add static checks that pretend to prove:

- trigger quality;
- exclusion completeness;
- workflow correctness;
- exit-evidence adequacy;
- semantic overlap.

Those belong to contributor review and live evaluation.

### 10.7 Catalog-wide manual conformance audit

Record a manual audit of all 25 existing skills against the eight anatomy concepts in Section 10.1 and of every script-owning skill against the five operational fields in Section 10.5. The audit must identify the reviewer, skill, concept or field, evidence location, and disposition. Remediate every gap without imposing cosmetic headings. The audit is complete only when every in-scope skill and script-owning skill has a recorded review and no anatomy or script-convention gap remains open.

### 10.8 Tests

Extend `tests/test_validate_skills.py` with focused cases for:

- invalid directory name;
- invalid frontmatter name;
- description over 1,024 characters;
- a body over 500 lines producing a warning without failure;
- a valid boundary case at exactly 1,024 characters.
- a cross-skill asset URI failing while an owning-skill asset URI and a bare adjacent-owner reference pass.

Keep the tests fixture-based and deterministic.

## 11. Workstream F: Description-Density Experiment

### 11.1 Problem

All skill descriptions are injected into routing context. Several are large, but current measurements are characters rather than actual input tokens or latency. Broad shortening can erase the exclusions that make routing accurate.

### 11.2 Measurement tool

Add `evals/catalog_probe.py` before collecting the first cost baseline. It must use the same OMP RPC path as live routing rather than a reconstructed prompt.

The probe accepts a baseline skill root, treatment skill root, model, profile, fixed prompt set, warm-up count, paired sample count, and output path. A normal comparison is runnable as:

```sh
python3 evals/catalog_probe.py \
  --baseline-root ../skills-baseline \
  --treatment-root . \
  --model "$MODEL" \
  --profile "$PROFILE" \
  --warmups 3 \
  --samples 15 \
  --output evals/results/catalog-probe/comparison.json
```

For token attribution, the probe sends a matched no-skill control through the same RPC path and verifies that the non-catalog request payload hash is identical. `catalog_input_tokens` is the OMP-reported full-request input tokens minus the matched control. If OMP cannot expose input usage or remove only the catalog block, record the metric as unavailable and do not make a token-reduction claim.

The output schema records:

- exact serialized baseline and treatment catalogs, SHA-256 hashes, and byte counts;
- model, profile, tool configuration, fixed prompt ID, request payload hash, and run order;
- OMP-reported total input tokens, control input tokens, and derived catalog input tokens;
- elapsed milliseconds per warm-up and measured request;
- sample count, paired median latency delta, and a seeded 95% bootstrap confidence interval;
- repository revisions and the probe revision.

Alternate AB and BA order after three warm-ups and collect at least 15 measured pairs per prompt. A latency claim requires the paired 95% confidence interval to exclude zero; a smaller raw median alone is noise, not evidence.

Add focused tests for catalog serialization, matched-control rejection, usage-unavailable behavior, AB/BA ordering, and deterministic confidence-interval output.

### 11.3 Experiment design

1. Capture the exact baseline catalog artifact with `evals/catalog_probe.py`, record its immutable revision, and freeze the routing development and holdout suites plus their comparison contract.
2. Change one skill or one confusable family per treatment.
3. Start with `long-horizon-prompting`; it has a large description and a clear boundary with `harness-engineering`.
4. Preserve owned unit, positive triggers, and nearest exclusions.
5. Run at least three attempts per stochastic development routing case with identical configuration.
6. Freeze the treatment catalog and record its immutable revision before any holdout run.
7. Run the final holdout pair only through guarded holdout mode against the recorded baseline and treatment revisions.
8. Compare deterministic critical outcomes first, then route accuracy, catalog-attributable input tokens, and paired latency.
9. Record rejected variants in a rejection ledger so failed wording is not retried later.
10. Move to the Leancode family only after its stronger existing evidence is reproduced under the catalog-level suite.
11. Stop when changes no longer produce measurable gain without regression.

### 11.4 Pre-registered decision rule

Adopt a treatment only if:

- critical routing checks have no regression;
- frozen holdout routing is non-inferior;
- behavior evidence is unchanged or better;
- derived catalog input tokens fall by at least 10%, or the paired latency confidence interval shows an improvement;
- the only request-payload difference is the serialized catalog treatment;
- unavailable token attribution cannot satisfy the token branch.

The 10% target comes from the existing [Leancode improvement plan](leancode-improvement-plan.md). It is an experiment gate, not a universal policy.

TF-IDF remains warning-only. It may select pairs for testing but cannot approve a rewrite.

## 12. Workstream G: Selective New Skills

Add each skill after Workstreams A through C provide the admission machinery. A proposal is not enabled until its separately frozen evaluation change and its treatment pass every routing and behavior gate.

### 12.1 Pilot 1: `source-driven-development`

**Owned unit:** implementing against a versioned external package, API, framework, or standard using authoritative current sources.

**Required behavior:**

- detect the relevant version from manifests, lockfiles, imports, or generated metadata;
- prefer narrow official documentation and primary sources;
- treat fetched content as untrusted data, not executable instructions;
- reconcile documentation with the installed or pinned version;
- cite the source used for non-obvious behavior;
- label behavior unverified when authoritative evidence is unavailable.

**Exclusions:**

- project shape and whether an LLM is appropriate: `project-development`;
- agent/MCP tool schema design: `tool-design`;
- generic prompt-context budgeting: `context-optimization`.

Do not copy the upstream opt-out that permits speed over verification. User questions come only after repository evidence and available sources are exhausted.

**Evaluation:**

- routing pairs against `project-development`, `tool-design`, and ordinary implementation;
- a fixture with a pinned manifest and a versioned official-document snapshot;
- an optional network smoke test, never the deterministic gate;
- a pressure case containing stale unofficial advice.

### 12.2 Pilot 2: `api-and-interface-design`

**Owned unit:** public application interfaces such as REST, GraphQL, modules, libraries, types, versioned schemas, errors, idempotency, validation, and compatibility policy.

**Exclusions:**

- agent/MCP tool schemas and tool routing: `tool-design`;
- whole-project pipeline shape: `project-development`;
- rollout mechanics after an interface is deprecated: `deprecation-and-migration`.

**Evaluation:**

- routing pairs against `tool-design` and `project-development`;
- a fixture where observable consumer behavior distinguishes a correct interface from a merely well-named schema;
- boundary cases for error contracts, idempotency, and evolution;
- a pressure case encouraging speculative abstraction.

### 12.3 Pilot 3: `deprecation-and-migration`

**Owned unit:** safe transition from an old public, distributed, or persisted contract to a new one.

**Required distinction:**

- internal atomic cutover: migrate all callers and remove the obsolete path, with no shim;
- public or rolling compatibility: explicit compatibility window, usage evidence, staged removal, and rollback;
- database change: expand, backfill, verify, cut over, then contract.

**Exclusions:**

- direct simplification without a compatibility boundary: `leancode`;
- project-level architecture selection: `project-development`;
- designing the replacement interface itself: `api-and-interface-design`.

**Evaluation:**

- one internal clean-cutover fixture where a compatibility alias is a critical failure;
- one rolling-production fixture where immediate removal is a critical failure;
- routing pairs against `leancode` and `project-development`.

### 12.4 Admission package for each pilot

Each pilot uses two independently revertible, separately reviewed changes:

1. **Frozen evaluation proposal:** add pilot-specific development and holdout routing and behavior files, required fixtures, and evaluator or rubric logic under non-active `proposal` status. Review and freeze this change before the skill treatment; it is excluded from active coverage and normal suite runs and may reference the single proposed root while that root is absent. After the freeze, run only its development proposal-baseline comparisons against the entry's pinned pre-treatment catalog revision.
2. **Skill treatment:** add `<skill>/SKILL.md`, only the needed skill-local references, the README inventory entry, attribution with immutable upstream revision and source path, applicable upstream license text, and frontmatter `metadata` for source, revision, adaptation type, and license notice. Canonicalize only the frozen development files and use their comparisons for iteration without changing cases, fixtures, evaluators, or rubrics; keep holdout files under `proposal`. Then freeze the treatment content and comparison configuration, record the immutable `treatment_catalog_revision`, and set the manifest's sole `admission_candidate` to that root and revision. Deterministic validation now permits the candidate's canonical development coverage plus its frozen, revision-pinned proposal holdout files without exposing holdout. Run the final development treatment against the pinned revision, then run the holdout pair only through guarded holdout mode against the proposal's isolated manifest-pinned roots. If the comparison passes, canonicalize the holdout files and clear `admission_candidate` in the same transition; full canonical coverage is mandatory thereafter and at release. Holdout output must not be exposed before the freeze; changing the treatment afterward invalidates the pair.

Every required baseline attempt must be complete and reproducible. A missing or infrastructure-failed baseline attempt makes the comparison `INCONCLUSIVE`; task or critical-check failures from completed baselines remain paired comparison evidence. Admission requires zero critical failures on every required treatment routing and behavior attempt in both development and holdout, in addition to the registered non-inferiority, provenance, portability, and cost gates; an aggregate score cannot offset a treatment critical failure.

Use the upstream material as adapted source, not as authority over this repository's runtime contract.

## 13. Workstream H: Conditional Gap Investigations

### 13.1 Agent security boundaries

First audit `hosted-agents`, `harness-engineering`, and `tool-design` behavior cases. Add a new skill only if the audit shows repeated failures that those owners cannot express cleanly.

If admitted, scope it narrowly to agent-specific boundaries:

- prompt and indirect prompt injection;
- tool authorization and least privilege;
- credential exposure;
- sandbox and filesystem boundaries;
- destructive action approval;
- untrusted model output crossing into executable operations.

Do not import a broad web-security monolith. General application security remains outside this skill set unless separately justified.

### 13.2 Debugging

Create a six-case baseline before proposing a skill:

1. user-reported failure is ground truth even when local reproduction differs;
2. intermittent race or timing failure;
3. malicious instructions embedded in an error or log;
4. root cause versus symptom suppression;
5. unreproducible issue with bounded evidence collection;
6. regression guard after the fix.

Run three attempts per case. Add a debugging skill only if the same critical failure occurs in at least two of three attempts and a treatment skill fixes it without routing or behavior regression. Otherwise retain debugging as harness-level engineering behavior.

### 13.3 Observability

No immediate skill. Reconsider only after at least three distinct real tasks, or one production incident, are blocked by missing telemetry guidance. The evidence must identify a unit of work not already owned by `harness-engineering`, `hosted-agents`, or project-specific engineering instructions.

### 13.4 Performance and remaining lifecycle gaps

Track routing misses, evaluator failures, user corrections, and post-task review findings. Add a performance or lifecycle skill only when the evidence shows:

- a recurring task class;
- a stable reusable workflow;
- a distinct nearest-neighbor boundary;
- material failure without specialized guidance;
- benefit that exceeds catalog-token and routing-collision cost.

## 14. Upstream Catalog Disposition

This table prevents repeated debate and silent scope expansion.

| Upstream area | Decision | Local owner or condition |
|---|---|---|
| context engineering family | Retain local adaptations | 17 existing context skills |
| code simplification | Retain local specialization | Leancode family |
| skill router / `using-agent-skills` | Reject | OMP native routing already owns discovery |
| source-driven development | Pilot | Workstream G |
| API and interface design | Pilot | Workstream G |
| deprecation and migration | Pilot | Workstream G |
| security | Conditional narrow audit | Workstream H |
| observability | Demand-gated | Workstream H |
| debugging | Failure-gated | Workstream H |
| performance | Demand-gated | Workstream H |
| idea, interview, specification, constraints, planning | Do not import now | harness and `project-development` cover current need |
| incremental development and TDD commands | Do not import as policy | verification remains change-specific and runtime-first |
| browser testing | Do not import | harness browser capability owns execution |
| generic code review | Do not import | reviewer agents and task-specific review skills own it |
| frontend UI design | Do not import without product demand | no current repository evidence |
| Git, CI/CD, documentation, ADR, and shipping commands | Do not import | repository and harness workflows own these tasks |
| doubt-driven development | Do not import as standalone skill | evidence-first reasoning is a global engineering rule |

A skipped upstream skill can be reconsidered through the same demand and admission gates. It is not permanently forbidden.

## 15. Workstream I: Architecture and Portability Boundaries

### 15.1 Rejected runtime architecture

Do not add an always-on `using-agent-skills` skill or session hook. Upstream issue [#569](https://github.com/addyosmani/agent-skills/issues/569) shows the duplication risk when a host already provides native routing. A second router adds tokens, conflicting instructions, and a new failure surface without owning a distinct task.

### 15.2 Reference portability

Keep references local to each skill. Upstream issue [#361](https://github.com/addyosmani/agent-skills/issues/361) demonstrates that root-shared references break independent skill installation. Duplication is acceptable when it preserves an install boundary; shared source should exist only when packaging materializes each complete skill.

The current repository has six cross-skill asset links from `evaluation`, `multi-agent-patterns`, and `tool-design` into `project-development/references/case-studies.md`. Migrate those links under Workstream E and fail future cross-skill asset URIs in validation. Preserve each evidence claim's original source and date. Bare references that route a reader to an adjacent skill remain valid.

### 15.3 Multi-host packaging

Do not hand-copy commands or wrappers. Upstream issue [#445](https://github.com/addyosmani/agent-skills/issues/445) shows that syntactically valid integrations may still be undiscoverable in a host.

If multi-host distribution becomes a product goal:

1. write a decision record naming supported hosts, owner, and support horizon;
2. keep one canonical skill source;
3. generate host adapters;
4. validate generated parity;
5. run installation and discovery smoke tests in every supported host;
6. publish compatibility and version policy;
7. treat adapter failures as release blockers.

This is a separate project, not part of the skill-quality work above.

## 16. Implementation Sequence

Keep evaluator changes separate from measured skill changes so the target cannot move during comparison.

### Change 0: Freeze baseline

- add and test `evals/catalog_probe.py`;
- record repository revision, 25-skill inventory, serialized catalog, attributable input tokens when available, paired routing latency, active evaluation commands, and current result URIs;
- copy no Git-ignored raw data into source control;
- identify the durable artifact owner and storage decision deadline.

**Exit:** the baseline manifest and catalog probe artifact are reproducible and immutable; unavailable token attribution is explicit.

### Change 1: Evaluation manifest and validator

- add `evals/suites.json`;
- register the complete comparison contract for each execution-selectable routing and behavior suite, including immutable baseline and treatment catalog revisions for every holdout comparison;
- record the immutable `base_catalog_revision`, the nullable single-root `admission_candidate`, and each proposal's actual pre-treatment `baseline_catalog_revision` and later frozen `treatment_catalog_revision`;
- require a candidate's canonical development coverage and matching revision-pinned proposal holdout entries, then full canonical coverage when the state is cleared or release is selected;
- retain immutable evaluated-catalog pins when entries become historical;
- classify all 25 JSONL files;
- add `evals/validate.py` and focused tests;
- update CI and the evaluation guide.

**Exit:** every case file is classified exactly once, pinned catalog revisions resolve deterministically, a valid frozen admission candidate passes without adding proposal holdout to active coverage, historical entries retain their evaluated roots, and existing active-validation data validates.

### Change 2: Safe suite selection

- add lifecycle- and split-aware `--suite`, `--mode`, `--allow-historical`, `--historical-catalog`, `--proposal-baseline`, and guarded holdout behavior to the runner;
- make normal `--suite` and low-level `--cases` development-only, rejecting every holdout outside `--mode holdout`;
- make the holdout guard verify locked comparison configuration and immutable baseline/treatment revisions, evaluate only their isolated roots, and serve proposal, canonical, independent-holdout, release-only, and permitted historical selections;
- make historical development execution require an explicit retained baseline or treatment pin, resolve it to an isolated root, and fail on a missing or unresolvable pin instead of using the working tree;
- route independent-holdout and release holdout selection through that guard rather than around it;
- record every evaluated revision and root, manifest and case hashes, comparison metadata, and effective timeouts in result metadata;
- add runner regressions for early canonical-holdout rejection through both `--suite` and `--cases`, guarded success, independent-holdout/release delegation, and historical baseline/treatment root selection without working-tree fallback.

**Exit:** normal and low-level runs cannot expose holdout data; every holdout execution uses the locked contract and recorded immutable baseline and treatment roots; frozen proposal development data runs only as a pinned, non-covering baseline; historical development runs only against the explicitly selected retained archived root.

### Change 3: Four routing gaps

- add development and holdout pairs for the four missing skills;
- run canonical routing baseline and treatment comparisons.

**Exit:** canonical development-and-holdout routing coverage is 25 of 25.

### Change 4: Anatomy, portability, and objective validation

- add contributor and anatomy guides;
- audit all 25 existing skills against the anatomy contract and every script-owning skill against the script convention;
- remediate every recorded semantic gap;
- migrate the six cross-skill asset links into owning skill-local evidence;
- update README links;
- add kebab-case, 1,024-character, cross-skill asset, and 500-line warning checks;
- add focused validator tests.

**Exit:** objective rules pass, every audit row has a disposition, no anatomy or script-convention gap remains open, each current skill is independently installable, and semantic rules remain explicitly review-based.

### Changes 5–7: Behavior waves

- one change per wave in Workstream C;
- freeze each wave's holdout, baseline revision, treatment revision, and comparison configuration before running its holdout through the guard;
- publish results and evidence status.

**Exit:** every existing skill is either behavior-verified or explicitly marked routing-only by generated evidence.

### Change 8: Release-evidence remediation

- complete human calibration and technical attestation;
- publish immutable artifacts;
- regenerate the Simplified Engineering English release report.

**Exit:** the regenerated report is `GO`, or complete evidence identifies a substantive failed gate as `NO-GO`; missing required evidence is `INCONCLUSIVE` and does not complete this change.

### Change 9: Description experiment

- test `long-horizon-prompting` first;
- proceed family by family only after freezing and recording each baseline/treatment pair and running holdout through the guard;
- maintain rejected-variant ledger.

**Exit:** adopted reductions have measured benefit and no frozen-holdout regression.

### Changes 10a–12b: New-skill pilots

1. `source-driven-development`;
2. `api-and-interface-design`;
3. `deprecation-and-migration`.

For each pilot, change `a` freezes the non-active development and holdout evaluation proposal and runs only its pinned development baseline. Change `b` canonicalizes only the development files for treatment iteration, freezes the treatment content and configuration, records `treatment_catalog_revision`, and declares that one root as `admission_candidate`. This candidate state permits deterministic validation with canonical development coverage and frozen, matching revision-pinned proposal holdout files. Change `b` then runs the final development treatment and invokes guarded holdout mode for the paired baseline and treatment against the manifest-pinned immutable roots. The holdout files remain `proposal` until that pair passes; passing canonicalizes them and clears the candidate state atomically, without modifying the frozen cases, fixtures, evaluators, or rubrics. Rejection clears the state, removes the root, and archives the files with their pins. Holdout results remain unobserved until treatment freeze. Each change is separately reviewed and independently revertible.

**Exit:** each skill is enabled only after every required baseline attempt is complete and reproducible, every required treatment attempt has zero critical failures, and the routing, behavior, registered non-inferiority, cost, provenance, and portability gates pass. A pending candidate may pass deterministic validation only under the narrow manifest exception, but cannot pass release until its state is cleared and full canonical coverage exists. Missing or infrastructure-failed attempts are `INCONCLUSIVE`.

### Change 13: Conditional decisions

- run security audit and debugging baseline;
- review observability and performance demand evidence;
- record an explicit add, defer, or reject decision for each.

**Exit:** no conditional skill is added on intuition alone.

## 17. File Change Map

| Path | Action | Required content | Verification |
|---|---|---|---|
| `evals/suites.json` | Add | exhaustive case-file lifecycle manifest, nullable single-root admission candidate, immutable baseline and treatment catalog revisions retained for historical reproduction, and suite-specific locked comparison contracts including timeout policy | evaluation validator tests |
| `evals/catalog_probe.py` | Add | OMP-native catalog capture, token attribution, and paired latency measurement | focused probe tests and a baseline run |
| `evals/validate.py` | Add | deterministic schema, path, ID-scope, skill, admission-candidate, historical-pin, proposal-revision, pairing, comparison-contract, split-aware selection, holdout-revision, and coverage checks | direct run and focused unit tests |
| `evals/run.py` | Update | development-only normal selectors, one guarded paired holdout executor over immutable roots, independent/release delegation, explicit retained-root historical development, pinned proposal-baseline execution, and complete result metadata | evaluation harness tests |
| `evals/README.md` | Update | statuses, admission-candidate and archived-pin fields, lifecycle matrix, development-only selectors, guarded holdout sequencing, explicit historical root selection, baseline critical semantics, and evidence policy | link and command review |
| `.github/workflows/validate-skills.yml` | Update | run skill and evaluation validators | workflow syntax and local commands |
| `tests/test_eval_validation.py` | Add | failure cases for all structural invariants, including invalid candidate state, candidate clearing or release without full coverage, absent historical or holdout revisions, and guard bypasses | unit-test discovery |
| `tests/test_evaluation_harness.py` | Update narrowly | normal `--suite` and low-level `--cases` early-holdout rejection, guarded paired execution, independent/release delegation, historical baseline/treatment root selection and failures, proposal development baseline behavior, and result metadata including immutable roots and timeouts | focused unit tests |
| `evals/cases/routing-development.jsonl` | Update | four development routing pairs | eval validator and live run |
| `evals/cases/routing-holdout.jsonl` | Update | four independent holdout pairs | eval validator and guarded frozen run |
| behavior case files | Update or add through manifest | wave-based development and holdout cases; all holdouts execute only through the guard after treatment freeze | deterministic checks and guarded live comparison |
| `CONTRIBUTING.md` | Add | authoring, provenance, evaluation, and review process | link validation |
| `docs/skill-anatomy.md` | Add | flexible anatomy and progressive disclosure | contributor review |
| all 25 existing skill directories | Audit; update only recorded gaps | anatomy conformance and script convention where applicable | recorded catalog-wide manual review |
| `README.md` | Update | contributor links, inventory, generated evidence status | skill validator |
| `evaluation/SKILL.md`, `multi-agent-patterns/SKILL.md`, `tool-design/SKILL.md` | Update | remove six cross-skill asset dependencies without losing cited evidence | skill validator and standalone-install review |
| `scripts/validate_skills.py` | Update | objective name, description, body-size, and cross-skill asset rules | validator tests |
| `tests/test_validate_skills.py` | Update | new hard-error, portability, and warning boundaries | focused unit tests |
| release reports and result manifests | Update | durable artifact links; immutable result manifests with evaluated baseline and treatment revisions and resolved roots, comparison-contract hashes, effective timeouts and equality, and completed gate inputs; release-report eligibility and rollback-invalidation dispositions | reproducibility review |
| each new skill directory | Add separately from its frozen evaluation proposal | complete skill, local references, metadata | admission gate |
| `ATTRIBUTION.md` | Update per pilot | pinned source path and revision | skill validator |
| upstream license file | Add only if needed | exact applicable license text | license review |

Do not create all future paths in one scaffold change. Add a path only when its implementation change is ready.

## 18. Verification and Release Gates

### 18.1 Deterministic repository checks

Run after each relevant change:

```sh
python3 scripts/validate_skills.py
python3 evals/validate.py
python3 -m unittest discover -s tests
python3 -m unittest discover -s context-compression/tests
bun test tests/leancode_hook.test.ts
```

A change may use narrower checks during development, but the release gate runs the complete list.

### 18.2 Live evaluation gates

Use the commands and locked configuration in the [evaluation guide](../evals/README.md). For every comparison:

- pin the model and profile;
- pin the tool set;
- use the same attempts and effective per-attempt and overall timeouts, record those values in each result manifest, and report their baseline/treatment equality;
- run deterministic grading before optional judges;
- preserve raw outputs;
- use development evidence only while the treatment remains editable; normal `--suite` and low-level `--cases` must reject every holdout during that period;
- freeze treatment content and comparison configuration and record immutable baseline and treatment catalog revisions before any holdout run;
- run every holdout pair through the guarded executor against only the resolved immutable baseline and treatment roots; independent-holdout and release modes must delegate to it, no holdout output may tune that treatment, and changing either root or the locked configuration invalidates the pair;
- use swapped-order judging where pairwise judges are involved;
- use the frozen suite-specific comparison contract without post-run rule changes;
- report each baseline and treatment critical failure, not only aggregate score; expected failures in a completed baseline remain comparison evidence rather than failing the treatment-only zero-critical gate.

### 18.3 Catalog release gate

A catalog release passes only when:

- all enabled skills have canonical development and holdout routing coverage;
- `admission_candidate` is `null`, and every formerly pending root has full canonical development and holdout coverage;
- every JSONL file is classified exactly once;
- IDs in the global active-ID scope are unique;
- repository and evaluation validation pass;
- each new or materially changed skill has behavior evidence;
- every required pilot baseline attempt is complete and reproducible; a missing or infrastructure-failed attempt makes the comparison `INCONCLUSIVE`;
- every admitted pilot has zero critical failures on every required treatment routing and behavior attempt;
- no critical deterministic regression exists;
- holdout performance from guarded execution against the recorded immutable baseline and treatment roots is non-inferior under the frozen suite-specific comparison contract;
- no release decision relies on a result whose baseline or treatment root contains a rolled-back skill; affected routing, behavior, and cost gates have been rerun on the current catalog;
- result artifacts are durable and hash-addressed;
- provenance, license, references, and README inventory are complete;
- token and latency effects are measured for catalog-description or skill additions;
- no skill contains a cross-skill asset URI;
- no always-on router, root-shared reference, or hand-copied host adapter has been introduced.

## 19. Rollback and Change Control

- preserve every baseline, treatment, and historical result manifest, including pinned proposal-baseline evidence;
- when an admitted skill is rolled back, preserve its evidence as historical but mark every later result whose baseline or treatment root contained that skill ineligible for release, including results for dependent pilots;
- before release, rerun every affected routing, behavior, and cost gate against the current catalog; new current-catalog evidence restores eligibility, not reuse or rewriting of the historical result;
- never rewrite a historical case file to make a new treatment pass;
- review and freeze evaluator changes in a non-active proposal change before the skill treatment that uses them;
- revert a skill and its local references, inventory row, attribution, and generated status together;
- if a new skill fails admission, clear `admission_candidate` and remove the root from the enabled catalog rather than leaving an alias or compatibility shim;
- keep pilot-specific development and holdout files immutable, reclassify them as historical, retain their immutable `baseline_catalog_revision` and `treatment_catalog_revision` pins when present, and register the removed name in `retired_skills`;
- never leave a removed target in a shared canonical case file;
- restore a description treatment immediately when a critical routing or behavior regression appears;
- do not average away a failing holdout with stronger development results;
- rerun only the affected comparison after infrastructure failure; until the required attempt completes, the comparison is `INCONCLUSIVE`, and poor model outcomes may not be selectively rerun without applying the same policy to baseline and treatment.

## 20. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Metric gaming | Make normal and low-level selection development-only; freeze holdouts, evaluators, treatment content, and comparison configuration before the sole guarded holdout path can expose results. |
| Evaluation contamination | Reject every holdout selected through normal `--suite` or `--cases`; require the guard to resolve and evaluate only recorded immutable baseline and treatment roots, and route independent-holdout and release selections through that same guard. Proposal pilots may reuse manifest pins; every other treatment must register equivalent revisions. |
| Description overcompression | Preserve owned unit and exclusions; require live routing non-inferiority. |
| New routing collisions | Add nearest-neighbor positive and negative pairs before enabling a skill. |
| Prompt-cost growth | Measure serialized input tokens and latency for every addition. |
| Judge position bias | Swap order, report sensitivity, and require human adjudication for critical cases. |
| Model drift | Record exact model/profile and compare only like-for-like runs. |
| Stale external documentation | Pin fixture snapshots and detected package versions; use network checks only as optional smoke tests. |
| License drift | Pin source revisions and validate notices and license files. |
| Broken standalone installs | Keep references local and test skill directory completeness. |
| Manual-review bottleneck | Assign named owners and deadlines before declaring a release candidate. |
| Lost raw evidence | Require immutable external URI, hash, retention, and access policy. |
| Historical data used against the wrong catalog | Require manifest status, explicit historical override and baseline/treatment selector, a retained immutable pin, isolated-root resolution, and failure without working-tree fallback. |
| Admission validation deadlock or premature release | Permit exactly one manifest-declared candidate with canonical development and frozen revision-pinned proposal holdout files; require the state to be cleared and full canonical coverage before release. |
| Stale evidence after rollback | Preserve affected results as historical, mark every result whose baseline or treatment root contained the removed skill ineligible for release, and rerun affected routing, behavior, and cost gates on the current catalog. |
| Multi-host scope creep | Treat adapters as a separate product with generated parity and install smoke tests. |
| Validator false confidence | Limit hard checks to objective syntax and inventory; use live evaluation for semantics. |
| Whole-catalog rewrite risk | Change one family or skill at a time with independent rollback. |

## 21. Source Material and Decisions

Pinned upstream sources used for this plan:

- [Repository README](https://github.com/addyosmani/agent-skills/blob/be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39/README.md)
- [Skill anatomy](https://github.com/addyosmani/agent-skills/blob/be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39/docs/skill-anatomy.md)
- [Evaluation guide](https://github.com/addyosmani/agent-skills/blob/be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39/evals/README.md)
- [Contributor guide](https://github.com/addyosmani/agent-skills/blob/be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39/CONTRIBUTING.md)
- [Evaluation runner](https://github.com/addyosmani/agent-skills/blob/be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39/scripts/run-evals.js)
- [`using-agent-skills`](https://github.com/addyosmani/agent-skills/blob/be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39/skills/using-agent-skills/SKILL.md)
- [`build` command](https://github.com/addyosmani/agent-skills/blob/be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39/commands/build.toml)
- [`source-driven-development`](https://github.com/addyosmani/agent-skills/blob/be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39/skills/source-driven-development/SKILL.md)
- [`api-and-interface-design`](https://github.com/addyosmani/agent-skills/blob/be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39/skills/api-and-interface-design/SKILL.md)
- [`deprecation-and-migration`](https://github.com/addyosmani/agent-skills/blob/be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39/skills/deprecation-and-migration/SKILL.md)
- [Routing vocabulary issue #351](https://github.com/addyosmani/agent-skills/issues/351)
- [Shared-reference portability issue #361](https://github.com/addyosmani/agent-skills/issues/361)
- [Host discovery issue #445](https://github.com/addyosmani/agent-skills/issues/445)
- [Always-on router duplication issue #569](https://github.com/addyosmani/agent-skills/issues/569)

Local evidence and prior plans:

- [Leancode improvement plan](leancode-improvement-plan.md)
- [Simplified Engineering English improvement plan](simplified-engineering-english-improvement-plan.md)
- [Simplified Engineering English release report](../evals/results/see-improvement/release-report.md)
- [Evaluation guide](../evals/README.md)
- [Repository README](../README.md)

## 22. Definition of Done

The improvement program is done when all of the following are true:

- [ ] every final holdout result evaluates and records immutable baseline and treatment catalog revisions and resolved roots under a locked comparison configuration;
- [ ] all evaluation case files are machine-classified; normal `--suite`, low-level `--cases`, and proposal-baseline execution are development-only; every holdout lifecycle status, including independent and release selection, reaches the same guard only after treatment freeze;
- [ ] evaluation structure, coverage, split-aware selection, immutable holdout roots, guarded-execution delegation, the single-root admission-candidate exception, historical archived-root selection, and suite-specific comparison-contract validation run in CI, with regressions for early holdout rejection, invalid candidate transitions, release without full canonical coverage, and missing or unresolvable historical pins;
- [ ] canonical routing coverage is 25 of 25 for the existing catalog;
- [ ] all existing skills have generated `verified`, `routing-only`, or `unverified` evidence status;
- [ ] contributor and skill-anatomy guidance are published and linked;
- [ ] all 25 existing skills and every script-owning skill have a recorded manual anatomy/script audit, and every identified gap is remediated;
- [ ] objective validator additions and focused tests pass;
- [ ] Simplified Engineering English human calibration, technical attestation, critical adjudication, and durable storage evidence are complete, and its decision is `GO` under the evidence policy;
- [ ] every adopted description change has measured token or latency benefit and frozen-holdout non-inferiority under its pre-registered suite contract;
- [ ] each admitted pilot skill has a separately reviewed and frozen evaluation proposal, complete and reproducible baseline attempts, complete provenance, local references, routing evidence, behavior evidence, zero critical failures on every required treatment attempt, cost measurement, an independent rollback, a cleared admission-candidate state, and full canonical development and holdout coverage;
- [ ] no skill depends on another skill's asset files;
- [ ] rejected-pilot evidence remains immutable and validator-clean through historical status, retained immutable evaluated-catalog pins, and a retired identity; historical development runs resolve only an explicitly selected archived root and never the working tree; every result whose baseline or treatment root contained the removed skill remains release-ineligible; and affected routing, behavior, and cost gates pass on new current-catalog evidence;
- [ ] security, debugging, observability, and performance each have a recorded evidence-based add, defer, or reject decision;
- [ ] no rejected runtime architecture was introduced;
- [ ] all deterministic repository checks and required live release gates pass;
- [ ] release reports link to durable, immutable evidence and contain no unsupported efficacy claims.
