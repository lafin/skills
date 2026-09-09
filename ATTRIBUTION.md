# Skill Sources and License Scope

This repository contains original work, imported skills, and adaptations.
The root [MIT license](LICENSE) covers repository-original material only.
Imported material keeps its source notice below.

## Context Engineering Skills

Source: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering

Fetched commit: `c578e85e40fe2bda7c1fec91ff64cf5285434934`

Copyright (c) 2025 Context Engineering Agent Skills Contributors. Imported
materials are provided under the MIT License; see
[LICENSE-context-engineering](LICENSE-context-engineering).

Import scope: the 17 direct child skill directories from upstream `skills/`,
including their `SKILL.md` files, references, and illustrative scripts.
Upstream plugin, researcher, and examples infrastructure was excluded.

Import date: 2026-07-18.

## ML System Design Skills

Source: https://github.com/ML-SystemDesign/MLSystemDesign

The following local skills contain material from the named source snapshots:

| Local skill | Source path | Source commit | Adaptation |
|---|---|---|---|
| `lossless-doc-compress` | `skills/lossless-doc-compress` | `61b9bcdb971e7424cdc4d400085338dc35da910e` | Imported |
| `ml-system-design-review` | `skills/ml-system-design-review` | `90830cd7e52dc2cd6ff2a0d69d96f042759d3430` | Modified metadata |
| `ai-stage-gate` | `skills/ai-stage-gate` | `e439d91dbbd6a303115e42a6b9545563a7c4641f` | Modified metadata |

The upstream repository distributes these skills under the MIT License. Keep
the upstream notice in
[LICENSE-ml-system-design](LICENSE-ml-system-design). The exact
`lossless-doc-compress` snapshot includes that license. The license file was
added after the other two named source snapshots, at upstream commit
`d330164abcfe296330180962a5b8a92aeb736842`. This record distinguishes the
content snapshot from the later repository license record.

The `ai-stage-gate` source also credits Hushpar as conceptual inspiration. No
Hushpar code or license grant is asserted here.

## Leancode Skills

The four Leancode skills first appear in local commit
`e929566264f23040891a2c4c521d3e9110869bf5`, authored and committed by
`lafin` on 2026-07-18T22:17:02+03:00. That commit has no source note or
co-author trailer for these files.

`leancode/SKILL.md` shares wording and the four-principle structure with
`multica-ai/andrej-karpathy-skills` at commit
`8462496b34419f20b32778610571ac723e91f94c`, authored and committed by
Jiayuan Zhang on 2026-01-27T03:53:00Z. The external commit message describes
the file as Karpathy-inspired and has a `Co-Authored-By: Claude Opus 4.5`
trailer.

A trimmed-line comparison between those two first snapshots found these 21
distinct exact lines:

- `## 1. Think Before Coding`
- `Don't assume. Don't hide confusion. Surface tradeoffs.` (bold in both)
- `If a simpler approach exists, say so. Push back when warranted.`
- `If something is unclear, stop. Name what's confusing. Ask.`
- `## 2. Simplicity First`
- `Minimum code that solves the problem. Nothing speculative.` (bold in both)
- `## 3. Surgical Changes`
- `Touch only what you must. Clean up only your own mess.` (bold in both)
- `When editing existing code:`
- `Don't "improve" adjacent code, comments, or formatting.`
- `Don't refactor things that aren't broken.`
- `Match existing style, even if you'd do it differently.`
- `When your changes create orphans:`
- `Remove imports/variables/functions that YOUR changes made unused.`
- `Don't remove pre-existing dead code unless asked.`
- `## 4. Goal-Driven Execution`
- `Define success criteria. Loop until verified.` (bold in both)
- `Transform tasks into verifiable goals:`
- `1. [Step] → verify: [check]`
- `2. [Step] → verify: [check]`
- `3. [Step] → verify: [check]`

The external snapshot predates the local commit, but the available history
does not establish copying direction. The external repository and both
implementations cite Andrej Karpathy's public observations as inspiration.
The external repository declares MIT in its README and skill metadata but
does not contain a complete license notice at the inspected commit. This
repository licenses its local Leancode material under the root MIT license
without asserting ownership of third-party wording.

No substantive external match was found for `leancode-review`,
`leancode-audit`, or `leancode-debt`.

## Simplified Engineering English

`simplified-engineering-english` is repository-original material inspired by
ASD-STE100 Issue 9, published in January 2025:
https://asd-ste100.org/

ASD owns ASD-STE100. The local skill adapts controlled-language concepts and
does not distribute the standard or its dictionary. The root MIT license
covers only the local adaptation.
