---
name: context-degradation
description: "This skill should be used for diagnosing and mitigating context degradation: lost-in-middle failures, context poisoning, context clash, context confusion, attention-pattern issues, and agent performance degradation caused by accumulated or conflicting context."
license: MIT
metadata:
  upstream: "muratcankoylan/Agent-Skills-for-Context-Engineering"
  upstream_commit: "c578e85e40fe2bda7c1fec91ff64cf5285434934"
  upstream_path: "skills/context-degradation"
  adaptation: modified
  license_notice: LICENSE-context-engineering
---

# Context Degradation Patterns

Diagnose and fix context failures before they cascade. Context degradation is not binary — it is a continuum that manifests through five distinct, predictable patterns: lost-in-middle, poisoning, distraction, confusion, and clash. Each pattern has specific detection signals and mitigation strategies. Treat degradation as an engineering problem with measurable thresholds, not an unpredictable failure mode.

## When to Activate

Activate this skill when:
- Agent performance degrades unexpectedly during long conversations
- Debugging cases where agents produce incorrect or irrelevant outputs
- Designing systems that must handle large contexts reliably
- Evaluating context engineering choices for production systems
- Investigating "lost in middle" phenomena in agent outputs
- Analyzing context-related failures in agent behavior

Do not activate this skill for adjacent work owned by other skills:
- Explaining foundational context mechanics without an active failure: `context-fundamentals`.
- Applying token-efficiency tactics after the failure pattern is known: `context-optimization`.
- Designing a compression or handoff summary strategy: `context-compression`.
- Persisting large outputs, logs, or scratch state outside the prompt: `filesystem-context`.

## Core Concepts

Treat position as an evaluation variable: benchmark whether critical information is recovered from the beginning, middle, and end of the target workload, then place it where measured recall is strongest. Do not assume that every model or task follows the same positional pattern.

Treat context poisoning as a circuit breaker problem. Once a hallucination, tool error, or incorrect retrieved fact enters context, it compounds through repeated self-reference. A poisoned goals section causes every downstream decision to reinforce incorrect assumptions. Detection requires tracking claim provenance; recovery requires truncating to before the poisoning point or restarting with verified-only context.

Filter context before loading it. Irrelevant material consumes context capacity and can change model behavior, so keep information that is not immediately relevant behind tool calls.

Isolate task contexts to prevent confusion. When context contains multiple task types or switches between objectives, models incorporate constraints from the wrong task, call tools appropriate for a different context, or blend requirements from multiple sources. Explicit task segmentation with separate context windows eliminates cross-contamination.

Resolve context clash through priority rules, not accumulation. When multiple correct-but-contradictory sources appear in context (version conflicts, perspective conflicts, multi-source retrieval), models cannot determine which applies. Mark contradictions explicitly, establish source precedence, and filter outdated versions before they enter context.

## Detailed Topics

### Lost-in-Middle: Detection and Placement Strategy

Test critical information at the beginning, middle, and end of representative long contexts. If the target model recovers edge-positioned information more reliably, place critical constraints at those measured positions.

Use explicit section headers and summaries to make position experiments easy to construct and interpret. When a document must be included in full, test whether prepending a summary or appending conclusions improves recovery on the target model.

Monitor for lost-in-middle symptoms: correct information exists in context but the model ignores it, responses contradict provided data, or the model "forgets" instructions given earlier in a long prompt.

### Context Poisoning: Prevention and Recovery

Validate all external inputs before they enter context. Tool outputs, retrieved documents, and model-generated summaries are the three primary poisoning vectors. Each introduces unverified claims that subsequent reasoning treats as ground truth.

Detect poisoning through these signals: degraded output quality on previously-successful tasks, tool misalignment (wrong tools or parameters), and hallucinations that persist despite explicit correction. When these cluster, suspect poisoning rather than model capability issues.

Recover by removing poisoned content, not by adding corrections on top. Truncate to before the poisoning point, restart with clean context preserving only verified information, or explicitly mark the poisoned section and request re-evaluation from scratch. Layering corrections over poisoned context rarely works — the original errors retain attention weight.

### Context Distraction: Curation Over Accumulation

Measure the effect of irrelevant documents instead of assuming the model will ignore them. Test a clean context against contexts containing one or more distractors, then set retrieval filters from the observed difference.

Apply relevance filtering before loading retrieved documents. Use namespacing and structural organization to make section boundaries clear. Prefer tool-call-based access over pre-loading: store reference material behind retrieval tools so it enters context only when directly relevant to the current reasoning step.

### Context Confusion: Task Isolation

Segment different tasks into separate context windows. Context confusion is distinct from distraction — it concerns the model applying wrong-context constraints to the current task, not just attention dilution. Signs include responses addressing the wrong aspect of a query, tool calls appropriate for a different task, and outputs mixing requirements from multiple sources.

Implement clear transitions between task contexts. Use state management that isolates objectives, constraints, and tool definitions per task. When task-switching within a single session is unavoidable, use explicit "context reset" markers that signal which constraints apply to the current segment.

### Context Clash: Conflict Resolution Protocols

Establish source priority rules before conflicts arise. Context clash differs from poisoning — multiple pieces of information are individually correct but mutually contradictory (version conflicts, perspective differences, multi-source retrieval with divergent facts).

Implement version filtering to exclude outdated information before it enters context. When contradictions are unavoidable, mark them explicitly with structured conflict annotations: state what conflicts, which source each claim comes from, and which source takes precedence. Without explicit priority rules, models resolve contradictions unpredictably.

### Empirical Benchmarks and Thresholds

Treat advertised context-window length as a capacity limit, not a quality guarantee. Benchmark the target workload at progressively larger context sizes, including retrieval and reasoning tasks rather than only simple needle retrieval.

**Model-Specific Degradation Thresholds**

Do not use a general percentage of the advertised window as a degradation threshold. Onset depends on the model version, task, prompt, and context composition. Measure it for the deployed workload and repeat the measurement after model or infrastructure changes.

### Counterintuitive Findings

Account for these possibilities when designing context experiments:

**Shuffled context may behave differently from coherent context.** Compare both arrangements when order is not semantically required; do not assume that more organization improves retrieval.

**A single distractor may be enough to change results.** Compare a clean baseline with one-distractor and multi-distractor cases before choosing a relevance threshold.

**Needle-question similarity may affect retrieval.** Include both high- and low-similarity cases in retrieval tests rather than generalizing from exact-match cases.

### When Larger Contexts Hurt

Do not assume that a larger context improves performance. Measure task quality as context grows and define the operating limit from the target model and workload.

Factor in cost: larger contexts can increase both processing time and compute cost. Measure provider pricing and latency at the actual context sizes before choosing a large-context strategy.

Recognize the cognitive bottleneck: even with infinite context, asking a single model to maintain quality across dozens of independent tasks creates degradation that more context cannot solve. Split tasks across sub-agents instead of expanding context.

## Practical Guidance

### The Four-Bucket Mitigation Framework

Apply these four strategies based on which degradation pattern is active:

**Write** — Save context outside the window using scratchpads, file systems, or external storage. Use when utilization approaches the measured safe limit. This keeps active context lean while preserving information access through tool calls.

**Select** — Pull only relevant context into the window through retrieval, filtering, and prioritization. Use when distraction or confusion symptoms appear. Apply relevance scoring before loading; exclude anything below threshold rather than including everything available.

**Compress** — Reduce tokens while preserving information through summarization, abstraction, and observation masking. Use when context is growing but all content is relevant. Replace verbose tool outputs with compact structured summaries; abstract repeated patterns into single references.

**Isolate** — Split context across sub-agents or sessions to prevent any single context from growing past its degradation threshold. Use when confusion or clash symptoms appear, or when tasks are independent. This is the most aggressive strategy but often the most effective for complex multi-task systems.

### Architectural Patterns for Resilience

Implement just-in-time context loading: retrieve information only when the current reasoning step needs it, not preemptively. Use observation masking to replace verbose tool outputs with compact references after processing. Deploy sub-agent architectures where each agent holds only task-relevant context. Trigger compaction before context exceeds the model-specific degradation onset threshold — not after symptoms appear.

## Examples

**Example 1: Detecting Degradation**
```yaml
# Illustrative measurements; replace with observed workload data
baseline:
  context_tokens: measured_value
  quality_score: measured_value
larger_context:
  context_tokens: measured_value
  quality_score: measured_value
```

**Example 2: Testing Position Sensitivity**
```markdown
# Run the same prompt with critical information in different positions

[CURRENT TASK]
- Goal: Generate quarterly report
- Deadline: End of week

[DETAILED CONTEXT]
- Supporting data
- Analysis sections

[KEY FINDINGS]
- Revenue increased
- Costs decreased
- Growth in Region A
```

**Example 3: Context poisoning circuit breaker**
```text
symptom: agent keeps citing an incorrect retrieved claim after correction
diagnosis: poisoned context, not a missing-instruction problem
action:
  1. identify first turn where the bad claim entered
  2. truncate or restart from before that point
  3. reload only verified sources
  4. record the rejected claim and source provenance
```

**Example 4: Context clash annotation**
```yaml
conflict:
  topic: billing API version
  source_a: docs/v1.md says endpoint is /charges
  source_b: docs/v2.md says endpoint is /payments
  precedence: docs/v2.md
  reason: current production version
```

## Guidelines

1. Monitor context length and performance correlation during development
2. Test critical information at beginning, middle, and end positions
3. Implement compaction triggers before degradation becomes severe
4. Validate retrieved documents for accuracy before adding to context
5. Use versioning to prevent outdated information from causing clash
6. Segment tasks to prevent context confusion across different objectives
7. Design for graceful degradation rather than assuming perfect conditions
8. Test with progressively larger contexts to find degradation thresholds

## Gotchas

1. **Normal variance looks like degradation**: Do not diagnose degradation from a single quality drop. Establish a baseline over repeated runs and look for a sustained decline tied to context growth.

2. **Model-specific thresholds go stale**: Re-benchmark after model, prompt, or infrastructure changes rather than treating a published threshold as permanent.

3. **Needle-in-haystack scores create false confidence**: A single-fact retrieval test does not establish production quality on workloads that require multi-fact reasoning, instruction following, or synthesis. Use task-specific benchmarks that mirror the deployed workload.

4. **Contradictory retrieved documents poison silently**: When a RAG pipeline retrieves two documents that disagree on a fact, the model may silently pick one without signaling the conflict. This looks like a correct response but is effectively random. Implement contradiction detection in the retrieval layer before documents enter context.

5. **Prompt quality problems masquerade as degradation**: Poor prompt structure can produce the same symptoms as context pressure. Before diagnosing degradation, verify the prompt on a smaller context.

6. **Assumed curve shape hides failures**: Do not assume degradation is linear or has a universal cliff. Measure quality across context sizes and set compaction triggers before the measured failure region.

7. **Over-organizing context can backfire**: Compare coherent and shuffled layouts when order is not semantically required. Use the layout that performs better on the target retrieval task.

## Integration

This skill owns diagnosis and mitigation of active context failures. Adjacent skills own the implementation tactics once the failure is identified:

- `context-fundamentals`: conceptual explanation of attention and context windows before a failure exists.
- `context-optimization`: masking, caching, partitioning, and other token-efficiency tactics after diagnosis.
- `context-compression`: structured summaries and handoffs when accumulated context must be compacted.
- `filesystem-context`: offloading raw outputs, logs, and scratch state so poisoned or bulky context can be inspected without staying in the prompt.
- `multi-agent-patterns`: isolating tasks into separate contexts to prevent confusion and clash.
- `evaluation`: degradation tests and production monitoring.

## References

Internal reference:
- [Degradation Patterns Reference](skill://context-degradation/references/patterns.md) - Read when: debugging a specific degradation pattern and needing implementation-level detection code (attention analysis, poisoning tracking, relevance scoring, recovery procedures)

Runnable script:

### `degradation_detector.py`

- **Status:** Example.
- **Boundary:** Simulates attention and uses heuristics for token counts, poisoning, and hallucination signals. It does not measure a model, so its risk labels do not prove live degradation.
- **Run:** From the repository root, run `python context-degradation/scripts/degradation_detector.py`. The demo accepts no arguments or credentials and uses synthetic context.
- **Output:** Writes human-readable structure, simulated-attention, lost-in-middle, poisoning, and composite-health reports to standard output. `analyze_agent_context` returns the composite report as a dictionary.
- **Failure:** The demo exits non-zero only on an uncaught Python error. Repair the reported import or input-type error; a risky or degraded report remains a successful process result.

Related skills in this collection:
- context-fundamentals - Read when: lacking foundational understanding of context windows, token budgets, or placement mechanics
- context-optimization - Read when: degradation is diagnosed and specific mitigation techniques (compaction, compression, masking) are needed
- evaluation - Read when: setting up production monitoring to detect degradation before it impacts users

External resources:
- Liu et al., 2023 "Lost in the Middle" - Read when: needing primary research backing for U-shaped attention claims or designing position-aware context layouts
- RULER benchmark documentation - Read when: evaluating model claims about long-context support or comparing models for context-heavy workloads
- Production engineering guides from AI labs - Read when: implementing context management in production infrastructure

---

## Skill Metadata

**Created**: 2025-12-20
**Last Updated**: 2026-05-15
**Author**: Agent Skills for Context Engineering Contributors
**Version**: 2.1.0
