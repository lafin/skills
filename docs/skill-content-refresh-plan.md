# Skill Content Refresh Plan

## 1. Purpose

This plan corrects defects and stale content found in the 2026-10-06 review of all 25 root skills and their four upstream sources. It complements [the skill set improvement plan](skill-set-improvement-plan.md). That plan owns evaluation machinery, routing coverage, anatomy, and new-skill admission. This plan owns the content of existing skills: facts, citations, code examples, scripts, and guidance that recent research or vendor changes made wrong or incomplete.

The work is done when every item in Sections 6–9 is applied, rejected with a recorded reason, or deferred to a named owner decision, and every applied item has passed its verification class in Section 4.

## 2. Baseline

| Field | Value |
|---|---|
| Repository revision | `7529a16` plus the `PD-0` edit (Section 5) |
| Review date | 2026-10-06 |
| Skills reviewed | 25 root skills, `.omp/hooks/pre/leancode.ts`, three staged proposals |
| `python3 scripts/validate_skills.py` | passed |
| Agent Skills spec conformance | All `SKILL.md` files are under 500 lines, all descriptions are 1024 characters or fewer, and all references are one level deep. `tool-design` body is about 5.2k tokens (chars/4 estimate), above the spec's ~5k recommendation. Source: <https://agentskills.io/specification> |

Line numbers below refer to the baseline revision. Re-read each location before editing. Items marked **[INFERENCE]** were not verified against a primary source and need verification before change.

## 3. Upstream Drift

| Source | Pinned | Upstream HEAD on 2026-10-06 | Delta that touches local skills | Disposition |
|---|---|---|---|---|
| `muratcankoylan/Agent-Skills-for-Context-Engineering` | `c578e85e40fe2bda7c1fec91ff64cf5285434934` | `58b55a8921758d13453b440704fb1b5b208c0b0e` (v2.6.0) | New `self-managed-context` skill. Reciprocal routing lines in `context-compression`, `context-optimization`, `filesystem-context`, `self-improvement-loops`. One prefix-cache sentence in `context-optimization`. Retired model ID in `project-development/scripts/pipeline_template.py` (commit `0416003a`). Governance, researcher, and schema infrastructure outside `skills/`. | Model ID applied (`PD-0`). Prefix-cache sentence adopted as `CO-8`. Skill import deferred (`RP-4`). Routing lines to the non-imported skill rejected. Infrastructure out of scope per the Section 3.2 non-goals of the skill set plan. |
| `ML-SystemDesign/MLSystemDesign` | per-skill commits in [ATTRIBUTION](../ATTRIBUTION.md) | `8dd0d88852fe7445e9d2627c59124f0f161040c1` | None under `skills/lossless-doc-compress`, `skills/ml-system-design-review`, or `skills/ai-stage-gate`. | No sync. Local fix `LDC-1` should also go upstream (`RP-6`). |
| `multica-ai/andrej-karpathy-skills` | `8462496b34419f20b32778610571ac723e91f94c` | `2c606141936f1eeef17fa3043a72095b4765b9c2` | `CLAUDE.md` unchanged. New `skills/karpathy-guidelines/SKILL.md` is `CLAUDE.md` plus frontmatter. New `EXAMPLES.md` (~520 lines; Goal-Driven Example 3 has identical ❌ and ✅ bodies). | Nothing to adopt. |
| `addyosmani/agent-skills` | `be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39` | `1401c8b8030e023baeebb31781a6653fe8e93026` | `api-and-interface-design` fixes `throw;` → `throw e;` (absent from the local proposal). `docs/skill-anatomy.md` adds a model-neutral procedure rule and restricts top-level frontmatter keys to the spec set. | Adopt both anatomy rules (`RP-1`). No proposal change needed. |

## 4. Change Classes and Gates

Each item has one class. The class sets the gate.

| Class | Scope | Gate |
|---|---|---|
| **D** — defect | Wrong facts, citations, numbers, model IDs, code examples, scripts, and metadata. Includes corrections inside a `SKILL.md` body when the instruction's intent does not change. | Section 10.1 deterministic checks plus the item's smoke check. No live evaluation. |
| **G** — guidance | Adds, removes, or changes what a skill tells the agent to do. | One development behavior case that observes the new behavior, run baseline versus treatment under the skill set plan §18.2. Holdout follows the same section. Evaluation-case additions land in a separate commit before the skill change (skill set plan §16). |
| **R** — routing | Description text or "Do not activate" lists. | Canonical routing development and holdout pairs under the skill set plan §11, one skill or confusable family per treatment. |

Leancode-family **G** items also follow the candidate gate in [the Leancode improvement plan](leancode-improvement-plan.md). `simplified-engineering-english` **G** items also follow its release governance in the skill set plan §9.1.

Model-neutral rule (from `RP-1`): prose and reference examples use placeholders such as `JUDGE_MODEL`, not vendor model IDs. Executable script defaults may name a current model ID only when the script is a mock or template and the value matches upstream.

## 5. Already Applied

- **PD-0** · D · `project-development/scripts/pipeline_template.py:32,278,763` — Replaced retired `claude-sonnet-4-20250514` with `claude-sonnet-4-6`, matching upstream `0416003a`. Verified: `--help` runs and `python3 -m unittest tests.test_script_contracts` passes. Metadata still pins `c578e85`; `RP-2` resolves that.

## 6. Wave 1 — Repository Hygiene

Run first. These items change no skill behavior.

- **RP-1** · D · `docs/skill-anatomy.md`, `CONTRIBUTING.md`, `scripts/validate_skills.py`, `tests/test_validate_skills.py`
  - Add the model-neutral rule: a step that cannot be justified without naming a model, model version, or one host's private tool name does not belong in a skill.
  - Add a hard validator error for top-level frontmatter keys outside `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. All 25 skills pass this today.
  - Add one validator test with a disallowed key.
  - Source: upstream `addyosmani/agent-skills` `docs/skill-anatomy.md` at `1401c8b`; <https://agentskills.io/specification>.
- **RP-2** · D · 17 context-engineering `SKILL.md` frontmatters, `ATTRIBUTION.md`, `README.md`
  - Bump `metadata.upstream_commit` to `58b55a8921758d13453b440704fb1b5b208c0b0e` for all 17 skills. The 12 skills that upstream did not touch have identical upstream content at both commits. The 5 touched skills keep `adaptation: modified`.
  - In `ATTRIBUTION.md`, record the new fetched commit and the Section 3 disposition: adopted `PD-0` and `CO-8`; did not import `self-managed-context` or its reciprocal routing lines.
- **RP-3** · D · `docs/skill-set-improvement-plan.md`
  - §10.4 (line 443), §15.2 (line 729), and the file-change map (line 865): no cross-skill asset links into `project-development/references/case-studies.md` remain in `evaluation`, `multi-agent-patterns`, or `tool-design`. Mark the migration complete.
  - Line 320: replace the `leancode-debt` oracle "extracts only syntactically valid debt markers" with "extracts every `lean-debt:` marker with its ceiling and revisit trigger, flags incomplete markers `no-ceiling` or `no-trigger`, and edits no source". The current text conflicts with `leancode-debt/SKILL.md:41-42`.
- **RP-4** · D · `docs/conditional-skill-decisions.md`
  - Add a `self-managed-context` section. Decision: **DEFER import**.
  - Evidence: the upstream skill is 276 lines, ~3,460 words (near the ~5k-token body ceiling), plus 23 KB of references. Its results rest on one paper (CLM, <https://arxiv.org/abs/2609.37725>, 2026-09-29). OMP exposes no model-editable live context, so no local task needs the skill.
  - Port its three general rules into existing owners instead: edit-position cost (`CO-8`), deterministic budget readouts (`CO-4`), summary text as untrusted data (`CC-4`, `CD-5`).
  - Revisit when a target host exposes model-editable context, or when an independent replication of the CLM results is published.
- **RP-5** · D · `CONTRIBUTING.md`
  - Add a recurring upstream drift check. Run it before each catalog release:

    ```sh
    gh api "repos/<owner>/<repo>/compare/<pinned-sha>...HEAD" \
      --jq '.files[] | select(.filename | startswith("skills/")) | "\(.status) \(.filename)"'
    ```

  - Record each delta's disposition in `ATTRIBUTION.md`.
- **RP-6** · owner decision · upstream contributions
  - Offer `LDC-1` to `ML-SystemDesign/MLSystemDesign`. Offer the shared defects in `EV-1`, `AE-1`, `AE-3`, `MS-1`, `MS-2`, and `MAP-2` to `muratcankoylan/Agent-Skills-for-Context-Engineering`, where the same files exist.

## 7. Wave 2 — Defect Fixes (Class D)

Group commits by skill family. One commit per family keeps review small and revert easy.

### 7.1 Leancode family and hook

- **LC-1** · `leancode/SKILL.md:183` — "a PCA9685 runs a few percent fast" is wrong. The oscillator lands anywhere from about 23 to 27 MHz around the nominal 25 MHz, in either direction. **Change:** state that range. Keep the paragraph. Source: <https://raw.githubusercontent.com/adafruit/Adafruit-PWM-Servo-Driver-Library/master/examples/servo/servo.ino> lines 49–64.
- **LD-1** · see `RP-3`.
- **HK-2** · `.omp/hooks/pre/leancode.ts:15-20,36-57` — **[INFERENCE]** The reminder filter and legacy-migration code may be dead. Reason: the hook uses the `context` event, which changes the LLM context for one call and does not write reminders to session history. The first hook version (`8d25b71`) also used `context`. **Change:** add one `evals/mode_smoke.py` assertion that `event.messages` never contains a prior hook reminder. If it holds across all four modes, delete `LEGACY_REMINDERS`, `isLeancodeStateMessage`, the filter, and their tests (`tests/leancode_hook.test.ts:5-8,122-189`). If it fails, generate `LEGACY_REMINDERS` from `leancodeReminder()` so the reminder text exists in one place. Check: `bun test tests/leancode_hook.test.ts` and `mode_smoke.py`.

### 7.2 Context core

- **CF-1** · `context-fundamentals/references/context-components.md:229-235`, `context-fundamentals/scripts/context_manager.py:79`, `context-optimization/scripts/compaction.py:85`, and the other scripts that use `len(text) // 4` — The 4 chars/token estimate undercounts by about 35–40% on the Claude tokenizer introduced with Opus 4.7 (1M tokens ≈ 2.5M characters). **Change:** state that the ratio depends on the tokenizer. Accept a token-counting function as a parameter, and keep `len // 4` only as a labeled fallback. Source: <https://platform.claude.com/docs/en/models/overview>.
- **CF-3** · `context-fundamentals/references/context-components.md:178-189` — `inject_summaries` appends a summary every 20 messages but keeps the summarized messages, so context grows. It also inserts mid-conversation `system` messages, which not every model accepts. **Change:** replace the summarized span with the summary, use a user-role message, or delete the example and link `context-compression`.
- **CF-4** · `context-fundamentals/scripts/context_manager.py:345`, `references/context-components.md:243-244` — The fixed 80,000-token "recommended limit" and fixed budget ranges contradict `SKILL.md:81`. **Change:** make the limit a required parameter, or label it as a demo value.
- **CF-5** · `context-fundamentals/SKILL.md:216-218` — External resources have no URLs. **Change:** link Liu et al. 2023 (<https://arxiv.org/abs/2307.03172>), Chroma Context Rot (<https://www.trychroma.com/research/context-rot>), NoLiMa (<https://arxiv.org/abs/2502.05167>), and Anthropic's context-window docs (<https://platform.claude.com/docs/en/build-with-claude/context-windows>).
- **CD-1** · `context-degradation/references/patterns.md:12-38,45-78,262-268` — The code hard-codes the first and last 10% of positions as "attention favored", needs attention weights that closed APIs do not expose, and fixes alerts at 70% and 90%. This contradicts `SKILL.md:35,87`. **Change:** replace it with a behavioral probe (recall by position and length). Make the thresholds parameters taken from a measured baseline.
- **CD-2** · `context-degradation/SKILL.md:93-97,236-238` — The three "counterintuitive findings" are Chroma's Context Rot results (July 2025, 18 models) and are uncited. **Change:** cite Chroma and NoLiMa.
- **CD-6** · `context-degradation/SKILL.md:61` — "the original errors retain attention weight" states a mechanism without a source. **Change:** "corrections layered on top are often ignored; measure on the target workload".
- **CD-7** · `context-degradation/SKILL.md:109-119` — **[INFERENCE]** The Write/Select/Compress/Isolate taxonomy appears to come from LangChain's 2025 context-engineering post. **Change:** verify the source, then attribute it or reword.
- **CC-1** · `context-compression/SKILL.md:15,35-47,103-125,176-220` — The skill restates Factory's "Evaluating Context Compression for AI Agents" (2025-12-16) without citing it. **Change:** restore the citation. Source: <https://factory.com/news/evaluating-compression>.
- **CC-2** · `context-compression/SKILL.md:37` — "This prevents drift" overstates the source, which says "less likely to drift". The anchored method scored 2.45/5 on artifact trail, and its overall lead was 0.26–0.35 on a 0–5 scale. **Change:** "reduces drift", with the effect size.
- **CC-5** · `context-compression/SKILL.md:280` — The talk is "The Infinite Software Crisis" by Jake Nations, AI Engineer Code 2025, not "Netflix Engineering, AI Summit 2025". **Change:** correct and link <https://ai.engineer/talks/eIoohUmYpGI-infinite-software-crisis>.
- **CC-6** · `context-compression/scripts/compression_evaluator.py:345,473-474` — The judge model is hard-coded to `gpt-5.2`. **Change:** make the judge model a required argument (model-neutral rule). Check: `python3 -m unittest discover -s context-compression/tests`.
- **CC-7** · `context-compression/SKILL.md:39` — Optional. Cite JetBrains (<https://arxiv.org/abs/2605.11051>): an embedding-based compressor succeeds on single-shot tasks and fails on multi-step agentic coding.
- **CO-5** · `context-optimization/SKILL.md:132,160`, `scripts/compaction.py:421` — Two different fixed trigger thresholds (0.8 and 70%) contradict `SKILL.md:84`. **Change:** use one named `measured_safe_limit` parameter.
- **CO-6** · `context-optimization/references/optimization_techniques.md:162-164` — "Place critical information at attention-favored positions (beginning and end)" contradicts the measure-first rule. **Change:** "test placement; use the measured best position".

### 7.3 Systems

- **MS-1** · `memory-systems/SKILL.md:127-132`, `references/implementation.md:492-505` — The Mem0 v3 API puts entity IDs inside `filters=`, and `add` takes a messages list. The claim that Mem0 returns only the current preference is unsupported: `add` is add-only. **Change:** use `m.add(messages, user_id=...)` and `m.search(q, filters={"user_id": ...})`, remove the supersession claim, and record the SDK version. Sources: <https://docs.mem0.ai/core-concepts/memory-operations/search>, <https://docs.mem0.ai/core-concepts/memory-operations/add>.
- **MS-2** · `memory-systems/references/implementation.md:515-523` — Graphiti `add_episode` requires `reference_time`. **Change:** add `reference_time=datetime.now(timezone.utc)`. Source: <https://raw.githubusercontent.com/getzep/graphiti/main/graphiti_core/graphiti.py>.
- **MS-3** · `memory-systems/SKILL.md:95`, `references/implementation.md:234-237,303,361-374,390-402` — The "working consolidation code" calls undefined methods (`update_validity_periods`, `rebuild_indexes`, `_get_edge`, `_extract_label`, `_extract_type`, `_extract_where`) and deletes edges. Deleting edges breaks the skill's "invalidate, do not discard" rule (`SKILL.md:95,178`). **Change:** set `valid_until` instead of deleting, and either define the methods or label the block as pseudocode.
- **MS-4** · `memory-systems/SKILL.md:137-150`, `references/implementation.md:309`, `scripts/memory_store.py:383` — `query_at_time` has two signatures. **Change:** use the script's dict form everywhere.
- **MS-5** · `memory-systems/SKILL.md:156,164,168`, `references/implementation.md:533-541` — Cognee v1.0 lists `memify()` as a legacy operation (replaced by `improve()`), and the default `query_type` is `HYBRID_COMPLETION`. **Change:** update and date the examples. Sources: <https://docs.cognee.ai/core-concepts/main-operations/legacy-operations/memify.md>, <https://docs.cognee.ai/python-api/search.md>.
- **MS-7** · `memory-systems/SKILL.md:21,106` — The Letta Filesystem API is deprecated and disabled. **Change:** date the Letta guidance and name its replacement. Source: <https://docs.letta.com/v1-sdk/concepts/filesystem>. Also correct the MemBench venue to Findings of ACL 2025 (<https://aclanthology.org/2025.findings-acl.989/>).
- **FC-1** · `filesystem-context/references/implementation-patterns.md:243-253` — The `SkillLoader` block uses `@dataclass` and `field` without importing them. **Change:** add `from dataclasses import dataclass, field`.
- **FC-3** · `filesystem-context/references/implementation-patterns.md:545-548` — The targets (<20%, >50%, >70%) have no source. **Change:** label them as illustrative or delete them.
- **FC-4** · `filesystem-context/SKILL.md:135` — "O(n) static token cost into O(1)" is wrong; the index stays O(n). **Change:** "O(n) one-line index plus O(k) loaded bodies".
- **FC-5** · `filesystem-context/SKILL.md:102,305-308` — The external resources have no URLs, and the "recitation" quote has no attribution. **Change:** add URLs (<https://agentskills.io/specification>, <https://www.letta.com/blog/benchmarking-ai-agent-memory>). Verify and attribute the quote (**[INFERENCE]**: likely the Manus context-engineering post).
- **TD-4** · `tool-design/references/architectural_reduction.md:11-48` — The block wraps the TypeScript-only AI SDK in Python syntax and uses the invalid model ID `"claude-opus-4.5"`. **Change:** replace it with model-neutral pseudocode, or quote the TypeScript source labeled "as published December 2025". Source: <https://vercel.com/blog/we-removed-80-percent-of-our-agents-tools>.
- **TD-5** · `tool-design/SKILL.md:53`, `references/best_practices.md:117` — Two research claims have no citation. **Change:** cite <https://www.anthropic.com/engineering/advanced-tool-use> or soften.
- **LB-1** · `latent-briefing/SKILL.md:160`, `references/attention-matching-formulation.md:7` — The primary source is an X post. **Change:** cite Ramp Labs, "Latent Briefing", Ben Geist, 2026-04-10: <https://labs.ramp.com/research/latent-briefing-kv-cache/index.md>.
- **LB-2** · `latent-briefing/SKILL.md:27,89-97,136` — The skill tells readers to interpret results it never states. **Change:** add a dated evidence block in `references/`, in the style of `tool-design/references/d0-evidence.md`: Claude Sonnet 4 orchestrator, Qwen3-14B worker, LongBench v2, n=42 per condition, ~65% fewer worker tokens, +3 pp at the best threshold, uniform head weights. State that the orchestrator model is retired, so exact reproduction is not possible.
- **LB-4** · `latent-briefing/SKILL.md:45,70`, reference line 59 — The threshold is called `tau` in one file and `k` in the other. **Change:** use one name, and state that negative thresholds keep more than the median.
- **BDI-1** · `bdi-mental-states/SKILL.md:161-179`, `references/rdf-examples.md:166-176`, `references/framework-integration.md:480-498`, `references/sparql-competency.md:206-210` — `hasStartTime` and `hasEndTime` are object properties with range `:TimeInstant`. Queries compare them directly to `xsd:dateTime` literals and return nothing. **Change:** use `?interval bdi:hasStartTime/bdi:time ?s`, and model instants as IRIs that carry `bdi:time`. Source: <https://w3id.org/fossr/ontology/bdi/>.
- **BDI-2** · `bdi-mental-states/references/bdi-ontology-core.md:107-112` — `owl:maxCardinality 1` on `hasValidity` is not in the published ontology, which uses an existential restriction. **Change:** use the existential form or label the restriction a local extension.
- **BDI-3** · `bdi-mental-states/SKILL.md:295-299`, `references/sparql-competency.md:163-170` — CQ4 orders by IRI, and the transitive `precedes` returns every successor. **Change:** walk from `bdi:beginsWith` with non-transitive adjacency.
- **BDI-4** · `bdi-mental-states/SKILL.md:23,369` — **Change:** cite Journal of Web Semantics 2026, DOI `10.1016/j.websem.2026.100885`, arXiv `2511.17162`. Mark the JADE/JADEX mappings as illustrative.
- **BDI-5** · `bdi-mental-states/SKILL.md:217-221` — There is an empty `### Integration Patterns` heading, and `## Detailed Topics` is out of order. **Change:** delete the heading and move the section.

### 7.4 Workflows

- **MAP-1** · `multi-agent-patterns/SKILL.md:167,254,272-274`, `references/frameworks.md:91-249` — AutoGen is in maintenance mode, the GroupChat snippet uses undefined names, and the "CrewAI-style" section is plain Python. **Change:** point to Microsoft Agent Framework, add OpenAI Agents SDK handoffs and Claude Agent SDK subagents, and label the CrewAI section as a generic sketch. Sources: <https://github.com/microsoft/autogen>, <https://openai.github.io/openai-agents-python/handoffs/>, <https://code.claude.com/docs/en/agent-sdk/subagents>.
- **MAP-2** · `multi-agent-patterns/references/frameworks.md:70-88,147-192` — The LangGraph supervisor example has no `END` and loops. The swarm example uses static edges and an undefined `State`. `langgraph-supervisor` is unmaintained. **Change:** rewrite against `Command(goto=..., graph=Command.PARENT)`, or reduce both to labeled pseudocode with links. Source: <https://docs.langchain.com/oss/python/migrate/langgraph-supervisor>.
- **MAP-5** · `multi-agent-patterns/SKILL.md:86-106` — "eliminate translation errors entirely" is unsupported. **Change:** attribute it to LangChain's τ-bench study, where swarm narrowly beat supervisor and both trailed a single agent. Lead with passing artifacts by reference. Sources: <https://www.langchain.com/blog/benchmarking-multi-agent-architectures>, <https://www.anthropic.com/engineering/multi-agent-research-system>.
- **MAP-6** · `multi-agent-patterns/scripts/coordination.py:179,374-387,399,444,483-485` — `consensus_strength` divides by the vote count instead of the total weight (the demo prints 0.57; the correct value is 0.74). No expertise factor exists despite the docstring. `transfer_with_state` drains the whole inbox and never receives an ack. Subtask IDs are never set. **Change:** normalize by total weight, correct the docstrings, filter for acks, and assign IDs. Check: run the script and confirm 0.74.
- **MAP-7** · `multi-agent-patterns/references/frameworks.md:292-318` — The file lock checks and then opens (a race), never creates `locks/`, and lacks imports. **Change:** use `os.open(path, os.O_CREAT | os.O_EXCL)`, or link `filesystem-context`.
- **MAP-8** · `multi-agent-patterns/SKILL.md:275`, `references/multi-agent-research-evidence.md:5,11` — arXiv 2308.00352 is MetaGPT, not multi-agent theory or evaluation. The Anthropic URL redirects. **Change:** cite MAST (<https://arxiv.org/abs/2503.13657>) and <https://arxiv.org/abs/2512.08296>, and use the canonical Anthropic URL.
- **HA-1** · `hosted-agents/references/infrastructure-patterns.md:3,11-61,91-122,181-194,312-334` — The Modal snippets use APIs that do not exist. Snapshots use `snapshot_filesystem()` and restore through `Sandbox.create(image=...)`, `exec` takes argv, Modal 1.0 dropped `__init__` on `@app.cls`, and OpenCode installs from npm as `opencode-ai`. **Change:** replace them with one short example against the current SDK, and delete the "production systems at scale" claim. Sources: <https://modal.com/docs/guide/sandbox-snapshots>, <https://modal.com/docs/guide/modal-1-0-migration>, <https://opencode.ai/docs/>.
- **HA-2** · `hosted-agents/scripts/sandbox_manager.py:416-423` — `if warm:` is checked before `elif snapshot_id:`. A follow-up prompt therefore gets a warm sandbox and loses the session's work. **Change:** prefer `snapshot_id`. Check: a throwaway script that creates a session, snapshots it, warms the pool, and sends a follow-up.
- **HA-3** · `hosted-agents/scripts/sandbox_manager.py:479-484,530-550`, `references/infrastructure-patterns.md:51-52,532-537` — Every waiter flushes the queued writes again, so a stale write can overwrite a newer one. The git display name is interpolated into a shell string (injection). **Change:** wait for the sync event and write once. Pass git identity as argv.
- **HA-5** · `hosted-agents/references/infrastructure-patterns.md:205-305` — The Durable Object example uses `server.accept()`, which prevents hibernation, keeps state in a `Map` that hibernation loses, passes an array to `sql.exec`, and calls an undefined `forwardToSandbox`. **Change:** use `ctx.acceptWebSocket()` and spread bindings, or reduce the example to a schema plus a link. Sources: <https://developers.cloudflare.com/durable-objects/best-practices/websockets/>, <https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/>.
- **HA-7** · `hosted-agents/references/infrastructure-patterns.md:341-384,699`, `SKILL.md:308,310`, `scripts/sandbox_manager.py` — The Slack bot defines async handlers on a sync `App`, hard-codes `gpt-4o-mini`, links to redirecting URLs, and calls `datetime.utcnow()` (deprecated since Python 3.12). **Change:** use `AsyncApp`, a model placeholder, current links, and `datetime.now(timezone.utc)`.
- **HE-4** · `harness-engineering/SKILL.md:221-227` — The references have no URLs or dates. That contradicts the skill's own Gotcha 8. **Change:** add both.
- **LH-1** · `long-horizon-prompting/references/cdc-prompt-annotated.md:5,10`, `SKILL.md:103` — The CDC proof now has a kernel-checked Lean formalization and arXiv expositions. **Change:** update the provenance. Keep the "prompt contribution not ablated" caveat. Sources: <https://github.com/openai/cdc-lean>, <https://arxiv.org/abs/2607.15399>, <https://arxiv.org/abs/2607.16356>.
- **LH-3** · `long-horizon-prompting/references/research-evidence.md:9` — PushBench reports retrieval controllers at 69–78% and backlog controllers at 25–50%, not "backlog 69–78%". The stuck-loop claim is not in the abstract. **Change:** report the two controllers separately, and verify or delete the stuck-loop sentence. Source: <https://arxiv.org/abs/2605.23574>.
- **LH-4a** · `long-horizon-prompting/references/vendor-guidance.md:32,36-56,99-109` — The OpenAI URLs moved. **Change:** pin <https://developers.openai.com/api/docs/guides/latest-model/gpt-5.6.md> and <https://developers.openai.com/api/docs/guides/responses-multi-agent>.
- **LH-5** · `long-horizon-prompting/SKILL.md:68,232`, `references/vendor-guidance.md:65` — **Change:** cite the GPT-5.6 system card directly for "cheating is more pronounced with system prompts that emphasize sustained persistence". Source: <https://deploymentsafety.openai.com/gpt-5-6/metagaming-in-training>.
- **LH-6** · `long-horizon-prompting/references/research-evidence.md:11,17,36` — **Change:** correct the METR quote ("combined with better logical reasoning"), correct the paper title to "Evaluating…" (<https://arxiv.org/abs/2602.18998>), add Time Horizon 1.1 and its >16 h reliability caveat (<https://metr.org/blog/2026-1-29-time-horizon-1-1/>, <https://metr.org/time-horizons/>), and narrow the "nothing in training supplies stopping" claim to its single survey source (<https://arxiv.org/abs/2605.02801>).
- **PD-1** · `project-development/references/pipeline-patterns.md:342,374-375,436` — `gpt-4` and `gpt-4-turbo` shut down on 2026-10-23. The $3/$15 rates are labeled "GPT-4 Turbo" but are Sonnet 4.5/4.6 prices (GPT-4 Turbo is $10/$30). **Change:** remove the model defaults and vendor labels, and make pricing a required input. Sources: <https://developers.openai.com/api/docs/deprecations>, <https://platform.claude.com/docs/en/about-claude/pricing>.
- **PD-2** · `project-development/references/pipeline-patterns.md:340-349`, `scripts/pipeline_template.py:699-705` — `cl100k` and chars/4 undercount on current tokenizers. **Change:** calibrate from prototype usage or a provider token-counting endpoint. Same pattern as `CF-1`.
- **PD-4** · `project-development/references/pipeline-patterns.md:559-609` — The stage tests fail. The indented fixture defeats the header regex, missing sections never add to `parse_errors`, and `stage_acquire(test_dir, [item])` does not match the template signature `stage_acquire(batch_id, limit)`. **Change:** dedent the fixture, record missing-section errors, and align the signatures.
- **PD-5** · `project-development/references/case-studies.md:229,269-301`, `SKILL.md:182,312` — The Manus blog says four refactors, not five. The "five" and the sub-agent details come from Lance Martin's notes, which also say Manus dropped `todo.md`. **Change:** attribute each claim to its source, and state that `todo.md` was superseded. Sources: <https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus>, <http://rlancemartin.github.io/2025/10/15/manus>.
- **PD-7** · `project-development/references/case-studies.md:237-243` — **Change:** date the cached-price example (July 2025) and say "10× or more, depending on model".
- **PD-8** · `project-development/scripts/pipeline_template.py:701,722`, `SKILL.md:142,214`, `references/pipeline-patterns.md:369`, `references/case-studies.md:128` — The retry buffer is fixed at 20–30%, contradicting "derive from observed failure rates". Output tokens are 500 in one place and 1000 in another. The "5-minute test" has no source. **Change:** make both values inputs, and delete "5-minute".
- **SIL-1** · `self-improvement-loops/SKILL.md:65,210`, `references/loop-design-evidence.md:75` — In DGM, the checker was hidden, and hacking still occurred; a lineage audit caught it. The fabricated "tests passed" log was the base-model behavior DGM was asked to fix. **Change:** "hiding the checker reduces hacking but does not prevent it". Source: <https://arxiv.org/html/2505.22954v3>.
- **SIL-2** · `self-improvement-loops/SKILL.md:76,216`, `references/loop-design-evidence.md:21,27` — Self-Harness v3 adds SWE-bench Verified and AppWorld (9/9 pairs improve). The metric is mean single-attempt success over 2 repeats. **Change:** update the scope and the metric wording. Source: <https://arxiv.org/html/2606.09498v3>.
- **SIL-3** · `self-improvement-loops/SKILL.md:215`, `references/loop-design-evidence.md:28` — In Self-Harness, promotion is a deterministic held-out gate, and no agent approves. **Change:** state that.
- **SIL-4** · `self-improvement-loops/SKILL.md:108-109`, `references/loop-design-evidence.md:98` — The AFlow paper reports strong transferability and attributes the ADAS gap to linear search. **Change:** correct both claims. Source: <https://arxiv.org/html/2410.10762v4>.
- **SIL-9** · `self-improvement-loops/references/loop-design-evidence.md:21-133`, `SKILL.md:47,241-250` — 22 "[Evidence context]" self-links carry no information. GEPA appears only in a table. **Change:** delete the self-links, add a GEPA entry (<https://dspy.ai/current/api/optimizers/GEPA/overview/>), and cite METR under Guideline 1 (<https://metr.org/blog/2025-06-05-recent-reward-hacking/>).

### 7.5 Evaluation, writing, and review

- **EV-1** · `evaluation/scripts/evaluator.py:202-245,257-259,437`, `SKILL.md:285-289` — Each dimension without evidence falls back to a default (0.7/0.8/0.8/0.5/0.8). The defaults sum to 0.74, above the 0.7 pass threshold. Empty output and the wrong answer `"London"` both pass. `expected["answer"]` is never read. **Change:** score missing evidence as 0 or `unknown`, read `expected["answer"]`, and make the demo show at least one failure. Check: `python3 evaluation/scripts/evaluator.py` reports at least one failure.
- **EV-2** · `evaluation/SKILL.md:164-170` — `config["weights"]` reads the loop variable after the loop ends. **Change:** `{d: c["weight"] for d, c in rubric.items()}`.
- **EV-5** · `evaluation/SKILL.md:276-279,287-295` — The external resources have no links, and the version footer does not change behavior. **Change:** link <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents> and delete the footer.
- **AE-1** · `advanced-evaluation/references/bias-mitigation.md:9-12` — "~55% first-position preference" does not match MT-Bench Table 2, which shows Claude-v1 at 75.0% first, GPT-3.5 at 50.0%, and GPT-4 at 30.0%, all 2023 models. **Change:** delete the per-vendor numbers. Say that bias varies by judge and prompt, and that swaps on the target judge measure it. Source: <https://arxiv.org/abs/2306.05685>.
- **AE-2** · `advanced-evaluation/references/bias-mitigation.md:139-144`, `references/implementation-patterns.md:116,130` — `claude-4-5-sonnet` was never a valid ID. `gpt-5.2` is labeled both "cheaper" and "more capable". **Change:** use `JUDGE_MODEL` and `SCREEN_MODEL` placeholders.
- **AE-3** · `advanced-evaluation/references/metrics-guide.md:233-236` — `await` inside a plain `def` is a SyntaxError. **Change:** `async def`.
- **AE-7** · `advanced-evaluation/references/bias-mitigation.md:97-112`, `SKILL.md:133-135`, `references/implementation-patterns.md:178-193` — The 500-word length target and the confidence formulas have no source. **Change:** label them as illustrative. State that confidence needs calibration against human labels.
- **AE-8** · `advanced-evaluation/SKILL.md:414-417` — The section repeats the Integration section at lines 380–388. **Change:** delete it.
- **SEE-4** · `simplified-engineering-english/references/rules.md` source columns (lines 21, 32, 35, 44–46, 58, 62) — STE-derived rules cite topics, not rule numbers. Issue 9 renamed "noun clusters" to "multi-word nouns". **Change:** cite exact rule numbers (2.1/2.2, 3.2/3.4/3.6, 4.2, 5.1/5.4/5.5, 6.3, 7.1–7.3, 8.1, 8.4–8.7), and rename the SEE-NOUN-01 source. Source: <https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf>.
- **LDC-1** · `lossless-doc-compress/references/slop-and-hedging.md:18`, `references/removal-taxonomy.md:13-14` — "essentially identical" → "identical" changes approximate equality into exact equality, which `fidelity-rules.md:44-48` forbids. "quite" often changes degree. **Change:** move the example to the KEEP or FLAG list, and remove "quite" from the removable hedges. Set `metadata.adaptation: modified` and update `ATTRIBUTION.md`, because the skill is currently recorded as imported.
- **LDC-2** · `lossless-doc-compress/references/compression-workflow.md:41-42`, `references/output-templates.md:21-35` — The self-check needs words removed per category, and the log template does not record them. **Change:** add a words-removed column to the log template.

## 8. Wave 3 — Guidance Changes (Class G)

Order by risk: security and false-pass defects first, then factual guidance, then style. Each bullet is one treatment unless it says it is grouped.

### 8.1 Security and correctness

- **HA-4** · `hosted-agents/SKILL.md:61-65,168-173`, `references/infrastructure-patterns.md:43,97,658-662`, `scripts/sandbox_manager.py:191` — The skill puts an `x-access-token` clone URL and `GITHUB_APP_TOKEN`/`NPM_TOKEN` inside the sandbox. The token persists in `.git/config` and from there in images and snapshots, and it expires after one hour. **Change:** never place credentials in sandbox images or snapshots. Inject credentials through a proxy outside the sandbox, scoped to the session branch. Sources: <https://www.anthropic.com/engineering/claude-code-sandboxing>, <https://modal.com/docs/sdk/py/latest/Sandbox>, <https://developers.cloudflare.com/sandbox/>, <https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app>. Behavior case: a sandbox setup request that tempts token injection.
- **HA-6** · `hosted-agents/SKILL.md:55-59,271`, `references/infrastructure-patterns.md:644-669` — **Change:** add a gotcha about snapshot expiry (Modal: filesystem snapshots 30 days, memory snapshots 7 days, `NotFoundError` on expiry; sandboxes default to 5 minutes with a 24-hour cap). Replace the `blocked_commands` denylist with platform egress allowlists. Sources: <https://modal.com/docs/guide/sandbox-snapshots>, <https://modal.com/docs/guide/sandbox-networking>, <https://developers.openai.com/codex/cloud/internet-access>. Group with `HA-4`.
- **FC-2** · `filesystem-context/SKILL.md:149-161,264-273` — **Change:** add a gotcha: confine agent writes to a rooted directory, reject path traversal, and treat persisted instructions as untrusted input. Source: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool>.
- **CC-4 + CD-5** · `context-compression/SKILL.md:233-247`, `context-degradation/SKILL.md:57` — OpenAI reported a model that wrote jailbreak-style instructions into its own compaction summaries, and a successor that obeyed them. **Change:** treat summary text as data. A summary must not add constraints that do not appear in user or task messages. Flag imperatives that cannot be traced to the user or the task. Source: <https://alignment.openai.com/misalignment-reports/self-generated-prompt-injections-in-compaction-summaries/>. One grouped treatment across both skills.
- **TD-1** · `tool-design/SKILL.md:110-125,264` — "Always use fully qualified `ServerName:tool_name`" conflicts with MCP: since 2025-11-25, tool names SHOULD use only `A-Za-z0-9_-.`, and disambiguation is the client's job. **Change:** server authors choose names that are unique within the server and use the allowed charset (dots allowed for namespaces). Prompts refer to tools by the qualified form the host exposes. Sources: <https://modelcontextprotocol.io/specification/2026-07-28/server/tools>, <https://modelcontextprotocol.io/specification/2025-11-25/changelog>.
- **TD-2** · `tool-design/SKILL.md:94-104,180-191`, `references/best_practices.md:41-70` — **Change:** add checklist items: `outputSchema` with `structuredContent` for structured results; honest `annotations` (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`), which clients treat as untrusted; input-validation failures returned as `isError: true` tool results, not protocol errors; stateful tools that take explicit server-minted handles (the 2026-07-28 revision is stateless); deterministic `tools/list` order. Pin the spec revision. Source: <https://modelcontextprotocol.io/specification/2026-07-28/changelog>. Group with `TD-1`.
- **TD-6** · `tool-design/SKILL.md:133-161,245-256` — The body is over ~5k tokens. The `optimize_tool_description` template calls an undefined `get_agent_response`, and the Guidelines repeat Core Concepts. **Change:** delete both blocks to make room for `TD-2`. Group with `TD-1`.
- **EV-3** · `evaluation/SKILL.md:47-55,101-116,238-251` — **Change:** add "Trials and reliability": k trials per task in isolated environments, reporting pass@1 and pass^k (0.75 per trial → about 42% at k=3). Add capability and regression suites, a reference solution per task, transcript review, and "0% pass@100 means the task or grader is broken". Replace Gotcha 6. Source: <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>.
- **EV-4** · `evaluation/SKILL.md:37,51` — **Change:** grade outcomes by default, and add tool-call or process assertions only for steps that safety or policy requires. Same source. Group with `EV-3`.
- **AE-4** · `advanced-evaluation/SKILL.md:42-44,190-203,348` — Pairwise protocols are more exploitable by distractor features (about 35% preference flips versus 9% for absolute scores). **Change:** when a system is optimized against the judge, prefer absolute or rubric scoring, or add distractor-controlled pairs. Keep pairwise for one-off comparisons. Source: <https://arxiv.org/abs/2504.14716>.
- **AE-5** · `advanced-evaluation/SKILL.md:56`, `references/bias-mitigation.md:126-164` — **Change:** the judge must not share a model, lineage, or family with the generator, or with synthetic data used to train it (preference leakage). Source: <https://arxiv.org/abs/2502.01534>. Group with `AE-4`.
- **AE-6** · `advanced-evaluation/SKILL.md:83-108` — **Change:** use one criterion per judge call when criteria interact, and add an `UNKNOWN` score. Source: the Anthropic evals guide above. Group with `AE-4`.
- **SIL-5** · `self-improvement-loops/SKILL.md:74-76,128-139` — The gate compares only against the previous harness. Under matched budgets, harness evolution fails to beat test-time-scaling baselines. **Change:** add a matched-budget best-of-N or retry baseline, and an untouched final test split separate from the reused gate split. Source: <https://arxiv.org/abs/2607.12227>.

### 8.2 Factual guidance

- **MAP-3** · `multi-agent-patterns/SKILL.md:153-163,222,232` — Majority voting accounts for most of debate's gains. More discussion rounds hurt. **Change:** make independent sampling plus a weighted vote the baseline. Use debate only when it shows a measured gain over the vote. Sources: <https://arxiv.org/abs/2508.17536>, <https://arxiv.org/abs/2502.19130>.
- **MAP-4** · `multi-agent-patterns/SKILL.md:17-25,37-43,68,108-123,195-202` — **Change:** add a "stay single-agent" gate. Split work by context boundary, not by role. Add a single-writer rule and the generator-verifier pattern. Demote swarm. Replace "parallel time approaches the longest subtask" with "parallelism buys thoroughness, not speed". Fix Example 1. Sources: <https://arxiv.org/abs/2512.08296>, <https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them>, <https://claude.com/blog/multi-agent-coordination-patterns>. Group with `MAP-3`.
- **CO-1** · `context-optimization/SKILL.md:37,71-84,187` — **Change:** add a short list of provider cache rules, with links and no price table: tool changes invalidate everything downstream; restrict tools with `allowed_tools` or `tool_choice` instead of removing them; the TTL sets the idle budget between agent turns; minimum cacheable sizes exist. Sources: <https://platform.claude.com/docs/en/build-with-claude/prompt-caching>, <https://developers.openai.com/api/docs/guides/prompt-caching>, <https://ai.google.dev/gemini-api/docs/caching>.
- **CO-2** · `context-optimization/SKILL.md:76-77` — Both Anthropic and OpenAI render tools before the system prompt. **Change:** list tools first. Group with `CO-1`.
- **CO-3** · `context-optimization/SKILL.md:61-69` — **Change:** name native tool-result clearing (`clear_tool_uses_20250919`), and state the rule "clear in large batches, because each clear invalidates the cache". Source: <https://platform.claude.com/docs/en/build-with-claude/context-editing>. Group with `CO-1`.
- **CO-4** · `context-optimization/SKILL.md:94-101` — Some current models get no injected token-budget updates. **Change:** the harness supplies a deterministic token readout (usage fields or token counting) on those models. Source: <https://platform.claude.com/docs/en/build-with-claude/context-windows>. Group with `CO-1`.
- **CO-8** · `context-optimization/SKILL.md` KV-cache section — Adopt the upstream sentence: an edit to earlier history costs the text that follows it, so batch such edits and place them near the end. Group with `CO-1`.
- **CO-7** · `context-optimization/SKILL.md:49-59,181,189` — The compaction content repeats `context-compression`. **Change:** keep only the trigger and budget policy, and link `context-compression` for summary content.
- **CC-3** · `context-compression/SKILL.md:35-41,153-168` — **Change:** add "native options first", which maps each strategy to provider compaction features. Mark opaque provider compaction as uninspectable, so probe evaluation is the only check. Sources: <https://platform.claude.com/docs/en/build-with-claude/compaction>, <https://developers.openai.com/api/docs/guides/compaction>.
- **CD-3 + CD-4** · `context-degradation/SKILL.md:15,59,194,238` — **Change:** add premature termination as a length-related symptom (<https://arxiv.org/abs/2606.29718>). Add Classifier Context Rot (<https://arxiv.org/abs/2605.12366>) and LOCA-bench (<https://arxiv.org/abs/2602.07962>) as evidence, and periodic reminders as a measured partial mitigation.
- **MS-6** · `memory-systems/SKILL.md:25,58-66,181,230-231` — **Change:** in memory benchmarks, fix the LLM and embedding model across arms, include a verbatim-RAG or filesystem baseline, report write-path cost, and stratify by question type. Sources: <https://www.letta.com/blog/benchmarking-ai-agent-memory>, <https://arxiv.org/abs/2606.29914>.
- **MS-8** · `memory-systems/SKILL.md:103` — Optional. Name Anthropic's client-side memory tool as a vendor implementation of file-system memory. Source: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool>.
- **TD-3** · `tool-design/SKILL.md:53,61,106-108`, `references/best_practices.md:23-27` — **Change:** for large catalogs, consider deferred loading or tool search before merging tools that do different things. Treat the reported numbers as vendor-scoped. Source: <https://www.anthropic.com/engineering/advanced-tool-use>.
- **LB-3** · `latent-briefing/SKILL.md:104,128,133-138` — **Change:** add token eviction to the strong baselines. Add a gotcha about the choice of proxy query and compaction timing (<https://arxiv.org/abs/2608.00902>). Require a mismatched-cache audit before claiming latent transfer (<https://arxiv.org/abs/2608.04893>). Treat KV state that crosses a process or trust boundary as security-sensitive (<https://arxiv.org/abs/2606.28958>).
- **HE-2** · `harness-engineering/SKILL.md:49-57,221-227` — **Change:** add "locked-surface mechanics": a feature list in which the agent may only flip `passes`, an `init.sh` smoke test, an initializer/coder split, and linters whose messages include the fix. Sources: <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>, <https://openai.com/index/harness-engineering/>.
- **HE-3** · `harness-engineering/SKILL.md:72,150,196,204` — In the skill's own source, the novelty-gated run could not improve the baseline, and prompt text did not stop the agent from halting. **Change:** recast the novelty gate as dedup against the registry. Handle stopped loops with external re-arm or a monitor. Source: <https://www.primeintellect.ai/auto-nanogpt>.
- **LH-2** · `long-horizon-prompting/SKILL.md:91,237`, `references/research-evidence.md:10,51` — BudgetThinker is a training method, not prompt evidence. Anthropic advises against token countdowns because they cause premature handoff. **Change:** split Gotcha 8: re-inject verified progress, and enforce budgets in the harness without showing token countdowns. Sources: <https://arxiv.org/abs/2508.17196>, <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5>.
- **LH-4b** · `long-horizon-prompting/SKILL.md:95,107,239`, `references/vendor-guidance.md` — **Change:** add a GPT-6 entry (it asks more questions and under-delegates, so state the autonomy grant and delegation intent explicitly), and qualify Gotcha 10. Source: <https://developers.openai.com/api/docs/guides/prompt-guidance>.
- **PD-3** · `project-development/SKILL.md:134-144,213-217` — **Change:** add batch APIs and cached prefixes as cost levers (they stack). Move parallelism out of the cost list, because it cuts latency, not cost. Source: <https://platform.claude.com/docs/en/about-claude/pricing>.
- **SIL-6** · `self-improvement-loops/SKILL.md:56-61,149,204` — Harness-update quality is flat across proposer capability. **Change:** measure proposer usefulness and executor uptake separately; a cheap proposer can be enough. Source: <https://arxiv.org/abs/2605.30621>.
- **SIL-7** · `self-improvement-loops/SKILL.md:78-80,120,146` — In WikiSkill, a consolidated knowledge layer on the proposer side improved skill evolution, and the paper reports that evolved skills transfer across models. **Change:** allow a consolidated proposer-side layer linked to raw traces. Validate each evolved skill on the target model before reuse. Name skill-library evolution at rung 3. Source: <https://arxiv.org/abs/2608.27454>. The reviewing agent reported a negative-transfer figure (50.5% → 18.1%) and an executor-side drop to 60.9%. Verify both against the paper before citing them, because the abstract reports positive transfer.
- **MSD-1** · `ml-system-design-review/references/rubrics.md:30,35` — **Change:** add history depth, seasonality coverage, and schema stability to the Data B/A cells. Add label delay and business KPIs linked to model metrics to the Monitoring B/A cells.
- **MSD-2** · `ml-system-design-review/references/rubrics.md:34` — Optional. Name the serving levers (batching, caching, model routing, quantization) in the A cell. Group with `MSD-1`.
- **MSD-3** · `ml-system-design-review/references/modern-ai-systems.md:92,103` — **Change:** "report pass^k for user-facing agents". Group with `MSD-1`.
- **LDC-3** · `lossless-doc-compress/references/compression-workflow.md:38-44`, `references/output-templates.md:54-56` — "lossless ✓" has no mechanical check. **Change:** before claiming lossless, require that numbers, identifiers, code blocks, and table cells appear byte-exact in the output. Reuse the gate wording from `simplified-engineering-english/SKILL.md:83`.

### 8.3 Leancode family

These items use the Leancode candidate gate.

- **LC-2** · `leancode/SKILL.md:64` — "If something is unclear, stop. Name what's confusing. Ask." conflicts with lines 58–60 and 67–70. **Change:** delete line 64.
- **LC-3** · `leancode/SKILL.md` after line 141 — **Change:** add "The check verifies the logic; it does not define it. Never special-case test inputs to make a check pass." Source: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md>.
- **LC-4** · existing Candidate 4 — Add an async variant to its fixtures: `@lru_cache` on an `async def` raises `RuntimeError: cannot reuse already awaited coroutine` on the second call.
- **LR-1** · `leancode-review/SKILL.md:58-61` — **Change:** never flag smoke tests or `assert` self-checks, validation at trust boundaries, error handling that prevents data loss, security or accessibility code, or anything the request required.
- **LR-2** · `leancode-review/SKILL.md:52` — **Change:** delete "the only metric that matters". Group with `LR-1`.
- **LA-1** · `leancode-audit/SKILL.md` Output, after line 42 — **Change:** each finding names the exact cut and its evidence; file size alone is not a finding. State which paths were scanned. This matches the existing eval oracles in `evals/cases/catalog-behavior-*.jsonl:13`.
- **LA-2** · `leancode-audit/SKILL.md:20,27` — The `scope:` tag has no request to compare against in a whole-repo audit. **Change:** delete the tag. Group with `LA-1`.
- **LA-3** · `leancode-audit/SKILL.md` Scan scope — **Change:** if the repository already has a dead-code analyzer (for example knip or vulture), run it and cite its output. Do not install one without asking. Confirm each `delete:` with a reference search. Group with `LA-1`.
- **LA-4** · `leancode-audit/SKILL.md:36-38` — **Change:** replace "files exporting one thing" with "modules whose single export has a single caller". Add "fallbacks for states internal code cannot reach" and "comments that restate the code". Group with `LA-1`.
- **LD-2** · `leancode-debt/SKILL.md:44` — **Change:** end with `<N> markers, <M> no-trigger, <K> no-ceiling.`
- **LD-3** · `leancode-debt/SKILL.md:22-26` — **Change:** start from `git grep -nI -F "lean-debt:"`, then keep hits inside comments. Group with `LD-2`.
- **HK-1** · `.omp/hooks/pre/leancode.ts:28` — The reminder reached report-only subagents during this review. **Change:** re-run Candidate 3 as a hook-only candidate that appends "an explicitly requested report or format wins". Candidate 3's development grade passed 21/21 critical; only the combined gate failed.

### 8.4 Simplified Engineering English

These items follow the SEE release governance.

- **SEE-1** · `references/rules.md:46` — STE Rule 4.2 bans all contractions. **Change:** strict prohibits all contractions. Engineering-default is unchanged.
- **SEE-2** · `references/rules.md:44,49-56` — The strict word count omits STE Rules 8.4 (a vertical-list colon ends a sentence) and 8.5 (a parenthetical counts as one word). **Change:** add both rules, or relabel the counting as "adapted".
- **SEE-3** · `references/rules.md:42`, `SKILL.md:50` — **Change:** in strict, list the Rule 3.2 tense set and apply Rules 3.4 and 3.5. Limit the perfect and progressive allowance to engineering-default.
- **SEE-5** · `SKILL.md:58-60`, `references/rules.md` procedure section — **Change:** add Rule 5.5 (notes give information, not instructions) to the procedure card as an error in both profiles. Add Rules 9.3 (no phrasal verbs) and 6.6 (at most six sentences per paragraph) as strict-only controls.

## 9. Wave 4 — Routing Changes (Class R)

Run these inside the description-density experiment (skill set plan §11), one family per treatment.

- **CF-2** · `context-fundamentals/SKILL.md:3` — Replace "U-shaped attention curve" with "position sensitivity and context rot". Chroma found no position effect across 11 needle positions on its task. Family: context core.
- **HE-1 + SIL-8** · `harness-engineering/SKILL.md:28-32` — Add exclusions: self-modified harnesses and prompts → `self-improvement-loops`; launch-brief wording → `long-horizon-prompting`. Both siblings already route loop governance here. Family: workflows.
- **PD-6** · `project-development/SKILL.md:3,26,148-158` versus `multi-agent-patterns/SKILL.md:3` — Both claim the single-versus-multi-agent decision. **Decision:** `project-development` owns "whether to build and pipeline shape". `multi-agent-patterns` owns "single versus multiple agents and topology". Add a routing pair for this boundary before the treatment.
- **LDC-4** · `lossless-doc-compress/SKILL.md:39-45` — Add exclusions: clarity rewrites → `simplified-engineering-english`; session handoffs → `context-compression`.
- **LD-4** · `leancode-debt/SKILL.md:8` — Replace "changes nothing" with "changes no source"; the skill writes `LEANCODE-DEBT.md` on request.

## 10. Verification

### 10.1 Deterministic checks (every wave)

```sh
python3 scripts/validate_skills.py
python3 evals/validate.py
python3 -m unittest discover -s tests
python3 -m unittest discover -s context-compression/tests
bun test tests/leancode_hook.test.ts
```

### 10.2 Script smoke checks (Wave 2)

Run each script that a Wave 2 commit touches, and check the stated result:

| Script | Expected result after the fix |
|---|---|
| `python3 evaluation/scripts/evaluator.py` | At least one case fails. |
| `python3 multi-agent-patterns/scripts/coordination.py` | Consensus strength 0.74 for the demo votes. |
| `python3 hosted-agents/scripts/sandbox_manager.py` | Exits 0. A follow-up with a snapshot restores the snapshot when the pool is warm. |
| `python3 context-fundamentals/scripts/context_manager.py` | Exits 0 and uses the supplied counter. |
| `python3 context-optimization/scripts/compaction.py` | Exits 0. One threshold parameter. |
| `python3 memory-systems/scripts/memory_store.py` | Exits 0. `query_at_time` takes a dict. |
| `python3 project-development/scripts/pipeline_template.py all --batch-id smoke` (in a temporary directory) | Exits 0. |

### 10.3 Reference code syntax check (Wave 2)

For each changed reference file, parse every fenced `python` block. A block labeled as pseudocode is exempt. Run this as a throwaway command; it is not a permanent test:

````sh
python3 - memory-systems/references/implementation.md <<'EOF'
import re, sys
for path in sys.argv[1:]:
    for i, block in enumerate(re.findall(r"```python\n(.*?)```", open(path).read(), re.S)):
        try:
            compile(block, f"{path}#{i}", "exec")
        except SyntaxError as e:
            print(f"{path} block {i}: {e}")
EOF
````

Replace the example path with the changed reference files. No output means every block compiles. Compiling does not catch missing imports or undefined names (`FC-1`, `MS-3`), so run those blocks after fixing them.

### 10.4 Live evaluation (Waves 3 and 4)

Use the commands, locked configuration, and gates in [the evaluation guide](../evals/README.md) and skill set plan §18.2. Each **G** treatment needs one development behavior case that observes the changed behavior. Add the case, with its `suites.json` hash update, in a commit before the skill change.

## 11. Owner Decisions

These items change policy or legal framing. Do not apply them without an explicit decision.

| ID | Question | Recommendation |
|---|---|---|
| LC-5 | `leancode` metadata says `adaptation: inspired` and that the copying direction is unverified. The review found that §1 and most of §3–§4 match upstream `CLAUDE.md` almost word for word, and that the upstream snapshot is six months older. Change to `adaptation: derived`? | Owner decision. `ATTRIBUTION.md` deliberately avoids inferring direction. If you change it, update `ATTRIBUTION.md` in the same commit. |
| HE-5 | `harness-engineering/SKILL.md:82-84,206` forbid merge or push without human approval. OpenAI documents agents that merge their own changes when rollback is cheap. Add a standing-grant exception? | Keep the default. Add the exception only if a user workflow needs it. |
| RP-6 | Send fixes upstream? | Yes for `LDC-1`, `EV-1`, and `AE-3`; these are small and unambiguous. |

## 12. Rejected

| Proposal | Reason |
|---|---|
| Import `self-managed-context` | See `RP-4`. |
| Add upstream routing lines that point to `self-managed-context` | The skill is not in the catalog. |
| Import `EXAMPLES.md` from `andrej-karpathy-skills` | ~520 lines, one broken example, no new rules. |
| Add price or context-window tables to skills | They go stale quickly. Link provider docs instead. |
| Add a validator denylist of retired model IDs | Brittle. The model-neutral rule (`RP-1`) removes most IDs instead. |
| Add a validator check for drift between the shared blocks in `ai-stage-gate` and `ml-system-design-review` | Low value for two copies. Review them manually during `RP-5`. |
| Hard-code EU AI Act dates in `ai-stage-gate` | Not verified, and they go stale. |
| Edit `leancode/SKILL.md:108` to absorb "don't annotate unchanged code" | The gap is small; line 119 already covers type hints. Revisit only inside Leancode Candidate 5. |

## 13. Definition of Done

- [x] Wave 1 items `RP-1` to `RP-5` are merged, and the deterministic checks pass.
- [x] Every Wave 2 item is merged or rejected with a reason, and its smoke check passed.
- [ ] Every Wave 3 item has a development behavior result, and every merged item has a holdout result under skill set plan §18.2.
- [ ] Every Wave 4 item ran inside the description-density experiment.
- [ ] Every Section 11 decision is recorded.
- [x] `ATTRIBUTION.md` and the skill metadata match the synced upstream commits.

## 14. Implementation Status (2026-10-06)

- **Applied in the working tree:** every item in Sections 6–9 except the Section 11 owner decisions. No item was rejected. `ATTRIBUTION.md` records `LDC-1` and `MSD-1` as modifications.
- **Proposed evaluation cases:** `evals/cases/refresh-behavior-development.jsonl` (36 behavior cases, one per **G** treatment group) and `evals/cases/refresh-routing-development.jsonl` (12 routing cases covering both directions of every **R** pair). Both are registered as canonical development suites `refresh-behavior` and `refresh-routing`. Holdout files for these suites do not exist yet; write them after the development runs, without tuning against them.
- **HK-2:** fallback branch applied. `LEGACY_REMINDERS` is now derived from `leancodeReminder()`. `evals/mode_smoke.py` asserts that no prior reminder reaches `context` (probe: `evals/leancode_context_probe.ts`), but its only run (`evals/results/content-refresh/mode-smoke-hk2.json`) failed before any model turn, so the filter stays until the assertion passes.
- **Blocked:** every live gate (Section 10.4, `HK-1` Candidate 3 rerun, `HK-2` smoke). The pinned evaluation profile `skill-eval-isolated` has no valid `openai-codex` credential (`No API key found for openai-codex`; refresh token rejected). Unblock: run `omp --profile skill-eval-isolated` and `/login`, then run `refresh-behavior` and `refresh-routing` baseline and treatment per `evals/README.md`.
- **Open owner decisions:** `LC-5`, `HE-5`, `RP-6`.
