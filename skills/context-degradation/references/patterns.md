# Context Degradation Patterns: Technical Reference

This document provides technical details on diagnosing and measuring context degradation.

## Position and Length Sensitivity

### Behavioral Recall Probe

Closed model APIs do not expose attention weights, and position effects vary by model and task. Measure recall behaviorally: insert a known fact at several positions in filler of several lengths, ask for it, and record accuracy per cell.

```python
def probe_recall_by_position(call_model, fact, question, expected, filler,
                             lengths, positions, trials=5):
    """
    Measure recall of *fact* by context length and relative position.

    Args:
        call_model: Callable(prompt: str) -> str for the target model.
        filler: Long task-representative text; sliced to each length.
        lengths: Context sizes to test, in characters.
        positions: Relative insertion points in [0, 1].
        trials: Repeats per cell, to separate noise from degradation.

    Returns:
        Dict mapping (length, position) to recall accuracy in [0, 1].
    """
    results = {}
    for length in lengths:
        haystack = filler[:length]
        for position in positions:
            cut = int(len(haystack) * position)
            prompt = f"{haystack[:cut]}\n{fact}\n{haystack[cut:]}\n\n{question}"
            hits = sum(expected in call_model(prompt) for _ in range(trials))
            results[(length, position)] = hits / trials
    return results
```

### Lost-in-Middle Detection

Compare each cell with the short-context baseline instead of labeling fixed regions as favored:

```python
def detect_position_loss(results, baseline_length, max_drop):
    """
    Flag (length, position) cells whose recall falls more than *max_drop*
    below the same position at *baseline_length*.

    *max_drop* comes from the variance of repeated baseline runs, not a
    universal constant.
    """
    at_risk = []
    for (length, position), recall in results.items():
        baseline = results[(baseline_length, position)]
        if baseline - recall > max_drop:
            at_risk.append({"length": length, "position": position,
                            "baseline": baseline, "recall": recall})
    best_position = max(
        {p for (_, p) in results},
        key=lambda p: sum(r for (_, q), r in results.items() if q == p),
    )
    return {"at_risk": at_risk, "best_measured_position": best_position}
```

Place critical information at the best measured position, and set the compaction trigger below the shortest length with an at-risk cell.

## Context Poisoning Detection

### Hallucination Tracking

Track potential hallucinations across conversation turns:

```python
class HallucinationTracker:
    def __init__(self):
        self.claims = []
        self.verifications = []
    
    def add_claims(self, text):
        """Extract claims from text for later verification."""
        claims = extract_claims(text)
        self.claims.extend([{"text": c, "verified": None} for c in claims])
    
    def verify_claims(self, ground_truth):
        """Verify claims against ground truth."""
        for claim in self.claims:
            if claim["verified"] is None:
                claim["verified"] = check_claim(claim["text"], ground_truth)
    
    def get_poisoning_indicators(self):
        """
        Return indicators of potential context poisoning.
        
        High ratio of unverified claims suggests poisoning risk.
        """
        unverified = sum(1 for c in self.claims if not c["verified"])
        verified_false = sum(1 for c in self.claims if c["verified"] == False)
        
        return {
            "unverified_count": unverified,
            "false_count": verified_false,
            "poisoning_risk": verified_false > 0 or unverified > len(self.claims) * 0.3
        }
```

### Error Propagation Analysis

Track how errors flow through context:

```python
def analyze_error_propagation(context, error_points):
    """
    Analyze how errors at specific points affect downstream context.

    Returns visualization of error spread and impact assessment.
    """
    impact_map = {}

    for error_point in error_points:
        # Find all references to content after error point
        downstream_refs = find_references(context, after=error_point)

        for ref in downstream_refs:
            if ref not in impact_map:
                impact_map[ref] = []
            impact_map[ref].append({
                "source": error_point,
                "type": classify_error_type(context[error_point])
            })

    # Assess severity
    high_impact_areas = [k for k, v in impact_map.items() if len(v) > 3]

    return {
        "impact_map": impact_map,
        "high_impact_areas": high_impact_areas,
        "requires_intervention": len(high_impact_areas) > 0
    }
```

## Distraction Metrics

### Relevance Scoring

Score relevance of context elements to current task:

```python
def score_context_relevance(context_elements, task_description):
    """
    Score each context element for relevance to current task.
    
    Returns scores and identifies high-distraction elements.
    """
    task_embedding = embed(task_description)
    
    scored_elements = []
    for i, element in enumerate(context_elements):
        element_embedding = embed(element)
        relevance = cosine_similarity(task_embedding, element_embedding)
        scored_elements.append({
            "index": i,
            "content_preview": element[:100],
            "relevance_score": relevance
        })
    
    # Sort by relevance
    scored_elements.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Identify potential distractors
    threshold = calculate_relevance_threshold(scored_elements)
    distractors = [e for e in scored_elements if e["relevance_score"] < threshold]
    
    return {
        "scored_elements": scored_elements,
        "distractors": distractors,
        "recommendation": f"Consider removing {len(distractors)} low-relevance elements"
    }
```

## Degradation Monitoring System

### Context Health Dashboard

Implement continuous monitoring of context health:

```python
class ContextHealthMonitor:
    def __init__(self, measured_safe_limit, position_results, baseline_length, max_drop):
        # All four come from a measured baseline on the target model and workload.
        self.limit = measured_safe_limit
        self.position_results = position_results  # from probe_recall_by_position
        self.baseline_length = baseline_length
        self.max_drop = max_drop
        self.metrics = []
    
    def assess_health(self, context_tokens, context, task):
        """
        Assess overall context health for current task.
        
        *context_tokens* comes from the provider's usage fields or
        token-counting API. Returns composite score and component metrics.
        """
        metrics = {
            "token_count": context_tokens,
            "utilization_ratio": context_tokens / self.limit,
            "attention_distribution": detect_position_loss(
                self.position_results, self.baseline_length, self.max_drop),
            "relevance_scores": score_context_relevance(context, task),
            "age_tokens": count_recent_tokens(context)
        }
        
        # Calculate composite health score
        health_score = self._calculate_composite(metrics)
        
        result = {
            "health_score": health_score,
            "metrics": metrics,
            "status": self._interpret_score(health_score),
            "recommendations": self._generate_recommendations(metrics)
        }
        
        self.metrics.append(result)
        return result
    
    def _calculate_composite(self, metrics):
        """Calculate composite health score from components."""
        # Weighted combination of metrics
        utilization_penalty = min(metrics["utilization_ratio"] * 0.5, 0.3)
        attention_penalty = self._calculate_attention_penalty(metrics["attention_distribution"])
        relevance_penalty = self._calculate_relevance_penalty(metrics["relevance_scores"])
        
        base_score = 1.0
        score = base_score - utilization_penalty - attention_penalty - relevance_penalty
        return max(0, score)
    
    def _interpret_score(self, score):
        """Interpret health score and return status."""
        if score > 0.8:
            return "healthy"
        elif score > 0.6:
            return "warning"
        elif score > 0.4:
            return "degraded"
        else:
            return "critical"
```

### Alert Thresholds

Derive alert thresholds from a measured baseline, not fixed percentages of the window:

```python
def build_context_alerts(measured_safe_limit, warning_margin, baseline_relevance_p10):
    """
    *measured_safe_limit*: largest context size with no at-risk probe cell.
    *warning_margin*: fraction below that limit at which to warn, chosen from
    how fast context grows per turn on the workload.
    *baseline_relevance_p10*: 10th-percentile relevance on accepted runs.
    """
    return {
        "utilization_warning": measured_safe_limit * (1 - warning_margin),
        "utilization_critical": measured_safe_limit,
        "relevance_threshold": baseline_relevance_p10,
        "consecutive_warnings": 3  # Debounce; tune from baseline noise
    }
```

## Recovery Procedures

### Context Truncation Strategy

When context degrades beyond recovery, truncate strategically:

```python
def truncate_context_for_recovery(context, preserved_elements, target_size):
    """
    Truncate context while preserving critical elements.
    
    Strategy:
    1. Preserve system prompt and tool definitions
    2. Preserve recent conversation turns
    3. Preserve critical retrieved documents
    4. Summarize older content if needed
    5. Truncate from middle if still over target
    """
    truncated = []
    
    # Category 1: Critical system elements (preserve always)
    system_elements = extract_system_elements(context)
    truncated.extend(system_elements)
    
    # Category 2: Recent conversation (preserve more)
    recent_turns = extract_recent_turns(context, num_turns=10)
    truncated.extend(recent_turns)
    
    # Category 3: Critical documents (preserve key ones)
    critical_docs = extract_critical_documents(context, preserved_elements)
    truncated.extend(critical_docs)
    
    # Check size and summarize if needed
    while len(truncated) > target_size:
        # Summarize oldest category 3 elements
        truncated = summarize_oldest(truncated, category="documents")
        
        # If still too large, truncate oldest turns
        if len(truncated) > target_size:
            truncated = truncate_oldest_turns(truncated, keep_recent=5)
    
    return truncated
```

