# Langgraph - Interactions

**Pages:** 15

---

## >    Interrupt(

**URL:** llms-txt#>----interrupt(

---

## Run creation, streaming, updates, etc.

**URL:** llms-txt#run-creation,-streaming,-updates,-etc.

---

## Interrupt concurrent

**URL:** llms-txt#interrupt-concurrent

**Contents:**
- Setup
- Create runs
- View run results

Source: https://docs.langchain.com/langsmith/interrupt-concurrent

This guide assumes knowledge of what double-texting is, which you can learn about in the [double-texting conceptual guide](/langsmith/double-texting).

The guide covers the `interrupt` option for double texting, which interrupts the prior run of the graph and starts a new one with the double-text. This option does not delete the first run, but rather keeps it in the database but sets its status to `interrupted`. Below is a quick example of using the `interrupt` option.

First, we will define a quick helper function for printing out JS and CURL model outputs (you can skip this if using Python):

<Tabs>
  <Tab title="Javascript">
    
  </Tab>

<Tab title="CURL">
    
  </Tab>
</Tabs>

Now, let's import our required packages and instantiate our client, assistant, and thread.

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="Javascript">
    
  </Tab>

<Tab title="CURL">
    
  </Tab>
</Tabs>

Now we can start our two runs and join the second one until it has completed:

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="Javascript">
    
  </Tab>

<Tab title="CURL">
    
  </Tab>
</Tabs>

We can see that the thread has partial data from the first run + data from the second run

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="Javascript">
    
  </Tab>

<Tab title="CURL">
    
  </Tab>
</Tabs>

Verify that the original, interrupted run was interrupted

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="Javascript">
    
  </Tab>
</Tabs>

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/interrupt-concurrent.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
</Tab>

  <Tab title="CURL">
```

Example 2 (unknown):
```unknown
</Tab>
</Tabs>

Now, let's import our required packages and instantiate our client, assistant, and thread.

<Tabs>
  <Tab title="Python">
```

Example 3 (unknown):
```unknown
</Tab>

  <Tab title="Javascript">
```

Example 4 (unknown):
```unknown
</Tab>

  <Tab title="CURL">
```

---

## > [Interrupt(value='Do you approve this action?')]

**URL:** llms-txt#>-[interrupt(value='do-you-approve-this-action?')]

---

## Use the functional API

**URL:** llms-txt#use-the-functional-api

**Contents:**
- Creating a simple workflow
- Parallel execution
- Calling graphs
- Call other entrypoints
- Streaming
- Retry policy

Source: https://docs.langchain.com/oss/python/langgraph/use-functional-api

The [**Functional API**](/oss/python/langgraph/functional-api) allows you to add LangGraph's key features — [persistence](/oss/python/langgraph/persistence), [memory](/oss/python/langgraph/add-memory), [human-in-the-loop](/oss/python/langgraph/interrupts), and [streaming](/oss/python/langgraph/streaming) — to your applications with minimal changes to your existing code.

<Tip>
  For conceptual information on the functional API, see [Functional API](/oss/python/langgraph/functional-api).
</Tip>

## Creating a simple workflow

When defining an `entrypoint`, input is restricted to the first argument of the function. To pass multiple inputs, you can use a dictionary.

<Accordion title="Extended example: simple workflow">
  
</Accordion>

<Accordion title="Extended example: Compose an essay with an LLM">
  This example demonstrates how to use the `@task` and `@entrypoint` decorators
  syntactically. Given that a checkpointer is provided, the workflow results will
  be persisted in the checkpointer.

## Parallel execution

Tasks can be executed in parallel by invoking them concurrently and waiting for the results. This is useful for improving performance in IO bound tasks (e.g., calling APIs for LLMs).

<Accordion title="Extended example: parallel LLM calls">
  This example demonstrates how to run multiple LLM calls in parallel using `@task`. Each call generates a paragraph on a different topic, and results are joined into a single text output.

This example uses LangGraph's concurrency model to improve execution time, especially when tasks involve I/O like LLM completions.
</Accordion>

The **Functional API** and the [**Graph API**](/oss/python/langgraph/graph-api) can be used together in the same application as they share the same underlying runtime.

<Accordion title="Extended example: calling a simple graph from the functional API">
  
</Accordion>

## Call other entrypoints

You can call other **entrypoints** from within an **entrypoint** or a **task**.

<Accordion title="Extended example: calling another entrypoint">
  
</Accordion>

The **Functional API** uses the same streaming mechanism as the **Graph API**. Please
read the [**streaming guide**](/oss/python/langgraph/streaming) section for more details.

Example of using the streaming API to stream both updates and custom data.

1. Import [`get_stream_writer`](https://reference.langchain.com/python/langgraph/config/#langgraph.config.get_stream_writer) from `langgraph.config`.
2. Obtain a stream writer instance within the entrypoint.
3. Emit custom data before computation begins.
4. Emit another custom message after computing the result.
5. Use `.stream()` to process streamed output.
6. Specify which streaming modes to use.

<Warning>
  **Async with Python \< 3.11**
  If using Python \< 3.11 and writing async code, using [`get_stream_writer`](https://reference.langchain.com/python/langgraph/config/#langgraph.config.get_stream_writer) will not work. Instead please
  use the `StreamWriter` class directly. See [Async with Python \< 3.11](/oss/python/langgraph/streaming#async) for more details.

```python  theme={null}
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.types import RetryPolicy

**Examples:**

Example 1 (unknown):
```unknown
<Accordion title="Extended example: simple workflow">
```

Example 2 (unknown):
```unknown
</Accordion>

<Accordion title="Extended example: Compose an essay with an LLM">
  This example demonstrates how to use the `@task` and `@entrypoint` decorators
  syntactically. Given that a checkpointer is provided, the workflow results will
  be persisted in the checkpointer.
```

Example 3 (unknown):
```unknown
</Accordion>

## Parallel execution

Tasks can be executed in parallel by invoking them concurrently and waiting for the results. This is useful for improving performance in IO bound tasks (e.g., calling APIs for LLMs).
```

Example 4 (unknown):
```unknown
<Accordion title="Extended example: parallel LLM calls">
  This example demonstrates how to run multiple LLM calls in parallel using `@task`. Each call generates a paragraph on a different topic, and results are joined into a single text output.
```

---

## Streaming API

**URL:** llms-txt#streaming-api

**Contents:**
- Basic usage
  - Supported stream modes
  - Stream multiple modes
- Stream graph state
  - Stream Mode: `updates`
  - Stream Mode: `values`
- Subgraphs
- Debugging
- LLM tokens
  - Filter LLM tokens

Source: https://docs.langchain.com/langsmith/streaming

[LangGraph SDK](/langsmith/langgraph-python-sdk) allows you to [stream outputs](/oss/python/langgraph/streaming/) from the [LangSmith Deployment API](/langsmith/server-api-ref).

<Note>
  LangGraph SDK and Agent Server are a part of [LangSmith](/langsmith/home).
</Note>

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="JavaScript">
    
  </Tab>

<Tab title="cURL">
    Create a thread:

Create a streaming run:

<Accordion title="Extended example: streaming updates">
  This is an example graph you can run in the Agent Server.
  See [LangSmith quickstart](/langsmith/deployment-quickstart) for more details.

Once you have a running Agent Server, you can interact with it using
  [LangGraph SDK](/langsmith/langgraph-python-sdk)

<Tabs>
    <Tab title="Python">

1. The `client.runs.stream()` method returns an iterator that yields streamed outputs.
         2\. Set `stream_mode="updates"` to stream only the updates to the graph state after each node. Other stream modes are also available. See [supported stream modes](#supported-stream-modes) for details.
    </Tab>

<Tab title="JavaScript">

1. The `client.runs.stream()` method returns an iterator that yields streamed outputs.
      2. Set `streamMode: "updates"` to stream only the updates to the graph state after each node. Other stream modes are also available. See [supported stream modes](#supported-stream-modes) for details.
    </Tab>

<Tab title="cURL">
      Create a thread:

Create a streaming run:

### Supported stream modes

| Mode                             | Description                                                                                                                                                                         | LangGraph Library Method                                                                                      |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| [`values`](#stream-graph-state)  | Stream the full graph state after each [super-step](/langsmith/graph-rebuild#graphs).                                                                                               | `.stream()` / `.astream()` with [`stream_mode="values"`](/oss/python/langgraph/streaming#stream-graph-state)  |
| [`updates`](#stream-graph-state) | Streams the updates to the state after each step of the graph. If multiple updates are made in the same step (e.g., multiple nodes are run), those updates are streamed separately. | `.stream()` / `.astream()` with [`stream_mode="updates"`](/oss/python/langgraph/streaming#stream-graph-state) |
| [`messages-tuple`](#messages)    | Streams LLM tokens and metadata for the graph node where the LLM is invoked (useful for chat apps).                                                                                 | `.stream()` / `.astream()` with [`stream_mode="messages"`](/oss/python/langgraph/streaming#messages)          |
| [`debug`](#debug)                | Streams as much information as possible throughout the execution of the graph.                                                                                                      | `.stream()` / `.astream()` with [`stream_mode="debug"`](/oss/python/langgraph/streaming#stream-graph-state)   |
| [`custom`](#stream-custom-data)  | Streams custom data from inside your graph                                                                                                                                          | `.stream()` / `.astream()` with [`stream_mode="custom"`](/oss/python/langgraph/streaming#stream-custom-data)  |
| [`events`](#stream-events)       | Stream all events (including the state of the graph); mainly useful when migrating large LCEL apps.                                                                                 | `.astream_events()`                                                                                           |

### Stream multiple modes

You can pass a list as the `stream_mode` parameter to stream multiple modes at once.

The streamed outputs will be tuples of `(mode, chunk)` where `mode` is the name of the stream mode and `chunk` is the data streamed by that mode.

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="JavaScript">
    
  </Tab>

<Tab title="cURL">
    
  </Tab>
</Tabs>

## Stream graph state

Use the stream modes `updates` and `values` to stream the state of the graph as it executes.

* `updates` streams the **updates** to the state after each step of the graph.
* `values` streams the **full value** of the state after each step of the graph.

<Accordion title="Example graph">
  
</Accordion>

<Note>
  **Stateful runs**
  Examples below assume that you want to **persist the outputs** of a streaming run in the [checkpointer](/oss/python/langgraph/persistence) DB and have created a thread. To create a thread:

<Tabs>
    <Tab title="Python">
      
    </Tab>

<Tab title="JavaScript">
      
    </Tab>

<Tab title="cURL">
      
    </Tab>
  </Tabs>

If you don't need to persist the outputs of a run, you can pass `None` instead of `thread_id` when streaming.
</Note>

### Stream Mode: `updates`

Use this to stream only the **state updates** returned by the nodes after each step. The streamed outputs include the name of the node as well as the update.

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="JavaScript">
    
  </Tab>

<Tab title="cURL">
    
  </Tab>
</Tabs>

### Stream Mode: `values`

Use this to stream the **full state** of the graph after each step.

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="JavaScript">
    
  </Tab>

<Tab title="cURL">
    
  </Tab>
</Tabs>

To include outputs from [subgraphs](/oss/python/langgraph/use-subgraphs) in the streamed outputs, you can set `subgraphs=True` in the `.stream()` method of the parent graph. This will stream outputs from both the parent graph and any subgraphs.

1. Set `stream_subgraphs=True` to stream outputs from subgraphs.

<Accordion title="Extended example: streaming from subgraphs">
  This is an example graph you can run in the Agent Server.
  See [LangSmith quickstart](/langsmith/deployment-quickstart) for more details.

Once you have a running Agent Server, you can interact with it using
  [LangGraph SDK](/langsmith/langgraph-python-sdk)

<Tabs>
    <Tab title="Python">

1. Set `stream_subgraphs=True` to stream outputs from subgraphs.
    </Tab>

<Tab title="JavaScript">

1. Set `streamSubgraphs: true` to stream outputs from subgraphs.
    </Tab>

<Tab title="cURL">
      Create a thread:

Create a streaming run:

**Note** that we are receiving not just the node updates, but we also the namespaces which tell us what graph (or subgraph) we are streaming from.
</Accordion>

Use the `debug` streaming mode to stream as much information as possible throughout the execution of the graph. The streamed outputs include the name of the node as well as the full state.

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="JavaScript">
    
  </Tab>

<Tab title="cURL">
    
  </Tab>
</Tabs>

Use the `messages-tuple` streaming mode to stream Large Language Model (LLM) outputs **token by token** from any part of your graph, including nodes, tools, subgraphs, or tasks.

The streamed output from [`messages-tuple` mode](#supported-stream-modes) is a tuple `(message_chunk, metadata)` where:

* `message_chunk`: the token or message segment from the LLM.
* `metadata`: a dictionary containing details about the graph node and LLM invocation.

<Accordion title="Example graph">

1. Note that the message events are emitted even when the LLM is run using `invoke` rather than `stream`.
</Accordion>

<Tabs>
  <Tab title="Python">

1. The "messages-tuple" stream mode returns an iterator of tuples `(message_chunk, metadata)` where `message_chunk` is the token streamed by the LLM and `metadata` is a dictionary with information about the graph node where the LLM was called and other information.
  </Tab>

<Tab title="JavaScript">

1. The "messages-tuple" stream mode returns an iterator of tuples `(message_chunk, metadata)` where `message_chunk` is the token streamed by the LLM and `metadata` is a dictionary with information about the graph node where the LLM was called and other information.
  </Tab>

<Tab title="cURL">
    
  </Tab>
</Tabs>

### Filter LLM tokens

* To filter the streamed tokens by LLM invocation, you can [associate `tags` with LLM invocations](/oss/python/langgraph/streaming#filter-by-llm-invocation).
* To stream tokens only from specific nodes, use `stream_mode="messages"` and [filter the outputs by the `langgraph_node` field](/oss/python/langgraph/streaming#filter-by-node) in the streamed metadata.

## Stream custom data

To send **custom user-defined data**:

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="JavaScript">
    
  </Tab>

<Tab title="cURL">
    
  </Tab>
</Tabs>

To stream all events, including the state of the graph:

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="JavaScript">
    
  </Tab>

<Tab title="cURL">
    
  </Tab>
</Tabs>

If you don't want to **persist the outputs** of a streaming run in the [checkpointer](/oss/python/langgraph/persistence) DB, you can create a stateless run without creating a thread:

<Tabs>
  <Tab title="Python">

1. We are passing `None` instead of a `thread_id` UUID.
  </Tab>

<Tab title="JavaScript">

1. We are passing `None` instead of a `thread_id` UUID.
  </Tab>

<Tab title="cURL">
    
  </Tab>
</Tabs>

LangSmith allows you to join an active [background run](/langsmith/background-run) and stream outputs from it. To do so, you can use [LangGraph SDK's](/langsmith/langgraph-python-sdk) `client.runs.join_stream` method:

<Tabs>
  <Tab title="Python">

1. This is the `run_id` of an existing run you want to join.
  </Tab>

<Tab title="JavaScript">

1. This is the `run_id` of an existing run you want to join.
  </Tab>

<Tab title="cURL">
    
  </Tab>
</Tabs>

<Warning>
  **Outputs not buffered**
  When you use `.join_stream`, output is not buffered, so any output produced before joining will not be received.
</Warning>

For API usage and implementation, refer to the [API reference](https://langchain-ai.github.io/langgraph/cloud/reference/api/api_ref.html#tag/thread-runs/POST/threads/\{thread_id}/runs/stream).

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/streaming.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
</Tab>

  <Tab title="JavaScript">
```

Example 2 (unknown):
```unknown
</Tab>

  <Tab title="cURL">
    Create a thread:
```

Example 3 (unknown):
```unknown
Create a streaming run:
```

Example 4 (unknown):
```unknown
</Tab>
</Tabs>

<Accordion title="Extended example: streaming updates">
  This is an example graph you can run in the Agent Server.
  See [LangSmith quickstart](/langsmith/deployment-quickstart) for more details.
```

---

## Check what was interrupted

**URL:** llms-txt#check-what-was-interrupted

---

## Interrupts

**URL:** llms-txt#interrupts

**Contents:**
- Pause using `interrupt`
- Resuming interrupts

Source: https://docs.langchain.com/oss/python/langgraph/interrupts

Interrupts allow you to pause graph execution at specific points and wait for external input before continuing. This enables human-in-the-loop patterns where you need external input to proceed. When an interrupt is triggered, LangGraph saves the graph state using its [persistence](/oss/python/langgraph/persistence) layer and waits indefinitely until you resume execution.

Interrupts work by calling the `interrupt()` function at any point in your graph nodes. The function accepts any JSON-serializable value which is surfaced to the caller. When you're ready to continue, you resume execution by re-invoking the graph using `Command`, which then becomes the return value of the `interrupt()` call from inside the node.

Unlike static breakpoints (which pause before or after specific nodes), interrupts are **dynamic**—they can be placed anywhere in your code and can be conditional based on your application logic.

* **Checkpointing keeps your place:** the checkpointer writes the exact graph state so you can resume later, even when in an error state.
* **`thread_id` is your pointer:** set `config={"configurable": {"thread_id": ...}}` to tell the checkpointer which state to load.
* **Interrupt payloads surface as `__interrupt__`:** the values you pass to `interrupt()` return to the caller in the `__interrupt__` field so you know what the graph is waiting on.

The `thread_id` you choose is effectively your persistent cursor. Reusing it resumes the same checkpoint; using a new value starts a brand-new thread with an empty state.

## Pause using `interrupt`

The [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) function pauses graph execution and returns a value to the caller. When you call [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) within a node, LangGraph saves the current graph state and waits for you to resume execution with input.

To use [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt), you need:

1. A **checkpointer** to persist the graph state (use a durable checkpointer in production)
2. A **thread ID** in your config so the runtime knows which state to resume from
3. To call `interrupt()` where you want to pause (payload must be JSON-serializable)

When you call [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt), here's what happens:

1. **Graph execution gets suspended** at the exact point where [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) is called
2. **State is saved** using the checkpointer so execution can be resumed later, In production, this should be a persistent checkpointer (e.g. backed by a database)
3. **Value is returned** to the caller under `__interrupt__`; it can be any JSON-serializable value (string, object, array, etc.)
4. **Graph waits indefinitely** until you resume execution with a response
5. **Response is passed back** into the node when you resume, becoming the return value of the `interrupt()` call

## Resuming interrupts

After an interrupt pauses execution, you resume the graph by invoking it again with a `Command` that contains the resume value. The resume value is passed back to the `interrupt` call, allowing the node to continue execution with the external input.

```python  theme={null}
from langgraph.types import Command

**Examples:**

Example 1 (unknown):
```unknown
When you call [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt), here's what happens:

1. **Graph execution gets suspended** at the exact point where [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) is called
2. **State is saved** using the checkpointer so execution can be resumed later, In production, this should be a persistent checkpointer (e.g. backed by a database)
3. **Value is returned** to the caller under `__interrupt__`; it can be any JSON-serializable value (string, object, array, etc.)
4. **Graph waits indefinitely** until you resume execution with a response
5. **Response is passed back** into the node when you resume, becoming the return value of the `interrupt()` call

## Resuming interrupts

After an interrupt pauses execution, you resume the graph by invoking it again with a `Command` that contains the resume value. The resume value is passed back to the `interrupt` call, allowing the node to continue execution with the external input.
```

---

## Initial run - hits the interrupt and pauses

**URL:** llms-txt#initial-run---hits-the-interrupt-and-pauses

---

## Human-in-the-loop

**URL:** llms-txt#human-in-the-loop

**Contents:**
- Interrupt decision types
- Configuring interrupts
- Responding to interrupts

Source: https://docs.langchain.com/oss/python/langchain/human-in-the-loop

The Human-in-the-Loop (HITL) middleware lets you add human oversight to agent tool calls.
When a model proposes an action that might require review — for example, writing to a file or executing SQL — the middleware can pause execution and wait for a decision.

It does this by checking each tool call against a configurable policy. If intervention is needed, the middleware issues an [interrupt](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) that halts execution. The graph state is saved using LangGraph’s [persistence layer](/oss/python/langgraph/persistence), so execution can pause safely and resume later.

A human decision then determines what happens next: the action can be approved as-is (`approve`), modified before running (`edit`), or rejected with feedback (`reject`).

## Interrupt decision types

The middleware defines three built-in ways a human can respond to an interrupt:

| Decision Type | Description                                                               | Example Use Case                                    |
| ------------- | ------------------------------------------------------------------------- | --------------------------------------------------- |
| ✅ `approve`   | The action is approved as-is and executed without changes.                | Send an email draft exactly as written              |
| ✏️ `edit`     | The tool call is executed with modifications.                             | Change the recipient before sending an email        |
| ❌ `reject`    | The tool call is rejected, with an explanation added to the conversation. | Reject an email draft and explain how to rewrite it |

The available decision types for each tool depend on the policy you configure in `interrupt_on`.
When multiple tool calls are paused at the same time, each action requires a separate decision.
Decisions must be provided in the same order as the actions appear in the interrupt request.

<Tip>
  When **editing** tool arguments, make changes conservatively. Significant modifications to the original arguments may cause the model to re-evaluate its approach and potentially execute the tool multiple times or take unexpected actions.
</Tip>

## Configuring interrupts

To use HITL, add the middleware to the agent’s `middleware` list when creating the agent.

You configure it with a mapping of tool actions to the decision types that are allowed for each action. The middleware will interrupt execution when a tool call matches an action in the mapping.

<Info>
  You must configure a checkpointer to persist the graph state across interrupts.
  In production, use a persistent checkpointer like [`AsyncPostgresSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver). For testing or prototyping, use [`InMemorySaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.memory.InMemorySaver).

When invoking the agent, pass a `config` that includes the **thread ID** to associate execution with a conversation thread.
  See the [LangGraph interrupts documentation](/oss/python/langgraph/interrupts) for details.
</Info>

## Responding to interrupts

When you invoke the agent, it runs until it either completes or an interrupt is raised. An interrupt is triggered when a tool call matches the policy you configured in `interrupt_on`. In that case, the invocation result will include an `__interrupt__` field with the actions that require review. You can then present those actions to a reviewer and resume execution once decisions are provided.

```python  theme={null}
from langgraph.types import Command

**Examples:**

Example 1 (unknown):
```unknown
<Info>
  You must configure a checkpointer to persist the graph state across interrupts.
  In production, use a persistent checkpointer like [`AsyncPostgresSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver). For testing or prototyping, use [`InMemorySaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.memory.InMemorySaver).

  When invoking the agent, pass a `config` that includes the **thread ID** to associate execution with a conversation thread.
  See the [LangGraph interrupts documentation](/oss/python/langgraph/interrupts) for details.
</Info>

## Responding to interrupts

When you invoke the agent, it runs until it either completes or an interrupt is raised. An interrupt is triggered when a tool call matches the policy you configured in `interrupt_on`. In that case, the invocation result will include an `__interrupt__` field with the actions that require review. You can then present those actions to a reviewer and resume execution once decisions are provided.
```

---

## Check if execution was interrupted

**URL:** llms-txt#check-if-execution-was-interrupted

if result.get("__interrupt__"):
    # Extract interrupt information
    interrupts = result["__interrupt__"][0].value
    action_requests = interrupts["action_requests"]
    review_configs = interrupts["review_configs"]

# Create a lookup map from tool name to review config
    config_map = {cfg["action_name"]: cfg for cfg in review_configs}

# Display the pending actions to the user
    for action in action_requests:
        review_config = config_map[action["name"]]
        print(f"Tool: {action['name']}")
        print(f"Arguments: {action['args']}")
        print(f"Allowed decisions: {review_config['allowed_decisions']}")

# Get user decisions (one per action_request, in order)
    decisions = [
        {"type": "approve"}  # User approved the deletion
    ]

# Resume execution with decisions
    result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config  # Must use the same config!
    )

---

## The interrupt contains the full HITL request with action_requests and review_configs

**URL:** llms-txt#the-interrupt-contains-the-full-hitl-request-with-action_requests-and-review_configs

print(result['__interrupt__'])

---

## __interrupt__ contains the payload that was passed to interrupt()

**URL:** llms-txt#__interrupt__-contains-the-payload-that-was-passed-to-interrupt()

print(result["__interrupt__"])

---

## The resume payload becomes the return value of interrupt() inside the node

**URL:** llms-txt#the-resume-payload-becomes-the-return-value-of-interrupt()-inside-the-node

**Contents:**
- Common patterns
  - Approve or reject

graph.invoke(Command(resume=True), config=config)
python  theme={null}
from typing import Literal
from langgraph.types import interrupt, Command

def approval_node(state: State) -> Command[Literal["proceed", "cancel"]]:
    # Pause execution; payload shows up under result["__interrupt__"]
    is_approved = interrupt({
        "question": "Do you want to proceed with this action?",
        "details": state["action_details"]
    })

# Route based on the response
    if is_approved:
        return Command(goto="proceed")  # Runs after the resume payload is provided
    else:
        return Command(goto="cancel")
python  theme={null}

**Examples:**

Example 1 (unknown):
```unknown
**Key points about resuming:**

* You must use the **same thread ID** when resuming that was used when the interrupt occurred
* The value passed to `Command(resume=...)` becomes the return value of the [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) call
* The node restarts from the beginning of the node where the [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) was called when resumed, so any code before the [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) runs again
* You can pass any JSON-serializable value as the resume value

## Common patterns

The key thing that interrupts unlock is the ability to pause execution and wait for external input. This is useful for a variety of use cases, including:

* <Icon icon="check-circle" /> [Approval workflows](#approve-or-reject): Pause before executing critical actions (API calls, database changes, financial transactions)
* <Icon icon="pencil" /> [Review and edit](#review-and-edit-state): Let humans review and modify LLM outputs or tool calls before continuing
* <Icon icon="wrench" /> [Interrupting tool calls](#interrupts-in-tools): Pause before executing tool calls to review and edit the tool call before execution
* <Icon icon="shield-check" /> [Validating human input](#validating-human-input): Pause before proceeding to the next step to validate human input

### Approve or reject

One of the most common uses of interrupts is to pause before a critical action and ask for approval. For example, you might want to ask a human to approve an API call, a database change, or any other important decision.
```

Example 2 (unknown):
```unknown
When you resume the graph, pass `true` to approve or `false` to reject:
```

---

## Functional API overview

**URL:** llms-txt#functional-api-overview

**Contents:**
- Functional API vs. Graph API
- Example
- Entrypoint
  - Definition
  - Injectable parameters
  - Executing
  - Resuming
  - Short-term memory
- Task
  - Definition

Source: https://docs.langchain.com/oss/python/langgraph/functional-api

The **Functional API** allows you to add LangGraph's key features — [persistence](/oss/python/langgraph/persistence), [memory](/oss/python/langgraph/add-memory), [human-in-the-loop](/oss/python/langgraph/interrupts), and [streaming](/oss/python/langgraph/streaming) — to your applications with minimal changes to your existing code.

It is designed to integrate these features into existing code that may use standard language primitives for branching and control flow, such as `if` statements, `for` loops, and function calls. Unlike many data orchestration frameworks that require restructuring code into an explicit pipeline or DAG, the Functional API allows you to incorporate these capabilities without enforcing a rigid execution model.

The Functional API uses two key building blocks:

* **`@entrypoint`** – Marks a function as the starting point of a workflow, encapsulating logic and managing execution flow, including handling long-running tasks and interrupts.
* **[`@task`](https://reference.langchain.com/python/langgraph/func/#langgraph.func.task)** – Represents a discrete unit of work, such as an API call or data processing step, that can be executed asynchronously within an entrypoint. Tasks return a future-like object that can be awaited or resolved synchronously.

This provides a minimal abstraction for building workflows with state management and streaming.

<Tip>
  For information on how to use the functional API, see [Use Functional API](/oss/python/langgraph/use-functional-api).
</Tip>

## Functional API vs. Graph API

For users who prefer a more declarative approach, LangGraph's [Graph API](/oss/python/langgraph/graph-api) allows you to define workflows using a Graph paradigm. Both APIs share the same underlying runtime, so you can use them together in the same application.

Here are some key differences:

* **Control flow**: The Functional API does not require thinking about graph structure. You can use standard Python constructs to define workflows. This will usually trim the amount of code you need to write.
* **Short-term memory**: The **GraphAPI** requires declaring a [**State**](/oss/python/langgraph/graph-api#state) and may require defining [**reducers**](/oss/python/langgraph/graph-api#reducers) to manage updates to the graph state. `@entrypoint` and `@tasks` do not require explicit state management as their state is scoped to the function and is not shared across functions.
* **Checkpointing**: Both APIs generate and use checkpoints. In the **Graph API** a new checkpoint is generated after every [superstep](/oss/python/langgraph/graph-api). In the **Functional API**, when tasks are executed, their results are saved to an existing checkpoint associated with the given entrypoint instead of creating a new checkpoint.
* **Visualization**: The Graph API makes it easy to visualize the workflow as a graph which can be useful for debugging, understanding the workflow, and sharing with others. The Functional API does not support visualization as the graph is dynamically generated during runtime.

Below we demonstrate a simple application that writes an essay and [interrupts](/oss/python/langgraph/interrupts) to request human review.

<Accordion title="Detailed Explanation">
  This workflow will write an essay about the topic "cat" and then pause to get a review from a human. The workflow can be interrupted for an indefinite amount of time until a review is provided.

When the workflow is resumed, it executes from the very start, but because the result of the `writeEssay` task was already saved, the task result will be loaded from the checkpoint instead of being recomputed.

An essay has been written and is ready for review. Once the review is provided, we can resume the workflow:

The workflow has been completed and the review has been added to the essay.
</Accordion>

The [`@entrypoint`](https://reference.langchain.com/python/langgraph/func/#langgraph.func.entrypoint) decorator can be used to create a workflow from a function. It encapsulates workflow logic and manages execution flow, including handling *long-running tasks* and [interrupts](/oss/python/langgraph/interrupts).

An **entrypoint** is defined by decorating a function with the `@entrypoint` decorator.

The function **must accept a single positional argument**, which serves as the workflow input. If you need to pass multiple pieces of data, use a dictionary as the input type for the first argument.

Decorating a function with an `entrypoint` produces a [`Pregel`](https://reference.langchain.com/python/langgraph/pregel/#langgraph.pregel.Pregel.stream) instance which helps to manage the execution of the workflow (e.g., handles streaming, resumption, and checkpointing).

You will usually want to pass a **checkpointer** to the `@entrypoint` decorator to enable persistence and use features like **human-in-the-loop**.

<Tabs>
  <Tab title="Sync">
    
  </Tab>

<Tab title="Async">
    
  </Tab>
</Tabs>

<Warning>
  **Serialization**
  The **inputs** and **outputs** of entrypoints must be JSON-serializable to support checkpointing. Please see the [serialization](#serialization) section for more details.
</Warning>

### Injectable parameters

When declaring an `entrypoint`, you can request access to additional parameters that will be injected automatically at run time. These parameters include:

| Parameter    | Description                                                                                                                                                                 |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **previous** | Access the state associated with the previous `checkpoint` for the given thread. See [short-term-memory](#short-term-memory).                                               |
| **store**    | An instance of \[BaseStore]\[langgraph.store.base.BaseStore]. Useful for [long-term memory](/oss/python/langgraph/use-functional-api#long-term-memory).                     |
| **writer**   | Use to access the StreamWriter when working with Async Python \< 3.11. See [streaming with functional API for details](/oss/python/langgraph/use-functional-api#streaming). |
| **config**   | For accessing run time configuration. See [RunnableConfig](https://python.langchain.com/docs/concepts/runnables/#runnableconfig) for information.                           |

<Warning>
  Declare the parameters with the appropriate name and type annotation.
</Warning>

<Accordion title="Requesting Injectable Parameters">
  
</Accordion>

Using the [`@entrypoint`](#entrypoint) yields a [`Pregel`](https://reference.langchain.com/python/langgraph/pregel/#langgraph.pregel.Pregel.stream) object that can be executed using the `invoke`, `ainvoke`, `stream`, and `astream` methods.

<Tabs>
  <Tab title="Invoke">
    
  </Tab>

<Tab title="Async Invoke">
    
  </Tab>

<Tab title="Stream">
    
  </Tab>

<Tab title="Async Stream">
    
  </Tab>
</Tabs>

Resuming an execution after an [interrupt](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) can be done by passing a **resume** value to the [`Command`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.Command) primitive.

<Tabs>
  <Tab title="Invoke">
    
  </Tab>

<Tab title="Async Invoke">
    
  </Tab>

<Tab title="Stream">
    
  </Tab>

<Tab title="Async Stream">
    
  </Tab>
</Tabs>

**Resuming after an error**

To resume after an error, run the `entrypoint` with a `None` and the same **thread id** (config).

This assumes that the underlying **error** has been resolved and execution can proceed successfully.

<Tabs>
  <Tab title="Invoke">
    
  </Tab>

<Tab title="Async Invoke">
    
  </Tab>

<Tab title="Stream">
    
  </Tab>

<Tab title="Async Stream">
    
  </Tab>
</Tabs>

### Short-term memory

When an `entrypoint` is defined with a `checkpointer`, it stores information between successive invocations on the same **thread id** in [checkpoints](/oss/python/langgraph/persistence#checkpoints).

This allows accessing the state from the previous invocation using the `previous` parameter.

By default, the `previous` parameter is the return value of the previous invocation.

#### `entrypoint.final`

[`entrypoint.final`](https://reference.langchain.com/python/langgraph/func/#langgraph.func.entrypoint.final) is a special primitive that can be returned from an entrypoint and allows **decoupling** the value that is **saved in the checkpoint** from the **return value of the entrypoint**.

The first value is the return value of the entrypoint, and the second value is the value that will be saved in the checkpoint. The type annotation is `entrypoint.final[return_type, save_type]`.

A **task** represents a discrete unit of work, such as an API call or data processing step. It has two key characteristics:

* **Asynchronous Execution**: Tasks are designed to be executed asynchronously, allowing multiple operations to run concurrently without blocking.
* **Checkpointing**: Task results are saved to a checkpoint, enabling resumption of the workflow from the last saved state. (See [persistence](/oss/python/langgraph/persistence) for more details).

Tasks are defined using the `@task` decorator, which wraps a regular Python function.

<Warning>
  **Serialization**
  The **outputs** of tasks must be JSON-serializable to support checkpointing.
</Warning>

**Tasks** can only be called from within an **entrypoint**, another **task**, or a [state graph node](/oss/python/langgraph/graph-api#nodes).

Tasks *cannot* be called directly from the main application code.

When you call a **task**, it returns *immediately* with a future object. A future is a placeholder for a result that will be available later.

To obtain the result of a **task**, you can either wait for it synchronously (using `result()`) or await it asynchronously (using `await`).

<Tabs>
  <Tab title="Synchronous Invocation">
    
  </Tab>

<Tab title="Asynchronous Invocation">
    
  </Tab>
</Tabs>

## When to use a task

**Tasks** are useful in the following scenarios:

* **Checkpointing**: When you need to save the result of a long-running operation to a checkpoint, so you don't need to recompute it when resuming the workflow.
* **Human-in-the-loop**: If you're building a workflow that requires human intervention, you MUST use **tasks** to encapsulate any randomness (e.g., API calls) to ensure that the workflow can be resumed correctly. See the [determinism](#determinism) section for more details.
* **Parallel Execution**: For I/O-bound tasks, **tasks** enable parallel execution, allowing multiple operations to run concurrently without blocking (e.g., calling multiple APIs).
* **Observability**: Wrapping operations in **tasks** provides a way to track the progress of the workflow and monitor the execution of individual operations using [LangSmith](https://docs.smith.langchain.com/).
* **Retryable Work**: When work needs to be retried to handle failures or inconsistencies, **tasks** provide a way to encapsulate and manage the retry logic.

There are two key aspects to serialization in LangGraph:

1. `entrypoint` inputs and outputs must be JSON-serializable.
2. `task` outputs must be JSON-serializable.

These requirements are necessary for enabling checkpointing and workflow resumption. Use python primitives like dictionaries, lists, strings, numbers, and booleans to ensure that your inputs and outputs are serializable.

Serialization ensures that workflow state, such as task results and intermediate values, can be reliably saved and restored. This is critical for enabling human-in-the-loop interactions, fault tolerance, and parallel execution.

Providing non-serializable inputs or outputs will result in a runtime error when a workflow is configured with a checkpointer.

To utilize features like **human-in-the-loop**, any randomness should be encapsulated inside of **tasks**. This guarantees that when execution is halted (e.g., for human in the loop) and then resumed, it will follow the same *sequence of steps*, even if **task** results are non-deterministic.

LangGraph achieves this behavior by persisting **task** and [**subgraph**](/oss/python/langgraph/use-subgraphs) results as they execute. A well-designed workflow ensures that resuming execution follows the *same sequence of steps*, allowing previously computed results to be retrieved correctly without having to re-execute them. This is particularly useful for long-running **tasks** or **tasks** with non-deterministic results, as it avoids repeating previously done work and allows resuming from essentially the same.

While different runs of a workflow can produce different results, resuming a **specific** run should always follow the same sequence of recorded steps. This allows LangGraph to efficiently look up **task** and **subgraph** results that were executed prior to the graph being interrupted and avoid recomputing them.

Idempotency ensures that running the same operation multiple times produces the same result. This helps prevent duplicate API calls and redundant processing if a step is rerun due to a failure. Always place API calls inside **tasks** functions for checkpointing, and design them to be idempotent in case of re-execution. Re-execution can occur if a **task** starts, but does not complete successfully. Then, if the workflow is resumed, the **task** will run again. Use idempotency keys or verify existing results to avoid duplication.

### Handling side effects

Encapsulate side effects (e.g., writing to a file, sending an email) in tasks to ensure they are not executed multiple times when resuming a workflow.

<Tabs>
  <Tab title="Incorrect">
    In this example, a side effect (writing to a file) is directly included in the workflow, so it will be executed a second time when resuming the workflow.

<Tab title="Correct">
    In this example, the side effect is encapsulated in a task, ensuring consistent execution upon resumption.

### Non-deterministic control flow

Operations that might give different results each time (like getting current time or random numbers) should be encapsulated in tasks to ensure that on resume, the same result is returned.

* In a task: Get random number (5) → interrupt → resume → (returns 5 again) → ...
* Not in a task: Get random number (5) → interrupt → resume → get new random number (7) → ...

This is especially important when using **human-in-the-loop** workflows with multiple interrupts calls. LangGraph keeps a list of resume values for each task/entrypoint. When an interrupt is encountered, it's matched with the corresponding resume value. This matching is strictly **index-based**, so the order of the resume values should match the order of the interrupts.

If order of execution is not maintained when resuming, one [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) call may be matched with the wrong `resume` value, leading to incorrect results.

Please read the section on [determinism](#determinism) for more details.

<Tabs>
  <Tab title="Incorrect">
    In this example, the workflow uses the current time to determine which task to execute. This is non-deterministic because the result of the workflow depends on the time at which it is executed.

<Tab title="Correct">
    In this example, the workflow uses the input `t0` to determine which task to execute. This is deterministic because the result of the workflow depends only on the input.

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/langgraph/functional-api.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
<Accordion title="Detailed Explanation">
  This workflow will write an essay about the topic "cat" and then pause to get a review from a human. The workflow can be interrupted for an indefinite amount of time until a review is provided.

  When the workflow is resumed, it executes from the very start, but because the result of the `writeEssay` task was already saved, the task result will be loaded from the checkpoint instead of being recomputed.
```

Example 2 (unknown):
```unknown
An essay has been written and is ready for review. Once the review is provided, we can resume the workflow:
```

Example 3 (unknown):
```unknown

```

Example 4 (unknown):
```unknown
The workflow has been completed and the review has been added to the essay.
</Accordion>

## Entrypoint

The [`@entrypoint`](https://reference.langchain.com/python/langgraph/func/#langgraph.func.entrypoint) decorator can be used to create a workflow from a function. It encapsulates workflow logic and manages execution flow, including handling *long-running tasks* and [interrupts](/oss/python/langgraph/interrupts).

### Definition

An **entrypoint** is defined by decorating a function with the `@entrypoint` decorator.

The function **must accept a single positional argument**, which serves as the workflow input. If you need to pass multiple pieces of data, use a dictionary as the input type for the first argument.

Decorating a function with an `entrypoint` produces a [`Pregel`](https://reference.langchain.com/python/langgraph/pregel/#langgraph.pregel.Pregel.stream) instance which helps to manage the execution of the workflow (e.g., handles streaming, resumption, and checkpointing).

You will usually want to pass a **checkpointer** to the `@entrypoint` decorator to enable persistence and use features like **human-in-the-loop**.

<Tabs>
  <Tab title="Sync">
```

---
