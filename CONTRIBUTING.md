# Contributing

Contributions must keep each skill independently installable, routable by OMP, and supported by review or evaluation evidence appropriate to the change.

## Before editing

1. Identify the unit of work that the skill owns and its nearest adjacent owners.
2. Read the existing skill, its local references, and its evaluation cases.
3. Decide whether the change affects routing, behavior, provenance, or executable helpers.
4. Keep harness-wide planning, delegation, verification, and user-ground-truth rules out of individual skills.

Use [Skill anatomy](docs/skill-anatomy.md) as a content contract. It is not a required heading template.

## Skill layout and metadata

A root skill uses this layout:

```text
<lower-case-kebab-name>/
  SKILL.md
  references/  # only when needed
  scripts/     # only when needed
  assets/      # only when needed
```

Do not add empty directories. The directory and frontmatter `name` must use lower-case kebab case and must match exactly. A `description` must be non-empty and no longer than 1,024 characters. It should state the owned work, user-language triggers, and the closest exclusions. Keep workflow detail in the body.

Repository-original metadata uses:

```yaml
---
name: example-skill
description: Use this skill when ... Do not use it for ...
license: MIT
metadata:
  provenance: repository-original
---
```

Imported or adapted material must record the exact upstream repository, immutable 40-character commit, source path, adaptation type, and any required license notice:

```yaml
metadata:
  upstream: owner/repository
  upstream_commit: 0123456789abcdef0123456789abcdef01234567
  upstream_path: path/to/source
  adaptation: imported  # imported, modified, or inspired
  license_notice: LICENSE-upstream
```

Update `ATTRIBUTION.md` when attribution scope changes. Do not infer copying direction or replace an immutable revision with a branch or tag.

## References and progressive disclosure

Keep core decisions and safety boundaries in `SKILL.md`. Move independently useful deep examples, research notes, long rubrics, and reusable tables into the owning skill's `references/` directory. Link every reference directly from `SKILL.md`; do not create discovery chains between references.

Use owning-skill asset URIs such as `skill://example-skill/references/details.md`. A skill must not depend on another skill's asset path. A bare URI such as `skill://adjacent-owner` may route the reader to an adjacent owner.

A `SKILL.md` file above 500 lines produces a review warning, not a validation failure. Split content only when the extracted material is useful on its own and the skill still works without loading every reference.

## Executable helpers

Python helpers may remain under the owning skill. The skill must document each helper's:

- **Status:** production helper, evaluator, example, or template;
- **Boundary:** what it validates or transforms and what it does not prove;
- **Run:** exact command and required inputs;
- **Output:** stable machine-readable or human-readable result;
- **Failure:** non-zero conditions and repair direction.

Examples and templates must identify mocks, heuristics, replacement points, and unavailable external services. A helper is not evidence of semantic correctness unless an evaluation establishes that claim.

## Evaluation process

Deterministic checks run before model judges. Description changes require routing evaluation. New or materially changed skills require development behavior cases and separately frozen holdout behavior cases. Use repository fixtures when the claimed result is a file or code change, and define observable success, prohibited outcomes, pressure conditions, and critical failures.

Freeze evaluator or rubric changes in a separate pre-treatment change. Baseline and treatment comparisons must use the same model, profile, tools, attempt count, and effective timeouts. Use at least three attempts when output varies materially. Do not inspect or tune against holdout prompts; execute them only through the guarded holdout path against recorded immutable baseline and treatment revisions.

Follow [the evaluation guide](evals/README.md) for suite lifecycle, commands, result manifests, and release evidence. Preserve historical evidence when a case or skill is retired. Do not claim efficacy from source inspection, routing evidence alone, incomplete attempts, or unavailable artifacts.

## Review gates

Before requesting review:

1. Run the objective repository checks:

   ```sh
   python3 scripts/validate_skills.py
   python3 evals/validate.py
   python3 -m unittest discover -s tests
   python3 -m unittest discover -s context-compression/tests
   bun test tests/leancode_hook.test.ts
   ```

2. Review the eight anatomy concepts and any script fields in [Skill anatomy](docs/skill-anatomy.md).
3. Confirm that provenance, licenses, local references, README inventory, and evaluation manifests are complete.
4. Confirm that every changed routing or behavior claim has the required development and frozen-holdout evidence.
5. Record unresolved evidence as a blocker.

Objective validation does not prove trigger quality, exclusion completeness, workflow correctness, semantic overlap, or exit-evidence adequacy. Those decisions require contributor review and, where applicable, live evaluation. Required human review, qualified technical attestation, durable external artifact storage, and credentials must be supplied by authorized people or systems; contributors must not synthesize them.