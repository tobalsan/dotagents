# Langgraph - Memory

**Pages:** 6

---

## Human-in-the-loop requires a thread ID for persistence

**URL:** llms-txt#human-in-the-loop-requires-a-thread-id-for-persistence

config = {"configurable": {"thread_id": "some_id"}}

---

## Initialize an in-memory checkpointer for persistence

**URL:** llms-txt#initialize-an-in-memory-checkpointer-for-persistence

checkpointer = InMemorySaver()

@task
def slow_task():
    """
    Simulates a slow-running task by introducing a 1-second delay.
    """
    time.sleep(1)
    return "Ran slow task."

@entrypoint(checkpointer=checkpointer)
def main(inputs, writer: StreamWriter):
    """
    Main workflow function that runs the slow_task and get_info tasks sequentially.

Parameters:
    - inputs: Dictionary containing workflow input values.
    - writer: StreamWriter for streaming custom data.

The workflow first executes `slow_task` and then attempts to execute `get_info`,
    which will fail on the first invocation.
    """
    slow_task_result = slow_task().result()  # Blocking call to slow_task
    get_info().result()  # Exception will be raised here on the first attempt
    return slow_task_result

---

## Create config with thread_id for state persistence

**URL:** llms-txt#create-config-with-thread_id-for-state-persistence

config = {"configurable": {"thread_id": str(uuid.uuid4())}}

---

## Persistence

**URL:** llms-txt#persistence

**Contents:**
- Threads
- Checkpoints
  - Get state

Source: https://docs.langchain.com/oss/python/langgraph/persistence

LangGraph has a built-in persistence layer, implemented through checkpointers. When you compile a graph with a checkpointer, the checkpointer saves a `checkpoint` of the graph state at every super-step. Those checkpoints are saved to a `thread`, which can be accessed after graph execution. Because `threads` allow access to graph's state after execution, several powerful capabilities including human-in-the-loop, memory, time travel, and fault-tolerance are all possible. Below, we'll discuss each of these concepts in more detail.

<img src="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/checkpoints.jpg?fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=966566aaae853ed4d240c2d0d067467c" alt="Checkpoints" data-og-width="2316" width="2316" data-og-height="748" height="748" data-path="oss/images/checkpoints.jpg" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/checkpoints.jpg?w=280&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=7bb8525bfcd22b3903b3209aa7497f47 280w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/checkpoints.jpg?w=560&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=e8d07fc2899b9a13c7b00eb9b259c3c9 560w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/checkpoints.jpg?w=840&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=46a2f9ed3b131a7c78700711e8c314d6 840w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/checkpoints.jpg?w=1100&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=c339bd49757810dad226e1846f066c94 1100w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/checkpoints.jpg?w=1650&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=8333dfdb9d766363f251132f2dfa08a1 1650w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/checkpoints.jpg?w=2500&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=33ba13937eed043ba4a7a87b36d3046f 2500w" />

<Info>
  **LangGraph API handles checkpointing automatically**
  When using the LangGraph API, you don't need to implement or configure checkpointers manually. The API handles all persistence infrastructure for you behind the scenes.
</Info>

A thread is a unique ID or thread identifier assigned to each checkpoint saved by a checkpointer. It contains the accumulated state of a sequence of [runs](/langsmith/assistants#execution). When a run is executed, the [state](/oss/python/langgraph/graph-api#state) of the underlying graph of the assistant will be persisted to the thread.

When invoking a graph with a checkpointer, you **must** specify a `thread_id` as part of the `configurable` portion of the config.

A thread's current and historical state can be retrieved. To persist state, a thread must be created prior to executing a run. The LangSmith API provides several endpoints for creating and managing threads and thread state. See the [API reference](https://langchain-ai.github.io/langgraph/cloud/reference/api/) for more details.

The state of a thread at a particular point in time is called a checkpoint. Checkpoint is a snapshot of the graph state saved at each super-step and is represented by `StateSnapshot` object with the following key properties:

* `config`: Config associated with this checkpoint.
* `metadata`: Metadata associated with this checkpoint.
* `values`: Values of the state channels at this point in time.
* `next` A tuple of the node names to execute next in the graph.
* `tasks`: A tuple of `PregelTask` objects that contain information about next tasks to be executed. If the step was previously attempted, it will include error information. If a graph was interrupted [dynamically](/oss/python/langgraph/interrupts#pause-using-interrupt) from within a node, tasks will contain additional data associated with interrupts.

Checkpoints are persisted and can be used to restore the state of a thread at a later time.

Let's see what checkpoints are saved when a simple graph is invoked as follows:

After we run the graph, we expect to see exactly 4 checkpoints:

* Empty checkpoint with [`START`](https://reference.langchain.com/python/langgraph/constants/#langgraph.constants.START) as the next node to be executed
* Checkpoint with the user input `{'foo': '', 'bar': []}` and `node_a` as the next node to be executed
* Checkpoint with the outputs of `node_a` `{'foo': 'a', 'bar': ['a']}` and `node_b` as the next node to be executed
* Checkpoint with the outputs of `node_b` `{'foo': 'b', 'bar': ['a', 'b']}` and no next nodes to be executed

Note that we `bar` channel values contain outputs from both nodes as we have a reducer for `bar` channel.

When interacting with the saved graph state, you **must** specify a [thread identifier](#threads). You can view the *latest* state of the graph by calling `graph.get_state(config)`. This will return a `StateSnapshot` object that corresponds to the latest checkpoint associated with the thread ID provided in the config or a checkpoint associated with a checkpoint ID for the thread, if provided.

```python  theme={null}

**Examples:**

Example 1 (unknown):
```unknown
A thread's current and historical state can be retrieved. To persist state, a thread must be created prior to executing a run. The LangSmith API provides several endpoints for creating and managing threads and thread state. See the [API reference](https://langchain-ai.github.io/langgraph/cloud/reference/api/) for more details.

## Checkpoints

The state of a thread at a particular point in time is called a checkpoint. Checkpoint is a snapshot of the graph state saved at each super-step and is represented by `StateSnapshot` object with the following key properties:

* `config`: Config associated with this checkpoint.
* `metadata`: Metadata associated with this checkpoint.
* `values`: Values of the state channels at this point in time.
* `next` A tuple of the node names to execute next in the graph.
* `tasks`: A tuple of `PregelTask` objects that contain information about next tasks to be executed. If the step was previously attempted, it will include error information. If a graph was interrupted [dynamically](/oss/python/langgraph/interrupts#pause-using-interrupt) from within a node, tasks will contain additional data associated with interrupts.

Checkpoints are persisted and can be used to restore the state of a thread at a later time.

Let's see what checkpoints are saved when a simple graph is invoked as follows:
```

Example 2 (unknown):
```unknown
After we run the graph, we expect to see exactly 4 checkpoints:

* Empty checkpoint with [`START`](https://reference.langchain.com/python/langgraph/constants/#langgraph.constants.START) as the next node to be executed
* Checkpoint with the user input `{'foo': '', 'bar': []}` and `node_a` as the next node to be executed
* Checkpoint with the outputs of `node_a` `{'foo': 'a', 'bar': ['a']}` and `node_b` as the next node to be executed
* Checkpoint with the outputs of `node_b` `{'foo': 'b', 'bar': ['a', 'b']}` and no next nodes to be executed

Note that we `bar` channel values contain outputs from both nodes as we have a reducer for `bar` channel.

### Get state

When interacting with the saved graph state, you **must** specify a [thread identifier](#threads). You can view the *latest* state of the graph by calling `graph.get_state(config)`. This will return a `StateSnapshot` object that corresponds to the latest checkpoint associated with the thread ID provided in the config or a checkpoint associated with a checkpoint ID for the thread, if provided.
```

---

## Compile with checkpointer for persistence

**URL:** llms-txt#compile-with-checkpointer-for-persistence

**Contents:**
- 3. Test the graph locally

graph = builder.compile(checkpointer=checkpointer)
python  theme={null}
from IPython.display import display, Image

display(Image(graph.get_graph().draw_mermaid_png()))
python {highlight={2,13}} theme={null}

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
<img src="https://mintcdn.com/langchain-5e9cc07a/IMK8wJkjSpMCGODD/langsmith/images/autogen-output.png?fit=max&auto=format&n=IMK8wJkjSpMCGODD&q=85&s=1165c5d1a5c154b2491d6a5fca30853f" alt="LangGraph chatbot with one step: START routes to autogen, where call_autogen_agent sends the latest user message (with prior context) to the AutoGen agent." data-og-width="180" width="180" data-og-height="134" height="134" data-path="langsmith/images/autogen-output.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/IMK8wJkjSpMCGODD/langsmith/images/autogen-output.png?w=280&fit=max&auto=format&n=IMK8wJkjSpMCGODD&q=85&s=6a6671038776cd1784c968ee2ecf973e 280w, https://mintcdn.com/langchain-5e9cc07a/IMK8wJkjSpMCGODD/langsmith/images/autogen-output.png?w=560&fit=max&auto=format&n=IMK8wJkjSpMCGODD&q=85&s=94c98b5b118ae49006d2f56179e1dc0d 560w, https://mintcdn.com/langchain-5e9cc07a/IMK8wJkjSpMCGODD/langsmith/images/autogen-output.png?w=840&fit=max&auto=format&n=IMK8wJkjSpMCGODD&q=85&s=703b4822dfc1c3395c16dd9e7d0f1462 840w, https://mintcdn.com/langchain-5e9cc07a/IMK8wJkjSpMCGODD/langsmith/images/autogen-output.png?w=1100&fit=max&auto=format&n=IMK8wJkjSpMCGODD&q=85&s=0f6b4e65d2f036d5b28dde44afbb5fd8 1100w, https://mintcdn.com/langchain-5e9cc07a/IMK8wJkjSpMCGODD/langsmith/images/autogen-output.png?w=1650&fit=max&auto=format&n=IMK8wJkjSpMCGODD&q=85&s=17f044c125e4a480d4bd8814c19a0949 1650w, https://mintcdn.com/langchain-5e9cc07a/IMK8wJkjSpMCGODD/langsmith/images/autogen-output.png?w=2500&fit=max&auto=format&n=IMK8wJkjSpMCGODD&q=85&s=841b246f7eabe796de9c4ac0af4816dd 2500w" />

## 3. Test the graph locally

Before deploying to LangSmith, you can test the graph locally:
```

---

## Checkpointer is REQUIRED for human-in-the-loop

**URL:** llms-txt#checkpointer-is-required-for-human-in-the-loop

**Contents:**
- Decision types
- Handle interrupts

checkpointer = MemorySaver()

agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[delete_file, read_file, send_email],
    interrupt_on={
        "delete_file": True,  # Default: approve, edit, reject
        "read_file": False,   # No interrupts needed
        "send_email": {"allowed_decisions": ["approve", "reject"]},  # No editing
    },
    checkpointer=checkpointer  # Required!
)
python  theme={null}
interrupt_on = {
    # Sensitive operations: allow all options
    "delete_file": {"allowed_decisions": ["approve", "edit", "reject"]},

# Moderate risk: approval or rejection only
    "write_file": {"allowed_decisions": ["approve", "reject"]},

# Must approve (no rejection allowed)
    "critical_operation": {"allowed_decisions": ["approve"]},
}
python  theme={null}
import uuid
from langgraph.types import Command

**Examples:**

Example 1 (unknown):
```unknown
## Decision types

The `allowed_decisions` list controls what actions a human can take when reviewing a tool call:

* **`"approve"`**: Execute the tool with the original arguments as proposed by the agent
* **`"edit"`**: Modify the tool arguments before execution
* **`"reject"`**: Skip executing this tool call entirely

You can customize which decisions are available for each tool:
```

Example 2 (unknown):
```unknown
## Handle interrupts

When an interrupt is triggered, the agent pauses execution and returns control. Check for interrupts in the result and handle them accordingly.
```

---
