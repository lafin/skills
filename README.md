# omp Skills

Canonical skills for [OMP](https://github.com/oh-my-pi). Root `<name>/SKILL.md` files are the source of truth.

## OMP

Register this directory in
`~/.omp/agent/config.yml`:

```yaml
skills:
  customDirectories:
    - /<path>/skills
  enableSkillCommands: true
```

Scanning is non-recursive: each skill is `<this-dir>/<name>/SKILL.md`. Restart
omp after changing the configuration or any skill file.

Skills load on demand via `skill://<name>`, and their assets via
`skill://<name>/references/<file>.md`. With `enableSkillCommands`, each skill is
also invocable as `/skill:<name>`.

`.omp/hooks/pre/leancode.ts` keeps leancode active every turn and registers
`/leancode lite|full|ultra|off`. The selected mode persists for the current OMP
process; a new process starts in `full`. The hook loads when OMP runs with this
repository as the working directory; elsewhere, pass it with
`--extension <path>/.omp/hooks/pre/leancode.ts`.

## Validation

```sh
python3 -m pip install -r requirements-validation.txt -r requirements-examples.txt
python3 scripts/validate_skills.py
python3 evals/validate.py
python3 -m unittest discover -s tests
bun test tests/leancode_hook.test.ts
```

The validators check skill metadata, provenance, links, license notices, Python
dependencies, and evaluation-suite structure. The focused tests exercise
validator defects, script contracts, stable example output, and the evaluation
harness. See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution process,
[Skill anatomy](docs/skill-anatomy.md) for the flexible content contract, and
[evals/README.md](evals/README.md) for the OMP behavior and routing evaluation
framework, artifact contract, and reproduction commands.

## Leancode

- `leancode` — implement the smallest verified solution.
- `leancode-review` — review a diff for unnecessary complexity.
- `leancode-audit` — audit a repository for removable complexity.
- `leancode-debt` — list deferred `lean-debt:` shortcuts and their revisit triggers.

## Context engineering

- **Foundations:** `context-fundamentals`, `context-degradation`, `context-compression`, `context-optimization`
- **Systems:** `memory-systems`, `filesystem-context`, `tool-design`
- **Workflows:** `multi-agent-patterns`, `hosted-agents`, `harness-engineering`, `long-horizon-prompting`, `project-development`
- **Evaluation:** `evaluation`, `advanced-evaluation`
- **Specialized:** `latent-briefing`, `self-improvement-loops`, `bdi-mental-states`

## Writing

- `simplified-engineering-english` — write and review consequential software-engineering prose while preserving technical meaning and reducing ambiguity; adapts selected ASD-STE100 mechanisms.
- `lossless-doc-compress` — compress and de-slop design docs, PRDs, and RFCs without losing facts, numbers, decisions, or caveats.

## Reviews

- `ml-system-design-review` — review ML/AI system designs and implementation evidence.
- `ai-stage-gate` — make evidence-based Go / Conditional / Kill decisions for AI initiatives.


## Credentials

- The Context Engineering skills are derived from [Agent Skills for Context Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) at commit `c578e85e40fe2bda7c1fec91ff64cf5285434934`, © 2025 Context Engineering Agent Skills Contributors, under the MIT License. See [ATTRIBUTION.md](ATTRIBUTION.md) and [LICENSE-context-engineering](LICENSE-context-engineering).
- `latent-briefing` also draws on work from Ramp Labs.
- `lossless-doc-compress`, `ml-system-design-review`, and `ai-stage-gate` contain imported or adapted material from [MLSystemDesign](https://github.com/ML-SystemDesign/MLSystemDesign). See [ATTRIBUTION.md](ATTRIBUTION.md) for exact commits and scopes and [LICENSE-ml-system-design](LICENSE-ml-system-design) for the required notice.
- The `leancode` lineage is recorded against the observed external comparison commit without inferring copying direction. See [ATTRIBUTION.md](ATTRIBUTION.md).
- The root [LICENSE](LICENSE) covers repository-original material only; upstream notices continue to apply to imported material.

## Staged evaluation proposals

`source-driven-development`, `api-and-interface-design`, and
`deprecation-and-migration` are non-active candidates under `proposals/`.
They are excluded from root skill discovery until their frozen routing and
behavior admission gates pass. See [ATTRIBUTION.md](ATTRIBUTION.md) and
[LICENSE-addy-agent-skills](LICENSE-addy-agent-skills) for their pinned source
and license.
