# Vercel d0 Architectural Reduction Evidence

## Evidence: Vercel d0 Architectural Reduction (December 2025)

**Source:** [Vercel Engineering, "We removed 80% of our agent's tools"](https://vercel.com/blog/we-removed-80-percent-of-our-agents-tools), published December 2025.

**Scope:** Vercel's reported comparison of two text-to-SQL agent architectures on five internal analytics questions.

**Limitation:** This vendor-authored case study uses a small internal evaluation set. It does not establish that tool reduction improves other agents or workloads.

Vercel reported that reducing its d0 architecture from 17 specialized tools to two primitive tools (`ExecuteCommand` and `ExecuteSQL`) changed success from 80% to 100%, average execution time from 274.8 seconds to 77.4 seconds, average token use from about 102,000 to about 61,000, and average steps from about 12 to about 7. Preserve the study's scope and limitation whenever citing these results.
