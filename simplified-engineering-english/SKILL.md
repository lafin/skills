---
name: simplified-engineering-english
description: "Use this skill when writing or reviewing software-engineering prose that people or agents must act on: procedures, runbooks, requirements, contracts, API reference, design documents, ADRs, PRs, issues, comments, error messages, incident records, and diagnostics. It preserves facts, conditions, qualifiers, numbers, units, versions, identifiers, commands, quotations, obligation force, uncertainty, and causal claims while reducing ambiguity. Route document compression, session summaries, evaluation design, tool and project architecture, implementation minimality, ML architecture review, and source-code review to their dedicated skills; SEE governs prose only."
license: MIT
metadata:
  provenance: repository-original
---

# Simplified Engineering English

Simplified Engineering English (SEE) is a controlled-language workflow for software-engineering prose. It adapts selected mechanisms from ASD-STE100 and combines them with explicit software terminology, obligation, evidence, and review rules. SEE does not certify technical correctness.

## Scope

Use SEE when prose controls an operation, implementation, test, audit, translation, agent action, or consequential reader decision.

Do not use SEE to decide architecture, code structure, implementation, test design, or rendered accessibility behavior. Do not use it for marketing, casual chat, or code identifiers. Route information-preserving document compression to `lossless-doc-compress`, session handoffs to `context-compression`, evaluation design to `evaluation`, tool interfaces to `tool-design`, project and pipeline design to `project-development`, ML design review to `ml-system-design-review`, implementation minimality to `leancode`, and source-code complexity review to `leancode-review`.

## Preservation Invariant

A rewrite MUST preserve facts, typed technical roles and relations, conditions, qualifiers, modal, temporal, and provenance scope, numbers, units, versions, identifiers, commands, quotations, obligation force, uncertainty, and supported causal claims. Keep each source audience, organization, product scope, deployment scope, and environment scope in the rewritten content. Preserve product, system, person, and named-scope capitalization; a lowercase occurrence inside a command does not replace the prose name. Copy every explicitly exact output token character by character without adding punctuation. Name both roles and their relation; for example, do not replace “a parameter receives an argument” with “a parameter is set to a value.” Preserve every character inside a quotation, including punctuation; do not move outside punctuation into the quotation.
Treat each quoted span, including its quotation marks, as one indivisible token. If a rewrite moves the span to a sentence end, put new sentence punctuation after the closing quotation mark; never insert it inside the exact span.
Treat each task-declared exact field value as a literal token. After the field separator, emit only the requested value; do not append a period, semicolon, quotation mark, or annotation.

Authorized safety, security, privacy, legal, or regulatory redaction can replace protected content. Record the redaction. Do not treat an exemption from rewriting as proof that the content is correct or safe to publish.

Use task context to interpret the source. Do not copy a governing declaration or other context into the rewrite unless it is part of the source or the required output.

If the source satisfies every applicable error-level rule, return it unchanged. A warning, suggestion, optional detail, or possible precision improvement is not a consequential defect. When a task identifies text as already precise or compliant and requests no-op preservation, treat that characterization as authoritative unless it directly contradicts a source fact or a safety, security, obligation, or preservation rule. Otherwise, return the exact source and report no ambiguity.

## Precedence

Apply rules in this order:

1. Safety, security, privacy, legal, and regulatory constraints.
2. Technical meaning, including facts, scope, conditions, qualifiers, units, versions, uncertainty, and obligation force.
3. Verbatim identifiers, commands, literal values, and required quotations, except for authorized redaction.
4. Authoritative language, protocol, platform, and product terminology.
5. The project glossary and artifact contract.
6. The selected SEE profile and artifact card.
7. General SEE defaults.
8. Concision and stylistic preference.

A lower-precedence rule MUST NOT alter a higher-precedence property.

## Select a Profile

| Profile | Use for | Rule posture |
| --- | --- | --- |
| Strict controlled | Safety-critical, regulated, equipment-maintenance, or translation-sensitive text; projects that explicitly require STE-like controls | Technical safeguards and declared grammar controls are errors. Apply 20-word procedural and 25-word descriptive limits, restricted voice and tense, no contractions, controlled multi-word nouns, project-approved vocabulary, and the documented word count. |
| Engineering-default | Design documents, ADRs, PRs, issues, ordinary developer documentation, comments, and explanatory API documentation | Technical safeguards are errors. Voice, tense, length, contractions, semicolons, and similar style signals are warnings or project choices unless they obscure meaning. |

Do not infer the strict profile from the artifact name alone. Use the project declaration or task requirement. If neither selects strict, use engineering-default.

## Select an Artifact Card

For a mixed artifact, apply each card only to its matching blocks.

### Procedure and runbook

Require prerequisites, imperative steps, one consequential action per step, and conditions before actions when early action can cause an error. State an observable result when success is not self-evident. Put risk information before the governed action. When authoring a procedure, state rollback or irreversibility for state-changing, destructive, costly, security-sensitive, or availability-affecting work. When rewriting source text, do not add a rollback, irreversibility, recovery-availability, or missing-recovery claim that the source does not contain unless the task explicitly requests a gap analysis. Do not require rollback text for read-only diagnostics.

### Requirement and contract

Require a declared obligation convention, one independently verifiable obligation per statement, an explicit subject and response, applicable conditions and measurable limits, an objective verification method, and rationale outside normative text. Preserve each named obligation convention and standard that the source declares. A trigger, response, bound, and unit can supply objective pass-fail evidence; do not demand extra environment or measurement detail unless the source permits materially different verdicts. Use EARS when its temporal clauses fit the intended behavior. Do not force EARS onto every constraint, interface rule, or quality attribute. Route traceability, completeness, feasibility, assumptions, and unresolved values to requirements governance.

### Explanation and reference

State the reader need and scope near the start. Order information by dependency. Keep terminology stable. Distinguish behavior, rationale, recommendation, and implementation detail. Declare product and version scope at document or section level. Use meaningful headings and links. Report every unresolved vague performance, reliability, scale, or security claim when the source does not support a precise replacement. Use Diátaxis to classify the reader need, not to infer sentence limits.

### Error, incident, and diagnostic record

State what failed or what was observed. Give a cause only when it is known and safe for the audience. Give a recovery action when one exists. Name the affected input or resource when disclosure is safe. In review findings, name every source-declared missing operation, input or resource, cause, and recovery detail that limits actionability. If the source provides no cause, state that the cause is unknown. Do not infer missing details. Separate user-facing details from operator diagnostics. When a visual cue has no source text equivalent, preserve its description, do not invent an equivalent, and report the missing nonvisual equivalent. Mark observations, reports, inferences, assumptions, and unknowns where provenance matters. Keep timeline facts separate from causal hypotheses.
For an unknown cause, use an explicit cause statement such as “The cause is unknown.” Do not use a vague failure adjective such as “unspecified” as a substitute.
If the source reports an observation but no failure, do not add an unknown-cause statement or a missing-recovery finding.

## Rewrite Workflow

1. Honor an explicit no-op constraint before applying style guidance. Then identify the audience, publication channel, artifact card, and selected profile.
2. Inventory source facts, typed technical roles and relations, conditions, exceptions, modal, temporal, and provenance qualifiers, numbers, units, versions, status codes, protected spans, quotations, obligation force, uncertainty, and causal claims. Keep descriptive facts separate from obligations: never add a declared obligation keyword to a statement that does not contain one. Preserve authorization tense and exclusive scope.
3. Identify authorized redactions and authoritative ecosystem or project terminology.
4. Apply the dictionary and detailed rules without changing the inventory.
5. Restructure the artifact only as much as the identified defects require.
6. Report consequential source ambiguity instead of selecting an unsupported interpretation. Before reporting an ambiguity, identify at least two materially different interpretations supported by the source and the consequential difference. The absence of an unstated detail and the conventional omitted subject of an imperative are not ambiguities by themselves. A vague term, placeholder noun, or underdefined criterion in the source can be ambiguous when it permits materially different actions, referents, or verification verdicts; report those interpretations and their consequence. If the source does not support two interpretations, do not report an ambiguity; preserve explicit uncertainty or an evidence limitation as a fact.
7. Run a literal-preservation gate before returning: for each exact token, protected name, command, value, and quotation, search for the exact source bytes in the rewritten content. A copy in an ambiguity, rationale, or metadata field does not satisfy preservation in the rewrite. If a span is missing, paste the source span back without retyping or editing it. Check punctuation immediately before and after quotations separately. Then compare the rewrite with the full inventory and resolve every unexplained difference.
8. Report deterministic coverage, semantic findings with source spans, technical-review status, and unsupported claims.

## Conflicts and Ambiguity

Do not invent an actor to remove passive voice. Do not invent a threshold to make a requirement measurable. Do not invent a cause or recovery to make an error actionable. Do not delete a condition, exception, negative prohibition, uncertainty marker, mean measurement, or required qualification to shorten a sentence.

An ambiguity is consequential only when the source supports materially different actions, obligations, technical interpretations, verification verdicts, or security outcomes. Treat a reference as resolved when it has one grammatically and technically compatible antecedent; do not hypothesize an unmentioned alternative. Do not report a merely possible refinement as an ambiguity. Report each unresolved vague claim explicitly; retaining its words does not resolve it.

When authoritative terminology conflicts with an SEE default, use the authoritative term. When a project glossary is authoritative and unambiguous, it overrides an SEE default. Record unresolved conflicts for the technical reviewer.

## Verification and Reporting

Use deterministic checks for exact lexical or structural predicates. Use parser-assisted checks for cross-block structure. Use semantic review for word sense, ambiguity, atomicity, EARS suitability, measurable evidence, safe disclosure, completeness, uncertainty, and causal status. A qualified technical reviewer remains responsible for correctness, safety, security, feasibility, operational validity, product terminology, and approval to publish.

A requirement can use a test, demonstration, inspection, or analysis as its objective verification method. Naming a test is neither necessary nor sufficient.

When reporting a review, include:

```text
Profile: <strict | engineering-default>
Artifact card: <card name>
Deterministic checks: <rule IDs or none>
Parser-assisted checks: <rule IDs or none>
Semantic findings: <rule ID, source span, evidence, or none>
Technical approval: <complete | required>
Ambiguities: <items or none>
Unsupported claims: <items or none>
```

Do not describe text as SEE-conforming unless every applicable rule has an enforcement result and the required technical review is complete.

## References

- Detailed rules, sources, profiles, severities, enforcement classes, examples, and legacy-rule inventory: `references/rules.md`
- Material terminology distinctions, lexical defaults, project glossary governance, and exemptions: `references/dictionary.md`

SEE derives its controlled-language structure from ASD-STE100. The detailed reference identifies adopted, adapted, SEE-policy, house-style, and heuristic relationships. SEE reproduces no official STE dictionary and makes no certification claim.
