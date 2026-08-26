# omp Skills

Skills for [omp](https://github.com/oh-my-pi). Register this directory in
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
`/leancode lite|full|ultra|off`. It loads when omp runs with this repository as
the working directory; elsewhere, pass it with `--extension <path>/.omp/hooks/pre/leancode.ts`.

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

- `simplified-engineering-english` — write and review software-engineering prose in a controlled subset of English derived from ASD-STE100.
- `lossless-doc-compress` — compress and de-slop design docs, PRDs, and RFCs without losing facts, numbers, decisions, or caveats.

## Reviews

- `ml-system-design-review` — review ML/AI system designs and implementation evidence.
- `ai-stage-gate` — make evidence-based Go / Conditional / Kill decisions for AI initiatives.

## Credentials

- The Context Engineering skills are derived from [Agent Skills for Context Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) at commit `c578e85e40fe2bda7c1fec91ff64cf5285434934`, © 2025 Context Engineering Agent Skills Contributors, under the MIT License. See [ATTRIBUTION.md](ATTRIBUTION.md) and [LICENSE-context-engineering](LICENSE-context-engineering).
- `latent-briefing` also draws on work from Ramp Labs.
- `ml-system-design-review` is based on the ML System Design framework by Kravchenko and Babushkin.
- `lossless-doc-compress` is imported from [MLSystemDesign](https://github.com/ML-SystemDesign/MLSystemDesign) at commit `61b9bcdb971e7424cdc4d400085338dc35da910e`, under the MIT License.
- `ai-stage-gate` is a vendor-neutral adaptation inspired by [Hushpar](https://github.com/Hushpar) and the ML System Design skill collection.
- The Leancode skills are MIT-licensed; no upstream author or source attribution is recorded in their metadata.
