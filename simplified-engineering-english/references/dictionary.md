# SEE Part 2 — Dictionary

The controlled vocabulary for Simplified Engineering English. Three bounded sets, plus the policy for project-local terms.

Unlike ASD-STE100, this dictionary is **not a closed word list**. Software prose is dominated by identifiers and domain terms that no central list can track. SEE controls the terms that teams actually conflate, and the words that reliably destroy precision.

---

## 1. Confusable Pairs

Each term has one approved sense. Using one for the other is a Rule 1.3 violation. These are the distinctions software teams lose most often.

### Failure vocabulary

| Term | Approved sense |
|---|---|
| `fault` | The defect in the code or configuration. The static cause. |
| `error` | The incorrect internal state produced when the fault is executed. |
| `failure` | The externally observable deviation from the specification. |
| `outage` | A failure that removes availability for users. |
| `incident` | The tracked event and its response process, not the technical failure. |
| `bug` | Informal synonym for `fault`. Acceptable in issue titles, not in analysis. |
| `regression` | A failure in behavior that previously worked. Requires a named prior version. |

A fault causes an error; an error may surface as a failure. Do not write "the error caused the bug."

### Identity and access

| Term | Approved sense |
|---|---|
| `authentication` | Establishing who the principal is. |
| `authorization` | Establishing what the principal may do. |
| `identity` | The principal itself. |
| `credential` | The secret or token that proves identity. |
| `session` | Server-recognized state following authentication. |
| `permission` | A single granted capability. |
| `role` | A named set of permissions. |
| `principal` | Any authenticatable actor: user, service, or agent. |

Never abbreviate either to `auth` in prose. `auth` is permitted only inside a protected span such as `` `authMiddleware` ``.

### Code organization

| Term | Approved sense |
|---|---|
| `module` | A unit of code with a defined interface, in the host language's sense. |
| `package` | A distributable, versioned artifact. |
| `library` | A dependency called by your code. |
| `framework` | A dependency that calls your code. |
| `service` | An independently deployed process with a network interface. |
| `component` | A logical part of a system. Use only when the boundary is stated. |
| `repository` | A version-control repository. Never a storage abstraction unless the project defines it so. |

### Interfaces

| Term | Approved sense |
|---|---|
| `API` | The whole contract a system exposes. |
| `endpoint` | One addressable operation within an API. |
| `route` | The path pattern that reaches an endpoint. |
| `interface` | A language-level type contract. |
| `contract` | The full behavioral agreement, including error and timing behavior. |
| `schema` | The structural definition of data. |
| `protocol` | The wire-level rules of exchange. |

### Parameters and configuration

| Term | Approved sense |
|---|---|
| `parameter` | The declared name in a signature. |
| `argument` | The value passed at a call site. |
| `option` | A user-settable choice with a default. |
| `flag` | A boolean option, or a command-line switch. |
| `setting` | A persisted configuration value. |
| `variable` | A named binding in code. |
| `field` | A member of a struct, object, or record. |
| `property` | A member with accessor semantics. |

### Concurrency

| Term | Approved sense |
|---|---|
| `process` | An OS process with its own address space. |
| `thread` | An OS thread within a process. |
| `task` | A unit of asynchronous work managed by a runtime. |
| `job` | A unit of scheduled or queued work with a lifecycle. |
| `worker` | A long-lived executor that consumes tasks or jobs. |
| `concurrent` | Overlapping in time. |
| `parallel` | Executing simultaneously on separate cores. |
| `asynchronous` | Not blocking the caller. Says nothing about parallelism. |

`concurrent` and `parallel` are not synonyms and must not be swapped.

### Performance

| Term | Approved sense |
|---|---|
| `latency` | Time for one operation, always with a percentile. |
| `throughput` | Operations completed per unit of time. |
| `response time` | Latency measured at the client, including network. |
| `utilization` | Fraction of a resource's capacity in use. |
| `saturation` | The point at which queueing begins. |
| `capacity` | The maximum sustainable load, with its conditions. |

State a percentile with every latency figure. A mean latency is not a claim.

### Data and state

| Term | Approved sense |
|---|---|
| `persist` | Write to durable storage. |
| `cache` | Store a copy for speed, with a defined invalidation rule. |
| `store` | Write, without a durability claim. |
| `record` | One row or document. |
| `entity` | A domain object with identity. |
| `stale` | Correct at an earlier time, not now. |
| `inconsistent` | Two views disagree at the same time. |
| `corrupt` | Structurally invalid. |

### Change and lifecycle

| Term | Approved sense |
|---|---|
| `deprecated` | Still works. Discouraged. Removal version stated. |
| `removed` | No longer present. Names the version that removed it. |
| `breaking change` | Requires a consumer to change code or configuration. |
| `release` | A published, versioned artifact. |
| `deploy` | Move a release into an environment. |
| `rollout` | A progressive deploy. |
| `rollback` | Return to a prior release. |
| `revert` | Undo a commit in version control. |
| `patch` | A change set, or a semantic-version patch increment. State which. |

`deprecated` never means `removed`. Rule 9.3 requires all four deprecation facts.

---

## 2. Rewrite Pairs

Replace the left with the right. Enforceable as a `substitution` rule.

### Verbosity

| Unapproved | Approved |
|---|---|
| utilize, leverage, employ | use |
| commence, initiate, kick off | start |
| terminate, cease | stop, end |
| facilitate, enable (as filler) | name the actual action |
| in order to | to |
| due to the fact that, owing to the fact that | because |
| at this point in time | now, or delete |
| for the purpose of | to, for |
| in the event that | if |
| prior to, subsequent to | before, after |
| a number of, a variety of | state the number |
| is able to, has the ability to | can |
| perform a validation of | validate |
| make a determination | decide |
| provide support for | supports, or name the behavior |
| it should be noted that | delete |
| please note that | delete |

### Vagueness

| Unapproved | Approved |
|---|---|
| simply, just, easily, merely | delete |
| basically, essentially, actually | delete |
| very, quite, fairly, rather | delete, or quantify |
| robust, scalable, performant | state the measured property |
| lightweight, seamless, elegant | delete, or state the measurement |
| best practice | state the practice and why |
| etc., and so on, and more | complete the list |
| and/or | state which, or use `or` with the inclusive case named |
| some, several, many, most | state the number or fraction |
| soon, shortly, in future | state the version or date |
| significantly, dramatically | state the magnitude |

### Idiom

| Unapproved | Approved |
|---|---|
| under the hood | internally |
| out of the box | by default |
| plumbing, glue, magic | name the mechanism |
| gotcha | limitation, or known issue |
| nuke, blow away | delete, remove |
| spin up, stand up | start, create, deploy |
| reach out | contact, ask |
| deep dive | detailed explanation |
| low-hanging fruit | state the change and its cost |
| sanity check | verification, validation |

### False obligation

| Unapproved | Approved |
|---|---|
| you should probably | SHOULD, with the exception condition |
| it is recommended | RECOMMENDED, with the obligated party |
| ideally, preferably | SHOULD, or delete |
| make sure to, be sure to | MUST, or an imperative step |
| try to | MUST or SHOULD. `try` is not an obligation. |
| consider doing | MAY, with the criterion for choosing |

### Ableist or exclusionary

| Unapproved | Approved |
|---|---|
| sanity check | validation, verification |
| dummy value | placeholder, sample |
| master/slave | primary/replica, leader/follower |
| whitelist/blacklist | allowlist/denylist |
| crazy, insane, dumb | state the actual property |
| grandfathered | legacy-exempt |
| obviously, clearly, of course | delete |

`obviously` is prohibited because it is never true for the reader who needs the sentence.

---

## 3. Part-of-Speech Locks

These terms have one approved grammatical role. Converting them is a Rule 1.4 violation.

| Term | Approved as | Prohibited |
|---|---|---|
| `request` | noun | as a verb: "request the endpoint" → "send a request to the endpoint" |
| `impact` | noun | as a verb: "impacts latency" → "increases latency" |
| `architect` | noun | as a verb: "architect a solution" → "design a solution" |
| `access` | noun, verb | fine as both; state the actor when used as a verb |
| `default` | noun, adjective | as a verb: "defaults to" is permitted; "default the value" is not |
| `error` | noun | as a verb: "the call errored" → "the call returned an error" |
| `action` | noun | as a verb: "action the request" → "process the request" |
| `surface` | noun | as a verb: "surface the error" → "display the error" or "return the error" |
| `onboard` | verb | as a noun: "the onboard" → "the onboarding process" |
| `ask`, `spend`, `learning` | verb, verb, verb | as nouns: "the ask" → "the request"; "the spend" → "the cost"; "the learnings" → "what we learned" |

---

## 4. Approved Procedural Verbs

Prefer these in procedural steps. They are unambiguous and translate cleanly.

`add`, `apply`, `build`, `check`, `clone`, `close`, `configure`, `connect`, `copy`, `create`, `delete`, `deploy`, `disable`, `download`, `edit`, `enable`, `enter`, `export`, `import`, `install`, `merge`, `move`, `open`, `press`, `pull`, `push`, `read`, `rename`, `replace`, `restart`, `run`, `save`, `select`, `send`, `set`, `start`, `stop`, `uninstall`, `update`, `upgrade`, `verify`, `wait`, `write`

Notes:

- Use `select` for UI choices, not `click`, `tap`, or `choose`. `select` is device-neutral.
- Use `enter` for typed input, not `type` or `input`.
- Use `run` for commands, not `execute`, `invoke`, `fire`, or `issue`.
- Use `verify` for a check the reader performs, and state the expected observation.

---

## 5. Project Technical Terms

Each project maintains its own glossary. This is SEE's equivalent of STE's Technical Nouns and Technical Verbs: the escape hatch that lets domain vocabulary in under control.

Record each entry with these fields:

```yaml
term: idempotency key
definition: >
  A client-supplied identifier that makes a repeated request return the
  original result instead of performing the operation again.
part_of_speech: noun
short_form: idem key        # optional, defined at first use
replaces: [dedup token, request id]   # terms this supersedes
status: approved            # approved | deprecated | proposed
owner: platform-team
since: v3.1
```

Rules for the glossary:

1. Add a term only when an existing approved term cannot express the concept.
2. One term per concept. Adding a term requires deprecating every synonym it replaces.
3. State the part of speech and honor it (Rule 1.4).
4. Keep the glossary in version control next to the code.
5. Feed the glossary to the checker as a vocabulary file, so that its terms stop being flagged and its deprecated synonyms start being flagged.
6. A deprecated term stays in the glossary with its replacement, so older documents remain interpretable.

---

## 6. Exemptions

The following are never flagged by SEE rules:

- Any protected span under Rule 2.1: identifiers, paths, commands, flags, URLs, versions, literals.
- Quoted output from a tool, log, or error.
- Quoted text from a third-party specification or standard.
- Legally reviewed license, security, or compliance text.
- The literal name of a product, company, protocol, or standard, even when it violates a rewrite pair.
