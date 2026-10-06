# Infrastructure Patterns for Hosted Agents

This reference provides implementation patterns for building hosted agent infrastructure. Code targets the Modal Python SDK 1.x and Cloudflare Workers; check each provider's current docs before use.

## Sandbox Architecture

### Modal Integration Pattern

Modal sandboxes support filesystem snapshots. A snapshot is an `Image`, so restoring means creating a new sandbox from it. `exec` takes argv, not a shell string.

```python
import modal

MODEL = "provider/model"  # placeholder; set per deployment
# Proxies outside the sandbox hold the GitHub and model credentials and only
# allow pushes to the session branch. Nothing secret enters the sandbox.
GIT_PROXY = "https://git-proxy.example.com"
EGRESS = ["git-proxy.example.com", "llm-proxy.example.com"]

app = modal.App.lookup("coding-agent", create_if_missing=True)
base = (
    modal.Image.debian_slim()
    .apt_install("git", "nodejs", "npm")
    .run_commands("npm install -g opencode-ai")
)


def run(sb: modal.Sandbox, *argv: str, workdir: str = "/workspace") -> str:
    p = sb.exec(*argv, workdir=workdir)
    if p.wait() != 0:
        raise RuntimeError(f"{argv[0]} failed: {p.stderr.read()}")
    return p.stdout.read()


def build_repo_image(repo: str) -> modal.Image:
    """Clone, install, build, snapshot. Run on the rebuild cadence."""
    sb = modal.Sandbox.create(app=app, image=base, timeout=30 * 60)
    try:
        run(sb, "git", "clone", f"{GIT_PROXY}/{repo}.git", "/workspace", workdir="/")
        run(sb, "npm", "install")
        run(sb, "npm", "run", "build")
        return sb.snapshot_filesystem()  # expires after 30 days by default
    finally:
        sb.terminate()


def start_session(repo_image: modal.Image, snapshot: modal.Image | None,
                  user_name: str, user_email: str) -> modal.Sandbox:
    """A follow-up restores its session snapshot; a new session uses the repo image."""
    sb = modal.Sandbox.create(
        app=app,
        image=snapshot or repo_image,
        timeout=2 * 60 * 60,  # default is 5 minutes; maximum is 24 hours
        outbound_domain_allowlist=EGRESS,
    )
    try:
        # argv, not a shell string: a display name cannot inject commands
        run(sb, "git", "config", "user.name", user_name)
        run(sb, "git", "config", "user.email", user_email)
    except modal.exception.NotFoundError:
        sb.terminate()
        if snapshot is None:
            raise
        # Expired snapshot: start fresh, then check out the pushed session branch
        return start_session(repo_image, None, user_name, user_email)
    return sb


def run_prompt(sb: modal.Sandbox, prompt: str) -> modal.Image:
    """Run the agent, then snapshot so a follow-up can resume this work."""
    run(sb, "opencode", "run", "--model", MODEL, prompt)
    return sb.snapshot_filesystem()
```

### Image Build Pipeline

Call `build_repo_image` from a scheduled job on the cadence derived from the staleness target. Store each image's `object_id`, commit SHA, and build time, and expire warm sandboxes built from an older image.

### Warm Pool Management

Maintain pre-warmed sandboxes for instant session starts:

```python
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import modal

@dataclass
class WarmSandbox:
    sandbox: modal.Sandbox
    repo: str
    created_at: datetime
    image_version: str
    is_claimed: bool = False

class WarmPoolManager:
    def __init__(self, app: modal.App, images: dict[str, modal.Image],
                 target_pool_size: int = 3):
        self.app = app
        self.images = images  # repo -> latest image from build_repo_image
        self.target_size = target_pool_size
        self.pools = defaultdict(list)  # repo -> [WarmSandbox]
        self.max_age = timedelta(minutes=25)  # Expire before next image build
    
    def get_warm_sandbox(self, repo: str) -> WarmSandbox | None:
        """Get a pre-warmed sandbox if available."""
        pool = self.pools[repo]
        
        for sandbox in pool:
            if not sandbox.is_claimed and self._is_valid(sandbox):
                sandbox.is_claimed = True
                return sandbox
        
        return None
    
    def _is_valid(self, sandbox: WarmSandbox) -> bool:
        """Check if sandbox is still valid."""
        age = datetime.now(timezone.utc) - sandbox.created_at
        current_image = self.images[sandbox.repo].object_id

        return (
            age < self.max_age and
            sandbox.image_version == current_image
        )
    
    def maintain_pool(self, repo: str):
        """Ensure pool has target number of warm sandboxes."""
        # Remove expired sandboxes
        self.pools[repo] = [s for s in self.pools[repo] if self._is_valid(s)]
        
        # Add new sandboxes to reach target
        current_count = len([s for s in self.pools[repo] if not s.is_claimed])
        needed = self.target_size - current_count
        
        for _ in range(needed):
            sandbox = self._create_warm_sandbox(repo)
            self.pools[repo].append(sandbox)
    
    def _create_warm_sandbox(self, repo: str) -> WarmSandbox:
        """Create a new warm sandbox from latest image."""
        image = self.images[repo]
        sandbox = modal.Sandbox.create(app=self.app, image=image, timeout=30 * 60)

        # Sync to latest; the session blocks writes until this finishes
        sandbox.exec("git", "pull", "--ff-only", workdir="/workspace")

        return WarmSandbox(
            sandbox=sandbox,
            repo=repo,
            created_at=datetime.now(timezone.utc),
            image_version=image.object_id
        )
```

## API Layer Patterns

### Cloudflare Durable Objects for Session State

Each session gets its own Durable Object with isolated SQLite. Accept WebSockets with `ctx.acceptWebSocket()` so the object can hibernate between messages; hibernation discards in-memory fields, so read connections from `ctx.getWebSockets()` and keep state in SQLite ([WebSocket hibernation](https://developers.cloudflare.com/durable-objects/best-practices/websockets/), [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/)).

```typescript
import { DurableObject } from "cloudflare:workers";

interface Env {
  SANDBOX_QUEUE: Queue; // consumer starts or resumes the session's sandbox
}

export class SessionDO extends DurableObject<Env> {
  private sql: SqlStorage;

  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.initializeSchema();
  }

  private initializeSchema() {
    this.sql.exec(`
      CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        author_id TEXT,
        author_name TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      );
      
      CREATE TABLE IF NOT EXISTS artifacts (
        id INTEGER PRIMARY KEY,
        type TEXT NOT NULL,
        path TEXT,
        content TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      );
      
      CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        type TEXT NOT NULL,
        data TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      );
    `);
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (request.headers.get("Upgrade") === "websocket") {
      const [client, server] = Object.values(new WebSocketPair());
      this.ctx.acceptWebSocket(server); // unlike server.accept(), allows hibernation
      return new Response(null, { status: 101, webSocket: client });
    }

    switch (url.pathname) {
      case "/message":
        return this.handleMessage(request);
      case "/event": // sandbox posts tool and file events here
        return this.handleEvent(request);
      default:
        return new Response("Not found", { status: 404 });
    }
  }

  async webSocketClose(ws: WebSocket, code: number, reason: string) {
    ws.close(code, reason);
  }

  private broadcast(message: object) {
    const data = JSON.stringify(message);
    for (const ws of this.ctx.getWebSockets()) {
      ws.send(data);
    }
  }

  async handleMessage(request: Request): Promise<Response> {
    const { content, author } = await request.json();

    // Bindings are spread arguments, not an array
    this.sql.exec(
      `INSERT INTO messages (role, content, author_id, author_name) VALUES (?, ?, ?, ?)`,
      "user", content, author.id, author.name
    );

    this.broadcast({ type: "message", role: "user", content, author });

    // Hand off to the sandbox worker; results arrive later via /event
    await this.env.SANDBOX_QUEUE.send({ sessionId: this.ctx.id.toString(), content, author });

    return Response.json({ queued: true }, { status: 202 });
  }

  async handleEvent(request: Request): Promise<Response> {
    const { type, data } = await request.json<{ type: string; data: unknown }>();
    this.sql.exec(`INSERT INTO events (type, data) VALUES (?, ?)`, type, JSON.stringify(data));
    this.broadcast({ type, data });
    return new Response(null, { status: 204 });
  }
}
```

### Real-Time Event Streaming

The agent process in the sandbox posts each tool, file, and token event to the session's `/event` endpoint, authenticated with a session-scoped credential held by the proxy. The Durable Object stores the event and broadcasts it to every connected client, so a client that reconnects after hibernation can replay from the `events` table.

## Client Integration Patterns

### Slack Bot with Repository Classification

Async handlers need `AsyncApp` ([Bolt for Python](https://docs.slack.dev/tools/bolt-python/)). `start_session` and `format_result_blocks` are the application's own session API and Block Kit formatter.

```python
import asyncio
import json
import os

from openai import AsyncOpenAI
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])
llm = AsyncOpenAI()  # any OpenAI-compatible endpoint
CLASSIFIER_MODEL = os.environ["CLASSIFIER_MODEL"]  # a fast, cheap model

# Repository descriptions for classification
REPO_DESCRIPTIONS = [
    {
        "name": "frontend-monorepo",
        "description": "React frontend application with dashboard, user portal, and admin interfaces",
        "hints": ["dashboard", "UI", "component", "page", "frontend"]
    },
    {
        "name": "backend-services",
        "description": "Node.js API services including auth, payments, and core business logic",
        "hints": ["API", "endpoint", "service", "backend", "database"]
    },
    {
        "name": "mobile-app",
        "description": "React Native mobile application for iOS and Android",
        "hints": ["mobile", "app", "iOS", "Android", "native"]
    }
]

async def classify_repository(message: str, channel: str, thread: list[str]) -> str:
    """Use fast model to classify which repo the message refers to."""
    prompt = f"""Classify which repository this message is about.

Message: {message}
Channel: #{channel}
Thread context: {' | '.join(thread[-3:])}

Repositories:
{json.dumps(REPO_DESCRIPTIONS, indent=2)}

Return ONLY the repository name, or "unknown" if unclear."""

    response = await llm.chat.completions.create(
        model=CLASSIFIER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50
    )
    
    return response.choices[0].message.content.strip()

@app.event("app_mention")
async def handle_mention(event, say, client):
    """Handle @mentions of the bot."""
    channel = event["channel"]
    message = event["text"]
    thread_ts = event.get("thread_ts", event["ts"])
    
    # Get thread context if in a thread
    thread_messages = []
    if "thread_ts" in event:
        result = await client.conversations_replies(
            channel=channel,
            ts=thread_ts
        )
        thread_messages = [m["text"] for m in result["messages"]]
    
    # Get channel info for context
    channel_info = await client.conversations_info(channel=channel)
    channel_name = channel_info["channel"]["name"]
    
    # Classify repository
    repo = await classify_repository(message, channel_name, thread_messages)
    
    if repo == "unknown":
        await say(
            text="I'm not sure which repository you're referring to. Could you specify?",
            thread_ts=thread_ts
        )
        return
    
    # Start session and process
    session = await start_session(repo, event["user"])
    
    await say(
        text=f":robot_face: Starting work in `{repo}`...",
        thread_ts=thread_ts
    )
    
    result = await session.process(message)
    
    # Post result with Block Kit formatting
    await say(
        blocks=format_result_blocks(result),
        thread_ts=thread_ts
    )

if __name__ == "__main__":
    asyncio.run(AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start_async())
```

### Chrome Extension DOM Extraction

Extract DOM structure instead of sending screenshots:

```typescript
// content-script.ts
interface ElementInfo {
  tag: string;
  classes: string[];
  id?: string;
  text?: string;
  rect: DOMRect;
  reactComponent?: string;
}

function extractDOMInfo(element: Element): ElementInfo {
  // Get React component name if available
  let reactComponent: string | undefined;
  const fiberKey = Object.keys(element).find((key) =>
    key.startsWith("__reactFiber")
  );
  if (fiberKey) {
    const fiber = (element as any)[fiberKey];
    reactComponent = fiber?.type?.name || fiber?.type?.displayName;
  }

  return {
    tag: element.tagName.toLowerCase(),
    classes: Array.from(element.classList),
    id: element.id || undefined,
    text: element.textContent?.slice(0, 100),
    rect: element.getBoundingClientRect(),
    reactComponent,
  };
}

function extractSelectedArea(selection: DOMRect): ElementInfo[] {
  const elements: ElementInfo[] = [];

  // Find all elements within selection bounds
  document.querySelectorAll("*").forEach((el) => {
    const rect = el.getBoundingClientRect();
    if (
      rect.top >= selection.top &&
      rect.left >= selection.left &&
      rect.bottom <= selection.bottom &&
      rect.right <= selection.right
    ) {
      elements.push(extractDOMInfo(el));
    }
  });

  return elements;
}

// Message handler for sidebar
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "EXTRACT_SELECTION") {
    const elements = extractSelectedArea(request.selection);
    sendResponse({ elements });
  }
});
```

## Multiplayer Implementation

### Authorship Tracking

Track which user made each change:

```python
@dataclass
class PromptContext:
    content: str
    author: Author
    session_id: str
    timestamp: datetime

@dataclass
class Author:
    id: str
    name: str
    email: str
    github_token: str  # For PR creation

class MultiplayerSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.participants: dict[str, Author] = {}
        self.prompt_queue: list[PromptContext] = []
    
    def add_participant(self, author: Author):
        """Add a participant to the session."""
        self.participants[author.id] = author
        self.broadcast_event("participant_joined", author)
    
    async def process_prompt(self, prompt: PromptContext):
        """Process prompt with author attribution."""
        # Update git config for this author; argv, not a shell string
        await self.sandbox.exec("git", "config", "user.name", prompt.author.name)
        await self.sandbox.exec("git", "config", "user.email", prompt.author.email)
        
        # Run agent
        result = await self.agent.run(prompt.content)
        
        # If changes were made, create PR with author's token
        if result.has_changes:
            await self.create_pr(
                branch=result.branch,
                author=prompt.author
            )
        
        return result
    
    async def create_pr(self, branch: str, author: Author):
        """Create PR using the author's GitHub token."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {author.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            await session.post(
                f"https://api.github.com/repos/{self.repo}/pulls",
                headers=headers,
                json={
                    "title": self.generate_pr_title(),
                    "body": self.generate_pr_body(),
                    "head": branch,
                    "base": "main"
                }
            )
```

## Metrics and Monitoring

### Key Metrics to Track

```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class SessionMetrics:
    session_id: str
    started_at: datetime
    first_token_at: datetime | None
    completed_at: datetime | None
    pr_created: bool
    pr_merged: bool
    prompts_count: int
    participants_count: int
    
    @property
    def time_to_first_token(self) -> timedelta | None:
        if self.first_token_at:
            return self.first_token_at - self.started_at
        return None

class MetricsAggregator:
    def get_adoption_metrics(self, period: timedelta) -> dict:
        """Get adoption metrics for a time period."""
        sessions = self.get_sessions_in_period(period)
        
        total_prs = sum(1 for s in sessions if s.pr_created)
        merged_prs = sum(1 for s in sessions if s.pr_merged)
        
        return {
            "total_sessions": len(sessions),
            "prs_created": total_prs,
            "prs_merged": merged_prs,
            "merge_rate": merged_prs / total_prs if total_prs > 0 else 0,
            "avg_time_to_first_token": self._avg_ttft(sessions),
            "unique_users": len(set(s.author_id for s in sessions)),
            "multiplayer_sessions": sum(
                1 for s in sessions if s.participants_count > 1
            )
        }
    
    def get_repository_metrics(self) -> dict[str, dict]:
        """Get metrics broken down by repository."""
        metrics = {}
        
        for repo in self.repositories:
            repo_sessions = self.get_sessions_for_repo(repo)
            total_prs = self.get_total_prs(repo)
            agent_prs = sum(1 for s in repo_sessions if s.pr_merged)
            
            metrics[repo] = {
                "agent_pr_percentage": agent_prs / total_prs * 100,
                "session_count": len(repo_sessions),
                "avg_prompts_per_session": sum(
                    s.prompts_count for s in repo_sessions
                ) / len(repo_sessions)
            }
        
        return metrics
```

## Security Considerations

### Sandbox Isolation

Enforce egress at the platform, not with a command denylist: blocking `curl` does not stop `python` or `node` from opening sockets. Keep credentials out of the sandbox entirely; a token in a clone URL or environment variable persists in `.git/config` or process state and is copied into every image and snapshot. Route git and registry traffic through a proxy outside the sandbox that injects a short-lived credential and permits pushes only to the session branch ([Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing), [Modal networking](https://modal.com/docs/guide/sandbox-networking)).

```python
class SandboxSecurityConfig:
    """Security configuration for sandboxes."""
    
    # Egress allowlist, enforced by the platform
    # (Modal: Sandbox.create(outbound_domain_allowlist=...))
    outbound_domain_allowlist = [
        "git-proxy.example.com",       # injects the session-scoped GitHub token
        "registry-proxy.example.com",  # injects registry credentials
    ]
    
    # Resource limits (Modal: sandbox timeout defaults to 5 minutes, max 24 hours)
    max_memory_mb = 4096
    max_cpu_cores = 2
    max_disk_gb = 10
    max_runtime_hours = 4
    
    # Secrets placed in the sandbox image, environment, or snapshot: none
    secrets_in_sandbox: list[str] = []
```

### Token Handling

This runs in the proxy and API, outside the sandbox. Installation tokens expire after one hour; mint one per request, scoped to the session's repository ([GitHub docs](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app)).

```python
class TokenManager:
    """Manage tokens for GitHub operations, outside the sandbox."""
    
    def get_app_installation_token(self, repo: str) -> str:
        """Get short-lived token for repo access."""
        # Token expires in 1 hour; scope it to one repository
        return github_app.create_installation_token(
            installation_id=self.get_installation_id(repo),
            repositories=[repo.split("/")[1]],
            permissions={"contents": "write", "pull_requests": "write"}
        )
    
    def get_user_token(self, user_id: str) -> str:
        """Get user's OAuth token for PR creation."""
        # Stored encrypted, decrypted at runtime
        encrypted = self.storage.get(f"user_token:{user_id}")
        return self.decrypt(encrypted)
```

## References

- [Modal Sandboxes](https://modal.com/docs/guide/sandboxes)
- [Modal Sandbox Snapshots](https://modal.com/docs/guide/sandbox-snapshots)
- [Modal 1.0 migration guide](https://modal.com/docs/guide/modal-1-0-migration)
- [OpenCode](https://opencode.ai/docs/)
- [Cloudflare Durable Objects](https://developers.cloudflare.com/durable-objects/)
- [Cloudflare Agents SDK](https://developers.cloudflare.com/agents/)
- [GitHub Apps Authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app)
- [Slack Bolt for Python](https://docs.slack.dev/tools/bolt-python/)
- [Chrome Extension APIs](https://developer.chrome.com/docs/extensions/)
