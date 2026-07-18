---
name: leancode-audit
description: >
  Whole-repo audit for over-engineering. Like leancode-review, but scans the
  entire codebase instead of a diff: a ranked list of what to delete, simplify,
  or replace with stdlib/native equivalents. Use when the user says "audit this
  codebase", "audit for over-engineering", "what can I delete from this repo",
  "find bloat", "leancode-audit", or "/leancode-audit". One-shot report, does
  not apply fixes.
license: MIT
---

leancode-review, repo-wide. Scan the whole tree instead of a diff. Rank
findings biggest cut first.

## Tags

Same as leancode-review:

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.
- `scope:` unrelated change, drive-by refactor, restyle, or added type hints. Revert it.

## Scan scope

Exclude dependencies, generated code, build artifacts, and lockfiles by default.
Include one only when the user explicitly asks to audit that surface.

## Hunt

Deps the stdlib or platform already ships, single-implementation interfaces,
factories with one product, wrappers that only delegate, files exporting one
thing, dead flags and config, hand-rolled stdlib.

## Output

One line per finding, ranked: `<tag> <what to cut>. <replacement>. [path]`.
End with `net: -<N> lines, -<M> deps possible.` Nothing to cut: `Lean already. Ship.`

## Boundaries

Complexity only, correctness bugs, security holes, and performance go to a
normal review pass. Lists findings, applies nothing. One-shot.
