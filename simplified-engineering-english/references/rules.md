# SEE Detailed Rules

This file is the canonical inventory for Simplified Engineering English (SEE) rules. `SKILL.md` contains only the execution workflow. `dictionary.md` contains terminology and lexical data.

## Record Schema

Each rule record gives a stable ID, rule text, applicable profile and artifact card, severity, enforcement class, source and relationship, exceptions, examples, and rationale. Relationships are `adopted`, `adapted`, `SEE-policy`, `house-style`, or `heuristic`. Enforcement is `deterministic`, `parser-assisted`, `semantic review`, or `technical review`.

Profiles: `both`, `strict`, or `engineering-default`. Cards: `all`, `procedure`, `requirement`, `explanation`, or `error-record`.

## Authority and Precedence

Apply safety, security, privacy, legal, and regulatory constraints first. Then preserve technical meaning and obligation force. Preserve verbatim technical content except for authorized redaction. Authoritative ecosystem terms override the project glossary. The project glossary and artifact contract override SEE defaults. The selected profile and card override general SEE defaults. Style never overrides meaning.

## Preserve Meaning

| ID | Rule | Profile / card | Severity | Enforcement | Source / relationship | Exceptions | Compliant / counterexample | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SEE-PRESERVE-01` | Preserve facts, typed technical roles and relations, conditions, modal, temporal, and provenance qualifiers, values, versions, technical tokens, obligation force, uncertainty, and supported causal claims. Keep descriptive facts separate from obligations. Preserve authorization tense and exclusive scope. | both / all | error | deterministic for declared exact fields; semantic and technical review otherwise | SEE preservation policy / SEE-policy | Authorized higher-precedence redaction. | Good: keeps `50 ms`, a plain-present copy fact, and `authorizes only`. Bad: adds `SHALL` to the copy fact or changes `authorizes only` to `authorized`. | A clearer sentence with changed meaning is a defect. |
| `SEE-NOOP-01` | Leave source text unchanged when it satisfies all applicable error-level rules. Treat an explicit task characterization of text as precise or compliant as authoritative unless it directly contradicts a source fact or a safety, security, obligation, or preservation rule. | both / all | error for an unsupported change | deterministic exact comparison for declared no-op cases; semantic review otherwise | SEE preservation policy / SEE-policy | A directly evidenced error-level defect. | Good: returns an already compliant procedure exactly. Bad: restructures it to satisfy a warning. | Unnecessary edits add regression risk without improving the artifact. |
| `SEE-SPAN-01` | Preserve product, system, person, and named-scope capitalization, identifiers, commands, paths, flags, environment variables, methods, status codes, versions, literal values, and explicitly exact output tokens verbatim. A lowercase occurrence inside a command does not replace a prose name. Do not append punctuation to an exact token. | both / all | error | deterministic: `evals/grade.py` generated `manifest_protected_spans_*` and `manifest_numbers_units_versions_status_codes_*` checks | ASD-STE100 Issue 9, word and term controls, software adaptation / adapted | Authorized redaction under `SEE-DISCLOSE-01`. | Good: `PROFILE: strict` and run `db migrate --dry-run`. Bad: `PROFILE: strict.` or run `db-migrate --dryrun`. | Technical tokens and names are not ordinary prose. |
| `SEE-QUOTE-01` | Preserve required quotations and quoted output verbatim. Copy each required quoted span from the source and compare it with the rewrite character by character before returning. Do not move adjacent punctuation into or out of the quotation. | both / all | error | deterministic: generated `manifest_quoted_spans_*` checks | SEE preservation policy / SEE-policy | A task that explicitly requests quotation editing; authorized secret redaction. | Good: source and rewrite both contain `"massively improved"` before a comma. Bad: changes it to `"massively improved,"`. | A quotation must remain attributable to its source. |
| `SEE-AMBIG-01` | Report consequential source ambiguity instead of selecting an unsupported interpretation. Before reporting an ambiguity, identify at least two materially different interpretations supported by the source and the consequential difference. If you cannot, do not report an ambiguity; preserve explicit uncertainty or an evidence limitation as a fact. Treat a reference as resolved when it has one grammatically and technically compatible antecedent. | both / all | error | semantic review with the source span and competing interpretations | ISO 24495-1 understandability outcome; SEE preservation policy / SEE-policy | A merely possible precision improvement that does not change an outcome. | Good: reports that `it` has two compatible referents. Bad: invents a second referent for `the pressure` after the source names only manifold pressure. | An unsupported clarification invents meaning; an unsupported finding creates needless churn. |

## Choose Terminology

| ID | Rule | Profile / card | Severity | Enforcement | Source / relationship | Exceptions | Compliant / counterexample | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SEE-TERM-01` | Use the authoritative term for each concept and keep it stable within its declared scope. | both / all | error | semantic and technical review; lexical checker for declared accepted forms | ASD-STE100 Issue 9, consistent terminology / adapted | An explicit comparison of two terms. | Good: uses `job` throughout. Bad: alternates `job`, `task`, and `work item` without definitions. | Synonym drift can change system boundaries. |
| `SEE-TERM-02` | Use each controlled term only in its defined sense and declared part of speech. | both / all | error for material distinctions; warning otherwise | semantic review; lexical checker only for observable forms | ASD-STE100 Issue 9, approved meanings and parts of speech / adapted | An authoritative ecosystem or project definition. | Good: a parameter receives an argument. Bad: calls the argument a parameter at the call site. | Word form alone cannot prove word sense. |
| `SEE-TERM-03` | Replace vague, inflated, idiomatic, exclusionary, or open-ended expressions with the exact property or set. When the source does not support a precise replacement, preserve the claim and report the unresolved term. | both / all | warning; error when scope or obligation changes | deterministic lexical check outside exempt scopes, then semantic review | Google developer style; ISO 24495-1 / adapted | Required quotation, product name, or technical term. | Good: reports that `faster` lacks a metric and baseline. Bad: silently treats `very fast and scalable` as precise. | Exact properties are actionable; an explicit gap is safer than invented precision. |
| `SEE-TERM-04` | Define an abbreviation or project term before repeated use and record authoritative project terms in the glossary. | both / all | warning; error when undefined use changes interpretation | parser-assisted definition check; technical review of glossary meaning | ASD-STE100 Issue 9, abbreviations and technical names / adapted | Terms the intended audience can be proven to know; a term used once should be written in full. | Good: service-level objective (SLO), then SLO. Bad: an unexplained local acronym. | Definitions bound a term to one meaning. |
| `SEE-ACCESS-01` | Use descriptive headings, meaningful links, textual error identification, text alternatives, accessible UI labels, and no color-, position-, punctuation-, or symbol-only meaning. | both / all | error when information is inaccessible; warning for editorial defects | parser-assisted checks plus rendered-surface review | Google accessibility guidance; WCAG 2.2, 3.3.1 and 3.3.3 / adapted | Runtime keyboard, focus, ARIA, right-to-left, expansion, and localization-code behavior route to implementation review. | Good: `Status: failed`. Bad: `The red icon means failure` with no text. | Prose must retain meaning across presentation modes. |

## Identify Actors, Actions, Conditions, and Results

| ID | Rule | Profile / card | Severity | Enforcement | Source / relationship | Exceptions | Compliant / counterexample | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SEE-ACTOR-01` | Name the responsible actor when responsibility or behavior depends on it. | both / all | error for consequential ambiguity | semantic review | Google active-voice guidance / adapted | The actor is unknown, irrelevant, intentionally omitted for a valid reason, or the affected object is the relevant subject. | Good: `The client retries.` Bad: `Retries happen.` | Accountability and system behavior need a subject. |
| `SEE-VOICE-01` | Prefer active voice. Permit passive voice when omission of the actor preserves the intended emphasis or unknown state. Never invent an actor. | strict / all: restricted; engineering-default / all: warning | error only when responsibility becomes unclear | semantic review | Google active-voice guidance / adapted | Unknown, irrelevant, or deliberately omitted actors; object-focused explanation. | Good: `The record was deleted; the actor is unknown.` Bad: `An operator deleted the record` without evidence. | Mechanical active-voice conversion can invent facts. |
| `SEE-TENSE-01` | Use tense and aspect that preserve actual state and event order. Prefer simple present for general behavior; permit past events, delayed future outcomes, and material perfect or progressive relationships. | strict / all: restricted; engineering-default / all: warning | error when temporal meaning changes | semantic review | Google tense guidance; Microsoft verb guidance / adapted | A complex tense that is necessary for sequence or state. | Good: `The response will arrive after the queued job completes.` Bad: changes scheduled future behavior to present behavior. | Simpler grammar cannot justify changed time. |
| `SEE-ACTION-01` | Use a direct verb and name the concrete behavior. Avoid nominalizations and vague `allow`, `enable`, or `support` claims. | both / all | warning; error when behavior is ambiguous | lexical warning plus semantic review | ASD-STE100 Issue 9, verb controls; Microsoft verb guidance / adapted | An authoritative term of art. | Good: `The API returns 100 items and a token.` Bad: `The API supports pagination.` | Concrete actions expose observable behavior. |
| `SEE-COND-01` | Preserve every condition and exception. Put a procedure condition before its action when acting early can cause an error. | both / procedure; preservation applies to all | error | semantic review; case-specific deterministic checks only for declared observable forms or order | ASD-STE100 Issue 9, procedural conditions / adopted and adapted | Condition-after-action is acceptable when early action cannot mislead or cause harm. | Good: `If the pod is stopped, delete it.` Bad: `Delete it if the pod is stopped` in a skimmable destructive step. | A reader can act before reaching a trailing condition. |
| `SEE-SENT-01` | Under strict profile, limit procedural sentences to 20 words and descriptive sentences to 25 under the declared tokenizer. Under engineering-default, treat length as a review signal. | strict / all; engineering-default / all | error in strict; warning in default | deterministic only with a documented tokenizer | ASD-STE100 Issue 9, sentence length / adopted for strict; heuristic for default | Do not remove a condition, qualifier, or logical relation to meet a count. | Good: split at a logical boundary. Bad: delete `unless recovery is complete`. | Length can expose density but does not prove clarity. |
| `SEE-NOUN-01` | Under strict profile, use no more than three consecutive nouns in an unapproved noun cluster. Under engineering-default, flag only clusters that obscure relationships. | strict / all; engineering-default / all | error in strict; warning in default | parser-assisted part-of-speech check plus semantic review | ASD-STE100 Issue 9, noun clusters / adapted | Authoritative technical names, protected spans, and glossary-approved terms. | Good: `limit for the service request queue`. Bad: `service request queue limit`. | Long noun clusters can conceal the relationship between concepts. |
| `SEE-STRUCT-01` | Use one clear subject and topic, explicit required words, parallel lists for complex sets, and structure that preserves logical relationships. Strict profile prohibits semicolons and ambiguous contractions; default profile treats them as project choices unless meaning suffers. | strict and engineering-default / all | error for ambiguity; otherwise warning or project choice | deterministic for declared punctuation policy; parser-assisted and semantic review otherwise | ASD-STE100 Issue 9, sentence and paragraph controls; Google contractions guidance / adapted and house-style | A project can select spelling and common-contraction policy. Parentheses can carry optional information. | Good: two sentences preserve two claims. Bad: splits a condition from its governed action. | Mechanical style rules are subordinate to meaning. |

### Strict Word Count

Use this SEE tokenizer only when the strict profile is selected and the project does not declare a stricter tokenizer:

1. Identify sentence boundaries outside code spans, URLs, versions, decimal numbers, abbreviations, and quoted output.
2. Replace each protected span and each glossary-approved multi-word term with one placeholder.
3. Count each remaining whitespace-delimited lexical token and each placeholder as one word. Ignore standalone punctuation. Count a hyphenated compound as one word. Strict text does not use contractions.
4. Apply the 20-word limit to procedural conditions, actions, and results. Apply the 25-word limit to descriptive sentences.

If a checker cannot apply these rules reliably, classify the result as parser-assisted and require review. Do not report a deterministic sentence-count result.

## Select Obligation Force

| ID | Rule | Profile / card | Severity | Enforcement | Source / relationship | Exceptions | Compliant / counterexample | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SEE-BCP14-01` | Apply BCP 14 only when the artifact declares RFC 2119 and RFC 8174 semantics. Only uppercase keyword forms have the special meanings; lowercase words keep ordinary English meaning. | both / requirement | error | parser-assisted declaration and casing check; semantic review | RFC 8174 §2 / adopted | A normative artifact may use another declared obligation convention or ordinary language. | Good: a declared profile uses `MUST`; explanatory prose says `may`. Bad: assumes every lowercase `should` is normative. | RFC 8174 defines scope and casing, not mandatory keyword use. |
| `SEE-BCP14-02` | Preserve the declared force of `MUST`, `MUST NOT`, `REQUIRED`, `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, `RECOMMENDED`, `NOT RECOMMENDED`, `MAY`, and `OPTIONAL`. Never add one of these keywords to a descriptive fact that does not contain it. `SHOULD` and `SHOULD NOT` permit justified deviation after implications are understood and weighed. | both / requirement | error | deterministic: generated `manifest_expected_obligation_force_*`; semantic review of meaning | RFC 2119 §§1–7 and RFC 8174 §2 / adopted | The project can choose one preferred absolute keyword and need not use every synonym. | Good: keeps `SHOULD` and leaves a plain-present copy fact descriptive. Bad: changes `SHOULD` to `MUST` or adds `SHALL` to the copy fact. | Obligation strength is part of the contract. |
| `SEE-REQ-01` | State one independently verifiable obligation per normative statement, with an explicit subject and response. Keep rationale adjacent but outside the statement. Treat a stated trigger, response, bound, and unit as objective pass-fail evidence unless the source permits materially different verdicts. | both / requirement | error | parser-assisted shape check; semantic and technical review | NASA requirement checklist; SEE atomicity policy / adapted and SEE-policy | One system response can contain inseparable effects when the contract defines one outcome. Do not require optional environment or measurement detail that does not change the verdict. | Good: one gateway response and one threshold. Bad: one sentence combines unrelated latency, logging, and retry duties. | Atomic statements isolate evidence and change impact without inventing verification gaps. |
| `SEE-EARS-01` | Use EARS only when its temporal syntax fits: zero or more preconditions, zero or one trigger, one system name, and one or more responses. Complex forms can include unwanted-behavior `If` and `Then`; an optional feature is `included` unless runtime enablement is intended. | both / requirement | warning; error only when forced syntax changes meaning | parser-assisted shape check plus semantic review of suitability | Official EARS guide; Mavin et al., DOI 10.1109/RE.2009.9 / adopted with SEE atomicity layered separately | Constraints, interface rules, and quality attributes that do not fit EARS. | Good: `While connected, when data arrives, the client SHALL store it.` Bad: invents an event for a static quality constraint. | EARS is a syntax pattern, not complete requirements governance. |

## Structure the Artifact

| ID | Rule | Profile / card | Severity | Enforcement | Source / relationship | Exceptions | Compliant / counterexample | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SEE-PROC-01` | Put prerequisites before numbered imperative steps. Keep one consequential action per step and mark alternatives as choices. | both / procedure | error for unsafe order; warning otherwise | parser-assisted structure check | ASD-STE100 Issue 9, procedures / adapted | Simultaneous or automatic inseparable actions can share a step. | Good: prerequisites, then `1. Run ...`. Bad: hides required access in step 4. | Readers need safe execution order. |
| `SEE-PROC-02` | State the observable result for a step whose success is not self-evident. State rollback or irreversibility for consequential state changes. When missing recovery information limits safe execution, state before the action that recovery is unspecified. | both / procedure | error for consequential work | parser-assisted presence check; semantic and technical review | ASD-STE100 procedural results; SEE rollback policy / adapted and SEE-policy | Read-only diagnostics do not require rollback text. Do not claim that recovery is unavailable unless the source establishes it. | Good: reports that recovery is unspecified before a destructive command. Bad: invents exit code 0 or claims that recovery is impossible without evidence. | Actionability cannot exceed source knowledge. |
| `SEE-EXPL-01` | State reader need and scope early, order concepts by dependency, keep terms stable, and separate behavior, rationale, recommendation, and implementation detail. | both / explanation | warning; error for semantic mixing | parser-assisted headings; semantic review | Diátaxis; ISO 24495-1 / adapted | A short note can combine compatible context when the distinction remains explicit. | Good: behavior first, then `Rationale:`. Bad: presents a design preference as a guarantee. | Readers must distinguish contract from explanation. |
| `SEE-ERROR-01` | State what failed or was observed, a safe known cause, an available next action, and a safely disclosable affected input. In review findings, name every source-declared missing operation, input or resource, cause, and recovery detail that limits actionability. If the source provides no cause, state that the cause is unknown. Do not infer missing elements. | both / error-record | error | parser-assisted labels; semantic and technical review | WCAG 2.2, 3.3.1 and 3.3.3; Google error guidance / adapted | Omit sensitive or purpose-incompatible detail from the audience response. | Good: `Unknown: operation, affected input, and cause.` Bad: invents a network fault or omits the unknown cause. | A precise false error is worse than an explicit unknown. |

## State Risk, Recovery, and Disclosure

| ID | Rule | Profile / card | Severity | Enforcement | Source / relationship | Exceptions | Compliant / counterexample | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SEE-RISK-01` | Put consequential risk before the governed action. State consequence, prevention or recovery, and affected scope. When recovery is unknown and limits safe execution, state that it is unspecified before the action. | both / procedure and error-record | error | parser-assisted cross-block order; technical review | ASD-STE100 Issue 9, safety instructions, adapted to software / adapted | Do not claim that recovery is unavailable unless the source establishes it. | Good: an unspecified-recovery warning precedes `rm -rf`. Bad: the warning follows the command or claims that rollback is impossible without evidence. | A reader must see risk before acting. |
| `SEE-RISK-02` | Use the project's severity taxonomy. `WARNING`, `CAUTION`, and `NOTE` are an optional SEE software adaptation, not an official STE severity mapping. | both / procedure and error-record | project choice; error for label misuse that hides consequence | parser-assisted label check plus technical review | ASD-STE100 safety-instruction structure / adapted | A project-specific incident or safety taxonomy. | Good: maps label to declared consequence. Bad: treats every inconvenience as a warning. | Label inflation destroys signal. |
| `SEE-DISCLOSE-01` | Include an actionable local path when the reader can inspect it safely. Exclude server paths, stack traces, dependency details, secrets, and internal queries from unauthorized responses; put detail in an authorized operator channel. | both / error-record | error | deterministic exact redaction checks plus security review | OWASP Error Handling Cheat Sheet / adapted | Authorized operators can receive required diagnostic detail through an approved channel. | Good: keeps `/Users/alex/report.csv` and redacts `/srv/private/...`. Bad: removes both or leaks both. | Actionability and information disclosure are separate decisions. |
| `SEE-FAILURE-01` | State the failure behavior of retries, timeouts, fallbacks, and other degraded paths when it is part of the artifact contract. | both / requirement, procedure, error-record | error when omission changes the contract | semantic and technical review | SEE software policy / SEE-policy | The artifact explicitly excludes the failure path and links to its contract. | Good: states retry exhaustion behavior. Bad: says only `retries automatically`. | Silent failure semantics cause unsafe assumptions. |

## Scope Time, Version, and Evidence

| ID | Rule | Profile / card | Severity | Enforcement | Source / relationship | Exceptions | Compliant / counterexample | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SEE-TIME-01` | Declare product and version scope at document or section level. Qualify individual claims only when their scope differs. Avoid floating time references that can become stale; permit unambiguous immediate time and real delayed future outcomes. | both / all | error when scope changes; warning otherwise | parser-assisted metadata check; semantic review | Google tense guidance; SEE version policy / adapted and SEE-policy | Immediate procedure or observation where `now` has one operational reference. | Good: `Since v3.4`. Bad: `currently` in undated API reference. | Stable scope prevents documentation rot. |
| `SEE-DEPREC-01` | State the deprecated item, deprecation version, replacement, and planned removal version or that no removal is scheduled. Give an owner or tracking reference when unresolved. | both / explanation and requirement | error for contract records | parser-assisted field check plus technical review | SEE software lifecycle policy / SEE-policy | None for a formal deprecation record. | Good: `Removed: not scheduled; owner: SDK team.` Bad: uses deprecated to mean removed. | Consumers need migration and timing facts. |
| `SEE-EVID-01` | In incidents, debugging, investigations, research, and agent handoffs, distinguish observed, reported, inferred, assumed, and unknown claims. Keep timeline facts separate from causal hypotheses. | both / error-record; optional elsewhere | error when causal status changes | parser-assisted markers plus semantic review with source evidence | ISO 24495-1; SEE evidence policy / SEE-policy | Tutorials, ADRs, and API reference do not require a marker on every sentence. | Good: `Observed:` and `Inferred:`. Bad: states a pending hypothesis as past fact. | Evidence status is part of technical meaning. |
| `SEE-MEASURE-01` | State the statistic, workload, sample or interval, and measurement point required to interpret a performance, reliability, scale, or security claim. Keep distinct statistics when they answer distinct questions. | both / explanation and requirement | error for consequential claims | semantic and technical review | ISO 24495-1 usability; SEE measurement policy / SEE-policy | A document can link to a named measurement record. | Good: keeps mean and p99. Bad: deletes the mean because p99 exists. | A measurement is meaningful only in its decision context. |
| `SEE-REVISION-01` | Coordinate terminology and prose/code changes in the same reviewed change set or coordinated release. Classify consumer impact instead of labeling every terminology edit breaking. | both / all | warning; error when consumers receive inconsistent contract text | repository/process check plus technical review | SEE software release policy / SEE-policy | Separate repositories or release pipelines can coordinate through one release record. | Good: records editorial versus API impact. Bad: requires one Git commit across repositories. | Consistency matters; storage topology does not. |

## Verify and Report

| ID | Rule | Profile / card | Severity | Enforcement | Source / relationship | Exceptions | Compliant / counterexample | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SEE-VERIFY-01` | Give or support objective pass-fail evidence by test, demonstration, inspection, or analysis. Naming a test is neither necessary nor sufficient. | both / requirement and procedure | error for normative claims | semantic and technical review | NASA requirement checklist / adapted | A source with an unresolved measurable value must report the gap rather than invent it. | Good: verification by inspection of a signed manifest. Bad: rejects the requirement only because no executable test applies. | Different requirement types need different evidence methods. |
| `SEE-COVERAGE-01` | Name exact rule IDs and enforcement results. Do not claim SEE conformance without all applicable results and required technical approval. | both / all | error for publication claims | deterministic report-schema check plus technical review | ASD-STE100 tooling guidance; Vale documentation / adapted | None for a conformance claim. | Good: lists deterministic, parser, semantic, and technical coverage. Bad: calls Level 1 fully machine-checkable. | Automated checks cannot prove semantics or technical truth. |

## Legacy Rule Inventory

This migration inventory covers every former `SKILL.md` rule. Ranges are inclusive. The destination record supplies authority, profile, severity, enforcement, source, exceptions, examples, and rationale. A legacy ID is not a compatibility alias.

| Legacy ID | Destination | Disposition |
| --- | --- | --- |
| `1.1` | `SEE-TERM-01` | retained |
| `1.2` | `SEE-TERM-03` | retained as contextual lexical default |
| `1.3` | `SEE-TERM-02` | retained for material distinctions |
| `1.4` | `SEE-TERM-02` | narrowed to declared controlled terms |
| `1.5` | `SEE-TERM-03` | changed from absolute list to precision rule |
| `1.6` | `SEE-STRUCT-01` | retained when the set is consequential |
| `1.7` | `SEE-TERM-04` | retained with audience exception |
| `1.8` | `SEE-AMBIG-01` | retained |
| `1.9` | `SEE-TERM-03` | retained for translation-sensitive or ambiguous prose |
| `1.10-1.11` | `SEE-STRUCT-01`, `SEE-PRESERVE-01` | negative wording allowed when it carries prohibition or scope |
| `1.12` | `SEE-STRUCT-01` | changed to project choice |
| `1.13` | `SEE-ACCESS-01` | retained as information-accessibility rule |
| `1.14` | `SEE-TERM-04` | retained |
| `2.1-2.3` | `SEE-SPAN-01`, `SEE-QUOTE-01` | retained with authorized-redaction precedence |
| `2.4` | `SEE-ACTION-01` | retained as a clarity warning |
| `2.5` | `SEE-SPAN-01`, `SEE-TERM-02` | retained |
| `2.6` | `SEE-SENT-01` | strict error; default warning |
| `2.7` | `SEE-TERM-04` | retained |
| `3.1` | `SEE-ACTOR-01` | narrowed to material actors |
| `3.2` | `SEE-VOICE-01` | corrected passive-voice exceptions |
| `3.3-3.5` | `SEE-TENSE-01` | corrected to preserve temporal meaning |
| `3.6-3.7` | `SEE-ACTION-01` | retained as direct-behavior guidance |
| `3.8` | `SEE-BCP14-01` | retained under declared obligation scope |
| `4.1-4.2` | `SEE-SENT-01` | strict error; default warning |
| `4.3` | `SEE-ACTOR-01`, `SEE-STRUCT-01` | narrowed to consequential ambiguity |
| `4.4-4.5` | `SEE-STRUCT-01` | retained |
| `4.6` | `SEE-SENT-01` | strict tokenizer policy |
| `4.7-4.10` | `SEE-STRUCT-01` | strict controls or default choices; required information preserved |
| `5.1-5.2` | `SEE-PROC-01` | retained |
| `5.3` | `SEE-COND-01` | retained only when early action can mislead or harm |
| `5.4` | `SEE-PROC-01` | retained |
| `5.5` | `SEE-PROC-02` | retained without invented results |
| `5.6` | `SEE-PROC-01` | retained |
| `5.7` | `SEE-PROC-02`, `SEE-RISK-01` | limited to consequential state changes |
| `5.8` | `SEE-STRUCT-01` | retained as artifact structure |
| `6.1-6.6` | `SEE-EXPL-01`, `SEE-TERM-01` | retained and consolidated |
| `7.1` | `SEE-BCP14-01`, `SEE-BCP14-02` | corrected set includes `NOT RECOMMENDED` |
| `7.2-7.3` | `SEE-REQ-01` | retained as SEE atomicity policy |
| `7.4` | `SEE-BCP14-02` | corrected: no exhaustive exception sentence required |
| `7.5` | `SEE-BCP14-01` | corrected: lowercase forms have ordinary meaning |
| `7.6` | `SEE-BCP14-02`, `SEE-EXPL-01` | retained |
| `7.7` | `SEE-EARS-01` | corrected EARS cardinality and scope |
| `7.8` | `SEE-REQ-01`, `SEE-VERIFY-01` | replaced test-only criterion |
| `7.9` | `SEE-REQ-01` | retained |
| `8.1` | `SEE-RISK-02` | labels changed to optional software adaptation |
| `8.2-8.4` | `SEE-RISK-01` | retained consequence, placement, and scope |
| `8.5` | `SEE-RISK-02` | retained as taxonomy discipline |
| `8.6` | `SEE-ERROR-01`, `SEE-DISCLOSE-01` | corrected local versus server-path policy |
| `8.7` | `SEE-FAILURE-01` | retained |
| `9.1-9.2` | `SEE-TIME-01` | corrected immediate and document-level scope exceptions |
| `9.3` | `SEE-DEPREC-01` | corrected unknown removal plan |
| `9.4` | `SEE-TIME-01` | retained: plans are not facts |
| `9.5` | `SEE-EVID-01` | narrowed to provenance-sensitive artifacts |
| `9.6` | `SEE-MEASURE-01` | corrected mean and tail-statistic treatment |
| `9.7` | `SEE-EVID-01` | retained |
| `9.8` | `SEE-REVISION-01` | retained in decision records |
| `10.1` | `SEE-STRUCT-01` | retained when consistency aids interpretation |
| `10.2` | `SEE-TERM-01`, dictionary glossary contract | retained |
| `10.3` | `SEE-REVISION-01` | corrected from same commit to coordinated change |
| `10.4` | `SEE-STRUCT-01` | retained |
| `10.5` | `SEE-REVISION-01` | corrected for separate repositories and pipelines |

## Coverage Declaration

Implemented deterministic evaluation coverage:

- `SEE-SPAN-01`: `evals/grade.py` generated `manifest_protected_spans_*` and `manifest_numbers_units_versions_status_codes_*` checks.
- `SEE-QUOTE-01`: generated `manifest_quoted_spans_*` checks.
- `SEE-BCP14-02`: generated `manifest_expected_obligation_force_*` checks.
- Case-specific lexical and structure predicates: named checks in the frozen SEE JSONL cases.

`SEE-COND-01` requires semantic review. A case can add a deterministic condition predicate only when its source form or required order makes that predicate valid.

Parser-assisted rules: no general production checker is implemented. Semantic review and technical approval remain required. `evals/see-rubric.json` defines the seven review dimensions and critical floors.

## Sources

- ASD-STE100 Issue 9: <https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf>
- ASD-STE100 overview: <https://www.asd-ste100.org/about_STE.html>
- ASD-STE100 tooling guidance: <https://asd-ste100.org/STEsoftware.html>
- ISO 24495-1:2023: <https://www.iso.org/standard/78907.html>
- Controlled-language survey: <https://aclanthology.org/J14-1005/>
- RFC 2119: <https://www.rfc-editor.org/rfc/rfc2119>
- RFC 8174: <https://www.rfc-editor.org/rfc/rfc8174>
- EARS guide: <https://alistairmavin.com/ears/>
- Original EARS paper: <https://doi.org/10.1109/RE.2009.9>
- Ten Years of EARS: <https://doi.org/10.1109/MS.2019.2921164>
- NASA requirements checklist: <https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/>
- Requirements-smell research: <https://arxiv.org/abs/2404.11106>
- Google developer style: <https://developers.google.com/style>
- Google active voice: <https://developers.google.com/style/voice>
- Google contractions: <https://developers.google.com/style/contractions>
- Google tense: <https://developers.google.com/style/tense>
- Google accessibility: <https://developers.google.com/style/accessibility>
- Microsoft verbs: <https://learn.microsoft.com/en-us/style-guide/grammar/verbs>
- Diátaxis: <https://diataxis.fr/>
- WCAG error identification: <https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html>
- WCAG error suggestion: <https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html>
- OWASP error handling: <https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html>
- Vale occurrence: <https://docs.vale.sh/checks/occurrence>
- Vale metric: <https://docs.vale.sh/checks/metric>
- Vale conditional: <https://docs.vale.sh/checks/conditional>
- Vale vocabularies: <https://docs.vale.sh/keys/vocabularies>
- Vale scopes: <https://docs.vale.sh/topics/scopes>
