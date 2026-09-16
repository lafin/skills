---
name: context-optimization
description: "This skill should be used for improving context efficiency: context budgeting, observation masking, prefix or KV-cache strategy, partitioning, token-cost reduction, retrieval scoping, and extending effective context capacity without lowering answer quality."
license: MIT
metadata:
  upstream: "muratcankoylan/Agent-Skills-for-Context-Engineering"
  upstream_commit: "c578e85e40fe2bda7c1fec91ff64cf5285434934"
  upstream_path: "skills/context-optimization"
  adaptation: modified
  license_notice: LICENSE-context-engineering
---

# Context Optimization Techniques

Context optimization extends the effective capacity of limited context windows through strategic compression, masking, caching, and partitioning. Effective optimization increases useful capacity without requiring larger models or longer windows — but only when applied with measurement discipline. The techniques below are ordered by impact and risk.

## When to Activate

Activate this skill when:
- Context budgets or token costs constrain task complexity
- Observation masking can replace verbose tool outputs with retrievable references
- Prefix or KV-cache hit rate needs improvement
- Retrieval scoping can reduce irrelevant loaded context
- Context partitioning can extend effective capacity across agents
- Budget triggers are needed for masking, compaction, or partitioning

Do not activate this skill for adjacent work owned by other skills:
- Explaining why attention or context windows behave this way: `context-fundamentals`.
- Diagnosing active lost-in-middle, poisoning, distraction, confusion, or clash: `context-degradation`.
- Designing a structured handoff summary for a long conversation: `context-compression`.
- Storing large outputs, plans, or logs as files: `filesystem-context`.

## Core Concepts

Apply four primary strategies in this priority order:

1. **KV-cache optimization** — Reorder and stabilize prompt structure so the inference engine reuses cached Key/Value tensors. This is the cheapest optimization when the runtime supports prefix caching: low quality risk, immediate cost and latency savings. Apply it first when stable prefixes exist.

2. **Observation masking** — When tool outputs occupy a large share of the measured context, replace processed outputs with compact references. The original content remains retrievable if needed downstream.

3. **Compaction** — Summarize accumulated context before measured window pressure causes failure, then reinitialize with the summary. Compaction is lossy; apply it after masking has removed measured low-value bulk.

4. **Context partitioning** — Split work across sub-agents with isolated contexts when a single window cannot hold the full problem. Each sub-agent operates in a clean context focused on its subtask. Reserve this for tasks whose measured context pressure exceeds the coordination overhead.

The governing principle: context quality matters more than quantity. Every optimization preserves signal while reducing noise. Measure before optimizing, then measure the optimization's effect.

## Detailed Topics

### Compaction Strategies

Trigger compaction before context pressure causes missed instructions or truncation: summarize the current context, then reinitialize with the summary. This distills the window's contents for continuation. Prioritize whichever measured category consumes the most tokens rather than assuming tool outputs always dominate. Never compress the system prompt — it anchors model behavior and its removal can change model behavior.

Preserve different elements by message type:

- **Tool outputs**: Extract key findings, metrics, error codes, and conclusions. Strip verbose raw output, stack traces (unless debugging is ongoing), and boilerplate headers.
- **Conversational turns**: Retain decisions, commitments, user preferences, and context shifts. Remove filler, pleasantries, and exploratory back-and-forth that led to a conclusion already captured.
- **Retrieved documents**: Keep claims, facts, and data points relevant to the active task. Remove supporting evidence and elaboration that served a one-time reasoning purpose.

Set token-reduction and quality-loss targets from a measured task baseline. Audit every aggressive summary for critical information loss.

### Observation Masking

Mask observations selectively based on recency and ongoing relevance — not uniformly. Apply these rules:

- **Never mask**: Observations critical to the current task, observations from the most recent turn, observations used in active reasoning chains, and error outputs when debugging is in progress.
- **Mask after relevance ends**: Verbose outputs whose key points have already been extracted into the conversation flow. Replace with a compact reference: `[Obs:{ref_id} elided. Key: {summary}. Full content retrievable.]`
- **Always mask immediately**: Repeated/duplicate outputs, boilerplate headers and footers, outputs already summarized earlier in the conversation.

Measure masking by reduced observation tokens and retained task quality. Keep the full content externally and a reference ID in context so the agent can request the original when needed.

### KV-Cache Optimization

Maximize prefix cache hits by structuring prompts so that stable content occupies the prefix and dynamic content appears at the end. KV-cache stores Key and Value tensors computed during inference; when consecutive requests share an identical prefix, the cached tensors are reused, saving both cost and latency.

Apply this ordering in every prompt:
1. System prompt (most stable — never changes within a session)
2. Tool definitions (stable across requests)
3. Frequently reused templates and few-shot examples
4. Conversation history (grows but shares prefix with prior turns)
5. Current query and dynamic content (least stable — always last)

Design prompts for cache stability: remove timestamps, session counters, and request IDs from the system prompt. Move dynamic metadata into a separate user message or tool result where it does not break the prefix. Even a single whitespace change in the prefix invalidates the entire cached block downstream of that change.

Measure cache hit rate, cached-token cost, and latency for each stable workload instead of applying a universal target.

### Context Partitioning

Partition work across sub-agents when a single context cannot hold the full problem without triggering aggressive compaction. Each sub-agent operates in a clean, focused context for its subtask, then returns a structured result to a coordinator agent.

Plan partitioning when measured task context no longer fits safely in one window. Decompose the task into independent subtasks, assign each to a sub-agent, and aggregate results. Validate that all partitions completed before merging, merge compatible results, and apply summarization if the aggregated output still exceeds budget.

This approach achieves separation of concerns — detailed search context stays isolated within sub-agents while the coordinator focuses on synthesis. However, coordination has real token cost: the coordinator prompt, result aggregation, and error handling all consume tokens. Only partition when the savings exceed this overhead.

### Budget Management

Allocate explicit token budgets across context categories before the session begins: system prompt, tool definitions, retrieved documents, message history, tool outputs, and a reserved buffer. Monitor usage against budget continuously and trigger optimization when a category exceeds its measured allocation.

Use trigger-based optimization rather than periodic optimization. Monitor these signals:
- Token utilization approaches the runtime's measured safe limit — trigger compaction
- Attention degradation indicators (repetition, missed instructions) — trigger masking + compaction
- Quality score drops below baseline — audit context composition before optimizing

## Practical Guidance

### Optimization Decision Framework

Select the optimization technique based on what dominates the context:

| Context Composition | First Action | Second Action |
|---|---|---|
| Tool outputs are the largest measured category | Observation masking | Compaction of remaining turns |
| Retrieved documents dominate | Summarization | Partitioning if docs are independent |
| Message history dominates | Compaction with selective preservation | Partitioning for new subtasks |
| Multiple components contribute | KV-cache optimization first, then layer masking + compaction |
| Near-limit with active debugging | Mask resolved tool outputs only — preserve error details |

### Performance Targets

Track these metrics to validate optimization effectiveness:

- **Compaction**: Reduced context tokens without regression on the task-quality suite
- **Masking**: Reduced observation tokens with the original content still retrievable
- **Cache optimization**: Higher cache hit rate with lower measured cached-token cost or latency
- **Partitioning**: Net token savings after coordinator and handoff overhead

Iterate on strategies based on measured results. If an optimization technique does not measurably improve the target metric, remove it — optimization machinery itself consumes tokens and adds latency.

## Examples

**Example 1: Compaction Trigger**
```python
if context_tokens / context_limit > 0.8:
    context = compact_context(context)
```

**Example 2: Observation Masking**
```python
if len(observation) > max_length:
    ref_id = store_observation(observation)
    return f"[Obs:{ref_id} elided. Key: {extract_key(observation)}]"
```

**Example 3: Cache-Friendly Ordering**
```python
# Stable content first
context = [system_prompt, tool_definitions]  # Cacheable
context += [reused_templates]  # Reusable
context += [unique_content]  # Unique
```

**Example 4: Budget-triggered optimization policy**
```yaml
budgets:
  tool_outputs: 35%
  message_history: 30%
  retrieved_documents: 20%
  reserved_buffer: 15%
triggers:
  tool_outputs_over_budget: mask resolved observations
  total_context_over_70_percent: compact message history
  repeated_irrelevant_retrievals: tighten retrieval scope
```

## Guidelines

1. Measure before optimizing—know your current state
2. Apply masking before compaction — remove low-value bulk first, then summarize what remains
3. Design for cache stability with consistent prompts
4. Partition before context becomes problematic
5. Monitor optimization effectiveness over time
6. Balance token savings against quality preservation
7. Test optimization at production scale
8. Implement graceful degradation for edge cases

## Gotchas

1. **Whitespace breaks KV-cache**: Even a single whitespace or newline change in the prompt prefix invalidates the entire KV-cache block downstream of that point. Pin system prompts as immutable strings — do not interpolate timestamps, version numbers, or session IDs into them. Diff prompt templates byte-for-byte between deployments.

2. **Timestamps in system prompts destroy cache hit rates**: Including `Current date: {today}` or similar dynamic content in the system prompt forces a full cache miss on every new day (or every request, if using time-of-day). Move dynamic metadata into a user message or a separate tool result appended after the stable prefix.

3. **Compaction under pressure loses critical state**: A model performing compaction near its context limit can omit task goals, user constraints, or nuanced state. Trigger compaction before the limit. If compaction must happen late, use a separate model call with a clean context containing only the material to summarize.

4. **Masking error outputs breaks debugging loops**: Over-aggressive masking hides error messages, stack traces, and failure details that the agent needs in subsequent turns to diagnose and fix issues. During active debugging, preserve error-related observations until the issue is resolved.

5. **Partitioning overhead can exceed savings**: Each sub-agent requires its own system prompt, tool definitions, and coordination messages. Estimate total tokens for the coordinator and all sub-agents before committing to partitioning.

6. **Cache miss cost spikes after deployment changes**: Reordering tools, rewording the system prompt, or changing few-shot examples between deployments invalidates the changed prefix. Roll out prompt changes gradually and monitor cache hit rate during deployment windows.

7. **Compaction creates false confidence in stale summaries**: Once context is compacted, the summary looks authoritative but may reflect outdated state. If the task has evolved since compaction (new user requirements, corrected assumptions), the summary silently carries forward stale information. After compaction, re-validate the summary against the current task goal before proceeding.

## Integration

This skill owns token-efficiency tactics and budget policy. Adjacent skills own diagnosis, storage, and architecture:

- `context-fundamentals`: mental models for why context quality and attention placement matter.
- `context-degradation`: diagnosis when output quality has already dropped.
- `context-compression`: lossy summarization and handoff strategy.
- `filesystem-context`: file-backed offloading for full outputs and logs.
- `multi-agent-patterns`: partitioning work across isolated agent contexts.
- `latent-briefing`: selective KV retention across orchestrator-worker boundaries in compatible runtimes.
- `evaluation`: measuring whether the optimization improved quality, cost, or latency.
- `memory-systems`: persistent retrieval layers that feed context just in time.

## References

Internal reference:
- [Optimization Techniques Reference](skill://context-optimization/references/optimization_techniques.md) - Read when: implementing a specific optimization technique and needing detailed code patterns, threshold tables, or integration examples beyond what the skill body provides

Runnable script:

### `compaction.py`

- **Status:** Example.
- **Boundary:** Uses illustrative token, summary, and cache heuristics without a tokenizer, model, or inference service. It does not prove quality, savings, or cache behavior in production.
- **Run:** From the repository root, run `python context-optimization/scripts/compaction.py`. The demo accepts no arguments or credentials and uses built-in text and budget data.
- **Output:** Writes human-readable token estimates, masking and retrieval status, budget advice, prompt stabilization, and a summary to standard output. Library callers receive strings, tuples, and dictionaries from the exported functions and classes.
- **Failure:** The demo exits non-zero only on an uncaught Python error. Repair the reported import, invalid argument, or input-type error; an optimization recommendation is report data, not a process failure.

Related skills in this collection:
- context-fundamentals - Read when: unfamiliar with context window mechanics, token counting, or attention distribution basics
- context-degradation - Read when: diagnosing why agent performance has dropped and needing to identify which degradation pattern is occurring before selecting an optimization
- evaluation - Read when: setting up metrics and benchmarks to measure whether an optimization technique actually improved outcomes

External resources:
- Research on context window limitations - Read when: evaluating model-specific context behavior (e.g., lost-in-the-middle effects, attention decay curves)
- KV-cache optimization techniques - Read when: implementing prefix caching at the inference infrastructure level (vLLM, TGI, or cloud provider APIs)
- Production engineering guides - Read when: deploying context optimization in a production pipeline and needing operability patterns (monitoring, alerting, rollback)

---

## Skill Metadata

**Created**: 2025-12-20
**Last Updated**: 2026-05-15
**Author**: Agent Skills for Context Engineering Contributors
**Version**: 2.1.0
