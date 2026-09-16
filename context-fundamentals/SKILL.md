---
name: context-fundamentals
description: "This skill should be used to explain or reason about the foundational concepts of context engineering: what context is, the anatomy of a context window, how attention mechanics work, the U-shaped attention curve, why context quality matters more than quantity, and the mental models needed to interpret every other context-engineering decision. Use this for conceptual explanation, onboarding, and background reading. Route operational work to the specialized skills: debugging attention failures goes to context-degradation, token-efficiency work goes to context-optimization, conversation summarization goes to context-compression, and project-shape decisions go to project-development."
license: MIT
metadata:
  upstream: "muratcankoylan/Agent-Skills-for-Context-Engineering"
  upstream_commit: "c578e85e40fe2bda7c1fec91ff64cf5285434934"
  upstream_path: "skills/context-fundamentals"
  adaptation: modified
  license_notice: LICENSE-context-engineering
---

# Context Engineering Fundamentals

Context is the complete state available to a language model at inference time: system instructions, tool definitions, retrieved documents, message history, and tool outputs. Context engineering is the discipline of curating the smallest high-signal token set that maximizes the likelihood of desired outcomes.

This skill is the conceptual foundation that every other skill in the collection builds on. It explains what context is, how attention mechanics work, why context quality matters more than quantity, and the mental models needed to interpret every other context-engineering decision. It does not own operational work: debugging attention failures belongs to `context-degradation`, token-efficiency tactics belong to `context-optimization`, conversation summarization belongs to `context-compression`, file-based offloading belongs to `filesystem-context`, and project-shape decisions belong to `project-development`.

## When to Activate

Activate this skill when the work is conceptual:

- Explaining what context is and how attention mechanics constrain agent behavior.
- Onboarding new contributors who need the mental models before diving into operational skills.
- Reasoning about a context-related design decision from first principles (what does this constraint mean, why does this trade-off exist) before picking a specific tactic.
- Writing or reviewing documentation that needs to ground operational guidance in the underlying mechanics.

Do not activate this skill for operational work. The specialized skills handle the doing:

- Diagnosing lost-in-middle, context poisoning, or attention failures: `context-degradation`.
- Reducing token cost via masking, partitioning, prefix caching, budgets: `context-optimization`.
- Compressing a long session into a handoff summary: `context-compression`.
- Offloading large tool outputs or maintaining a durable scratchpad: `filesystem-context`.
- Deciding the shape of an LLM project or pipeline: `project-development`.

## Core Concepts

Treat context as a finite input budget, not a storage bin. The engineering problem is maximizing utility per token within the hard token limit and the workload's measured effective capacity.

Apply four principles when assembling context:

1. **Informativity over exhaustiveness** — include only what matters for the current decision; design systems that can retrieve additional information on demand.
2. **Position-aware placement** — test whether the target model recovers critical constraints differently from the beginning, middle, and end of representative contexts, then use the best-performing placement.
3. **Progressive disclosure** — load skill names and summaries at startup; load full content only when a skill activates for a specific task.
4. **Iterative curation** — context engineering is not a one-time prompt-writing exercise but an ongoing discipline applied every time content is passed to the model.

## Detailed Topics

### The Anatomy of Context

**System Prompts**
Organize system prompts into distinct sections using XML tags or Markdown headers (background, instructions, tool guidance, output format). Test where the target model follows critical constraints most reliably rather than assuming one placement works for every workload.

Calibrate instruction altitude to balance two failure modes. Too-low altitude hardcodes brittle logic that breaks when conditions shift. Too-high altitude provides vague guidance that fails to give concrete signals for desired behavior. Aim for heuristic-driven instructions: specific enough to guide behavior, flexible enough to generalize — for example, numbered steps with room for judgment at each step.

Start minimal, then add instructions reactively based on observed failure modes rather than preemptively stuffing edge cases. Curate diverse, canonical few-shot examples that portray expected behavior instead of listing every possible scenario.

**Tool Definitions**
Write tool descriptions that answer three questions: what the tool does, when to use it, and what it returns. Include usage context, parameter defaults, and error cases — agents cannot disambiguate tools that a human engineer cannot disambiguate either.

Keep the tool set minimal. Consolidate overlapping tools because serialized schemas consume context and create ambiguous routing choices. Measure the serialized token count instead of estimating it from source lines.

**Retrieved Documents**
Maintain lightweight identifiers (file paths, stored queries, web links) and load data into context dynamically using just-in-time retrieval. This mirrors human cognition — maintain an index, not a copy. Strong identifiers (e.g., `customer_pricing_rates.json`) let agents locate relevant files even without search tools; weak identifiers (e.g., `data/file1.json`) force unnecessary loads.

When chunking large documents, split at natural semantic boundaries (section headers, paragraph breaks) rather than arbitrary character limits that sever mid-concept.

**Message History**
Message history serves as the agent's scratchpad memory for tracking progress, maintaining task state, and preserving reasoning across turns. For long-running tasks, it can grow to dominate context usage — monitor and apply compaction before it crowds out active instructions.

Cyclically refine history: once a tool has been called deep in the conversation, the raw result rarely needs to remain verbatim. Replace stale tool outputs with compact summaries or references to reduce low-signal bulk.

**Tool Outputs**
Tool outputs can become the largest part of an agent trajectory. Measure their share, then apply observation masking when they crowd out active instructions or task state. Replace processed outputs with compact, retrievable references and retain the most recently relevant file contents.

### Context Windows and Attention Mechanics

**The Attention Budget**
For $n$ tokens, standard full self-attention computes $n^2$ pairwise relationships. The nominal window states what fits, not the quality the model will achieve on a particular workload.

Measure quality across representative context sizes instead of assuming a universal effective-capacity ceiling.

**Position Encoding Limits**
Test information retrieval and long-range reasoning at the context lengths the application will use; do not infer task quality from the nominal window alone.

**Progressive Disclosure in Practice**
Implement progressive disclosure at three levels:

1. **Skill selection** — load only names and descriptions at startup; activate full skill content on demand.
2. **Document loading** — load summaries first; fetch detail sections only when the task requires them.
3. **Tool result retention** — keep recent results in full; compress or evict older results.

Keep the boundary crisp: if a skill or document is activated, load it fully rather than partially — partial loads create confusing gaps that degrade reasoning quality.

### Context Quality Versus Quantity

Reject the assumption that a larger context window automatically solves memory problems. Measure cost and task quality across representative context sizes.

Apply the signal-density test: for each piece of context, ask whether removing it changes the model's output. If not, remove it.

## Practical Guidance

This section provides conceptual application advice. Pointers to operational skills are explicit.

### Reasoning About a Context Decision

When a context-related design decision needs to be made, separate the conceptual question from the operational one. The conceptual question is "what does this mean and why does it matter"; the operational question is "what specific technique do we apply." Use this skill to answer the first; route to the specialized skill that owns the second.

For example, deciding whether to summarize a long agent session has two parts: (1) whether quality declines as the measured context grows and (2) what compression strategy preserves the right state and when to trigger it (`context-compression`).

### Reading Order For New Contributors

A contributor coming to context engineering for the first time should read:

1. This skill, to internalize the finite-budget framing and the need to measure position sensitivity.
2. `context-degradation`, to see what context failures look like in practice and how to diagnose them.
3. Two or three of `context-optimization`, `context-compression`, `filesystem-context`, `memory-systems` depending on which operational concern is most relevant to their project.

Skipping step 1 produces operators who apply techniques without understanding why; skipping the operational skills produces theorists who do not know which technique fits which failure mode.

## Examples

**Example 1: Organizing System Prompts**

Illustrates how to put critical constraints at clearly labeled positions and then verify that the target model follows them:

```markdown
<BACKGROUND_INFORMATION>
You are a Python expert helping a development team.
Current project: Data processing pipeline in Python 3.9+
</BACKGROUND_INFORMATION>

<INSTRUCTIONS>
- Write clean, idiomatic Python code
- Include type hints for function signatures
- Add docstrings for public functions
- Follow PEP 8 style guidelines
</INSTRUCTIONS>

<OUTPUT_DESCRIPTION>
Provide code blocks with syntax highlighting.
Explain non-obvious decisions in comments.
</OUTPUT_DESCRIPTION>
```

**Example 2: Position As An Evaluation Variable**

A large-context model may not use every position equally on every workload. When deciding how much of an upstream knowledge base to load, ask not only "will it fit" but also "can the target model recover the parts that matter from their assigned positions."

The corresponding operational question—how to reduce the load after measuring a problem—belongs to `context-optimization`.

## Guidelines

1. Treat context as a finite resource
2. Test critical information at different context positions
3. Use progressive disclosure to defer loading until needed
4. Organize system prompts with clear section boundaries
5. Monitor context usage during development
6. Implement compaction triggers before the measured safe context limit
7. Test for context degradation
8. Prefer smaller high-signal context over larger low-signal context

## Gotchas

1. **Nominal window is not effective capacity**: A model advertising a large context window may degrade well before that limit on complex retrieval or reasoning tasks. Budget below the nominal window until your own degradation tests prove otherwise.

2. **Character-based token estimates silently drift**: Prose, code, URLs, file paths, and non-English text tokenize differently. Use the provider's actual tokenizer or counting API for any budget-critical calculation.

3. **Serialized tool schemas consume more context than their source layout suggests**: Brackets, quotes, descriptions, and repeated field metadata all count toward the prompt. Audit the serialized token count before adding tools.

4. **Message history balloons silently in agentic loops**: Each tool call adds both the request and response to history. Set a measured history ceiling and trigger compaction before task instructions are displaced.

5. **Critical instructions can be position-sensitive**: Test safety constraints, output-format requirements, and behavioral guardrails at different positions in representative long prompts. Place them where the target model follows them most reliably.

6. **Progressive disclosure that loads too eagerly defeats its purpose**: Loading every "potentially relevant" skill or document at the first hint of relevance recreates the context-stuffing problem. Set strict activation thresholds — a skill should load only when the task explicitly matches its trigger conditions, not when the topic is merely adjacent.

7. **Mixing instruction altitudes causes inconsistent behavior**: Combining hyper-specific rules ("always use exactly 3 bullet points") with vague directives ("be helpful") in the same prompt creates conflicting signals. Group instructions by altitude level and keep each section internally consistent — either heuristic-driven or prescriptive, not both interleaved.

## Integration

This skill is the conceptual foundation. It does not own operational work; it provides the mental models the operational skills assume.

Routing map for operational work:

- `context-degradation`: diagnosing attention failures, lost-in-middle, poisoning, distraction.
- `context-optimization`: token-efficiency tactics (masking, partitioning, caching, budgets).
- `context-compression`: compacting long sessions while preserving decisions, files, risks.
- `filesystem-context`: offloading large outputs and using files as a durable scratchpad.
- `memory-systems`: cross-session memory architectures with entity tracking.
- `multi-agent-patterns`: when to split work across agents for context isolation.
- `tool-design`: writing tool descriptions and schemas that route correctly.
- `project-development`: deciding LLM fit and shaping multi-stage pipelines.

Read this skill first to build the mental models; read the operational skill that fits the task when actually doing the work.

## References

Internal reference:
- [Context Components Reference](skill://context-fundamentals/references/context-components.md) - Read when: debugging a specific context component (system prompts, tool definitions, message history, tool outputs) or implementing chunking, observation masking, or budget allocation tables

Runnable script:

### `context_manager.py`

- **Status:** Example.
- **Boundary:** Approximates token counts from character ratios rather than tokenizer output. It validates only its local context structure and does not prove model behavior.
- **Run:** From the repository root, run `python context-fundamentals/scripts/context_manager.py`. The demo accepts no arguments or credentials and uses built-in prompt, task, and document strings.
- **Output:** Writes a human-readable estimated token total, utilization, section breakdown, and validation result to standard output. `build_agent_context` returns `context`, `usage_report`, and `validation` fields.
- **Failure:** The demo exits non-zero only on an uncaught Python error. Repair the reported import or input-type error; a printed validation failure is report data and does not set a non-zero exit status.

Related skills in this collection:
- context-degradation - Read when: agent performance drops as conversations grow or measured context pressure rises
- context-optimization - Read when: token costs are too high or compaction/compression strategies are needed

External resources:
- Anthropic's "Effective Context Engineering for AI Agents" — production patterns for compaction, sub-agents, and hybrid retrieval
- Research on transformer attention mechanisms and the lost-in-the-middle effect
- Tokenomics research on agentic software engineering token distribution

---

## Skill Metadata

**Created**: 2025-12-20
**Last Updated**: 2026-05-15
**Author**: Agent Skills for Context Engineering Contributors
**Version**: 2.2.0
