---
description: Review a topic, fix verified HIGH and MEDIUM findings, and repeat until only LOW findings remain.
---

# /review-and-fix

Invocation: `/review-and-fix [--max=N] <topic>`

Examples:

- `/review-and-fix security`
- `/review-and-fix --max=3 performance in src/api`
- `/review-and-fix correctness of all changes`

## Arguments

Parse only `$ARGUMENTS`.

- `<topic>` is required. Treat all non-flag text as one topic.
- `--max=N` sets the maximum repair iterations. The default is `5`.
- `N` MUST be an integer from `1` through `20`.
- Reject an unknown flag, a conflicting repeated flag, or an empty topic.
- On rejection, show the invocation syntax and stop without changing files.

The topic defines both the review lens and optional scope text. Do not replace the requested topic with a general review.

Resolve the scope in this order:

1. Use paths, globs, commits, or scope terms that the topic names.
2. Otherwise, use staged, unstaged, untracked, and deleted files in the current Git workspace.
3. If the workspace has no changes, use the smallest repository area that contains the topic's entry points.

Include direct callers, consumers, tests, schemas, and configuration only when they prove the reviewed contract. Exclude dependency caches, generated build output, session data, and logs unless the topic names them.

## Severity

Every finding MUST use one severity:

- `HIGH`: A supported path can cause an exploit, data loss, serious incorrect behavior, a crash, or a public-contract break. No reasonable workaround exists.
- `MEDIUM`: A supported path has a reproducible defect or material risk. The impact is bounded or a workaround exists.
- `LOW`: The issue is minor hardening, maintainability, usability, or an unlikely edge case. The fix is optional.

Do not assign severity from fix effort. Do not report style preferences without an observable consequence.

A finding MUST contain:

- stable ID;
- severity;
- path and line, when available;
- short title;
- concrete evidence;
- user or system impact;
- smallest safe fix.

Omit uncertain claims. Put missing evidence in review coverage instead of a finding.

## Agent routing

Use OMP agents. Do not simulate subagents with repeated local reads.

Use these built-in agents first:

- `scout`: scope discovery and shard planning for a large review;
- `reviewer`: correctness, reliability, performance, architecture, tests, and general topics;
- `security-reviewer`: security, authentication, authorization, privacy, and secret-handling topics;
- `designer`: UI, UX, accessibility, interaction, and visual topics;
- `librarian`: external library, framework, protocol, and API-contract questions;
- `deep-verifier`: independent evidence checks, severity checks, and cross-shard deduplication;
- `fixer`: implementation of confirmed findings.

The controller MUST use the `task` tool for delegation. Select the generic default task agent only when no specialist matches the topic. Use `sonic` only for mechanical inventory or counting.

The controller owns scope, iteration state, finding IDs, deduplication, reports, stop decisions, and verification.

## Efficient review

First measure the resolved scope. Count review lines as changed lines for a diff scope and total lines for a snapshot scope. A review is large when it has more than 20 files or more than 3000 review lines.

For a small review, dispatch the minimum matching reviewer set.

For a large review:

1. Dispatch one `scout` to return paths, module boundaries, contracts, and a shard plan.
2. Group files by module and contract. Do not shard only by equal line counts.
3. Target at most 15 files or 2500 review lines per shard.
4. Dispatch at most six independent review shards in one `task` batch.
5. Dispatch more waves only after the current wave reaches its barrier.
6. Send agents paths, the topic, scope rules, and the diff base. Use `NONE` as the diff base for a snapshot scope. Do not paste source files or full diffs into prompts.
7. Do not assign one file to multiple reviewers unless two topic specialists are necessary.
8. Keep accepted results for unchanged shards. Re-review only dirty shards and their direct contract closure.

Every review task MUST skip builds, linters, formatters, and test suites. The controller runs verification once after the fix wave.

Require each review task to return structured data with these fields:

- `findings`: finding records without controller IDs;
- `reviewed_paths`: paths inspected for the assigned topic;
- `unreviewed_paths`: paths that need more evidence, with a reason.

Use `schemaMode: strict` and a task-specific `outputSchema` when the runtime supports it.

If a reviewer reports an unreviewed in-scope path, reassign that path before the review is complete.

## Evidence and deduplication

After each review wave:

1. Assign each raw candidate a temporary ID in the form `C<iteration>-<shard>-<number>`.
2. Send every proposed `HIGH` and `MEDIUM` candidate to `deep-verifier` in `VERIFY` mode.
3. Reject, downgrade, or confirm each candidate from fresh evidence.
4. When more than one candidate remains, send confirmed and downgraded candidates to `deep-verifier` in `DEDUPLICATE` mode.
5. Merge duplicate `LOW` candidates by root cause and affected contract.
6. Keep the highest supported severity, not the highest proposed severity.
7. Assign stable finding IDs in the form `I<iteration>-F<number>`.
8. Fix only findings with a `CONFIRMED` or `DOWNGRADED` verification decision.

For a large candidate set, partition verification by module. Dispatch at most six independent `deep-verifier` tasks in one batch.

A changed path invalidates only findings and clean-review evidence that depend on that path or its contract closure.

## Repair loop

An iteration uses one confirmed review state, one fix wave, one verification step, and one post-fix review.

Build the initial confirmed review state before the first iteration. A later iteration MUST reuse the prior post-fix review state.

Run this loop:

1. Use the current confirmed review state.
2. If no `HIGH` or `MEDIUM` finding remains, report the iteration and stop.
3. Group confirmed `HIGH` and `MEDIUM` findings by file ownership and dependency order.
4. Dispatch `fixer` agents for disjoint path groups in one `task` batch.
5. Serialize fixes that touch the same file or public contract.
6. A fixer MUST address the root cause and preserve unrelated user changes.
7. A fixer MUST update affected callers, tests, schemas, and documentation when the contract requires it.
8. A fixer MUST NOT run project-wide validation while sibling fixers are active.
9. Fix a `LOW` finding only when the fix is local, safe, and requires no extra dependency or public behavior change.
10. Recheck every fixer rejection with `deep-verifier`. Remove the finding only when fresh evidence disproves it.
11. If a fixer needs an obtainable in-scope path, expand exclusive ownership and redispatch the finding in this iteration.
12. If a fixer needs unavailable information or access, keep the finding open and stop with `BLOCKED`.
13. Ensure that every dispatched finding has one applied, verified-rejected, or blocked outcome.
14. Run the narrowest existing formatter and focused verification command for each changed contract.
15. Track verification as `PASS`, `FAIL`, or `N/A` for each finding.
16. Keep an original finding open until its verification is `PASS` or justified `N/A`.
17. Re-review every changed path and its direct contract closure with the matching review specialist.
18. Merge the post-fix results with unchanged clean-shard evidence and unchanged open findings.
19. Count a finding as fixed only when verification passed or is justified `N/A`, and post-fix review no longer reproduces it.
20. Report the iteration.
21. If `HIGH` or `MEDIUM` findings remain and the iteration count is below `--max`, start the next iteration from this review state.

When verification fails, keep each affected original finding open. Add a separate finding only when evidence proves a distinct defect and its severity. Use `BLOCKED` for an unavailable tool, environment, permission, or required oracle.

## Stop rules

Stop with one status:

- `CLEAN`: The current review state has no findings.
- `LOW_ONLY`: The current review state has only `LOW` findings.
- `LIMIT_REACHED`: `--max` repair iterations completed and `HIGH` or `MEDIUM` findings remain.
- `BLOCKED`: A required fix or verification step needs information or access that tools cannot obtain.
- `USAGE`: The invocation is invalid.

`LOW` findings never start another iteration. Report them as optional work.

Do not claim `CLEAN` or `LOW_ONLY` from agent consensus alone. The resolved scope MUST have complete topic coverage. Every path changed by a fixer MUST have post-fix review coverage.

## Iteration report

After every iteration, print exactly one brief report before any next iteration:

```text
Iteration <n>/<max>: found HIGH <n>, MEDIUM <n>, LOW <n>; fixed HIGH <n>, MEDIUM <n>, LOW <n>; remaining HIGH <n>, MEDIUM <n>, LOW <n>; verification <PASS|FAIL|N/A>.
```

Counts are finding counts, not patch or file counts.

## Final report

Return:

```text
Status: <CLEAN|LOW_ONLY|LIMIT_REACHED|BLOCKED|USAGE>
Topic: <topic>
Scope: <brief resolved scope>
Iterations: <used>/<max>
Fixed: HIGH <n>, MEDIUM <n>, LOW <n>
Remaining: HIGH <n>, MEDIUM <n>, LOW <n>
Verification: <commands and results, or N/A with reason>
```

List remaining findings after the record. Keep each finding to one line with ID, severity, path, line, and title.
