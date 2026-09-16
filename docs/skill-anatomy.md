# Skill anatomy

This guide defines the content a skill must make easy to find. It does not require a fixed outline or cosmetic heading names. Preserve clear existing structures.

## Content contract

Each skill must cover these concepts:

1. **Purpose and owned unit of work.** State the concrete decision, transformation, or artifact the skill owns.
2. **Positive triggers.** Describe requests that should activate the skill in language users are likely to use.
3. **Exclusions and adjacent owners.** Name the nearest confusable work and route it to the correct skill or harness capability.
4. **Workflow or decision process.** Give the ordered actions, branches, inputs, and constraints needed to do the work.
5. **Failure modes.** Name domain-specific red flags, tempting shortcuts, and rationalizations that produce plausible but incorrect results.
6. **Exit evidence and output contract.** Define what the skill returns and what observable evidence shows that the work is complete.
7. **Progressive-disclosure references.** Link optional detail directly from `SKILL.md` and state when to load it.
8. **Executable-script status and boundary.** For every helper, state its operational contract; if there is no helper, no script section is needed.

A concept may appear under any heading, table, checklist, or concise paragraph. Reviewers assess whether a reader can find and act on it, not whether the document matches a template.

## Routing description

The frontmatter `description` is catalog metadata. It must be non-empty, no longer than 1,024 characters, and answer three questions:

- What unit of work does this skill own?
- What user requests should trigger it?
- What closest requests belong elsewhere?

Do not summarize the full workflow in the description. Description changes require routing evaluation because character count is objective but trigger quality is semantic.

## Progressive disclosure

Keep core decisions, hard constraints, and safety boundaries in `SKILL.md`. Move material to `references/` when it is independently useful and expensive to load on every activation, such as:

- deep examples;
- research notes and dated evidence;
- long rubrics or checklists;
- reusable tables;
- implementation detail for a narrow subtask.

Every reference must be reachable directly from `SKILL.md`. State why or when to read it. Avoid a chain where one reference is discoverable only through another. The skill must remain operable without loading every reference.

Keep assets inside the owning skill. Use `skill://<owner>/references/<file>` for an owning-skill asset. Use bare `skill://<adjacent-owner>` only to route to another skill. A path into another skill's assets creates a non-portable dependency and is rejected.

A file above 500 lines receives a warning for review. Length alone is not a reason to split coherent material.

## Script contract

For each executable helper, document:

| Field | Required content |
| --- | --- |
| Status | Production helper, evaluator, example, or template |
| Boundary | What the script validates or transforms and what it does not prove |
| Run | Exact command, inputs, and required environment |
| Output | Stable machine-readable or human-readable contract |
| Failure | Non-zero conditions and the repair direction |

Examples and templates must disclose mocks, heuristics, pseudo-random data, replacement points, and missing external integrations. Do not create empty `scripts/`, `references/`, or `assets/` directories.

## Evidence and review

Deterministic validation covers only objective properties: names, exact name matching, description length, provenance fields, immutable revisions, license notices, paths, fragments, asset ownership, Python syntax and dependencies, and README inventory.

Contributor review and live evaluation cover semantic properties:

- trigger quality and routing boundaries;
- completeness of exclusions;
- workflow correctness;
- failure-mode coverage;
- adequacy of exit evidence;
- semantic overlap with adjacent skills.

A new or materially changed skill needs development and frozen-holdout behavior evidence. A description change needs routing evidence. Evaluator and rubric changes must be frozen separately before treatment. Holdout comparisons must use recorded immutable catalog revisions and identical execution settings.

Human review, qualified technical attestation, durable external evidence storage, and credentials remain external gates when required. Missing gates make a decision incomplete; source text or generated records cannot substitute for them.