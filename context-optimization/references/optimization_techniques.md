# Context Optimization Reference

This document provides detailed technical reference for context optimization techniques and strategies.

## Compaction Strategies

### Summary-Based Compaction

Summary-based compaction replaces verbose content with concise summaries while preserving key information. The approach works by identifying sections that can be compressed, generating summaries that capture essential points, and replacing full content with summaries.

The effectiveness of compaction depends on what information is preserved. Critical decisions, user preferences, and current task state should never be compacted. Intermediate results and supporting evidence can be summarized more aggressively. Boilerplate, repeated information, and exploratory reasoning can often be removed entirely.

### Token Budget Allocation

Measure each serialized context component with the target model's tokenizer:
system prompt, tool definitions, retrieved documents, message history, and
tool outputs. Allocate the window from the observed workload and keep a reserve
for the response and recovery actions. Do not use one fixed token range across
models or tasks.

### Compaction Thresholds

Run degradation probes at increasing context utilization. Set the warning,
compaction, and emergency thresholds before the first measured quality cliff.
Record the model, workload, window size, and evaluation version with those
thresholds.

## Observation Masking Patterns

### Selective Masking

Not all observations should be masked equally. Consider masking observations that have served their purpose and are no longer needed for active reasoning. Keep observations that are central to the current task. Keep observations from the most recent turn. Keep observations that may be referenced again.

### Masking Implementation

```python
def selective_mask(observations: List[Dict], current_task: Dict) -> List[Dict]:
    """
    Selectively mask observations based on relevance.
    
    Returns observations with mask field indicating masked content.
    """
    masked = []
    
    for obs in observations:
        relevance = calculate_relevance(obs, current_task)
        
        if relevance < 0.3 and obs["age"] > 3:
            # Low relevance and old - mask
            masked.append({
                **obs,
                "masked": True,
                "reference": store_for_reference(obs["content"]),
                "summary": summarize_content(obs["content"])
            })
        else:
            masked.append({
                **obs,
                "masked": False
            })
    
    return masked
```

## KV-Cache Optimization

### Prefix Stability

KV-cache hit rates depend on prefix stability. Stable prefixes enable cache reuse across requests. Dynamic prefixes invalidate cache and force recomputation.

Elements that should remain stable include system prompts, tool definitions, and frequently used templates. Elements that may vary include timestamps, session identifiers, and query-specific content.

### Cache-Friendly Design

Design prompts to maximize cache hit rates:

1. Place stable content at the beginning
2. Use consistent formatting across requests
3. Avoid dynamic content in prompts when possible
4. Use placeholders for dynamic content

```python
# Cache-unfriendly: Dynamic timestamp in prompt
system_prompt = f"""
Current time: {datetime.now().isoformat()}
You are a helpful assistant.
"""

# Cache-friendly: Stable prompt with dynamic time as variable
system_prompt = """
You are a helpful assistant.
Current time is provided separately when relevant.
"""
```

## Context Partitioning Strategies

### Sub-Agent Isolation

Partition work across sub-agents to prevent any single context from growing too large. Each sub-agent operates with a clean context focused on its subtask.

### Partition Planning

```python
def plan_partitioning(task: Dict, context_limit: int) -> Dict:
    """
    Plan how to partition a task based on context limits.
    
    Returns partitioning strategy and subtask definitions.
    """
    estimated_context = estimate_task_context(task)
    
    if estimated_context <= context_limit:
        return {
            "strategy": "single_agent",
            "subtasks": [task]
        }
    
    # Plan multi-agent approach
    subtasks = decompose_task(task)
    
    return {
        "strategy": "multi_agent",
        "subtasks": subtasks,
        "coordination": "hierarchical"
    }
```

## Optimization Decision Framework

### When to Optimize

Consider context optimization when utilization approaches the measured safe limit, response quality degrades as conversations extend, or measured cost or latency no longer meets the workload target.

### What Optimization to Apply

Choose optimization strategies based on context composition:

If tool outputs dominate context, apply observation masking. If retrieved documents dominate context, apply summarization or partitioning. If message history dominates context, apply compaction with summarization. If multiple components contribute, combine strategies.

### Evaluation of Optimization

After applying optimization, evaluate effectiveness:

- Measure token reduction achieved
- Measure quality preservation (output quality should not degrade)
- Measure latency improvement
- Measure cost reduction

Iterate on optimization strategies based on evaluation results.

## Common Pitfalls

### Over-Aggressive Compaction

Compacting too aggressively can remove critical information. Always preserve task goals, user preferences, and recent conversation context. Test compaction at increasing aggressiveness levels to find the optimal balance.

### Masking Critical Observations

Masking observations that are still needed can cause errors. Track observation usage and only mask content that is no longer referenced. Consider keeping references to masked content that could be retrieved if needed.

### Ignoring Attention Distribution

The lost-in-middle phenomenon means that information placement matters. Place critical information at attention-favored positions (beginning and end of context). Use explicit markers to highlight important content.

### Premature Optimization

Not all contexts require optimization. Adding optimization machinery has overhead. Optimize only when context limits actually constrain agent performance.

## Monitoring and Alerting

### Key Metrics

Track these metrics to understand optimization needs:

- Context token count over time
- Cache hit rates for repeated patterns
- Response quality metrics by context size
- Cost per conversation by context length
- Latency by context size

### Alert Thresholds

Set alerts from the accepted workload baseline:

- Context utilization approaches the measured safe limit
- Cache hit rate falls below its baseline
- Quality score crosses the product's error budget
- Cost rises beyond the approved variance

## Integration Patterns

### Integration with Agent Framework

Integrate optimization into agent workflow:

```python
class OptimizingAgent:
    def __init__(self, context_limit: int = 80000):
        self.context_limit = context_limit
        self.optimizer = ContextOptimizer()
    
    def process(self, user_input: str, context: Dict) -> Dict:
        # Check if optimization needed
        if self.optimizer.should_compact(context):
            context = self.optimizer.compact(context)
        
        # Process with optimized context
        response = self._call_model(user_input, context)
        
        # Track metrics
        self.optimizer.record_metrics(context, response)
        
        return response
```

### Integration with Memory Systems

Connect optimization with memory systems:

```python
class MemoryAwareOptimizer:
    def __init__(self, memory_system, context_limit: int):
        self.memory = memory_system
        self.limit = context_limit
    
    def optimize_context(self, current_context: Dict, task: str) -> Dict:
        # Check if information is in memory
        relevant_memories = self.memory.retrieve(task)
        
        # Move information to memory if not needed in context
        for mem in relevant_memories:
            if mem["importance"] < threshold:
                current_context = remove_from_context(current_context, mem)
                # Keep reference that memory can be retrieved
        
        return current_context
```

## Performance Measurement

Do not apply universal reduction, quality, cache, cost, or latency targets.
Measure each technique against the same task suite and runtime configuration:

- **Compaction**: context tokens, task-quality regressions, and compaction latency
- **Masking**: masked observation tokens, retrieval success, and task quality
- **Cache optimization**: cache hit rate, cached-token cost, and latency
- **Partitioning**: total tokens and latency including coordinator and handoff overhead

Keep the optimization only when the target metric improves without crossing a
quality or correctness limit.

