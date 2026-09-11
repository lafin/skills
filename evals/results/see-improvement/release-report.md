# SEE Improvement Release Report

## Decision

**NO-GO.** The V24 automated gate passes for the evaluated configuration, but publication and release remain blocked. Do not claim release readiness, SEE conformance, general efficacy, or qualified approval.

- Overall decision: `release-gate-final.json`
- Automated gate: `remediation-v24-gate.json`
- Overall `efficacy_claim`: `null`

## Evaluated Configuration

- Model: `openai-codex/gpt-5.6-sol`
- OMP: `omp/18.1.17`
- Profile: `skill-eval-isolated`
- Thinking: `off`
- Attempts: 3 per case
- Tools: none
- Behavior timeout: 10 minutes
- Routing timeout: 2 minutes
- Candidate `simplified-engineering-english/SKILL.md` SHA-256: `256976f959ac379e0080835f7b6f5201908b722dbab4384d0e32cc12e31e20a8`
- Runner `evals/run.py` SHA-256: `be310d7d73869c11412724d66d66105850b22cd3210e4c753f1cbc4aa443cca0`
- Grader `evals/grade.py` SHA-256: `21f818a084b4aecf52a6980f15558b2424bcedc640fb6b59647804d3a5fb0cc8`
- Independent holdout SHA-256: `c69cf79fc08fe1e97cad6fa35f5759ea8df53362b0e2eb83ea3cc6f001907842`

The treatment manifests bind the candidate hash above. The independent V21 holdout was authored and audited without access to the candidate, prior evidence, responses, or this remediation history; its final response-blind audit was `GO`.

## Paired Results

| Corpus | Baseline | Treatment | Token delta | Cost delta | Runtime delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| Behavior development | 29/42 | 42/42 | +232,337 | +$0.278644 | +198.592 s |
| Behavior holdout | 24/36 | 36/36 | +200,547 | +$0.2945752 | +206.453 s |
| Routing development | 30/30 | 30/30 | -330 | -$0.0013200 | -3.200 s |
| Routing holdout | 36/36 | 36/36 | -396 | -$0.0015840 | +9.378 s |

Every arm recorded zero tool calls, zero questions, and zero invalid or incomplete responses. OMP reports aggregate uncached input and cache-read tokens, not the target skill's input-token share.

## Corrected Regressions

The final candidate and evaluator cover these observed failure classes:

- preserve exact quotations, output tokens, and protected technical spans in rewritten content;
- distinguish actual source ambiguity from absent unstated details and omitted imperative subjects;
- keep recovery controls before destructive actions without inventing recovery for observation-only prose;
- retain redaction boundaries without requiring values that must be removed;
- preserve obligation boundaries and force, named audiences, organizations, product scope, deployment scope, and environment scope;
- accept faithful terminology-drift explanations without requiring one exact paraphrase;
- validate each routing artifact against its own frozen prompt when paired skill descriptions differ.

`expected_obligation_force` remains semantic judge criteria. Generating an exact lexical check would reject faithful paraphrases and create a second prose convention; deterministic checks instead enforce exact values, protected spans, fields, cardinality, unambiguous order, redaction literals, and no-op equality.

## Gate Interpretation

`remediation-v24-gate.json` passes all automated criteria: known cost metrics, development improvement, preserved holdout passes, measured correctness benefit for increased behavior cost, no critical deterministic regressions, and complete routing holdout passage. Its claim applies only to the evaluated model, OMP version, profile, prompts, cases, and three-attempt configuration.

The independent Anthropic Claude Sonnet 4.6 judge ran through the `work` profile with thinking off and no tools. It returned valid results for all 156 blinded payloads: 84 development payloads and 72 holdout payloads. Capture cost was $3.10253265.

| Split | Baseline | Treatment | Tie | Position-sensitive | Critical-flagged |
| --- | ---: | ---: | ---: | ---: | ---: |
| Development | 11 | 3 | 9 | 19 | 5 |
| Holdout | 3 | 1 | 21 | 11 | 1 |

The judge is supporting evidence only. Thirty of 78 swapped pairs were position-sensitive. Six pairs contained a critical-issue flag; the pair-level flag does not identify the affected condition, and several rationales conflict across orderings. Human calibration and adjudication remain required.

The overall decision remains `NO-GO` because:

1. The 26-pair, seven-dimension human calibration packet has no reviewer or scores, and the model-judge disagreements have not been adjudicated.
2. The technical attestation has no named qualified authority or assessments.
3. Raw artifacts are local and Git-ignored; no durable external artifact store is configured.

## Iteration Disposition

- V1-V17: rejected or audit-only development evidence; not final release evidence.
- V18: rejected after holdout exposed invented ambiguity findings and protected alternatives moved out of rewritten content.
- V19: rejected because the first correction over-suppressed genuine vague source terms; its holdout also used exact-prose checks that rejected faithful paraphrases.
- V20-V22: rejected or smoke-only evidence; V22 included a command-order oracle false positive.
- V23: candidate and independent holdout were retained, but the development oracle rejected a faithful `synonyms`/`different` explanation; V24 broadens only that development oracle.
- `remediation-v24-development-behavior-treatment`: rejected capture because one infrastructure terminal artifact was incomplete.
- `remediation-v24b-development-behavior-treatment`: accepted replacement capture, 42/42.

Rejected runs remain separate for auditability. They were not substituted into final scores.

## Evidence and Reproduction

Accepted run directories:

- `remediation-v24-development-behavior-baseline`
- `remediation-v24b-development-behavior-treatment`
- `remediation-v23-independent-behavior-baseline`
- `remediation-v23-independent-behavior-treatment`
- `remediation-v19-development-routing-baseline`
- `remediation-v23-development-routing-treatment`
- `remediation-v19-independent-routing-baseline`
- `remediation-v23-independent-routing-treatment`

Compact evidence:

- `paired-results.json`
- `remediation-v24-gate.json`
- `release-gate-final.json`
- `remediation-freeze-v24.json`
- `remediation-holdout-freeze-v24.json`
- `remediation-v24-human-calibration-packet.json` and restricted key
- `remediation-v24-technical-attestation.json`
- `remediation-v24-development-judge/` and `remediation-v24-holdout-judge/`
- `remediation-v24-model-judge-analysis.json`
- `evidence-manifest.json`

Runnable repository checks:

```sh
python3 scripts/validate_skills.py
PYTHONPATH=. python3 -m unittest discover -s tests -p test_evaluation_harness.py
python3 -m evals.grade --help
```

Raw manifests, prompts, responses, usage, runtimes, grader evidence, and hashes are retained under each accepted run directory. The raw `artifacts/` directories are local and excluded by `.gitignore`. This is not durable publication storage.

## Supported and Unsupported Claims

Supported: for the exact evaluated configuration, deterministic behavior improved from 29/42 to 42/42 on development and from 24/36 to 36/36 on the independently frozen holdout; routing stayed at 30/30 and 36/36; no deterministic critical regression was observed.

Unsupported: release readiness, SEE conformance, human-calibrated semantic superiority, qualified technical approval, cost reduction, published efficacy, and generalization to other models, profiles, prompts, repositories, or production traffic.

## Rollback

Prior rollback inputs:

- Repository commit: `a2384f71dc317446706c66799d26e15e6b18836a`
- Prior skill SHA-256: `8016301f988af5b7a27d1219e819bdc64d9e9d7818880260d5958d7369693b56`
- Prior dictionary SHA-256: `965dd00aacb08ee95dd63a9a59a1ccdd4f8aed68c11c98ae3ab4dc5a54345fed`

Restore the prior skill and dictionary together. Preserve the rejected evidence and final manifests so the decision remains reproducible.
