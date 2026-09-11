# SEE Dictionary

This reference controls only material terminology, lexical defaults, project glossary governance, and rewrite exemptions. It is not a closed word list.

## Precedence

Use terminology in this order:

1. An authoritative language, protocol, platform, product, safety, security, legal, or regulatory source.
2. The project glossary and artifact contract.
3. SEE material distinctions and lexical defaults.

A project glossary overrides an SEE default when the project term is authoritative and unambiguous. An override does not permit one term to mean two concepts in the same scope.

## Material Cross-Domain Distinctions

These distinctions are errors in both profiles when conflation changes technical meaning.

### Failure

| Term | Meaning |
| --- | --- |
| `fault` | A defect in code or configuration: the static cause. |
| `error` | An incorrect internal state produced when a fault is activated. |
| `failure` | An externally observable deviation from the applicable specification. |
| `outage` | A failure that removes availability for users. |
| `incident` | A tracked event and its response process. |
| `regression` | A failure in behavior that worked in a named prior version. |

A fault can produce an error. An error can result in a failure. Use `bug` only when the artifact permits the informal synonym for `fault`.

### Identity and access

| Term | Meaning |
| --- | --- |
| `authentication`; `authenticate` | Establish who a principal is. |
| `authorization`; `authorize` | Establish what a principal may do. |
| `identity` | The principal. |
| `credential` | A secret or token that proves identity. |
| `session` | Server-recognized state after authentication. |
| `permission` | One granted capability. |
| `role` | A named set of permissions. |
| `principal` | An actor that can authenticate, such as a user or service. |

Do not replace authentication with authorization, or the reverse. Use bare `auth` only when an authoritative project term defines it or when it is a protected identifier.

### Parameters and configuration

| Term | Meaning |
| --- | --- |
| `parameter` | A declared name in a signature. |
| `argument` | A value passed at a call site. |
| `option` | A user-settable choice, possibly with a default. |
| `flag` | A Boolean option or command-line switch. |
| `setting` | A persisted configuration value. |
| `variable` | A named binding in code. |
| `field` | A member of a structure, object, or record. |
| `property` | A member with accessor semantics. |

### Concurrency

| Term | Meaning |
| --- | --- |
| `process` | An operating-system process with its own address space. |
| `thread` | An operating-system thread in a process. |
| `task` | A unit of asynchronous work managed by a runtime. |
| `job` | A scheduled or queued unit of work with a lifecycle. |
| `worker` | A long-lived executor that consumes tasks or jobs. |
| `concurrent`; `concurrency` | Work whose execution intervals overlap. |
| `parallel`; `parallelism` | Work that executes simultaneously on separate processing resources. |
| `asynchronous`; `asynchrony` | A relationship in which the caller does not wait for completion. It does not assert parallel execution. |

### Lifecycle

| Term | Meaning |
| --- | --- |
| `deprecated` | Still available but discouraged. The record names the replacement and removal plan. |
| `removed` | No longer available in the named version. |
| `breaking change` | A change that requires a consumer to change code or configuration. |
| `release` | A published versioned artifact. |
| `deploy` | Put a release into an environment. |
| `rollout` | Progressively deploy a release. |
| `rollback` | Return an environment to a prior release. |
| `revert` | Undo a version-control change. |

## Override-Aware Software Defaults

The following senses are SEE defaults, not universal definitions. Use an authoritative ecosystem or project sense when it differs.

| Term | SEE default sense |
| --- | --- |
| `module` | A code unit with an interface in the host language. |
| `package` | A distributable or language-defined collection. |
| `library` | A dependency that application code calls. |
| `framework` | A dependency that controls application flow and calls application code. |
| `service` | An independently operated capability, often exposed through a network interface. |
| `component` | A stated logical or deployment boundary. Name the boundary. |
| `repository` | A version-control repository. State another authoritative sense when needed. |
| `API` | A system's exposed contract. |
| `endpoint` | One addressable operation in an API. |
| `route` | A path or dispatch pattern that reaches an endpoint. |
| `interface` | A language or system boundary contract. |
| `contract` | A behavioral agreement, including applicable error and timing behavior. |
| `schema` | A structural data definition. |
| `protocol` | Rules for an exchange. |
| `latency` | Time for an operation. State the statistic and measurement point needed for the decision. |
| `response time` | Latency measured at a stated boundary, often the client. |
| `throughput` | Completed operations per unit of time under stated conditions. |
| `capacity` | Maximum sustainable load under stated conditions. |
| `cache` | A copy retained to reduce access cost, with an applicable invalidation rule. |
| `store` | Write data without an implied durability level. |
| `persist` | Write data to storage that meets a stated durability guarantee. |
| `record` | One row, document, event, or ecosystem-defined data unit. |
| `entity` | A domain object with identity. |
| `stale` | Correct for an earlier state or time but not for the declared reference state or time. |
| `inconsistent` | Two applicable views disagree for the same reference state. |
| `corrupt` | Invalid under a named structural or integrity rule. |

A mean latency is a measurement claim. State whether the decision needs a mean, percentile, distribution, or another statistic. Give the workload, sample or interval, and measurement point required to interpret the claim.

## Lexical Defaults

Apply these replacements only to surrounding prose, not protected or quoted text. A replacement must preserve technical meaning.

| Avoid | Replace with |
| --- | --- |
| utilize, leverage, employ | use, when `use` preserves the relationship |
| commence, initiate, kick off | start |
| terminate, cease | stop or end, according to the lifecycle |
| facilitate, enable, support as filler | name the concrete behavior |
| in order to | to |
| due to the fact that, owing to the fact that | because |
| at this point in time | `now` only for an immediate unambiguous observation or procedure; otherwise use a date or version, or delete |
| for the purpose of | to or for |
| in the event that | if |
| prior to, subsequent to | before, after |
| a number of, a variety of, some, several, many, most | state the number, fraction, or rule that defines the set |
| is able to, has the ability to | can, when capability is intended |
| perform a validation of | validate |
| make a determination | decide |
| it should be noted that, please note that | delete |
| simply, just, easily, merely, basically, essentially, actually | delete unless technically required |
| very, quite, fairly, rather, significantly, dramatically | quantify or delete |
| robust, scalable, performant, lightweight, seamless, elegant | state the measured property or delete |
| best practice | state the practice and reason |
| etc., and so on, and more | complete the set or name its rule |
| and/or | state the combinations or use inclusive `or` with scope made clear |
| soon, shortly, in future | state a date, version, event, or remove the claim |
| under the hood | internally, or name the mechanism |
| out of the box | by default, when a default is defined |
| plumbing, glue, magic | name the mechanism |
| gotcha | limitation or known issue |
| nuke, blow away | delete or remove, according to scope |
| spin up, stand up | start, create, or deploy, according to the lifecycle |
| reach out | contact or ask |
| deep dive | detailed explanation |
| low-hanging fruit | state the change and cost |
| sanity check | validation or verification, according to purpose |
| dummy value | placeholder or sample |
| master/slave | the authoritative project relationship, such as primary/replica or leader/follower |
| whitelist/blacklist | the authoritative project terms, such as allowlist/denylist |
| crazy, insane, dumb | state the property |
| grandfathered | state the exact exemption and its effective scope |
| obviously, clearly, of course | delete or provide evidence |

Do not convert ordinary English into a BCP 14 obligation. `MUST`, `SHOULD`, `NOT RECOMMENDED`, and related keywords apply only under a declared obligation convention. In a procedure, use an imperative when it expresses the intended instruction.

## Part-of-Speech Defaults

| Term | Approved role | Avoid |
| --- | --- | --- |
| `request` | noun | Use as a verb only when an authoritative API or project usage requires it. |
| `impact` | noun | Prefer a precise verb such as increases, delays, or removes. |
| `architect` | noun | Use `design` as the verb. |
| `default` | noun, adjective, and intransitive verb in `defaults to` | Do not write `default the value`; write `set the default value`. |
| `error` | noun | Write `returned an error`, not `errored`, unless the ecosystem defines the verb. |
| `action` | noun | Use a precise verb such as process. |
| `surface` | noun | Use `display`, `return`, or `result in` as the verb. |
| `onboard` | verb | Use `onboarding` for the process. |
| `ask`, `spend`, `learning` | verbs | Use request, cost, or what was learned as the noun. |

## Procedural Verbs

Prefer direct verbs such as `add`, `apply`, `build`, `check`, `close`, `configure`, `connect`, `copy`, `create`, `delete`, `deploy`, `disable`, `download`, `edit`, `enable`, `enter`, `export`, `import`, `install`, `merge`, `move`, `open`, `press`, `read`, `rename`, `replace`, `restart`, `run`, `save`, `select`, `send`, `set`, `start`, `stop`, `uninstall`, `update`, `upgrade`, `verify`, `wait`, and `write`.

Use `select` for a device-neutral UI choice. Use `enter` for text input. Use `run` for a command. Use `verify` for a reader check and state the expected observation.

## Project Glossary Contract

Record each term with these fields:

```yaml
term: idempotency key
definition: A client value that makes a repeated request return the original result.
part_of_speech: noun
domain: payments-api
source: contracts/payments.yaml
approved_variants: []
rejected_alternatives: [dedup token, request id]
replacement: null
status: approved
owner: platform-team
since: v3.1
```

`status` is `proposed`, `approved`, or `deprecated`. A deprecated term names `replacement`. Keep old entries so historical text remains interpretable. Coordinate accepted terminology changes in the same reviewed change set or release. Classify the consumer effect as editorial, search or discoverability, user-interface terminology, API or schema, or migration-requiring.

A Vale vocabulary or similar lexical checker can enforce approved spelling, casing, and rejected alternatives. It cannot prove a definition, word sense, part of speech in context, technical correctness, or publication approval.

## Exemption and Redaction Precedence

Apply these exceptions in order:

1. Authorized security, privacy, legal, or regulatory redaction can replace sensitive text.
2. External quotations remain verbatim unless the task requests quotation editing.
3. Tool output and logs remain verbatim, with authorized secret redaction.
4. Code spans, identifiers, paths, commands, flags, environment variables, methods, status codes, versions, and literal values remain verbatim.
5. Product, company, protocol, and standard names remain verbatim.
6. Surrounding prose follows the selected SEE profile.

An exemption from rewriting does not make the exempt content technically correct or safe to publish.
