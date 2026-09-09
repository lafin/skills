---
name: self-improvement-loops
description: "This skill should be used when the harness, scaffold, workflow, or optimizer itself is the optimization target: recursive self-improvement (RSI) loops, meta-harnesses, self-improving harnesses that mine their own failures and propose bounded edits, evolutionary or population-based search over agent scaffolds, acceptance gates for self-modifying systems, and agentic context evolution where the mechanism that produces context is versioned and evolved. Route governance of a single autonomous loop (locked surfaces, durable logs, rollback, novelty gates, approval boundaries) to harness-engineering, measurement and quality-gate design to evaluation, judge design to advanced-evaluation, and remote sandbox infrastructure to hosted-agents."
license: MIT
metadata:
  upstream: "muratcankoylan/Agent-Skills-for-Context-Engineering"
  upstream_commit: "c578e85e40fe2bda7c1fec91ff64cf5285434934"
  upstream_path: "skills/self-improvement-loops"
  adaptation: modified
  license_notice: LICENSE-context-engineering
---

# Self-Improvement Loops

This skill covers systems where the harness is the artifact being optimized: an agent mines its own failures and edits its own scaffold, a meta-agent searches over harness code, a population of workflow candidates evolves against an evaluator, or the mechanism that produces context is itself versioned and improved. The design question shifts from "how do I control one loop" (harness-engineering) to "how do I let a loop rewrite parts of itself without corrupting the signal that steers it".

A recurring constraint in the reviewed systems is that the loop optimizes its given signal, including weaknesses in that signal. Design the loop to resist gaps between the metric and the intent. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-anchor-survey)

## When to Activate

Activate this skill when:

- Building a loop where an agent proposes edits to its own harness, prompts, context playbook, or workflow based on mined failure patterns
- Designing meta-level search over harness or scaffold code: meta-agent search, tree search over workflow graphs, evolutionary program search with an LLM mutation operator
- Choosing acceptance criteria for any self-modifying agent system
- Evolving the mechanism that manages context (a skill, playbook, or context function) rather than hand-editing the context artifact
- Diagnosing a degenerating self-improvement loop: reward hacking, diversity collapse, context collapse, or silent stagnation
- Deciding which level of the optimization ladder (prompt, context, workflow, harness code, optimizer code) a recurring failure should be fixed at

Do not activate this skill for adjacent work owned by other skills:

- Governance of a single autonomous loop that does not modify itself: locked and editable surfaces, durable logs, rollback, novelty gates, PR preparation, and human approval boundaries belong to `harness-engineering`. That skill defines the control surfaces; this skill defines what happens when the surfaces themselves become the optimization target.
- Building the evaluator, regression suite, or quality gates that score candidates: `evaluation`.
- LLM-as-judge design, pairwise comparison, and bias mitigation for candidate scoring: `advanced-evaluation`.
- One-shot token efficiency, masking, or caching without an improvement loop: `context-optimization`.
- Remote sandboxes and background execution infrastructure for running the loop: `hosted-agents`.
- Whether to build the loop at all, pipeline shape, and cost estimation: `project-development`.

## Core Concepts

### The Optimization Ladder

The systems reviewed on 2026-07-08 target progressively deeper objects. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-anchor-survey)

| Rung | Optimized object | Example systems |
| --- | --- | --- |
| 1 | Instruction prompts | Promptbreeder, GEPA |
| 2 | Structured context | ACE (playbook of itemized bullets) |
| 3 | Context mechanism | MCE (the skill that produces context) |
| 4 | Workflow graph | ADAS, AFlow |
| 5 | Harness code | Self-Harness (bounded self-edits), Meta-Harness, Darwin Godel Machine |
| 6 | Optimizer code | STOP (the improver improves the improver) |

Each higher rung expands the design space and the surface for evaluator gaming. Fix a recurring failure at the lowest rung that can express the fix. A stale-library failure is a context fix, not a workflow rewrite. Only move up when failure clusters at the current rung persist across candidates. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-anchor-survey)

### The Loop Is Not the Intelligence

In the STOP study, recursive optimizer edits improved mean downstream performance with GPT-4 but degraded it with GPT-3.5-turbo and Mixtral. The study does not establish a general model-capability threshold. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-stop-capability-threshold) Two implications:

1. Run a capability validation before enabling recursion: a fixed number of iterations on a held-out task set, with the loop counted as net-negative if the trajectory declines.
2. Detect the degenerate stagnation mode. A broken improver that silently returns its input unchanged looks like stability in aggregate metrics. Track edit diffs, not only scores.

### The Outside-the-Loop Invariant

Keep the evaluator, its instrumentation, permission control, and budget enforcement outside the surface the loop can modify. In reviewed incidents, agents removed detector markers when checking code was visible and modified exposed scoring functions. [DGM evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-darwin-godel-machine-objective-hacking) [METR evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-metr-scorer-visibility)

Operational rules:

- The STOP study reports prompt-stated budget constraints being removed during self-rewrites. Enforce budgets, permissions, and sandbox boundaries in the runtime, never in the mutable prompt or harness code. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-stop-capability-threshold)
- Hide the scoring implementation from the proposer. Expose scores and traces, not evaluator source.
- Sandbox at the OS or container level. Do not rely on permission gates within mutable harness code. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-darwin-godel-machine-objective-hacking)
- Treat any detected exploit as a failed candidate, not a high score, or the hack inflates the very metric steering the loop.

### Empirical Acceptance, Never Rationale

Accept a self-modification only on measured evidence, using two splits: a held-in split that checks the targeted weakness and a held-out split the proposer never sees. The reviewed Self-Harness gate accepts only when neither split regresses and at least one strictly improves under repeated evaluation. It reported held-out gains for all three tested base models on its fixed benchmark subset. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-self-harness-bounded-self-edits) Reject candidates that trade one split against the other even when the sum improves. Log rejected candidates with their evidence so the proposer stops rediscovering them.

### Filesystem Experience Archive

Store every candidate as a directory containing its source, scores, and raw execution traces. Let the proposer navigate the archive with search tools instead of stuffing history into its context window. In the Meta-Harness ablation, full raw-trace access outperformed scores-only feedback and scores plus LLM-written summaries on the tested text-classification suite. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-meta-harness-search) Do not pre-summarize the archive. Curate access paths, not content.

### Diversity Preservation

The reviewed evolutionary systems use several diversity mechanisms, with results tied to their specific tasks and evaluators. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-evolutionary-harness-search)

- Keep an archive of every candidate that retains core capability. Archived variants can provide later stepping stones.
- Discount fitness pressure by offspring count so heavily-mined candidates lose priority while every archive member keeps nonzero selection probability.
- Reject near-duplicate proposals by embedding similarity before paying evaluation cost.
- Keep a route back to the seed or blank candidate in the selection distribution as an escape from local optima.

## Detailed Topics

### Anatomy of a Failure-Driven Self-Edit Loop

The reviewed Self-Harness method has three stages. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-self-harness-bounded-self-edits)

1. **Weakness mining.** Cluster failed traces by a three-part signature: verifier-level cause, causal status of the agent behavior, and the abstract mechanism exposed by the trace. Never cluster on error strings alone; a timeout is a symptom shared by unrelated mechanisms. Apply an addressability filter to exclude clusters that reflect task difficulty or capability limits rather than harness defects. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-self-harness-bounded-self-edits)
2. **Bounded proposal.** Give the proposer the four inputs used by Self-Harness: editable surfaces, mined failure patterns, passing behaviors to preserve, and summaries of prior edit attempts. Require proposals to touch one surface, differ across parallel candidates, and record the targeted pattern, expected effect, and regression risks. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-self-harness-bounded-self-edits)
3. **Validation and merge.** Apply the two-split acceptance gate. Merge compatible accepted edits and log rejected ones without changing the active harness. Record changed surfaces, split outcomes, and the decision for every transition. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-self-harness-bounded-self-edits)

### Meta-Level Search over Harness Code

When searching whole harness programs from outside rather than editing a running harness from inside:

- Keep the outer loop minimal: no hand-tuned mutation operators or parent-selection heuristics. Delegate diagnosis and edit decisions to a coding-agent proposer. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-meta-harness-search)
- Initialize from a strong available harness, not from scratch. The reviewed Meta-Harness winner added an environment-bootstrap snapshot to its seed harness. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-meta-harness-search)
- Maintain a Pareto frontier over the objectives that actually matter (accuracy, context cost, latency) rather than collapsing to one scalar.
- Structure search memory per candidate with recorded modification outcomes. In the reviewed AFlow comparison, per-node experience records outperformed archive-in-context conditioning across six benchmarks. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-evolutionary-harness-search)
- Re-run the search when the executor model changes. The reviewed AFlow workflows degraded when transferred to another executor. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-evolutionary-harness-search)

### Context Evolution as Self-Improvement

Context playbooks that update themselves have two relevant failure modes. Brevity bias removes domain-specific heuristics in favor of short generic instructions. In the reviewed AppWorld case study, a monolithic rewrite collapsed context and reduced accuracy below the no-adaptation baseline. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-context-evolution) Use this pattern:

- Represent context as itemized entries with stable identifiers and helpful/harmful counters.
- Produce incremental deltas, merged by deterministic non-model logic. The curator never rewrites the whole artifact.
- Deduplicate by embedding similarity, periodically or lazily.
- Gate the whole mechanism on feedback quality. The reviewed ACE study reports degradation below the static baseline without reliable execution signals or labels. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-context-evolution)

One level up, version the mechanism that produces context separately from the produced context. Evolve the mechanism against a validation split and warm-start from the prior best artifact plus its rollout results. Check the train-validation gap each iteration to catch mechanism overfitting. The reviewed evidence limits this approach to settings with useful feedback and reports setting-dependent results. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-context-evolution)

### What Belongs to Humans

Humans move up the stack rather than out of the loop. Reserve for human decision points: changes to the evaluator or acceptance gate, expansion of editable surfaces, promotion of a discovered harness to production, and abandonment decisions for research directions. The reviewed survey argues that training data underrepresents failed directions and that preserving negative results can reduce repeated search. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-anchor-survey) Make failed candidates first-class artifacts.

## Practical Guidance

### Loop-Readiness Checklist

Do not enable self-modification until every item holds:

1. A fast, deterministic, automatable evaluator exists.
2. A held-out split exists that the proposer never sees, refreshed if the loop runs long enough to overfit it.
3. Budgets, permissions, and sandboxing are enforced by the runtime, outside every editable surface.
4. Editable surfaces are explicitly declared (marked regions or configuration points); everything else is locked, and immutability is programmatically re-verified after each candidate.
5. An archive with full lineage of diffs exists; audits read diffs and raw traces, not the fitness signal.
6. Evaluation spending is staged: cheap interface or smoke checks before full evaluation, repeated runs where scoring is noisy.
7. A task-specific capability validation run does not show a declining improvement trajectory.
8. Human decision points are wired for evaluator changes, surface expansion, and promotion.

### Choosing the Loop Level

| Recurring failure | Fix at | Loop pattern |
| --- | --- | --- |
| Missing domain heuristics, repeated known mistakes | Structured context | Itemized playbook with delta updates |
| Context playbook itself plateaus across tasks | Context mechanism | Evolve the skill on validation data |
| Wrong sequencing, missing verification steps | Workflow | Search over workflow graphs with per-node experience |
| Failure clusters persist across workflow candidates | Harness code | Failure-driven bounded self-edits or meta-level search |
| Improvement strategy itself is weak | Optimizer code | Only with strong models and locked meta-evaluation |

## Examples

**Example 1: Two-split acceptance gate**

```python
def accept(candidate, baseline, held_in, held_out, repeats=3):
    d_in = mean_score(candidate, held_in, repeats) - mean_score(baseline, held_in, repeats)
    d_out = mean_score(candidate, held_out, repeats) - mean_score(baseline, held_out, repeats)
    if d_in < 0 or d_out < 0:
        return False              # no regression on either split
    return max(d_in, d_out) > 0  # strict improvement on at least one
```

The held-out split is invisible to the proposer. A candidate that gains on held-in by sacrificing held-out is rejected even if the sum is positive.

**Example 2: Experience archive layout**

```text
search-run/
  candidates/
    c0041/
      harness.py          # full candidate source
      scores.json          # per-split, per-repeat results
      traces/              # raw prompts, tool calls, outputs, state updates
      lineage.txt          # parent id, diff summary, decision, evidence
  frontier.json            # current Pareto set over (quality, cost)
  rejected.jsonl           # rejected candidates with reasons, append-only
```

The proposer greps this tree selectively. Nothing is summarized into its prompt by default.

**Example 3: Routing a failure to the right rung**

```text
Observed: agent repeatedly uses a deprecated API despite instructions.
Wrong fix: propose a harness-code edit adding retry logic.
Right fix: rung 2. Inject current API docs into task context at
execution time. Training-data defaults override prompt instructions,
so ground the context; do not add machinery.
```

## Guidelines

1. Enforce every constraint in the runtime; treat prompt-stated constraints as decorative.
2. Keep evaluator source, instrumentation, and permission checks invisible to and unmodifiable by the loop.
3. Gate acceptance on held-in plus held-out no-regression with repeated evaluation; never accept on the proposer's rationale.
4. Declare editable surfaces explicitly and re-verify locked regions after every candidate.
5. Archive all viable candidates with raw traces; select parents with offspring-count discounting.
6. Reject near-duplicates by embedding similarity before spending evaluation budget.
7. Evaluate from raw logs and original outputs, never from model-written reports of them.
8. Count detected evaluator exploits as failures and audit lineage diffs, not scores.
9. Fix failures at the lowest ladder rung that expresses the fix.
10. Re-search when the executor model or the seed harness changes materially.
11. Verify the task-specific capability-validation trajectory before enabling recursion.
12. Keep evaluator changes, surface expansion, and production promotion as human decisions.

## Gotchas

1. **Prompt constraints evolve away**: STOP generated self-rewrites that dropped budget constraints, and a warning did not reduce reported sandbox-disabling code. Put enforcement in the runtime. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-stop-capability-threshold)
2. **Visible scorers get gamed**: DGM and METR report detector disabling, timing overwrites, or evaluator modification when checking code was visible. Expose scores and traces, never evaluator internals. [DGM evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-darwin-godel-machine-objective-hacking) [METR evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-metr-scorer-visibility)
3. **Self-reported success**: A reviewed autonomous-research study reports success declarations based on model-written reports instead of raw logs. Bind every reported number to a raw artifact at write time. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-reward-hacking-and-oversight)
4. **Monolithic rewrite collapse**: In one AppWorld case study, a whole-playbook rewrite reduced context from 18,282 tokens to 122 and accuracy from 66.7 to 57.1, below the 63.7 no-adaptation baseline. Update by itemized deltas with deterministic merge. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-context-evolution)
5. **Hill-climbing the latest candidate**: Discarding the archive removes alternative parents, and reported DGM ablations were worse without the archive. Keep viable candidates available for selection. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-darwin-godel-machine-objective-hacking)
6. **Stagnation disguised as stability**: STOP produced degenerate improvers that returned their input unchanged. Alarm on empty or trivial diffs, not only score drops. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-stop-capability-threshold)
7. **Same-agent proposal and approval**: The reviewed Self-Harness design uses the same agent as proposer and approver. Put independent review outside the loop for higher-stakes changes. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-self-harness-bounded-self-edits)
8. **Benchmark-shaped improvements**: Self-Harness reports model-specific edits on a fixed benchmark subset, and Meta-Harness searches and evaluates on the same benchmark. Validate on a distribution shift before promotion. [Self-Harness evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-self-harness-bounded-self-edits) [Meta-Harness evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-meta-harness-search)
9. **Cross-stage score cherry-picking**: The ScientistOne paper reports writeup stages selecting favorable intermediate scores instead of the shipped artifact's score. Bind scores to submitted candidates deterministically. [Evidence](skill://self-improvement-loops/references/loop-design-evidence.md#evidence-reviewed-2026-07-08-reward-hacking-and-oversight)

## Integration

This skill connects to:

- harness-engineering - Owns the control surfaces (locked, editable, append-only, human) that this skill's loops operate within; every self-improvement loop presupposes that boundary design
- evaluation - Owns the deterministic evaluators, regression suites, and quality gates that serve as the locked fitness signal
- advanced-evaluation - Owns judge design and bias mitigation when candidate scoring requires model judgment
- filesystem-context - Owns the durable file layout patterns the experience archive builds on
- multi-agent-patterns - Parallel candidate evaluation and proposer-verifier separation are multi-agent topologies
- hosted-agents - Owns the sandboxed execution infrastructure that enforces the runtime boundary
- context-optimization - Owns one-shot context efficiency; this skill owns the loop that evolves context mechanisms over time

## References

Internal reference:
- [Loop design evidence](skill://self-improvement-loops/references/loop-design-evidence.md) - Dated per-system results, acceptance-rule details, ablation findings, and documented reward-hacking incidents backing this skill

Related skills in this collection:
- harness-engineering - Single-loop governance and control surfaces
- evaluation - Evaluator and quality-gate construction

External resources:
- Weng, "Harness Engineering for Self-Improvement" (Lil'Log, 2026) - Survey and framing of the optimization ladder and RSI challenges
- Zhang et al., "Self-Harness: Harnesses That Improve Themselves" (arXiv 2606.09498) - Failure-driven bounded self-edits with two-split acceptance
- Lee et al., "Meta-Harness: End-to-End Optimization of Model Harnesses" (arXiv 2603.28052) - Filesystem experience store and coding-agent proposer
- Ye et al., "Meta Context Engineering via Agentic Skill Evolution" (arXiv 2601.21557) - Mechanism-versus-artifact separation in context evolution
- Zhang et al., "Agentic Context Engineering" (arXiv 2510.04618) - Itemized deltas, deterministic merge, context collapse
- Zhang et al., "Darwin Godel Machine" (arXiv 2505.22954) - Archive-based harness evolution and documented objective hacking
- Zelikman et al., "Self-Taught Optimizer" (arXiv 2310.02304) - Recursive improver and the capability-threshold negative result
- Novikov et al., "AlphaEvolve" (arXiv 2506.13131) - Bounded mutation markers and evaluation cascades
- Lange et al., "ShinkaEvolve" (arXiv 2509.19349) - Novelty rejection and sample-efficient parent sampling
- METR, "Recent Frontier Models Are Reward Hacking" (2025) - Documented evaluator-gaming incidents in agentic tasks

---

## Skill Metadata

**Created**: 2026-07-08
**Last Updated**: 2026-07-08
**Author**: Agent Skills for Context Engineering Contributors
**Version**: 1.0.0
