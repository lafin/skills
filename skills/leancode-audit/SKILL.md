---
name: leancode-audit
description: >
  Whole-repo audit for over-engineering. Like leancode-review, but scans the
  entire codebase instead of a diff: a ranked list of what to delete, simplify,
  or replace with stdlib/native equivalents. Use when the user says "audit this
  codebase", "audit for over-engineering", "what can I delete from this repo",
  "find bloat", "leancode-audit", or "/skill:leancode-audit". One-shot report, does
  not apply fixes.
license: MIT
metadata:
  provenance: repository-original
---

leancode-review, repo-wide. Scan the whole tree instead of a diff. Rank
findings biggest cut first.

## Tags

Same as leancode-review, except `scope:`; a whole-repo audit has no request to
compare against:

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.

## Scan scope

Exclude dependencies, generated code, build artifacts, and lockfiles by default.
Include one only when the user explicitly asks to audit that surface.

If the repository already has a dead-code analyzer (for example knip or
vulture), run it and cite its output. Do not install one without asking.
Confirm each `delete:` with a reference search.

## Hunt

Deps the stdlib or platform already ships, single-implementation interfaces,
factories with one product, wrappers that only delegate, modules whose single
export has a single caller, dead flags and config, fallbacks for states internal
code cannot reach, comments that restate the code, hand-rolled stdlib.

## Output

One line per finding, ranked: `<tag> <what to cut>. <replacement>. [path]`.
Each finding names the exact cut and its evidence (callers, references, or
analyzer output); file size alone is not a finding. State which paths were
scanned.
End with `net: -<N> lines, -<M> deps possible.` Nothing to cut: `Lean already. Ship.`

## Boundaries

Complexity only, correctness bugs, security holes, and performance go to a
normal review pass. Lists findings, applies nothing. One-shot.
