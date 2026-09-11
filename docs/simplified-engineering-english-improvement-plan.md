# Simplified Engineering English Improvement Plan

## 1. Purpose

Improve `simplified-engineering-english` without changing technical meaning, obligation force, security properties, or user-visible facts during a rewrite.

The work must answer four questions:

1. Does the skill preserve facts, conditions, qualifiers, numbers, units, versions, identifiers, and obligation force?
2. Does the skill reduce consequential ambiguity and improve actionability across its supported artifact types?
3. Which rules should be hard requirements, review warnings, strict-profile controls, or project-specific choices?
4. Which conformance claims can the repository support with deterministic checks, semantic review, and retained evaluation evidence?

Do not change the production skill until a valid baseline exists. Current repository evidence covers skill routing only. It does not establish that the skill improves prose or preserves technical contracts.

## 2. Decision Summary

Use a preservation-first revision rather than adding more rules.

The target design has:

- one explicit technical-preservation invariant;
- one rule-precedence order;
- a small set of rules that apply to every supported artifact;
- a strict controlled-language profile for safety, regulatory, maintenance, and translation-sensitive work;
- an engineering-default profile for ordinary software documentation;
- compact artifact cards for procedures, requirements, explanations and references, errors, incidents, and diagnostic records;
- rule-level source and adaptation labels;
- enforcement claims limited to the checks that actually run;
- paired baseline and treatment evaluations with separate technical-fidelity, ambiguity, actionability, readability, and compliance results.

Do not treat a difference from Google, Microsoft, or another style guide as proof that an SEE rule is wrong. Those guides provide context and alternatives. Retain a strict rule when its selected profile requires it and evaluation supports it.

## 3. Current State

### 3.1 Components

| Component | Path | Current role |
| --- | --- | --- |
| Main skill | `simplified-engineering-english/SKILL.md` | Defines activation, 82 rules, artifact modes, conformance levels, enforcement guidance, and governance. |
| Dictionary | `simplified-engineering-english/references/dictionary.md` | Defines confusable terms, rewrite pairs, part-of-speech locks, procedural verbs, glossary policy, and exemptions. |
| Development routing cases | `evals/cases/routing-development.jsonl` | Contains one positive SEE routing case and one nearby negative case against `leancode`. |
| Holdout routing cases | `evals/cases/routing-holdout.jsonl` | Contains one positive SEE routing case and one nearby negative case against `leancode`. |
| Evaluation runner | `evals/run.py` | Captures real OMP baseline and treatment runs. |
| Evaluation grader | `evals/grade.py` | Applies deterministic grading, paired gates, token accounting, and optional blinded judgment. |
| Evaluation guide | `evals/README.md` | Defines immutable run artifacts, baseline and treatment parity, holdout discipline, and efficacy-claim requirements. |
| Repository validator | `scripts/validate_skills.py` | Validates skill structure and repository contracts. |

### 3.2 Confirmed High-Risk Defects

#### No preservation-first invariant

Protected spans cover some literal text, but no rule requires preservation of all source meaning before stylistic revision. A rewrite can alter:

- a fact;
- an actor;
- a condition or exception;
- a number or unit;
- a version range;
- obligation force;
- uncertainty or epistemic status;
- causal status;
- a security boundary.

This omission is critical because a fluent rewrite can satisfy surface rules while changing a technical contract.

#### Direct internal conflicts

| Location | Conflict | Required correction |
| --- | --- | --- |
| Rule 8.6 and its example | The rule prohibits internal paths. The example includes `/etc/app.yaml`. | Distinguish actionable local paths from sensitive server paths and secret-bearing values. |
| Rule 9.1 and dictionary rewrite pairs | Rule 9.1 prohibits `now`. The dictionary replaces “at this point in time” with `now`. | Prefer a version, date, or deletion when time scope matters. Permit ordinary `now` only outside version-sensitive claims. |
| Dictionary definition of `stale` | The definition uses the prohibited word `now`. | Define the term without violating the time-reference rule. |
| Dictionary part-of-speech rule for `default` | The table excludes verb use and then permits “defaults to.” | Record the permitted intransitive verb sense or prohibit it consistently. |
| Dictionary part-of-speech rule for `surface` | The table prohibits verb use. An earlier explanation says an error may “surface.” | Use an approved verb or permit the intended sense consistently. |
| Core-principle and section-origin claims | The skill says Sections 7 through 9 have no STE equivalent. Section 8 calls itself an analogue of STE warnings and cautions. | Describe obligations and evidence as additions, and risk and writing mechanisms as adaptations. |

#### Source and adaptation boundaries are unclear

The skill combines:

- official ASD-STE100 rules;
- BCP 14 keyword semantics;
- EARS syntax;
- ISO plain-language principles;
- general developer style guidance;
- local SEE policy.

The reader cannot reliably determine which source requires a rule, which rule is adapted, and which rule is an untested local recommendation.

#### Requirements guidance combines separate layers

Section 7 combines:

1. obligation force;
2. EARS clause order;
3. atomicity and verification;
4. rationale placement.

The current combination misstates parts of RFC 2119, RFC 8174, and EARS and treats one syntax as a complete requirements-quality system.

#### Machine-checkability is overstated

Level 1 is called fully machine-checkable, but it includes semantic tasks such as:

- selecting the correct word sense;
- resolving ambiguous pronouns;
- distinguishing an entity from a concept;
- enforcing part of speech in context;
- validating project glossary governance.

The current Vale mapping also assigns capabilities too broadly. `occurrence` counts a configured token. `conditional` relates regular-expression matches. Vale vocabularies enforce accepted and rejected expressions, spelling, and casing. These mechanisms do not establish semantic correctness.

### 3.3 Unverified Design Risks

Treat these statements as hypotheses until paired evaluations test them:

- Loading all 82 rules before selecting an artifact mode can reduce instruction salience.
- Fourteen artifact rows can create overlapping or inconsistent behavior.
- Hard sentence caps can improve strict controlled text but reduce clarity in ordinary explanatory text.
- Universal bans on passive voice, contractions, perfect constructions, and future tense can cause unnecessary or meaning-changing rewrites.
- A shorter `SKILL.md` with detailed rules in a reference file can reduce input cost without reducing quality.
- A language model can review semantic SEE rules reliably enough to support a release gate.

### 3.4 Strengths to Preserve

Keep these mechanisms unless evaluation finds a regression:

- one concept and one term within a defined context;
- protected identifiers, commands, paths, literal values, versions, and quoted output;
- conditions before consequential instructions;
- explicit actors when responsibility matters;
- one independently reviewable action or obligation per unit;
- prerequisites and observable results for procedures;
- risk information before the governed action;
- measured performance, reliability, security, and scale claims;
- separation of observations from hypotheses;
- human technical review after automated checks.

## 4. Success Criteria

A candidate revision can ship only when all of the following conditions are true:

1. Baseline and treatment runs use the same pinned model, profile, tools, reasoning settings, case inputs, and attempt count.
2. The candidate introduces zero critical changes to facts, conditions, qualifiers, numbers, units, versions, identifiers, commands, quotations, obligation force, or supported uncertainty.
3. The candidate does not invent an actor, cause, date, measurement, recovery action, exception, or requirement.
4. Every development and holdout case passes its deterministic preservation checks.
5. The candidate does not regress on already-compliant no-op cases.
6. The candidate reduces consequential ambiguity on both development and holdout cases.
7. Technical fidelity does not regress in any artifact family.
8. The strict profile enforces its declared controlled-language rules consistently.
9. The engineering-default profile does not enforce house-style choices as universal correctness rules.
10. Every claimed automated rule names the checker and exact rule ID that enforces it.
11. Every semantic rule names the required reviewer and evidence.
12. Routing coverage distinguishes SEE from adjacent prose, evaluation, implementation, and review skills.
13. Any increase in prompt tokens, output tokens, tool calls, questions, or latency has a recorded correctness benefit.
14. Repository validation and focused evaluation tests pass.
15. The retained evaluation artifacts satisfy the contracts in `evals/README.md`.

Do not set an aggregate quality threshold before baseline measurement. Record critical floors and per-dimension thresholds before the first treatment run.

## 5. Rule Authority and Precedence

### 5.1 Authority Categories

Every rule must use one category:

| Category | Meaning | Example |
| --- | --- | --- |
| `adopted` | The rule retains the source requirement within the source's declared scope. | BCP 14 uppercase keyword meaning in a document that declares BCP 14. |
| `adapted` | The rule changes the source mechanism for a software context. | Software-focused risk labels derived from STE safety instructions. |
| `SEE-policy` | The rule is a local controlled-language decision. | One obligation keyword per atomic normative statement. |
| `house-style` | The project can replace the rule without losing SEE semantics. | American English spelling or contraction policy. |
| `heuristic` | The rule identifies text for review and does not prove a defect. | Sentence length or possible passive voice outside the strict profile. |

### 5.2 Precedence

Apply rules in this order:

1. Safety, security, privacy, legal, and regulatory constraints.
2. Technical meaning, including facts, scope, conditions, qualifiers, units, versions, uncertainty, and obligation force.
3. Verbatim identifiers, commands, literal values, and required quotations, except when an authorized security rule requires redaction.
4. Authoritative language, protocol, platform, and product terminology.
5. The project glossary and artifact contract.
6. The selected SEE profile and artifact card.
7. General SEE defaults.
8. Concision and stylistic preference.

A lower-precedence rule must not alter a higher-precedence property.

### 5.3 Rule Record

Each retained or new rule must state:

- stable rule ID;
- concise rule text;
- applicable profile and artifact card;
- severity: error, warning, or suggestion;
- enforcement class: deterministic, parser-assisted, semantic review, or technical review;
- source URL and source section when applicable;
- source relationship from Section 5.1;
- exceptions;
- compliant example;
- counterexample;
- rationale or measured failure class.

Store the full records in `simplified-engineering-english/references/rules.md`. Keep only the workflow, universal invariants, and profile-selection table in `SKILL.md`.

Do not create a separate machine-readable registry until an implemented checker needs one. If tooling needs structured rule data, make that data canonical and generate duplicate documentation from it rather than maintaining two manual copies.

## 6. Target Skill Structure

### 6.1 `SKILL.md`

Keep `simplified-engineering-english/SKILL.md` focused on execution:

1. Scope and non-scope.
2. Audience and artifact identification.
3. Technical-preservation invariant.
4. Rule precedence.
5. Base-profile selection.
6. Artifact-card selection.
7. Rewrite workflow.
8. Ambiguity and conflict handling.
9. Verification and reporting.
10. Links to detailed rules and dictionary guidance.

### 6.2 Detailed Rules

Create `simplified-engineering-english/references/rules.md` only after the baseline is frozen. Move detailed grammar, procedure, requirement, risk, time, and evidence rules into it.

Organize rules by the decision an agent must make, not by source-standard numbering alone:

- preserve meaning;
- choose terminology;
- identify actors, actions, conditions, and results;
- select obligation force;
- structure the artifact;
- state risk and recovery;
- scope time, version, and evidence;
- verify the result.

Retain source mappings so a reviewer can trace each rule back to ASD-STE100, BCP 14, EARS, ISO, another guide, or an SEE-specific decision.

### 6.3 Dictionary

Revise `simplified-engineering-english/references/dictionary.md` into three explicit groups:

1. Cross-domain distinctions with material engineering consequences.
2. Default software terms that authoritative ecosystem or project terminology can override.
3. Project glossary governance and checker integration.

The project glossary must override an SEE default when the project term is authoritative and unambiguous. A language, protocol, or platform specification overrides both.

### 6.4 Base Profiles

#### Strict controlled profile

Use for:

- safety-critical procedures;
- regulated documentation;
- aircraft or equipment maintenance material;
- translation-sensitive source text;
- projects that explicitly require STE-like constraints.

Candidate controls:

- maximum 20 words for procedural sentences;
- maximum 25 words for descriptive sentences;
- restricted voice and tense;
- no contractions;
- controlled multi-word nouns;
- controlled word counting;
- stricter approved vocabulary.

These controls are hard requirements only when this profile is selected.

#### Engineering-default profile

Use for:

- design documents;
- ADRs;
- PR descriptions;
- issues;
- ordinary developer documentation;
- code comments;
- explanatory API documentation.

This profile keeps semantic safeguards as errors. It treats voice, tense, sentence length, contractions, and similar style signals as warnings or project choices.

### 6.5 Artifact Cards

Use compact artifact cards rather than one independent rule system per artifact.

#### Procedure and runbook

Require:

- prerequisites;
- imperative steps;
- one consequential action per step;
- condition before action when acting early can cause an error;
- observable result when success is not self-evident;
- rollback or irreversibility information for state-changing, destructive, costly, security-sensitive, or availability-affecting work;
- risk information before the governed action.

Do not require rollback text for read-only or diagnostic procedures.

#### Requirement and contract

Require:

- declared obligation profile;
- one independently verifiable obligation per statement;
- explicit subject and response;
- conditions, thresholds, tolerances, units, and timing where applicable;
- an objective verification method;
- rationale outside the normative statement;
- a handoff to requirements governance for traceability, completeness, feasibility, assumptions, and unresolved values.

Use EARS when its temporal clauses fit the intended behavior. Do not force EARS onto every constraint, interface rule, or quality attribute.

#### Explanation and reference

Require:

- the reader's need and scope near the start;
- information in dependency order;
- stable terminology;
- a clear distinction between behavior, rationale, recommendation, and implementation detail;
- document- or section-level version scope;
- meaningful headings and links.

Use the Diátaxis user need to distinguish tutorial, how-to, reference, and explanation content. Do not infer sentence caps from Diátaxis.

#### Error, incident, and diagnostic record

Require:

- what failed or what was observed;
- a safe cause when the cause is known and suitable for the audience;
- a recovery action when one exists;
- the affected input or resource when disclosure is safe;
- separate user-facing and operator-facing detail;
- observation, report, inference, assumption, and unknown markers where evidence provenance matters;
- separation of timeline facts from causal hypotheses.

## 7. Correctness Changes

### 7.1 Technical Preservation

Add this invariant near the start of `SKILL.md`:

> A rewrite MUST preserve facts, conditions, qualifiers, numbers, units, versions, identifiers, commands, quotations, obligation force, uncertainty, and supported causal claims. If the source is ambiguous, identify the ambiguity instead of selecting an interpretation.

Add deterministic preservation fields to evaluation cases before changing any production text.

### 7.2 BCP 14

Correct the obligation section to state:

- BCP 14 applies when the artifact declares RFC 2119 and RFC 8174 semantics.
- Only uppercase forms have the special BCP 14 meanings.
- Lowercase forms retain normal English meaning.
- Normative text does not require a BCP 14 keyword merely because RFC 8174 exists.
- `NOT RECOMMENDED` belongs to the declared keyword set.
- `SHOULD` and `SHOULD NOT` permit justified deviation after the implications are understood and weighed.
- A sentence does not need an exhaustive exception condition to use `SHOULD` correctly.
- Exactly one keyword per atomic normative statement is an SEE policy, not an RFC requirement.

Let each requirements or protocol project choose one preferred absolute keyword. Do not switch between `MUST` and `SHALL` for stylistic variety.

### 7.3 EARS

Correct the EARS description:

- zero or more preconditions;
- zero or one trigger;
- one system name;
- one or more system responses;
- complex forms can include unwanted-behavior `If` and `Then` clauses;
- an optional feature is “included” unless the requirement intentionally describes runtime enablement.

If SEE retains one response per requirement, label that restriction as an atomicity policy layered on EARS.

### 7.4 Verification

Replace “name the test that would fail” with objective verification guidance:

- test;
- demonstration;
- inspection;
- analysis.

A requirement must provide or support measurable pass/fail evidence. Naming a test is neither necessary nor sufficient.

### 7.5 Risk and Error Messages

Separate three concerns:

1. The consequence and avoidance structure.
2. The project's severity taxonomy.
3. Information disclosure for the intended audience.

Keep this invariant:

1. Place risk information before the governed action.
2. State the consequence.
3. State the prevention or recovery action.
4. State the affected scope when consequential.

Permit project-specific labels. Identify the current WARNING, CAUTION, and NOTE model as an SEE software adaptation rather than an official STE severity mapping.

For errors:

- include an actionable local path when the user can inspect it safely;
- exclude server paths, stack traces, dependency details, secrets, and internal queries from unauthorized responses;
- log diagnostic detail in an authorized operator channel;
- provide a correction only when it is known and does not compromise security or the content's purpose.

### 7.6 Time, Version, and Evidence

Revise time and version rules:

- declare the applicable product and version at document or section level;
- qualify an individual claim only when its version differs from the surrounding scope;
- prohibit floating time references when they can become stale;
- permit ordinary time words when they describe an immediate procedure or observation unambiguously;
- permit future tense for a genuinely delayed or asynchronous result;
- continue to prohibit presenting an unshipped plan as current behavior.

Require evidence markers primarily in incidents, debugging records, investigations, research, and agent handoffs. Do not require a marker for every non-obvious sentence in a tutorial, ADR, or API reference.

A deprecation record should state:

- the deprecated item;
- the deprecation version;
- the replacement;
- the planned removal version, or an explicit statement that no removal version is scheduled;
- an owner or tracking reference when removal remains unresolved.

### 7.7 Revision and Release Scope

Replace “same commit” requirements with “same reviewed change set or coordinated release.” Some projects store code and documentation in separate repositories or publish them through separate pipelines.

Do not call every terminology change a breaking change. Classify it by consumer effect:

- editorial-only;
- search or discoverability impact;
- user-interface terminology change;
- API or schema change;
- migration-requiring breaking change.

## 8. Language Policy Changes to Evaluate

### 8.1 Hard Rule, Warning, or House Style

| Topic | Strict profile | Engineering-default profile |
| --- | --- | --- |
| Technical fact preservation | Error | Error |
| Protected-span preservation | Error | Error |
| Project terminology | Error | Error |
| Obligation-force preservation | Error | Error |
| Ambiguous consequential actor | Error | Error |
| Sentence cap | Error | Warning |
| Passive voice | Restricted | Warning when responsibility becomes unclear |
| Perfect or progressive tense | Restricted | Warning only when sequence or state becomes unclear |
| Contractions | Prohibited | Project or artifact choice |
| American English | Project choice | Project choice |
| Semicolon | Prohibited | Suggestion unless accessibility or parsing requires stricter treatment |
| Three-word multi-word noun | Error with declared exceptions | Warning |
| Evidence markers | Artifact-specific | Artifact-specific |

### 8.2 Voice

Use active voice when the actor or responsible party matters. Permit passive voice when:

- the actor is unknown;
- the actor is irrelevant;
- the actor is intentionally omitted for a valid reason;
- the affected object is the relevant subject.

Do not invent an actor to eliminate passive voice.

### 8.3 Sentence Length

Retain the ASD-STE100 20-word procedural and 25-word descriptive limits in the strict profile.

In the engineering-default profile:

- flag a long sentence for review;
- split it only when the split preserves logical relationships;
- do not trade a precise condition, exception, or qualifier for a lower word count.

Document the counting algorithm. The current protected-span convention is an SEE adaptation and requires custom tokenization if it remains part of conformance.

### 8.4 Contractions

Evaluate this profile split:

- strict or normative text: no contractions;
- conversational documentation and user-interface text: common contractions permitted;
- unusual or ambiguous contractions: prohibited.

### 8.5 Tense and Aspect

Prefer simple present for general behavior. Permit:

- simple past for completed events;
- future tense for actual delayed or asynchronous outcomes;
- perfect or progressive constructions when they preserve a material state or temporal relationship that a simple tense would lose.

Continue to reject dangling participles and unclear event ordering.

## 9. Dictionary Plan

### 9.1 Keep Material Distinctions

Retain strict distinctions when conflation can change engineering meaning:

- authentication and authorization;
- parameter and argument;
- fault, error, and failure;
- concurrency, parallelism, and asynchrony;
- deprecated and removed;
- release, deploy, rollout, rollback, and revert.

Add verb forms such as `authenticate` and `authorize` when the main rules use them.

### 9.2 Make Context-Dependent Terms Overridable

Mark these and similar entries as defaults rather than universal senses:

- module;
- package;
- library;
- framework;
- service;
- component;
- repository;
- API;
- endpoint;
- route;
- latency;
- response time;
- capacity;
- cache;
- record;
- entity.

Remove false absolutes. For example, a mean latency is a measurement claim, although it can be insufficient for a tail-latency decision. Require the statistic, workload, sample, interval, and measurement point that the decision needs.

### 9.3 Glossary Contract

Define these fields for a project term:

- `term`;
- `definition`;
- `part_of_speech`;
- `domain`;
- `source`;
- `approved_variants`;
- `rejected_alternatives`;
- `replacement` when deprecated;
- `status`;
- `owner`;
- `since`.

Do not claim that a Vale vocabulary enforces the definition or part of speech. Compile only accepted spellings, casing, and rejected alternatives into Vale data.

### 9.4 Exemption Precedence

Define exemptions explicitly:

1. Authorized security redaction can replace sensitive text.
2. Quoted external text remains verbatim unless the task requests a quotation edit.
3. Tool output and logs remain verbatim, with secrets redacted when authorized.
4. Code spans remain verbatim.
5. Product and protocol names remain verbatim.
6. Surrounding prose remains subject to the selected profile.

An exemption from rewriting does not make the exempt content technically correct or safe to publish.

## 10. Accessibility and Internationalization

Keep prose-facing controls inside SEE:

- descriptive headings;
- meaningful link text;
- text equivalents for meaningful images and diagrams;
- no meaning conveyed only by color, position, punctuation, or a symbol;
- simple tables with an introduced purpose;
- references to UI elements by accessible label rather than visual location;
- errors identified in text;
- declared document language where the format supports it;
- no idioms or locale-dependent examples in translation-sensitive content.

Route implementation controls to a companion accessibility or localization review:

- keyboard behavior;
- focus management;
- ARIA relationships;
- screen-reader runtime testing;
- right-to-left layout;
- text expansion;
- locale-sensitive formatting code;
- translatable-string concatenation.

Use the ISO 24495-1 outcomes as the top-level document check:

- relevant;
- findable;
- understandable;
- usable.

## 11. Enforcement Plan

### 11.1 Deterministic Lexical Checks

Suitable checks include:

- prohibited rewrite terms outside exempt scopes;
- approved product spelling and casing;
- rejected glossary alternatives;
- uppercase BCP 14 keywords in a declared BCP 14 profile;
- forbidden literal patterns;
- exact protected-span preservation between source and rewrite;
- required headings or labels in a structured artifact;
- sentence and paragraph counts under a documented tokenizer.

### 11.2 Parser-Assisted Structural Checks

Suitable checks include:

- warning placement before a destructive step;
- numbered sequential procedure steps;
- prerequisites before the first step;
- requirement IDs and rationale placement;
- artifact-specific required sections;
- code and quotation exemptions;
- document- or section-level version metadata.

Use Vale scopes when they express the rule correctly. Use the existing evaluation grader or a small project script when cross-block ordering or source-to-rewrite preservation is required.

### 11.3 Semantic Review

Require human or calibrated model review for:

- word sense;
- ambiguous reference;
- technical accuracy;
- appropriate actor omission;
- atomicity;
- EARS suitability;
- measurable verification;
- safe disclosure;
- completeness;
- preserved uncertainty and causal status.

A model review must return evidence before a verdict and must identify the source span that supports each finding.

### 11.4 Technical-Authority Review

A qualified technical reviewer remains responsible for:

- correctness;
- safety;
- security;
- completeness;
- feasible requirements;
- operational validity;
- product-specific terminology;
- approval to publish.

### 11.5 Coverage Declaration

Replace broad conformance levels with a generated or explicit coverage statement:

```text
Deterministic checks: SEE-TERM-01, SEE-SPAN-01, SEE-BCP14-01
Parser-assisted checks: SEE-PROC-02, SEE-RISK-03
Semantic review: SEE-REQ-04, SEE-EVID-02
Technical approval: required
```

Do not describe a document as SEE-conforming unless every applicable rule has an enforcement result and the required technical review is complete.

## 12. Evaluation Design

### 12.1 Freeze the Baseline

Before changing `SKILL.md` or `dictionary.md`:

1. Record the repository commit and skill hashes.
2. Pin the exact model snapshot.
3. Use an isolated profile with no unrelated MCP servers, hooks, rules, extensions, or sessions.
4. Record the reasoning settings and tool policy.
5. Freeze development and holdout cases.
6. Run at least three attempts per stochastic case.
7. Retain raw requests, responses, usage, runtime data, and grader evidence.
8. Do not reconstruct a baseline from a treatment run.

A comparison is invalid when baseline and treatment differ in model, prompt inputs, tools, profile, reasoning settings, timeout policy, case data, or grading logic.

### 12.2 Behavior Corpus

Create twelve initial transformation cases across four families.

#### Procedure and runbook

- Ordinary case: vague actors, mixed terminology, missing expected result.
- Adversarial case: destructive command, warning placement, protected command, and required negative prohibition.
- No-op case: an already precise read-only diagnostic procedure.

#### Requirement and API contract

- Ordinary case: vague performance and compound obligations.
- Adversarial case: valid `MUST NOT`, valid `SHOULD`, EARS-incompatible quality constraint, and multiple verification methods.
- No-op case: an atomic measurable requirement with correct BCP 14 force.

#### Explanation and ADR

- Ordinary case: mixed mechanism and rationale, floating version reference, and terminology drift.
- Adversarial case: legitimate passive voice, future asynchronous behavior, and a required qualification.
- No-op case: a concise version-scoped explanation.

#### Error and incident record

- Ordinary case: vague error with no affected input or next action.
- Adversarial case: actionable local path, sensitive server path, uncertain cause, quoted logs, and an inaccessible visual-only cue.
- No-op case: a safe error plus a fact-only incident timeline.

### 12.3 Routing Corpus

Add at least eight cases:

- four positive cases spanning distinct SEE artifacts;
- four negative cases that belong to adjacent skills.

Include comparisons with:

- `lossless-doc-compress` for information-preserving compression;
- `evaluation` for evaluation-system design;
- `tool-design` for tool-interface contracts;
- `leancode` for implementation minimality;
- `ml-system-design-review` for architecture-quality review;
- general code-review skills for source-code correctness.

A routing case must test the frontmatter description. It must not require the full skill to run.

### 12.4 Adversarial Coverage

The complete corpus must include:

- a `MUST NOT` security requirement;
- correct simultaneous use of authentication and authorization;
- correct simultaneous use of parameter and argument;
- quoted output containing `and/or`;
- a protected identifier such as `legacyFlag`;
- an actionable local path and a sensitive server path;
- an unknown deprecation-removal version;
- legitimate asynchronous future tense;
- passive voice with an unknown actor;
- a 20/21-word procedural boundary;
- a 25/26-word descriptive boundary;
- a warning before a destructive operation;
- correct use of fault, error, and failure;
- a mean latency and a tail-latency claim with distinct purposes;
- a requirement verified by analysis or inspection;
- an ambiguous source that the agent must report rather than silently resolve.

### 12.5 Case Manifest

Each case must record:

- artifact family;
- selected profile;
- source facts;
- protected spans;
- quoted spans;
- conditions and exceptions;
- numbers, units, versions, and status codes;
- expected obligation force;
- permitted rewrites;
- required structure;
- known ambiguity traps;
- prohibited inventions;
- deterministic checks;
- judge criteria when necessary.

### 12.6 Deterministic Gates

Fail a candidate on any of these outcomes:

- changed protected identifier, command, path, literal, or quotation without an authorized redaction rule;
- changed number, unit, version, status code, condition, exception, or obligation force;
- invented actor, fact, cause, date, measurement, recovery, or commitment;
- deleted material qualification or uncertainty;
- leaked secret or unauthorized internal detail;
- risk information placed after the destructive action;
- missing required artifact structure;
- changes to a no-op case without an identified defect.

### 12.7 Quality Dimensions

Score each dimension separately on a defined 0 through 4 rubric:

1. Technical fidelity.
2. Residual consequential ambiguity.
3. Actionability or objective verifiability.
4. Readability and scanability.
5. Selected-profile compliance.
6. Unnecessary-edit rate.
7. Source traceability of reviewer findings.

Do not allow an aggregate score to hide a technical-fidelity failure.

Set critical floors before treatment evaluation. Initial proposed floors are:

- technical fidelity: at least 3 in every case and no critical mutation;
- ambiguity: at least 3 for operational and normative artifacts;
- profile compliance: at least 3;
- readability: at least 2;
- protected-span preservation: exact unless authorized redaction applies.

Calibrate or replace these numeric floors from the frozen baseline before using them as a release claim.

### 12.8 Model and Human Judgment

Use deterministic grading first.

For residual semantic or preference judgments:

1. Use a judge model from a different model family when available.
2. Hide condition labels.
3. Compare baseline and treatment in both A/B orders.
4. Require evidence before the verdict.
5. Report position-sensitive disagreements.
6. Calibrate the rubric on a human-reviewed sample.
7. Route low-confidence and safety-sensitive results to a human reviewer.
8. Retain per-dimension results and confidence.

Human review must cover at least a representative sample from each artifact family and every candidate critical regression.

### 12.9 Cost and Attention Metrics

Record:

- skill input tokens;
- cache-read tokens;
- output tokens;
- total tokens;
- tool calls;
- questions;
- runtime;
- invalid or incomplete responses.

Treat reduced prompt cost from progressive disclosure as a hypothesis. A shorter prompt cannot ship when it reduces technical fidelity, ambiguity detection, or profile compliance.

## 13. Implementation Sequence

Test small changes independently. Do not combine all revisions into one treatment because a combined result cannot identify which change caused an improvement or regression.

### Phase 0: Baseline and Rule Inventory

Files:

- `evals/cases/see-behavior-development.jsonl`
- `evals/cases/see-behavior-holdout.jsonl`
- existing routing case files
- `evals/run.py` and `evals/grade.py` only if the current schemas cannot express required checks

Work:

1. Inventory every current rule and assign a provisional authority category, profile, severity, and enforcement class.
2. Create the twelve transformation cases and eight routing cases.
3. Freeze development and holdout splits.
4. Add deterministic preservation checks.
5. Capture the unmodified baseline with at least three attempts per case.
6. Grade and retain the baseline.

Exit criteria:

- every case has an immutable manifest;
- critical preservation properties have deterministic checks;
- baseline artifacts satisfy `evals/README.md`;
- no production skill or dictionary text has changed.

### Phase 1: Correctness and Precedence

Files:

- `simplified-engineering-english/SKILL.md`
- `simplified-engineering-english/references/dictionary.md`

Work:

1. Add the technical-preservation invariant.
2. Add rule precedence.
3. Repair the path, `now`, `stale`, `default`, and `surface` conflicts.
4. Correct the origin and attribution wording.
5. Remove or mark unsupported superlatives and efficacy claims.
6. Correct BCP 14 semantics and add `NOT RECOMMENDED`.
7. Correct EARS syntax and scope.
8. Replace test-only verification language.

Check:

- run the focused development corpus;
- inspect every technical-fidelity and obligation-force result;
- do not use holdout results to tune this phase.

Exit criteria:

- zero critical preservation regressions;
- all direct contradictions are removed;
- source requirements and SEE adaptations are distinguishable;
- development results improve or remain non-inferior on every critical dimension.

### Phase 2: Profiles and Progressive Disclosure

Files:

- `simplified-engineering-english/SKILL.md`
- `simplified-engineering-english/references/rules.md`

Work:

1. Add strict and engineering-default profiles.
2. Add compact artifact cards.
3. Move detailed rules into `references/rules.md`.
4. Classify each rule as error, warning, suggestion, or project choice.
5. Add source relationship and enforcement metadata.
6. Clarify ambiguity reporting and companion-skill routing.

Check:

- compare this candidate with the accepted Phase 1 candidate;
- measure quality and token changes independently;
- test mixed artifacts that combine a procedure with explanation or a contract with rationale.

Exit criteria:

- profile selection is deterministic for the evaluation corpus;
- strict-profile controls remain available;
- engineering-default rewrites do not apply strict house style without selection;
- any claimed context-cost reduction is supported by paired evidence.

### Phase 3: Dictionary and Glossary Governance

Files:

- `simplified-engineering-english/references/dictionary.md`
- a project glossary schema or fixture only if the evaluation requires it

Work:

1. Keep material cross-domain distinctions.
2. Mark ecosystem-dependent definitions as defaults.
3. Add authoritative override precedence.
4. Correct false absolutes in performance and architecture terms.
5. Define the project glossary fields.
6. Separate semantic glossary data from Vale-compatible accepted and rejected expressions.
7. Define exemption and redaction precedence.

Check:

- run cases where two confusable terms are both correct;
- run cases where a platform specification overrides an SEE default;
- run cases where the project glossary replaces a general term.

Exit criteria:

- the dictionary does not force terminology that contradicts an authoritative ecosystem;
- automatic checks enforce only the fields they can observe;
- semantic definitions remain subject to semantic and technical review.

### Phase 4: Enforcement

Files:

- existing evaluation code where reusable;
- `simplified-engineering-english/scripts/check_see.py` only if Vale and the existing grader cannot implement a required deterministic check;
- focused checker tests only for implemented behavior

Work:

1. Implement lexical checks with existing tools before adding code.
2. Use Vale scopes only where they match the rule's actual semantics.
3. Implement source-to-rewrite preservation checks in the evaluation layer.
4. Add document-tree checks only for cross-block artifact structure.
5. Emit exact checked rule IDs.
6. Separate deterministic failures from semantic review findings.
7. Remove broad conformance claims that no checker supports.

Check:

- each automatic rule has positive, negative, exemption, and boundary examples;
- each check reports the correct source location;
- false positives do not force technical changes;
- the checker cannot report full conformance without required semantic and technical reviews.

Exit criteria:

- all implemented checks have focused tests;
- no checker claim exceeds observed behavior;
- custom code exists only for behavior unavailable from Vale or the existing grader.

### Phase 5: Development and Holdout Evaluation

Files:

- frozen case files
- new immutable result directories under `evals/results/`

Work:

1. Capture treatment runs for the accepted candidate.
2. Grade development runs.
3. Freeze the candidate before opening holdout results.
4. Capture and grade holdout runs.
5. Run blinded, position-swapped judgment for residual semantic dimensions.
6. Conduct the human calibration review.
7. Run the repository merge gate.
8. Record quality, false-positive, and cost results separately.

Exit criteria:

- zero critical regressions;
- no holdout loss on baseline-passing critical cases;
- measured ambiguity improvement;
- non-inferior technical fidelity;
- acceptable per-rule false-positive behavior;
- explained cost changes;
- a passing gate before any efficacy claim.

### Phase 6: Release and Documentation

Files:

- `simplified-engineering-english/SKILL.md`
- `simplified-engineering-english/references/rules.md`
- `simplified-engineering-english/references/dictionary.md`
- `README.md` only if the public skill summary or repository instructions change
- compact evaluation reports and manifests

Work:

1. Apply only the candidate supported by the gate.
2. Update source links and version dates.
3. Record checker coverage and review requirements.
4. Remove obsolete rules, examples, aliases, and duplicated guidance.
5. Validate repository contracts.
6. Publish the retained evidence required by `evals/README.md`.

Exit criteria:

- the production files match the evaluated candidate;
- no stale rule or contradictory example remains;
- the release report states supported and unsupported claims;
- rollback inputs are retained.

## 14. Release and Rollback

### 14.1 Release Checklist

- Baseline and treatment metadata match.
- Production content matches the evaluated candidate hash.
- Deterministic preservation checks pass.
- Development and holdout gates pass.
- Position-sensitive judge results are resolved or reported.
- Human calibration covers every artifact family.
- Critical technical-fidelity regressions are zero.
- No-op preservation passes.
- Rule sources and relationships are present.
- Checker coverage names exact rule IDs.
- Repository validation passes.
- Raw and compact evaluation evidence is retained according to repository policy.

### 14.2 Rollback Triggers

Rollback the candidate if post-release evidence finds any of these conditions:

- changed obligation force;
- changed fact, number, unit, version, condition, or exception;
- altered protected or quoted text without authorized redaction;
- invented technical content;
- unsafe error disclosure;
- strict-profile regression;
- systematic false positives that force incorrect terminology;
- routing regression that activates SEE for implementation work or bypasses SEE for consequential prose;
- production content that differs from the evaluated candidate.

### 14.3 Rollback Method

Retain:

- the prior skill and dictionary hashes;
- baseline and treatment manifests;
- case snapshots;
- deterministic grades;
- judge summaries;
- the accepted release report.

Restore the last passing skill and dictionary together. Do not keep partial compatibility aliases for removed rule IDs unless retained evaluation artifacts require them for interpretation.

## 15. Risks and Controls

| Risk | Control |
| --- | --- |
| Style compliance changes technical meaning. | Apply the preservation invariant before every other language rule and fail deterministically on critical fields. |
| A source guide is treated as universal law. | Record source scope and relationship for every rule. |
| Relaxing rules removes the value of controlled language. | Retain a strict profile and test it independently. |
| The strict profile leaks into ordinary artifacts. | Require explicit profile selection and test engineering-default counterexamples. |
| EARS is treated as complete requirements engineering. | Limit it to suitable syntax and route lifecycle governance to a companion review. |
| A checker reports semantic conformance. | Declare exact check coverage and require semantic and technical review. |
| The dictionary overrides authoritative ecosystem terminology. | Apply source and glossary precedence. |
| Error detail leaks internal information. | Separate user and operator channels and test authorized versus unauthorized paths. |
| Accessibility scope expands into implementation guidance. | Keep prose controls in SEE and route rendered-surface checks elsewhere. |
| Progressive disclosure loses a critical rule. | Compare technical fidelity and ambiguity before and after the split. |
| Evals reward fluent rewrites. | Score technical fidelity and unnecessary edits independently; deterministic failures override judges. |
| The corpus overfits known examples. | Freeze holdouts and add production-derived cases after release without rewriting historical results. |
| One model-specific result becomes a universal claim. | Pin the evaluated model and repeat evaluation for materially different models. |
| Rule metadata becomes duplicate maintenance work. | Keep one canonical record when machine-readable tooling is introduced. |

## 16. Non-goals

- Do not reproduce the ASD-STE100 dictionary.
- Do not claim official ASD or STEMG certification.
- Do not turn SEE into a complete requirements-management process.
- Do not turn SEE into an accessibility implementation standard.
- Do not govern source-code identifiers or architecture decisions.
- Do not require one house style for every software organization.
- Do not add a checker before a rule has a defined scope, severity, and acceptance case.
- Do not add every NASA, Google, Microsoft, Red Hat, IBM, W3C, or ISO recommendation to the core skill.
- Do not claim prompt-density, comprehension, translation, or reviewer benefits without paired evidence.
- Do not use holdout results to tune the candidate.
- Do not preserve deprecated compatibility paths after a clean rule cutover unless retained evidence requires interpretability.

## 17. Supporting Sources

### Controlled and Plain Language

- ASD-STE100 Issue 9: <https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf>
- ASD-STE100 overview: <https://www.asd-ste100.org/about_STE.html>
- ASD-STE100 tooling guidance: <https://asd-ste100.org/STEsoftware.html>
- ISO 24495-1:2023 overview: <https://www.iso.org/standard/78907.html>
- Kuhn, “A Survey and Classification of Controlled Natural Languages”: <https://aclanthology.org/J14-1005/>

### Obligation and Requirements

- RFC 2119: <https://www.rfc-editor.org/rfc/rfc2119>
- RFC 8174: <https://www.rfc-editor.org/rfc/rfc8174>
- Official EARS guide: <https://alistairmavin.com/ears/>
- Original EARS paper: <https://doi.org/10.1109/RE.2009.9>
- “Ten Years of EARS”: <https://doi.org/10.1109/MS.2019.2921164>
- NASA requirements checklist: <https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/>
- Gentili and Falessi, “Characterizing Requirements Smells”: <https://arxiv.org/abs/2404.11106>

### Documentation, Accessibility, and Errors

- Google developer documentation style guide: <https://developers.google.com/style>
- Google active-voice guidance: <https://developers.google.com/style/voice>
- Google contractions guidance: <https://developers.google.com/style/contractions>
- Google tense guidance: <https://developers.google.com/style/tense>
- Google accessibility guidance: <https://developers.google.com/style/accessibility>
- Microsoft verb guidance: <https://learn.microsoft.com/en-us/style-guide/grammar/verbs>
- Diátaxis: <https://diataxis.fr/>
- WCAG error identification: <https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html>
- WCAG error suggestion: <https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html>
- OWASP error-handling guidance: <https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html>

### Enforcement

- Vale `occurrence`: <https://docs.vale.sh/checks/occurrence>
- Vale `metric`: <https://docs.vale.sh/checks/metric>
- Vale `conditional`: <https://docs.vale.sh/checks/conditional>
- Vale vocabularies: <https://docs.vale.sh/keys/vocabularies>
- Vale scopes: <https://docs.vale.sh/topics/scopes>

## 18. Final Deliverables

The improvement project is complete only when it produces:

1. a frozen and retained baseline;
2. a rule inventory with authority, profile, severity, enforcement, and source fields;
3. a preservation-first `SKILL.md`;
4. corrected BCP 14 and EARS guidance;
5. strict and engineering-default profiles;
6. compact artifact cards;
7. a sourced detailed-rules reference;
8. a corrected, override-aware dictionary;
9. deterministic preservation checks;
10. semantic and technical review rubrics;
11. development and holdout behavior cases;
12. expanded routing cases;
13. focused checker tests for every implemented automatic rule;
14. paired quality and cost results;
15. a passing release gate;
16. retained evidence sufficient to reproduce the decision;
17. a release report that states supported claims, unsupported claims, and rollback triggers.
