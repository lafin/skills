# OpenCode Skills

This directory contains skills for OpenCode. Configure it as a global skill path:

```json
{
  "skills": {
    "paths": ["/<path>/skills"]
  }
}
```

Restart OpenCode after changing this configuration or any skill file.

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

## Reviews

- `ml-system-design-review` — review ML/AI system designs and implementation evidence.
- `ai-stage-gate` — make evidence-based Go / Conditional / Kill decisions for AI initiatives.

## Credentials

- The Context Engineering skills are derived from [Agent Skills for Context Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) at commit `c578e85e40fe2bda7c1fec91ff64cf5285434934`, © 2025 Context Engineering Agent Skills Contributors, under the MIT License. See [ATTRIBUTION.md](ATTRIBUTION.md) and [LICENSE-context-engineering](LICENSE-context-engineering).
- `latent-briefing` also draws on work from Ramp Labs.
- `ml-system-design-review` is based on the ML System Design framework by Kravchenko and Babushkin.
- `ai-stage-gate` is a vendor-neutral adaptation inspired by [Hushpar](https://github.com/Hushpar) and the ML System Design skill collection.
- The Leancode skills are MIT-licensed; no upstream author or source attribution is recorded in their metadata.
