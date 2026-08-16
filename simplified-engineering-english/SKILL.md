---
name: simplified-engineering-english
description: "This skill should be used when writing or reviewing any software-engineering prose that other people or agents must act on: documentation, README files, API reference, requirements, design docs, ADRs, commit messages, changelogs, PR descriptions, issue reports, code comments, error messages, runbooks, and incident reports. It defines Simplified Engineering English (SEE), a controlled subset of English for software engineering derived from ASD-STE100 Simplified Technical English. Use it to remove ambiguity, fix vague or unverifiable claims, enforce one term per concept, and make prose machine-checkable. Route code structure and implementation decisions elsewhere; this skill governs language only."
license: MIT
---

# Simplified Engineering English (SEE)

Simplified Engineering English is a controlled subset of English for software-engineering communication. It restricts vocabulary, grammar, information order, and claim strength so that a sentence has one reasonable interpretation for a reader who is tired, non-native, remote, or a language model.

SEE is a derivative of **ASD-STE100 Simplified Technical English** (STE), the aerospace standard maintained by the ASD Simplified Technical English Maintenance Group. STE was created in 1983 because aircraft-maintenance manuals were misread and mistranslated, with safety consequences. Issue 9 (January 2025) contains 53 writing rules in 9 sections and a dictionary of approximately 900 approved words. SEE keeps STE's architecture and replaces its aerospace assumptions with software ones.

**No official STE dictionary or supplement for software exists.** The adjacent work covers separate layers: EARS constrains requirements syntax, RFC 2119 defines obligation keywords, Conventional Commits constrains commit structure, Diátaxis separates document purposes, and the Google, Microsoft, and IBM style guides supply editorial word lists. None of them unifies controlled vocabulary, software grammar, per-artifact modes, obligation semantics, and conformance levels. SEE is that unification.

## When to Activate

Activate SEE when prose carries operational consequence:

- A reader will execute a procedure, run a command, or change a production system.
- A statement will be implemented, tested, or audited as a requirement.
- The text will be translated, or read by many non-native speakers.
- The text will be consumed by an agent that cannot ask a clarifying question.
- A review found ambiguity, drift in terminology, or unverifiable claims.
- The team is standardizing documentation, commit, ADR, or error-message practice.

Do not activate SEE for marketing copy, blog posts, conference talks, casual chat, or code identifiers. SEE governs prose. It does not govern code style, naming conventions inside source files, or architecture.

## Core Principles

**Control the whole writing system, not the word length.** STE's transferable idea is not "use short words." It is that vocabulary, grammar, information order, terminology, and review are governed together. A four-word sentence can still be wrong.

**One concept, one term. One term, one concept.** Synonym variation is a defect, not style. If the codebase says `job`, the documentation says `job`, not `task`, `work item`, or `unit`. Repetition is intentional.

**Protect the code, control the prose.** STE closes its dictionary to about 900 words. Software cannot: identifiers, APIs, protocols, and product names are the payload. SEE therefore exempts protected spans entirely (Section 2) and applies lexical control only to the connective English between them.

**Every claim declares its strength and its evidence.** Software prose fails less from long sentences than from claims whose obligation level, version scope, and epistemic status are invisible. Sections 7, 8, and 9 have no STE equivalent and carry most of SEE's value.

**Rules do not replace review.** A conforming document can be technically wrong, incomplete, or missing a prerequisite. SEE reduces a class of failure; it does not certify correctness.

---

# Part 1 — Writing Rules

SEE defines **82 rules in 10 sections**. Sections 1 through 6 and 10 adapt STE. Sections 7, 8, and 9 are new for software.

## Section 1 — Words and Terms

**1.1** Use the approved term for a concept, and use it every time. See `references/dictionary.md`.

**1.2** Do not use a term that the dictionary marks unapproved when an approved replacement exists. Replace `utilize` with `use`, `leverage` with `use`, `commence` with `start`, `in order to` with `to`.

**1.3** Use a controlled term with its approved sense only. `Error`, `fault`, and `failure` are distinct and are not interchangeable. So are `authenticate` and `authorize`, `parameter` and `argument`, `module` and `package`, `latency` and `response time`.

**1.4** Do not convert a controlled noun into a verb, or a controlled verb into a noun. Write `send a request`, not `request the server`. Write `deploy the service`, not `do a deployment of the service`, unless the noun form is the approved one.

**1.5** Do not use a vague quantifier or intensifier: `simply`, `just`, `easily`, `quickly`, `robust`, `scalable`, `performant`, `lightweight`, `seamless`, `basically`, `essentially`. Delete it, or replace it with a number.

**1.6** Do not use `etc.`, `and/or`, `and so on`, or an open-ended list. State the complete set, or name the rule that generates it.

**1.7** Define an abbreviation at first use in each document, then use it consistently. Do not define an abbreviation used once; write it out.

**1.8** Do not use an ambiguous pronoun. If `it`, `this`, `that`, or `they` could refer to more than one preceding noun, repeat the noun.

**1.9** Do not use a metaphor, idiom, or culture-specific reference. Replace `under the hood` with `internally`, `out of the box` with `by default`, `a piece of cake` with `simple` or a measured claim.

**1.10** Do not use a negative construction where a positive one exists. Write `the cache holds 100 entries`, not `the cache does not hold more than 100 entries`.

**1.11** Do not stack negatives. `Do not disable the flag unless verification is not required` is prohibited.

**1.12** Use American English spelling unless the project mandates another variant. Record the choice once, in the project configuration.

**1.13** Do not use an emoji, decorative symbol, or typographic ornament to carry meaning. Meaning that depends on a glyph is lost to screen readers, plain-text pipelines, and diffs.

**1.14** Introduce a new domain term explicitly. Write the full term first, then the short form in parentheses, then use the short form.

## Section 2 — Protected Spans

A **protected span** is text that names an entity in a system. It is exempt from Sections 1, 3, and 4, and counts as one word (Rule 4.6).

**2.1** Treat the following as protected spans: identifiers, type names, file paths, commands, flags, environment variables, HTTP methods, status codes, error codes, URLs, version strings, and literal values.

**2.2** Mark every protected span with code formatting when the format supports it. Write the identifier in backticks, not as bare text and not as an English phrase such as "the retry count field".

**2.3** Do not alter a protected span to satisfy a prose rule. Do not pluralize, hyphenate, capitalize, or translate an identifier. Write ``two `Job` records``, not ``two `Job`s``.

**2.4** Do not use a protected span as an English part of speech. Write ``call `flush()` `` or ``the `flush()` method``, not ``you should `flush()` the buffer before you `close()` it``, where the identifier substitutes for the verb.

**2.5** Distinguish the entity from the concept. `` `user` `` is a variable; a user is a person. Never let the reader guess which one a sentence means.

**2.6** Limit a compound noun phrase to **three words**, excluding protected spans. Rewrite `service account token rotation policy failure` as `a failure in the rotation policy for service-account tokens`. This is STE Rule 2.1, and it is the single most effective rule against unreadable software prose.

**2.7** If an established term exceeds three words, write it in full once, then use an approved short form.

## Section 3 — Verbs and Voice

**3.1** Use active voice. Name the actor.

**3.2** Use passive voice only when the actor is genuinely unknown, genuinely irrelevant, or deliberately unnamed, and only in explanatory text. Never use passive voice in a procedure or a requirement.

**3.3** Use simple present for behavior that holds now. Use simple past for a completed event. Use simple future only for a scheduled change with a stated version or date.

**3.4** Do not use a compound or perfect construction: `has been running`, `will have completed`, `would have been retried`. Use the simple form.

**3.5** Do not use an `-ing` form as a verb or as a sentence opener. Replace `Starting the server, the config loads` with `When the server starts, it loads the config`. An `-ing` word that is an established noun (`logging`, `caching`, `testing`) or part of an approved term is permitted.

**3.6** Do not hide an action inside an abstract noun. Write `the scheduler retries the job`, not `retry of the job is performed by the scheduler`. Prohibited nominalizations include `perform a validation`, `provide support for`, `make a determination`, and `carry out an execution`.

**3.7** Do not use `allow`, `enable`, or `support` as the main verb of a behavior claim without naming who does what. Replace "the API supports pagination" with "the API returns at most 100 items per page and a `nextPageToken` for the next page".

**3.8** Do not use a modal that conceals an obligation. `Can`, `might`, `may`, and `should` are governed by Section 7.

## Section 4 — Sentences and Counting

**4.1** Use a maximum of **20 words** in a procedural sentence, a requirement, an error message, or a warning.

**4.2** Use a maximum of **25 words** in an explanatory sentence or a note.

**4.3** Put one subject in each sentence.

**4.4** Do not omit an article or a required word to save length. `Set flag` is prohibited; write `Set the flag`.

**4.5** Use a vertical list for three or more parallel items, conditions, or alternatives. Do not embed a list in a sentence with `and` and commas.

**4.6** Count a protected span, a hyphenated term, a number with its unit, and a parenthetical as **one word**.

**4.7** Do not use a semicolon. Write two sentences.

**4.8** Do not use a contraction.

**4.9** Do not use a parenthetical to carry required information. If the reader must know it, it belongs in a sentence.

**4.10** Use no more than **six sentences** in a paragraph, and one topic per paragraph.

## Section 5 — Procedures

A procedure tells a reader to do something. This includes runbooks, how-to guides, installation steps, migration guides, and incident response.

**5.1** Write each step in the imperative. `Run the migration.` Not `The migration should be run.` Not `You will want to run the migration.`

**5.2** Put one instruction in each step. Combine actions only when they are simultaneous or when the second follows immediately and automatically.

**5.3** Put the condition before the command, and separate it with a comma. `If the pod is in CrashLoopBackOff, delete the pod.` Never `Delete the pod if the pod is in CrashLoopBackOff.` A reader who acts on the first half of the sentence must not act wrongly.

**5.4** State the prerequisites before the first step, as a list. Include required access, required tools with versions, and required state.

**5.5** State the expected result after any step whose success is not self-evident. Give the observable signal, not the internal mechanism.

**5.6** Number the steps of a sequence. Do not number a set of alternatives; use a list with an explicit `Choose one:`.

**5.7** State how to undo the procedure, or state explicitly that it cannot be undone. See Section 8.

**5.8** Use a note for information only. A note must not contain an instruction, a requirement, a limit, or a risk. Move any of those into a step, a requirement, or a warning.

## Section 6 — Explanations

An explanation tells a reader how or why something works. This includes architecture documents, design rationale, concept pages, and the body of an ADR.

**6.1** Give information in order of dependency. Do not use a term or concept before you define it.

**6.2** Repeat the key term rather than substituting a synonym or a pronoun.

**6.3** State the subject of the explanation in the first sentence of the section.

**6.4** Separate the mechanism from the rationale. Say what the system does, then say why it was built that way. Do not interleave them.

**6.5** Do not explain a procedure in explanatory prose. Link to the procedure.

**6.6** State what is out of scope when a reader could reasonably expect it to be in scope.

## Section 7 — Obligation

Every normative statement declares its strength. SEE adopts the RFC 2119 and RFC 8174 keywords and adds their scope discipline.

**7.1** Use an obligation keyword in uppercase and only in its defined sense: **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT** for absolutes; **SHOULD**, **SHOULD NOT**, **RECOMMENDED** for defaults that permit a justified exception; **MAY**, **OPTIONAL** for genuine freedom.

**7.2** Use exactly one obligation keyword in a normative sentence.

**7.3** Name the obligated party. `The client MUST retry` is valid. `Retries MUST happen` is not.

**7.4** State the exception condition whenever SHOULD or SHOULD NOT is used. A SHOULD with no stated escape is a MUST written weakly.

**7.5** Do not use lowercase `must`, `should`, or `may` to express an obligation in a normative document. Use them only in explanatory prose, where they carry no normative weight.

**7.6** Distinguish a **guarantee** from a **recommendation** from an **implementation detail**. Mark a statement about current internal behavior explicitly as non-contractual if callers must not depend on it.

**7.7** Write a requirement in one of the five EARS patterns:

| Pattern | Form |
|---|---|
| Ubiquitous | The `<system>` SHALL `<response>`. |
| Event-driven | When `<trigger>`, the `<system>` SHALL `<response>`. |
| State-driven | While `<state>`, the `<system>` SHALL `<response>`. |
| Optional feature | Where `<feature>` is enabled, the `<system>` SHALL `<response>`. |
| Unwanted behavior | If `<condition>`, then the `<system>` SHALL `<response>`. |

Combine only as `While <state>, when <trigger>, the <system> SHALL <response>`.

**7.8** Make every requirement atomic, verifiable, and free of implementation detail. If you cannot name the test that would fail, the requirement is not a requirement.

**7.9** Keep rationale out of the requirement sentence. Put it in an adjacent `Rationale:` line.

## Section 8 — Risk and Destructive Operations

This section is the software analogue of STE's warnings and cautions. Its labels are fixed and its structure is mandatory.

**8.1** Use one of three labels, by consequence:

| Label | Consequence |
|---|---|
| **WARNING** | Irreversible loss: data deletion, key destruction, customer impact, security exposure. |
| **CAUTION** | Recoverable damage: downtime, cost, degraded state, manual repair. |
| **NOTE** | No damage. Information only. |

**8.2** Structure a WARNING or CAUTION in three parts, in this order: the command or condition, the consequence, and the required precaution or recovery.

> **WARNING:** `terraform destroy` deletes every resource in the workspace. Recovery requires a restore from backup. Confirm the workspace name before you run it.

**8.3** Place the warning **before** the step it governs, never after and never in a footnote.

**8.4** State the blast radius: what is affected, and what is not.

**8.5** Do not use a WARNING for a non-destructive inconvenience. Label inflation destroys the signal.

**8.6** Write an error message with three elements in order: what failed, why, and the next action. Name the specific input or resource. Do not blame the user. Do not leak a secret, a token, or an internal path.

> `Cannot parse config at /etc/app.yaml line 12: 'timeout' expects a duration such as '30s', found '30'. Add a unit suffix.`

**8.7** State the failure mode of every retry, timeout, and fallback. Silence about failure is a defect.

## Section 9 — Time, Version, and Evidence

Software prose rots. This section stops it.

**9.1** Do not use a floating time reference: `currently`, `now`, `recently`, `soon`, `new`, `legacy`, `upcoming`, `at the moment`, `in the near future`. Use a version, a date, or delete the sentence.

**9.2** Scope a behavior claim to a version or a version range. `Since v2.4, the client retries idempotent requests.`

**9.3** State a deprecation with four facts: what is deprecated, the version that deprecated it, the replacement, and the version that removes it. Do not use `deprecated` to mean `removed`, or the reverse.

**9.4** Do not describe a plan as a fact. A statement about unshipped work is marked as a plan and carries an owner or a tracking reference.

**9.5** Mark the epistemic status of any non-obvious claim:

| Status | Marker | Meaning |
|---|---|---|
| Observed | `Observed:` | Measured or reproduced. State how. |
| Reported | `Reported:` | Someone stated it. Name the source. |
| Inferred | `Inferred:` | Derived from evidence. State the evidence. |
| Assumed | `Assumed:` | Believed, unverified. State how to verify. |
| Unknown | `Unknown:` | Explicitly not established. |

**9.6** Do not state a performance, security, reliability, or scale claim without its measurement conditions. `p99 latency is 40 ms at 500 requests per second on a 4-core node` is a claim. `It is fast` is not.

**9.7** In an incident report or a debugging note, separate the timeline of observed facts from the causal hypothesis. Never write a hypothesis in the past indicative as though it were confirmed.

**9.8** Attribute a decision. An ADR, a design choice, and a trade-off record the decider and the date.

## Section 10 — Consistency and Revision

**10.1** Use the same sentence pattern for the same kind of statement throughout a document set.

**10.2** Maintain a project glossary of approved technical terms with their definitions and their part of speech. This is the project's extension of Part 2.

**10.3** When a term changes, change every occurrence in the same commit.

**10.4** Rewrite the sentence when word substitution is not enough. Most SEE violations are structural, not lexical.

**10.5** Keep the prose and the code in one commit. Documentation that lags the code is worse than absent documentation, because it is trusted.

---

# Part 2 — Dictionary

The controlled vocabulary, the confusable-term table, the rewrite pairs, and the term-governance policy are in `references/dictionary.md`.

SEE does **not** define a closed ~900-word list as STE does. In software, the closed list is the wrong mechanism: the vocabulary is dominated by identifiers and domain terms, and it turns over faster than any committee. SEE instead controls three bounded sets:

1. **Confusable pairs** — terms teams genuinely conflate, each with its distinct sense.
2. **Rewrite pairs** — unapproved words with a mandatory replacement.
3. **Project technical terms** — the local glossary each project owns, with definition and part of speech.

Everything else is unconstrained prose subject to Part 1.

---

# Artifact Modes

Different artifacts obey different subsets. Apply the mode, not the whole standard, to every artifact.

| Artifact | Sentence cap | Required sections | Notes |
|---|---|---|---|
| How-to, runbook, install guide | 20 | 1–5, 8, 10 | Imperative. Prerequisites and rollback mandatory. |
| Tutorial | 25 | 1–6, 10 | Explanation permitted between steps. |
| API reference | 20 | 1–4, 7, 9 | Every guarantee marked. Every claim version-scoped. |
| Architecture / concept doc | 25 | 1–4, 6, 9, 10 | Mechanism separated from rationale. |
| Requirement / spec | 20 | 1–4, 7 | EARS pattern mandatory. One obligation per statement. |
| ADR | 25 | 1–4, 6, 7, 9 | Context, options, decision, consequences, decider, date. |
| Commit message | 20 | 1–4, 9 | Conventional Commits structure. Imperative subject. State what changed and why. |
| Changelog entry | 20 | 1–4, 9 | Keep a Changelog categories. Reader-visible effect, not internal diff. |
| PR description | 25 | 1–4, 9 | What, why, risk, how verified. |
| Issue / bug report | 25 | 1–4, 9 | Observed vs expected. Reproduction steps as a procedure. |
| Code comment | 25 | 1–4, 6, 9 | Explain why, not what. Never restate the code. |
| Error message | 20 | 1–4, 8 | Rule 8.6 structure. One sentence where possible. |
| Incident report | 25 | 1–9 | Timeline of facts separated from hypothesis (9.7). |
| Agent instruction / prompt | 20 | 1–5, 7, 8 | Obligation keywords mandatory. No ambiguous pronouns. |

---

# Conformance Levels

Adopt SEE incrementally. Declare the level in the project configuration.

- **Level 1 — Terminology.** Sections 1, 2, 10. Rewrite pairs enforced, one term per concept, protected spans marked. Fully machine-checkable. This level alone captures most of the benefit.
- **Level 2 — Grammar.** Adds Sections 3 and 4. Active voice, simple tense, sentence caps, no semicolons, no nominalizations. Largely machine-checkable.
- **Level 3 — Structure.** Adds Sections 5, 6, and 8. Artifact modes applied, procedures imperative and condition-first, warnings structured and correctly placed. Partly machine-checkable.
- **Level 4 — Semantics.** Adds Sections 7 and 9. Obligation keywords, EARS requirements, version scoping, evidence markers. Machine-checkable in shape, human-checkable in truth.

Do not claim a level the checker does not run in CI.

---

# Enforcement

Encode Levels 1 and 2 in `vale` styles, which express rules as YAML and already ship Microsoft, Google, and Red Hat vocabularies:

- `substitution` for rewrite pairs (Rule 1.2).
- `existence` for prohibited words (1.5, 1.6, 1.9, 9.1) and for the semicolon and contractions (4.7, 4.8).
- `consistency` for confusable pairs (1.3).
- `occurrence` for sentence caps (4.1, 4.2) and paragraph length (4.10).
- `conditional` for abbreviation definition (1.7) and deprecation completeness (9.3).
- Vocabulary files for the project glossary (10.2), which also suppresses false positives on identifiers.

Level 3 structure checks fit `textlint` or a custom linter with document-tree access. Level 4 requires human or model review; a language model is an effective SEE reviewer because every rule is a stated, checkable predicate.

Three limits, taken directly from the STEMG's own guidance on STE tooling:

1. A checker finds violations. It does not write conforming prose.
2. A checker cannot judge whether a sentence is technically correct.
3. A green check is not approval. Human technical review remains mandatory.

---

# Governance

**Term proposals.** Anyone proposes a term for the project glossary. The proposal states the term, its definition, its part of speech, and the terms it replaces.

**Review.** A named terminology owner accepts or rejects it. One owner per project, not a committee.

**Versioning.** The glossary is versioned with the code. A term change is a breaking change to the documentation set and updates every occurrence (Rule 10.3).

**Deprecation.** A retired term stays in the glossary marked as deprecated with its replacement, so old documents remain interpretable.

---

# What SEE Deliberately Does Not Do

- **No closed word list.** Software vocabulary is open. Closing it would fail, and maintaining ~900 approved general words is cost without return when identifiers dominate the text.
- **No part-of-speech lock across the whole lexicon.** STE locks every approved word. SEE locks only the controlled terms in the dictionary, because software prose needs ordinary English flexibility for its connective tissue.
- **No formal semantics.** Attempto Controlled English maps English to logic. That is a different and much more restrictive goal. SEE stays readable as ordinary English.
- **No style opinion.** SEE has no view on Oxford commas, heading case, or tone. Those belong to a house style guide and compose with SEE.
- **No prose in code identifiers.** Naming conventions belong to the language's own style guide.

---

# Attribution

Derived from the architecture of **ASD-STE100 Simplified Technical English**, © ASD (Aerospace, Security and Defence Industries Association of Europe), maintained by the ASD STEMG and available at [asd-ste100.org](https://asd-ste100.org/). SEE paraphrases STE's mechanisms and reproduces no part of the standard's text or dictionary. Sentence caps (20 procedural / 25 descriptive), the three-word noun-cluster limit, and the condition-before-command rule are STE's, adapted here for software.

SEE also incorporates:

- **EARS** (Easy Approach to Requirements Syntax), Alistair Mavin — the five requirement patterns in Rule 7.7.
- **RFC 2119 / RFC 8174** — the obligation keywords in Section 7.
- **Conventional Commits** and **Keep a Changelog** — artifact structure in the modes table.
- **Diátaxis**, Daniele Procida — the artifact-mode separation.
- **ISO 24495-1:2023** plain-language principles and the **Google** and **Microsoft** developer style guides — informing the rewrite pairs.
