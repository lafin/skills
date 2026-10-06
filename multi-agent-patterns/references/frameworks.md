# Multi-Agent Patterns: Technical Reference

This document provides implementation details for multi-agent architectures across different frameworks.

## Supervisor Pattern

### LangChain Subagents (Supervisor)

The `langgraph-supervisor` package is no longer actively maintained. LangChain's [migration guide](https://docs.langchain.com/oss/python/migrate/langgraph-supervisor) replaces `create_supervisor` with a main `create_agent` that calls each worker through a tool. The supervisor stops when its model answers without a tool call, so no hand-written loop edges are needed.

```python
from langchain.agents import create_agent
from langchain.tools import tool

MODEL = "MODEL"  # placeholder: a "provider:model" string or a chat model instance

research_agent = create_agent(
    model=MODEL, tools=[], system_prompt="You are a research specialist. Cite sources."
)
writer_agent = create_agent(
    model=MODEL, tools=[], system_prompt="You write content from the research notes you receive."
)

@tool("research", description="Gather and cite sources for a question.")
def call_research(query: str) -> str:
    result = research_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content  # return only the final message

@tool("write", description="Draft content from research notes.")
def call_writer(notes: str) -> str:
    result = writer_agent.invoke({"messages": [{"role": "user", "content": notes}]})
    return result["messages"][-1].content

supervisor = create_agent(
    model=MODEL,
    tools=[call_research, call_writer],
    system_prompt="Delegate research, then writing. Answer the user when the draft is done.",
)
```

### Porting from AutoGen

AutoGen is in maintenance mode: it receives no new features, and new users should start with [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) ([AutoGen README](https://github.com/microsoft/autogen)). Agent Framework provides graph-based workflows with sequential, concurrent, handoff, and group-collaboration patterns. Port `GroupChat` code with the [AutoGen migration guide](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/).

## Handoff (Swarm) Pattern Implementation

### LangGraph Handoffs with `Command.PARENT`

Each agent is a node in a parent graph. A handoff tool returns `Command(goto=..., graph=Command.PARENT)` to move control to another node, and passes the triggering `AIMessage` with a matching `ToolMessage` so the receiver sees valid history. A conditional edge ends the run when the active agent answers without a tool call. Source: [LangChain handoffs](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs).

```python
from langchain.agents import AgentState, create_agent
from langchain.messages import AIMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from typing_extensions import NotRequired

MODEL = "MODEL"  # placeholder: a "provider:model" string or a chat model instance

class SwarmState(AgentState):
    active_agent: NotRequired[str]

def make_handoff(target: str):
    @tool(f"transfer_to_{target}", description=f"Hand the conversation to the {target} agent.")
    def handoff(runtime: ToolRuntime) -> Command:
        last_ai = next(m for m in reversed(runtime.state["messages"]) if isinstance(m, AIMessage))
        ack = ToolMessage(content=f"Transferred to {target}", tool_call_id=runtime.tool_call_id)
        return Command(
            goto=target,
            update={"active_agent": target, "messages": [last_ai, ack]},
            graph=Command.PARENT,
        )
    return handoff

AGENTS = {
    "triage": create_agent(
        model=MODEL, tools=[make_handoff("research")], state_schema=SwarmState,
        system_prompt="Classify the request. Hand research questions to research.",
    ),
    "research": create_agent(
        model=MODEL, tools=[make_handoff("triage")], state_schema=SwarmState,
        system_prompt="Answer research questions. Hand anything else back to triage.",
    ),
}

def route(state: SwarmState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and not last.tool_calls:
        return END  # the active agent answered; stop
    return state.get("active_agent", "triage")

builder = StateGraph(SwarmState)
for name, agent in AGENTS.items():
    builder.add_node(name, agent)
    builder.add_conditional_edges(name, route, [*AGENTS, END])
builder.add_conditional_edges(START, lambda s: s.get("active_agent", "triage"), list(AGENTS))
swarm = builder.compile()
```

### OpenAI Agents SDK Handoffs

The [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/handoffs/) exposes each handoff to the model as a `transfer_to_<agent_name>` tool. Pass an `Agent` directly, or wrap it in `handoff()` to set `input_filter` (what history the receiver sees) or `on_handoff`.

```python
from agents import Agent, handoff
from agents.extensions import handoff_filters

billing_agent = Agent(name="Billing agent", instructions="Resolve billing questions.")
refund_agent = Agent(name="Refund agent", instructions="Process refund requests.")

triage_agent = Agent(
    name="Triage agent",
    instructions="Route each request to the right specialist.",
    handoffs=[billing_agent, handoff(refund_agent, input_filter=handoff_filters.remove_all_tools)],
)
# Run with: Runner.run_sync(triage_agent, "I was charged twice.")
```

### Claude Agent SDK Subagents

The [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/subagents) defines subagents with `AgentDefinition` and invokes them through the `Agent` tool. A subagent starts with a fresh context; the only parent input is the `Agent` tool's prompt, and only its final message returns to the parent.

```python
import asyncio
from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob", "Agent"],
    agents={
        "code-reviewer": AgentDefinition(
            description="Security code reviewer. Use for security reviews.",
            prompt="You review code for security issues and report findings with file paths.",
            tools=["Read", "Grep", "Glob"],  # read-only
        ),
    },
)

async def main():
    async for message in query(prompt="Use the code-reviewer agent on the auth module", options=options):
        if hasattr(message, "result"):
            print(message.result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Hierarchical Pattern Implementation

### Generic Manager-Worker Sketch

This is plain Python, not the CrewAI API; the helper functions are placeholders. For CrewAI's hierarchical process, see the [CrewAI documentation](https://docs.crewai.com/).

```python
# Pseudocode: generic manager-worker sketch; helper functions are placeholders.
class ManagerAgent:
    def __init__(self, name, system_prompt, llm):
        self.name = name
        self.system_prompt = system_prompt
        self.llm = llm
        self.workers = []
    
    def add_worker(self, worker):
        """Add a worker agent to the team."""
        self.workers.append(worker)
    
    def delegate(self, task):
        """
        Analyze task and delegate to appropriate worker.
        
        Returns work assignment and expected output format.
        """
        # Analyze task requirements
        requirements = analyze_task_requirements(task)
        
        # Select best worker
        best_worker = select_worker(self.workers, requirements)
        
        # Create assignment
        assignment = {
            "worker": best_worker.name,
            "task": task,
            "context": self.get_relevant_context(task),
            "output_format": requirements.output_format,
            "deadline": requirements.deadline
        }
        
        return assignment
    
    def review_output(self, worker_output, requirements):
        """
        Review worker output against requirements.
        
        Returns approval or revision request.
        """
        quality_score = assess_quality(worker_output, requirements)
        
        if quality_score >= requirements.threshold:
            return {"status": "approved", "output": worker_output}
        else:
            return {
                "status": "revision_requested",
                "feedback": generate_feedback(worker_output, requirements),
                "revise_worker": requirements.revise_worker
            }
```

## Context Isolation Patterns

### Full Context Delegation

```python
def delegate_with_full_context(planner_state, subagent):
    """
    Pass entire planner context to subagent.
    
    Use for complex tasks requiring complete understanding.
    """
    return {
        "context": planner_state,
        "subagent": subagent,
        "isolation_mode": "full"
    }
```

### Instruction Passing

```python
def delegate_with_instructions(task_spec, subagent):
    """
    Pass only instructions to subagent.
    
    Use for simple, well-defined subtasks.
    """
    return {
        "instructions": {
            "objective": task_spec.objective,
            "constraints": task_spec.constraints,
            "inputs": task_spec.inputs,
            "outputs": task_spec.output_schema
        },
        "subagent": subagent,
        "isolation_mode": "minimal"
    }
```

### File System Coordination

```python
import json
import os

class FileSystemCoordination:
    def __init__(self, workspace_path):
        self.workspace = workspace_path
        self.lock_dir = os.path.join(workspace_path, "locks")
        os.makedirs(self.lock_dir, exist_ok=True)
    
    def write_shared_state(self, key, value):
        """Write state accessible to all agents."""
        path = os.path.join(self.workspace, f"{key}.json")
        with open(path, 'w') as f:
            json.dump(value, f)
        return path
    
    def read_shared_state(self, key):
        """Read state written by any agent."""
        path = os.path.join(self.workspace, f"{key}.json")
        with open(path, 'r') as f:
            return json.load(f)
    
    def acquire_lock(self, resource, agent_id):
        """Create the lock file atomically; fail if another agent holds it."""
        lock_path = os.path.join(self.lock_dir, f"{resource}.lock")
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return False
        with os.fdopen(fd, 'w') as f:
            f.write(agent_id)
        return True
    
    def release_lock(self, resource):
        """Release a lock held by this agent."""
        os.remove(os.path.join(self.lock_dir, f"{resource}.lock"))
```

## Consensus Mechanisms

### Weighted Voting

```python
def weighted_consensus(agent_outputs, weights):
    """
    Calculate weighted consensus from agent outputs.
    
    Weight = verbalized_confidence * domain_expertise
    """
    weighted_sum = sum(
        output.vote * weights[output.agent_id]
        for output in agent_outputs
    )
    total_weight = sum(weights[output.agent_id] for output in agent_outputs)
    
    return weighted_sum / total_weight
```

### Debate Protocol

```python
class DebateProtocol:
    def __init__(self, agents, max_rounds=5):
        self.agents = agents
        self.max_rounds = max_rounds
        self.history = []
    
    def run_debate(self, topic):
        """Execute structured debate on topic."""
        # Initial statements
        statements = {agent.name: agent.initial_statement(topic) 
                      for agent in self.agents}
        
        for round_num in range(self.max_rounds):
            # Generate critiques
            critiques = {}
            for agent in self.agents:
                critiques[agent.name] = agent.critique(
                    topic, 
                    statements,
                    exclude=[agent.name]
                )
            
            # Update statements with critique integration
            for agent in self.agents:
                statements[agent.name] = agent.integrate_critique(
                    statements[agent.name],
                    critiques
                )
            
            # Check for convergence
            if self.check_convergence(statements):
                break
        
        # Final evaluation
        return self.evaluate_final(statements)
```

## Failure Recovery

### Circuit Breaker

```python
class AgentCircuitBreaker:
    def __init__(self, failure_threshold=3, timeout_seconds=60):
        self.failure_count = {}
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
    
    def call(self, agent, task):
        """Execute agent task with circuit breaker protection."""
        if self.is_open(agent.name):
            raise CircuitBreakerOpen(f"Agent {agent.name} temporarily unavailable")
        
        try:
            result = agent.execute(task)
            self.record_success(agent.name)
            return result
        except Exception as e:
            self.record_failure(agent.name)
            if self.failure_count[agent.name] >= self.failure_threshold:
                self.open_circuit(agent.name)
            raise
```

### Checkpoint and Resume

```python
class CheckpointManager:
    def __init__(self, checkpoint_dir):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
    
    def save_checkpoint(self, workflow_id, step, state):
        """Save workflow state for potential resume."""
        checkpoint = {
            "workflow_id": workflow_id,
            "step": step,
            "state": state,
            "timestamp": time.time()
        }
        path = f"{self.checkpoint_dir}/{workflow_id}.json"
        with open(path, 'w') as f:
            json.dump(checkpoint, f)
    
    def load_checkpoint(self, workflow_id):
        """Load last saved checkpoint for workflow."""
        path = f"{self.checkpoint_dir}/{workflow_id}.json"
        with open(path, 'r') as f:
            return json.load(f)
```

