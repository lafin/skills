# Catalog Skill Anatomy Audit

- **Review date:** 2026-09-16
- **Reviewer:** automated repository audit
- **Scope:** the 25 skills present before the three admission pilots in `docs/skill-set-improvement-plan.md`; all `SKILL.md` files and all 12 owned Python scripts
- **Method:** inspect each skill against the eight concepts in Section 10.1 of the plan; inspect every script owner against the five fields in Section 10.5; record only repository evidence
- **Disposition vocabulary:** **Pass** means the concept or field is actionable at the cited location. **Pass (N/A)** means the concept does not apply because the skill owns no executable script or needs no progressive-disclosure asset.
- **Result:** 25 of 25 skills pass all applicable anatomy concepts. All 12 script owners pass all five operational fields. No gap remains open.

Each matrix cell is one audit record: the row identifies the skill, the column identifies the concept or field, and the cell gives the disposition and evidence location.

## Anatomy concept key

1. Purpose and owned unit of work
2. Positive triggers in user language
3. Exclusions and adjacent owners
4. Workflow or decision process
5. Failure modes, red flags, or shortcut rationalizations
6. Domain-specific exit evidence and output contract
7. Progressive-disclosure references
8. Status and boundary of executable scripts

## All-skill anatomy review

| Skill | 1 Purpose | 2 Triggers | 3 Exclusions | 4 Process | 5 Failures | 6 Exit/output | 7 References | 8 Scripts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `advanced-evaluation` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — **When to Activate**, **Integration** | Pass — **Evaluation Approaches**, **Practical Guidance** | Pass — **The Bias Landscape**, **Gotchas** | Pass — **Evaluation Pipeline Design**, output-format examples | Pass — **References** | Pass — **`evaluation_example.py`** |
| `ai-stage-gate` | Pass — opening scope paragraph | Pass — **Activation** | Pass — **Activation**, sibling boundary in opening text | Pass — **Mandatory First Step**, `references/review-workflow.md` | Pass — **Missing-artifact gate**, `references/gate-decisions.md` | Pass — **Default Output** | Pass — **Reference Routing** | Pass (N/A) — no `scripts/*.py` |
| `bdi-mental-states` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — **Use BDI Only When Mental-State Semantics Matter**, **Integration** | Pass — **Build a BDI Model in Six Passes** | Pass — **Gotchas** | Pass — pass 5 and pass 6 of the six-pass workflow | Pass — **References** | Pass (N/A) — no `scripts/*.py` |
| `context-compression` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — **When to Activate**, **Integration** | Pass — **Apply the Three-Phase Compression Workflow**, **Implement Anchored Iterative Summarization** | Pass — **Gotchas** | Pass — **Evaluate Compression with Probes**, six-dimension score contract | Pass — **References** | Pass — **`compression_evaluator.py`** |
| `context-degradation` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — **Integration** | Pass — **The Four-Bucket Mitigation Framework** | Pass — **Gotchas** | Pass — diagnostic examples and `analyze_agent_context` report contract | Pass — **References** | Pass — **`degradation_detector.py`** |
| `context-fundamentals` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — **Integration** | Pass — **Reasoning About a Context Decision**, **Reading Order For New Contributors** | Pass — **Gotchas** | Pass — conceptual answer boundary in **Integration** and example outputs | Pass — **References** | Pass — **`context_manager.py`** |
| `context-optimization` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — **Integration** | Pass — **Optimization Decision Framework** | Pass — **Gotchas** | Pass — **Performance Targets** | Pass — **References** | Pass — **`compaction.py`** |
| `evaluation` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — **When to Activate**, **Integration** | Pass — **Building Evaluation Frameworks** | Pass — **Avoiding Evaluation Pitfalls**, **Gotchas** | Pass — rubric, regression, and production-monitoring report contracts | Pass — **References** | Pass — **`evaluator.py`** |
| `filesystem-context` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — **Integration** | Pass — six filesystem patterns and **When to Use Filesystem Context** | Pass — **Gotchas** | Pass — file-reference, plan, and token-accounting contracts | Pass — **References** | Pass — **`filesystem_context.py`** |
| `harness-engineering` | Pass — opening paragraph and **Harness Boundary** | Pass — **When to Activate** | Pass — **When to Activate**, **Integration** | Pass — **Autoresearch-Style Loop**, **Research-To-Skill Loop** | Pass — **Metric Gaming Resistance**, **Gotchas** | Pass — **Harness Design Checklist**, durable results-log contract | Pass — **References** | Pass (N/A) — no `scripts/*.py` |
| `hosted-agents` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — boundary example and **Integration** | Pass — **Hosted Agent Design Checklist** | Pass — **Gotchas** | Pass — **Metrics That Matter**, session lifecycle example | Pass — **References** | Pass — **`sandbox_manager.py`** |
| `latent-briefing` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — negative routes in **When to Activate**, **Integration** | Pass — **Decision Framework**, **Practical Guidance** | Pass — **Gotchas** | Pass — task accuracy, token, retention, overhead, and latency measures in **Practical Guidance** | Pass — **References** | Pass (N/A) — no `scripts/*.py` |
| `leancode` | Pass — opening four-reflex contract | Pass — frontmatter description and **Persistence** mode triggers | Pass — **When NOT to be lazy**, **Boundaries** | Pass — four numbered reflex sections | Pass — prohibited abstractions and safety exceptions | Pass — **Goal-Driven Execution**, **Output** | Pass (N/A) — short self-contained skill; no deep asset needed | Pass (N/A) — no `scripts/*.py` |
| `leancode-audit` | Pass — opening sentence | Pass — frontmatter user-language triggers | Pass — **Scan scope**, **Boundaries** | Pass — **Scan scope**, **Hunt** | Pass — tagged hunt list and excluded surfaces | Pass — **Output** | Pass (N/A) — short self-contained skill; no deep asset needed | Pass (N/A) — no `scripts/*.py` |
| `leancode-debt` | Pass — opening scan contract | Pass — frontmatter user-language triggers | Pass — scan exclusions and **Boundaries** | Pass — **Scan** | Pass — malformed-marker treatment and excluded surfaces | Pass — **Output** | Pass (N/A) — short self-contained skill; no deep asset needed | Pass (N/A) — no `scripts/*.py` |
| `leancode-review` | Pass — opening sentence | Pass — frontmatter user-language triggers | Pass — **Boundaries** | Pass — **Format**, tagged review rules | Pass — examples of weightless findings and protected checks | Pass — **Format**, **Scoring** | Pass (N/A) — short self-contained skill; no deep asset needed | Pass (N/A) — no `scripts/*.py` |
| `long-horizon-prompting` | Pass — opening paragraphs | Pass — **When to Activate** | Pass — negative routes in **When to Activate**, **Integration** | Pass — **Brief-Writing Workflow** | Pass — **Gotchas**, non-counting outcomes | Pass — reporting and return contracts in **Anatomy of a Long-Horizon Brief** | Pass — **References** | Pass (N/A) — no `scripts/*.py` |
| `lossless-doc-compress` | Pass — opening scope paragraphs | Pass — **Activation** | Pass — activation exclusions and preservation boundary | Pass — reference-routed pass order and stopping rule | Pass — preservation invariant, severity rules, untrusted-document warning | Pass — **Default Output** | Pass — reference-routing section | Pass (N/A) — no `scripts/*.py` |
| `memory-systems` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — **Integration** | Pass — **Choosing a Memory Architecture** | Pass — **Gotchas** | Pass — retrieval-quality and temporal-validity evidence in **Practical Guidance** | Pass — **References** | Pass — **`memory_store.py`** |
| `ml-system-design-review` | Pass — opening scope paragraph | Pass — **Activation** | Pass — evidence-mode and neighboring-skill boundaries | Pass — evidence mapping and reference-routed review workflow | Pass — **Severity**, untrusted-artifact warning | Pass — **Default Output** | Pass — reference-routing section | Pass (N/A) — no `scripts/*.py` |
| `multi-agent-patterns` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — negative routes in **When to Activate**, **Integration** | Pass — pattern selection and handoff guidance | Pass — **Failure Modes and Mitigations**, **Gotchas** | Pass — coordination protocol and comparison evidence in **Guidelines** | Pass — **References** | Pass — **`coordination.py`** |
| `project-development` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — negative routes in **When to Activate**, **Integration** | Pass — **Project Planning Template** and staged-pipeline guidance | Pass — **Gotchas** | Pass — prototype, stage artifacts, and cost estimate contracts | Pass — **References** | Pass — **`pipeline_template.py`** |
| `self-improvement-loops` | Pass — opening paragraphs | Pass — **When to Activate** | Pass — negative routes in **When to Activate**, **Integration** | Pass — **Anatomy of a Failure-Driven Self-Edit Loop** | Pass — reward-hacking sections and **Gotchas** | Pass — two-split acceptance and transition-log contract | Pass — **References** | Pass (N/A) — no `scripts/*.py` |
| `simplified-engineering-english` | Pass — opening paragraph and **Scope** | Pass — **Scope** | Pass — negative routing in **Scope** | Pass — **Rewrite Workflow** | Pass — **Conflicts and Ambiguity** and artifact-card safeguards | Pass — **Verification and Reporting** | Pass — **References** | Pass (N/A) — no `scripts/*.py` |
| `tool-design` | Pass — opening paragraph and **Core Concepts** | Pass — **When to Activate** | Pass — negative routes in **When to Activate**, **Integration** | Pass — **Tool Selection Framework** | Pass — failure-mode examples and **Gotchas** | Pass — schema, response, and error contracts in **Detailed Topics** | Pass — **References** | Pass — **`description_generator.py`** |

## Script operational field key

- **Status:** production helper, evaluator, example, or an explicit non-production template
- **Boundary:** what the script transforms or validates and what it does not prove
- **Run:** exact repository-root command and required inputs
- **Output:** stable human-readable or machine-readable result
- **Failure:** non-zero conditions and a repair direction

## Script-owner operational review

| Skill | Status | Boundary | Run | Output | Failure | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| `advanced-evaluation` | Pass — **`evaluation_example.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed |
| `context-compression` | Pass — **`compression_evaluator.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed |
| `context-degradation` | Pass — **`degradation_detector.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed |
| `context-fundamentals` | Pass — **`context_manager.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed |
| `context-optimization` | Pass — **`compaction.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed |
| `evaluation` | Pass — **`evaluator.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed |
| `filesystem-context` | Pass — **`filesystem_context.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed |
| `hosted-agents` | Pass — **`sandbox_manager.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed; replacement points retained |
| `memory-systems` | Pass — **`memory_store.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed |
| `multi-agent-patterns` | Pass — **`coordination.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed |
| `project-development` | Pass — **`pipeline_template.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed; replacement points retained |
| `tool-design` | Pass — **`description_generator.py`** | Pass — same section | Pass — same section | Pass — same section | Pass — same section | Closed |

## Remediation disposition

| Gap found | Evidence | Disposition |
| --- | --- | --- |
| Six links in `evaluation`, `multi-agent-patterns`, and `tool-design` depended on another skill's case-study asset. | `evaluation/references/multi-agent-research-evidence.md`; `multi-agent-patterns/references/multi-agent-research-evidence.md`; `tool-design/references/d0-evidence.md` | Closed. Each owner now carries only the dated claim, source URL, scope, and limitation it cites. |
| The 12 script-owner documents lacked complete, consistently actionable operational contracts. | The 12 script sections listed above; `tests/test_script_contracts.py` | Closed. Each section states Status, Boundary, exact Run command and inputs, Output, and Failure with repair direction. Template replacement points remain explicit. |
| No other objective or documentary anatomy gap was found. | All-skill matrix above | Closed. No cosmetic heading rewrite was performed. |
