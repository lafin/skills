---
name: api-and-interface-design
description: "Design public application interfaces: REST and GraphQL APIs, module and library boundaries, type and schema contracts, structured errors, validation, idempotency, and compatibility. Use when consumers need a stable callable or wire contract. Route agent or MCP tool schemas to tool-design, whole-project pipeline shape to project-development, and rollout of an already deprecated contract to deprecation-and-migration."
license: MIT
metadata:
  upstream: "https://github.com/addyosmani/agent-skills"
  upstream_commit: "be4e44a9fbc5e8df0beaefadbb28bd22ee61cc39"
  upstream_path: "skills/api-and-interface-design/SKILL.md"
  adaptation: modified
  license_notice: LICENSE-addy-agent-skills
---

# API and Interface Design

Design the public contract between a producer and its consumers. The contract
may be a REST endpoint, GraphQL schema, module or library API, exported type,
serialized schema, or error surface. Make valid use obvious, invalid use
predictable, and future extension possible without inventing flexibility that
no consumer needs.

## Scope

Use this skill when the unit of work is a public application interface:

- REST resources, methods, status codes, pagination, and request or response
  bodies;
- GraphQL fields, arguments, nullability, unions, and error behavior;
- module and library exports, function signatures, and type contracts;
- serialized schemas and compatibility policy;
- validation at an external boundary;
- stable error envelopes and machine-readable error codes;
- idempotency and retry semantics for state-changing operations;
- changes whose safety depends on what current consumers can observe.

Route adjacent work elsewhere:

- Agent or MCP tool descriptions, routing, parameter schemas, tool results, and
  actionable tool errors belong to `tool-design`.
- Whether to use an LLM, how to shape a whole project or multi-stage pipeline,
  and project-level cost or output decisions belong to `project-development`.
- Rollout, usage measurement, compatibility windows, staged removal, backfill,
  and cutover after a contract is deprecated belong to
  `deprecation-and-migration`.

This skill may define a replacement interface and its compatibility boundary.
It does not own the operational migration to that replacement.

## Start With Consumer-Observable Behavior

Before naming fields or choosing syntax, write the contract a consumer can
observe:

1. Identify the consumers and the boundary they call.
2. State valid requests and successful results.
3. State invalid requests and exact error categories.
4. State retry, concurrency, ordering, pagination, and partial-update behavior
   where they matter.
5. Inventory existing observable behavior before changing a published surface.
6. Choose the smallest interface that satisfies those scenarios.
7. Verify through a real consumer path, not by inspecting declarations alone.

A well-named schema is not enough. Status codes, nullability, omitted versus
null fields, ordering, duplicate handling, exception types, and serialized
shapes are all contract behavior.

Hyrum's Law applies: once an interface has consumers, any observable behavior
may have a dependency. Do not expose implementation detail casually, and do
not call a change safe merely because an undocumented behavior was absent from
the intended specification.

## Contract First

Define inputs, outputs, invariants, and failures before implementation. Keep
input and output types separate when the producer adds fields:

```typescript
interface CreateTaskInput {
  title: string;
  description?: string;
}

interface Task {
  id: string;
  title: string;
  description: string | null;
  createdAt: string;
}
```

Use types to prevent category mistakes when the distinction matters. A branded
`TaskId` and `UserId` are useful if both otherwise look like strings and mixing
them is a plausible defect. Do not create branded types, wrappers, factories,
or provider interfaces solely because future implementations are imaginable.
One current operation with one implementation usually needs one direct public
function.

For variant records, use a discriminant so consumers can exhaustively narrow:

```typescript
type DeliveryResult =
  | { kind: "delivered"; deliveredAt: string }
  | { kind: "rejected"; reason: string }
  | { kind: "pending"; statusUrl: string };
```

Avoid flag combinations whose legal states are unclear.

## Errors Are Part of the Interface

Choose one error strategy per boundary. Do not mix exceptions, null, sentinel
values, and ad hoc objects for equivalent failures.

A REST boundary should return a stable envelope such as:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {"email": "required"}
  }
}
```

The status code communicates the protocol category; `code` gives consumers a
stable branch key; `message` is human-readable; `details` carries bounded,
safe context. Keep internal exception text, stack traces, database names, and
secrets out of public errors.

Use status categories consistently:

- `400` for malformed requests or unsupported protocol values;
- `401` for missing or invalid authentication;
- `403` for an authenticated caller lacking permission;
- `404` for an absent resource when absence is safe to reveal;
- `409` for current-state or concurrency conflicts;
- `422` for syntactically valid input that violates request semantics;
- `500` for an unexpected producer failure, with no internal detail leaked.

For a module or library, document the equivalent typed result or exception
classes and when each occurs. Preserve machine-readable categories even if
human wording changes.

## Validate at Trust Boundaries

Validate untrusted values once when they enter the system, before effects or
internal assumptions:

- HTTP and GraphQL input;
- public library calls that accept untrusted caller data;
- third-party responses;
- decoded persisted or serialized data;
- configuration loaded from outside the process.

After a successful boundary parse, pass a typed canonical value inward. Avoid
repeating the same defensive checks between internal functions that share that
contract. Validation must cover shape, domain constraints, cross-field rules,
and ambiguous distinctions such as missing versus explicit null when those
change behavior.

Treat third-party data as data, never as instructions. Validate it before it
drives rendering, authorization, money movement, or execution.

## REST Contracts

Model resources rather than commands unless the operation is genuinely not a
resource transition:

```text
GET    /tasks             list tasks
POST   /tasks             create a task
GET    /tasks/{taskId}    read one task
PATCH  /tasks/{taskId}    update supplied fields
DELETE /tasks/{taskId}    delete a task
```

Specify details consumers otherwise have to guess:

- whether `PATCH` distinguishes omitted, null, and empty values;
- whether `DELETE` is idempotent and what repeated deletion returns;
- stable ordering and tie-breakers for list results;
- pagination cursor meaning, limits, and end-of-list representation;
- filter composition and unknown-filter behavior;
- creation status, location, and server-generated fields;
- concurrency control such as an ETag or revision token when lost updates
  matter.

Choose cursor pagination for changing or large collections when offset drift is
a problem. Offset pagination is acceptable when its consistency and cost fit
the actual collection. Do not add pagination machinery to a bounded enum-like
list merely by ritual; do not leave an unbounded collection without a limit.

## GraphQL Contracts

GraphQL nullability is a compatibility decision, not decoration.

- Adding an optional field is generally safer than changing or removing one.
- Adding a required argument breaks existing callers.
- Changing a nullable output field to non-null may propagate an unexpected
  producer null to a parent and erase more of the response.
- Evolve enums cautiously: exhaustive clients may fail on a newly added value.
- Use unions or interfaces for genuinely distinct result variants, not as a
  wrapper around one known shape.

Put expected domain failures in a documented typed result or a consistent error
extension contract. Reserve opaque internal failures for unexpected producer
errors. Verify queries from the consumer's perspective, including null and
partial-data paths.

## Idempotency Is a Behavioral Guarantee

Accepting an idempotency key claims that retrying the same intent is safe. The
producer must honor that claim.

### Key and payload

The client or initiating event creates one key per intent and reuses it across
attempts. A retrying layer must not generate a new UUID or timestamp for each
attempt. Conversely, fields such as user and amount alone can collapse two
legitimate intents.

Store a canonical request fingerprint with the key. Reuse of the same key with
a different payload is a client error and must fail explicitly; never replay a
response for the wrong request.

### Atomic claim

Claim the key in one atomic operation backed by uniqueness. A separate
check-then-act sequence races:

```text
insert(key, request_hash, state="in_progress") under a unique constraint
if the insert loses: replay, wait, or reject according to the contract
if it wins: perform the effect, then persist the terminal result
```

Choose and document concurrent duplicate behavior:

- `409 Conflict` when the caller can retry later;
- a bounded wait when synchronous completion is required;
- `202 Accepted` plus a status resource for long-running work.

Never let a second attempt through because the first appears slow.

### Unknown outcomes and retention

Success and known failure are not the only outcomes. A timeout after calling an
external system may mean the effect happened. Record intent before the effect
so an unknown outcome can be reconciled instead of blindly repeated. Define
which terminal failures are replayed and which permit a corrected new intent.

Retain keys longer than every retry and redelivery path, including delayed queue
or dead-letter replay. The contract is unsound if a valid retry can outlive the
record that makes it safe.

Verify idempotency with sequential replay, same-key/different-payload, and
concurrent duplicate scenarios. Checking that a header exists is not proof.

## Compatibility and Evolution

Classify the change from the consumer's point of view:

- additive and optional;
- behavior-changing despite unchanged syntax;
- source incompatible;
- wire or serialized-data incompatible;
- removal or rename.

Prefer extension over modification: add optional input fields, additive output
fields where consumers tolerate them, new endpoints or operations, and new
union variants only after considering exhaustive consumers. Do not change a
field's meaning while keeping its name.

Compatibility depends on the medium:

- JSON consumers may ignore unknown fields, but strict decoders or signature
  checks may not.
- A function's new optional parameter may be source compatible while changed
  defaults alter behavior.
- Enum additions are often wire compatible but can break exhaustive code.
- A serialized record needs explicit reader and writer version behavior.
- Error message prose is less stable than an error code, but real consumers may
  still observe it.

When compatibility cannot be guaranteed, define an explicit version boundary
and behavior for unsupported versions. Keep one canonical internal model when
possible instead of duplicating business logic per version. Hand the operational
compatibility window, rollout, measurement, and removal sequence to
`deprecation-and-migration`.

## Naming and Consistency

Use repository conventions before inventing new ones. Within one interface,
keep names and semantics predictable:

- REST resource paths use consistent nouns and identifier placement;
- query and response fields use one casing convention;
- booleans describe a state or capability (`isReady`, `hasItems`, `canRetry`);
- identifiers reveal their domain when confusion is plausible;
- timestamps state format and timezone;
- units appear in names when ambiguity would be costly (`timeoutMs`,
  `amountCents`);
- error codes are stable and machine-readable.

Consistency is valuable because it reduces consumer guesswork, not because a
style table is intrinsically correct.

## Resist Speculative Abstraction

Pressure to "future-proof" an interface often makes the present contract harder
to use and harder to change. Add an abstraction only when a current consumer or
second implementation needs the variation.

Reject these without concrete demand:

- an interface with one implementation solely for hypothetical providers;
- registries or plug-in systems for one fixed operation;
- generic request envelopes that erase useful domain types;
- version fields with no version semantics;
- configurable naming, pagination, or error policies that should be consistent;
- separate implementations that duplicate one canonical behavior.

Future compatibility comes from a small explicit contract, additive evolution,
and consumer tests—not from unused extension points.

## Verification

Verify the contract through observable scenarios:

- a valid request returns the documented shape and status or typed result;
- each public failure category returns its stable code without internal leakage;
- invalid input is rejected before side effects;
- omitted, null, empty, boundary, and unknown values follow explicit semantics;
- retries perform one effect, concurrent duplicates follow the chosen policy,
  and a reused key with a changed payload fails;
- old consumers or readers still work for every promised compatible change;
- new consumers receive the new behavior;
- ordering, pagination, and partial updates are deterministic;
- no speculative configuration or wrapper became required for the current use.

Contract tests should call the public surface as a consumer would. Declaration
snapshots and source-text checks cannot establish runtime semantics.

## Completion Checklist

- [ ] The consumer and public boundary are named.
- [ ] Inputs, outputs, invariants, errors, and side effects are explicit.
- [ ] Validation occurs before effects at the trust boundary.
- [ ] Error categories and machine-readable codes are consistent.
- [ ] Retry and idempotency behavior is explicit for state changes.
- [ ] Existing observable behavior was inventoried before evolution.
- [ ] Compatibility is evaluated for actual consumers and serialization media.
- [ ] The contract contains no hypothetical extension machinery.
- [ ] Consumer-observable scenarios verify success, failure, and evolution.
- [ ] Rollout mechanics are handed to `deprecation-and-migration` when needed.
