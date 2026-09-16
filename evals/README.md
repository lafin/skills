# Behavior, repository, and routing evaluation

This evaluation uses OMP's real noninteractive adapter. `run.py` invokes `omp --mode=rpc`, sends JSONL requests on stdin, captures the complete JSONL event stream and stderr, and extracts the final assistant response, tool events, model, usage, and runtime fields. It does not call a model provider directly.

## Cases

- `cases/behavior.jsonl` contains eight development cases for `leancode` behavior.
- `cases/repository-development.jsonl` contains seven editable repository cases.
- `cases/repository-holdout.jsonl` contains three held-out repository cases. Do not use holdout results to tune a change.
- `cases/routing-development.jsonl` and `cases/routing-holdout.jsonl` contain distinct cases for each confusable skill pair.
- `cases/see-behavior-development.jsonl` and `cases/see-behavior-holdout.jsonl` contain the frozen SEE transformation corpus.
- `cases/see-routing-development.jsonl` and `cases/see-routing-holdout.jsonl` distinguish SEE from adjacent writing, evaluation, design, implementation, and review skills.

Every case names observable success, prohibited outcomes, and deterministic checks. Repository cases copy an immutable `fixtures/<fixture>/initial` tree into a temporary worktree and run the fixture's `verify.py` against the final tree. Behavior prompts request an explicit decision record because these cases measure change scope and verification choices without modifying this repository. Each routing case declares the confusable `available_skills` pair and the `evaluated_skills` whose content may differ between paired conditions.
SEE behavior cases also contain a fixed `case_manifest`. It records the artifact family, selected profile, source facts, protected and quoted spans, conditions, values, obligation force, permitted rewrites, required structure, ambiguity traps, and prohibited inventions. The grader checks only protected spans, quotations, values, and obligation force byte-for-byte. Conditions and exceptions require semantic review unless a case declares a valid structural predicate. Case validation rejects a value that is both declared for exact preservation and contained in a rewrite span that a `not_contains` check prohibits. `see-rubric.json` defines the separate semantic and technical review dimensions and critical floors.

## Manifest lifecycle and selection

`suites.json` is the complete case-file inventory. Each file records its
`kind`, `split`, lifecycle `status`, suite, frozen content hash, comparison
contract, and retained baseline and treatment catalog revisions where
applicable. The statuses have these execution rules:

| Status | Active coverage | Development | Guarded holdout | Independent holdout | Release |
|---|---|---|---|---|---|
| `proposal` | no | only `--proposal-baseline` | yes, after both revisions and the contract are frozen | no | no |
| `canonical` | yes | normal `--suite` or `--cases` | yes | no | yes |
| `independent-holdout` | no | no | no | yes | yes |
| `release-only` | no | no | no | no | yes |
| `historical` | no | only with an explicit retained catalog | only with `--allow-historical` | no | no |

Only canonical rows count toward active coverage. A non-null
`admission_candidate` names the one new root temporarily allowed to have
canonical development coverage while its proposal holdout stays frozen. It is
not a lifecycle status. Release selection is unavailable until the candidate
is cleared and full canonical coverage exists.

Normal `--suite` and explicit `--cases` selection are development-only.
`--mode holdout` is the only direct holdout path. It verifies the frozen case
hash and comparison contract, resolves both full catalog commits into isolated
roots, and evaluates only the root selected by `--condition`. Run it once per
condition; `grade.py` pairs the two immutable condition directories.
`independent-holdout` and `release` modes delegate every selected holdout to
the same guard. They do not bypass it.

## Capture real runs

Use one exact model name and the contract's profile, config, tool list,
thinking level, attempt count, system prompt hash, and timeout policy for both
conditions. Use a dedicated authenticated profile with no configured MCP
servers. The profile must register this repository root under
`skills.customDirectories`; immutable runs add a generated overlay that
replaces it with the selected archived root. `--tools ''` disables built-in
tools. Repository cases require an explicit editing-tool allowlist.

Development remains compatible with explicit case paths:

```sh
MODEL='openai-codex/gpt-5.6-sol'
PROFILE='skill-eval-isolated'
python3 evals/run.py \
  --cases evals/cases/routing-development.jsonl \
  --condition baseline --model "$MODEL" --profile "$PROFILE" --attempts 3 \
  --tools '' --output evals/results/change-id/development-baseline
python3 evals/run.py \
  --suite routing \
  --condition treatment --model "$MODEL" --profile "$PROFILE" --attempts 3 \
  --tools '' --output evals/results/change-id/development-treatment
```

Do not use development evidence as holdout evidence. Freeze the treatment
catalog and comparison configuration, record both full revisions, then capture
the two guarded sides:

```sh
python3 evals/run.py \
  --suite routing --mode holdout --condition baseline \
  --model "$MODEL" --profile "$PROFILE" --attempts 3 --tools '' \
  --output evals/results/change-id/holdout-baseline
python3 evals/run.py \
  --suite routing --mode holdout --condition treatment \
  --model "$MODEL" --profile "$PROFILE" --attempts 3 --tools '' \
  --output evals/results/change-id/holdout-treatment
```

Independent and release selection use the same guarded executor:

```sh
python3 evals/run.py \
  --suite see-behavior --mode independent-holdout --condition treatment \
  --model "$MODEL" --profile "$PROFILE" --attempts 3 --tools '' \
  --output evals/results/change-id/independent-treatment
python3 evals/run.py \
  --suite see-behavior --mode release --condition treatment \
  --model "$MODEL" --profile "$PROFILE" --attempts 3 --tools '' \
  --output evals/results/change-id/release-treatment
```

A proposal development baseline is available only through its frozen manifest
entry and pre-treatment catalog:

```sh
python3 evals/run.py \
  --proposal-baseline evals/cases/pilot-routing-development.jsonl \
  --condition baseline --model "$MODEL" --profile "$PROFILE" --attempts 3 \
  --tools '' --output evals/results/pilot/development-baseline
```

For forensic reproduction of historical development evidence, select the
retained side explicitly. The runner fails if the pin cannot be resolved; it
never falls back to the working tree.

```sh
python3 evals/run.py \
  --cases evals/cases/retired-pilot-development.jsonl \
  --allow-historical --historical-catalog baseline --condition baseline \
  --model "$MODEL" --profile "$PROFILE" --attempts 3 --tools '' \
  --output evals/results/forensics/retired-baseline
```

Keep the explicit case path, condition, output manifest, and archived catalog
commit together when reproducing evidence. A changed frozen hash, contract
hash, configuration, or catalog root is a new comparison, not a reproduction.

For behavior cases, baseline disables skills. Treatment exposes only the
canonical target and invokes `/skill:<target>` before the case prompt. Routing
cases expose only their declared confusable candidates. Repository cases copy
an immutable fixture into a temporary worktree. Config overlays passed with
`--config` are included in preflight and each RPC command. Repository verifier
processes default to 30 seconds; change this with `--verifier-timeout`.

A run directory is immutable. Its `manifest.json` records the suite, mode,
condition, suite-manifest and case hashes, case source revision, comparison
contract hash, model, profile, tools, attempts, effective per-attempt and
overall timeouts, redacted effective OMP configuration, and every evaluated or
resolved catalog revision and root. `cases.jsonl` is the exact case snapshot.
Each `artifacts/<case>/<attempt>.json` retains the prompt, sanitized command,
raw output, parsed response, tool trace, model/provider, usage, timing, and
errors. Repository artifacts also retain initial and final trees, their diff,
and verifier evidence.

Use a new output directory for every run and retain failed attempts. Raw
artifacts are excluded from Git; upload complete condition directories to
durable external storage. A published claim requires immutable artifact URI
and hash, retention period, access policy, responsible owner, both condition
directories, deterministic grades, judge evidence when used, and the gate
report. Missing storage, human review, qualified technical attestation, or
credentials are explicit blockers; never synthesize them. Baseline task or
critical failures from completed captures remain comparison evidence, while
infrastructure-failed or missing baseline attempts make the comparison
inconclusive. Required treatment critical failures cannot be averaged away.

The runner removes secret-named environment variables before starting OMP.
Its temporary worktrees and archived catalog roots prevent repository writes
and working-tree catalog fallback, but they are not operating-system
sandboxes. An agent with `read` or `bash` may read outside its worktree. Run
trusted cases only, or use an external sandbox with no host credentials.

## Grade captured artifacts

Grading makes no OMP or model call:

```sh
for run in \
  evals/results/change-id/development-baseline \
  evals/results/change-id/development-treatment \
  evals/results/change-id/holdout-baseline \
  evals/results/change-id/holdout-treatment
do
  python3 evals/grade.py run "$run"
done
```

Each invocation writes `grades.jsonl` and `grade-summary.json`. A single-condition summary always sets `efficacy_claim` to `null`.

## Optional blinded pairwise judgment

Use a judge only for a case's `judge_criteria`, after both conditions have deterministic grades:

```sh
python3 evals/grade.py judge-payload \
  --baseline evals/results/change-id/development-baseline \
  --treatment evals/results/change-id/development-treatment \
  --output evals/results/change-id/development-judge
```

`judge-payloads.jsonl` contains two payloads per judged artifact with opaque candidate IDs and swapped A/B order. `judge-key.json` is separate and must not be shown to the judge. There is no fake judge implementation. Use a different authenticated model family from the evaluated model when one is available. To acquire one real judgment with OMP, place the judge instruction plus one payload in `one-judge-payload.json`, then run:
```sh
omp -p --no-session --mode=json --no-extensions --no-skills --no-tools \
  --model "$JUDGE_MODEL" @one-judge-payload.json
```

Record each real final answer as JSONL with `pair_id`, `winner` (`A`, `B`, or `tie`), `critical_issue`, and `rationale`, then score both orderings:

```sh
python3 evals/grade.py judge-score \
  --key evals/results/change-id/development-judge/judge-key.json \
  --results real-judge-results.jsonl \
  --output evals/results/change-id/development-judge/judge-summary.json
```

Disagreement after order reversal is reported as `position-sensitive`. Judge evidence never replaces deterministic checks.

## Merge gate

```sh
python3 evals/grade.py gate \
  --development-baseline evals/results/change-id/development-baseline \
  --development-treatment evals/results/change-id/development-treatment \
  --holdout-baseline evals/results/change-id/holdout-baseline \
  --holdout-treatment evals/results/change-id/holdout-treatment \
  --routing-holdout-baseline evals/results/change-id/routing-holdout-baseline \
  --routing-holdout-treatment evals/results/change-id/routing-holdout-treatment \
  --output evals/results/change-id/merge-gate.json
```
For SEE behavior runs, add `--case-kind behavior`. This mode also requires every treatment behavior case to pass its deterministic checks.

The gate fails on a critical regression, no deterministic improvement in development, loss of any baseline-passing repository holdout result, any failed routing holdout case, mismatched model/runtime/tool configuration, incomplete pairing, or an unexplained increase in tokens, tool events, or questions. Supply `--correctness-benefit 'observed benefit'` only when raw paired evidence supports the extra cost. Only a passing report contains an efficacy claim; every other report sets it to `null`.

## Verify leancode modes

`mode_smoke.py` drives the real OMP RPC adapter with the production hook. It
checks `lite`, `full`, `ultra`, and `off`, in-process persistence, extension
reload persistence, new-process reset to `full`, quoted-marker preservation,
the requested model identity, and optional same-task behavior.
The artifact binds the OMP executable, version, hook, smoke script, runner,
config overlays, and redacted effective profile configuration:

```sh
python3 evals/mode_smoke.py \
  --model "$MODEL" --profile "$PROFILE" --thinking off \
  --behavior-attempts 1 \
  --output evals/results/change-id/mode-smoke.json
```

