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

## Capture real runs

Use one exact model name and the same OMP profile, config overlays, tool list,
thinking level, and attempt count for both conditions. Use a dedicated,
authenticated profile with no configured MCP servers so profile-level tools
cannot inspect the repository or cases. `--no-tools` disables built-in tools;
the runner also fails a capture when OMP reports a tool outside the explicit
allowlist. Use more than one attempt for a stochastic model. Capture the
baseline before changing skill text; do not recreate or synthesize it from a
treatment run.

The dedicated profile must register this repository root under
`skills.customDirectories`. Before capture, the runner rejects configured MCP
servers and verifies the requested model, thinking level, skills, extensions,
sessions, and tool policy. The manifest records the effective OMP
configuration with secret-bearing values redacted and canonical skill hashes.

Config overlays passed with `--config` are included in the effective-config
preflight and in every RPC command. Repository verifier processes default to a
30-second timeout; change it explicitly with `--verifier-timeout`.

```sh
MODEL='openai-codex/gpt-5.6-sol'
PROFILE='skill-eval-isolated'
python3 evals/run.py \
  --cases evals/cases/behavior.jsonl \
  --cases evals/cases/routing-development.jsonl \
  --condition baseline --model "$MODEL" --profile "$PROFILE" --attempts 3 \
  --tools '' --output evals/results/change-id/development-baseline
python3 evals/run.py \
  --cases evals/cases/routing-holdout.jsonl \
  --condition baseline --model "$MODEL" --profile "$PROFILE" --attempts 3 \
  --tools '' --output evals/results/change-id/holdout-baseline
```

Repository cases require their explicit editing tool allowlist:

```sh
python3 evals/run.py \
  --cases evals/cases/repository-development.jsonl \
  --condition baseline --model "$MODEL" --profile "$PROFILE" --attempts 3 \
  --tools read,bash,edit,write,glob,grep \
  --output evals/results/change-id/repository-development-baseline
python3 evals/run.py \
  --cases evals/cases/repository-holdout.jsonl \
  --condition baseline --model "$MODEL" --profile "$PROFILE" --attempts 3 \
  --tools read,bash,edit,write,glob,grep \
  --output evals/results/change-id/repository-holdout-baseline
```

After the candidate skill changes are frozen, run the treatment from that checkout with the same arguments except the condition and output directory:

```sh
python3 evals/run.py \
  --cases evals/cases/behavior.jsonl \
  --cases evals/cases/routing-development.jsonl \
  --condition treatment --model "$MODEL" --profile "$PROFILE" --attempts 3 \
  --tools '' --output evals/results/change-id/development-treatment
python3 evals/run.py \
  --cases evals/cases/routing-holdout.jsonl \
  --condition treatment --model "$MODEL" --profile "$PROFILE" --attempts 3 \
  --tools '' --output evals/results/change-id/holdout-treatment
```

Repeat the repository commands with `--condition treatment` and new output
directories. Never reuse a run directory.

For behavior cases, both arms use the same minimal structured-response system
prompt and disable discovered rules, extensions, sessions, and tools. Baseline
disables skills. Treatment exposes only the canonical target and sends
`/skill:<target>` as one RPC prompt before the case prompt in the same session.
For routing cases, both arms use a dedicated classification prompt and expose only the declared confusable pair through `--skills`. The runner places those two frontmatter descriptions in the case prompt and verifies them against OMP's runtime command catalog. Each case declares which candidate skill is under evaluation. A paired comparison fails when no declared evaluated skill differs between conditions, or when any undeclared skill differs. The repository hook and always-active configuration remain disabled in both conditions.

A run directory is immutable and contains:

- `manifest.json`: condition, timestamp, exact model request, OMP executable and version, repository status, skill commits and content hashes, evaluator hashes, case and config hashes, redacted effective OMP configuration, tool allowlist, and runtime flags.
- `cases.jsonl`: the exact case snapshot used by the run.
- `artifacts/<case>/<attempt>.json`: prompt, sanitized argv, raw stdout and stderr, exit code, parsed response, tool policy and trace, observed model and provider, usage, timing, and parse errors. Repository artifacts also retain the initial and final file snapshots, unified diff, verifier command, raw verifier output, and individual deterministic check results. These raw files can be hundreds of megabytes.

Use a new output directory for every run. Preserve every attempt, including
failed and invalid captures. Raw `artifacts/` directories are excluded from Git
by `.gitignore`; keep them locally or upload the complete run directories to
external artifact storage. Commit the compact manifests, case snapshots,
grades, judge outputs, and release reports. Grade summaries contain the raw
artifact hashes for completed graded runs and can verify a restored bundle.
Preserve complete run directories for captures that were not graded.

A published efficacy claim must retain both complete condition directories,
raw artifacts, deterministic grades, and the gate report in durable artifact
storage. Credentials must never be put in prompts, config overlays, or
artifacts.

The runner removes secret-named environment variables before it starts OMP.
It isolates repository writes in a temporary worktree, but it is not an
operating-system sandbox: an agent with `read` or `bash` can read outside that
worktree. Run repository cases only with trusted fixtures and prompts, or run
the entire evaluator in an external sandbox that contains no host credentials.

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

