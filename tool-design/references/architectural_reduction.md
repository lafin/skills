# Architectural Reduction

This document provides implementation patterns for reducing a specialized tool set to a smaller set of general-purpose capabilities.

The production example that motivates this pattern is documented once in the [dated Vercel d0 evidence](skill://project-development/references/case-studies.md#evidence-vercel-d0-architectural-reduction-december-2025). That section states the source, evaluation scope, reported results, and limits of the comparison.

## Implementation Pattern

### The File System Agent

```python
from ai import ToolLoopAgent, tool
from sandbox import Sandbox

# Create sandboxed environment with your data layer
sandbox = Sandbox.create()
await sandbox.write_files(data_layer_files)

# Single primitive tool
def create_execute_tool(sandbox):
    return tool(
        name="execute_command",
        description="""
        Execute a bash command in the sandbox environment.
        
        Use standard Unix tools to explore and understand the data layer:
        - ls: List directory contents
        - cat: Read file contents
        - grep: Search for patterns
        - find: Locate files
        
        The sandbox contains the semantic layer documentation:
        - /data/entities/*.yaml: Entity definitions
        - /data/measures/*.yaml: Measure calculations  
        - /data/joins/*.yaml: Join relationships
        - /docs/*.md: Additional documentation
        """,
        execute=lambda command: sandbox.exec(command)
    )

# Minimal agent
agent = ToolLoopAgent(
    model="claude-opus-4.5",
    tools={
        "execute_command": create_execute_tool(sandbox),
        "execute_sql": sql_tool,
    }
)
```

### Prerequisites for Success

This pattern works when:

1. **Documentation quality is high**: Files are well-structured, consistently named, and contain clear definitions.

2. **Model capability is sufficient**: The model can reason through complexity without hand-holding.

3. **Safety constraints permit**: The sandbox limits what the agent can access and modify.

4. **Domain is navigable**: The problem space can be explored through file inspection.

### When Not to Use

Reduction fails when:

1. **Data layer is messy**: Legacy naming conventions, undocumented joins, inconsistent structure. The model will produce faster bad queries.

2. **Specialized knowledge is required**: Domain expertise that can't be documented in files.

3. **Safety requires restrictions**: Operations that must be constrained for security or compliance.

4. **Workflows are genuinely complex**: Multi-step processes that benefit from structured orchestration.

## Design Principles

### Addition by Subtraction

The best agents may be the ones with the fewest tools. Every tool is a choice made for the model. Sometimes the model makes better choices when given primitive capabilities rather than constrained workflows.

### Trust Model Reasoning

Modern models can handle complexity. Constraining reasoning because you don't trust the model to reason is often counterproductive. Test what the model can actually do before building guardrails.

### Invest in Context, Not Tooling

The foundation matters more than clever tooling:
- Clear file naming conventions
- Well-structured documentation
- Consistent data organization
- Legible relationship definitions

### Build for Future Models

Models improve faster than tooling can keep up. An architecture optimized for today's model limitations may be over-constrained for tomorrow's model capabilities. Build minimal architectures that benefit from model improvements.

## Evaluation Framework

When considering architectural reduction, evaluate:

1. **Maintenance overhead**: How much time is spent maintaining tools vs. improving outcomes?

2. **Failure analysis**: Are failures caused by model limitations or tool constraints?

3. **Documentation quality**: Could the model navigate your data layer directly if given access?

4. **Constraint necessity**: Are guardrails protecting against real risks or hypothetical concerns?

5. **Model capability**: Has the model improved since tools were designed?

## Conclusion

Architectural reduction is not universally applicable, but the principle challenges a common assumption: that more sophisticated tooling leads to better outcomes. Sometimes the opposite is true. Start with the simplest possible architecture, add complexity only when proven necessary, and continuously question whether tools are enabling or constraining model capabilities.

## References

- Vercel Engineering: "We removed 80% of our agent's tools" (December 2025)
- AI SDK ToolLoopAgent documentation
- Vercel Sandbox documentation





