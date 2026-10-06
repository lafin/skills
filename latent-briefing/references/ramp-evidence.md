# Ramp Labs Latent Briefing Evidence

## Evidence: Ramp Labs Latent Briefing on LongBench v2 (April 2026)

**Source:** [Ramp Labs, "Latent Briefing: Efficient Memory Sharing for Multi-Agent Systems via KV Cache Compaction"](https://labs.ramp.com/research/latent-briefing-kv-cache/index.md), Ben Geist, published 2026-04-10. Checked 2026-10-06.

**Scope:** One recursive language model (RLM) setup: a Claude Sonnet 4 orchestrator and a Qwen3-14B worker on LongBench v2 reading comprehension. Three evaluation conditions of 42 questions each (126 total), each run as an uncompacted baseline and at thresholds `tau` = -1.0, 0.0, 1.0, and 2.0. Head weights were uniform because no optimized Attention Matching budgets exist for Qwen3-14B.

**Limitation:** This vendor-authored writeup uses one benchmark and n=42 per condition with a nondeterministic orchestrator; the author calls individual results noisy. Claude Sonnet 4 was retired from the Claude API on 2026-06-15 ([model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)), so exact reproduction is not possible. This repository did not reproduce the results.

Ramp reported a 65% reduction in worker-model token consumption. At the best threshold for each condition, accuracy rose 3 percentage points over the uncompacted baseline, median worker tokens fell 42–57%, and median total tokens fell 21–31%. The best threshold differed by condition. Median compaction overhead was about 1.7 seconds and grew linearly with input length. The per-condition tables are images in the source and are not transcribed here. Preserve the study's scope and limitation whenever citing these results.
