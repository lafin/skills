---
name: hosted-agents
description: "This skill should be used when designing hosted or background agent infrastructure: sandboxed execution, remote coding environments, warm pools, session persistence, multiplayer collaboration, self-spawning agents, or Modal-style sandboxes."
license: MIT
metadata:
  upstream: "muratcankoylan/Agent-Skills-for-Context-Engineering"
  upstream_commit: "c578e85e40fe2bda7c1fec91ff64cf5285434934"
  upstream_path: "skills/hosted-agents"
  adaptation: modified
  license_notice: LICENSE-context-engineering
---

# Hosted Agent Infrastructure

Hosted agents run in remote sandboxed environments rather than on local machines. They can provide elastic concurrency within provider and account limits, consistent execution environments, and multiplayer collaboration. Move infrastructure setup outside the user-visible request path where the workload permits.

## When to Activate

Activate this skill when:
- Building background coding agents that run independently of user devices
- Designing sandboxed execution environments for agent workloads
- Implementing multiplayer agent sessions with shared state
- Creating multi-client agent interfaces (Slack, Web, Chrome extensions)
- Scaling agent infrastructure beyond local machine constraints
- Building systems where agents spawn sub-agents for parallel work

Do not activate this skill for adjacent work owned by other skills:
- Designing the autonomous research loop, novelty gates, rollback policy, or merge boundaries: `harness-engineering`.
- Choosing supervisor, swarm, or handoff topology without hosted infrastructure concerns: `multi-agent-patterns`.
- Designing the tools used by a hosted agent, such as spawn/status tools or PR tools: `tool-design`.
- Managing file-backed state inside a session rather than the hosted runtime itself: `filesystem-context`.

## Core Concepts

Move agent execution to remote sandboxed environments when local resource contention, environment inconsistency, or single-machine constraints block the workload. Isolated sandboxes can provide reproducible environments and concurrent sessions within explicit quotas.

Design the architecture in three layers because each layer scales independently. Build sandbox infrastructure for isolated execution, an API layer for state management and client coordination, and client interfaces for user interaction across platforms. Keep these layers cleanly separated so sandbox changes do not ripple into clients.

## Detailed Topics

### Sandbox Infrastructure

**The Core Challenge**
Measure sandbox spin-up latency against the product's user-experience target. Development environments can require repository cloning, dependency installation, and build steps; perform reusable setup before the user submits a prompt when the workload permits.

**Image Registry Pattern**
Pre-build environment images on a cadence derived from the allowed code and dependency staleness. Include in each image:
- Cloned repository at a known commit
- All runtime dependencies installed
- Initial setup and build commands completed
- Precomputed caches where safe

When starting a session, use the most recent valid image and synchronize the repository before any write. Measure image age and synchronization time.

**Snapshot and Restore**
Take filesystem snapshots at key points to enable instant restoration for follow-up prompts without re-running setup:
- After initial image build (base snapshot)
- When agent finishes making changes (session snapshot)
- Before sandbox exit for potential follow-up

**Git Configuration for Background Agents**
Configure git identity explicitly in every sandbox because background agents are not tied to a specific user during image builds:
- Generate GitHub app installation tokens for repository access during clone
- Set git config `user.name` and `user.email` when committing and pushing changes
- Use the prompting user's identity for commits, not the app identity

**Warm Pool Strategy**
Maintain a pool of pre-warmed sandboxes for high-volume repositories because cold starts are the primary source of user frustration:
- Keep sandboxes ready before users start sessions
- Expire and recreate pool entries as new image builds complete
- Start warming a sandbox as soon as a user begins typing (predictive warm-up)

### Agent Framework Selection

**Server-First Architecture**
Structure the agent framework as a server first, with TUI and desktop apps as thin clients, because this prevents duplicating agent logic across surfaces:
- Multiple custom clients share one agent backend
- Consistent behavior across all interaction surfaces
- Plugin systems extend functionality without client changes
- Event-driven architectures deliver real-time updates to any connected client

**Code as Source of Truth**
Select frameworks where the agent can read its own source code to understand behavior. Prioritize this because having code as source of truth prevents the agent from hallucinating about its own capabilities -- an underrated failure mode in AI development.

**Plugin System Requirements**
Require a plugin system that supports runtime interception because this enables safety controls and observability without modifying core agent logic:
- Listen to tool execution events (e.g., `tool.execute.before`)
- Block or modify tool calls conditionally
- Inject context or state at runtime

### Speed Optimizations

**Predictive Warm-Up**
Start warming the sandbox when a user begins composing a prompt, not after submission. Measure whether the available interval covers the setup work:
- Clone latest changes while the user composes the prompt
- Run reusable setup before submission
- Fall back to a visible startup state when warm-up does not finish

**Parallel File Reading**
Allow the agent to start reading files before the latest base-branch sync completes only when the product can tolerate stale reads:
- Let independent research begin without waiting for git sync
- Block file edits until synchronization completes
- Revalidate any read result that affects a write

**Maximize Build-Time Work**
Move everything possible to the image build step because build-time duration is invisible to users:
- Full dependency installation
- Database schema setup
- Initial app and test suite runs (populates caches)

### Self-Spawning Agents

**Agent-Spawned Sessions**
Build tools that allow agents to spawn new sessions because frontier models are capable of decomposing work and coordinating sub-tasks:
- Research tasks across different repositories
- Parallel subtask execution for large changes
- Multiple smaller PRs from one major task

Expose three primitives: start a new session with specified parameters, read status of any session (check-in capability), and continue main work while sub-sessions run in parallel.

**Prompt Engineering for Self-Spawning**
Engineer prompts that guide when agents should spawn sub-sessions rather than doing work inline:
- Research tasks that require cross-repository exploration
- Breaking monolithic changes into smaller PRs
- Parallel exploration of different approaches

### API Layer

**Per-Session State Isolation**
Isolate state per session (SQLite per session works well) because cross-session interference is a subtle and hard-to-debug failure mode:
- Dedicated database per session
- No session can impact another's performance
- Architecture handles hundreds of concurrent sessions

**Real-Time Streaming**
Stream all agent work in real-time because high-frequency feedback is critical for user trust:
- Token streaming from model providers
- Tool execution status updates
- File change notifications

Use WebSocket connections with hibernation APIs to reduce compute costs during idle periods while maintaining open connections.

**Synchronization Across Clients**
Build a single state system that synchronizes across all clients (chat interfaces, Slack bots, Chrome extensions, web interfaces, VS Code instances) because users switch surfaces frequently and expect continuity. All changes sync to the session state, enabling seamless client switching.

### Multiplayer Support

**Why Multiplayer Matters**
Design for multiplayer at the data-model boundary when collaborative sessions are a product requirement. Shared synchronization can lower the marginal implementation cost, but authorization, attribution, and conflict handling remain explicit work:
- Teaching non-engineers to use AI effectively
- Live QA sessions with multiple team members
- Real-time PR review with immediate changes
- Collaborative debugging sessions

**Implementation Requirements**
Build the data model so sessions are not tied to single authors because multiplayer fails silently if authorship is hardcoded:
- Pass authorship info to each prompt
- Attribute code changes to the prompting user
- Share session links for instant collaboration

### Authentication and Authorization

**User-Based Commits**
Use GitHub authentication to open PRs on behalf of the user (not the app) because this preserves the audit trail and prevents users from approving their own AI-generated changes:
- Obtain user tokens for PR creation
- PRs appear as authored by the human, not the bot

**Sandbox-to-API Flow**
Follow this sequence because it keeps sandbox permissions minimal while letting the API handle sensitive operations:
1. Sandbox pushes changes (updating git user config)
2. Sandbox sends event to API with branch name and session ID
3. API uses user's GitHub token to create PR
4. GitHub webhooks notify API of PR events

### Client Implementations

**Slack Integration**
Prioritize Slack as the first distribution channel for internal adoption because it creates a virality loop as team members see others using it:
- No syntax required, natural chat interface
- Build a classifier (fast model with repo descriptions) to determine which repository to work in
- Include hints for common repositories; allow "unknown" for ambiguous cases

**Web Interface**
Build a web interface with these features because it serves as the primary power-user surface:
- Real-time streaming of agent work on desktop and mobile
- Hosted VS Code instance running inside sandbox
- Streamed desktop view for visual verification
- Before/after screenshots for PRs
- Statistics page: sessions resulting in merged PRs (primary metric), usage over time, live "humans prompting" count

**Chrome Extension**
Build a Chrome extension for non-engineering users because DOM and React internals extraction gives higher precision than raw screenshots at lower token cost:
- Sidebar chat interface with screenshot tool
- Extract DOM/React internals instead of raw images
- Distribute via managed device policy (bypasses Chrome Web Store)

## Practical Guidance

### Hosted Agent Design Checklist

Before building the system, decide these infrastructure properties explicitly:

1. **Sandbox lifecycle**: how sessions start, snapshot, restore, time out, and terminate.
2. **Image and warm-pool policy**: how often images rebuild, which caches are precomputed, and when warm sandboxes expire.
3. **Read/write synchronization**: whether agents may read before repository sync completes, and which events unblock writes.
4. **Per-session state isolation**: what storage belongs to one session, what is shared, and how cross-session interference is prevented.
5. **Auth and commit identity**: which operations use app tokens, which use user tokens, and how commits are attributed.
6. **Output extraction**: how branches, PRs, files, logs, screenshots, and session summaries leave the sandbox.
7. **Budget and teardown**: maximum runtime, cost ceilings, idle policy, and forced cleanup behavior.

### Follow-Up Message Handling

Choose between queueing and inserting follow-up messages sent during execution. Prefer queueing because it is simpler to manage and lets users send thoughts on next steps while the agent works. Build a mechanism to stop the agent mid-execution when needed, because without it users feel trapped.

### Metrics That Matter

Track these metrics because they indicate real value rather than vanity usage:
- Sessions resulting in merged PRs (primary success metric)
- Time from session start to first model response
- PR approval rate and revision count
- Agent-written code percentage across repositories

### Adoption Strategy

Drive internal adoption through visibility rather than mandates because forced usage breeds resentment:
- Work in public spaces (Slack channels) for visibility
- Let the product create virality loops
- Do not force usage over existing tools
- Build to people's needs, not hypothetical requirements

## Examples

**Example 1: Background coding session lifecycle**

```text
user prompt
-> API allocates warm sandbox from current image
-> sandbox syncs latest branch delta
-> reads allowed immediately, writes blocked until sync completes
-> agent edits and tests inside isolated workspace
-> sandbox snapshots final filesystem
-> branch is pushed
-> API creates PR using user token
-> session summary, logs, and PR URL are returned to clients
```

This sequence keeps setup work outside the user-visible path while preserving auditability and user ownership of code changes.

**Example 2: Boundary decision**

If the task is "make the agent loop run for days with locked rubrics and PR approval," use `harness-engineering`. If the task is "run that loop in remote sandboxes with warm pools, session snapshots, streaming clients, and user-authored PRs," use this skill.

## Guidelines

1. Rebuild environment images on a cadence derived from the dependency and code staleness target
2. Start warming sandboxes when users begin typing, not when they submit
3. Allow file reads before git sync completes; block only writes
4. Structure agent framework as server-first with clients as thin wrappers
5. Isolate state per session to prevent cross-session interference
6. Attribute commits to the user who prompted, not the app
7. Track merged PRs as primary success metric
8. Reuse the session synchronization architecture for multiplayer only after authorization, attribution, and conflict behavior are defined

## Gotchas

1. **Cold start latency**: Measure sandbox spin-up time and the user's tolerated wait. Use warm pools or predictive warm-up when cold starts exceed that target.
2. **Image staleness**: Infrequent image rebuilds can leave agents with outdated dependencies or code. Derive the rebuild cadence from the staleness target, monitor image age, and alert on failed builds.
3. **Sandbox cost runaway**: Long-running agents without timeout or budget caps accumulate unexpected costs. Set workload-specific timeout and per-session cost ceilings.
4. **Auth token expiration mid-session**: Long tasks fail when GitHub tokens expire partway through. Implement token refresh logic and check token validity before sensitive operations like PR creation.
5. **Git config in sandboxes**: Missing `user.name` or `user.email` causes commit failures in background agents. Always set git identity explicitly during sandbox configuration, never assume it carries over from the image.
6. **State loss on sandbox recycle**: Agents lose completed work if the sandbox is recycled or times out before results are extracted. Always snapshot before termination and extract artifacts (branches, PRs, files) before letting the sandbox die.
7. **Oversubscribing warm pools**: Maintaining too many warm sandboxes wastes money during low-traffic periods. Scale pool size based on traffic patterns and time-of-day; use autoscaling rather than fixed pool sizes.
8. **Missing output extraction**: Agents complete work inside the sandbox but results never get pulled out to the user. Build explicit extraction steps (push branch, create PR, return file contents) into the session teardown flow.

## Integration

This skill owns hosted runtime infrastructure. Adjacent skills own the control system, topology, and tool contracts:

- `harness-engineering`: governance, locked evaluators, rollback, novelty gates, and human approval boundaries around autonomous work.
- `multi-agent-patterns`: self-spawning and supervisor patterns once hosted infrastructure exists.
- `tool-design`: spawn, status, teardown, and PR tools exposed to agents.
- `context-optimization`: managing context across distributed hosted sessions.
- `filesystem-context`: using the sandbox filesystem for durable session state and artifacts.

## References

Internal reference:
- [Infrastructure Patterns](skill://hosted-agents/references/infrastructure-patterns.md) - Read when: implementing sandbox lifecycle, image builds, or warm pool logic for the first time

Runnable script:

### `sandbox_manager.py`

- **Status:** Template.
- **Boundary:** Demonstrates hosted-sandbox lifecycle structure with placeholder identities and credentials. Provider I/O, snapshots, image creation, restore, timeout enforcement, and token-backed authorization are not implemented, so it does not create a real sandbox or establish production isolation, persistence, authorization, or availability.
- **Replacement points:** Implement sandbox I/O and snapshots, image creation and restore, provider lifecycle and timeout operations, synchronization signaling, and the GitHub token provider for the selected infrastructure before production use. A caller that writes through `AgentSession` must call `mark_sync_complete()` after repository synchronization or replace that manual signal with provider state.
- **Run:** From the repository root, run `python hosted-agents/scripts/sandbox_manager.py`. The bundled demonstration accepts no arguments or real credentials and uses placeholder repositories and tokens.
- **Output:** Writes human-readable simulated image/session lifecycle messages and a placeholder snapshot value to standard output. After replacement, library methods must return the `Sandbox`, `RepositoryImage`, session, command-result, file-content, and snapshot values documented by their type annotations.
- **Failure:** The demo exits non-zero on an uncaught Python or asynchronous lifecycle error; `start_session` can also raise `ValueError` when no image exists. The background build loop instead prints provider failures and continues. Repair the named provider replacement point, ensure an image is available, and connect repository synchronization to `mark_sync_complete()` before retrying queued writes.

Related skills in this collection:
- multi-agent-patterns - Read when: designing self-spawning or supervisor coordination patterns
- tool-design - Read when: building tools for agent session management or status checking
- context-optimization - Read when: context windows fill up across distributed agent sessions

External resources:
- [Ramp](https://builders.ramp.com/post/why-we-built-our-background-agent) - Read when: evaluating whether to build vs. buy background agent infrastructure
- [Modal Sandboxes](https://modal.com/docs/guide/sandbox) - Read when: choosing a cloud sandbox provider or comparing isolation models
- [Cloudflare Durable Objects](https://developers.cloudflare.com/durable-objects/) - Read when: designing per-session state management with WebSocket hibernation
- [OpenCode](https://github.com/sst/opencode) - Read when: selecting a server-first agent framework or studying plugin architectures

---

## Skill Metadata

**Created**: 2026-01-12
**Last Updated**: 2026-05-15
**Author**: Agent Skills for Context Engineering Contributors
**Version**: 1.2.0
