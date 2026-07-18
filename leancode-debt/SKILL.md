---
name: leancode-debt
description: >
  Harvest debt-bearing `lean-debt:` comments into a ledger, so deliberate
  shortcuts and deferrals get tracked instead of rotting into "later means
  never". Use when the user says "leancode debt",
  "/leancode-debt", "what did leancode defer", "list the shortcuts", "leancode
  ledger", or "what did we mark to do later". One-shot report, changes nothing.
license: MIT
---

`lean:` comments are informational intent, not debt. A debt-bearing deferral
uses `lean-debt:` and names both its ceiling and revisit trigger, for example:
`// lean-debt: linear scan; ceiling: large collections; revisit: index when
profiles show it matters`. This collects deferrals so they cannot quietly become
permanent.

## Scan

Search comment content for `lean-debt:` using the language-appropriate prefixes
in the repository (commonly `#`, `//`, `/* ... */`, `--`, `;`, or `%`). Do
not prescribe one brittle regex. Exclude dependencies, generated code, build
artifacts, lockfiles, and VCS metadata by default; scan any of them only when
the user explicitly opts in.

Each hit is one ledger row. Match comment content, not prose that merely
mentions the convention.

## Output

One row per marker, grouped by file:

`<file>:<line> — <what was simplified>. ceiling: <the limit named>. revisit: <the trigger to revisit>.`

The convention is `lean-debt: <shortcut>; ceiling: <limit>; revisit: <trigger>`,
so pull the ceiling and trigger straight from the comment. Want an owner per row too? add
`git blame -L<line>,<line>`.

Flag the rot risk: a missing revisit trigger gets `no-trigger`; a missing ceiling
gets `no-ceiling`.

End with `<N> markers, <M> with no trigger.` Nothing found: `No lean-debt entries. Clean ledger.`

## Boundaries

Reads and reports only, changes nothing. To persist it, ask and it writes the
ledger to a file (e.g. `LEANCODE-DEBT.md`). One-shot.
