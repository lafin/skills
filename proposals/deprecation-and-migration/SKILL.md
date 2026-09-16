---
name: deprecation-and-migration
description: >
  Use for safely moving consumers from an old public, distributed, or persisted
  contract to a replacement: internal atomic cutovers, compatibility windows and
  rolling production migrations, or database expand/backfill/verify/cutover/contract.
  Route direct simplification with no compatibility boundary to leancode,
  project-level architecture choices to project-development, and replacement
  interface design to api-and-interface-design.
license: MIT
metadata:
  upstream: "https://github.com/addyosmani/agent-skills"
  upstream_commit: "be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39"
  upstream_path: "skills/deprecation-and-migration/SKILL.md"
  adaptation: modified
  license_notice: LICENSE-addy-agent-skills
---

# Deprecation and Migration

Move consumers safely from an old contract to a ready replacement, then remove
the old contract. Choose the migration mode before editing: the wrong mode
creates either needless compatibility code or an unsafe cutover.

## Scope

Use this skill when an existing contract crosses a compatibility boundary:

- public APIs, libraries, events, protocols, or files used outside one atomic
  change;
- distributed services or fleets where old and new versions overlap;
- persisted data or database schemas;
- internal interfaces whose callers must all move together.

Do not use it to design the replacement interface; use
`api-and-interface-design`. Do not use it to choose the project's architecture;
use `project-development`. If the change is only direct local simplification
with no compatibility boundary, use `leancode`.

Do not begin a compulsory migration until the replacement covers the required
behavior and is deployable. If it is not ready, report that prerequisite rather
than pretending a deprecation notice makes the transition safe.

## Classify the Migration

| Mode | Boundary | Required strategy |
|---|---|---|
| Internal atomic cutover | All callers and producer can change in one repository/release | Migrate every caller, verify behavior, remove the old path in the same change. No alias or shim. |
| Public or rolling compatibility | Consumers deploy independently, are external, or old and new versions overlap | Keep both paths for an explicit window, measure use, roll out in stages, preserve rollback, then remove after the gate. |
| Database change | The contract is persisted data or schema | Expand, backfill, verify, cut over, then contract in separate deploys. |

When ownership or deploy independence is unknown, investigate consumers and
release topology first. Do not silently choose atomic cutover.

## 1. Internal Atomic Cutover

Use a clean cutover only when every caller is discoverable and can ship with the
producer.

1. Find all definitions, imports, calls, configuration, tests, and generated
   references to the old contract.
2. Change the producer and every caller together.
3. Verify consumer-observable behavior at the real entry points.
4. Remove the old symbol, alias, adapter, tests, documentation, and configuration.
5. Search again for stale references.

A compatibility alias is a failure in this mode. It hides a missed caller and
turns an atomic change into an unowned deprecation. If one consumer cannot move
in the same release, reclassify the work as a rolling migration.

Rollback is the previous atomic release, not a permanent old-name shim. Keep the
change revertible until its behavior check passes.

## 2. Public or Rolling Compatibility

Independent consumers require an explicit transition rather than immediate
removal.

### Establish the contract

Record:

- the old and replacement contracts and any observable differences;
- known owners and consumers, including discovery limits;
- whether deprecation is advisory or compulsory;
- the compatibility window or removal criterion;
- the usage signal that proves progress;
- the rollout stages, stop conditions, and rollback action.

A date without usage evidence is not a removal gate. For a compulsory deadline,
state the risk or maintenance reason and provide migration instructions or
tooling.

### Roll out

1. Deploy the replacement while the old path still works.
2. Instrument old-path use and distinguish real traffic from probes or retries.
3. Migrate owned consumers first and verify their observable results.
4. Shift a bounded cohort or traffic percentage. Compare errors, correctness,
   and service objectives; stop on a breached threshold.
5. Increase exposure only after the prior stage passes.
6. Hold at the replacement with the old path idle but available for the agreed
   rollback window.
7. Remove the old path only after the registered usage and compatibility gates
   pass.

Rollback must remain executable during the window: route traffic back, disable
the new writer or feature, or redeploy the prior compatible version. Do not
remove the old implementation, destroy old-format data, or make the replacement
the sole readable form before that rollback is proven.

Adapters and dual paths are temporary tools for this mode. Give each an owner
and removal gate; do not copy them into an internal atomic cutover.

## 3. Database Migration

Never rename or drop a live column in the same deploy that introduces code
requiring the new shape. Old and new application versions overlap, and data
outlives either version.

### Expand

Add the new nullable column, table, index, or representation without removing
the old one. Deploy code that can tolerate both shapes. If writes occur during
the migration, dual-write or otherwise capture changes so the backfill cannot
lose concurrent updates.

### Backfill

Copy existing data in bounded, restartable batches off the hot path. Define a
stable cursor, throttle policy, idempotent retry behavior, and progress metric.
Do not use one unbounded update where it can lock or overload production.

### Verify

Before switching reads, compare old and new representations using explicit
invariants: row coverage, null counts, checksums or sampled semantic equality,
and reconciliation of writes that arrived during backfill. Investigate drift;
do not average it away.

### Cut over

Switch reads or traffic behind a reversible control while maintaining the old
representation and any required dual-write. Observe the agreed bake window.
Rollback switches reads or traffic back; it must not require reconstructing data
that the migration already destroyed.

### Contract

After all old readers and writers are gone, verification remains clean, and the
rollback window closes, stop old writes. Drop the old schema in a later,
dedicated deploy. Treat backup/restore as disaster recovery, not as a substitute
for a reversible pre-contract cutover.

## Removal Gate

Remove the old contract only when all applicable evidence is present:

- the replacement is deployed and covers required behavior;
- known consumers are migrated and unknown-consumer discovery was addressed;
- old-path usage is zero for the agreed observation window;
- rollout checks and service objectives pass;
- rollback was exercised or otherwise directly verified while still possible;
- for data changes, backfill invariants pass and no old reader or writer remains.

After the gate passes, remove the old implementation, compatibility layer,
flags, metrics that existed only for migration, tests, documentation, and
configuration. Leaving a dormant path behind is not a completed migration.

## Pressure Checks

Reject these shortcuts:

- “Keep the alias just in case” during an internal atomic cutover.
- “All known clients moved” when uninstrumented or external clients may exist.
- “Delete the fallback now to reduce maintenance” before the rolling rollback
  window closes.
- “Rename the column in place” or combine additive and destructive schema work.
- “Backfill succeeded” without reconciliation against concurrent writes.
- “We can write the rollback later” after the destructive step has shipped.

Report which migration mode applies, the evidence required for cutover and
removal, and the exact rollback boundary. Never claim zero usage, successful
backfill, rollback readiness, or production safety without observed evidence.
