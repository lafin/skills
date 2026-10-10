# Anthropic Multi-Agent Research Evidence

## Evidence: Anthropic Multi-Agent Research (June 2025)

**Source:** [Anthropic Engineering, "How we built our multi-agent research system"](https://www.anthropic.com/engineering/multi-agent-research-system), published June 2025.

**Scope:** Anthropic's report about its production research system and its BrowseComp analysis.

**Limitation:** This vendor-authored report does not establish a universal token multiplier, performance-driver ranking, or multi-agent scaling law.

Anthropic reported that its multi-agent research system used about 15 times as many tokens as ordinary chat for the studied workload. Its BrowseComp analysis attributed 80% of observed performance variance to token usage; tool calls and model choice contributed additional explanatory power, and the three factors together explained 95% of observed variance. Treat these figures as workload-specific planning and evaluation signals. Measure the target system against a single-agent baseline.

For independent evidence, see the MAST failure taxonomy (<https://arxiv.org/abs/2503.13657>), which classifies 14 failure modes from annotated multi-agent traces, and Kim et al. (<https://arxiv.org/abs/2512.08296>), where multi-agent performance relative to a single agent ranged from +80.8% to −70.0% depending on task structure.
