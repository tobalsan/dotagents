---
name: langgraph
description: Create workflows with LangGraph
---

# Langgraph Skill

Comprehensive assistance with LangGraph development, extracted from official documentation. LangGraph is a Python framework for building stateful, multi-actor applications with LLMs using a graph-based architecture.

## When to Use This Skill

This skill should be triggered when:
- Building agent workflows with state management, persistence, or human-in-the-loop
- Implementing LLM applications that need memory across interactions
- Creating multi-step AI workflows with conditional logic
- Working with tool-calling agents that need to maintain context
- Debugging LangGraph graphs, nodes, edges, or state
- Converting between Graph API and Functional API
- Setting up LangGraph Server or LangSmith deployments
- Implementing streaming, interrupts, or double-texting patterns

## Key Concepts

### Graph API vs Functional API
- **Graph API**: Define agents as graphs with explicit nodes and edges. Best for complex workflows with clear state transitions.
- **Functional API**: Define agents as functions with standard control flow (loops, conditionals). Best for simpler workflows or when migrating existing code.

### Core Components
- **State**: Persistent data throughout agent execution. Use `Annotated` with `operator.add` to append to lists.
- **Nodes**: Units of work (functions) that process state
- **Edges**: Connections between nodes (can be conditional)
- **Checkpointer**: Persistence layer for saving graph state
- **Tasks**: In Functional API, functions decorated with `@task` that can run in parallel
- **Entrypoint**: In Functional API, main function decorated with `@entrypoint`

## Quick Reference

### 1. Basic Agent with Graph API (Tool-calling)

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing_extensions import TypedDict
import operator
from typing import Annotated

# Define state
class State(TypedDict):
    messages: Annotated[list, operator.add]

# Define model node
def call_model(state: State):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# Define tool node
def call_tools(state: State):
    tools_call = tool_node.invoke(state["messages"])
    return {"messages": [tools_call]}

# Build graph
builder = StateGraph(State)
builder.add_node("model", call_model)
builder.add_node("tools", call_tools)
builder.add_edge(START, "model")

# Conditional edge: route to tools or end
def should_continue(state: State):
    return "tools" if state["messages"][-1].tool_calls else END

builder.add_conditional_edges("model", should_continue)
builder.add_edge("tools", "model")

# Compile with checkpointer
graph = builder.compile(checkpointer=InMemorySaver())
```

### 2. Basic Workflow with Functional API

```python
from langgraph.func import entrypoint, task
from langgraph.checkpoint.memory import InMemorySaver

@task
async def process_data(data: str) -> str:
    # Process data
    return f"Processed: {data}"

@entrypoint(checkpointer=InMemorySaver())
async def workflow(input_data: str):
    result = await process_data(input_data)
    return result
```

### 3. Parallel Task Execution

```python
from langgraph.func import entrypoint, task

@task
async def generate_paragraph(topic: str) -> str:
    response = await llm.ainvoke(f"Write a paragraph about {topic}")
    return response.content

@entrypoint()
async def parallel_workflow(topics: list[str]):
    # Execute tasks in parallel
    tasks = [generate_paragraph(topic) for topic in topics]
    results = await asyncio.gather(*tasks)
    return "\n\n".join(results)
```

### 4. Streaming Updates

```python
# Stream graph state updates
for chunk in client.runs.stream(
    thread_id=thread["thread_id"],
    assistant_id="agent",
    input={"messages": [{"role": "user", "content": "What is 2+2?"}]},
    stream_mode="updates"  # Also: "values", "debug", "messages-tuple"
):
    print(chunk)
```

### 5. Custom Authentication for Deployments

```python
from langgraph_sdk.auth import Auth

auth = Auth()

@auth.authenticate
async def get_current_user(authorization: str):
    # Validate token and return user info
    token = authorization.replace("Bearer ", "")
    user = verify_jwt(token)
    return {
        "identity": user["sub"],
        "oauth_token": token,
        "role": user.get("role")
    }

# In langgraph.json:
# "auth": {"path": "auth.py"}

# Access in graph:
def my_node(state: State, config: dict):
    user = config["configurable"]["langgraph_auth_user"]
    user_id = user["identity"]
    # Use user info...
```

### 6. Human-in-the-Loop with Interrupts

```python
from langgraph.types import interrupt

def approval_node(state: State):
    # Interrupt and wait for approval
    approval = interrupt("Do you approve this action?")

    if approval:
        # Continue processing
        return {"approved": True}
    else:
        return {"approved": False}
```

### 7. Stream Custom Data

```python
from langgraph.config import get_stream_writer

@entrypoint()
async def workflow(data: str):
    writer = get_stream_writer()

    # Emit custom data
    writer("Starting computation...")

    result = await compute(data)

    writer(f"Completed with result: {result}")
    return result

# Stream with custom mode
for chunk in graph.stream(input_data, stream_mode="custom"):
    print(chunk)
```

### 8. State with Annotations (Append vs Replace)

```python
from typing_extensions import TypedDict
from typing import Annotated
import operator

class State(TypedDict):
    # Messages will be APPENDED (not replaced)
    messages: Annotated[list, operator.add]

    # Counter will be REPLACED
    counter: int

    # Custom reducer function
    scores: Annotated[list[int], lambda old, new: old + new if old else new]
```

### 9. Conditional Routing

```python
from langgraph.graph import StateGraph, END

def route_logic(state: State) -> str:
    if state["error_count"] > 3:
        return "error_handler"
    elif state["needs_review"]:
        return "review"
    else:
        return END

builder = StateGraph(State)
builder.add_node("process", process_node)
builder.add_node("error_handler", error_node)
builder.add_node("review", review_node)

builder.add_conditional_edges("process", route_logic)
```

### 10. Local Development Setup

```bash
# Install CLI
pip install langgraph-cli

# Create new project from template
langgraph new my-agent --template new-langgraph-project-python

# Install dependencies in edit mode
cd my-agent
pip install -e .

# Create .env file with API keys
echo "ANTHROPIC_API_KEY=your-key" > .env

# Start development server
langgraph dev
```

## Reference Files

This skill includes comprehensive documentation in `references/`:

### basics.md (17 pages)
Core fundamentals and getting started guides:
- **Quickstart**: Build a calculator agent using Graph API or Functional API
- **Local Server Setup**: Run LangGraph apps locally with the CLI
- **Installation and Configuration**: Set up dependencies and environment

### graphs.md (115 pages)
Graph architecture and deployment:
- **Building State Graphs**: Create nodes, edges, and state management
- **Custom Authentication**: Add auth handlers for deployments
- **Webhook Notifications**: Configure alerts and integrations
- **Deployment Configuration**: Set up LangSmith Cloud/Hybrid/Self-hosted

### interactions.md (15 pages)
Runtime interactions and control flow:
- **Streaming API**: Stream updates, values, debug info, and LLM tokens
- **Interrupts**: Implement human-in-the-loop patterns
- **Double-texting**: Handle concurrent runs with interrupt/rollback/reject strategies
- **Functional API Usage**: Use `@task` and `@entrypoint` decorators

### memory.md
State persistence and memory management:
- **Checkpointers**: Persist graph state across runs
- **Thread Management**: Handle multi-turn conversations
- **State Updates**: Modify and retrieve historical state

### other.md
Additional topics:
- **Subgraphs**: Compose nested graph structures
- **Error Handling**: Implement retry policies and error recovery
- **Testing and Debugging**: Tools for development workflows

## Working with This Skill

### For Beginners
Start with **basics.md** for:
- The quickstart tutorial (simple calculator agent)
- Understanding State, Nodes, and Edges
- Choosing between Graph API and Functional API
- Local development setup with `langgraph dev`

### For Building Agents
Use **graphs.md** and **interactions.md** for:
- Tool-calling patterns with LLMs
- State management with `Annotated` types
- Streaming responses to users
- Human-in-the-loop workflows with interrupts
- Conditional routing between nodes

### For Production Deployment
Refer to **graphs.md** for:
- Authentication and authorization
- LangSmith Cloud/Hybrid/Self-hosted setup
- Webhook integrations
- Environment configuration in `langgraph.json`

### For Advanced Features
Explore **memory.md** and **other.md** for:
- Custom checkpointer implementations
- Subgraph composition
- Retry policies and error handling
- Performance optimization

## Common Patterns

### Agent with Memory
```python
from langgraph.checkpoint.memory import InMemorySaver

graph = builder.compile(checkpointer=InMemorySaver())

# Use with thread_id to persist state
graph.invoke(
    {"messages": [{"role": "user", "content": "Hello"}]},
    config={"configurable": {"thread_id": "user-123"}}
)
```

### Multi-Mode Streaming
```python
# Stream multiple outputs simultaneously
for mode, chunk in graph.stream(
    input_data,
    stream_mode=["updates", "messages"]
):
    if mode == "updates":
        print(f"Node update: {chunk}")
    elif mode == "messages":
        print(f"LLM token: {chunk}")
```

## Resources

### Local References

- [basics](./references/basics.md)
- [graphs](./references/graphs.md)
- [interactions](./references/interactions.md)
- [memory](./references/memory.md)

### Official Documentation
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangSmith Platform](https://docs.langchain.com/langsmith/)
- [Graph API Reference](https://reference.langchain.com/python/langgraph/graphs/)
- [Functional API Reference](https://reference.langchain.com/python/langgraph/func/)

### Example Templates
- [Python Template](https://github.com/langchain-ai/new-langgraph-project)
- [JavaScript Template](https://github.com/langchain-ai/new-langgraphjs-project)

## Notes

- State persistence requires a checkpointer (InMemorySaver for dev, PostgreSQL/Redis for prod)
- The Functional API and Graph API share the same runtime and can be mixed
- For async code with Python < 3.11, use `StreamWriter` class directly instead of `get_stream_writer()`
- LangGraph SDK is part of LangSmith - server functionality requires LangSmith deployment
- Use `langgraph dev` for local development with hot-reload
- Authentication only applies to LangSmith deployments, not standalone library usage

## Troubleshooting

### Common Issues
1. **Missing checkpointer**: Add `checkpointer=InMemorySaver()` to `.compile()` for persistence
2. **State not updating**: Check if using `Annotated[list, operator.add]` for append behavior
3. **Streaming not working**: Verify `stream_mode` parameter and that you're iterating the stream
4. **Auth not applied**: Ensure `auth` path is set in `langgraph.json` and handler returns `identity` field
5. **Thread errors**: Create thread before streaming with `client.threads.create()`
