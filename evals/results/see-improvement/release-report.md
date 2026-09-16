# SEE Improvement Release Report

## Decision

**INCONCLUSIVE.** The V24 automated gate passes for the locally captured evaluated configuration, but required evidence is missing. Under the evidence policy, missing required review, immutable-root, comparison-contract, timeout, or durable-artifact evidence cannot produce either `GO` or `NO-GO`. Do not claim release readiness, SEE conformance, general efficacy, or qualified approval.

- Overall decision: `release-gate-final.json`
- Automated gate: `remediation-v24-gate.json` (`pass`, supporting evidence only)
- Failed substantive gates: none established from complete evidence
- Incomplete gates: immutable evaluated catalogs, frozen comparison contract, timeout equality, human calibration and adjudication, technical attestation, and durable external storage
- Overall `efficacy_claim`: `null`

## Evaluated Configuration and Missing Identity Evidence

The local manifests record:

- Model: `openai-codex/gpt-5.6-sol`
- OMP: `omp/18.1.17`
- Profile: `skill-eval-isolated`
- Thinking: `off`
- Attempts: 3 per case
- Tools: none
- Behavior per-attempt timeout: 10 minutes
- Routing per-attempt timeout: 2 minutes
- Candidate `simplified-engineering-english/SKILL.md` SHA-256: `256976f959ac379e0080835f7b6f5201908b722dbab4384d0e32cc12e31e20a8`
- Runner `evals/run.py` SHA-256: `be310d7d73869c11412724d66d66105850b22cd3210e4c753f1cbc4aa443cca0`
- Grader `evals/grade.py` SHA-256: `21f818a084b4aecf52a6980f15558b2424bcedc640fb6b59647804d3a5fb0cc8`
- Independent holdout SHA-256: `c69cf79fc08fe1e97cad6fa35f5759ea8df53362b0e2eb83ea3cc6f001907842`

Required comparison identity fields remain unavailable:

| Field | Baseline | Treatment | Status |
| --- | --- | --- | --- |
| Evaluated catalog revision | unavailable | unavailable | incomplete |
| Resolved evaluated root | unavailable | unavailable | incomplete |
| Comparison-contract path and SHA-256 | unavailable | unavailable | incomplete |
| Effective overall timeout | unavailable | unavailable | incomplete |
| Timeout equality | — | — | unverified |
| Immutable artifact URI and hash | unavailable | unavailable | incomplete |
| Artifact access policy | unavailable | unavailable | incomplete |
| Artifact retention period | unavailable | unavailable | incomplete |
| Responsible owner | unavailable | unavailable | incomplete |

The repository freeze records bind the candidate and case hashes shown above. They do not supply the immutable evaluated baseline and treatment revisions and roots, the pre-registered comparison-contract identity, or the durable artifact metadata required for release evidence.

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

`remediation-v24-gate.json` passes its legacy automated criteria: known cost metrics, development improvement, preserved holdout passes, measured correctness benefit for increased behavior cost, no critical deterministic regressions, and complete routing holdout passage. This is a local automated observation only. The accepted run metadata does not establish the immutable evaluated roots, registered comparison contract, effective overall timeouts and equality, or durable artifacts needed to reproduce a release comparison.

The independent Anthropic Claude Sonnet 4.6 judge ran through the `work` profile with thinking off and no tools. It returned valid results for all 156 blinded payloads: 84 development payloads and 72 holdout payloads. Capture cost was $3.10253265.

| Split | Baseline | Treatment | Tie | Position-sensitive | Critical-flagged |
| --- | ---: | ---: | ---: | ---: | ---: |
| Development | 11 | 3 | 9 | 19 | 5 |
| Holdout | 3 | 1 | 21 | 11 | 1 |

The judge is supporting evidence only. Thirty of 78 swapped pairs were position-sensitive. Six pairs contained a critical-issue flag; the pair-level flag does not identify the affected condition, and several rationales conflict across orderings. Human calibration and adjudication remain required.

The overall decision remains `INCONCLUSIVE` because:

1. The accepted results do not identify immutable baseline and treatment catalog revisions and resolved roots.
2. No pre-registered comparison-contract path and content hash are recorded for this comparison.
3. The legacy manifests record per-attempt limits but not effective overall timeouts or an explicit baseline/treatment timeout-equality result.
4. The 26-pair, seven-dimension human calibration packet has no reviewer, qualifications, scores, confidence, comments, or locked adjudications.
5. The technical attestation has no named qualified authority, qualification basis, assessments, decision, or signature.
6. Raw artifacts are local and Git-ignored; immutable baseline and treatment URIs and hashes, access policy, retention period, and responsible owner are unavailable.

These are incomplete gates, not established failed substantive gates. The automated pass cannot replace them.

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

The following local run directories supplied the automated summaries:

- `remediation-v24-development-behavior-baseline`
- `remediation-v24b-development-behavior-treatment`
- `remediation-v23-independent-behavior-baseline`
- `remediation-v23-independent-behavior-treatment`
- `remediation-v19-development-routing-baseline`
- `remediation-v23-development-routing-treatment`
- `remediation-v19-independent-routing-baseline`
- `remediation-v23-independent-routing-treatment`

Compact repository evidence:

- `paired-results.json`
- `remediation-v24-gate.json`
- `release-gate-final.json`
- `remediation-freeze-v24.json`
- `remediation-holdout-freeze-v24.json`
- `remediation-v24-human-calibration-packet.json` and restricted key
- `remediation-v24-technical-attestation.json`
- `remediation-v24-model-judge-analysis.json`
- `evidence-manifest.json`

The raw `artifacts/` directories are local and excluded by `.gitignore`. They are not durable publication storage and no release claim in this report relies on their continued availability.

The release decision can be regenerated only after all of these external inputs are supplied:

1. immutable baseline and treatment catalog revisions plus their resolved roots;
2. the frozen comparison-contract path and SHA-256;
3. baseline and treatment effective per-attempt and overall timeouts plus an explicit equality result;
4. complete baseline and treatment artifact sets in durable storage, each with an immutable URI and content hash;
5. the storage access policy, retention period, and responsible owner;
6. completed qualified human calibration and locked dispositions for all position-sensitive and critical-flagged pairs; and
7. a completed attestation from a named qualified technical authority.

## Supported and Unsupported Claims

Supported automated observation: in the local captures for the stated configuration, deterministic behavior changed from 29/42 to 42/42 on development and from 24/36 to 36/36 on holdout; routing stayed at 30/30 and 36/36; no deterministic critical regression was recorded.

This observation is not a release or efficacy claim because the required immutable and durable evidence is incomplete. Unsupported: release readiness, SEE conformance, human-calibrated semantic superiority, qualified technical approval, cost reduction, published efficacy, and generalization to other models, profiles, prompts, repositories, or production traffic.

## Rollback

Prior rollback inputs:

- Repository commit: `a2384f71dc317446706c66799d26e15e6b18836a`
- Prior skill SHA-256: `8016301f988af5b7a27d1219e819bdc64d9e9d7818880260d5958d7369693b56`
- Prior dictionary SHA-256: `965dd00aacb08ee95dd63a9a59a1ccdd4f8aed68c11c98ae3ab4dc5a54345fed`

Restore the prior skill and dictionary together. Preserve the rejected evidence and final manifests so the decision remains reproducible.
