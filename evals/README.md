# Behavior and routing evaluation

This evaluation uses OMP's real noninteractive adapter. `run.py` invokes `omp --mode=rpc`, sends JSONL requests on stdin, captures the complete JSONL event stream and stderr, and extracts the final assistant response, tool events, model, usage, and runtime fields. It does not call a model provider directly.

## Cases

- `cases/behavior.jsonl` contains eight development cases for `leancode` behavior.
- `cases/routing-development.jsonl` contains two known cases for each confusable pair, one for each skill.
- `cases/routing-holdout.jsonl` contains two different held-out cases for each pair. Do not use holdout results to tune a change.

Every case names observable success, prohibited outcomes, and deterministic checks. Behavior prompts request an explicit decision record because these cases measure change scope and verification choices without modifying this repository. Routing requests append both exact candidate names and their captured frontmatter descriptions, then require one exact selection.

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
`skills.customDirectories`. The manifest records the effective OMP
configuration and canonical skill hashes.

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

For behavior cases, both arms use the same minimal structured-response system
prompt and disable discovered rules, extensions, sessions, and tools. Baseline
disables skills. Treatment exposes only the canonical target and sends
`/skill:<target>` as one RPC prompt before the case prompt in the same session.
For routing cases, both arms preserve OMP's default skill-discovery prompt and
expose the complete canonical repository skill catalog through one `--skills`
filter. The runner places the two candidate frontmatter descriptions in the
case prompt and verifies them against OMP's runtime command catalog. The
repository commit and canonical content hashes distinguish a pre-change
baseline from a post-change treatment. The repository hook and always-active
configuration remain disabled in both conditions.

A run directory is immutable and contains:

- `manifest.json`: condition, timestamp, exact model request, OMP executable and version, repository status, skill commits and content hashes, evaluator hashes, case and config hashes, effective OMP configuration, tool allowlist, and runtime flags.
- `cases.jsonl`: the exact case snapshot used by the run.
- `artifacts/<case>/<attempt>.json`: prompt, sanitized argv, raw stdout and stderr, exit code, parsed response, tool policy and trace, observed model and provider, usage, timing, and parse errors.

Use a new output directory for every run. Preserve all attempts, including failures. A published claim must commit or otherwise retain both condition directories, their raw artifacts, deterministic grades, and the gate report. Credentials must never be put in prompts, config overlays, or artifacts.

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

`judge-payloads.jsonl` contains two payloads per judged artifact with opaque candidate IDs and swapped A/B order. `judge-key.json` is separate and must not be shown to the judge. There is no fake judge implementation. To acquire one real judgment with OMP, place the judge instruction plus one payload in `one-judge-payload.json`, then run:

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
  --output evals/results/change-id/merge-gate.json
```

The gate fails on a critical regression, no deterministic improvement in development, a holdout routing regression, mismatched model/runtime/tool configuration, incomplete pairing, or an unexplained increase in tokens, tool events, or questions. Supply `--correctness-benefit 'observed benefit'` only when raw paired evidence supports the extra cost. Only a passing report contains an efficacy claim; every other report sets it to `null`.

