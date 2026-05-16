# Langgraph - Graphs

**Pages:** 115

---

## Add custom authentication

**URL:** llms-txt#add-custom-authentication

**Contents:**
- Add custom authentication to your deployment
- Enable agent authentication
  - Authorizing a user for Studio

Source: https://docs.langchain.com/langsmith/custom-auth

This guide shows you how to add custom authentication to your LangSmith application. The steps on this page apply to both [cloud](/langsmith/cloud) and [self-hosted](/langsmith/self-hosted) deployments. It does not apply to isolated usage of the [LangGraph open source library](/oss/python/langgraph/overview) in your own custom server.

## Add custom authentication to your deployment

To leverage custom authentication and access user-level metadata in your deployments, set up custom authentication to automatically populate the `config["configurable"]["langgraph_auth_user"]` object through a custom authentication handler. You can then access this object in your graph with the `langgraph_auth_user` key to [allow an agent to perform authenticated actions on behalf of the user](#enable-agent-authentication).

1. Implement authentication:

<Note>
     Without a custom `@auth.authenticate` handler, LangGraph sees only the API-key owner (usually the developer), so requests aren’t scoped to individual end-users. To propagate custom tokens, you must implement your own handler.
   </Note>

* This handler receives the request (headers, etc.), validates the user, and returns a dictionary with at least an identity field.
* You can add any custom fields you want (e.g., OAuth tokens, roles, org IDs, etc.).

2. In your [`langgraph.json`](/langsmith/application-structure#configuration-file), add the path to your auth file:

3. Once you've set up authentication in your server, requests must include the required authorization information based on your chosen scheme. Assuming you are using JWT token authentication, you could access your deployments using any of the following methods:

<Tabs>
     <Tab title="Python Client">
       
     </Tab>

<Tab title="Python RemoteGraph">
       
     </Tab>

<Tab title="JavaScript Client">
       
     </Tab>

<Tab title="JavaScript RemoteGraph">
       
     </Tab>

<Tab title="CURL">
       
     </Tab>
   </Tabs>

For more details on RemoteGraph, refer to the [Use RemoteGraph](/langsmith/use-remote-graph) guide.

## Enable agent authentication

After [authentication](#add-custom-authentication-to-your-deployment), the platform creates a special configuration object (`config`) that is passed to LangSmith deployment. This object contains information about the current user, including any custom fields you return from your `@auth.authenticate` handler.

To allow an agent to perform authenticated actions on behalf of the user, access this object in your graph with the `langgraph_auth_user` key:

<Note>
  Fetch user credentials from a secure secret store. Storing secrets in graph state is not recommended.
</Note>

### Authorizing a user for Studio

By default, if you add custom authorization on your resources, this will also apply to interactions made from [Studio](/langsmith/studio). If you want, you can handle logged-in Studio users differently by checking [is\_studio\_user()](https://langchain-ai.github.io/langgraph/cloud/reference/sdk/python_sdk_ref/#langgraph_sdk.auth.types.StudioUser).

<Note>
  `is_studio_user` was added in version 0.1.73 of the langgraph-sdk. If you're on an older version, you can still check whether `isinstance(ctx.user, StudioUser)`.
</Note>

```python  theme={null}
from langgraph_sdk.auth import is_studio_user, Auth
auth = Auth()

**Examples:**

Example 1 (unknown):
```unknown
* This handler receives the request (headers, etc.), validates the user, and returns a dictionary with at least an identity field.
* You can add any custom fields you want (e.g., OAuth tokens, roles, org IDs, etc.).

2. In your [`langgraph.json`](/langsmith/application-structure#configuration-file), add the path to your auth file:
```

Example 2 (unknown):
```unknown
3. Once you've set up authentication in your server, requests must include the required authorization information based on your chosen scheme. Assuming you are using JWT token authentication, you could access your deployments using any of the following methods:

   <Tabs>
     <Tab title="Python Client">
```

Example 3 (unknown):
```unknown
</Tab>

     <Tab title="Python RemoteGraph">
```

Example 4 (unknown):
```unknown
</Tab>

     <Tab title="JavaScript Client">
```

---

## Build the state graph

**URL:** llms-txt#build-the-state-graph

builder = StateGraph(OverallState)
builder.add_node(node)  # node_1 is the first node
builder.add_edge(START, "node")  # Start the graph with node_1
builder.add_edge("node", END)  # End the graph after node_1
graph = builder.compile()

---

## Build workflow

**URL:** llms-txt#build-workflow

orchestrator_worker_builder = StateGraph(State)

---

## Configure webhook notifications for LangSmith alerts

**URL:** llms-txt#configure-webhook-notifications-for-langsmith-alerts

**Contents:**
- Overview
- Prerequisites
- Integration Configuration
  - Step 1: Prepare Your Receiving Endpoint
  - Step 2: Configure Webhook Parameters
  - Step 3: Test the Webhook
- Troubleshooting
- Security Considerations
- Sending alerts to Slack using a webhook
  - Prerequisites

Source: https://docs.langchain.com/langsmith/alerts-webhook

This guide details the process for setting up webhook notifications for [LangSmith alerts](/langsmith/alerts). Before proceeding, make sure you have followed the steps leading up to the notification step of creating the alert by following [this guide](./alerts). Webhooks enable integration with custom services and third-party platforms by sending HTTP POST requests when alert conditions are triggered. Use webhooks to forward alert data to ticketing systems, chat applications, or custom monitoring solutions.

* An endpoint that can receive HTTP POST requests
* Appropriate authentication credentials for your receiving service (if required)

## Integration Configuration

### Step 1: Prepare Your Receiving Endpoint

Before configuring the webhook in LangSmith, ensure your receiving endpoint:

* Accepts HTTP POST requests
* Can process JSON payloads
* Is accessible from external services
* Has appropriate authentication mechanisms (if required)

Additionally, if on a custom deployment of LangSmith, make sure there are no firewall settings blocking egress traffic from LangSmith services.

### Step 2: Configure Webhook Parameters

<img src="https://mintcdn.com/langchain-5e9cc07a/1RIJxfRpkszanJLL/langsmith/images/webhook-setup.png?fit=max&auto=format&n=1RIJxfRpkszanJLL&q=85&s=fecb6275ad3d576a864d1c6a2771c847" alt="Webhook Setup" data-og-width="754" width="754" data-og-height="523" height="523" data-path="langsmith/images/webhook-setup.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/1RIJxfRpkszanJLL/langsmith/images/webhook-setup.png?w=280&fit=max&auto=format&n=1RIJxfRpkszanJLL&q=85&s=ef03d3ab887113e73dbdc1097076d103 280w, https://mintcdn.com/langchain-5e9cc07a/1RIJxfRpkszanJLL/langsmith/images/webhook-setup.png?w=560&fit=max&auto=format&n=1RIJxfRpkszanJLL&q=85&s=a25fcaedcbed92c9c3f2e2bddd8d88bd 560w, https://mintcdn.com/langchain-5e9cc07a/1RIJxfRpkszanJLL/langsmith/images/webhook-setup.png?w=840&fit=max&auto=format&n=1RIJxfRpkszanJLL&q=85&s=4785471ce1e58f3c48ce19b7be3889c5 840w, https://mintcdn.com/langchain-5e9cc07a/1RIJxfRpkszanJLL/langsmith/images/webhook-setup.png?w=1100&fit=max&auto=format&n=1RIJxfRpkszanJLL&q=85&s=8c7dd40aeb5635cdf4ddf207d0dfe7c7 1100w, https://mintcdn.com/langchain-5e9cc07a/1RIJxfRpkszanJLL/langsmith/images/webhook-setup.png?w=1650&fit=max&auto=format&n=1RIJxfRpkszanJLL&q=85&s=aff125529b9db8fbf861999e70bcdb26 1650w, https://mintcdn.com/langchain-5e9cc07a/1RIJxfRpkszanJLL/langsmith/images/webhook-setup.png?w=2500&fit=max&auto=format&n=1RIJxfRpkszanJLL&q=85&s=e9de7c4f0dcc440d734f4f3d09d2abf4 2500w" />

In the notification section of your alert complete the webhook configuration with the following parameters:

* **URL**: The complete URL of your receiving endpoint
  * Example: `https://api.example.com/incident-webhook`

* **Headers**: JSON Key-value pairs sent with the webhook request

* Common headers include:

* `Authorization`: For authentication tokens
    * `Content-Type`: Usually set to `application/json` (default)
    * `X-Source`: To identify the source as LangSmith

* If no headers, then simply use `{}`

* **Request Body Template**: Customize the JSON payload sent to your endpoint

* Default: LangSmith sends the payload defined and the following additonal key-value pairs appended to the payload:

* `project_name`: Name of the triggered alert
    * `alert_rule_id`: A UUID to identify the LangSmith alert. This can be used as a de-duplication key in the webhook service.
    * `alert_rule_name`: The name of the alert rule.
    * `alert_rule_type`: The type of alert (as of 04/01/2025 all alerts are of type `threshold`).
    * `alert_rule_attribute`: The attribute associated with the alert rule - `error_count`, `feedback_score` or `latency`.
    * `triggered_metric_value`: The value of the metric at the time the threshold was triggered.
    * `triggered_threshold`: The threshold that triggered the alert.
    * `timestamp`: The timestamp that triggered the alert.

### Step 3: Test the Webhook

Click **Send Test Alert** to send the webhook notification to ensure the notification works as intended.

If webhook notifications aren't being delivered:

* Verify the webhook URL is correct and accessible
* Ensure any authentication headers are properly formatted
* Check that your receiving endpoint accepts POST requests
* Examine your endpoint's logs for received but rejected requests
* Verify your custom payload template is valid JSON format

## Security Considerations

* Use HTTPS for your webhook endpoints
* Implement authentication for your webhook endpoint
* Consider adding a shared secret in your headers to verify webhook sources
* Validate incoming webhook requests before processing them

## Sending alerts to Slack using a webhook

Here is an example for configuring LangSmith alerts to send notifications to Slack channels using the [`chat.postMessage`](https://api.slack.com/methods/chat.postMessage) API.

* Access to a Slack workspace
* A LangSmith project to set up alerts
* Permissions to create Slack applications

### Step 1: Create a Slack App

1. Visit the [Slack API Applications page](https://api.slack.com/apps)
2. Click **Create New App**
3. Select **From scratch**
4. Provide an **App Name** (e.g., "LangSmith Alerts")
5. Select the workspace where you want to install the app
6. Click **Create App**

### Step 2: Configure Bot Permissions

1. In the left sidebar of your Slack app configuration, click **OAuth & Permissions**

2. Scroll down to **Bot Token Scopes** under **Scopes** and click **Add an OAuth Scope**

3. Add the following scopes:

* `chat:write` (Send messages as the app)
   * `chat:write.public` (Send messages to channels the app isn't in)
   * `channels:read` (View basic channel information)

### Step 3: Install the App to Your Workspace

1. Scroll up to the top of the **OAuth & Permissions** page
2. Click **Install to Workspace**
3. Review the permissions and click **Allow**
4. Copy the **Bot User OAuth Token** that appears (begins with `xoxb-`)

### Step 4: Configure the Webhook Alert in LangSmith

1. In LangSmith, navigate to your project
2. Select **Alerts → Create Alert**
3. Define your alert metrics and conditions
4. In the notification section, select **Webhook**
5. Configure the webhook with the following settings:

> **Note:** Replace `xoxb-your-token-here` with your actual Bot User OAuth Token

**Request Body Template**

**NOTE:** Fill in the `channel_id`, `alert_name`, `project_name` and `project_url` when creating the alert. You can find your `project_url` in the browser's URL bar. Copy the portion up to but not including any query parameters.

6. Click **Save** to activate the webhook configuration

### Step 5: Test the Integration

1. In the LangSmith alert configuration, click **Test Alert**
2. Check your specified Slack channel for the test notification
3. Verify that the message contains the expected alert information

### (Optional) Step 6: Link to the Alert Preview in the Request Body

After creating an alert, you can optionally link to its preview in the webhook's request body.

<img src="https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/alert-preview-pane.png?fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=286ebb8f90bafbdcacf9a0602aaf749c" alt="Alert Preview Pane" data-og-width="832" width="832" data-og-height="773" height="773" data-path="langsmith/images/alert-preview-pane.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/alert-preview-pane.png?w=280&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=20a409a30bff44a1a8bb1b79a6a2216b 280w, https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/alert-preview-pane.png?w=560&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=414bb4719617bd23452273c73327d601 560w, https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/alert-preview-pane.png?w=840&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=6bc7bc7aaee65f7f4afac42102047ad2 840w, https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/alert-preview-pane.png?w=1100&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=491244ac56f6f4bcbb64419b267df0fe 1100w, https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/alert-preview-pane.png?w=1650&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=d47f5ba127c3f61e3cb7498f8b7568fe 1650w, https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/alert-preview-pane.png?w=2500&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=6a70706db839b2d211024116ba19acef 2500w" />

1. Save your alert
2. Find your saved alert in the alerts table and click it
3. Copy the dsiplayed URL
4. Click "Edit Alert"
5. Replace the existing project URL with the copied alert preview URL

## Additional Resources

* [LangSmith Alerts Documentation](/langsmith/alerts)
* [Slack chat.postMessage API Documentation](https://api.slack.com/methods/chat.postMessage)
* [Slack Block Kit Builder](https://app.slack.com/block-kit-builder/)

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/alerts-webhook.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
**Headers**
```

Example 2 (unknown):
```unknown
> **Note:** Replace `xoxb-your-token-here` with your actual Bot User OAuth Token

**Request Body Template**
```

---

## Compile the workflow

**URL:** llms-txt#compile-the-workflow

orchestrator_worker = orchestrator_worker_builder.compile()

---

## Edges taken after the `action` node is called.

**URL:** llms-txt#edges-taken-after-the-`action`-node-is-called.

workflow.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    grade_documents,
)
workflow.add_edge("generate_answer", END)
workflow.add_edge("rewrite_question", "generate_query_or_respond")

---

## How to interact with a deployment using RemoteGraph

**URL:** llms-txt#how-to-interact-with-a-deployment-using-remotegraph

**Contents:**
- Prerequisites
- Initialize the graph
  - Use a URL
  - Use a client
- Invoke the graph
  - Asynchronously
  - Synchronously
- Persist state at the thread level
- Use as a subgraph

Source: https://docs.langchain.com/langsmith/use-remote-graph

[`RemoteGraph`](https://langchain-ai.github.io/langgraph/reference/remote_graph) is a client-side interface that allows you to interact with your [deployment](/langsmith/deployments) as if it were a local graph. It provides API parity with [`CompiledGraph`](/oss/python/langgraph/graph-api#compiling-your-graph), which means that you can use the same methods (`invoke()`, `stream()`, `get_state()`, etc.) in your development and production environments. This page describes how to initialize a `RemoteGraph` and interact with it.

`RemoteGraph` is useful for the following:

* Separation of development and deployment: Build and test a graph locally with `CompiledGraph`, deploy it to LangSmith, and then [use `RemoteGraph`](#initialize-the-graph) to call it in production while working with the same API interface.
* Thread-level persistence: [Persist and fetch the state](#persist-state-at-the-thread-level) of a conversation across calls with a thread ID.
* Subgraph embedding: Compose modular graphs for a multi-agent workflow by embedding a `RemoteGraph` as a [subgraph](#use-as-a-subgraph) within another graph.
* Reusable workflows: Use deployed graphs as nodes or [tools](https://langchain-ai.github.io/langgraph/reference/remote_graph/#langgraph.pregel.remote.RemoteGraph.as_tool), so that you can reuse and expose complex logic.

<Warning>
  **Important: Avoid calling the same deployment**

`RemoteGraph` is designed to call graphs on other deployments. Do not use `RemoteGraph` to call itself or another graph on the same deployment, as this can lead to deadlocks and resource exhaustion. Instead, use local graph composition or [subgraphs](/oss/python/langgraph/use-subgraphs) for graphs within the same deployment.
</Warning>

Before getting started with `RemoteGraph`, make sure you have:

* Access to [LangSmith](/langsmith/home), where your graphs are developed and managed.
* A running [Agent Server](/langsmith/agent-server), which hosts your deployed graphs for remote interaction.

## Initialize the graph

When initializing a `RemoteGraph`, you must always specify:

* `name`: The name of the graph you want to interact with **or** an assistant ID. If you specify a graph name, the default assistant will be used. If you specify an assistant ID, that specific assistant will be used. The graph name is the same name you use in the `langgraph.json` configuration file for your deployment.
* `api_key`: A valid [LangSmith API key](/langsmith/create-account-api-key). You can set as an environment variable (`LANGSMITH_API_KEY`) or pass directly in the `api_key` argument. You can also provide the API key in the `client` / `sync_client` arguments, if `LangGraphClient` / `SyncLangGraphClient` was initialized with the `api_key` argument.

Additionally, you have to provide one of the following:

* [`url`](#use-a-url): The URL of the deployment you want to interact with. If you pass the `url` argument, both sync and async clients will be created using the provided URL, headers (if provided), and default configuration values (e.g., timeout).
* [`client`](#use-a-client): A `LangGraphClient` instance for interacting with the deployment asynchronously (e.g., using `.astream()`, `.ainvoke()`, `.aget_state()`, `.aupdate_state()`).
* `sync_client`: A `SyncLangGraphClient` instance for interacting with the deployment synchronously (e.g., using `.stream()`, `.invoke()`, `.get_state()`, `.update_state()`).

<Note>
  If you pass both `client` or `sync_client` as well as the `url` argument, they will take precedence over the `url` argument. If none of the `client` / `sync_client` / `url` arguments are provided, `RemoteGraph` will raise a `ValueError` at runtime.
</Note>

`RemoteGraph` implements the same Runnable interface as `CompiledGraph`, so you can use it in the same way as a compiled graph. It supports the full set of standard methods, including `.invoke()`, `.stream()`, `.get_state()`, and `.update_state()`, as well as their asynchronous variants.

<Note>
  To use the graph asynchronously, you must provide either the `url` or `client` when initializing the `RemoteGraph`.
</Note>

<Note>
  To use the graph synchronously, you must provide either the `url` or `sync_client` when initializing the `RemoteGraph`.
</Note>

<CodeGroup>
  
</CodeGroup>

## Persist state at the thread level

By default, graph runs (for example, calls made with `.invoke()` or `.stream()`) are stateless, which means that intermediate checkpoints and the final state are not persisted after a run.

If you want to preserve the outputs of a run—for example, to support human-in-the-loop workflows—you can create a thread and pass its ID through the `config` argument. This works the same way as with a regular compiled graph:

<Note>
  If you need to use a `checkpointer` with a graph that has a `RemoteGraph` subgraph node, make sure to use UUIDs as thread IDs.
</Note>

A graph can also call out to multiple `RemoteGraph` instances as [*subgraph*](/oss/python/langgraph/use-subgraphs) nodes. This allows for modular, scalable workflows where different responsibilities are split across separate graphs.

`RemoteGraph` exposes the same interface as a regular `CompiledGraph`, so you can use it directly as a subgraph inside another graph. For example:

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/use-remote-graph.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
</CodeGroup>

### Use a client

<CodeGroup>
```

Example 3 (unknown):
```unknown

```

Example 4 (unknown):
```unknown
</CodeGroup>

## Invoke the graph

`RemoteGraph` implements the same Runnable interface as `CompiledGraph`, so you can use it in the same way as a compiled graph. It supports the full set of standard methods, including `.invoke()`, `.stream()`, `.get_state()`, and `.update_state()`, as well as their asynchronous variants.

### Asynchronously

<Note>
  To use the graph asynchronously, you must provide either the `url` or `client` when initializing the `RemoteGraph`.
</Note>

<CodeGroup>
```

---

## Dataset prebuilt JSON schema types

**URL:** llms-txt#dataset-prebuilt-json-schema-types

Source: https://docs.langchain.com/langsmith/dataset-json-types

LangSmith recommends that you set a schema on the inputs and outputs of your dataset schemas to ensure data consistency and that your examples are in the right format for downstream processing, like running evals.

In order to better support LLM workflows, LangSmith has support for a few different predefined prebuilt types. These schemas are hosted publicly by the LangSmith API, and can be defined in your dataset schemas using [JSON Schema references](https://json-schema.org/understanding-json-schema/structuring#dollarref). The table of available schemas can be seen below

| Type    | JSON Schema Reference Link                                                                                                       | Usage                                                                                                                     |
| ------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Message | [https://api.smith.langchain.com/public/schemas/v1/message.json](https://api.smith.langchain.com/public/schemas/v1/message.json) | Represents messages sent to a chat model, following the OpenAI standard format.                                           |
| Tool    | [https://api.smith.langchain.com/public/schemas/v1/tooldef.json](https://api.smith.langchain.com/public/schemas/v1/tooldef.json) | Tool definitions available to chat models for function calling, defined in OpenAI's JSON Schema inspired function format. |

LangSmith lets you define a series of transformations that collect the above prebuilt types from your traces and add them to your dataset. For more info on available transformations, see our [reference](/langsmith/dataset-transformations)

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/dataset-json-types.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## Target function for running the relevant step

**URL:** llms-txt#target-function-for-running-the-relevant-step

async def run_intent_classifier(inputs: dict) -> dict:
    # Note that we can access and run the intent_classifier node of our graph directly.
    command = await graph.nodes['intent_classifier'].ainvoke(inputs)
    return {"route": command.goto}

---

## Observability in Studio

**URL:** llms-txt#observability-in-studio

**Contents:**
- Iterate on prompts
  - Direct node editing
  - Graph configuration
  - Playground
- Run experiments over a dataset
  - Prerequisites
  - Experiment setup
- Debug LangSmith traces
  - Open deployed threads
  - Testing local agents with remote traces

Source: https://docs.langchain.com/langsmith/observability-studio

LangSmith [Studio](/langsmith/studio) provides tools to inspect, debug, and improve your app beyond execution. By working with traces, datasets, and prompts, you can see how your application behaves in detail, measure its performance, and refine its outputs:

* [Iterate on prompts](#iterate-on-prompts): Modify prompts inside graph nodes directly or with the LangSmith playground.
* [Run experiments over a dataset](#run-experiments-over-a-dataset): Execute your assistant over a LangSmith dataset to score and compare results.
* [Debug LangSmith traces](#debug-langsmith-traces): Import traced runs into Studio and optionally clone them into your local agent.
* [Add a node to a dataset](#add-node-to-dataset): Turn parts of thread history into dataset examples for evaluation or further analysis.

## Iterate on prompts

Studio supports the following methods for modifying prompts in your graph:

* [Direct node editing](#direct-node-editing)
* [Playground interface](#playground)

### Direct node editing

Studio allows you to edit prompts used inside individual nodes, directly from the graph interface.

### Graph configuration

Define your [configuration](/oss/python/langgraph/use-graph-api#add-runtime-configuration) to specify prompt fields and their associated nodes using `langgraph_nodes` and `langgraph_type` keys.

#### `langgraph_nodes`

* **Description**: Specifies which nodes of the graph a configuration field is associated with.
* **Value Type**: Array of strings, where each string is the name of a node in your graph.
* **Usage Context**: Include in the `json_schema_extra` dictionary for Pydantic models or the `metadata["json_schema_extra"]` dictionary for dataclasses.
* **Example**:

#### `langgraph_type`

* **Description**: Specifies the type of configuration field, which determines how it's handled in the UI.
* **Value Type**: String
* **Supported Values**:
  * `"prompt"`: Indicates the field contains prompt text that should be treated specially in the UI.
* **Usage Context**: Include in the `json_schema_extra` dictionary for Pydantic models or the `metadata["json_schema_extra"]` dictionary for dataclasses.
* **Example**:

<Accordion title="Full example configuration">
  
</Accordion>

#### Editing prompts in the UI

1. Locate the gear icon on nodes with associated configuration fields.
2. Click to open the configuration modal.
3. Edit the values.
4. Save to update the current assistant version or create a new one.

The [playground](/langsmith/create-a-prompt) interface allows testing individual LLM calls without running the full graph:

1. Select a thread.
2. Click **View LLM Runs** on a node. This lists all the LLM calls (if any) made inside the node.
3. Select an LLM run to open in the playground.
4. Modify prompts and test different model and tool settings.
5. Copy updated prompts back to your graph.

## Run experiments over a dataset

Studio lets you run [evaluations](/langsmith/evaluation-concepts) by executing your assistant against a predefined LangSmith [dataset](/langsmith/evaluation-concepts#datasets). This allows you to test performance across a variety of inputs, compare outputs to reference answers, and score results with configured [evaluators](/langsmith/evaluation-concepts#evaluators).

This guide shows you how to run a full end-to-end experiment directly from Studio.

Before running an experiment, ensure you have the following:

* **A LangSmith dataset**: Your dataset should contain the inputs you want to test and optionally, reference outputs for comparison. The schema for the inputs must match the required input schema for the assistant. For more information on schemas, see [here](/oss/python/langgraph/use-graph-api#schema). For more on creating datasets, refer to [How to Manage Datasets](/langsmith/manage-datasets-in-application#set-up-your-dataset).
* **(Optional) Evaluators**: You can attach evaluators (e.g., LLM-as-a-Judge, heuristics, or custom functions) to your dataset in LangSmith. These will run automatically after the graph has processed all inputs.
* **A running application**: The experiment can be run against:
  * An application deployed on [LangSmith](/langsmith/deployments).
  * A locally running application started via the [langgraph-cli](/langsmith/local-server).

1. Launch the experiment. Click the **Run experiment** button in the top right corner of the Studio page.
2. Select your dataset. In the modal that appears, select the dataset (or a specific dataset split) to use for the experiment and click **Start**.
3. Monitor the progress. All of the inputs in the dataset will now be run against the active assistant. Monitor the experiment's progress via the badge in the top right corner.
4. You can continue to work in Studio while the experiment runs in the background. Click the arrow icon button at any time to navigate to LangSmith and view the detailed experiment results.

## Debug LangSmith traces

This guide explains how to open LangSmith traces in Studio for interactive investigation and debugging.

### Open deployed threads

1. Open the LangSmith trace, selecting the root run.
2. Click **Run in Studio**.

This will open Studio connected to the associated deployment with the trace's parent thread selected.

### Testing local agents with remote traces

This section explains how to test a local agent against remote traces from LangSmith. This enables you to use production traces as input for local testing, allowing you to debug and verify agent modifications in your development environment.

* A LangSmith traced thread
* A [locally running agent](/langsmith/local-server#local-development-server).

<Info>
  **Local agent requirements**

* langgraph>=0.3.18
  * langgraph-api>=0.0.32
  * Contains the same set of nodes present in the remote trace
</Info>

1. Open the LangSmith trace, selecting the root run.
2. Click the dropdown next to **Run in Studio**.
3. Enter your local agent's URL.
4. Select **Clone thread locally**.
5. If multiple graphs exist, select the target graph.

A new thread will be created in your local agent with the thread history inferred and copied from the remote thread, and you will be navigated to Studio for your locally running application.

## Add node to dataset

Add [examples](/langsmith/evaluation-concepts#examples) to [LangSmith datasets](/langsmith/manage-datasets) from nodes in the thread log. This is useful to evaluate individual steps of the agent.

1. Select a thread.
2. Click **Add to Dataset**.
3. Select nodes whose input/output you want to add to a dataset.
4. For each selected node, select the target dataset to create the example in. By default a dataset for the specific assistant and node will be selected. If this dataset does not yet exist, it will be created.
5. Edit the example's input/output as needed before adding it to the dataset.
6. Select **Add to dataset** at the bottom of the page to add all selected nodes to their respective datasets.

For more details, refer to [How to evaluate an application's intermediate steps](/langsmith/evaluate-on-intermediate-steps).

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/observability-studio.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
#### `langgraph_type`

* **Description**: Specifies the type of configuration field, which determines how it's handled in the UI.
* **Value Type**: String
* **Supported Values**:
  * `"prompt"`: Indicates the field contains prompt text that should be treated specially in the UI.
* **Usage Context**: Include in the `json_schema_extra` dictionary for Pydantic models or the `metadata["json_schema_extra"]` dictionary for dataclasses.
* **Example**:
```

Example 2 (unknown):
```unknown
<Accordion title="Full example configuration">
```

---

## You can then create edges to/from this node by referencing it as `"my_node"`

**URL:** llms-txt#you-can-then-create-edges-to/from-this-node-by-referencing-it-as-`"my_node"`

**Contents:**
  - `START` Node
  - `END` Node
  - Node Caching

python  theme={null}
from langgraph.graph import START

graph.add_edge(START, "node_a")
python  theme={null}
from langgraph.graph import END

graph.add_edge("node_a", END)
python  theme={null}
import time
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

class State(TypedDict):
    x: int
    result: int

builder = StateGraph(State)

def expensive_node(state: State) -> dict[str, int]:
    # expensive computation
    time.sleep(2)
    return {"result": state["x"] * 2}

builder.add_node("expensive_node", expensive_node, cache_policy=CachePolicy(ttl=3))
builder.set_entry_point("expensive_node")
builder.set_finish_point("expensive_node")

graph = builder.compile(cache=InMemoryCache())

print(graph.invoke({"x": 5}, stream_mode='updates'))    # [!code highlight]

**Examples:**

Example 1 (unknown):
```unknown
### `START` Node

The [`START`](https://reference.langchain.com/python/langgraph/constants/#langgraph.constants.START) Node is a special node that represents the node that sends user input to the graph. The main purpose for referencing this node is to determine which nodes should be called first.
```

Example 2 (unknown):
```unknown
### `END` Node

The `END` Node is a special node that represents a terminal node. This node is referenced when you want to denote which edges have no actions after they are done.
```

Example 3 (unknown):
```unknown
### Node Caching

LangGraph supports caching of tasks/nodes based on the input to the node. To use caching:

* Specify a cache when compiling a graph (or specifying an entrypoint)
* Specify a cache policy for nodes. Each cache policy supports:
  * `key_func` used to generate a cache key based on the input to a node, which defaults to a `hash` of the input with pickle.
  * `ttl`, the time to live for the cache in seconds. If not specified, the cache will never expire.

For example:
```

---

## How to set up an application with requirements.txt

**URL:** llms-txt#how-to-set-up-an-application-with-requirements.txt

**Contents:**
- Specify dependencies
- Specify environment variables
- Define graphs

Source: https://docs.langchain.com/langsmith/setup-app-requirements-txt

An application must be configured with a [configuration file](/langsmith/cli#configuration-file) in order to be deployed to LangSmith (or to be self-hosted). This how-to guide discusses the basic steps to set up an application for deployment using `requirements.txt` to specify project dependencies.

This example is based on [this repository](https://github.com/langchain-ai/langgraph-example), which uses the LangGraph framework.

The final repository structure will look something like this:

<Tip>
  LangSmith Deployment supports deploying a [LangGraph](/oss/python/langgraph/overview) *graph*. However, the implementation of a *node* of a graph can contain arbitrary Python code. This means any framework can be implemented within a node and deployed on LangSmith Deployment. This lets you keep your core application logic outside LangGraph while still using LangSmith for [deployment](/langsmith/deployments), scaling, and [observability](/langsmith/observability).
</Tip>

You can also set up with:

* `pyproject.toml`: If you prefer using poetry for dependency management, check out [this how-to guide](/langsmith/setup-app-requirements-txt) on using `pyproject.toml` for LangSmith.
* a monorepo: If you are interested in deploying a graph located inside a monorepo, take a look at [this repository](https://github.com/langchain-ai/langgraph-example-monorepo) for an example of how to do so.

After each step, an example file directory is provided to demonstrate how code can be organized.

## Specify dependencies

Dependencies can optionally be specified in one of the following files: `pyproject.toml`, `setup.py`, or `requirements.txt`. If none of these files is created, then dependencies can be specified later in the [configuration file](#create-the-configuration-file).

The dependencies below will be included in the image, you can also use them in your code, as long as with a compatible version range:

Example `requirements.txt` file:

Example file directory:

## Specify environment variables

Environment variables can optionally be specified in a file (e.g. `.env`). See the [Environment Variables reference](/langsmith/env-var) to configure additional variables for a deployment.

Example file directory:

<Tip>
  By default, LangSmith follows the `uv`/`pip` behavior of **not** installing prerelease versions unless explicitly allowed. If want to use prereleases, you have the following options:

* With `pyproject.toml`: add `allow-prereleases = true` to your `[tool.uv]` section.
  * With `requirements.txt` or `setup.py`: you must explicitly specify every prerelease dependency, including transitive ones. For example, if you declare `a==0.0.1a1` and `a` depends on `b==0.0.1a1`, then you must also explicitly include `b==0.0.1a1` in your dependencies.
</Tip>

Implement your graphs. Graphs can be defined in a single file or multiple files. Make note of the variable names of each [CompiledStateGraph](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph) to be included in the application. The variable names will be used later when creating the [LangGraph configuration file](/langsmith/cli#configuration-file).

Example `agent.py` file, which shows how to import from other modules you define (code for the modules is not shown here, please see [this repository](https://github.com/langchain-ai/langgraph-example) to see their implementation):

```python  theme={null}

**Examples:**

Example 1 (unknown):
```unknown
<Tip>
  LangSmith Deployment supports deploying a [LangGraph](/oss/python/langgraph/overview) *graph*. However, the implementation of a *node* of a graph can contain arbitrary Python code. This means any framework can be implemented within a node and deployed on LangSmith Deployment. This lets you keep your core application logic outside LangGraph while still using LangSmith for [deployment](/langsmith/deployments), scaling, and [observability](/langsmith/observability).
</Tip>

You can also set up with:

* `pyproject.toml`: If you prefer using poetry for dependency management, check out [this how-to guide](/langsmith/setup-app-requirements-txt) on using `pyproject.toml` for LangSmith.
* a monorepo: If you are interested in deploying a graph located inside a monorepo, take a look at [this repository](https://github.com/langchain-ai/langgraph-example-monorepo) for an example of how to do so.

After each step, an example file directory is provided to demonstrate how code can be organized.

## Specify dependencies

Dependencies can optionally be specified in one of the following files: `pyproject.toml`, `setup.py`, or `requirements.txt`. If none of these files is created, then dependencies can be specified later in the [configuration file](#create-the-configuration-file).

The dependencies below will be included in the image, you can also use them in your code, as long as with a compatible version range:
```

Example 2 (unknown):
```unknown
Example `requirements.txt` file:
```

Example 3 (unknown):
```unknown
Example file directory:
```

Example 4 (unknown):
```unknown
## Specify environment variables

Environment variables can optionally be specified in a file (e.g. `.env`). See the [Environment Variables reference](/langsmith/env-var) to configure additional variables for a deployment.

Example `.env` file:
```

---

## How to evaluate an application's intermediate steps

**URL:** llms-txt#how-to-evaluate-an-application's-intermediate-steps

**Contents:**
- 1. Define your LLM pipeline
- 2. Create a dataset and examples to evaluate the pipeline
- 3. Define your custom evaluators
- 4. Evaluate the pipeline
- Related

Source: https://docs.langchain.com/langsmith/evaluate-on-intermediate-steps

While, in many scenarios, it is sufficient to evaluate the final output of your task, in some cases you might want to evaluate the intermediate steps of your pipeline.

For example, for retrieval-augmented generation (RAG), you might want to

1. Evaluate the retrieval step to ensure that the correct documents are retrieved w\.r.t the input query.
2. Evaluate the generation step to ensure that the correct answer is generated w\.r.t the retrieved documents.

In this guide, we will use a simple, fully-custom evaluator for evaluating criteria 1 and an LLM-based evaluator for evaluating criteria 2 to highlight both scenarios.

In order to evaluate the intermediate steps of your pipeline, your evaluator function should traverse and process the `run`/`rootRun` argument, which is a `Run` object that contains the intermediate steps of your pipeline.

## 1. Define your LLM pipeline

The below RAG pipeline consists of 1) generating a Wikipedia query given the input question, 2) retrieving relevant documents from Wikipedia, and 3) generating an answer given the retrieved documents.

Requires `langsmith>=0.3.13`

This pipeline will produce a trace that looks something like: <img src="https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=3b691ca56f9d60035dcba2c248692fa1" alt="evaluation_intermediate_trace.png" data-og-width="2586" width="2586" data-og-height="1676" height="1676" data-path="langsmith/images/evaluation-intermediate-trace.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=280&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=23a9b9abdb3e43e0f6326f0d4293ab7d 280w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=560&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=4b771691bd1afffe9f371a105f7eaebe 560w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=840&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=beb01776de9a5fa663c82d4380bc78cd 840w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=1100&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=ec84bd3345df3d2cef38878b902c355b 1100w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=1650&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=043a7f22da6b158e070c853d67bacd69 1650w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=2500&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=42a9ea799157fee30a6b243c02615a02 2500w" />

## 2. Create a dataset and examples to evaluate the pipeline

We are building a very simple dataset with a couple of examples to evaluate the pipeline.

Requires `langsmith>=0.3.13`

## 3. Define your custom evaluators

As mentioned above, we will define two evaluators: one that evaluates the relevance of the retrieved documents w\.r.t the input query and another that evaluates the hallucination of the generated answer w\.r.t the retrieved documents. We will be using LangChain LLM wrappers, along with [`with_structured_output`](https://python.langchain.com/v0.1/docs/modules/model_io/chat/structured_output/) to define the evaluator for hallucination.

The key here is that the evaluator function should traverse the `run` / `rootRun` argument to access the intermediate steps of the pipeline. The evaluator can then process the inputs and outputs of the intermediate steps to evaluate according to the desired criteria.

Example uses `langchain` for convenience, this is not required.

## 4. Evaluate the pipeline

Finally, we'll run `evaluate` with the custom evaluators defined above.

The experiment will contain the results of the evaluation, including the scores and comments from the evaluators: <img src="https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-experiment.png?fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=e926744573c6b9757ba22ff245a3da2c" alt="evaluation_intermediate_experiment.png" data-og-width="2446" width="2446" data-og-height="1244" height="1244" data-path="langsmith/images/evaluation-intermediate-experiment.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-experiment.png?w=280&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=7b6e321b15a06b2adc7f1cacb8e07a35 280w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-experiment.png?w=560&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=c677007bcc1e2af4b3767d6b44fcb327 560w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-experiment.png?w=840&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=a39153399b6721b7c51693f5a59cf2b0 840w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-experiment.png?w=1100&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=1132228eba6761a724ae98d85fcf536c 1100w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-experiment.png?w=1650&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=5d74785384737df0cf67145b397b1934 1650w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-experiment.png?w=2500&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=bef00e4bdc12289d9f1e4b77ed8489cf 2500w" />

* [Evaluate a `langgraph` graph](/langsmith/evaluate-on-intermediate-steps)

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/evaluate-on-intermediate-steps.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
</CodeGroup>

Requires `langsmith>=0.3.13`

<CodeGroup>
```

Example 3 (unknown):
```unknown

```

Example 4 (unknown):
```unknown
</CodeGroup>

This pipeline will produce a trace that looks something like: <img src="https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=3b691ca56f9d60035dcba2c248692fa1" alt="evaluation_intermediate_trace.png" data-og-width="2586" width="2586" data-og-height="1676" height="1676" data-path="langsmith/images/evaluation-intermediate-trace.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=280&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=23a9b9abdb3e43e0f6326f0d4293ab7d 280w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=560&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=4b771691bd1afffe9f371a105f7eaebe 560w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=840&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=beb01776de9a5fa663c82d4380bc78cd 840w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=1100&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=ec84bd3345df3d2cef38878b902c355b 1100w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=1650&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=043a7f22da6b158e070c853d67bacd69 1650w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/evaluation-intermediate-trace.png?w=2500&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=42a9ea799157fee30a6b243c02615a02 2500w" />

## 2. Create a dataset and examples to evaluate the pipeline

We are building a very simple dataset with a couple of examples to evaluate the pipeline.

Requires `langsmith>=0.3.13`

<CodeGroup>
```

---

## Define a new graph

**URL:** llms-txt#define-a-new-graph

workflow = StateGraph(State)

---

## Agent Server

**URL:** llms-txt#agent-server

**Contents:**
- Application structure
- Parts of a deployment
  - Graphs
  - Persistence and task queue
- Learn more

Source: https://docs.langchain.com/langsmith/agent-server

LangSmith Deployment's **Agent Server** offers an API for creating and managing agent-based applications. It is built on the concept of [assistants](/langsmith/assistants), which are agents configured for specific tasks, and includes built-in [persistence](/oss/python/langgraph/persistence#memory-store) and a **task queue**. This versatile API supports a wide range of agentic application use cases, from background processing to real-time interactions.

Use Agent Server to create and manage [assistants](/langsmith/assistants), [threads](/oss/python/langgraph/persistence#threads), [runs](/langsmith/assistants#execution), [cron jobs](/langsmith/cron-jobs), [webhooks](/langsmith/use-webhooks), and more.

<Tip>
  **API reference**<br />
  For detailed information on the API endpoints and data models, refer to the [API reference docs](https://langchain-ai.github.io/langgraph/cloud/reference/api/api_ref.html).
</Tip>

To use the Enterprise version of the Agent Server, you must acquire a license key that you will need to specify when running the Docker image. To acquire a license key, [contact our sales team](https://www.langchain.com/contact-sales).

You can run the Enterprise version of the Agent Server on the following LangSmith [platform](/langsmith/platform-setup) options:

* [Cloud](/langsmith/cloud)
* [Hybrid](/langsmith/hybrid)
* [Self-hosted](/langsmith/self-hosted)

## Application structure

To deploy an Agent Server application, you need to specify the graph(s) you want to deploy, as well as any relevant configuration settings, such as dependencies and environment variables.

Read the [application structure](/langsmith/application-structure) guide to learn how to structure your LangGraph application for deployment.

## Parts of a deployment

When you deploy Agent Server, you are deploying one or more [graphs](#graphs), a database for [persistence](/oss/python/langgraph/persistence), and a task queue.

When you deploy a graph with Agent Server, you are deploying a "blueprint" for an [Assistant](/langsmith/assistants).

An [Assistant](/langsmith/assistants) is a graph paired with specific configuration settings. You can create multiple assistants per graph, each with unique settings to accommodate different use cases
that can be served by the same graph.

Upon deployment, Agent Server will automatically create a default assistant for each graph using the graph's default configuration settings.

<Note>
  We often think of a graph as implementing an [agent](/oss/python/langgraph/workflows-agents), but a graph does not necessarily need to implement an agent. For example, a graph could implement a simple
  chatbot that only supports back-and-forth conversation, without the ability to influence any application control flow. In reality, as applications get more complex, a graph will often implement a more complex flow that may use [multiple agents](/oss/python/langchain/multi-agent) working in tandem.
</Note>

### Persistence and task queue

Agent Server leverages a database for [persistence](/oss/python/langgraph/persistence) and a task queue.

[PostgreSQL](https://www.postgresql.org/) is supported as a database for Agent Server and [Redis](https://redis.io/) as the task queue.

If you're deploying using [LangSmith cloud](/langsmith/cloud), these components are managed for you. If you're deploying Agent Server on your [own infrastructure](/langsmith/self-hosted), you'll need to set up and manage these components yourself.

For more information on how these components are set up and managed, review the [hosting options](/langsmith/platform-setup) guide.

* [Application Structure](/langsmith/application-structure) guide explains how to structure your application for deployment.
* The [API Reference](https://langchain-ai.github.io/langgraph/cloud/reference/api/api_ref.html) provides detailed information on the API endpoints and data models.

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/agent-server.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## Invoke the graph

**URL:** llms-txt#invoke-the-graph

config = {"configurable": {"thread_id": "2", "user_id": "1"}}

---

## my_agent/agent.py

**URL:** llms-txt#my_agent/agent.py

from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END, START
from my_agent.utils.nodes import call_model, should_continue, tool_node # import nodes
from my_agent.utils.state import AgentState # import state

---

## Compile

**URL:** llms-txt#compile

**Contents:**
  - 1. Run the graph

checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)
graph
python  theme={null}
config = {
    "configurable": {
        "thread_id": uuid.uuid4(),
    }
}
state = graph.invoke({}, config)

print(state["topic"])
print()
print(state["joke"])

How about "The Secret Life of Socks in the Dryer"? You know, exploring the mysterious phenomenon of how socks go into the laundry as pairs but come out as singles. Where do they go? Are they starting new lives elsewhere? Is there a sock paradise we don't know about? There's a lot of comedic potential in the everyday mystery that unites us all!

**Examples:**

Example 1 (unknown):
```unknown
### 1. Run the graph
```

Example 2 (unknown):
```unknown
**Output:**
```

---

## Define the runtime context

**URL:** llms-txt#define-the-runtime-context

**Contents:**
- Create the configuration file
- Next

class GraphContext(TypedDict):
    model_name: Literal["anthropic", "openai"]

workflow = StateGraph(AgentState, context_schema=GraphContext)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)
workflow.add_edge("action", "agent")

graph = workflow.compile()
bash  theme={null}
my-app/
├── my_agent # all project code lies within here
│   ├── utils # utilities for your graph
│   │   ├── __init__.py
│   │   ├── tools.py # tools for your graph
│   │   ├── nodes.py # node functions for your graph
│   │   └── state.py # state definition of your graph
│   ├── __init__.py
│   └── agent.py # code for constructing your graph
├── .env
└── pyproject.toml
json  theme={null}
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./my_agent/agent.py:graph"
  },
  "env": ".env"
}
bash  theme={null}
my-app/
├── my_agent # all project code lies within here
│   ├── utils # utilities for your graph
│   │   ├── __init__.py
│   │   ├── tools.py # tools for your graph
│   │   ├── nodes.py # node functions for your graph
│   │   └── state.py # state definition of your graph
│   ├── __init__.py
│   └── agent.py # code for constructing your graph
├── .env # environment variables
├── langgraph.json  # configuration file for LangGraph
└── pyproject.toml # dependencies for your project
```

After you setup your project and place it in a GitHub repository, it's time to [deploy your app](/langsmith/deployment-quickstart).

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/setup-pyproject.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
Example file directory:
```

Example 2 (unknown):
```unknown
## Create the configuration file

Create a [configuration file](/langsmith/cli#configuration-file) called `langgraph.json`. See the [configuration file reference](/langsmith/cli#configuration-file) for detailed explanations of each key in the JSON object of the configuration file.

Example `langgraph.json` file:
```

Example 3 (unknown):
```unknown
Note that the variable name of the `CompiledGraph` appears at the end of the value of each subkey in the top-level `graphs` key (i.e. `:<variable_name>`).

<Warning>
  **Configuration file location**
  The configuration file must be placed in a directory that is at the same level or higher than the Python files that contain compiled graphs and associated dependencies.
</Warning>

Example file directory:
```

---

## How to set up an application with pyproject.toml

**URL:** llms-txt#how-to-set-up-an-application-with-pyproject.toml

**Contents:**
- Specify dependencies
- Specify environment variables
- Define graphs

Source: https://docs.langchain.com/langsmith/setup-pyproject

An application must be configured with a [configuration file](/langsmith/cli#configuration-file) in order to be deployed to LangSmith (or to be self-hosted). This how-to guide discusses the basic steps to set up an application for deployment using `pyproject.toml` to define your package's dependencies.

This example is based on [this repository](https://github.com/langchain-ai/langgraph-example-pyproject), which uses the LangGraph framework.

The final repository structure will look something like this:

<Tip>
  LangSmith Deployment supports deploying a [LangGraph](/oss/python/langgraph/overview) *graph*. However, the implementation of a *node* of a graph can contain arbitrary Python code. This means any framework can be implemented within a node and deployed on LangSmith Deployment. This lets you keep your core application logic outside LangGraph while still using LangSmith for [deployment](/langsmith/deployments), scaling, and [observability](/langsmith/observability).
</Tip>

You can also set up with:

* `requirements.txt`: for dependency management, check out [this how-to guide](/langsmith/setup-app-requirements-txt) on using `requirements.txt` for LangSmith.
* a monorepo: To deploy a graph located inside a monorepo, take a look at [this repository](https://github.com/langchain-ai/langgraph-example-monorepo) for an example of how to do so.

After each step, an example file directory is provided to demonstrate how code can be organized.

## Specify dependencies

Dependencies can optionally be specified in one of the following files: `pyproject.toml`, `setup.py`, or `requirements.txt`. If none of these files is created, then dependencies can be specified later in the [configuration file](#create-the-configuration-file).

The dependencies below will be included in the image, you can also use them in your code, as long as with a compatible version range:

Example `pyproject.toml` file:

Example file directory:

## Specify environment variables

Environment variables can optionally be specified in a file (e.g. `.env`). See the [Environment Variables reference](/langsmith/env-var) to configure additional variables for a deployment.

Example file directory:

<Tip>
  By default, LangSmith follows the `uv`/`pip` behavior of **not** installing prerelease versions unless explicitly allowed. If want to use prereleases, you have the following options:

* With `pyproject.toml`: add `allow-prereleases = true` to your `[tool.uv]` section.
  * With `requirements.txt` or `setup.py`: you must explicitly specify every prerelease dependency, including transitive ones. For example, if you declare `a==0.0.1a1` and `a` depends on `b==0.0.1a1`, then you must also explicitly include `b==0.0.1a1` in your dependencies.
</Tip>

Implement your graphs. Graphs can be defined in a single file or multiple files. Make note of the variable names of each [CompiledStateGraph](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph) to be included in the application. The variable names will be used later when creating the [configuration file](/langsmith/cli#configuration-file).

Example `agent.py` file, which shows how to import from other modules you define (code for the modules is not shown here, please see [this repository](https://github.com/langchain-ai/langgraph-example-pyproject) to see their implementation):

```python  theme={null}

**Examples:**

Example 1 (unknown):
```unknown
<Tip>
  LangSmith Deployment supports deploying a [LangGraph](/oss/python/langgraph/overview) *graph*. However, the implementation of a *node* of a graph can contain arbitrary Python code. This means any framework can be implemented within a node and deployed on LangSmith Deployment. This lets you keep your core application logic outside LangGraph while still using LangSmith for [deployment](/langsmith/deployments), scaling, and [observability](/langsmith/observability).
</Tip>

You can also set up with:

* `requirements.txt`: for dependency management, check out [this how-to guide](/langsmith/setup-app-requirements-txt) on using `requirements.txt` for LangSmith.
* a monorepo: To deploy a graph located inside a monorepo, take a look at [this repository](https://github.com/langchain-ai/langgraph-example-monorepo) for an example of how to do so.

After each step, an example file directory is provided to demonstrate how code can be organized.

## Specify dependencies

Dependencies can optionally be specified in one of the following files: `pyproject.toml`, `setup.py`, or `requirements.txt`. If none of these files is created, then dependencies can be specified later in the [configuration file](#create-the-configuration-file).

The dependencies below will be included in the image, you can also use them in your code, as long as with a compatible version range:
```

Example 2 (unknown):
```unknown
Example `pyproject.toml` file:
```

Example 3 (unknown):
```unknown
Example file directory:
```

Example 4 (unknown):
```unknown
## Specify environment variables

Environment variables can optionally be specified in a file (e.g. `.env`). See the [Environment Variables reference](/langsmith/env-var) to configure additional variables for a deployment.

Example `.env` file:
```

---

## Compile the graph with the checkpointer and store

**URL:** llms-txt#compile-the-graph-with-the-checkpointer-and-store

graph = graph.compile(checkpointer=checkpointer, store=in_memory_store)
python  theme={null}

**Examples:**

Example 1 (unknown):
```unknown
We invoke the graph with a `thread_id`, as before, and also with a `user_id`, which we'll use to namespace our memories to this particular user as we showed above.
```

---

## with information about the graph node where the LLM was called and other information

**URL:** llms-txt#with-information-about-the-graph-node-where-the-llm-was-called-and-other-information

**Contents:**
- Stream custom data
- Use with any LLM

for msg, metadata in graph.stream(
    inputs,
    stream_mode="messages",  # [!code highlight]
):
    # Filter the streamed tokens by the langgraph_node field in the metadata
    # to only include the tokens from the specified node
    if msg.content and metadata["langgraph_node"] == "some_node_name":
        ...
python  theme={null}
  from typing import TypedDict
  from langgraph.graph import START, StateGraph
  from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")

class State(TypedDict):
        topic: str
        joke: str
        poem: str

def write_joke(state: State):
        topic = state["topic"]
        joke_response = model.invoke(
              [{"role": "user", "content": f"Write a joke about {topic}"}]
        )
        return {"joke": joke_response.content}

def write_poem(state: State):
        topic = state["topic"]
        poem_response = model.invoke(
              [{"role": "user", "content": f"Write a short poem about {topic}"}]
        )
        return {"poem": poem_response.content}

graph = (
        StateGraph(State)
        .add_node(write_joke)
        .add_node(write_poem)
        # write both the joke and the poem concurrently
        .add_edge(START, "write_joke")
        .add_edge(START, "write_poem")
        .compile()
  )

# The "messages" stream mode returns a tuple of (message_chunk, metadata)
  # where message_chunk is the token streamed by the LLM and metadata is a dictionary
  # with information about the graph node where the LLM was called and other information
  for msg, metadata in graph.stream(
      {"topic": "cats"},
      stream_mode="messages",  # [!code highlight]
  ):
      # Filter the streamed tokens by the langgraph_node field in the metadata
      # to only include the tokens from the write_poem node
      if msg.content and metadata["langgraph_node"] == "write_poem":
          print(msg.content, end="|", flush=True)
  python  theme={null}
    from typing import TypedDict
    from langgraph.config import get_stream_writer
    from langgraph.graph import StateGraph, START

class State(TypedDict):
        query: str
        answer: str

def node(state: State):
        # Get the stream writer to send custom data
        writer = get_stream_writer()
        # Emit a custom key-value pair (e.g., progress update)
        writer({"custom_key": "Generating custom data inside node"})
        return {"answer": "some data"}

graph = (
        StateGraph(State)
        .add_node(node)
        .add_edge(START, "node")
        .compile()
    )

inputs = {"query": "example"}

# Set stream_mode="custom" to receive the custom data in the stream
    for chunk in graph.stream(inputs, stream_mode="custom"):
        print(chunk)
    python  theme={null}
    from langchain.tools import tool
    from langgraph.config import get_stream_writer

@tool
    def query_database(query: str) -> str:
        """Query the database."""
        # Access the stream writer to send custom data
        writer = get_stream_writer()  # [!code highlight]
        # Emit a custom key-value pair (e.g., progress update)
        writer({"data": "Retrieved 0/100 records", "type": "progress"})  # [!code highlight]
        # perform query
        # Emit another custom key-value pair
        writer({"data": "Retrieved 100/100 records", "type": "progress"})
        return "some-answer"

graph = ... # define a graph that uses this tool

# Set stream_mode="custom" to receive the custom data in the stream
    for chunk in graph.stream(inputs, stream_mode="custom"):
        print(chunk)
    python  theme={null}
from langgraph.config import get_stream_writer

def call_arbitrary_model(state):
    """Example node that calls an arbitrary model and streams the output"""
    # Get the stream writer to send custom data
    writer = get_stream_writer()  # [!code highlight]
    # Assume you have a streaming client that yields chunks
    # Generate LLM tokens using your custom streaming client
    for chunk in your_custom_streaming_client(state["topic"]):
        # Use the writer to send custom data to the stream
        writer({"custom_llm_chunk": chunk})  # [!code highlight]
    return {"result": "completed"}

graph = (
    StateGraph(State)
    .add_node(call_arbitrary_model)
    # Add other nodes and edges as needed
    .compile()
)

**Examples:**

Example 1 (unknown):
```unknown
<Accordion title="Extended example: streaming LLM tokens from specific nodes">
```

Example 2 (unknown):
```unknown
</Accordion>

## Stream custom data

To send **custom user-defined data** from inside a LangGraph node or tool, follow these steps:

1. Use [`get_stream_writer`](https://reference.langchain.com/python/langgraph/config/#langgraph.config.get_stream_writer) to access the stream writer and emit custom data.
2. Set `stream_mode="custom"` when calling `.stream()` or `.astream()` to get the custom data in the stream. You can combine multiple modes (e.g., `["updates", "custom"]`), but at least one must be `"custom"`.

<Warning>
  **No [`get_stream_writer`](https://reference.langchain.com/python/langgraph/config/#langgraph.config.get_stream_writer) in async for Python \< 3.11**
  In async code running on Python \< 3.11, [`get_stream_writer`](https://reference.langchain.com/python/langgraph/config/#langgraph.config.get_stream_writer) will not work.
  Instead, add a `writer` parameter to your node or tool and pass it manually.
  See [Async with Python \< 3.11](#async) for usage examples.
</Warning>

<Tabs>
  <Tab title="node">
```

Example 3 (unknown):
```unknown
</Tab>

  <Tab title="tool">
```

Example 4 (unknown):
```unknown
</Tab>
</Tabs>

## Use with any LLM

You can use `stream_mode="custom"` to stream data from **any LLM API** — even if that API does **not** implement the LangChain chat model interface.

This lets you integrate raw LLM clients or external services that provide their own streaming interfaces, making LangGraph highly flexible for custom setups.
```

---

## Build the graph with explicit schemas

**URL:** llms-txt#build-the-graph-with-explicit-schemas

builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
builder.add_node(answer_node)
builder.add_edge(START, "answer_node")
builder.add_edge("answer_node", END)
graph = builder.compile()

---

## Call the graph: here we call it to generate a list of jokes

**URL:** llms-txt#call-the-graph:-here-we-call-it-to-generate-a-list-of-jokes

**Contents:**
- Create and control loops

for step in graph.stream({"topic": "animals"}):
    print(step)

{'generate_topics': {'subjects': ['lions', 'elephants', 'penguins']}}
{'generate_joke': {'jokes': ["Why don't lions like fast food? Because they can't catch it!"]}}
{'generate_joke': {'jokes': ["Why don't elephants use computers? They're afraid of the mouse!"]}}
{'generate_joke': {'jokes': ['Why don't penguins like talking to strangers at parties? Because they find it hard to break the ice.']}}
{'best_joke': {'best_selected_joke': 'penguins'}}
python  theme={null}
builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)

def route(state: State) -> Literal["b", END]:
    if termination_condition(state):
        return END
    else:
        return "b"

builder.add_edge(START, "a")
builder.add_conditional_edges("a", route)
builder.add_edge("b", "a")
graph = builder.compile()
python  theme={null}
from langgraph.errors import GraphRecursionError

try:
    graph.invoke(inputs, {"recursion_limit": 3})
except GraphRecursionError:
    print("Recursion Error")
python  theme={null}
import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    aggregate: Annotated[list, operator.add]

def a(state: State):
    print(f'Node A sees {state["aggregate"]}')
    return {"aggregate": ["A"]}

def b(state: State):
    print(f'Node B sees {state["aggregate"]}')
    return {"aggregate": ["B"]}

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
## Create and control loops

When creating a graph with a loop, we require a mechanism for terminating execution. This is most commonly done by adding a [conditional edge](/oss/python/langgraph/graph-api#conditional-edges) that routes to the [END](/oss/python/langgraph/graph-api#end-node) node once we reach some termination condition.

You can also set the graph recursion limit when invoking or streaming the graph. The recursion limit sets the number of [supersteps](/oss/python/langgraph/graph-api#graphs) that the graph is allowed to execute before it raises an error. Read more about the concept of recursion limits [here](/oss/python/langgraph/graph-api#recursion-limit).

Let's consider a simple graph with a loop to better understand how these mechanisms work.

<Tip>
  To return the last value of your state instead of receiving a recursion limit error, see the [next section](#impose-a-recursion-limit).
</Tip>

When creating a loop, you can include a conditional edge that specifies a termination condition:
```

Example 3 (unknown):
```unknown
To control the recursion limit, specify `"recursionLimit"` in the config. This will raise a `GraphRecursionError`, which you can catch and handle:
```

Example 4 (unknown):
```unknown
Let's define a graph with a simple loop. Note that we use a conditional edge to implement a termination condition.
```

---

## Graph API overview

**URL:** llms-txt#graph-api-overview

**Contents:**
- Graphs
  - StateGraph
  - Compiling your graph
- State
  - Schema

Source: https://docs.langchain.com/oss/python/langgraph/graph-api

At its core, LangGraph models agent workflows as graphs. You define the behavior of your agents using three key components:

1. [`State`](#state): A shared data structure that represents the current snapshot of your application. It can be any data type, but is typically defined using a shared state schema.

2. [`Nodes`](#nodes): Functions that encode the logic of your agents. They receive the current state as input, perform some computation or side-effect, and return an updated state.

3. [`Edges`](#edges): Functions that determine which `Node` to execute next based on the current state. They can be conditional branches or fixed transitions.

By composing `Nodes` and `Edges`, you can create complex, looping workflows that evolve the state over time. The real power, though, comes from how LangGraph manages that state.

To emphasize: `Nodes` and `Edges` are nothing more than functions – they can contain an LLM or just good ol' code.

In short: *nodes do the work, edges tell what to do next*.

LangGraph's underlying graph algorithm uses [message passing](https://en.wikipedia.org/wiki/Message_passing) to define a general program. When a Node completes its operation, it sends messages along one or more edges to other node(s). These recipient nodes then execute their functions, pass the resulting messages to the next set of nodes, and the process continues. Inspired by Google's [Pregel](https://research.google/pubs/pregel-a-system-for-large-scale-graph-processing/) system, the program proceeds in discrete "super-steps."

A super-step can be considered a single iteration over the graph nodes. Nodes that run in parallel are part of the same super-step, while nodes that run sequentially belong to separate super-steps. At the start of graph execution, all nodes begin in an `inactive` state. A node becomes `active` when it receives a new message (state) on any of its incoming edges (or "channels"). The active node then runs its function and responds with updates. At the end of each super-step, nodes with no incoming messages vote to `halt` by marking themselves as `inactive`. The graph execution terminates when all nodes are `inactive` and no messages are in transit.

The [`StateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph) class is the main graph class to use. This is parameterized by a user defined `State` object.

### Compiling your graph

To build your graph, you first define the [state](#state), you then add [nodes](#nodes) and [edges](#edges), and then you compile it. What exactly is compiling your graph and why is it needed?

Compiling is a pretty simple step. It provides a few basic checks on the structure of your graph (no orphaned nodes, etc). It is also where you can specify runtime args like [checkpointers](/oss/python/langgraph/persistence) and breakpoints. You compile your graph by just calling the `.compile` method:

<Warning>
  You **MUST** compile your graph before you can use it.
</Warning>

The first thing you do when you define a graph is define the `State` of the graph. The `State` consists of the [schema of the graph](#schema) as well as [`reducer` functions](#reducers) which specify how to apply updates to the state. The schema of the `State` will be the input schema to all `Nodes` and `Edges` in the graph, and can be either a `TypedDict` or a `Pydantic` model. All `Nodes` will emit updates to the `State` which are then applied using the specified `reducer` function.

The main documented way to specify the schema of a graph is by using a [`TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict). If you want to provide default values in your state, use a [`dataclass`](https://docs.python.org/3/library/dataclasses.html). We also support using a Pydantic [`BaseModel`](/oss/python/langgraph/use-graph-api#use-pydantic-models-for-graph-state) as your graph state if you want recursive data validation (though note that Pydantic is less performant than a `TypedDict` or `dataclass`).

By default, the graph will have the same input and output schemas. If you want to change this, you can also specify explicit input and output schemas directly. This is useful when you have a lot of keys, and some are explicitly for input and others for output. See the [guide](/oss/python/langgraph/use-graph-api#define-input-and-output-schemas) for more information.

#### Multiple schemas

Typically, all graph nodes communicate with a single schema. This means that they will read and write to the same state channels. But, there are cases where we want more control over this:

* Internal nodes can pass information that is not required in the graph's input / output.
* We may also want to use different input / output schemas for the graph. The output might, for example, only contain a single relevant output key.

It is possible to have nodes write to private state channels inside the graph for internal node communication. We can simply define a private schema, `PrivateState`.

It is also possible to define explicit input and output schemas for a graph. In these cases, we define an "internal" schema that contains *all* keys relevant to graph operations. But, we also define `input` and `output` schemas that are sub-sets of the "internal" schema to constrain the input and output of the graph. See [this guide](/oss/python/langgraph/graph-api#define-input-and-output-schemas) for more detail.

Let's look at an example:

```python  theme={null}
class InputState(TypedDict):
    user_input: str

class OutputState(TypedDict):
    graph_output: str

class OverallState(TypedDict):
    foo: str
    user_input: str
    graph_output: str

class PrivateState(TypedDict):
    bar: str

def node_1(state: InputState) -> OverallState:
    # Write to OverallState
    return {"foo": state["user_input"] + " name"}

def node_2(state: OverallState) -> PrivateState:
    # Read from OverallState, write to PrivateState
    return {"bar": state["foo"] + " is"}

def node_3(state: PrivateState) -> OutputState:
    # Read from PrivateState, write to OutputState
    return {"graph_output": state["bar"] + " Lance"}

builder = StateGraph(OverallState,input_schema=InputState,output_schema=OutputState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", "node_3")
builder.add_edge("node_3", END)

graph = builder.compile()
graph.invoke({"user_input":"My"})

**Examples:**

Example 1 (unknown):
```unknown
<Warning>
  You **MUST** compile your graph before you can use it.
</Warning>

## State

The first thing you do when you define a graph is define the `State` of the graph. The `State` consists of the [schema of the graph](#schema) as well as [`reducer` functions](#reducers) which specify how to apply updates to the state. The schema of the `State` will be the input schema to all `Nodes` and `Edges` in the graph, and can be either a `TypedDict` or a `Pydantic` model. All `Nodes` will emit updates to the `State` which are then applied using the specified `reducer` function.

### Schema

The main documented way to specify the schema of a graph is by using a [`TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict). If you want to provide default values in your state, use a [`dataclass`](https://docs.python.org/3/library/dataclasses.html). We also support using a Pydantic [`BaseModel`](/oss/python/langgraph/use-graph-api#use-pydantic-models-for-graph-state) as your graph state if you want recursive data validation (though note that Pydantic is less performant than a `TypedDict` or `dataclass`).

By default, the graph will have the same input and output schemas. If you want to change this, you can also specify explicit input and output schemas directly. This is useful when you have a lot of keys, and some are explicitly for input and others for output. See the [guide](/oss/python/langgraph/use-graph-api#define-input-and-output-schemas) for more information.

#### Multiple schemas

Typically, all graph nodes communicate with a single schema. This means that they will read and write to the same state channels. But, there are cases where we want more control over this:

* Internal nodes can pass information that is not required in the graph's input / output.
* We may also want to use different input / output schemas for the graph. The output might, for example, only contain a single relevant output key.

It is possible to have nodes write to private state channels inside the graph for internal node communication. We can simply define a private schema, `PrivateState`.

It is also possible to define explicit input and output schemas for a graph. In these cases, we define an "internal" schema that contains *all* keys relevant to graph operations. But, we also define `input` and `output` schemas that are sub-sets of the "internal" schema to constrain the input and output of the graph. See [this guide](/oss/python/langgraph/graph-api#define-input-and-output-schemas) for more detail.

Let's look at an example:
```

---

## Human-in-the-loop using server API

**URL:** llms-txt#human-in-the-loop-using-server-api

**Contents:**
- Dynamic interrupts
- Static interrupts
- Learn more

Source: https://docs.langchain.com/langsmith/add-human-in-the-loop

To review, edit, and approve tool calls in an agent or workflow, use LangGraph's [human-in-the-loop](/oss/python/langgraph/interrupts) features.

## Dynamic interrupts

<Tabs>
  <Tab title="Python">

1. The graph is invoked with some initial state.
    2. When the graph hits the interrupt, it returns an interrupt object with the payload and metadata.
       3\. The graph is resumed with a `Command(resume=...)`, injecting the human's input and continuing execution.
  </Tab>

<Tab title="JavaScript">

1. The graph is invoked with some initial state.
    2. When the graph hits the interrupt, it returns an interrupt object with the payload and metadata.
    3. The graph is resumed with a `{ resume: ... }` command object, injecting the human's input and continuing execution.
  </Tab>

<Tab title="cURL">
    Create a thread:

Run the graph until the interrupt is hit.:

<Accordion title="Extended example: using `interrupt`">
  This is an example graph you can run in the Agent Server.
  See [LangSmith quickstart](/langsmith/deployment-quickstart) for more details.

1. `interrupt(...)` pauses execution at `human_node`, surfacing the given payload to a human.
  2. Any JSON serializable value can be passed to the [`interrupt`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) function. Here, a dict containing the text to revise.
  3. Once resumed, the return value of `interrupt(...)` is the human-provided input, which is used to update the state.

Once you have a running Agent Server, you can interact with it using
  [LangGraph SDK](/langsmith/langgraph-python-sdk)

<Tabs>
    <Tab title="Python">

1. The graph is invoked with some initial state.
      2. When the graph hits the interrupt, it returns an interrupt object with the payload and metadata.
         3\. The graph is resumed with a `Command(resume=...)`, injecting the human's input and continuing execution.
    </Tab>

<Tab title="JavaScript">

1. The graph is invoked with some initial state.
      2. When the graph hits the interrupt, it returns an interrupt object with the payload and metadata.
      3. The graph is resumed with a `{ resume: ... }` command object, injecting the human's input and continuing execution.
    </Tab>

<Tab title="cURL">
      Create a thread:

Run the graph until the interrupt is hit:

</Tab>
  </Tabs>
</Accordion>

Static interrupts (also known as static breakpoints) are triggered either before or after a node executes.

<Warning>
  Static interrupts are **not** recommended for human-in-the-loop workflows. They are best used for debugging and testing.
</Warning>

You can set static interrupts by specifying `interrupt_before` and `interrupt_after` at compile time:

1. The breakpoints are set during `compile` time.
2. `interrupt_before` specifies the nodes where execution should pause before the node is executed.
3. `interrupt_after` specifies the nodes where execution should pause after the node is executed.

Alternatively, you can set static interrupts at run time:

<Tabs>
  <Tab title="Python">

1. `client.runs.wait` is called with the `interrupt_before` and `interrupt_after` parameters. This is a run-time configuration and can be changed for every invocation.
    2. `interrupt_before` specifies the nodes where execution should pause before the node is executed.
    3. `interrupt_after` specifies the nodes where execution should pause after the node is executed.
  </Tab>

<Tab title="JavaScript">

1. `client.runs.wait` is called with the `interruptBefore` and `interruptAfter` parameters. This is a run-time configuration and can be changed for every invocation.
    2. `interruptBefore` specifies the nodes where execution should pause before the node is executed.
    3. `interruptAfter` specifies the nodes where execution should pause after the node is executed.
  </Tab>

<Tab title="cURL">
    
  </Tab>
</Tabs>

The following example shows how to add static interrupts:

<Tabs>
  <Tab title="Python">

1. The graph is run until the first breakpoint is hit.
    2. The graph is resumed by passing in `None` for the input. This will run the graph until the next breakpoint is hit.
  </Tab>

<Tab title="JavaScript">

1. The graph is run until the first breakpoint is hit.
    2. The graph is resumed by passing in `null` for the input. This will run the graph until the next breakpoint is hit.
  </Tab>

<Tab title="cURL">
    Create a thread:

Run the graph until the breakpoint:

* [Human-in-the-loop conceptual guide](/oss/python/langgraph/interrupts): learn more about LangGraph human-in-the-loop features.
* [Common patterns](/oss/python/langgraph/interrupts#common-patterns): learn how to implement patterns like approving/rejecting actions, requesting user input, tool call review, and validating human input.

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/add-human-in-the-loop.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
1. The graph is invoked with some initial state.
    2. When the graph hits the interrupt, it returns an interrupt object with the payload and metadata.
       3\. The graph is resumed with a `Command(resume=...)`, injecting the human's input and continuing execution.
  </Tab>

  <Tab title="JavaScript">
```

Example 2 (unknown):
```unknown
1. The graph is invoked with some initial state.
    2. When the graph hits the interrupt, it returns an interrupt object with the payload and metadata.
    3. The graph is resumed with a `{ resume: ... }` command object, injecting the human's input and continuing execution.
  </Tab>

  <Tab title="cURL">
    Create a thread:
```

Example 3 (unknown):
```unknown
Run the graph until the interrupt is hit.:
```

Example 4 (unknown):
```unknown
Resume the graph:
```

---

## Thinking in LangGraph

**URL:** llms-txt#thinking-in-langgraph

**Contents:**
- Start with the process you want to automate
- Step 1: Map out your workflow as discrete steps
- Step 2: Identify what each step needs to do
  - LLM Steps
  - Data Steps
  - Action Steps
  - User Input Steps
- Step 3: Design your state
  - What belongs in state?
  - Keep state raw, format prompts on-demand

Source: https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph

Learn how to think about building agents with LangGraph by breaking down a customer support email agent into discrete steps

LangGraph can change how you think about the agents you build. When you build an agent with LangGraph, you will first break it apart into discrete steps called **nodes**. Then, you will describe the different decisions and transitions for each of your nodes. Finally, you will connect your nodes together through a shared **state** that each node can read from and write to. In this tutorial, we'll guide you through the thought process of building a customer support email agent with LangGraph.

## Start with the process you want to automate

Imagine that you need to build an AI agent that handles customer support emails. Your product team has given you these requirements:

* Read incoming customer emails
* Classify them by urgency and topic
* Search relevant documentation to answer questions
* Draft appropriate responses
* Escalate complex issues to human agents
* Schedule follow-ups when needed

Example scenarios to handle:

1. Simple product question: "How do I reset my password?"
2. Bug report: "The export feature crashes when I select PDF format"
3. Urgent billing issue: "I was charged twice for my subscription!"
4. Feature request: "Can you add dark mode to the mobile app?"
5. Complex technical issue: "Our API integration fails intermittently with 504 errors"

To implement an agent in LangGraph, you will usually follow the same five steps.

## Step 1: Map out your workflow as discrete steps

Start by identifying the distinct steps in your process. Each step will become a **node** (a function that does one specific thing). Then sketch how these steps connect to each other.

The arrows show possible paths, but the actual decision of which path to take happens inside each node.

Now that you've identified the components in your workflow, let's understand what each node needs to do:

* Read Email: Extract and parse the email content
* Classify Intent: Use an LLM to categorize urgency and topic, then route to appropriate action
* Doc Search: Query your knowledge base for relevant information
* Bug Track: Create or update issue in tracking system
* Draft Reply: Generate an appropriate response
* Human Review: Escalate to human agent for approval or handling
* Send Reply: Dispatch the email response

<Tip>
  Notice that some nodes make decisions about where to go next (Classify Intent, Draft Reply, Human Review), while others always proceed to the same next step (Read Email always goes to Classify Intent, Doc Search always goes to Draft Reply).
</Tip>

## Step 2: Identify what each step needs to do

For each node in your graph, determine what type of operation it represents and what context it needs to work properly.

<CardGroup cols={2}>
  <Card title="LLM Steps" icon="brain" href="#llm-steps">
    Use when you need to understand, analyze, generate text, or make reasoning decisions
  </Card>

<Card title="Data Steps" icon="database" href="#data-steps">
    Use when you need to retrieve information from external sources
  </Card>

<Card title="Action Steps" icon="bolt" href="#action-steps">
    Use when you need to perform external actions
  </Card>

<Card title="User Input Steps" icon="user" href="#user-input-steps">
    Use when you need human intervention
  </Card>
</CardGroup>

When a step needs to understand, analyze, generate text, or make reasoning decisions:

<AccordionGroup>
  <Accordion title="Classify Intent Node">
    * Static context (prompt): Classification categories, urgency definitions, response format
    * Dynamic context (from state): Email content, sender information
    * Desired outcome: Structured classification that determines routing
  </Accordion>

<Accordion title="Draft Reply Node">
    * Static context (prompt): Tone guidelines, company policies, response templates
    * Dynamic context (from state): Classification results, search results, customer history
    * Desired outcome: Professional email response ready for review
  </Accordion>
</AccordionGroup>

When a step needs to retrieve information from external sources:

<AccordionGroup>
  <Accordion title="Document Search Node">
    * Parameters: Query built from intent and topic
    * Retry strategy: Yes, with exponential backoff for transient failures
    * Caching: Could cache common queries to reduce API calls
  </Accordion>

<Accordion title="Customer History Lookup">
    * Parameters: Customer email or ID from state
    * Retry strategy: Yes, but with fallback to basic info if unavailable
    * Caching: Yes, with time-to-live to balance freshness and performance
  </Accordion>
</AccordionGroup>

When a step needs to perform an external action:

<AccordionGroup>
  <Accordion title="Send Reply Node">
    * When to execute: After approval (human or automated)
    * Retry strategy: Yes, with exponential backoff for network issues
    * Should not cache: Each send is a unique action
  </Accordion>

<Accordion title="Bug Track Node">
    * When to execute: Always when intent is "bug"
    * Retry strategy: Yes, critical to not lose bug reports
    * Returns: Ticket ID to include in response
  </Accordion>
</AccordionGroup>

When a step needs human intervention:

<AccordionGroup>
  <Accordion title="Human Review Node">
    * Context for decision: Original email, draft response, urgency, classification
    * Expected input format: Approval boolean plus optional edited response
    * When triggered: High urgency, complex issues, or quality concerns
  </Accordion>
</AccordionGroup>

## Step 3: Design your state

State is the shared [memory](/oss/python/concepts/memory) accessible to all nodes in your agent. Think of it as the notebook your agent uses to keep track of everything it learns and decides as it works through the process.

### What belongs in state?

Ask yourself these questions about each piece of data:

<CardGroup cols={2}>
  <Card title="Include in State" icon="check">
    Does it need to persist across steps? If yes, it goes in state.
  </Card>

<Card title="Don't Store" icon="code">
    Can you derive it from other data? If yes, compute it when needed instead of storing it in state.
  </Card>
</CardGroup>

For our email agent, we need to track:

* The original email and sender info (can't reconstruct these)
* Classification results (needed by multiple downstream nodes)
* Search results and customer data (expensive to re-fetch)
* The draft response (needs to persist through review)
* Execution metadata (for debugging and recovery)

### Keep state raw, format prompts on-demand

<Tip>
  A key principle: your state should store raw data, not formatted text. Format prompts inside nodes when you need them.
</Tip>

This separation means:

* Different nodes can format the same data differently for their needs
* You can change prompt templates without modifying your state schema
* Debugging is clearer - you see exactly what data each node received
* Your agent can evolve without breaking existing state

Let's define our state:

```python  theme={null}
from typing import TypedDict, Literal

**Examples:**

Example 1 (unknown):
```unknown
The arrows show possible paths, but the actual decision of which path to take happens inside each node.

Now that you've identified the components in your workflow, let's understand what each node needs to do:

* Read Email: Extract and parse the email content
* Classify Intent: Use an LLM to categorize urgency and topic, then route to appropriate action
* Doc Search: Query your knowledge base for relevant information
* Bug Track: Create or update issue in tracking system
* Draft Reply: Generate an appropriate response
* Human Review: Escalate to human agent for approval or handling
* Send Reply: Dispatch the email response

<Tip>
  Notice that some nodes make decisions about where to go next (Classify Intent, Draft Reply, Human Review), while others always proceed to the same next step (Read Email always goes to Classify Intent, Doc Search always goes to Draft Reply).
</Tip>

## Step 2: Identify what each step needs to do

For each node in your graph, determine what type of operation it represents and what context it needs to work properly.

<CardGroup cols={2}>
  <Card title="LLM Steps" icon="brain" href="#llm-steps">
    Use when you need to understand, analyze, generate text, or make reasoning decisions
  </Card>

  <Card title="Data Steps" icon="database" href="#data-steps">
    Use when you need to retrieve information from external sources
  </Card>

  <Card title="Action Steps" icon="bolt" href="#action-steps">
    Use when you need to perform external actions
  </Card>

  <Card title="User Input Steps" icon="user" href="#user-input-steps">
    Use when you need human intervention
  </Card>
</CardGroup>

### LLM Steps

When a step needs to understand, analyze, generate text, or make reasoning decisions:

<AccordionGroup>
  <Accordion title="Classify Intent Node">
    * Static context (prompt): Classification categories, urgency definitions, response format
    * Dynamic context (from state): Email content, sender information
    * Desired outcome: Structured classification that determines routing
  </Accordion>

  <Accordion title="Draft Reply Node">
    * Static context (prompt): Tone guidelines, company policies, response templates
    * Dynamic context (from state): Classification results, search results, customer history
    * Desired outcome: Professional email response ready for review
  </Accordion>
</AccordionGroup>

### Data Steps

When a step needs to retrieve information from external sources:

<AccordionGroup>
  <Accordion title="Document Search Node">
    * Parameters: Query built from intent and topic
    * Retry strategy: Yes, with exponential backoff for transient failures
    * Caching: Could cache common queries to reduce API calls
  </Accordion>

  <Accordion title="Customer History Lookup">
    * Parameters: Customer email or ID from state
    * Retry strategy: Yes, but with fallback to basic info if unavailable
    * Caching: Yes, with time-to-live to balance freshness and performance
  </Accordion>
</AccordionGroup>

### Action Steps

When a step needs to perform an external action:

<AccordionGroup>
  <Accordion title="Send Reply Node">
    * When to execute: After approval (human or automated)
    * Retry strategy: Yes, with exponential backoff for network issues
    * Should not cache: Each send is a unique action
  </Accordion>

  <Accordion title="Bug Track Node">
    * When to execute: Always when intent is "bug"
    * Retry strategy: Yes, critical to not lose bug reports
    * Returns: Ticket ID to include in response
  </Accordion>
</AccordionGroup>

### User Input Steps

When a step needs human intervention:

<AccordionGroup>
  <Accordion title="Human Review Node">
    * Context for decision: Original email, draft response, urgency, classification
    * Expected input format: Approval boolean plus optional edited response
    * When triggered: High urgency, complex issues, or quality concerns
  </Accordion>
</AccordionGroup>

## Step 3: Design your state

State is the shared [memory](/oss/python/concepts/memory) accessible to all nodes in your agent. Think of it as the notebook your agent uses to keep track of everything it learns and decides as it works through the process.

### What belongs in state?

Ask yourself these questions about each piece of data:

<CardGroup cols={2}>
  <Card title="Include in State" icon="check">
    Does it need to persist across steps? If yes, it goes in state.
  </Card>

  <Card title="Don't Store" icon="code">
    Can you derive it from other data? If yes, compute it when needed instead of storing it in state.
  </Card>
</CardGroup>

For our email agent, we need to track:

* The original email and sender info (can't reconstruct these)
* Classification results (needed by multiple downstream nodes)
* Search results and customer data (expensive to re-fetch)
* The draft response (needs to persist through review)
* Execution metadata (for debugging and recovery)

### Keep state raw, format prompts on-demand

<Tip>
  A key principle: your state should store raw data, not formatted text. Format prompts inside nodes when you need them.
</Tip>

This separation means:

* Different nodes can format the same data differently for their needs
* You can change prompt templates without modifying your state schema
* Debugging is clearer - you see exactly what data each node received
* Your agent can evolve without breaking existing state

Let's define our state:
```

---

## Observability

**URL:** llms-txt#observability

**Contents:**
- Prerequisites
- Enable tracing
- Trace selectively

Source: https://docs.langchain.com/oss/python/langgraph/observability

Traces are a series of steps that your application takes to go from input to output. Each of these individual steps is represented by a run. You can use [LangSmith](https://smith.langchain.com/) to visualize these execution steps. To use it, [enable tracing for your application](/langsmith/trace-with-langgraph). This enables you to do the following:

* [Debug a locally running application](/langsmith/observability-studio#debug-langsmith-traces).
* [Evaluate the application performance](/oss/python/langchain/evals).
* [Monitor the application](/langsmith/dashboards).

Before you begin, ensure you have the following:

* A [LangSmith account](https://smith.langchain.com/) (free to sign up)

To enable tracing for your application, set the following environment variables:

By default, the trace will be logged to the project with the name `default`. To configure a custom project name, see [Log to a project](#log-to-a-project).

For more information, see [Trace with LangGraph](/langsmith/trace-with-langgraph).

You may opt to trace specific invocations or parts of your application using LangSmith's `tracing_context` context manager:

```python  theme={null}
import langsmith as ls

**Examples:**

Example 1 (unknown):
```unknown
By default, the trace will be logged to the project with the name `default`. To configure a custom project name, see [Log to a project](#log-to-a-project).

For more information, see [Trace with LangGraph](/langsmith/trace-with-langgraph).

## Trace selectively

You may opt to trace specific invocations or parts of your application using LangSmith's `tracing_context` context manager:
```

---

## Workflow execution configuration with a unique thread identifier

**URL:** llms-txt#workflow-execution-configuration-with-a-unique-thread-identifier

config = {
    "configurable": {
        "thread_id": "1"  # Unique identifier to track workflow execution
    }
}

---

## How to evaluate a graph

**URL:** llms-txt#how-to-evaluate-a-graph

**Contents:**
- End-to-end evaluations
  - Define a graph

Source: https://docs.langchain.com/langsmith/evaluate-graph

<Info>
  [langgraph](https://langchain-ai.github.io/langgraph/)
</Info>

`langgraph` is a library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows. Evaluating `langgraph` graphs can be challenging because a single invocation can involve many LLM calls, and which LLM calls are made may depend on the outputs of preceding calls. In this guide we will focus on the mechanics of how to pass graphs and graph nodes to `evaluate()` / `aevaluate()`. For evaluation techniques and best practices when building agents head to the [langgraph docs](https://langchain-ai.github.io/langgraph/tutorials/#evaluation).

## End-to-end evaluations

The most common type of evaluation is an end-to-end one, where we want to evaluate the final graph output for each example input.

Lets construct a simple ReACT agent to start:

```python  theme={null}
from typing import Annotated, Literal, TypedDict
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Messages have the type "list". The 'add_messages' function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

---

## Parent graph

**URL:** llms-txt#parent-graph

**Contents:**
- View subgraph state
- Stream subgraph outputs

builder = StateGraph(State)
builder.add_node("node_1", subgraph)
builder.add_edge(START, "node_1")

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
python  theme={null}
subgraph_builder = StateGraph(...)
subgraph = subgraph_builder.compile(checkpointer=True)
python  theme={null}
  from langgraph.graph import START, StateGraph
  from langgraph.checkpoint.memory import MemorySaver
  from langgraph.types import interrupt, Command
  from typing_extensions import TypedDict

class State(TypedDict):
      foo: str

def subgraph_node_1(state: State):
      value = interrupt("Provide value:")
      return {"foo": state["foo"] + value}

subgraph_builder = StateGraph(State)
  subgraph_builder.add_node(subgraph_node_1)
  subgraph_builder.add_edge(START, "subgraph_node_1")

subgraph = subgraph_builder.compile()

builder = StateGraph(State)
  builder.add_node("node_1", subgraph)
  builder.add_edge(START, "node_1")

checkpointer = MemorySaver()
  graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}

graph.invoke({"foo": ""}, config)
  parent_state = graph.get_state(config)

# This will be available only when the subgraph is interrupted.
  # Once you resume the graph, you won't be able to access the subgraph state.
  subgraph_state = graph.get_state(config, subgraphs=True).tasks[0].state

# resume the subgraph
  graph.invoke(Command(resume="bar"), config)
  python  theme={null}
for chunk in graph.stream(
    {"foo": "foo"},
    subgraphs=True, # [!code highlight]
    stream_mode="updates",
):
    print(chunk)
python  theme={null}
  from typing_extensions import TypedDict
  from langgraph.graph.state import StateGraph, START

# Define subgraph
  class SubgraphState(TypedDict):
      foo: str
      bar: str

def subgraph_node_1(state: SubgraphState):
      return {"bar": "bar"}

def subgraph_node_2(state: SubgraphState):
      # note that this node is using a state key ('bar') that is only available in the subgraph
      # and is sending update on the shared state key ('foo')
      return {"foo": state["foo"] + state["bar"]}

subgraph_builder = StateGraph(SubgraphState)
  subgraph_builder.add_node(subgraph_node_1)
  subgraph_builder.add_node(subgraph_node_2)
  subgraph_builder.add_edge(START, "subgraph_node_1")
  subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
  subgraph = subgraph_builder.compile()

# Define parent graph
  class ParentState(TypedDict):
      foo: str

def node_1(state: ParentState):
      return {"foo": "hi! " + state["foo"]}

builder = StateGraph(ParentState)
  builder.add_node("node_1", node_1)
  builder.add_node("node_2", subgraph)
  builder.add_edge(START, "node_1")
  builder.add_edge("node_1", "node_2")
  graph = builder.compile()

for chunk in graph.stream(
      {"foo": "foo"},
      stream_mode="updates",
      subgraphs=True, # [!code highlight]
  ):
      print(chunk)
  
  ((), {'node_1': {'foo': 'hi! foo'}})
  (('node_2:e58e5673-a661-ebb0-70d4-e298a7fc28b7',), {'subgraph_node_1': {'bar': 'bar'}})
  (('node_2:e58e5673-a661-ebb0-70d4-e298a7fc28b7',), {'subgraph_node_2': {'foo': 'hi! foobar'}})
  ((), {'node_2': {'foo': 'hi! foobar'}})
  ```
</Accordion>

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/langgraph/use-subgraphs.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
If you want the subgraph to **have its own memory**, you can compile it with the appropriate checkpointer option. This is useful in [multi-agent](/oss/python/langchain/multi-agent) systems, if you want agents to keep track of their internal message histories:
```

Example 2 (unknown):
```unknown
## View subgraph state

When you enable [persistence](/oss/python/langgraph/persistence), you can [inspect the graph state](/oss/python/langgraph/persistence#checkpoints) (checkpoint) via the appropriate method. To view the subgraph state, you can use the subgraphs option.

You can inspect the graph state via `graph.get_state(config)`. To view the subgraph state, you can use `graph.get_state(config, subgraphs=True)`.

<Warning>
  **Available **only** when interrupted**
  Subgraph state can only be viewed **when the subgraph is interrupted**. Once you resume the graph, you won't be able to access the subgraph state.
</Warning>

<Accordion title="View interrupted subgraph state">
```

Example 3 (unknown):
```unknown
1. This will be available only when the subgraph is interrupted. Once you resume the graph, you won't be able to access the subgraph state.
</Accordion>

## Stream subgraph outputs

To include outputs from subgraphs in the streamed outputs, you can set the subgraphs option in the stream method of the parent graph. This will stream outputs from both the parent graph and any subgraphs.
```

Example 4 (unknown):
```unknown
<Accordion title="Stream from subgraphs">
```

---

## Run the graph

**URL:** llms-txt#run-the-graph

**Contents:**
- Use user-scoped MCP tools in your deployment
- Session behavior
- Authentication
- Disable MCP

print(graph.invoke({"question": "hi"}))
python  theme={null}
from langchain_mcp_adapters.client import MultiServerMCPClient

def mcp_tools_node(state, config):
    user = config["configurable"].get("langgraph_auth_user")
         , user["github_token"], user["email"], etc.

client = MultiServerMCPClient({
        "github": {
            "transport": "streamable_http", # (1)
            "url": "https://my-github-mcp-server/mcp", # (2)
            "headers": {
                "Authorization": f"Bearer {user['github_token']}"
            }
        }
    })
    tools = await client.get_tools() # (3)

# Your tool-calling logic here

tool_messages = ...
    return {"messages": tool_messages}
json  theme={null}
{
  "http": {
    "disable_mcp": true
  }
}
```

This will prevent the server from exposing the `/mcp` endpoint.

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/server-mcp.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
For more details, see the [low-level concepts guide](/oss/python/langgraph/graph-api#state).

## Use user-scoped MCP tools in your deployment

<Tip>
  **Prerequisites**
  You have added your own [custom auth middleware](/langsmith/custom-auth) that populates the `langgraph_auth_user` object, making it accessible through configurable context for every node in your graph.
</Tip>

To make user-scoped tools available to your LangSmith deployment, start with implementing a snippet like the following:
```

Example 2 (unknown):
```unknown
1. MCP only supports adding headers to requests made to `streamable_http` and `sse` `transport` servers.
2. Your MCP server URL.
3. Get available tools from your MCP server.

*This can also be done by [rebuilding your graph at runtime](/langsmith/graph-rebuild) to have a different configuration for a new run*

## Session behavior

The current LangGraph MCP implementation does not support sessions. Each `/mcp` request is stateless and independent.

## Authentication

The `/mcp` endpoint uses the same authentication as the rest of the LangGraph API. Refer to the [authentication guide](/langsmith/auth) for setup details.

## Disable MCP

To disable the MCP endpoint, set `disable_mcp` to `true` in your `langgraph.json` configuration file:
```

---

## Extraction schema, mirrors the graph state.

**URL:** llms-txt#extraction-schema,-mirrors-the-graph-state.

class PurchaseInformation(TypedDict):
    """All of the known information about the invoice / invoice lines the customer would like refunded. Do not make up values, leave fields as null if you don't know their value."""

invoice_id: int | None
    invoice_line_ids: list[int] | None
    customer_first_name: str | None
    customer_last_name: str | None
    customer_phone: str | None
    track_name: str | None
    album_title: str | None
    artist_name: str | None
    purchase_date_iso_8601: str | None
    followup: Annotated[
        str | None,
        ...,
        "If the user hasn't enough identifying information, please tell them what the required information is and ask them to specify it.",
    ]

---

## The "Auth" object is a container that LangGraph will use to mark our authentication function

**URL:** llms-txt#the-"auth"-object-is-a-container-that-langgraph-will-use-to-mark-our-authentication-function

---

## LangGraph JS/TS SDK

**URL:** llms-txt#langgraph-js/ts-sdk

Source: https://docs.langchain.com/langsmith/langgraph-js-ts-sdk

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/langgraph-js-ts-sdk.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## Evaluation job and results

**URL:** llms-txt#evaluation-job-and-results

**Contents:**
  - Trajectory evaluator
  - Single step evaluators

experiment_results = await client.aevaluate(
    run_graph,
    data=dataset_name,
    evaluators=[final_answer_correct],
    experiment_prefix="sql-agent-gpt4o-e2e",
    num_repetitions=1,
    max_concurrency=4,
)
experiment_results.to_pandas()
python  theme={null}
def trajectory_subsequence(outputs: dict, reference_outputs: dict) -> float:
    """Check how many of the desired steps the agent took."""
    if len(reference_outputs['trajectory']) > len(outputs['trajectory']):
        return False

i = j = 0
    while i < len(reference_outputs['trajectory']) and j < len(outputs['trajectory']):
        if reference_outputs['trajectory'][i] == outputs['trajectory'][j]:
            i += 1
        j += 1

return i / len(reference_outputs['trajectory'])
python  theme={null}
async def run_graph(inputs: dict) -> dict:
    """Run graph and track the trajectory it takes along with the final response."""
    trajectory = []
    # Set subgraph=True to stream events from subgraphs of the main graph: https://langchain-ai.github.io/langgraph/how-tos/streaming-subgraphs/
    # Set stream_mode="debug" to stream all possible events: https://langchain-ai.github.io/langgra/langsmith/observability-concepts/streaming
    async for namespace, chunk in graph.astream({"messages": [
            {
                "role": "user",
                "content": inputs['question'],
            }
        ]}, subgraphs=True, stream_mode="debug"):
        # Event type for entering a node
        if chunk['type'] == 'task':
            # Record the node name
            trajectory.append(chunk['payload']['name'])
            # Given how we defined our dataset, we also need to track when specific tools are
            # called by our question answering ReACT agent. These tool calls can be found
            # when the ToolsNode (named "tools") is invoked by looking at the AIMessage.tool_calls
            # of the latest input message.
            if chunk['payload']['name'] == 'tools' and chunk['type'] == 'task':
                for tc in chunk['payload']['input']['messages'][-1].tool_calls:
                    trajectory.append(tc['name'])
    return {"trajectory": trajectory}

experiment_results = await client.aevaluate(
    run_graph,
    data=dataset_name,
    evaluators=[trajectory_subsequence],
    experiment_prefix="sql-agent-gpt4o-trajectory",
    num_repetitions=1,
    max_concurrency=4,
)
experiment_results.to_pandas()
python  theme={null}

**Examples:**

Example 1 (unknown):
```unknown
You can see what these results look like here: [LangSmith link](https://smith.langchain.com/public/708d08f4-300e-4c75-9677-c6b71b0d28c9/d).

### Trajectory evaluator

As agents become more complex, they have more potential points of failure. Rather than using simple pass/fail evaluations, it's often better to use evaluations that can give partial credit when an agent takes some correct steps, even if it doesn't reach the right final answer.

This is where trajectory evaluations come in. A trajectory evaluation:

1. Compares the actual sequence of steps the agent took against an expected sequence
2. Calculates a score based on how many of the expected steps were completed correctly

For this example, our end-to-end dataset contains an ordered list of steps that we expect the agent to take. Let's create an evaluator that checks the agent's actual trajectory against these expected steps and calculates what percentage were completed:
```

Example 2 (unknown):
```unknown
Now we can run our evaluation. Our evaluator assumes that our target function returns a 'trajectory' key, so lets define a target function that does so. We'll need to usage [LangGraph's streaming capabilities](https://langchain-ai.github.io/langgra/langsmith/observability-concepts/streaming/) to record the trajectory.

Note that we are reusing the same dataset as for our final response evaluation, so we could have run both evaluators together and defined a target function that returns both "response" and "trajectory". In practice it's often useful to have separate datasets for each type of evaluation, which is why we show them separately here:
```

Example 3 (unknown):
```unknown
You can see what these results look like here: [LangSmith link](https://smith.langchain.com/public/708d08f4-300e-4c75-9677-c6b71b0d28c9/d).

### Single step evaluators

While end-to-end tests give you the most signal about your agents performance, for the sake of debugging and iterating on your agent it can be helpful to pinpoint specific steps that are difficult and evaluate them directly.

In our case, a crucial part of our agent is that it routes the user's intention correctly into either the "refund" path or the "question answering" path. Let's create a dataset and run some evaluations to directly stress test this one component.
```

---

## How to implement generative user interfaces with LangGraph

**URL:** llms-txt#how-to-implement-generative-user-interfaces-with-langgraph

**Contents:**
- Tutorial
  - 1. Define and configure UI components
  - 2. Send the UI components in your graph
  - 3. Handle UI elements in your React application
- How-to guides
  - Provide custom components on the client side
  - Show loading UI when components are loading
  - Customise the namespace of UI components.
  - Access and interact with the thread state from the UI component
  - Pass additional context to the client components

Source: https://docs.langchain.com/langsmith/generative-ui-react

<Info>
  **Prerequisites**

* [LangSmith](/langsmith/home)
  * [Agent Server](/langsmith/agent-server)
  * [`useStream()` React Hook](/langsmith/use-stream-react)
</Info>

Generative user interfaces (Generative UI) allows agents to go beyond text and generate rich user interfaces. This enables creating more interactive and context-aware applications where the UI adapts based on the conversation flow and AI responses.

<img src="https://mintcdn.com/langchain-5e9cc07a/JOyLr_spVEW0t2KF/langsmith/images/generative-ui-sample.jpg?fit=max&auto=format&n=JOyLr_spVEW0t2KF&q=85&s=105943c6c28853fad0a9bc3b4af3a999" alt="Agent Chat showing a prompt about booking/lodging and a generated set of hotel listing cards (images, titles, prices, locations) rendered inline as UI components." data-og-width="1814" width="1814" data-og-height="898" height="898" data-path="langsmith/images/generative-ui-sample.jpg" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/JOyLr_spVEW0t2KF/langsmith/images/generative-ui-sample.jpg?w=280&fit=max&auto=format&n=JOyLr_spVEW0t2KF&q=85&s=0fd526a7132d33ab6f72002d68a66dec 280w, https://mintcdn.com/langchain-5e9cc07a/JOyLr_spVEW0t2KF/langsmith/images/generative-ui-sample.jpg?w=560&fit=max&auto=format&n=JOyLr_spVEW0t2KF&q=85&s=0c9ffe86700a7b8404f1fdf51b906aa1 560w, https://mintcdn.com/langchain-5e9cc07a/JOyLr_spVEW0t2KF/langsmith/images/generative-ui-sample.jpg?w=840&fit=max&auto=format&n=JOyLr_spVEW0t2KF&q=85&s=50652e58566db8171ead4aef57d78fa6 840w, https://mintcdn.com/langchain-5e9cc07a/JOyLr_spVEW0t2KF/langsmith/images/generative-ui-sample.jpg?w=1100&fit=max&auto=format&n=JOyLr_spVEW0t2KF&q=85&s=a764d790719e8233313fabe4cee93958 1100w, https://mintcdn.com/langchain-5e9cc07a/JOyLr_spVEW0t2KF/langsmith/images/generative-ui-sample.jpg?w=1650&fit=max&auto=format&n=JOyLr_spVEW0t2KF&q=85&s=a02d8d6ecace7eee6df55e3a391c09e2 1650w, https://mintcdn.com/langchain-5e9cc07a/JOyLr_spVEW0t2KF/langsmith/images/generative-ui-sample.jpg?w=2500&fit=max&auto=format&n=JOyLr_spVEW0t2KF&q=85&s=b0709ca94bd9533f5ef5a80da1d60bf6 2500w" />

LangSmith supports colocating your React components with your graph code. This allows you to focus on building specific UI components for your graph while easily plugging into existing chat interfaces such as [Agent Chat](https://agentchat.vercel.app) and loading the code only when actually needed.

### 1. Define and configure UI components

First, create your first UI component. For each component you need to provide an unique identifier that will be used to reference the component in your graph code.

Next, define your UI components in your `langgraph.json` configuration:

The `ui` section points to the UI components that will be used by graphs. By default, we recommend using the same key as the graph name, but you can split out the components however you like, see [Customise the namespace of UI components](#customise-the-namespace-of-ui-components) for more details.

LangSmith will automatically bundle your UI components code and styles and serve them as external assets that can be loaded by the `LoadExternalComponent` component. Some dependencies such as `react` and `react-dom` will be automatically excluded from the bundle.

CSS and Tailwind 4.x is also supported out of the box, so you can freely use Tailwind classes as well as `shadcn/ui` in your UI components.

<Tabs>
  <Tab title="src/agent/ui.tsx">
    
  </Tab>

<Tab title="src/agent/styles.css">
    
  </Tab>
</Tabs>

### 2. Send the UI components in your graph

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="JS">
    Use the `typedUi` utility to emit UI elements from your agent nodes:

### 3. Handle UI elements in your React application

On the client side, you can use `useStream()` and `LoadExternalComponent` to display the UI elements.

Behind the scenes, `LoadExternalComponent` will fetch the JS and CSS for the UI components from LangSmith and render them in a shadow DOM, thus ensuring style isolation from the rest of your application.

### Provide custom components on the client side

If you already have the components loaded in your client application, you can provide a map of such components to be rendered directly without fetching the UI code from LangSmith.

### Show loading UI when components are loading

You can provide a fallback UI to be rendered when the components are loading.

### Customise the namespace of UI components.

By default `LoadExternalComponent` will use the `assistantId` from `useStream()` hook to fetch the code for UI components. You can customise this by providing a `namespace` prop to the `LoadExternalComponent` component.

<Tabs>
  <Tab title="src/app/page.tsx">
    
  </Tab>

<Tab title="langgraph.json">
    
  </Tab>
</Tabs>

### Access and interact with the thread state from the UI component

You can access the thread state inside the UI component by using the `useStreamContext` hook.

### Pass additional context to the client components

You can pass additional context to the client components by providing a `meta` prop to the `LoadExternalComponent` component.

Then, you can access the `meta` prop in the UI component by using the `useStreamContext` hook.

### Streaming UI messages from the server

You can stream UI messages before the node execution is finished by using the `onCustomEvent` callback of the `useStream()` hook. This is especially useful when updating the UI component as the LLM is generating the response.

Then you can push updates to the UI component by calling `ui.push()` / `push_ui_message()` with the same ID as the UI message you wish to update.

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="JS">
    
  </Tab>

<Tab title="ui.tsx">
    
  </Tab>
</Tabs>

### Remove UI messages from state

Similar to how messages can be removed from the state by appending a RemoveMessage you can remove an UI message from the state by calling `remove_ui_message` / `ui.delete` with the ID of the UI message.

<Tabs>
  <Tab title="Python">
    
  </Tab>

<Tab title="JS">
    
  </Tab>
</Tabs>

* [JS/TS SDK Reference](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html)

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/generative-ui-react.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
Next, define your UI components in your `langgraph.json` configuration:
```

Example 2 (unknown):
```unknown
The `ui` section points to the UI components that will be used by graphs. By default, we recommend using the same key as the graph name, but you can split out the components however you like, see [Customise the namespace of UI components](#customise-the-namespace-of-ui-components) for more details.

LangSmith will automatically bundle your UI components code and styles and serve them as external assets that can be loaded by the `LoadExternalComponent` component. Some dependencies such as `react` and `react-dom` will be automatically excluded from the bundle.

CSS and Tailwind 4.x is also supported out of the box, so you can freely use Tailwind classes as well as `shadcn/ui` in your UI components.

<Tabs>
  <Tab title="src/agent/ui.tsx">
```

Example 3 (unknown):
```unknown
</Tab>

  <Tab title="src/agent/styles.css">
```

Example 4 (unknown):
```unknown
</Tab>
</Tabs>

### 2. Send the UI components in your graph

<Tabs>
  <Tab title="Python">
```

---

## Building our graph

**URL:** llms-txt#building-our-graph

graph_builder = StateGraph(State)

graph_builder.add_node(gather_info)
graph_builder.add_node(refund)
graph_builder.add_node(lookup)

graph_builder.set_entry_point("gather_info")
graph_builder.add_edge("lookup", END)
graph_builder.add_edge("refund", END)

refund_graph = graph_builder.compile()

**Examples:**

Example 1 (unknown):
```unknown
We can visualize our refund graph:
```

---

## 2. Define a graph that accesses the config in a node

**URL:** llms-txt#2.-define-a-graph-that-accesses-the-config-in-a-node

class State(TypedDict):
    my_state_value: str

def node(state: State, runtime: Runtime[ContextSchema]):  # [!code highlight]
    if runtime.context["my_runtime_value"] == "a":  # [!code highlight]
        return {"my_state_value": 1}
    elif runtime.context["my_runtime_value"] == "b":  # [!code highlight]
        return {"my_state_value": 2}
    else:
        raise ValueError("Unknown values.")

builder = StateGraph(State, context_schema=ContextSchema)  # [!code highlight]
builder.add_node(node)
builder.add_edge(START, "node")
builder.add_edge("node", END)

graph = builder.compile()

---

## Streaming

**URL:** llms-txt#streaming

**Contents:**
- Supported stream modes
- Basic usage example
- Stream multiple modes
- Stream graph state
- Stream subgraph outputs
  - Debugging
- LLM tokens

Source: https://docs.langchain.com/oss/python/langgraph/streaming

LangGraph implements a streaming system to surface real-time updates. Streaming is crucial for enhancing the responsiveness of applications built on LLMs. By displaying output progressively, even before a complete response is ready, streaming significantly improves user experience (UX), particularly when dealing with the latency of LLMs.

What's possible with LangGraph streaming:

* <Icon icon="share-nodes" size={16} /> [**Stream graph state**](#stream-graph-state) — get state updates / values with `updates` and `values` modes.
* <Icon icon="square-poll-horizontal" size={16} /> [**Stream subgraph outputs**](#stream-subgraph-outputs) — include outputs from both the parent graph and any nested subgraphs.
* <Icon icon="square-binary" size={16} /> [**Stream LLM tokens**](#messages) — capture token streams from anywhere: inside nodes, subgraphs, or tools.
* <Icon icon="table" size={16} /> [**Stream custom data**](#stream-custom-data) — send custom updates or progress signals directly from tool functions.
* <Icon icon="layer-plus" size={16} /> [**Use multiple streaming modes**](#stream-multiple-modes) — choose from `values` (full state), `updates` (state deltas), `messages` (LLM tokens + metadata), `custom` (arbitrary user data), or `debug` (detailed traces).

## Supported stream modes

Pass one or more of the following stream modes as a list to the [`stream`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.stream) or [`astream`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.astream) methods:

| Mode       | Description                                                                                                                                                                         |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `values`   | Streams the full value of the state after each step of the graph.                                                                                                                   |
| `updates`  | Streams the updates to the state after each step of the graph. If multiple updates are made in the same step (e.g., multiple nodes are run), those updates are streamed separately. |
| `custom`   | Streams custom data from inside your graph nodes.                                                                                                                                   |
| `messages` | Streams 2-tuples (LLM token, metadata) from any graph nodes where an LLM is invoked.                                                                                                |
| `debug`    | Streams as much information as possible throughout the execution of the graph.                                                                                                      |

## Basic usage example

LangGraph graphs expose the [`stream`](https://reference.langchain.com/python/langgraph/pregel/#langgraph.pregel.Pregel.stream) (sync) and [`astream`](https://reference.langchain.com/python/langgraph/pregel/#langgraph.pregel.Pregel.astream) (async) methods to yield streamed outputs as iterators.

<Accordion title="Extended example: streaming updates">

## Stream multiple modes

You can pass a list as the `stream_mode` parameter to stream multiple modes at once.

The streamed outputs will be tuples of `(mode, chunk)` where `mode` is the name of the stream mode and `chunk` is the data streamed by that mode.

## Stream graph state

Use the stream modes `updates` and `values` to stream the state of the graph as it executes.

* `updates` streams the **updates** to the state after each step of the graph.
* `values` streams the **full value** of the state after each step of the graph.

<Tabs>
  <Tab title="updates">
    Use this to stream only the **state updates** returned by the nodes after each step. The streamed outputs include the name of the node as well as the update.

<Tab title="values">
    Use this to stream the **full state** of the graph after each step.

## Stream subgraph outputs

To include outputs from [subgraphs](/oss/python/langgraph/use-subgraphs) in the streamed outputs, you can set `subgraphs=True` in the `.stream()` method of the parent graph. This will stream outputs from both the parent graph and any subgraphs.

The outputs will be streamed as tuples `(namespace, data)`, where `namespace` is a tuple with the path to the node where a subgraph is invoked, e.g. `("parent_node:<task_id>", "child_node:<task_id>")`.

<Accordion title="Extended example: streaming from subgraphs">

**Note** that we are receiving not just the node updates, but we also the namespaces which tell us what graph (or subgraph) we are streaming from.
</Accordion>

Use the `debug` streaming mode to stream as much information as possible throughout the execution of the graph. The streamed outputs include the name of the node as well as the full state.

Use the `messages` streaming mode to stream Large Language Model (LLM) outputs **token by token** from any part of your graph, including nodes, tools, subgraphs, or tasks.

The streamed output from [`messages` mode](#supported-stream-modes) is a tuple `(message_chunk, metadata)` where:

* `message_chunk`: the token or message segment from the LLM.
* `metadata`: a dictionary containing details about the graph node and LLM invocation.

> If your LLM is not available as a LangChain integration, you can stream its outputs using `custom` mode instead. See [use with any LLM](#use-with-any-llm) for details.

<Warning>
  **Manual config required for async in Python \< 3.11**
  When using Python \< 3.11 with async code, you must explicitly pass [`RunnableConfig`](https://reference.langchain.com/python/langchain_core/runnables/#langchain_core.runnables.RunnableConfig) to `ainvoke()` to enable proper streaming. See [Async with Python \< 3.11](#async) for details or upgrade to Python 3.11+.
</Warning>

```python  theme={null}
from dataclasses import dataclass

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START

@dataclass
class MyState:
    topic: str
    joke: str = ""

model = init_chat_model(model="gpt-4o-mini")

def call_model(state: MyState):
    """Call the LLM to generate a joke about a topic"""
    # Note that message events are emitted even when the LLM is run using .invoke rather than .stream
    model_response = model.invoke(  # [!code highlight]
        [
            {"role": "user", "content": f"Generate a joke about {state.topic}"}
        ]
    )
    return {"joke": model_response.content}

graph = (
    StateGraph(MyState)
    .add_node(call_model)
    .add_edge(START, "call_model")
    .compile()
)

**Examples:**

Example 1 (unknown):
```unknown
<Accordion title="Extended example: streaming updates">
```

Example 2 (unknown):
```unknown

```

Example 3 (unknown):
```unknown
</Accordion>

## Stream multiple modes

You can pass a list as the `stream_mode` parameter to stream multiple modes at once.

The streamed outputs will be tuples of `(mode, chunk)` where `mode` is the name of the stream mode and `chunk` is the data streamed by that mode.
```

Example 4 (unknown):
```unknown
## Stream graph state

Use the stream modes `updates` and `values` to stream the state of the graph as it executes.

* `updates` streams the **updates** to the state after each step of the graph.
* `values` streams the **full value** of the state after each step of the graph.
```

---

## Decide whether to retrieve

**URL:** llms-txt#decide-whether-to-retrieve

workflow.add_conditional_edges(
    "generate_query_or_respond",
    # Assess LLM decision (call `retriever_tool` tool or respond to the user)
    tools_condition,
    {
        # Translate the condition outputs to nodes in our graph
        "tools": "retrieve",
        END: END,
    },
)

---

## Graph state

**URL:** llms-txt#graph-state

class State(TypedDict):
    topic: str  # Report topic
    sections: list[Section]  # List of report sections
    completed_sections: Annotated[
        list, operator.add
    ]  # All workers write to this key in parallel
    final_report: str  # Final report

---

## Durable execution

**URL:** llms-txt#durable-execution

**Contents:**
- Requirements
- Determinism and Consistent Replay
- Durability modes
  - `"exit"`
  - `"async"`
  - `"sync"`
- Using tasks in nodes
- Resuming Workflows
- Starting Points for Resuming Workflows

Source: https://docs.langchain.com/oss/python/langgraph/durable-execution

**Durable execution** is a technique in which a process or workflow saves its progress at key points, allowing it to pause and later resume exactly where it left off. This is particularly useful in scenarios that require [human-in-the-loop](/oss/python/langgraph/interrupts), where users can inspect, validate, or modify the process before continuing, and in long-running tasks that might encounter interruptions or errors (e.g., calls to an LLM timing out). By preserving completed work, durable execution enables a process to resume without reprocessing previous steps -- even after a significant delay (e.g., a week later).

LangGraph's built-in [persistence](/oss/python/langgraph/persistence) layer provides durable execution for workflows, ensuring that the state of each execution step is saved to a durable store. This capability guarantees that if a workflow is interrupted -- whether by a system failure or for [human-in-the-loop](/oss/python/langgraph/interrupts) interactions -- it can be resumed from its last recorded state.

<Tip>
  If you are using LangGraph with a checkpointer, you already have durable execution enabled. You can pause and resume workflows at any point, even after interruptions or failures.
  To make the most of durable execution, ensure that your workflow is designed to be [deterministic](#determinism-and-consistent-replay) and [idempotent](#determinism-and-consistent-replay) and wrap any side effects or non-deterministic operations inside [tasks](/oss/python/langgraph/functional-api#task). You can use [tasks](/oss/python/langgraph/functional-api#task) from both the [StateGraph (Graph API)](/oss/python/langgraph/graph-api) and the [Functional API](/oss/python/langgraph/functional-api).
</Tip>

To leverage durable execution in LangGraph, you need to:

1. Enable [persistence](/oss/python/langgraph/persistence) in your workflow by specifying a [checkpointer](/oss/python/langgraph/persistence#checkpointer-libraries) that will save workflow progress.

2. Specify a [thread identifier](/oss/python/langgraph/persistence#threads) when executing a workflow. This will track the execution history for a particular instance of the workflow.

3. Wrap any non-deterministic operations (e.g., random number generation) or operations with side effects (e.g., file writes, API calls) inside @\[`task`] to ensure that when a workflow is resumed, these operations are not repeated for the particular run, and instead their results are retrieved from the persistence layer. For more information, see [Determinism and Consistent Replay](#determinism-and-consistent-replay).

## Determinism and Consistent Replay

When you resume a workflow run, the code does **NOT** resume from the **same line of code** where execution stopped; instead, it will identify an appropriate [starting point](#starting-points-for-resuming-workflows) from which to pick up where it left off. This means that the workflow will replay all steps from the [starting point](#starting-points-for-resuming-workflows) until it reaches the point where it was stopped.

As a result, when you are writing a workflow for durable execution, you must wrap any non-deterministic operations (e.g., random number generation) and any operations with side effects (e.g., file writes, API calls) inside [tasks](/oss/python/langgraph/functional-api#task) or [nodes](/oss/python/langgraph/graph-api#nodes).

To ensure that your workflow is deterministic and can be consistently replayed, follow these guidelines:

* **Avoid Repeating Work**: If a [node](/oss/python/langgraph/graph-api#nodes) contains multiple operations with side effects (e.g., logging, file writes, or network calls), wrap each operation in a separate **task**. This ensures that when the workflow is resumed, the operations are not repeated, and their results are retrieved from the persistence layer.
* **Encapsulate Non-Deterministic Operations:** Wrap any code that might yield non-deterministic results (e.g., random number generation) inside **tasks** or **nodes**. This ensures that, upon resumption, the workflow follows the exact recorded sequence of steps with the same outcomes.
* **Use Idempotent Operations**: When possible ensure that side effects (e.g., API calls, file writes) are idempotent. This means that if an operation is retried after a failure in the workflow, it will have the same effect as the first time it was executed. This is particularly important for operations that result in data writes. In the event that a **task** starts but fails to complete successfully, the workflow's resumption will re-run the **task**, relying on recorded outcomes to maintain consistency. Use idempotency keys or verify existing results to avoid unintended duplication, ensuring a smooth and predictable workflow execution.

For some examples of pitfalls to avoid, see the [Common Pitfalls](/oss/python/langgraph/functional-api#common-pitfalls) section in the functional API, which shows
how to structure your code using **tasks** to avoid these issues. The same principles apply to the [StateGraph (Graph API)](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph).

LangGraph supports three durability modes that allow you to balance performance and data consistency based on your application's requirements. The durability modes, from least to most durable, are as follows:

* [`"exit"`](#exit)
* [`"async"`](#async)
* [`"sync"`](#sync)

A higher durability mode adds more overhead to the workflow execution.

<Tip>
  **Added in v0.6.0**
  Use the `durability` parameter instead of `checkpoint_during` (deprecated in v0.6.0) for persistence policy management:

* `durability="async"` replaces `checkpoint_during=True`
  * `durability="exit"` replaces `checkpoint_during=False`

for persistence policy management, with the following mapping:

* `checkpoint_during=True` -> `durability="async"`
  * `checkpoint_during=False` -> `durability="exit"`
</Tip>

Changes are persisted only when graph execution completes (either successfully or with an error). This provides the best performance for long-running graphs but means intermediate state is not saved, so you cannot recover from mid-execution failures or interrupt the graph execution.

Changes are persisted asynchronously while the next step executes. This provides good performance and durability, but there's a small risk that checkpoints might not be written if the process crashes during execution.

Changes are persisted synchronously before the next step starts. This ensures that every checkpoint is written before continuing execution, providing high durability at the cost of some performance overhead.

You can specify the durability mode when calling any graph execution method:

## Using tasks in nodes

If a [node](/oss/python/langgraph/graph-api#nodes) contains multiple operations, you may find it easier to convert each operation into a **task** rather than refactor the operations into individual nodes.

<Tabs>
  <Tab title="Original">
    
  </Tab>

<Tab title="With task">
    
  </Tab>
</Tabs>

## Resuming Workflows

Once you have enabled durable execution in your workflow, you can resume execution for the following scenarios:

* **Pausing and Resuming Workflows:** Use the [interrupt](https://reference.langchain.com/python/langgraph/types/#langgraph.types.interrupt) function to pause a workflow at specific points and the [`Command`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.Command) primitive to resume it with updated state. See [**Interrupts**](/oss/python/langgraph/interrupts) for more details.
* **Recovering from Failures:** Automatically resume workflows from the last successful checkpoint after an exception (e.g., LLM provider outage). This involves executing the workflow with the same thread identifier by providing it with a `None` as the input value (see this [example](/oss/python/langgraph/use-functional-api#resuming-after-an-error) with the functional API).

## Starting Points for Resuming Workflows

* If you're using a [StateGraph (Graph API)](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph), the starting point is the beginning of the [**node**](/oss/python/langgraph/graph-api#nodes) where execution stopped.
* If you're making a subgraph call inside a node, the starting point will be the **parent** node that called the subgraph that was halted.
  Inside the subgraph, the starting point will be the specific [**node**](/oss/python/langgraph/graph-api#nodes) where execution stopped.
* If you're using the Functional API, the starting point is the beginning of the [**entrypoint**](/oss/python/langgraph/functional-api#entrypoint) where execution stopped.

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/langgraph/durable-execution.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
## Using tasks in nodes

If a [node](/oss/python/langgraph/graph-api#nodes) contains multiple operations, you may find it easier to convert each operation into a **task** rather than refactor the operations into individual nodes.

<Tabs>
  <Tab title="Original">
```

Example 2 (unknown):
```unknown
</Tab>

  <Tab title="With task">
```

---

## How to set up a JavaScript application

**URL:** llms-txt#how-to-set-up-a-javascript-application

**Contents:**
- Specify dependencies
- Specify environment variables
- Define graphs
- Create the API config
- Next

Source: https://docs.langchain.com/langsmith/setup-javascript

An application must be configured with a [configuration file](/langsmith/cli#configuration-file) in order to be deployed to LangSmith (or to be self-hosted). This how-to guide discusses the basic steps to set up a JavaScript application for deployment using `package.json` to specify project dependencies.

This walkthrough is based on [this repository](https://github.com/langchain-ai/langgraphjs-studio-starter), which you can play around with to learn more about how to set up your application for deployment.

The final repository structure will look something like this:

<Tip>
  LangSmith Deployment supports deploying a [LangGraph](/oss/python/langgraph/overview) *graph*. However, the implementation of a *node* of a graph can contain arbitrary Python code. This means any framework can be implemented within a node and deployed on LangSmith Deployment. This lets you keep your core application logic outside LangGraph while still using LangSmith for [deployment](/langsmith/deployments), scaling, and [observability](/langsmith/observability).
</Tip>

After each step, an example file directory is provided to demonstrate how code can be organized.

## Specify dependencies

Dependencies can be specified in a `package.json`. If none of these files is created, then dependencies can be specified later in the [configuration file](#create-the-api-config).

Example `package.json` file:

When deploying your app, the dependencies will be installed using the package manager of your choice, provided they adhere to the compatible version ranges listed below:

Example file directory:

## Specify environment variables

Environment variables can optionally be specified in a file (e.g. `.env`). See the [Environment Variables reference](/langsmith/env-var) to configure additional variables for a deployment.

Example file directory:

Implement your graphs. Graphs can be defined in a single file or multiple files. Make note of the variable names of each compiled graph to be included in the application. The variable names will be used later when creating the [configuration file](/langsmith/cli#configuration-file).

Here is an example `agent.ts`:

Example file directory:

## Create the API config

Create a [configuration file](/langsmith/cli#configuration-file) called `langgraph.json`. See the [configuration file reference](/langsmith/cli#configuration-file) for detailed explanations of each key in the JSON object of the configuration file.

Example `langgraph.json` file:

Note that the variable name of the `CompiledGraph` appears at the end of the value of each subkey in the top-level `graphs` key (i.e. `:<variable_name>`).

<Info>
  **Configuration Location**
  The configuration file must be placed in a directory that is at the same level or higher than the TypeScript files that contain compiled graphs and associated dependencies.
</Info>

After you setup your project and place it in a GitHub repository, it's time to [deploy your app](/langsmith/deployment-quickstart).

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/setup-javascript.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
<Tip>
  LangSmith Deployment supports deploying a [LangGraph](/oss/python/langgraph/overview) *graph*. However, the implementation of a *node* of a graph can contain arbitrary Python code. This means any framework can be implemented within a node and deployed on LangSmith Deployment. This lets you keep your core application logic outside LangGraph while still using LangSmith for [deployment](/langsmith/deployments), scaling, and [observability](/langsmith/observability).
</Tip>

After each step, an example file directory is provided to demonstrate how code can be organized.

## Specify dependencies

Dependencies can be specified in a `package.json`. If none of these files is created, then dependencies can be specified later in the [configuration file](#create-the-api-config).

Example `package.json` file:
```

Example 2 (unknown):
```unknown
When deploying your app, the dependencies will be installed using the package manager of your choice, provided they adhere to the compatible version ranges listed below:
```

Example 3 (unknown):
```unknown
Example file directory:
```

Example 4 (unknown):
```unknown
## Specify environment variables

Environment variables can optionally be specified in a file (e.g. `.env`). See the [Environment Variables reference](/langsmith/env-var) to configure additional variables for a deployment.

Example `.env` file:
```

---

## Trace with LangGraph

**URL:** llms-txt#trace-with-langgraph

**Contents:**
- With LangChain
  - 1. Installation
  - 2. Configure your environment

Source: https://docs.langchain.com/langsmith/trace-with-langgraph

LangSmith smoothly integrates with LangGraph (Python and JS) to help you trace agents, whether you're using LangChain modules or other SDKs.

If you are using LangChain modules within LangGraph, you only need to set a few environment variables to enable tracing.

This guide will walk through a basic example. For more detailed information on configuration, see the [Trace With LangChain](/langsmith/trace-with-langchain) guide.

Install the LangGraph library and the OpenAI integration for Python and JS (we use the OpenAI integration for the code snippets below).

For a full list of packages available, see the [LangChain Python docs](https://python.langchain.com/docs/integrations/platforms/) and [LangChain JS docs](https://js.langchain.com/docs/integrations/platforms/).

### 2. Configure your environment

```bash wrap theme={null}
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=<your-api-key>

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown

```

Example 3 (unknown):
```unknown

```

Example 4 (unknown):
```unknown
</CodeGroup>

### 2. Configure your environment
```

---

## Define the nodes

**URL:** llms-txt#define-the-nodes

def node_a(state: State) -> Command[Literal["node_b", "node_c"]]:
    print("Called A")
    value = random.choice(["b", "c"])
    # this is a replacement for a conditional edge function
    if value == "b":
        goto = "node_b"
    else:
        goto = "node_c"

# note how Command allows you to BOTH update the graph state AND route to the next node
    return Command(
        # this is the state update
        update={"foo": value},
        # this is a replacement for an edge
        goto=goto,
    )

def node_b(state: State):
    print("Called B")
    return {"foo": state["foo"] + "b"}

def node_c(state: State):
    print("Called C")
    return {"foo": state["foo"] + "c"}
python  theme={null}
builder = StateGraph(State)
builder.add_edge(START, "node_a")
builder.add_node(node_a)
builder.add_node(node_b)
builder.add_node(node_c)

**Examples:**

Example 1 (unknown):
```unknown
We can now create the [`StateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph) with the above nodes. Notice that the graph doesn't have [conditional edges](/oss/python/langgraph/graph-api#conditional-edges) for routing! This is because control flow is defined with [`Command`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.Command) inside `node_a`.
```

---

## Graph node for executing the refund.

**URL:** llms-txt#graph-node-for-executing-the-refund.

---

## Test the graph with a valid input

**URL:** llms-txt#test-the-graph-with-a-valid-input

**Contents:**
- Add runtime configuration

graph.invoke({"a": "hello"})
python  theme={null}
try:
    graph.invoke({"a": 123})  # Should be a string
except Exception as e:
    print("An exception was raised because `a` is an integer rather than a string.")
    print(e)

An exception was raised because `a` is an integer rather than a string.
1 validation error for OverallState
a
  Input should be a valid string [type=string_type, input_value=123, input_type=int]
    For further information visit https://errors.pydantic.dev/2.9/v/string_type
python  theme={null}
  from langgraph.graph import StateGraph, START, END
  from pydantic import BaseModel

class NestedModel(BaseModel):
      value: str

class ComplexState(BaseModel):
      text: str
      count: int
      nested: NestedModel

def process_node(state: ComplexState):
      # Node receives a validated Pydantic object
      print(f"Input state type: {type(state)}")
      print(f"Nested type: {type(state.nested)}")
      # Return a dictionary update
      return {"text": state.text + " processed", "count": state.count + 1}

# Build the graph
  builder = StateGraph(ComplexState)
  builder.add_node("process", process_node)
  builder.add_edge(START, "process")
  builder.add_edge("process", END)
  graph = builder.compile()

# Create a Pydantic instance for input
  input_state = ComplexState(text="hello", count=0, nested=NestedModel(value="test"))
  print(f"Input object type: {type(input_state)}")

# Invoke graph with a Pydantic instance
  result = graph.invoke(input_state)
  print(f"Output type: {type(result)}")
  print(f"Output content: {result}")

# Convert back to Pydantic model if needed
  output_model = ComplexState(**result)
  print(f"Converted back to Pydantic: {type(output_model)}")
  python  theme={null}
  from langgraph.graph import StateGraph, START, END
  from pydantic import BaseModel

class CoercionExample(BaseModel):
      # Pydantic will coerce string numbers to integers
      number: int
      # Pydantic will parse string booleans to bool
      flag: bool

def inspect_node(state: CoercionExample):
      print(f"number: {state.number} (type: {type(state.number)})")
      print(f"flag: {state.flag} (type: {type(state.flag)})")
      return {}

builder = StateGraph(CoercionExample)
  builder.add_node("inspect", inspect_node)
  builder.add_edge(START, "inspect")
  builder.add_edge("inspect", END)
  graph = builder.compile()

# Demonstrate coercion with string inputs that will be converted
  result = graph.invoke({"number": "42", "flag": "true"})

# This would fail with a validation error
  try:
      graph.invoke({"number": "not-a-number", "flag": "true"})
  except Exception as e:
      print(f"\nExpected validation error: {e}")
  python  theme={null}
  from langgraph.graph import StateGraph, START, END
  from pydantic import BaseModel
  from langchain.messages import HumanMessage, AIMessage, AnyMessage
  from typing import List

class ChatState(BaseModel):
      messages: List[AnyMessage]
      context: str

def add_message(state: ChatState):
      return {"messages": state.messages + [AIMessage(content="Hello there!")]}

builder = StateGraph(ChatState)
  builder.add_node("add_message", add_message)
  builder.add_edge(START, "add_message")
  builder.add_edge("add_message", END)
  graph = builder.compile()

# Create input with a message
  initial_state = ChatState(
      messages=[HumanMessage(content="Hi")], context="Customer support chat"
  )

result = graph.invoke(initial_state)
  print(f"Output: {result}")

# Convert back to Pydantic model to see message types
  output_model = ChatState(**result)
  for i, msg in enumerate(output_model.messages):
      print(f"Message {i}: {type(msg).__name__} - {msg.content}")
  python  theme={null}
from langgraph.graph import END, StateGraph, START
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

**Examples:**

Example 1 (unknown):
```unknown
Invoke the graph with an **invalid** input
```

Example 2 (unknown):
```unknown

```

Example 3 (unknown):
```unknown
See below for additional features of Pydantic model state:

<Accordion title="Serialization Behavior">
  When using Pydantic models as state schemas, it's important to understand how serialization works, especially when:

  * Passing Pydantic objects as inputs
  * Receiving outputs from the graph
  * Working with nested Pydantic models

  Let's see these behaviors in action.
```

Example 4 (unknown):
```unknown
</Accordion>

<Accordion title="Runtime Type Coercion">
  Pydantic performs runtime type coercion for certain data types. This can be helpful but also lead to unexpected behavior if you're not aware of it.
```

---

## RemoteGraph

**URL:** llms-txt#remotegraph

Source: https://docs.langchain.com/langsmith/remote-graph

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/remote-graph.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## How to integrate LangGraph with AutoGen, CrewAI, and other frameworks

**URL:** llms-txt#how-to-integrate-langgraph-with-autogen,-crewai,-and-other-frameworks

**Contents:**
- Prerequisites
- Setup
- 1. Define AutoGen agent
- 2. Create the graph

Source: https://docs.langchain.com/langsmith/autogen-integration

This guide shows how to integrate AutoGen agents with LangGraph to leverage features like persistence, streaming, and memory, and then deploy the integrated solution to LangSmith for scalable production use. In this guide we show how to build a LangGraph chatbot that integrates with AutoGen, but you can follow the same approach with other frameworks.

Integrating AutoGen with LangGraph provides several benefits:

* Enhanced features: Add [persistence](/oss/python/langgraph/persistence), [streaming](/langsmith/streaming), [short and long-term memory](/oss/python/concepts/memory) and more to your AutoGen agents.
* Multi-agent systems: Build [multi-agent systems](/oss/python/langchain/multi-agent) where individual agents are built with different frameworks.
* Production deployment: Deploy your integrated solution to [LangSmith](/langsmith/home) for scalable production use.

* Python 3.9+
* Autogen: `pip install autogen`
* LangGraph: `pip install langgraph`
* OpenAI API key

Set your your environment:

## 1. Define AutoGen agent

Create an AutoGen agent that can execute code. This example is adapted from AutoGen's [official tutorials](https://github.com/microsoft/autogen/blob/0.2/notebook/agentchat_web_info.ipynb):

## 2. Create the graph

We will now create a LangGraph chatbot graph that calls AutoGen agent.

```python  theme={null}
from langchain_core.messages import convert_to_openai_messages
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import MemorySaver

def call_autogen_agent(state: MessagesState):
    # Convert LangGraph messages to OpenAI format for AutoGen
    messages = convert_to_openai_messages(state["messages"])

# Get the last user message
    last_message = messages[-1]

# Pass previous message history as context (excluding the last message)
    carryover = messages[:-1] if len(messages) > 1 else []

# Initiate chat with AutoGen
    response = user_proxy.initiate_chat(
        autogen_agent,
        message=last_message,
        carryover=carryover
    )

# Extract the final response from the agent
    final_content = response.chat_history[-1]["content"]

# Return the response in LangGraph format
    return {"messages": {"role": "assistant", "content": final_content}}

**Examples:**

Example 1 (unknown):
```unknown
## 1. Define AutoGen agent

Create an AutoGen agent that can execute code. This example is adapted from AutoGen's [official tutorials](https://github.com/microsoft/autogen/blob/0.2/notebook/agentchat_web_info.ipynb):
```

Example 2 (unknown):
```unknown
## 2. Create the graph

We will now create a LangGraph chatbot graph that calls AutoGen agent.
```

---

## Add OtelSpanProcessor to the tracer provider

**URL:** llms-txt#add-otelspanprocessor-to-the-tracer-provider

tracer_provider.add_span_processor(OtelSpanProcessor())

---

## Define the node that processes the input and generates an answer

**URL:** llms-txt#define-the-node-that-processes-the-input-and-generates-an-answer

def answer_node(state: InputState):
    # Example answer and an extra key
    return {"answer": "bye", "question": state["question"]}

---

## Subgraph

**URL:** llms-txt#subgraph

def subgraph_node_1(state: State):
    return {"foo": state["foo"] + "bar"}

subgraph_builder = StateGraph(State)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph = subgraph_builder.compile()

---

## Workflows and agents

**URL:** llms-txt#workflows-and-agents

**Contents:**
- Setup
- LLMs and augmentations

Source: https://docs.langchain.com/oss/python/langgraph/workflows-agents

This guide reviews common workflow and agent patterns.

* Workflows have predetermined code paths and are designed to operate in a certain order.
* Agents are dynamic and define their own processes and tool usage.

<img src="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/agent_workflow.png?fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=c217c9ef517ee556cae3fc928a21dc55" alt="Agent Workflow" data-og-width="4572" width="4572" data-og-height="2047" height="2047" data-path="oss/images/agent_workflow.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/agent_workflow.png?w=280&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=290e50cff2f72d524a107421ec8e3ff0 280w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/agent_workflow.png?w=560&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=a2bfc87080aee7dd4844f7f24035825e 560w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/agent_workflow.png?w=840&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=ae1fa9087b33b9ff8bc3446ccaa23e3d 840w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/agent_workflow.png?w=1100&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=06003ee1fe07d7a1ea8cf9200e7d0a10 1100w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/agent_workflow.png?w=1650&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=bc98b459a9b1fb226c2887de1696bde0 1650w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/agent_workflow.png?w=2500&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=1933bcdfd5c5b69b98ce96aafa456848 2500w" />

LangGraph offers several benefits when building agents and workflows, including [persistence](/oss/python/langgraph/persistence), [streaming](/oss/python/langgraph/streaming), and support for debugging as well as [deployment](/oss/python/langgraph/deploy).

To build a workflow or agent, you can use [any chat model](/oss/python/integrations/chat) that supports structured outputs and tool calling. The following example uses Anthropic:

1. Install dependencies:

2. Initialize the LLM:

## LLMs and augmentations

Workflows and agentic systems are based on LLMs and the various augmentations you add to them. [Tool calling](/oss/python/langchain/tools), [structured outputs](/oss/python/langchain/structured-output), and [short term memory](/oss/python/langchain/short-term-memory) are a few options for tailoring LLMs to your needs.

<img src="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=7ea9656f46649b3ebac19e8309ae9006" alt="LLM augmentations" data-og-width="1152" width="1152" data-og-height="778" height="778" data-path="oss/images/augmented_llm.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=280&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=53613048c1b8bd3241bd27900a872ead 280w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=560&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=7ba1f4427fd847bd410541ae38d66d40 560w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=840&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=503822cf29a28500deb56f463b4244e4 840w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=1100&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=279e0440278d3a26b73c72695636272e 1100w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=1650&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=d936838b98bc9dce25168e2b2cfd23d0 1650w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=2500&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=fa2115f972bc1152b5e03ae590600fa3 2500w" />

```python  theme={null}

**Examples:**

Example 1 (unknown):
```unknown
2. Initialize the LLM:
```

Example 2 (unknown):
```unknown
## LLMs and augmentations

Workflows and agentic systems are based on LLMs and the various augmentations you add to them. [Tool calling](/oss/python/langchain/tools), [structured outputs](/oss/python/langchain/structured-output), and [short term memory](/oss/python/langchain/short-term-memory) are a few options for tailoring LLMs to your needs.

<img src="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=7ea9656f46649b3ebac19e8309ae9006" alt="LLM augmentations" data-og-width="1152" width="1152" data-og-height="778" height="778" data-path="oss/images/augmented_llm.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=280&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=53613048c1b8bd3241bd27900a872ead 280w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=560&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=7ba1f4427fd847bd410541ae38d66d40 560w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=840&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=503822cf29a28500deb56f463b4244e4 840w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=1100&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=279e0440278d3a26b73c72695636272e 1100w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=1650&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=d936838b98bc9dce25168e2b2cfd23d0 1650w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/augmented_llm.png?w=2500&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=fa2115f972bc1152b5e03ae590600fa3 2500w" />
```

---

## LangGraph Python SDK

**URL:** llms-txt#langgraph-python-sdk

Source: https://docs.langchain.com/langsmith/langgraph-python-sdk

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/langgraph-python-sdk.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## my_graph.py.

**URL:** llms-txt#my_graph.py.

**Contents:**
  - Opt-out of configurable headers

@contextlib.asynccontextmanager
async def generate_agent(config):
  organization_id = config["configurable"].get("x-organization-id")
  if organization_id == "org1":
    graph = ...
    yield graph
  else:
    graph = ...
    yield graph

json  theme={null}
{
  "graphs": {"agent": "my_grph.py:generate_agent"}
}
json  theme={null}
{
  "http": {
    "configurable_headers": {
      "exclude": ["*"]
    }
  }
}
```

This will exclude all headers from being added to your run's configuration.

Note that exclusions take precedence over inclusions.

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/configurable-headers.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
### Opt-out of configurable headers

If you'd like to opt-out of configurable headers, you can simply set a wildcard pattern in the `exclude` list:
```

---

## Define the graph

**URL:** llms-txt#define-the-graph

graph = (
    StateGraph(MessagesState)
    ...
    .compile()
    .with_config({'callbacks': [tracer]})
)
```

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/langgraph/observability.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## Create a custom agent graph

**URL:** llms-txt#create-a-custom-agent-graph

custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    prompt="You are a specialized agent for data analysis..."
)

---

## LangGraph v1 migration guide

**URL:** llms-txt#langgraph-v1-migration-guide

**Contents:**
- Summary of changes
- Deprecations
- `create_react_agent` → `create_agent`
- Breaking changes
  - Dropped Python 3.9 support

Source: https://docs.langchain.com/oss/python/migrate/langgraph-v1

This guide outlines changes in LangGraph v1 and how to migrate from previous versions. For a high-level overview of changes, see the [what's new](/oss/python/releases/langgraph-v1) page.

## Summary of changes

LangGraph v1 is largely backwards compatible with previous versions. The main change is the deprecation of [`create_react_agent`](https://reference.langchain.com/python/langgraph/agents/#langgraph.prebuilt.chat_agent_executor.create_react_agent) in favor of LangChain's new [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent) function.

The following table lists all items deprecated in LangGraph v1:

| Deprecated item                            | Alternative                                                                                                                                                                                                                                             |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `create_react_agent`                       | [`langchain.agents.create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent)                                                                                                                               |
| `AgentState`                               | [`langchain.agents.AgentState`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.AgentState)                                                                                                                                   |
| `AgentStatePydantic`                       | `langchain.agents.AgentState` (no more pydantic state)                                                                                                                                                                                                  |
| `AgentStateWithStructuredResponse`         | `langchain.agents.AgentState`                                                                                                                                                                                                                           |
| `AgentStateWithStructuredResponsePydantic` | `langchain.agents.AgentState` (no more pydantic state)                                                                                                                                                                                                  |
| `HumanInterruptConfig`                     | `langchain.agents.middleware.human_in_the_loop.InterruptOnConfig`                                                                                                                                                                                       |
| `ActionRequest`                            | `langchain.agents.middleware.human_in_the_loop.InterruptOnConfig`                                                                                                                                                                                       |
| `HumanInterrupt`                           | `langchain.agents.middleware.human_in_the_loop.HITLRequest`                                                                                                                                                                                             |
| `ValidationNode`                           | Tools automatically validate input with [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent)                                                                                                        |
| `MessageGraph`                             | [`StateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph) with a `messages` key, like [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent) provides |

## `create_react_agent` → `create_agent`

LangGraph v1 deprecates the [`create_react_agent`](https://reference.langchain.com/python/langgraph/agents/#langgraph.prebuilt.chat_agent_executor.create_react_agent) prebuilt. Use LangChain's [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent), which runs on LangGraph and adds a flexible middleware system.

See the LangChain v1 docs for details:

* [Release notes](/oss/python/releases/langchain-v1#createagent)
* [Migration guide](/oss/python/migrate/langchain-v1#migrate-to-create_agent)

### Dropped Python 3.9 support

All LangChain packages now require **Python 3.10 or higher**. Python 3.9 reached [end of life](https://devguide.python.org/versions/) in October 2025.

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/python/migrate/langgraph-v1.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
</CodeGroup>

## Summary of changes

LangGraph v1 is largely backwards compatible with previous versions. The main change is the deprecation of [`create_react_agent`](https://reference.langchain.com/python/langgraph/agents/#langgraph.prebuilt.chat_agent_executor.create_react_agent) in favor of LangChain's new [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent) function.

## Deprecations

The following table lists all items deprecated in LangGraph v1:

| Deprecated item                            | Alternative                                                                                                                                                                                                                                             |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `create_react_agent`                       | [`langchain.agents.create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent)                                                                                                                               |
| `AgentState`                               | [`langchain.agents.AgentState`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.AgentState)                                                                                                                                   |
| `AgentStatePydantic`                       | `langchain.agents.AgentState` (no more pydantic state)                                                                                                                                                                                                  |
| `AgentStateWithStructuredResponse`         | `langchain.agents.AgentState`                                                                                                                                                                                                                           |
| `AgentStateWithStructuredResponsePydantic` | `langchain.agents.AgentState` (no more pydantic state)                                                                                                                                                                                                  |
| `HumanInterruptConfig`                     | `langchain.agents.middleware.human_in_the_loop.InterruptOnConfig`                                                                                                                                                                                       |
| `ActionRequest`                            | `langchain.agents.middleware.human_in_the_loop.InterruptOnConfig`                                                                                                                                                                                       |
| `HumanInterrupt`                           | `langchain.agents.middleware.human_in_the_loop.HITLRequest`                                                                                                                                                                                             |
| `ValidationNode`                           | Tools automatically validate input with [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent)                                                                                                        |
| `MessageGraph`                             | [`StateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph) with a `messages` key, like [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent) provides |

## `create_react_agent` → `create_agent`

LangGraph v1 deprecates the [`create_react_agent`](https://reference.langchain.com/python/langgraph/agents/#langgraph.prebuilt.chat_agent_executor.create_react_agent) prebuilt. Use LangChain's [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent), which runs on LangGraph and adds a flexible middleware system.

See the LangChain v1 docs for details:

* [Release notes](/oss/python/releases/langchain-v1#createagent)
* [Migration guide](/oss/python/migrate/langchain-v1#migrate-to-create_agent)

<CodeGroup>
```

Example 3 (unknown):
```unknown

```

---

## Run the agent - all steps will be traced automatically

**URL:** llms-txt#run-the-agent---all-steps-will-be-traced-automatically

**Contents:**
- Trace selectively

response = agent.invoke({
    "messages": [{"role": "user", "content": "Search for the latest AI news and email a summary to john@example.com"}]
})
python  theme={null}
import langsmith as ls

**Examples:**

Example 1 (unknown):
```unknown
By default, the trace will be logged to the project with the name `default`. To configure a custom project name, see [Log to a project](#log-to-a-project).

## Trace selectively

You may opt to trace specific invocations or parts of your application using LangSmith's `tracing_context` context manager:
```

---

## Create the graph with memory for persistence

**URL:** llms-txt#create-the-graph-with-memory-for-persistence

checkpointer = MemorySaver()

---

## Add nodes

**URL:** llms-txt#add-nodes

workflow.add_node("generate_topic", generate_topic)
workflow.add_node("write_joke", write_joke)

---

## Build the graph

**URL:** llms-txt#build-the-graph

builder = StateGraph(MessagesState)
builder.add_node("autogen", call_autogen_agent)
builder.add_edge(START, "autogen")

---

## LangGraph overview

**URL:** llms-txt#langgraph-overview

**Contents:**
- <Icon icon="download" size={20} /> Install
- Core benefits
- LangGraph ecosystem
- Acknowledgements

Source: https://docs.langchain.com/oss/python/langgraph/overview

<Callout icon="bullhorn" color="#DFC5FE" iconType="regular">
  **LangGraph v1.0 is now available!**

For a complete list of changes and instructions on how to upgrade your code, see the [release notes](/oss/python/releases/langgraph-v1) and [migration guide](/oss/python/migrate/langgraph-v1).

If you encounter any issues or have feedback, please [open an issue](https://github.com/langchain-ai/docs/issues/new?template=02-langgraph.yml\&labels=langgraph,python) so we can improve. To view v0.x documentation, [go to the archived content](https://github.com/langchain-ai/langgraph/tree/main/docs/docs).
</Callout>

Trusted by companies shaping the future of agents-- including Klarna, Replit, Elastic, and more-- LangGraph is a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents.

LangGraph is very low-level, and focused entirely on agent **orchestration**. Before using LangGraph, we recommend you familiarize yourself with some of the components used to build agents, starting with [models](/oss/python/langchain/models) and [tools](/oss/python/langchain/tools).

We will commonly use [LangChain](/oss/python/langchain/overview) components throughout the documentation to integrate models and tools, but you don't need to use LangChain to use LangGraph. If you are just getting started with agents or want a higher-level abstraction, we recommend you use LangChain's [agents](/oss/python/langchain/agents) that provide pre-built architectures for common LLM and tool-calling loops.

LangGraph is focused on the underlying capabilities important for agent orchestration: durable execution, streaming, human-in-the-loop, and more.

## <Icon icon="download" size={20} /> Install

Then, create a simple hello world example:

LangGraph provides low-level supporting infrastructure for *any* long-running, stateful workflow or agent. LangGraph does not abstract prompts or architecture, and provides the following central benefits:

* [Durable execution](/oss/python/langgraph/durable-execution): Build agents that persist through failures and can run for extended periods, resuming from where they left off.
* [Human-in-the-loop](/oss/python/langgraph/interrupts): Incorporate human oversight by inspecting and modifying agent state at any point.
* [Comprehensive memory](/oss/python/concepts/memory): Create stateful agents with both short-term working memory for ongoing reasoning and long-term memory across sessions.
* [Debugging with LangSmith](/langsmith/home): Gain deep visibility into complex agent behavior with visualization tools that trace execution paths, capture state transitions, and provide detailed runtime metrics.
* [Production-ready deployment](/langsmith/deployments): Deploy sophisticated agent systems confidently with scalable infrastructure designed to handle the unique challenges of stateful, long-running workflows.

## LangGraph ecosystem

While LangGraph can be used standalone, it also integrates seamlessly with any LangChain product, giving developers a full suite of tools for building agents. To improve your LLM application development, pair LangGraph with:

* [LangSmith](http://www.langchain.com/langsmith) — Helpful for agent evals and observability. Debug poor-performing LLM app runs, evaluate agent trajectories, gain visibility in production, and improve performance over time.
* [LangSmith](/langsmith/home) — Deploy and scale agents effortlessly with a purpose-built deployment platform for long running, stateful workflows. Discover, reuse, configure, and share agents across teams — and iterate quickly with visual prototyping in [Studio](/langsmith/studio).
* [LangChain](/oss/python/langchain/overview) - Provides integrations and composable components to streamline LLM application development. Contains agent abstractions built on top of LangGraph.

LangGraph is inspired by [Pregel](https://research.google/pubs/pub37252/) and [Apache Beam](https://beam.apache.org/). The public interface draws inspiration from [NetworkX](https://networkx.org/documentation/latest/). LangGraph is built by LangChain Inc, the creators of LangChain, but can be used without LangChain.

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/langgraph/overview.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
</CodeGroup>

Then, create a simple hello world example:
```

---

## Observability concepts

**URL:** llms-txt#observability-concepts

**Contents:**
- Runs
- Traces
- Threads
- Projects
- Feedback
- Tags
- Metadata
- Data storage and retention
- Deleting traces from LangSmith

Source: https://docs.langchain.com/langsmith/observability-concepts

This page covers key concepts that are important to understand when logging traces to LangSmith.

A [*trace*](#traces) records the sequence of steps your application takes—from receiving an input, through intermediate processing, to producing a final output. Each step within a trace is represented by a [*run*](#runs). Multiple traces are grouped together within a [*project*](#projects), and traces from multi-turn conversations can be linked together as a [*thread*](#threads).

The following diagram displays these concepts in the context of a simple RAG app, which retrieves documents from an index and generates an answer.

<div style={{ textAlign: 'center' }}>
  <img className="block dark:hidden" src="https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives.png?fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=50c5f4d966f8fe4f8ae0be0beaf11bc4" alt="Primitives of LangSmith Project, Trace, Run in the context of a question and answer RAG app." data-og-width="2701" width="2701" data-og-height="1739" height="1739" data-path="langsmith/images/primitives.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives.png?w=280&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=e0b6083af11ec78c1650c907a6b8649a 280w, https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives.png?w=560&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=9054d8620c453c520e161c1ba8fb1fdc 560w, https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives.png?w=840&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=8ece2e0b84019b722446e9bfdbf067f9 840w, https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives.png?w=1100&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=c4e3700fe862b539954b8c6c0124bfac 1100w, https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives.png?w=1650&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=f9dfe46dbb576c1faeb1f4ad52324527 1650w, https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives.png?w=2500&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=9137d815270a89f9d4df799381a88aac 2500w" />

<img className="hidden dark:block" src="https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives-dark.png?fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=3ca35a8a6cec65b9a5139e7ac8cac470" alt="Primitives of LangSmith Project, Trace, Run in the context of a question and answer RAG app." data-og-width="2919" width="2919" data-og-height="1752" height="1752" data-path="langsmith/images/primitives-dark.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives-dark.png?w=280&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=41bff3be3eabb386bd11347b77908625 280w, https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives-dark.png?w=560&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=1e7d10f532b2a099ca74cd80f1f0f90d 560w, https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives-dark.png?w=840&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=10e2a103221b086ed8985a8478c9992c 840w, https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives-dark.png?w=1100&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=a82db1fc02ffd0db0222ed0a14e48a86 1100w, https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives-dark.png?w=1650&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=70a1cd6dd3f30b5863bba85e92a30733 1650w, https://mintcdn.com/langchain-5e9cc07a/Tf5b6pnNY9Uj6Vtl/langsmith/images/primitives-dark.png?w=2500&fit=max&auto=format&n=Tf5b6pnNY9Uj6Vtl&q=85&s=33a6bfeb3258ced236732b0be95b6ab3 2500w" />
</div>

A *run* is a span representing a single unit of work or operation within your LLM application. This could be anything from a single call to an LLM or chain, to a prompt formatting call, to a runnable lambda invocation. If you are familiar with [OpenTelemetry](https://opentelemetry.io/), you can think of a run as a span.

<img src="https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/run.png?fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=a692d614eb441aef6e3a1f02f4a37e8a" alt="Run" data-og-width="1830" width="1830" data-og-height="1527" height="1527" data-path="langsmith/images/run.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/run.png?w=280&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=911a09dc4da0d94015cc2a22f95efce6 280w, https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/run.png?w=560&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=6ae06bcbba3e3b240cfa41950f4e451d 560w, https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/run.png?w=840&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=2e886c505427057c726f30b495fc7c4c 840w, https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/run.png?w=1100&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=48dfe76850483f46da1bbe4bcccb5f8b 1100w, https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/run.png?w=1650&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=eff65c5910eaa68456e26712dfa64d1d 1650w, https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/run.png?w=2500&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=d99e6ba31cd3f4039ad86b0ade0b78b4 2500w" />

A *trace* is a collection of runs for a single operation. For example, if you have a user request that triggers a chain, and that chain makes a call to an LLM, then to an output parser, and so on, all of these runs would be part of the same trace. If you are familiar with [OpenTelemetry](https://opentelemetry.io/), you can think of a LangSmith trace as a collection of spans. Runs are bound to a trace by a unique trace ID.

<img src="https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/trace.png?fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=dd692f6433fbcf0413a4516c170062f2" alt="Trace" data-og-width="1830" width="1830" data-og-height="1527" height="1527" data-path="langsmith/images/trace.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/trace.png?w=280&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=fea7f898d3f25c76bed212af157b1a1d 280w, https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/trace.png?w=560&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=5a75129cb5ab5fab0a6618d0c3160ec2 560w, https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/trace.png?w=840&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=3102493a51a280b38004ff8628231ad6 840w, https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/trace.png?w=1100&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=f0e4d194f6a6b18b4505a2b4a4f40fc3 1100w, https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/trace.png?w=1650&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=d1f0bb5ae6e5dec024c5e3726b848394 1650w, https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/trace.png?w=2500&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=f5d14619201af89c134fd1fb99b7cdf0 2500w" />

A *thread* is a sequence of traces representing a single conversation. Many LLM applications have a chatbot-like interface in which the user and the LLM application engage in a multi-turn conversation. Each turn in the conversation is represented as its own trace, but these traces are linked together by being part of the same thread. The most recent trace in a thread is the latest message exchange.

To group traces into threads, you pass a special metadata key (`session_id`, `thread_id`, or `conversation_id`) with a unique identifier value that links the traces together.

[Learn how to configure threads](/langsmith/threads).

<img className="block dark:hidden" src="https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-light.png?fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=f7af4c3904073d5f58f28c656603ca19" alt="Thread representing a sequence of traces in a multi-turn conversation." data-og-width="1273" width="1273" data-og-height="757" height="757" data-path="langsmith/images/thread-overview-light.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-light.png?w=280&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=cd769088ab3ab2dae09982915f23772d 280w, https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-light.png?w=560&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=70ae6b5a6b8edb83ba3604d4c6e0262e 560w, https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-light.png?w=840&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=61d89d8077072221373490edac65363c 840w, https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-light.png?w=1100&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=ad8159fe12f056dbc561c612e3797b97 1100w, https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-light.png?w=1650&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=3611f7bcc95c45bcb91c093ca36ef348 1650w, https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-light.png?w=2500&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=1c0426d7e83562e1d76e079959bda186 2500w" />

<img className="hidden dark:block" src="https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-dark.png?fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=f738de4cac932ed2b8657e8f3b706b77" alt="Thread representing a sequence of traces in a multi-turn conversation." data-og-width="1273" width="1273" data-og-height="753" height="753" data-path="langsmith/images/thread-overview-dark.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-dark.png?w=280&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=9bc9dd49c63661dceb981899c5f0332b 280w, https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-dark.png?w=560&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=01713d47cf762f99be1a1143b01582e8 560w, https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-dark.png?w=840&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=cfc77e449d0ce27cdfa51b2f7c6ed655 840w, https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-dark.png?w=1100&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=d84f671a8f2c1207dbb98c72a37d1832 1100w, https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-dark.png?w=1650&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=d592bd4c8671b3d7f19a49471888a901 1650w, https://mintcdn.com/langchain-5e9cc07a/zLS2qlRr5r04zU3G/langsmith/images/thread-overview-dark.png?w=2500&fit=max&auto=format&n=zLS2qlRr5r04zU3G&q=85&s=2405eaef2af227dd5e5efac85fc9e623 2500w" />

A *project* is a collection of traces. You can think of a project as a container for all the traces that are related to a single application or service. You can have multiple projects, and each project can have multiple traces.

<img src="https://mintcdn.com/langchain-5e9cc07a/H9jA2WRyA-MV4-H0/langsmith/images/project.png?fit=max&auto=format&n=H9jA2WRyA-MV4-H0&q=85&s=2426200ab2e619674636e41f11246c0d" alt="Project" data-og-width="1830" width="1830" data-og-height="1527" height="1527" data-path="langsmith/images/project.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/H9jA2WRyA-MV4-H0/langsmith/images/project.png?w=280&fit=max&auto=format&n=H9jA2WRyA-MV4-H0&q=85&s=97510cd2501c9d2dc529680172664219 280w, https://mintcdn.com/langchain-5e9cc07a/H9jA2WRyA-MV4-H0/langsmith/images/project.png?w=560&fit=max&auto=format&n=H9jA2WRyA-MV4-H0&q=85&s=8624fbec9c58a1999d702aed79a606f6 560w, https://mintcdn.com/langchain-5e9cc07a/H9jA2WRyA-MV4-H0/langsmith/images/project.png?w=840&fit=max&auto=format&n=H9jA2WRyA-MV4-H0&q=85&s=5d918966500e84ce29550591755d98f6 840w, https://mintcdn.com/langchain-5e9cc07a/H9jA2WRyA-MV4-H0/langsmith/images/project.png?w=1100&fit=max&auto=format&n=H9jA2WRyA-MV4-H0&q=85&s=d9a6a4b2365de4e4cf80506d3fc0a467 1100w, https://mintcdn.com/langchain-5e9cc07a/H9jA2WRyA-MV4-H0/langsmith/images/project.png?w=1650&fit=max&auto=format&n=H9jA2WRyA-MV4-H0&q=85&s=11761179be51c8cfc58193d6d0215269 1650w, https://mintcdn.com/langchain-5e9cc07a/H9jA2WRyA-MV4-H0/langsmith/images/project.png?w=2500&fit=max&auto=format&n=H9jA2WRyA-MV4-H0&q=85&s=779669a7f2f2106946d1f7eb3f427ed5 2500w" />

*Feedback* allows you to score an individual run based on certain criteria. Each feedback entry consists of a feedback tag and feedback score, and is bound to a run by a unique run ID. Feedback can be continuous or discrete (categorical), and you can reuse feedback tags across different runs within an organization.

You can collect feedback on runs in a number of ways:

1. [Sent up along with a trace](/langsmith/attach-user-feedback) from the LLM application.
2. Generated by a user in the app [inline](/langsmith/annotate-traces-inline) or in an [annotation queue](/langsmith/annotation-queues).
3. Generated by an automatic evaluator during [offline evaluation](/langsmith/evaluate-llm-application).
4. Generated by an [online evaluator](/langsmith/online-evaluations).

To learn more about how feedback is stored in the application, refer to the [Feedback data format guide](/langsmith/feedback-data-format).

<img src="https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/feedback.png?fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=13fa69590caa5ba050e3cda9dbb6a336" alt="Feedback" data-og-width="1830" width="1830" data-og-height="1527" height="1527" data-path="langsmith/images/feedback.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/feedback.png?w=280&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=ef7168bb4e77c0b70f5cc6b7062be002 280w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/feedback.png?w=560&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=75059818a510d95abea177fb5e3a1b4e 560w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/feedback.png?w=840&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=a29438f9e3126eb0aa01023e02c0b621 840w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/feedback.png?w=1100&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=904b4e5e7aa4dcfd49121b82fb269c5f 1100w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/feedback.png?w=1650&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=f5d68cfe719b0cc0a9d5e2b0fefb12ae 1650w, https://mintcdn.com/langchain-5e9cc07a/0B2PFrFBMRWNccee/langsmith/images/feedback.png?w=2500&fit=max&auto=format&n=0B2PFrFBMRWNccee&q=85&s=3be4d77ff49c91b49effcceeb96b38d3 2500w" />

*Tags* are collections of strings that can be attached to runs. You can use tags to do the following in the LangSmith UI:

* Categorize runs for easier search.
* Filter runs.
* Group runs together for analysis.

[Learn how to attach tags to your traces](/langsmith/add-metadata-tags).

<img src="https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/tags.png?fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=44e6b6242fd76e811dcc28d88c5c6db5" alt="Tags" data-og-width="1830" width="1830" data-og-height="1527" height="1527" data-path="langsmith/images/tags.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/tags.png?w=280&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=35d294b4a295130dfb7f23a8237fe53d 280w, https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/tags.png?w=560&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=ab7e4b06eced56da2b51eb9f88738e6f 560w, https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/tags.png?w=840&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=ecd67b36985d21a275b3b6aa34922a84 840w, https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/tags.png?w=1100&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=dfc774fcd984d08202f178eb75cc14e6 1100w, https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/tags.png?w=1650&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=9e5c4c571cbaf45fdab26f21e854bc29 1650w, https://mintcdn.com/langchain-5e9cc07a/ImHGLQW1HnQYwnJV/langsmith/images/tags.png?w=2500&fit=max&auto=format&n=ImHGLQW1HnQYwnJV&q=85&s=b792075475d671a84e3efb1ca47d527b 2500w" />

*Metadata* is a collection of key-value pairs that you can attach to runs. You can use metadata to store additional information about a run, such as the version of the application that generated the run, the environment in which the run was generated, or any other information that you want to associate with a run. Similarly to tags, you can use metadata to filter runs in the LangSmith UI or group runs together for analysis.

[Learn how to add metadata to your traces](/langsmith/add-metadata-tags).

<img src="https://mintcdn.com/langchain-5e9cc07a/4kN8yiLrZX_amfFn/langsmith/images/metadata.png?fit=max&auto=format&n=4kN8yiLrZX_amfFn&q=85&s=e48730c02b7974035bbb312734e86a92" alt="Metadata" data-og-width="1830" width="1830" data-og-height="1527" height="1527" data-path="langsmith/images/metadata.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/4kN8yiLrZX_amfFn/langsmith/images/metadata.png?w=280&fit=max&auto=format&n=4kN8yiLrZX_amfFn&q=85&s=6fbe88a76fd74d9fb36e89465ef068cc 280w, https://mintcdn.com/langchain-5e9cc07a/4kN8yiLrZX_amfFn/langsmith/images/metadata.png?w=560&fit=max&auto=format&n=4kN8yiLrZX_amfFn&q=85&s=7e3c71b02884707ca26863a88e4d04f6 560w, https://mintcdn.com/langchain-5e9cc07a/4kN8yiLrZX_amfFn/langsmith/images/metadata.png?w=840&fit=max&auto=format&n=4kN8yiLrZX_amfFn&q=85&s=8799298d81f72725c01a937c549fdb81 840w, https://mintcdn.com/langchain-5e9cc07a/4kN8yiLrZX_amfFn/langsmith/images/metadata.png?w=1100&fit=max&auto=format&n=4kN8yiLrZX_amfFn&q=85&s=6dbb9c568c187cbd8bd14a471f6977b3 1100w, https://mintcdn.com/langchain-5e9cc07a/4kN8yiLrZX_amfFn/langsmith/images/metadata.png?w=1650&fit=max&auto=format&n=4kN8yiLrZX_amfFn&q=85&s=be48eaaa028a65c6ca6698c27cf9da6b 1650w, https://mintcdn.com/langchain-5e9cc07a/4kN8yiLrZX_amfFn/langsmith/images/metadata.png?w=2500&fit=max&auto=format&n=4kN8yiLrZX_amfFn&q=85&s=810f9462214e87aba38b724a9b5083af 2500w" />

## Data storage and retention

For traces ingested on or after Wednesday, May 22, 2024, LangSmith (SaaS) retains trace data for a maximum of 400 days past the date and time the trace was inserted into the LangSmith trace database.

After 400 days, the traces are permanently deleted from LangSmith, with a limited amount of metadata retained for the purpose of showing accurate statistics, such as historic usage and cost.

<Note>
  If you wish to keep tracing data longer than the data retention period, you can add it to a dataset. A [dataset](/langsmith/manage-datasets) allows you to store the trace inputs and outputs (e.g., as a key-value dataset), and will persist indefinitely, even after the trace gets deleted.
</Note>

## Deleting traces from LangSmith

If you need to remove a trace from LangSmith before its expiration date, you can do so by deleting the project that contains it.

You can delete a project with one of the following ways:

* In the [LangSmith UI](https://smith.langchain.com), select the **Delete** option on the project's overflow menu.
* With the [`delete_tracer_sessions`](https://api.smith.langchain.com/redoc#tag/tracer-sessions/operation/delete_tracer_session_api_v1_sessions__session_id__delete) API endpoint
* With the `delete_project()` ([Python](https://reference.langchain.com/python/langsmith/observability/sdk/)) or `deleteProject()` ([JS/TS](https://reference.langchain.com/javascript/modules/langsmith.html)) in the LangSmith SDK.

LangSmith does not support self-service deletion of individual traces.

If you have a need to delete a single trace (or set of traces) from LangSmith project before its expiration date, the account owner should reach out to [LangSmith Support](mailto:support@langchain.dev) with the organization ID and trace IDs.

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/observability-concepts.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## Run the graph until the interrupt is hit.

**URL:** llms-txt#run-the-graph-until-the-interrupt-is-hit.

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Delete old records from the database",
            }
        ]
    },
    config=config # [!code highlight]
)

---

## Define the two nodes we will cycle between

**URL:** llms-txt#define-the-two-nodes-we-will-cycle-between

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

---

## Show the workflow

**URL:** llms-txt#show-the-workflow

display(Image(orchestrator_worker.get_graph().draw_mermaid_png()))

---

## Add the nodes

**URL:** llms-txt#add-the-nodes

orchestrator_worker_builder.add_node("orchestrator", orchestrator)
orchestrator_worker_builder.add_node("llm_call", llm_call)
orchestrator_worker_builder.add_node("synthesizer", synthesizer)

---

## Remember that langgraph graphs are also langchain runnables.

**URL:** llms-txt#remember-that-langgraph-graphs-are-also-langchain-runnables.

**Contents:**
- Evaluating intermediate steps
- Running and evaluating individual nodes
- Related
- Reference code

target = example_to_state | app

experiment_results = await aevaluate(
    target,
    data="weather agent",
    evaluators=[correct],
    max_concurrency=4,  # optional
    experiment_prefix="claude-3.5-baseline",  # optional
)
python  theme={null}
def right_tool(outputs: dict) -> bool:
    tool_calls = outputs["messages"][1].tool_calls
    return bool(tool_calls and tool_calls[0]["name"] == "search")

experiment_results = await aevaluate(
    target,
    data="weather agent",
    evaluators=[correct, right_tool],
    max_concurrency=4,  # optional
    experiment_prefix="claude-3.5-baseline",  # optional
)
python  theme={null}
from langsmith.schemas import Run, Example

def right_tool_from_run(run: Run, example: Example) -> dict:
    # Get documents and answer
    first_model_run = next(run for run in root_run.child_runs if run.name == "agent")
    tool_calls = first_model_run.outputs["messages"][-1].tool_calls
    right_tool = bool(tool_calls and tool_calls[0]["name"] == "search")
    return {"key": "right_tool", "value": right_tool}

experiment_results = await aevaluate(
    target,
    data="weather agent",
    evaluators=[correct, right_tool_from_run],
    max_concurrency=4,  # optional
    experiment_prefix="claude-3.5-baseline",  # optional
)
python  theme={null}
node_target = example_to_state | app.nodes["agent"]

node_experiment_results = await aevaluate(
    node_target,
    data="weather agent",
    evaluators=[right_tool_from_run],
    max_concurrency=4,  # optional
    experiment_prefix="claude-3.5-model-node",  # optional
)
python  theme={null}
  from typing import Annotated, Literal, TypedDict
  from langchain.chat_models import init_chat_model
  from langchain.tools import tool
  from langgraph.prebuilt import ToolNode
  from langgraph.graph import END, START, StateGraph
  from langgraph.graph.message import add_messages
  from langsmith import Client, aevaluate

# Define a graph
  class State(TypedDict):
      # Messages have the type "list". The 'add_messages' function
      # in the annotation defines how this state key should be updated
      # (in this case, it appends messages to the list, rather than overwriting them)
      messages: Annotated[list, add_messages]

# Define the tools for the agent to use
  @tool
  def search(query: str) -> str:
      """Call to surf the web."""
      # This is a placeholder, but don't tell the LLM that...
      if "sf" in query.lower() or "san francisco" in query.lower():
          return "It's 60 degrees and foggy."
      return "It's 90 degrees and sunny."

tools = [search]
  tool_node = ToolNode(tools)
  model = init_chat_model("claude-sonnet-4-5-20250929").bind_tools(tools)

# Define the function that determines whether to continue or not
  def should_continue(state: State) -> Literal["tools", END]:
      messages = state['messages']
      last_message = messages[-1]

# If the LLM makes a tool call, then we route to the "tools" node
      if last_message.tool_calls:
          return "tools"

# Otherwise, we stop (reply to the user)
      return END

# Define the function that calls the model
  def call_model(state: State):
      messages = state['messages']
      response = model.invoke(messages)
      # We return a list, because this will get added to the existing list
      return {"messages": [response]}

# Define a new graph
  workflow = StateGraph(State)

# Define the two nodes we will cycle between
  workflow.add_node("agent", call_model)
  workflow.add_node("tools", tool_node)

# Set the entrypoint as 'agent'
  # This means that this node is the first one called
  workflow.add_edge(START, "agent")

# We now add a conditional edge
  workflow.add_conditional_edges(
      # First, we define the start node. We use 'agent'.
      # This means these are the edges taken after the 'agent' node is called.
      "agent",
      # Next, we pass in the function that will determine which node is called next.
      should_continue,
  )

# We now add a normal edge from 'tools' to 'agent'.
  # This means that after 'tools' is called, 'agent' node is called next.
  workflow.add_edge("tools", 'agent')

# Finally, we compile it!
  # This compiles it into a LangChain Runnable,
  # meaning you can use it as you would any other runnable.
  # Note that we're (optionally) passing the memory when compiling the graph
  app = workflow.compile()

questions = [
      "what's the weather in sf",
      "whats the weather in san fran",
      "whats the weather in tangier"
  ]

answers = [
      "It's 60 degrees and foggy.",
      "It's 60 degrees and foggy.",
      "It's 90 degrees and sunny.",
  ]

# Create a dataset
  ls_client = Client()
  dataset = ls_client.create_dataset(
      "weather agent",
      inputs=[{"question": q} for q in questions],
      outputs=[{"answers": a} for a in answers],
  )

# Define evaluators
  async def correct(outputs: dict, reference_outputs: dict) -> bool:
      instructions = (
          "Given an actual answer and an expected answer, determine whether"
          " the actual answer contains all of the information in the"
          " expected answer. Respond with 'CORRECT' if the actual answer"
          " does contain all of the expected information and 'INCORRECT'"
          " otherwise. Do not include anything else in your response."
      )
      # Our graph outputs a State dictionary, which in this case means
      # we'll have a 'messages' key and the final message should
      # be our actual answer.
      actual_answer = outputs["messages"][-1].content
      expected_answer = reference_outputs["answer"]
      user_msg = (
          f"ACTUAL ANSWER: {actual_answer}"
          f"\n\nEXPECTED ANSWER: {expected_answer}"
      )
      response = await judge_llm.ainvoke(
          [
              {"role": "system", "content": instructions},
              {"role": "user", "content": user_msg}
          ]
      )
      return response.content.upper() == "CORRECT"

def right_tool(outputs: dict) -> bool:
      tool_calls = outputs["messages"][1].tool_calls
      return bool(tool_calls and tool_calls[0]["name"] == "search")

# Run evaluation
  experiment_results = await aevaluate(
      target,
      data="weather agent",
      evaluators=[correct, right_tool],
      max_concurrency=4,  # optional
      experiment_prefix="claude-3.5-baseline",  # optional
  )
  ```
</Accordion>

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/evaluate-graph.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
## Evaluating intermediate steps

Often it is valuable to evaluate not only the final output of an agent but also the intermediate steps it has taken. What's nice about `langgraph` is that the output of a graph is a state object that often already carries information about the intermediate steps taken. Usually we can evaluate whatever we're interested in just by looking at the messages in our state. For example, we can look at the messages to assert that the model invoked the 'search' tool upon as a first step.

Requires `langsmith>=0.2.0`
```

Example 2 (unknown):
```unknown
If we need access to information about intermediate steps that isn't in state, we can look at the Run object. This contains the full traces for all node inputs and outputs:

<Check>
  See more about what arguments you can pass to custom evaluators in this [how-to guide](/langsmith/code-evaluator).
</Check>
```

Example 3 (unknown):
```unknown
## Running and evaluating individual nodes

Sometimes you want to evaluate a single node directly to save time and costs. `langgraph` makes it easy to do this. In this case we can even continue using the evaluators we've been using.
```

Example 4 (unknown):
```unknown
## Related

* [`langgraph` evaluation docs](https://langchain-ai.github.io/langgraph/tutorials/#evaluation)

## Reference code

<Accordion title="Click to see a consolidated code snippet">
```

---

## Process final result

**URL:** llms-txt#process-final-result

**Contents:**
- Multiple tool calls
- Edit tool arguments
- Subagent interrupts
- Best practices
  - Always use a checkpointer
  - Use the same thread ID

print(result["messages"][-1]["content"])
python  theme={null}
config = {"configurable": {"thread_id": str(uuid.uuid4())}}

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Delete temp.txt and send an email to admin@example.com"
    }]
}, config=config)

if result.get("__interrupt__"):
    interrupts = result["__interrupt__"][0].value
    action_requests = interrupts["action_requests"]

# Two tools need approval
    assert len(action_requests) == 2

# Provide decisions in the same order as action_requests
    decisions = [
        {"type": "approve"},  # First tool: delete_file
        {"type": "reject"}    # Second tool: send_email
    ]

result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config
    )
python  theme={null}
if result.get("__interrupt__"):
    interrupts = result["__interrupt__"][0].value
    action_request = interrupts["action_requests"][0]

# Original args from the agent
    print(action_request["args"])  # {"to": "everyone@company.com", ...}

# User decides to edit the recipient
    decisions = [{
        "type": "edit",
        "edited_action": {
            "name": action_request["name"],  # Must include the tool name
            "args": {"to": "team@company.com", "subject": "...", "body": "..."}
        }
    }]

result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config
    )
python  theme={null}
agent = create_deep_agent(
    tools=[delete_file, read_file],
    interrupt_on={
        "delete_file": True,
        "read_file": False,
    },
    subagents=[{
        "name": "file-manager",
        "description": "Manages file operations",
        "system_prompt": "You are a file management assistant.",
        "tools": [delete_file, read_file],
        "interrupt_on": {
            # Override: require approval for reads in this subagent
            "delete_file": True,
            "read_file": True,  # Different from main agent!
        }
    }],
    checkpointer=checkpointer
)
python  theme={null}
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
agent = create_deep_agent(
    tools=[...],
    interrupt_on={...},
    checkpointer=checkpointer  # Required for HITL
)
python  theme={null}

**Examples:**

Example 1 (unknown):
```unknown
## Multiple tool calls

When the agent calls multiple tools that require approval, all interrupts are batched together in a single interrupt. You must provide decisions for each one in order.
```

Example 2 (unknown):
```unknown
## Edit tool arguments

When `"edit"` is in the allowed decisions, you can modify the tool arguments before execution:
```

Example 3 (unknown):
```unknown
## Subagent interrupts

Each subagent can have its own `interrupt_on` configuration that overrides the main agent's settings:
```

Example 4 (unknown):
```unknown
When a subagent triggers an interrupt, the handling is the same – check for `__interrupt__` and resume with `Command`.

## Best practices

### Always use a checkpointer

Human-in-the-loop requires a checkpointer to persist agent state between the interrupt and resume:
```

---

## Build graph

**URL:** llms-txt#build-graph

graph = StateGraph(dict)
graph.add_node("reasoning", reasoning_node)
graph.add_node("fallback", fallback_node)
graph.add_conditional_edges("reasoning", route_based_on_state)
graph.add_edge("fallback", END)
graph.set_entry_point("reasoning")

app = graph.compile()
python  theme={null}
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.errors import GraphRecursionError

**Examples:**

Example 1 (unknown):
```unknown
#### Proactive vs reactive approaches

There are two main approaches to handling recursion limits: proactive (monitoring within the graph) and reactive (catching errors externally).
```

---

## Proactive Approach (recommended)

**URL:** llms-txt#proactive-approach-(recommended)

def agent_with_monitoring(state: dict, config: RunnableConfig) -> dict:
    """Proactively monitor and handle recursion within the graph"""
    current_step = config["metadata"]["langgraph_step"]
    recursion_limit = config["recursion_limit"]

# Early detection - route to internal handling
    if current_step >= recursion_limit - 2:  # 2 steps before limit
        return {
            **state,
            "status": "recursion_limit_approaching",
            "final_answer": "Reached iteration limit, returning partial result"
        }

# Normal processing
    return {"messages": state["messages"] + [f"Step {current_step}"]}

---

## Nodes

**URL:** llms-txt#nodes

def orchestrator(state: State):
    """Orchestrator that generates a plan for the report"""

# Generate queries
    report_sections = planner.invoke(
        [
            SystemMessage(content="Generate a plan for the report."),
            HumanMessage(content=f"Here is the report topic: {state['topic']}"),
        ]
    )

return {"sections": report_sections.sections}

def llm_call(state: WorkerState):
    """Worker writes a section of the report"""

# Generate section
    section = llm.invoke(
        [
            SystemMessage(
                content="Write a report section following the provided name and description. Include no preamble for each section. Use markdown formatting."
            ),
            HumanMessage(
                content=f"Here is the section name: {state['section'].name} and description: {state['section'].description}"
            ),
        ]
    )

# Write the updated section to completed sections
    return {"completed_sections": [section.content]}

def synthesizer(state: State):
    """Synthesize full report from sections"""

# List of completed sections
    completed_sections = state["completed_sections"]

# Format completed section to str to use as context for final sections
    completed_report_sections = "\n\n---\n\n".join(completed_sections)

return {"final_report": completed_report_sections}

---

## Define edges

**URL:** llms-txt#define-edges

**Contents:**
  - Impose a recursion limit
- Async
- Combine control flow and state updates with `Command`

def route(state: State) -> Literal["b", END]:
    if len(state["aggregate"]) < 7:
        return "b"
    else:
        return END

builder.add_edge(START, "a")
builder.add_conditional_edges("a", route)
builder.add_edge("b", "a")
graph = builder.compile()
python  theme={null}
from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))
python  theme={null}
graph.invoke({"aggregate": []})

Node A sees []
Node B sees ['A']
Node A sees ['A', 'B']
Node B sees ['A', 'B', 'A']
Node A sees ['A', 'B', 'A', 'B']
Node B sees ['A', 'B', 'A', 'B', 'A']
Node A sees ['A', 'B', 'A', 'B', 'A', 'B']
python  theme={null}
from langgraph.errors import GraphRecursionError

try:
    graph.invoke({"aggregate": []}, {"recursion_limit": 4})
except GraphRecursionError:
    print("Recursion Error")

Node A sees []
Node B sees ['A']
Node C sees ['A', 'B']
Node D sees ['A', 'B']
Node A sees ['A', 'B', 'C', 'D']
Recursion Error
python  theme={null}
  import operator
  from typing import Annotated, Literal
  from typing_extensions import TypedDict
  from langgraph.graph import StateGraph, START, END
  from langgraph.managed.is_last_step import RemainingSteps

class State(TypedDict):
      aggregate: Annotated[list, operator.add]
      remaining_steps: RemainingSteps

def a(state: State):
      print(f'Node A sees {state["aggregate"]}')
      return {"aggregate": ["A"]}

def b(state: State):
      print(f'Node B sees {state["aggregate"]}')
      return {"aggregate": ["B"]}

# Define nodes
  builder = StateGraph(State)
  builder.add_node(a)
  builder.add_node(b)

# Define edges
  def route(state: State) -> Literal["b", END]:
      if state["remaining_steps"] <= 2:
          return END
      else:
          return "b"

builder.add_edge(START, "a")
  builder.add_conditional_edges("a", route)
  builder.add_edge("b", "a")
  graph = builder.compile()

# Test it out
  result = graph.invoke({"aggregate": []}, {"recursion_limit": 4})
  print(result)
  
  Node A sees []
  Node B sees ['A']
  Node A sees ['A', 'B']
  {'aggregate': ['A', 'B', 'A']}
  python  theme={null}
  import operator
  from typing import Annotated, Literal
  from typing_extensions import TypedDict
  from langgraph.graph import StateGraph, START, END

class State(TypedDict):
      aggregate: Annotated[list, operator.add]

def a(state: State):
      print(f'Node A sees {state["aggregate"]}')
      return {"aggregate": ["A"]}

def b(state: State):
      print(f'Node B sees {state["aggregate"]}')
      return {"aggregate": ["B"]}

def c(state: State):
      print(f'Node C sees {state["aggregate"]}')
      return {"aggregate": ["C"]}

def d(state: State):
      print(f'Node D sees {state["aggregate"]}')
      return {"aggregate": ["D"]}

# Define nodes
  builder = StateGraph(State)
  builder.add_node(a)
  builder.add_node(b)
  builder.add_node(c)
  builder.add_node(d)

# Define edges
  def route(state: State) -> Literal["b", END]:
      if len(state["aggregate"]) < 7:
          return "b"
      else:
          return END

builder.add_edge(START, "a")
  builder.add_conditional_edges("a", route)
  builder.add_edge("b", "c")
  builder.add_edge("b", "d")
  builder.add_edge(["c", "d"], "a")
  graph = builder.compile()
  python  theme={null}
  from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))
  python  theme={null}
  result = graph.invoke({"aggregate": []})
  
  Node A sees []
  Node B sees ['A']
  Node D sees ['A', 'B']
  Node C sees ['A', 'B']
  Node A sees ['A', 'B', 'C', 'D']
  Node B sees ['A', 'B', 'C', 'D', 'A']
  Node D sees ['A', 'B', 'C', 'D', 'A', 'B']
  Node C sees ['A', 'B', 'C', 'D', 'A', 'B']
  Node A sees ['A', 'B', 'C', 'D', 'A', 'B', 'C', 'D']
  python  theme={null}
  from langgraph.errors import GraphRecursionError

try:
      result = graph.invoke({"aggregate": []}, {"recursion_limit": 4})
  except GraphRecursionError:
      print("Recursion Error")
  
  Node A sees []
  Node B sees ['A']
  Node C sees ['A', 'B']
  Node D sees ['A', 'B']
  Node A sees ['A', 'B', 'C', 'D']
  Recursion Error
  shell  theme={null}
    pip install -U "langchain[openai]"
    python init_chat_model theme={null}
      import os
      from langchain.chat_models import init_chat_model

os.environ["OPENAI_API_KEY"] = "sk-..."

model = init_chat_model("gpt-4.1")
      python Model Class theme={null}
      import os
      from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "sk-..."

model = ChatOpenAI(model="gpt-4.1")
      shell  theme={null}
    pip install -U "langchain[anthropic]"
    python init_chat_model theme={null}
      import os
      from langchain.chat_models import init_chat_model

os.environ["ANTHROPIC_API_KEY"] = "sk-..."

model = init_chat_model("claude-sonnet-4-5-20250929")
      python Model Class theme={null}
      import os
      from langchain_anthropic import ChatAnthropic

os.environ["ANTHROPIC_API_KEY"] = "sk-..."

model = ChatAnthropic(model="claude-sonnet-4-5-20250929")
      shell  theme={null}
    pip install -U "langchain[openai]"
    python init_chat_model theme={null}
      import os
      from langchain.chat_models import init_chat_model

os.environ["AZURE_OPENAI_API_KEY"] = "..."
      os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
      os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

model = init_chat_model(
          "azure_openai:gpt-4.1",
          azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
      )
      python Model Class theme={null}
      import os
      from langchain_openai import AzureChatOpenAI

os.environ["AZURE_OPENAI_API_KEY"] = "..."
      os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
      os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

model = AzureChatOpenAI(
          model="gpt-4.1",
          azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
      )
      shell  theme={null}
    pip install -U "langchain[google-genai]"
    python init_chat_model theme={null}
      import os
      from langchain.chat_models import init_chat_model

os.environ["GOOGLE_API_KEY"] = "..."

model = init_chat_model("google_genai:gemini-2.5-flash-lite")
      python Model Class theme={null}
      import os
      from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = "..."

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
      shell  theme={null}
    pip install -U "langchain[aws]"
    python init_chat_model theme={null}
      from langchain.chat_models import init_chat_model

# Follow the steps here to configure your credentials:
      # https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

model = init_chat_model(
          "anthropic.claude-3-5-sonnet-20240620-v1:0",
          model_provider="bedrock_converse",
      )
      python Model Class theme={null}
      from langchain_aws import ChatBedrock

model = ChatBedrock(model="anthropic.claude-3-5-sonnet-20240620-v1:0")
      python  theme={null}
from langchain.chat_models import init_chat_model
from langgraph.graph import MessagesState, StateGraph

async def node(state: MessagesState):  # [!code highlight]
    new_message = await llm.ainvoke(state["messages"])  # [!code highlight]
    return {"messages": [new_message]}

builder = StateGraph(MessagesState).add_node(node).set_entry_point("node")
graph = builder.compile()

input_message = {"role": "user", "content": "Hello"}
result = await graph.ainvoke({"messages": [input_message]})  # [!code highlight]
python  theme={null}
def my_node(state: State) -> Command[Literal["my_other_node"]]:
    return Command(
        # state update
        update={"foo": "bar"},
        # control flow
        goto="my_other_node"
    )
python  theme={null}
import random
from typing_extensions import TypedDict, Literal
from langgraph.graph import StateGraph, START
from langgraph.types import Command

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
<img src="https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/graph_api_image_7.png?fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=e1b99e7efe45b1fdc5836d590d5fbbc3" alt="Simple loop graph" data-og-width="188" width="188" data-og-height="249" height="249" data-path="oss/images/graph_api_image_7.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/graph_api_image_7.png?w=280&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=a443c1ddc2f6a4e7c73f4482c7d63912 280w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/graph_api_image_7.png?w=560&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=f65d82d8aaeb024beb5da1aa2948bcdb 560w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/graph_api_image_7.png?w=840&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=b95f4df2fb69f28779a1d8dd113409d0 840w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/graph_api_image_7.png?w=1100&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=bdb4011d05756c10a1c7b5dea683fdb7 1100w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/graph_api_image_7.png?w=1650&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=dde791caa4279a6248b59b70df99dd2c 1650w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/graph_api_image_7.png?w=2500&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=e4d568719f1761ff3a3d2ea9175241d8 2500w" />

This architecture is similar to a [ReAct agent](/oss/python/langgraph/workflows-agents) in which node `"a"` is a tool-calling model, and node `"b"` represents the tools.

In our `route` conditional edge, we specify that we should end after the `"aggregate"` list in the state passes a threshold length.

Invoking the graph, we see that we alternate between nodes `"a"` and `"b"` before terminating once we reach the termination condition.
```

Example 3 (unknown):
```unknown

```

Example 4 (unknown):
```unknown
### Impose a recursion limit

In some applications, we may not have a guarantee that we will reach a given termination condition. In these cases, we can set the graph's [recursion limit](/oss/python/langgraph/graph-api#recursion-limit). This will raise a `GraphRecursionError` after a given number of [supersteps](/oss/python/langgraph/graph-api#graphs). We can then catch and handle this exception:
```

---

## LangGraph runtime

**URL:** llms-txt#langgraph-runtime

**Contents:**
- Overview
- Actors
- Channels
- Examples
- High-level API

Source: https://docs.langchain.com/oss/python/langgraph/pregel

[`Pregel`](https://reference.langchain.com/python/langgraph/pregel/) implements LangGraph's runtime, managing the execution of LangGraph applications.

Compiling a [StateGraph](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph) or creating an [`@entrypoint`](https://reference.langchain.com/python/langgraph/func/#langgraph.func.entrypoint) produces a [`Pregel`](https://reference.langchain.com/python/langgraph/pregel/) instance that can be invoked with input.

This guide explains the runtime at a high level and provides instructions for directly implementing applications with Pregel.

> **Note:** The [`Pregel`](https://reference.langchain.com/python/langgraph/pregel/) runtime is named after [Google's Pregel algorithm](https://research.google/pubs/pub37252/), which describes an efficient method for large-scale parallel computation using graphs.

In LangGraph, Pregel combines [**actors**](https://en.wikipedia.org/wiki/Actor_model) and **channels** into a single application. **Actors** read data from channels and write data to channels. Pregel organizes the execution of the application into multiple steps, following the **Pregel Algorithm**/**Bulk Synchronous Parallel** model.

Each step consists of three phases:

* **Plan**: Determine which **actors** to execute in this step. For example, in the first step, select the **actors** that subscribe to the special **input** channels; in subsequent steps, select the **actors** that subscribe to channels updated in the previous step.
* **Execution**: Execute all selected **actors** in parallel, until all complete, or one fails, or a timeout is reached. During this phase, channel updates are invisible to actors until the next step.
* **Update**: Update the channels with the values written by the **actors** in this step.

Repeat until no **actors** are selected for execution, or a maximum number of steps is reached.

An **actor** is a `PregelNode`. It subscribes to channels, reads data from them, and writes data to them. It can be thought of as an **actor** in the Pregel algorithm. `PregelNodes` implement LangChain's Runnable interface.

Channels are used to communicate between actors (PregelNodes). Each channel has a value type, an update type, and an update function – which takes a sequence of updates and modifies the stored value. Channels can be used to send data from one chain to another, or to send data from a chain to itself in a future step. LangGraph provides a number of built-in channels:

* [`LastValue`](https://reference.langchain.com/python/langgraph/channels/#langgraph.channels.LastValue): The default channel, stores the last value sent to the channel, useful for input and output values, or for sending data from one step to the next.
* [`Topic`](https://reference.langchain.com/python/langgraph/channels/#langgraph.channels.Topic): A configurable PubSub Topic, useful for sending multiple values between **actors**, or for accumulating output. Can be configured to deduplicate values or to accumulate values over the course of multiple steps.
* [`BinaryOperatorAggregate`](https://reference.langchain.com/python/langgraph/pregel/#langgraph.pregel.Pregel--advanced-channels-context-and-binaryoperatoraggregate): stores a persistent value, updated by applying a binary operator to the current value and each update sent to the channel, useful for computing aggregates over multiple steps; e.g.,`total = BinaryOperatorAggregate(int, operator.add)`

While most users will interact with Pregel through the [StateGraph](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph) API or the [`@entrypoint`](https://reference.langchain.com/python/langgraph/func/#langgraph.func.entrypoint) decorator, it is possible to interact with Pregel directly.

Below are a few different examples to give you a sense of the Pregel API.

<Tabs>
  <Tab title="Single node">

<Tab title="Multiple nodes">

<Tab title="BinaryOperatorAggregate">
    This example demonstrates how to use the [`BinaryOperatorAggregate`](https://reference.langchain.com/python/langgraph/pregel/#langgraph.pregel.Pregel--advanced-channels-context-and-binaryoperatoraggregate) channel to implement a reducer.

<Tab title="Cycle">
    This example demonstrates how to introduce a cycle in the graph, by having
    a chain write to a channel it subscribes to. Execution will continue
    until a `None` value is written to the channel.

LangGraph provides two high-level APIs for creating a Pregel application: the [StateGraph (Graph API)](/oss/python/langgraph/graph-api) and the [Functional API](/oss/python/langgraph/functional-api).

<Tabs>
  <Tab title="StateGraph (Graph API)">
    The [StateGraph (Graph API)](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph) is a higher-level abstraction that simplifies the creation of Pregel applications. It allows you to define a graph of nodes and edges. When you compile the graph, the StateGraph API automatically creates the Pregel application for you.

The compiled Pregel instance will be associated with a list of nodes and channels. You can inspect the nodes and channels by printing them.

You will see something like this:

You should see something like this

<Tab title="Functional API">
    In the [Functional API](/oss/python/langgraph/functional-api), you can use an [`@entrypoint`](https://reference.langchain.com/python/langgraph/func/#langgraph.func.entrypoint) to create a Pregel application. The `entrypoint` decorator allows you to define a function that takes input and returns output.

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/langgraph/pregel.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
</Tab>

  <Tab title="Multiple nodes">
```

Example 3 (unknown):
```unknown

```

Example 4 (unknown):
```unknown
</Tab>

  <Tab title="Topic">
```

---

## Use the graph API

**URL:** llms-txt#use-the-graph-api

**Contents:**
- Setup
- Define and update state
  - Define state
  - Update state
  - Process state updates with reducers
  - Bypass reducers with `Overwrite`
  - Define input and output schemas

Source: https://docs.langchain.com/oss/python/langgraph/use-graph-api

This guide demonstrates the basics of LangGraph's Graph API. It walks through [state](#define-and-update-state), as well as composing common graph structures such as [sequences](#create-a-sequence-of-steps), [branches](#create-branches), and [loops](#create-and-control-loops). It also covers LangGraph's control features, including the [Send API](#map-reduce-and-the-send-api) for map-reduce workflows and the [Command API](#combine-control-flow-and-state-updates-with-command) for combining state updates with "hops" across nodes.

<Tip>
  **Set up LangSmith for better debugging**

Sign up for [LangSmith](https://smith.langchain.com) to quickly spot issues and improve the performance of your LangGraph projects. LangSmith lets you use trace data to debug, test, and monitor your LLM apps built with LangGraph — read more about how to get started in the [docs](/langsmith/observability).
</Tip>

## Define and update state

Here we show how to define and update [state](/oss/python/langgraph/graph-api#state) in LangGraph. We will demonstrate:

1. How to use state to define a graph's [schema](/oss/python/langgraph/graph-api#schema)
2. How to use [reducers](/oss/python/langgraph/graph-api#reducers) to control how state updates are processed.

[State](/oss/python/langgraph/graph-api#state) in LangGraph can be a `TypedDict`, `Pydantic` model, or dataclass. Below we will use `TypedDict`. See [this section](#use-pydantic-models-for-graph-state) for detail on using Pydantic.

By default, graphs will have the same input and output schema, and the state determines that schema. See [this section](#define-input-and-output-schemas) for how to define distinct input and output schemas.

Let's consider a simple example using [messages](/oss/python/langgraph/graph-api#messagesstate). This represents a versatile formulation of state for many LLM applications. See our [concepts page](/oss/python/langgraph/graph-api#working-with-messages-in-graph-state) for more detail.

This state tracks a list of [message](https://python.langchain.com/docs/concepts/messages/) objects, as well as an extra integer field.

Let's build an example graph with a single node. Our [node](/oss/python/langgraph/graph-api#nodes) is just a Python function that reads our graph's state and makes updates to it. The first argument to this function will always be the state:

This node simply appends a message to our message list, and populates an extra field.

<Warning>
  Nodes should return updates to the state directly, instead of mutating the state.
</Warning>

Let's next define a simple graph containing this node. We use [`StateGraph`](/oss/python/langgraph/graph-api#stategraph) to define a graph that operates on this state. We then use [`add_node`](/oss/python/langgraph/graph-api#nodes) populate our graph.

LangGraph provides built-in utilities for visualizing your graph. Let's inspect our graph. See [this section](#visualize-your-graph) for detail on visualization.

<img src="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_1.png?fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=cf3d978b707847e166d5ed15bc7cbbe4" alt="Simple graph with single node" data-og-width="107" width="107" data-og-height="134" height="134" data-path="oss/images/graph_api_image_1.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_1.png?w=280&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=498bbdb0192eb26ab115d51b53fcb64c 280w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_1.png?w=560&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=94cbad4b92d5b887dff2bfbb6f8e0c6c 560w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_1.png?w=840&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=d90d58640d49e3fd4e558ab56acf4817 840w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_1.png?w=1100&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=cad59990b0c551a2aa96b684b102b953 1100w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_1.png?w=1650&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=318736f22c69f66c48f4189db3e39235 1650w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_1.png?w=2500&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=6740141ec001a9a4275cecfac67b9c55 2500w" />

In this case, our graph just executes a single node. Let's proceed with a simple invocation:

* We kicked off invocation by updating a single key of the state.
* We receive the entire state in the invocation result.

For convenience, we frequently inspect the content of [message objects](https://python.langchain.com/docs/concepts/messages/) via pretty-print:

### Process state updates with reducers

Each key in the state can have its own independent [reducer](/oss/python/langgraph/graph-api#reducers) function, which controls how updates from nodes are applied. If no reducer function is explicitly specified then it is assumed that all updates to the key should override it.

For `TypedDict` state schemas, we can define reducers by annotating the corresponding field of the state with a reducer function.

In the earlier example, our node updated the `"messages"` key in the state by appending a message to it. Below, we add a reducer to this key, such that updates are automatically appended:

Now our node can be simplified:

In practice, there are additional considerations for updating lists of messages:

* We may wish to update an existing message in the state.
* We may want to accept short-hands for [message formats](/oss/python/langgraph/graph-api#using-messages-in-your-graph), such as [OpenAI format](https://python.langchain.com/docs/concepts/messages/#openai-format).

LangGraph includes a built-in reducer [`add_messages`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.message.add_messages) that handles these considerations:

This is a versatile representation of state for applications involving [chat models](https://python.langchain.com/docs/concepts/chat_models/). LangGraph includes a pre-built `MessagesState` for convenience, so that we can have:

### Bypass reducers with `Overwrite`

In some cases, you may want to bypass a reducer and directly overwrite a state value. LangGraph provides the [`Overwrite`](https://reference.langchain.com/python/langgraph/types/) type for this purpose. When a node returns a value wrapped with `Overwrite`, the reducer is bypassed and the channel is set directly to that value.

This is useful when you want to reset or replace accumulated state rather than merge it with existing values.

You can also use JSON format with the special key `"__overwrite__"`:

<Warning>
  When nodes execute in parallel, only one node can use `Overwrite` on the same state key in a given super-step. If multiple nodes attempt to overwrite the same key in the same super-step, an `InvalidUpdateError` will be raised.
</Warning>

### Define input and output schemas

By default, `StateGraph` operates with a single schema, and all nodes are expected to communicate using that schema. However, it's also possible to define distinct input and output schemas for a graph.

When distinct schemas are specified, an internal schema will still be used for communication between nodes. The input schema ensures that the provided input matches the expected structure, while the output schema filters the internal data to return only the relevant information according to the defined output schema.

Below, we'll see how to define distinct input and output schema.

```python  theme={null}
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
</CodeGroup>

<Tip>
  **Set up LangSmith for better debugging**

  Sign up for [LangSmith](https://smith.langchain.com) to quickly spot issues and improve the performance of your LangGraph projects. LangSmith lets you use trace data to debug, test, and monitor your LLM apps built with LangGraph — read more about how to get started in the [docs](/langsmith/observability).
</Tip>

## Define and update state

Here we show how to define and update [state](/oss/python/langgraph/graph-api#state) in LangGraph. We will demonstrate:

1. How to use state to define a graph's [schema](/oss/python/langgraph/graph-api#schema)
2. How to use [reducers](/oss/python/langgraph/graph-api#reducers) to control how state updates are processed.

### Define state

[State](/oss/python/langgraph/graph-api#state) in LangGraph can be a `TypedDict`, `Pydantic` model, or dataclass. Below we will use `TypedDict`. See [this section](#use-pydantic-models-for-graph-state) for detail on using Pydantic.

By default, graphs will have the same input and output schema, and the state determines that schema. See [this section](#define-input-and-output-schemas) for how to define distinct input and output schemas.

Let's consider a simple example using [messages](/oss/python/langgraph/graph-api#messagesstate). This represents a versatile formulation of state for many LLM applications. See our [concepts page](/oss/python/langgraph/graph-api#working-with-messages-in-graph-state) for more detail.
```

Example 3 (unknown):
```unknown
This state tracks a list of [message](https://python.langchain.com/docs/concepts/messages/) objects, as well as an extra integer field.

### Update state

Let's build an example graph with a single node. Our [node](/oss/python/langgraph/graph-api#nodes) is just a Python function that reads our graph's state and makes updates to it. The first argument to this function will always be the state:
```

Example 4 (unknown):
```unknown
This node simply appends a message to our message list, and populates an extra field.

<Warning>
  Nodes should return updates to the state directly, instead of mutating the state.
</Warning>

Let's next define a simple graph containing this node. We use [`StateGraph`](/oss/python/langgraph/graph-api#stategraph) to define a graph that operates on this state. We then use [`add_node`](/oss/python/langgraph/graph-api#nodes) populate our graph.
```

---

## Human-in-the-loop leverages LangGraph's persistence layer.

**URL:** llms-txt#human-in-the-loop-leverages-langgraph's-persistence-layer.

---

## Add edges

**URL:** llms-txt#add-edges

**Contents:**
- Create branches
  - Run graph nodes in parallel
  - Defer node execution
  - Conditional branching
- Map-Reduce and the Send API

builder.add_edge(START, "step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", "step_3")
python  theme={null}
builder = StateGraph(State).add_sequence([step_1, step_2, step_3])
builder.add_edge(START, "step_1")
python  theme={null}
  from typing_extensions import TypedDict

class State(TypedDict):
      value_1: str
      value_2: int
  python  theme={null}
  def step_1(state: State):
      return {"value_1": "a"}

def step_2(state: State):
      current_value_1 = state["value_1"]
      return {"value_1": f"{current_value_1} b"}

def step_3(state: State):
      return {"value_2": 10}
  python  theme={null}
  from langgraph.graph import START, StateGraph

builder = StateGraph(State)

# Add nodes
  builder.add_node(step_1)
  builder.add_node(step_2)
  builder.add_node(step_3)

# Add edges
  builder.add_edge(START, "step_1")
  builder.add_edge("step_1", "step_2")
  builder.add_edge("step_2", "step_3")
  python  theme={null}
    builder.add_node("my_node", step_1)
    python  theme={null}
  graph = builder.compile()
  python  theme={null}
  from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))
  python  theme={null}
  graph.invoke({"value_1": "c"})
  
  {'value_1': 'a b', 'value_2': 10}
  python  theme={null}
    builder = StateGraph(State).add_sequence([step_1, step_2, step_3])  # [!code highlight]
    builder.add_edge(START, "step_1")

graph = builder.compile()

graph.invoke({"value_1": "c"})
    python  theme={null}
import operator
from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    aggregate: Annotated[list, operator.add]

def a(state: State):
    print(f'Adding "A" to {state["aggregate"]}')
    return {"aggregate": ["A"]}

def b(state: State):
    print(f'Adding "B" to {state["aggregate"]}')
    return {"aggregate": ["B"]}

def c(state: State):
    print(f'Adding "C" to {state["aggregate"]}')
    return {"aggregate": ["C"]}

def d(state: State):
    print(f'Adding "D" to {state["aggregate"]}')
    return {"aggregate": ["D"]}

builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(c)
builder.add_node(d)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)
graph = builder.compile()
python  theme={null}
from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))
python  theme={null}
graph.invoke({"aggregate": []}, {"configurable": {"thread_id": "foo"}})

Adding "A" to []
Adding "B" to ['A']
Adding "C" to ['A']
Adding "D" to ['A', 'B', 'C']
python  theme={null}
  graph.invoke({"value_1": "c"}, {"configurable": {"max_concurrency": 10}})
  python  theme={null}
import operator
from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    aggregate: Annotated[list, operator.add]

def a(state: State):
    print(f'Adding "A" to {state["aggregate"]}')
    return {"aggregate": ["A"]}

def b(state: State):
    print(f'Adding "B" to {state["aggregate"]}')
    return {"aggregate": ["B"]}

def b_2(state: State):
    print(f'Adding "B_2" to {state["aggregate"]}')
    return {"aggregate": ["B_2"]}

def c(state: State):
    print(f'Adding "C" to {state["aggregate"]}')
    return {"aggregate": ["C"]}

def d(state: State):
    print(f'Adding "D" to {state["aggregate"]}')
    return {"aggregate": ["D"]}

builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(b_2)
builder.add_node(c)
builder.add_node(d, defer=True)  # [!code highlight]
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b_2")
builder.add_edge("b_2", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)
graph = builder.compile()
python  theme={null}
from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))
python  theme={null}
graph.invoke({"aggregate": []})

Adding "A" to []
Adding "B" to ['A']
Adding "C" to ['A']
Adding "B_2" to ['A', 'B', 'C']
Adding "D" to ['A', 'B', 'C', 'B_2']
python  theme={null}
import operator
from typing import Annotated, Literal, Sequence
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    aggregate: Annotated[list, operator.add]
    # Add a key to the state. We will set this key to determine
    # how we branch.
    which: str

def a(state: State):
    print(f'Adding "A" to {state["aggregate"]}')
    return {"aggregate": ["A"], "which": "c"}  # [!code highlight]

def b(state: State):
    print(f'Adding "B" to {state["aggregate"]}')
    return {"aggregate": ["B"]}

def c(state: State):
    print(f'Adding "C" to {state["aggregate"]}')
    return {"aggregate": ["C"]}

builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(c)
builder.add_edge(START, "a")
builder.add_edge("b", END)
builder.add_edge("c", END)

def conditional_edge(state: State) -> Literal["b", "c"]:
    # Fill in arbitrary logic here that uses the state
    # to determine the next node
    return state["which"]

builder.add_conditional_edges("a", conditional_edge)  # [!code highlight]

graph = builder.compile()
python  theme={null}
from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))
python  theme={null}
result = graph.invoke({"aggregate": []})
print(result)

Adding "A" to []
Adding "C" to ['A']
{'aggregate': ['A', 'C'], 'which': 'c'}
python  theme={null}
  def route_bc_or_cd(state: State) -> Sequence[str]:
      if state["which"] == "cd":
          return ["c", "d"]
      return ["b", "c"]
  python  theme={null}
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing_extensions import TypedDict, Annotated
import operator

class OverallState(TypedDict):
    topic: str
    subjects: list[str]
    jokes: Annotated[list[str], operator.add]
    best_selected_joke: str

def generate_topics(state: OverallState):
    return {"subjects": ["lions", "elephants", "penguins"]}

def generate_joke(state: OverallState):
    joke_map = {
        "lions": "Why don't lions like fast food? Because they can't catch it!",
        "elephants": "Why don't elephants use computers? They're afraid of the mouse!",
        "penguins": "Why don't penguins like talking to strangers at parties? Because they find it hard to break the ice."
    }
    return {"jokes": [joke_map[state["subject"]]]}

def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]

def best_joke(state: OverallState):
    return {"best_selected_joke": "penguins"}

builder = StateGraph(OverallState)
builder.add_node("generate_topics", generate_topics)
builder.add_node("generate_joke", generate_joke)
builder.add_node("best_joke", best_joke)
builder.add_edge(START, "generate_topics")
builder.add_conditional_edges("generate_topics", continue_to_jokes, ["generate_joke"])
builder.add_edge("generate_joke", "best_joke")
builder.add_edge("best_joke", END)
graph = builder.compile()
python  theme={null}
from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))
python  theme={null}

**Examples:**

Example 1 (unknown):
```unknown
We can also use the built-in shorthand `.add_sequence`:
```

Example 2 (unknown):
```unknown
<Accordion title="Why split application steps into a sequence with LangGraph?">
  LangGraph makes it easy to add an underlying persistence layer to your application.
  This allows state to be checkpointed in between the execution of nodes, so your LangGraph nodes govern:

  * How state updates are [checkpointed](/oss/python/langgraph/persistence)
  * How interruptions are resumed in [human-in-the-loop](/oss/python/langgraph/interrupts) workflows
  * How we can "rewind" and branch-off executions using LangGraph's [time travel](/oss/python/langgraph/use-time-travel) features

  They also determine how execution steps are [streamed](/oss/python/langgraph/streaming), and how your application is visualized and debugged using [Studio](/langsmith/studio).

  Let's demonstrate an end-to-end example. We will create a sequence of three steps:

  1. Populate a value in a key of the state
  2. Update the same value
  3. Populate a different value

  Let's first define our [state](/oss/python/langgraph/graph-api#state). This governs the [schema of the graph](/oss/python/langgraph/graph-api#schema), and can also specify how to apply updates. See [this section](#process-state-updates-with-reducers) for more detail.

  In our case, we will just keep track of two values:
```

Example 3 (unknown):
```unknown
Our [nodes](/oss/python/langgraph/graph-api#nodes) are just Python functions that read our graph's state and make updates to it. The first argument to this function will always be the state:
```

Example 4 (unknown):
```unknown
<Note>
    Note that when issuing updates to the state, each node can just specify the value of the key it wishes to update.

    By default, this will **overwrite** the value of the corresponding key. You can also use [reducers](/oss/python/langgraph/graph-api#reducers) to control how updates are processed— for example, you can append successive updates to a key instead. See [this section](#process-state-updates-with-reducers) for more detail.
  </Note>

  Finally, we define the graph. We use [StateGraph](/oss/python/langgraph/graph-api#stategraph) to define a graph that operates on this state.

  We will then use [`add_node`](/oss/python/langgraph/graph-api#messagesstate) and [`add_edge`](/oss/python/langgraph/graph-api#edges) to populate our graph and define its control flow.
```

---

## Add edges to connect nodes

**URL:** llms-txt#add-edges-to-connect-nodes

orchestrator_worker_builder.add_edge(START, "orchestrator")
orchestrator_worker_builder.add_conditional_edges(
    "orchestrator", assign_workers, ["llm_call"]
)
orchestrator_worker_builder.add_edge("llm_call", "synthesizer")
orchestrator_worker_builder.add_edge("synthesizer", END)

---

## Log retriever traces

**URL:** llms-txt#log-retriever-traces

Source: https://docs.langchain.com/langsmith/log-retriever-trace

<Note>
  Nothing will break if you don't log retriever traces in the correct format and data will still be logged. However, the data will not be rendered in a way that is specific to retriever steps.
</Note>

Many LLM applications require looking up documents from vector databases, knowledge graphs, or other types of indexes. Retriever traces are a way to log the documents that are retrieved by the retriever. LangSmith provides special rendering for retrieval steps in traces to make it easier to understand and diagnose retrieval issues. In order for retrieval steps to be rendered correctly, a few small steps need to be taken.

1. Annotate the retriever step with `run_type="retriever"`.

2. Return a list of Python dictionaries or TypeScript objects from the retriever step. Each dictionary should contain the following keys:

* `page_content`: The text of the document.
   * `type`: This should always be "Document".
   * `metadata`: A python dictionary or TypeScript object containing metadata about the document. This metadata will be displayed in the trace.

The following code snippets show how to log a retrieval steps in Python and TypeScript.

The following image shows how a retriever step is rendered in a trace. The contents along with the metadata are displayed with each document.

<img src="https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/retriever-trace.png?fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=786c74f63e4c94d35535aa46ac9f38f4" alt="" data-og-width="1614" width="1614" data-og-height="736" height="736" data-path="langsmith/images/retriever-trace.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/retriever-trace.png?w=280&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=c2e2720a208cc2402e869e214609ec21 280w, https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/retriever-trace.png?w=560&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=8949f5484519221d159191e9437a862f 560w, https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/retriever-trace.png?w=840&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=7f376f3ca4575ffc08eb7fc6bdc0db4c 840w, https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/retriever-trace.png?w=1100&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=06ac1c1dfa24dab91376f2d641fe9aa2 1100w, https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/retriever-trace.png?w=1650&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=5046d388f4583d270740adfbd1e58539 1650w, https://mintcdn.com/langchain-5e9cc07a/Fr2lazPB4XVeEA7l/langsmith/images/retriever-trace.png?w=2500&fit=max&auto=format&n=Fr2lazPB4XVeEA7l&q=85&s=aa3aae9c839dd00ca450cfeb7b285371 2500w" />

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/log-retriever-trace.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown

```

---

## Invoke the graph with the initial state

**URL:** llms-txt#invoke-the-graph-with-the-initial-state

**Contents:**
  - Use Pydantic models for graph state

response = graph.invoke(
    {
        "a": "set at start",
    }
)

print()
print(f"Output of graph invocation: {response}")

Entered node `node_1`:
    Input: {'a': 'set at start'}.
    Returned: {'private_data': 'set by node_1'}
Entered node `node_2`:
    Input: {'private_data': 'set by node_1'}.
    Returned: {'a': 'set by node_2'}
Entered node `node_3`:
    Input: {'a': 'set by node_2'}.
    Returned: {'a': 'set by node_3'}

Output of graph invocation: {'a': 'set by node_3'}
python  theme={null}
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from pydantic import BaseModel

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
### Use Pydantic models for graph state

A [StateGraph](https://langchain-ai.github.io/langgraph/reference/graphs.md#langgraph.graph.StateGraph) accepts a [`state_schema`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema) argument on initialization that specifies the "shape" of the state that the nodes in the graph can access and update.

In our examples, we typically use a python-native `TypedDict` or [`dataclass`](https://docs.python.org/3/library/dataclasses.html) for `state_schema`, but [`state_schema`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema) can be any [type](https://docs.python.org/3/library/stdtypes.html#type-objects).

Here, we'll see how a [Pydantic BaseModel](https://docs.pydantic.dev/latest/api/base_model/) can be used for [`state_schema`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema) to add run-time validation on **inputs**.

<Note>
  **Known Limitations**

  * Currently, the output of the graph will **NOT** be an instance of a pydantic model.
  * Run-time validation only occurs on inputs to the first node in the graph, not on subsequent nodes or outputs.
  * The validation error trace from pydantic does not show which node the error arises in.
  * Pydantic's recursive validation can be slow. For performance-sensitive applications, you may want to consider using a `dataclass` instead.
</Note>
```

---

## Graph node for looking up the users purchases

**URL:** llms-txt#graph-node-for-looking-up-the-users-purchases

def lookup(state: State) -> dict:
    args = (
        state[k]
        for k in (
            "customer_first_name",
            "customer_last_name",
            "customer_phone",
            "track_name",
            "album_title",
            "artist_name",
            "purchase_date_iso_8601",
        )
    )
    results = _lookup(*args)
    if not results:
        response = "We did not find any purchases associated with the information you've provided. Are you sure you've entered all of your information correctly?"
        followup = response
    else:
        response = f"Which of the following purchases would you like to be refunded for?\n\n"
        followup = f"Which of the following purchases would you like to be refunded for?\n\n{tabulate(results, headers='keys')}"
    return {
        "messages": [{"role": "assistant", "content": response}],
        "followup": followup,
        "invoice_line_ids": [res["invoice_line_id"] for res in results],
    }

---

## Subgraphs

**URL:** llms-txt#subgraphs

**Contents:**
- Setup
- Invoke a graph from a node

Source: https://docs.langchain.com/oss/python/langgraph/use-subgraphs

This guide explains the mechanics of using subgraphs. A subgraph is a [graph](/oss/python/langgraph/graph-api#graphs) that is used as a [node](/oss/python/langgraph/graph-api#nodes) in another graph.

Subgraphs are useful for:

* Building [multi-agent systems](/oss/python/langchain/multi-agent)
* Re-using a set of nodes in multiple graphs
* Distributing development: when you want different teams to work on different parts of the graph independently, you can define each part as a subgraph, and as long as the subgraph interface (the input and output schemas) is respected, the parent graph can be built without knowing any details of the subgraph

When adding subgraphs, you need to define how the parent graph and the subgraph communicate:

* [Invoke a graph from a node](#invoke-a-graph-from-a-node) — subgraphs are called from inside a node in the parent graph
* [Add a graph as a node](#add-a-graph-as-a-node) — a subgraph is added directly as a node in the parent and **shares [state keys](/oss/python/langgraph/graph-api#state)** with the parent

<Tip>
  **Set up LangSmith for LangGraph development**
  Sign up for [LangSmith](https://smith.langchain.com) to quickly spot issues and improve the performance of your LangGraph projects. LangSmith lets you use trace data to debug, test, and monitor your LLM apps built with LangGraph — read more about how to get started [here](https://docs.smith.langchain.com).
</Tip>

## Invoke a graph from a node

A simple way to implement a subgraph is to invoke a graph from inside the node of another graph. In this case subgraphs can have **completely different schemas** from the parent graph (no shared keys). For example, you might want to keep a private message history for each of the agents in a [multi-agent](/oss/python/langchain/multi-agent) system.

If that's the case for your application, you need to define a node **function that invokes the subgraph**. This function needs to transform the input (parent) state to the subgraph state before invoking the subgraph, and transform the results back to the parent state before returning the state update from the node.

```python  theme={null}
from typing_extensions import TypedDict
from langgraph.graph.state import StateGraph, START

class SubgraphState(TypedDict):
    bar: str

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
</CodeGroup>

<Tip>
  **Set up LangSmith for LangGraph development**
  Sign up for [LangSmith](https://smith.langchain.com) to quickly spot issues and improve the performance of your LangGraph projects. LangSmith lets you use trace data to debug, test, and monitor your LLM apps built with LangGraph — read more about how to get started [here](https://docs.smith.langchain.com).
</Tip>

## Invoke a graph from a node

A simple way to implement a subgraph is to invoke a graph from inside the node of another graph. In this case subgraphs can have **completely different schemas** from the parent graph (no shared keys). For example, you might want to keep a private message history for each of the agents in a [multi-agent](/oss/python/langchain/multi-agent) system.

If that's the case for your application, you need to define a node **function that invokes the subgraph**. This function needs to transform the input (parent) state to the subgraph state before invoking the subgraph, and transform the results back to the parent state before returning the state update from the node.
```

---

## Invoke the graph with an input and print the result

**URL:** llms-txt#invoke-the-graph-with-an-input-and-print-the-result

**Contents:**
  - Pass private state between nodes

print(graph.invoke({"question": "hi"}))

{'answer': 'bye'}
python  theme={null}
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
Notice that the output of invoke only includes the output schema.

### Pass private state between nodes

In some cases, you may want nodes to exchange information that is crucial for intermediate logic but doesn't need to be part of the main schema of the graph. This private data is not relevant to the overall input/output of the graph and should only be shared between certain nodes.

Below, we'll create an example sequential graph consisting of three nodes (node\_1, node\_2 and node\_3), where private data is passed between the first two steps (node\_1 and node\_2), while the third step (node\_3) only has access to the public overall state.
```

---

## Implement a LangGraph integration

**URL:** llms-txt#implement-a-langgraph-integration

Source: https://docs.langchain.com/oss/python/contributing/implement-langgraph

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/contributing/implement-langgraph.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## Use time-travel

**URL:** llms-txt#use-time-travel

**Contents:**
- In a workflow
  - Setup

Source: https://docs.langchain.com/oss/python/langgraph/use-time-travel

When working with non-deterministic systems that make model-based decisions (e.g., agents powered by LLMs), it can be useful to examine their decision-making process in detail:

1. <Icon icon="lightbulb" size={16} /> **Understand reasoning**: Analyze the steps that led to a successful result.
2. <Icon icon="bug" size={16} /> **Debug mistakes**: Identify where and why errors occurred.
3. <Icon icon="magnifying-glass" size={16} /> **Explore alternatives**: Test different paths to uncover better solutions.

LangGraph provides [time travel](/oss/python/langgraph/use-time-travel) functionality to support these use cases. Specifically, you can resume execution from a prior checkpoint — either replaying the same state or modifying it to explore alternatives. In all cases, resuming past execution produces a new fork in the history.

To use [time-travel](/oss/python/langgraph/use-time-travel) in LangGraph:

1. [Run the graph](#1-run-the-graph) with initial inputs using [`invoke`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.invoke) or [`stream`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.stream) methods.
2. [Identify a checkpoint in an existing thread](#2-identify-a-checkpoint): Use the [`get_state_history`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.get_state_history) method to retrieve the execution history for a specific `thread_id` and locate the desired `checkpoint_id`.
   Alternatively, set an [interrupt](/oss/python/langgraph/interrupts) before the node(s) where you want execution to pause. You can then find the most recent checkpoint recorded up to that interrupt.
3. [Update the graph state (optional)](#3-update-the-state-optional): Use the [`update_state`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.update_state) method to modify the graph's state at the checkpoint and resume execution from alternative state.
4. [Resume execution from the checkpoint](#4-resume-execution-from-the-checkpoint): Use the `invoke` or `stream` methods with an input of `None` and a configuration containing the appropriate `thread_id` and `checkpoint_id`.

<Tip>
  For a conceptual overview of time-travel, see [Time travel](/oss/python/langgraph/use-time-travel).
</Tip>

This example builds a simple LangGraph workflow that generates a joke topic and writes a joke using an LLM. It demonstrates how to run the graph, retrieve past execution checkpoints, optionally modify the state, and resume execution from a chosen checkpoint to explore alternate outcomes.

First we need to install the packages required

Next, we need to set API keys for Anthropic (the LLM we will use)

<Tip>
  Sign up for [LangSmith](https://smith.langchain.com) to quickly spot issues and improve the performance of your LangGraph projects. LangSmith lets you use trace data to debug, test, and monitor your LLM apps built with LangGraph.
</Tip>

```python  theme={null}
import uuid

from typing_extensions import TypedDict, NotRequired
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    topic: NotRequired[str]
    joke: NotRequired[str]

model = init_chat_model(
    "claude-sonnet-4-5-20250929",
    temperature=0,
)

def generate_topic(state: State):
    """LLM call to generate a topic for the joke"""
    msg = model.invoke("Give me a funny topic for a joke")
    return {"topic": msg.content}

def write_joke(state: State):
    """LLM call to write a joke based on the topic"""
    msg = model.invoke(f"Write a short joke about {state['topic']}")
    return {"joke": msg.content}

**Examples:**

Example 1 (unknown):
```unknown
Next, we need to set API keys for Anthropic (the LLM we will use)
```

Example 2 (unknown):
```unknown
<Tip>
  Sign up for [LangSmith](https://smith.langchain.com) to quickly spot issues and improve the performance of your LangGraph projects. LangSmith lets you use trace data to debug, test, and monitor your LLM apps built with LangGraph.
</Tip>
```

---

## Build the graph with input and output schemas specified

**URL:** llms-txt#build-the-graph-with-input-and-output-schemas-specified

builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
builder.add_node(answer_node)  # Add the answer node
builder.add_edge(START, "answer_node")  # Define the starting edge
builder.add_edge("answer_node", END)  # Define the ending edge
graph = builder.compile()  # Compile the graph

---

## Graph node for extracting user info and routing to lookup/refund/END.

**URL:** llms-txt#graph-node-for-extracting-user-info-and-routing-to-lookup/refund/end.

async def gather_info(state: State) -> Command[Literal["lookup", "refund", END]]:
    info = await info_llm.ainvoke(
        [
            {"role": "system", "content": gather_info_instructions},
            *state["messages"],
        ]
    )
    parsed = info["parsed"]
    if any(parsed[k] for k in ("invoice_id", "invoice_line_ids")):
        goto = "refund"
    elif all(
        parsed[k]
        for k in ("customer_first_name", "customer_last_name", "customer_phone")
    ):
        goto = "lookup"
    else:
        goto = END
    update = {"messages": [info["raw"]], **parsed}
    return Command(update=update, goto=goto)

---

## NOTE: there are no edges between nodes A, B and C!

**URL:** llms-txt#note:-there-are-no-edges-between-nodes-a,-b-and-c!

**Contents:**
  - Navigate to a node in a parent graph
  - Use inside tools
- Visualize your graph
  - Mermaid
  - PNG

graph = builder.compile()
python  theme={null}
from IPython.display import display, Image

display(Image(graph.get_graph().draw_mermaid_png()))
python  theme={null}
graph.invoke({"foo": ""})

Called A
Called C
python  theme={null}
def my_node(state: State) -> Command[Literal["my_other_node"]]:
    return Command(
        update={"foo": "bar"},
        goto="other_subgraph",  # where `other_subgraph` is a node in the parent graph
        graph=Command.PARENT
    )
python  theme={null}
import operator
from typing_extensions import Annotated

class State(TypedDict):
    # NOTE: we define a reducer here
    foo: Annotated[str, operator.add]  # [!code highlight]

def node_a(state: State):
    print("Called A")
    value = random.choice(["a", "b"])
    # this is a replacement for a conditional edge function
    if value == "a":
        goto = "node_b"
    else:
        goto = "node_c"

# note how Command allows you to BOTH update the graph state AND route to the next node
    return Command(
        update={"foo": value},
        goto=goto,
        # this tells LangGraph to navigate to node_b or node_c in the parent graph
        # NOTE: this will navigate to the closest parent graph relative to the subgraph
        graph=Command.PARENT,  # [!code highlight]
    )

subgraph = StateGraph(State).add_node(node_a).add_edge(START, "node_a").compile()

def node_b(state: State):
    print("Called B")
    # NOTE: since we've defined a reducer, we don't need to manually append
    # new characters to existing 'foo' value. instead, reducer will append these
    # automatically (via operator.add)
    return {"foo": "b"}  # [!code highlight]

def node_c(state: State):
    print("Called C")
    return {"foo": "c"}  # [!code highlight]

builder = StateGraph(State)
builder.add_edge(START, "subgraph")
builder.add_node("subgraph", subgraph)
builder.add_node(node_b)
builder.add_node(node_c)

graph = builder.compile()
python  theme={null}
graph.invoke({"foo": ""})

Called A
Called C
python  theme={null}
@tool
def lookup_user_info(tool_call_id: Annotated[str, InjectedToolCallId], config: RunnableConfig):
    """Use this to look up user information to better assist them with their questions."""
    user_info = get_user_info(config.get("configurable", {}).get("user_id"))
    return Command(
        update={
            # update the state keys
            "user_info": user_info,
            # update the message history
            "messages": [ToolMessage("Successfully looked up user information", tool_call_id=tool_call_id)]
        }
    )
python  theme={null}
import random
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

class MyNode:
    def __init__(self, name: str):
        self.name = name
    def __call__(self, state: State):
        return {"messages": [("assistant", f"Called node {self.name}")]}

def route(state) -> Literal["entry_node", END]:
    if len(state["messages"]) > 10:
        return END
    return "entry_node"

def add_fractal_nodes(builder, current_node, level, max_level):
    if level > max_level:
        return
    # Number of nodes to create at this level
    num_nodes = random.randint(1, 3)  # Adjust randomness as needed
    for i in range(num_nodes):
        nm = ["A", "B", "C"][i]
        node_name = f"node_{current_node}_{nm}"
        builder.add_node(node_name, MyNode(node_name))
        builder.add_edge(current_node, node_name)
        # Recursively add more nodes
        r = random.random()
        if r > 0.2 and level + 1 < max_level:
            add_fractal_nodes(builder, node_name, level + 1, max_level)
        elif r > 0.05:
            builder.add_conditional_edges(node_name, route, node_name)
        else:
            # End
            builder.add_edge(node_name, END)

def build_fractal_graph(max_level: int):
    builder = StateGraph(State)
    entry_point = "entry_node"
    builder.add_node(entry_point, MyNode(entry_point))
    builder.add_edge(START, entry_point)
    add_fractal_nodes(builder, entry_point, 1, max_level)
    # Optional: set a finish point if required
    builder.add_edge(entry_point, END)  # or any specific node
    return builder.compile()

app = build_fractal_graph(3)
python  theme={null}
print(app.get_graph().draw_mermaid())

%%{init: {'flowchart': {'curve': 'linear'}}}%%
graph TD;
    tart__([<p>__start__</p>]):::first
    ry_node(entry_node)
    e_entry_node_A(node_entry_node_A)
    e_entry_node_B(node_entry_node_B)
    e_node_entry_node_B_A(node_node_entry_node_B_A)
    e_node_entry_node_B_B(node_node_entry_node_B_B)
    e_node_entry_node_B_C(node_node_entry_node_B_C)
    nd__([<p>__end__</p>]):::last
    tart__ --> entry_node;
    ry_node --> __end__;
    ry_node --> node_entry_node_A;
    ry_node --> node_entry_node_B;
    e_entry_node_B --> node_node_entry_node_B_A;
    e_entry_node_B --> node_node_entry_node_B_B;
    e_entry_node_B --> node_node_entry_node_B_C;
    e_entry_node_A -.-> entry_node;
    e_entry_node_A -.-> __end__;
    e_node_entry_node_B_A -.-> entry_node;
    e_node_entry_node_B_A -.-> __end__;
    e_node_entry_node_B_B -.-> entry_node;
    e_node_entry_node_B_B -.-> __end__;
    e_node_entry_node_B_C -.-> entry_node;
    e_node_entry_node_B_C -.-> __end__;
    ssDef default fill:#f2f0ff,line-height:1.2
    ssDef first fill-opacity:0
    ssDef last fill:#bfb6fc
python  theme={null}
from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

display(Image(app.get_graph().draw_mermaid_png()))
python  theme={null}
import nest_asyncio

nest_asyncio.apply()  # Required for Jupyter Notebook to run async functions

display(
    Image(
        app.get_graph().draw_mermaid_png(
            curve_style=CurveStyle.LINEAR,
            node_colors=NodeStyles(first="#ffdfba", last="#baffc9", default="#fad7de"),
            wrap_label_n_words=9,
            output_file_path=None,
            draw_method=MermaidDrawMethod.PYPPETEER,
            background_color="white",
            padding=10,
        )
    )
)
python  theme={null}
try:
    display(Image(app.get_graph().draw_png()))
except ImportError:
    print(
        "You likely need to install dependencies for pygraphviz, see more here https://github.com/pygraphviz/pygraphviz/blob/main/INSTALL.txt"
    )
```

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/langgraph/use-graph-api.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
<Warning>
  You might have noticed that we used [`Command`](https://reference.langchain.com/python/langgraph/types/#langgraph.types.Command) as a return type annotation, e.g. `Command[Literal["node_b", "node_c"]]`. This is necessary for the graph rendering and tells LangGraph that `node_a` can navigate to `node_b` and `node_c`.
</Warning>
```

Example 2 (unknown):
```unknown
<img src="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_11.png?fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=f11e5cddedbf2760d40533f294c44aea" alt="Command-based graph navigation" data-og-width="232" width="232" data-og-height="333" height="333" data-path="oss/images/graph_api_image_11.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_11.png?w=280&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=c1b27d92b257a6c4ac57f34f007d0ee1 280w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_11.png?w=560&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=695d0062e5fb8ebea5525379edbba476 560w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_11.png?w=840&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=7bd3f779df628beba60a397674f85b59 840w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_11.png?w=1100&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=85a9194e8b4d9df2d01d10784dcf75d0 1100w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_11.png?w=1650&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=efd9118d4bcd6d1eb92760c573645fbd 1650w, https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/graph_api_image_11.png?w=2500&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=1eb2a132386a64d18582af6978e4ac24 2500w" />

If we run the graph multiple times, we'd see it take different paths (A -> B or A -> C) based on the random choice in node A.
```

Example 3 (unknown):
```unknown

```

Example 4 (unknown):
```unknown
### Navigate to a node in a parent graph

If you are using [subgraphs](/oss/python/langgraph/use-subgraphs), you might want to navigate from a node within a subgraph to a different subgraph (i.e. a different node in the parent graph). To do so, you can specify `graph=Command.PARENT` in `Command`:
```

---

## Define nodes

**URL:** llms-txt#define-nodes

builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)

---

## Note that we're (optionally) passing the memory when compiling the graph

**URL:** llms-txt#note-that-we're-(optionally)-passing-the-memory-when-compiling-the-graph

**Contents:**
  - Create a dataset
  - Create an evaluator
  - Run evaluations

app = workflow.compile()
python  theme={null}
from langsmith import Client

questions = [
    "what's the weather in sf",
    "whats the weather in san fran",
    "whats the weather in tangier"
]

answers = [
    "It's 60 degrees and foggy.",
    "It's 60 degrees and foggy.",
    "It's 90 degrees and sunny.",
]

ls_client = Client()
dataset = ls_client.create_dataset(
    "weather agent",
    inputs=[{"question": q} for q in questions],
    outputs=[{"answers": a} for a in answers],
)
python  theme={null}
judge_llm = init_chat_model("gpt-4o")

async def correct(outputs: dict, reference_outputs: dict) -> bool:
    instructions = (
        "Given an actual answer and an expected answer, determine whether"
        " the actual answer contains all of the information in the"
        " expected answer. Respond with 'CORRECT' if the actual answer"
        " does contain all of the expected information and 'INCORRECT'"
        " otherwise. Do not include anything else in your response."
    )
    # Our graph outputs a State dictionary, which in this case means
    # we'll have a 'messages' key and the final message should
    # be our actual answer.
    actual_answer = outputs["messages"][-1].content
    expected_answer = reference_outputs["answer"]
    user_msg = (
        f"ACTUAL ANSWER: {actual_answer}"
        f"\n\nEXPECTED ANSWER: {expected_answer}"
    )
    response = await judge_llm.ainvoke(
        [
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_msg}
        ]
    )
    return response.content.upper() == "CORRECT"
python  theme={null}
from langsmith import aevaluate

def example_to_state(inputs: dict) -> dict:
  return {"messages": [{"role": "user", "content": inputs['question']}]}

**Examples:**

Example 1 (unknown):
```unknown
### Create a dataset

Let's create a simple dataset of questions and expected responses:
```

Example 2 (unknown):
```unknown
### Create an evaluator

And a simple evaluator:

Requires `langsmith>=0.2.0`
```

Example 3 (unknown):
```unknown
### Run evaluations

Now we can run our evaluations and explore the results. We'll just need to wrap our graph function so that it can take inputs in the format they're stored on our example:

<Note>
  If all of your graph nodes are defined as sync functions then you can use `evaluate` or `aevaluate`. If any of you nodes are defined as async, you'll need to use `aevaluate`
</Note>

Requires `langsmith>=0.2.0`
```

---

## The overall state of the graph (this is the public state shared across nodes)

**URL:** llms-txt#the-overall-state-of-the-graph-(this-is-the-public-state-shared-across-nodes)

class OverallState(BaseModel):
    a: str

def node(state: OverallState):
    return {"a": "goodbye"}

---

## Define graph state

**URL:** llms-txt#define-graph-state

class State(TypedDict):
    foo: str

---

## Rebuild graph at runtime

**URL:** llms-txt#rebuild-graph-at-runtime

**Contents:**
- Prerequisites
- Define graphs
  - No rebuild
  - Rebuild

Source: https://docs.langchain.com/langsmith/graph-rebuild

You might need to rebuild your graph with a different configuration for a new run. For example, you might need to use a different graph state or graph structure depending on the config. This guide shows how you can do this.

<Note>
  **Note**
  In most cases, customizing behavior based on the config should be handled by a single graph where each node can read a config and change its behavior based on it
</Note>

Make sure to check out [this how-to guide](/langsmith/setup-app-requirements-txt) on setting up your app for deployment first.

Let's say you have an app with a simple graph that calls an LLM and returns the response to the user. The app file directory looks like the following:

where the graph is defined in `openai_agent.py`.

In the standard LangGraph API configuration, the server uses the compiled graph instance that's defined at the top level of `openai_agent.py`, which looks like the following:

To make the server aware of your graph, you need to specify a path to the variable that contains the [`CompiledStateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph) instance in your LangGraph API configuration (`langgraph.json`), e.g.:

To make your graph rebuild on each new run with custom configuration, you need to rewrite `openai_agent.py` to instead provide a *function* that takes a config and returns a graph (or compiled graph) instance. Let's say we want to return our existing graph for user ID '1', and a tool-calling agent for other users. We can modify `openai_agent.py` as follows:

```python  theme={null}
from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessageGraph
from langgraph.graph.state import StateGraph
from langgraph.graph.message import add_messages
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from langchain.messages import BaseMessage
from langchain_core.runnables import RunnableConfig

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

model = ChatOpenAI(temperature=0)

def make_default_graph():
    """Make a simple LLM agent"""
    graph_workflow = StateGraph(State)
    def call_model(state):
        return {"messages": [model.invoke(state["messages"])]}

graph_workflow.add_node("agent", call_model)
    graph_workflow.add_edge("agent", END)
    graph_workflow.add_edge(START, "agent")

agent = graph_workflow.compile()
    return agent

def make_alternative_graph():
    """Make a tool-calling agent"""

@tool
    def add(a: float, b: float):
        """Adds two numbers."""
        return a + b

tool_node = ToolNode([add])
    model_with_tools = model.bind_tools([add])
    def call_model(state):
        return {"messages": [model_with_tools.invoke(state["messages"])]}

def should_continue(state: State):
        if state["messages"][-1].tool_calls:
            return "tools"
        else:
            return END

graph_workflow = StateGraph(State)

graph_workflow.add_node("agent", call_model)
    graph_workflow.add_node("tools", tool_node)
    graph_workflow.add_edge("tools", "agent")
    graph_workflow.add_edge(START, "agent")
    graph_workflow.add_conditional_edges("agent", should_continue)

agent = graph_workflow.compile()
    return agent

**Examples:**

Example 1 (unknown):
```unknown
my-app/
|-- requirements.txt
|-- .env
|-- openai_agent.py     # code for your graph
```

Example 2 (unknown):
```unknown
To make the server aware of your graph, you need to specify a path to the variable that contains the [`CompiledStateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph) instance in your LangGraph API configuration (`langgraph.json`), e.g.:
```

Example 3 (unknown):
```unknown
### Rebuild

To make your graph rebuild on each new run with custom configuration, you need to rewrite `openai_agent.py` to instead provide a *function* that takes a config and returns a graph (or compiled graph) instance. Let's say we want to return our existing graph for user ID '1', and a tool-calling agent for other users. We can modify `openai_agent.py` as follows:
```

---

## Next steps

**URL:** llms-txt#next-steps

Now that you've created a prompt, you can use it in your application code. See [how to pull a prompt programmatically](/langsmith/manage-prompts-programmatically#pull-a-prompt).

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/create-a-prompt.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## How to integrate LangGraph into your React application

**URL:** llms-txt#how-to-integrate-langgraph-into-your-react-application

**Contents:**
- Installation
- Example
- Customizing Your UI
  - Loading States
  - Resume a stream after page refresh
  - Thread Management
  - Messages Handling
  - Interrupts
  - Branching
  - Optimistic Updates

Source: https://docs.langchain.com/langsmith/use-stream-react

<Info>
  **Prerequisites**

* [LangSmith](/langsmith/home)
  * [Agent Server](/langsmith/agent-server)
</Info>

The [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) React hook provides a seamless way to integrate LangGraph into your React applications. It handles all the complexities of streaming, state management, and branching logic, letting you focus on building great chat experiences.

* Messages streaming: Handle a stream of message chunks to form a complete message
* Automatic state management for messages, interrupts, loading states, and errors
* Conversation branching: Create alternate conversation paths from any point in the chat history
* UI-agnostic design: bring your own components and styling

Let's explore how to use [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) in your React application.

The [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) provides a solid foundation for creating bespoke chat experiences. For pre-built chat components and interfaces, we also recommend checking out [CopilotKit](https://docs.copilotkit.ai/coagents/quickstart/langgraph) and [assistant-ui](https://www.assistant-ui.com/docs/runtimes/langgraph).

## Customizing Your UI

The [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) hook takes care of all the complex state management behind the scenes, providing you with simple interfaces to build your UI. Here's what you get out of the box:

* Thread state management
* Loading and error states
* Interrupts
* Message handling and updates
* Branching support

Here are some examples on how to use these features effectively:

The `isLoading` property tells you when a stream is active, enabling you to:

* Show a loading indicator
* Disable input fields during processing
* Display a cancel button

### Resume a stream after page refresh

The [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) hook can automatically resume an ongoing run upon mounting by setting `reconnectOnMount: true`. This is useful for continuing a stream after a page refresh, ensuring no messages and events generated during the downtime are lost.

By default the ID of the created run is stored in `window.sessionStorage`, which can be swapped by passing a custom storage in `reconnectOnMount` instead. The storage is used to persist the in-flight run ID for a thread (under `lg:stream:${threadId}` key).

You can also manually manage the resuming process by using the run callbacks to persist the run metadata and the `joinStream` function to resume the stream. Make sure to pass `streamResumable: true` when creating the run; otherwise some events might be lost.

### Thread Management

Keep track of conversations with built-in thread management. You can access the current thread ID and get notified when new threads are created:

We recommend storing the `threadId` in your URL's query parameters to let users resume conversations after page refreshes.

### Messages Handling

The [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) hook will keep track of the message chunks received from the server and concatenate them together to form a complete message. The completed message chunks can be retrieved via the `messages` property.

By default, the `messagesKey` is set to `messages`, where it will append the new messages chunks to `values["messages"]`. If you store messages in a different key, you can change the value of `messagesKey`.

Under the hood, the [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) hook will use the `streamMode: "messages-tuple"` to receive a stream of messages (i.e. individual LLM tokens) from any LangChain chat model invocations inside your graph nodes. Learn more about messages streaming in the [streaming](/langsmith/streaming#messages) guide.

The [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) hook exposes the `interrupt` property, which will be filled with the last interrupt from the thread. You can use interrupts to:

* Render a confirmation UI before executing a node
* Wait for human input, allowing agent to ask the user with clarifying questions

Learn more about interrupts in the [How to handle interrupts](/oss/python/langgraph/interrupts#pause-using-interrupt) guide.

For each message, you can use `getMessagesMetadata()` to get the first checkpoint from which the message has been first seen. You can then create a new run from the checkpoint preceding the first seen checkpoint to create a new branch in a thread.

A branch can be created in following ways:

1. Edit a previous user message.
2. Request a regeneration of a previous assistant message.

For advanced use cases you can use the `experimental_branchTree` property to get the tree representation of the thread, which can be used to render branching controls for non-message based graphs.

### Optimistic Updates

You can optimistically update the client state before performing a network request to the agent, allowing you to provide immediate feedback to the user, such as showing the user message immediately before the agent has seen the request.

### Cached Thread Display

Use the `initialValues` option to display cached thread data immediately while the history is being loaded from the server. This improves user experience by showing cached data instantly when navigating to existing threads.

### Optimistic Thread Creation

Use the `threadId` option in `submit` function to enable optimistic UI patterns where you need to know the thread ID before the thread is actually created.

The [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) hook is friendly for apps written in TypeScript and you can specify types for the state to get better type safety and IDE support.

You can also optionally specify types for different scenarios, such as:

* `ConfigurableType`: Type for the `config.configurable` property (default: `Record<string, unknown>`)
* `InterruptType`: Type for the interrupt value - i.e. contents of `interrupt(...)` function (default: `unknown`)
* `CustomEventType`: Type for the custom events (default: `unknown`)
* `UpdateType`: Type for the submit function (default: `Partial<State>`)

If you're using LangGraph.js, you can also reuse your graph's annotation types. However, make sure to only import the types of the annotation schema in order to avoid importing the entire LangGraph.js runtime (i.e. via `import type { ... }` directive).

The [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) hook provides several callback options to help you respond to different events:

* `onError`: Called when an error occurs.
* `onFinish`: Called when the stream is finished.
* `onUpdateEvent`: Called when an update event is received.
* `onCustomEvent`: Called when a custom event is received. See the [streaming](/oss/python/langgraph/streaming#stream-custom-data) guide to learn how to stream custom events.
* `onMetadataEvent`: Called when a metadata event is received, which contains the Run ID and Thread ID.

* [JS/TS SDK Reference](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html)

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/use-stream-react.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
## Example
```

Example 2 (unknown):
```unknown
## Customizing Your UI

The [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) hook takes care of all the complex state management behind the scenes, providing you with simple interfaces to build your UI. Here's what you get out of the box:

* Thread state management
* Loading and error states
* Interrupts
* Message handling and updates
* Branching support

Here are some examples on how to use these features effectively:

### Loading States

The `isLoading` property tells you when a stream is active, enabling you to:

* Show a loading indicator
* Disable input fields during processing
* Display a cancel button
```

Example 3 (unknown):
```unknown
### Resume a stream after page refresh

The [`useStream()`](https://langchain-ai.github.io/langgraphjs/reference/modules/sdk.html) hook can automatically resume an ongoing run upon mounting by setting `reconnectOnMount: true`. This is useful for continuing a stream after a page refresh, ensuring no messages and events generated during the downtime are lost.
```

Example 4 (unknown):
```unknown
By default the ID of the created run is stored in `window.sessionStorage`, which can be swapped by passing a custom storage in `reconnectOnMount` instead. The storage is used to persist the in-flight run ID for a thread (under `lg:stream:${threadId}` key).
```

---

## [{'expensive_node': {'result': 10}, '__metadata__': {'cached': True}}]

**URL:** llms-txt#[{'expensive_node':-{'result':-10},-'__metadata__':-{'cached':-true}}]

**Contents:**
- Edges
  - Normal Edges
  - Conditional Edges
  - Entry point
  - Conditional entry point
- `Send`
- `Command`
  - When should I use Command instead of conditional edges?
  - Navigating to a node in a parent graph
  - Using inside tools

python  theme={null}
graph.add_edge("node_a", "node_b")
python  theme={null}
graph.add_conditional_edges("node_a", routing_function)
python  theme={null}
graph.add_conditional_edges("node_a", routing_function, {True: "node_b", False: "node_c"})
python  theme={null}
from langgraph.graph import START

graph.add_edge(START, "node_a")
python  theme={null}
from langgraph.graph import START

graph.add_conditional_edges(START, routing_function)
python  theme={null}
graph.add_conditional_edges(START, routing_function, {True: "node_b", False: "node_c"})
python  theme={null}
def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state['subjects']]

graph.add_conditional_edges("node_a", continue_to_jokes)
python  theme={null}
def my_node(state: State) -> Command[Literal["my_other_node"]]:
    return Command(
        # state update
        update={"foo": "bar"},
        # control flow
        goto="my_other_node"
    )
python  theme={null}
def my_node(state: State) -> Command[Literal["my_other_node"]]:
    if state["foo"] == "bar":
        return Command(update={"foo": "baz"}, goto="my_other_node")
python  theme={null}
def my_node(state: State) -> Command[Literal["other_subgraph"]]:
    return Command(
        update={"foo": "bar"},
        goto="other_subgraph",  # where `other_subgraph` is a node in the parent graph
        graph=Command.PARENT
    )
python  theme={null}
@dataclass
class ContextSchema:
    llm_provider: str = "openai"

graph = StateGraph(State, context_schema=ContextSchema)
python  theme={null}
graph.invoke(inputs, context={"llm_provider": "anthropic"})
python  theme={null}
from langgraph.runtime import Runtime

def node_a(state: State, runtime: Runtime[ContextSchema]):
    llm = get_llm(runtime.context.llm_provider)
    # ...
python  theme={null}
graph.invoke(inputs, config={"recursion_limit": 5}, context={"llm": "anthropic"})
python  theme={null}
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

def my_node(state: dict, config: RunnableConfig) -> dict:
    current_step = config["metadata"]["langgraph_step"]
    print(f"Currently on step: {current_step}")
    return state
python  theme={null}
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END

def reasoning_node(state: dict, config: RunnableConfig) -> dict:
    current_step = config["metadata"]["langgraph_step"]
    recursion_limit = config["recursion_limit"]  # always present, defaults to 25

# Check if we're approaching the limit (e.g., 80% threshold)
    if current_step >= recursion_limit * 0.8:
        return {
            **state,
            "route_to": "fallback",
            "reason": "Approaching recursion limit"
        }

# Normal processing
    return {"messages": state["messages"] + ["thinking..."]}

def fallback_node(state: dict, config: RunnableConfig) -> dict:
    """Handle cases where recursion limit is approaching"""
    return {
        **state,
        "messages": state["messages"] + ["Reached complexity limit, providing best effort answer"]
    }

def route_based_on_state(state: dict) -> str:
    if state.get("route_to") == "fallback":
        return "fallback"
    elif state.get("done"):
        return END
    return "reasoning"

**Examples:**

Example 1 (unknown):
```unknown
1. First run takes two seconds to run (due to mocked expensive computation).
2. Second run utilizes cache and returns quickly.

## Edges

Edges define how the logic is routed and how the graph decides to stop. This is a big part of how your agents work and how different nodes communicate with each other. There are a few key types of edges:

* Normal Edges: Go directly from one node to the next.
* Conditional Edges: Call a function to determine which node(s) to go to next.
* Entry Point: Which node to call first when user input arrives.
* Conditional Entry Point: Call a function to determine which node(s) to call first when user input arrives.

A node can have multiple outgoing edges. If a node has multiple outgoing edges, **all** of those destination nodes will be executed in parallel as a part of the next superstep.

### Normal Edges

If you **always** want to go from node A to node B, you can use the [`add_edge`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph.add_edge) method directly.
```

Example 2 (unknown):
```unknown
### Conditional Edges

If you want to **optionally** route to one or more edges (or optionally terminate), you can use the [`add_conditional_edges`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph.add_conditional_edges) method. This method accepts the name of a node and a "routing function" to call after that node is executed:
```

Example 3 (unknown):
```unknown
Similar to nodes, the `routing_function` accepts the current `state` of the graph and returns a value.

By default, the return value `routing_function` is used as the name of the node (or list of nodes) to send the state to next. All those nodes will be run in parallel as a part of the next superstep.

You can optionally provide a dictionary that maps the `routing_function`'s output to the name of the next node.
```

Example 4 (unknown):
```unknown
<Tip>
  Use [`Command`](#command) instead of conditional edges if you want to combine state updates and routing in a single function.
</Tip>

### Entry point

The entry point is the first node(s) that are run when the graph starts. You can use the [`add_edge`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph.add_edge) method from the virtual [`START`](https://reference.langchain.com/python/langgraph/constants/#langgraph.constants.START) node to the first node to execute to specify where to enter the graph.
```

---

## Define the processing node

**URL:** llms-txt#define-the-processing-node

def answer_node(state: InputState):
    # Replace with actual logic and do something useful
    return {"answer": "bye", "question": state["question"]}

---

## Augment the LLM with tools

**URL:** llms-txt#augment-the-llm-with-tools

tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
llm_with_tools = llm.bind_tools(tools)
python Graph API theme={null}
  from langgraph.graph import MessagesState
  from langchain.messages import SystemMessage, HumanMessage, ToolMessage

# Nodes
  def llm_call(state: MessagesState):
      """LLM decides whether to call a tool or not"""

return {
          "messages": [
              llm_with_tools.invoke(
                  [
                      SystemMessage(
                          content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                      )
                  ]
                  + state["messages"]
              )
          ]
      }

def tool_node(state: dict):
      """Performs the tool call"""

result = []
      for tool_call in state["messages"][-1].tool_calls:
          tool = tools_by_name[tool_call["name"]]
          observation = tool.invoke(tool_call["args"])
          result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
      return {"messages": result}

# Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
  def should_continue(state: MessagesState) -> Literal["tool_node", END]:
      """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

messages = state["messages"]
      last_message = messages[-1]

# If the LLM makes a tool call, then perform an action
      if last_message.tool_calls:
          return "tool_node"

# Otherwise, we stop (reply to the user)
      return END

# Build workflow
  agent_builder = StateGraph(MessagesState)

# Add nodes
  agent_builder.add_node("llm_call", llm_call)
  agent_builder.add_node("tool_node", tool_node)

# Add edges to connect nodes
  agent_builder.add_edge(START, "llm_call")
  agent_builder.add_conditional_edges(
      "llm_call",
      should_continue,
      ["tool_node", END]
  )
  agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
  agent = agent_builder.compile()

# Show the agent
  display(Image(agent.get_graph(xray=True).draw_mermaid_png()))

# Invoke
  messages = [HumanMessage(content="Add 3 and 4.")]
  messages = agent.invoke({"messages": messages})
  for m in messages["messages"]:
      m.pretty_print()
  python Functional API theme={null}
  from langgraph.graph import add_messages
  from langchain.messages import (
      SystemMessage,
      HumanMessage,
      BaseMessage,
      ToolCall,
  )

@task
  def call_llm(messages: list[BaseMessage]):
      """LLM decides whether to call a tool or not"""
      return llm_with_tools.invoke(
          [
              SystemMessage(
                  content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
              )
          ]
          + messages
      )

@task
  def call_tool(tool_call: ToolCall):
      """Performs the tool call"""
      tool = tools_by_name[tool_call["name"]]
      return tool.invoke(tool_call)

@entrypoint()
  def agent(messages: list[BaseMessage]):
      llm_response = call_llm(messages).result()

while True:
          if not llm_response.tool_calls:
              break

# Execute tools
          tool_result_futures = [
              call_tool(tool_call) for tool_call in llm_response.tool_calls
          ]
          tool_results = [fut.result() for fut in tool_result_futures]
          messages = add_messages(messages, [llm_response, *tool_results])
          llm_response = call_llm(messages).result()

messages = add_messages(messages, llm_response)
      return messages

# Invoke
  messages = [HumanMessage(content="Add 3 and 4.")]
  for chunk in agent.stream(messages, stream_mode="updates"):
      print(chunk)
      print("\n")
  ```
</CodeGroup>

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/langgraph/workflows-agents.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
<CodeGroup>
```

Example 2 (unknown):
```unknown

```

---

## Connect nodes in a sequence

**URL:** llms-txt#connect-nodes-in-a-sequence

---

## we can add them as nodes directly.

**URL:** llms-txt#we-can-add-them-as-nodes-directly.

**Contents:**
- Evaluations
  - Final response evaluator

graph_builder.add_node("refund_agent", refund_graph)
graph_builder.add_node("question_answering_agent", qa_graph)
graph_builder.add_node(compile_followup)

graph_builder.set_entry_point("intent_classifier")
graph_builder.add_edge("refund_agent", "compile_followup")
graph_builder.add_edge("question_answering_agent", "compile_followup")
graph_builder.add_edge("compile_followup", END)

graph = graph_builder.compile()
python  theme={null}
display(Image(graph.get_graph().draw_mermaid_png()))
python  theme={null}
state = await graph.ainvoke(
    {"messages": [{"role": "user", "content": "what james brown songs do you have"}]}
)
print(state["followup"])

I found 20 James Brown songs in the database, all from the album "Sex Machine". Here they are: ...
python  theme={null}
state = await graph.ainvoke({"messages": [
    {
        "role": "user",
        "content": "my name is Aaron Mitchell and my number is +1 (204) 452-6452. I bought some songs by Led Zeppelin that i'd like refunded",
    }
]})
print(state["followup"])

Which of the following purchases would you like to be refunded for? ...
python  theme={null}
from langsmith import Client

**Examples:**

Example 1 (unknown):
```unknown
We can visualize our compiled parent graph including all of its subgraphs:
```

Example 2 (unknown):
```unknown
<img src="https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/agent-tutorial-graph.png?fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=619f9b540ea69b1662b2a599ce78241b" alt="graph" data-og-width="646" width="646" data-og-height="680" height="680" data-path="langsmith/images/agent-tutorial-graph.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/agent-tutorial-graph.png?w=280&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=227790d90780a4c56233650b957130df 280w, https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/agent-tutorial-graph.png?w=560&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=30ae6a9b1bc367152a57d4a0c3e41af7 560w, https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/agent-tutorial-graph.png?w=840&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=37f29b6e783cf2a80714c29ab0be3c5f 840w, https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/agent-tutorial-graph.png?w=1100&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=423ad48e0266ac257b6d76962697b45d 1100w, https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/agent-tutorial-graph.png?w=1650&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=581821d6b377b98108507712d6b08c51 1650w, https://mintcdn.com/langchain-5e9cc07a/E8FdemkcQxROovD9/langsmith/images/agent-tutorial-graph.png?w=2500&fit=max&auto=format&n=E8FdemkcQxROovD9&q=85&s=126ef194ff5042f691c8f52cf3a1cb75 2500w" />

#### Try it out

Let's give our custom support agent a whirl!
```

Example 3 (unknown):
```unknown

```

Example 4 (unknown):
```unknown

```

---

## this is the graph making function that will decide which graph to

**URL:** llms-txt#this-is-the-graph-making-function-that-will-decide-which-graph-to

---

## LangGraph CLI

**URL:** llms-txt#langgraph-cli

**Contents:**
- Installation
  - Quick commands
- Configuration file
  - Examples
- Commands
  - `dev`
  - `build`
  - `up`
  - `dockerfile`

Source: https://docs.langchain.com/langsmith/cli

**LangGraph CLI** is a command-line tool for building and running the [Agent Server](/langsmith/agent-server) locally. The resulting server exposes all API endpoints for runs, threads, assistants, etc., and includes supporting services such as a managed database for checkpointing and storage.

1. Ensure Docker is installed (e.g., `docker --version`).

3. Verify the install

| Command                               | What it does                                                                                                                         |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| [`langgraph dev`](#dev)               | Starts a lightweight local dev server (no Docker required), ideal for rapid testing.                                                 |
| [`langgraph build`](#build)           | Builds a Docker image of your LangGraph API server for deployment.                                                                   |
| [`langgraph dockerfile`](#dockerfile) | Emits a Dockerfile derived from your config for custom builds.                                                                       |
| [`langgraph up`](#up)                 | Starts the LangGraph API server locally in Docker. Requires Docker running; LangSmith API key for local dev; license for production. |

For JS, use `npx @langchain/langgraph-cli <command>` (or `langgraphjs` if installed globally).

## Configuration file

To build and run a valid application, the LangGraph CLI requires a JSON configuration file that follows this [schema](https://raw.githubusercontent.com/langchain-ai/langgraph/refs/heads/main/libs/cli/schemas/schema.json). It contains the following properties:

<Note>The LangGraph CLI defaults to using the configuration file named <strong>langgraph.json</strong> in the current directory.</Note>

<Tabs>
  <Tab title="Python">
    | Key                                                              | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
    | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | <span style={{ whiteSpace: "nowrap" }}>`dependencies`</span>     | **Required**. Array of dependencies for LangSmith API server. Dependencies can be one of the following: <ul><li>A single period (`"."`), which will look for local Python packages.</li><li>The directory path where `pyproject.toml`, `setup.py` or `requirements.txt` is located.<br />For example, if `requirements.txt` is located in the root of the project directory, specify `"./"`. If it's located in a subdirectory called `local_package`, specify `"./local_package"`. Do not specify the string `"requirements.txt"` itself.</li><li>A Python package name.</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | <span style={{ whiteSpace: "nowrap" }}>`graphs`</span>           | **Required**. Mapping from graph ID to path where the compiled graph or a function that makes a graph is defined. Example: <ul><li>`./your_package/your_file.py:variable`, where `variable` is an instance of `langgraph.graph.state.CompiledStateGraph`</li><li>`./your_package/your_file.py:make_graph`, where `make_graph` is a function that takes a config dictionary (`langchain_core.runnables.RunnableConfig`) and returns an instance of `langgraph.graph.state.StateGraph` or `langgraph.graph.state.CompiledStateGraph`. See [how to rebuild a graph at runtime](/langsmith/graph-rebuild) for more details.</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | <span style={{ whiteSpace: "nowrap" }}>`auth`</span>             | *(Added in v0.0.11)* Auth configuration containing the path to your authentication handler. Example: `./your_package/auth.py:auth`, where `auth` is an instance of `langgraph_sdk.Auth`. See [authentication guide](/langsmith/auth) for details.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | <span style={{ whiteSpace: "nowrap" }}>`base_image`</span>       | Optional. Base image to use for the LangGraph API server. Defaults to `langchain/langgraph-api` or `langchain/langgraphjs-api`. Use this to pin your builds to a particular version of the langgraph API, such as `"langchain/langgraph-server:0.2"`. See [https://hub.docker.com/r/langchain/langgraph-server/tags](https://hub.docker.com/r/langchain/langgraph-server/tags) for more details. (added in `langgraph-cli==0.2.8`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | <span style={{ whiteSpace: "nowrap" }}>`image_distro`</span>     | Optional. Linux distribution for the base image. Must be one of `"debian"`, `"wolfi"`, `"bookworm"`, or `"bullseye"`. If omitted, defaults to `"debian"`. Available in `langgraph-cli>=0.2.11`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | <span style={{ whiteSpace: "nowrap" }}>`env`</span>              | Path to `.env` file or a mapping from environment variable to its value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
    | <span style={{ whiteSpace: "nowrap" }}>`store`</span>            | Configuration for adding semantic search and/or time-to-live (TTL) to the BaseStore. Contains the following fields: <ul><li>`index` (optional): Configuration for semantic search indexing with fields `embed`, `dims`, and optional `fields`.</li><li>`ttl` (optional): Configuration for item expiration. An object with optional fields: `refresh_on_read` (boolean, defaults to `true`), `default_ttl` (float, lifespan in **minutes**; applied to newly created items only; existing items are unchanged; defaults to no expiration), and `sweep_interval_minutes` (integer, how often to check for expired items, defaults to no sweeping).</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
    | <span style={{ whiteSpace: "nowrap" }}>`ui`</span>               | Optional. Named definitions of UI components emitted by the agent, each pointing to a JS/TS file. (added in `langgraph-cli==0.1.84`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
    | <span style={{ whiteSpace: "nowrap" }}>`python_version`</span>   | `3.11`, `3.12`, or `3.13`. Defaults to `3.11`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
    | <span style={{ whiteSpace: "nowrap" }}>`node_version`</span>     | Specify `node_version: 20` to use LangGraph.js.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | <span style={{ whiteSpace: "nowrap" }}>`pip_config_file`</span>  | Path to `pip` config file.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
    | <span style={{ whiteSpace: "nowrap" }}>`pip_installer`</span>    | *(Added in v0.3)* Optional. Python package installer selector. It can be set to `"auto"`, `"pip"`, or `"uv"`. From version 0.3 onward the default strategy is to run `uv pip`, which typically delivers faster builds while remaining a drop-in replacement. In the uncommon situation where `uv` cannot handle your dependency graph or the structure of your `pyproject.toml`, specify `"pip"` here to revert to the earlier behaviour.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
    | <span style={{ whiteSpace: "nowrap" }}>`keep_pkg_tools`</span>   | *(Added in v0.3.4)* Optional. Control whether to retain Python packaging tools (`pip`, `setuptools`, `wheel`) in the final image. Accepted values: <ul><li><code>true</code> : Keep all three tools (skip uninstall).</li><li><code>false</code> / omitted : Uninstall all three tools (default behaviour).</li><li><code>list\[str]</code> : Names of tools <strong>to retain</strong>. Each value must be one of "pip", "setuptools", "wheel".</li></ul>. By default, all three tools are uninstalled.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
    | <span style={{ whiteSpace: "nowrap" }}>`dockerfile_lines`</span> | Array of additional lines to add to Dockerfile following the import from parent image.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
    | <span style={{ whiteSpace: "nowrap" }}>`checkpointer`</span>     | Configuration for the checkpointer. Supports: <ul><li>`ttl` (optional): Object with `strategy`, `sweep_interval_minutes`, `default_ttl` controlling checkpoint expiry.</li><li>`serde` (optional, 0.5+): Object with `allowed_json_modules` and `pickle_fallback` to tune deserialization behavior.</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
    | <span style={{ whiteSpace: "nowrap" }}>`http`</span>             | HTTP server configuration with the following fields: <ul><li>`app`: Path to custom Starlette/FastAPI app (e.g., `"./src/agent/webapp.py:app"`). See [custom routes guide](/langsmith/custom-routes).</li><li>`cors`: CORS configuration with fields such as `allow_origins`, `allow_methods`, `allow_headers`, `allow_credentials`, `allow_origin_regex`, `expose_headers`, and `max_age`.</li><li>`configurable_headers`: Define which request headers to expose as configurable values via `includes` / `excludes` patterns.</li><li>`logging_headers`: Mirror of `configurable_headers` for excluding sensitive headers from logs.</li><li>`middleware_order`: Choose how custom middleware and auth interact. `auth_first` runs authentication hooks before custom middleware, while `middleware_first` (default) runs your middleware first.</li><li>`enable_custom_route_auth`: Apply auth checks to routes added through `app`.</li><li>`disable_assistants`, `disable_mcp`, `disable_meta`, `disable_runs`, `disable_store`, `disable_threads`, `disable_ui`, `disable_webhooks`: Disable built-in routes or hooks.</li><li>`mount_prefix`: Prefix for mounted routes (e.g., "/my-deployment/api").</li></ul> |
    | <span style={{ whiteSpace: "nowrap" }}>`api_version`</span>      | *(Added in v0.3.7)* Which semantic version of the LangGraph API server to use (e.g., `"0.3"`). Defaults to latest. Check the server [changelog](/langsmith/agent-server-changelog) for details on each release.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
  </Tab>

<Tab title="JS">
    | Key                                                              | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
    | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | <span style={{ whiteSpace: "nowrap" }}>`graphs`</span>           | **Required**. Mapping from graph ID to path where the compiled graph or a function that makes a graph is defined. Example: <ul><li>`./src/graph.ts:variable`, where `variable` is an instance of [`CompiledStateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph)</li><li>`./src/graph.ts:makeGraph`, where `makeGraph` is a function that takes a config dictionary (`LangGraphRunnableConfig`) and returns an instance of [`StateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph) or [`CompiledStateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph). See [how to rebuild a graph at runtime](/langsmith/graph-rebuild) for more details.</li></ul> |
    | <span style={{ whiteSpace: "nowrap" }}>`env`</span>              | Path to `.env` file or a mapping from environment variable to its value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | <span style={{ whiteSpace: "nowrap" }}>`store`</span>            | Configuration for adding semantic search and/or time-to-live (TTL) to the BaseStore. Contains the following fields: <ul><li>`index` (optional): Configuration for semantic search indexing with fields `embed`, `dims`, and optional `fields`.</li><li>`ttl` (optional): Configuration for item expiration. An object with optional fields: `refresh_on_read` (boolean, defaults to `true`), `default_ttl` (float, lifespan in **minutes**; applied to newly created items only; existing items are unchanged; defaults to no expiration), and `sweep_interval_minutes` (integer, how often to check for expired items, defaults to no sweeping).</li></ul>                                                                                                                                                                |
    | <span style={{ whiteSpace: "nowrap" }}>`node_version`</span>     | Specify `node_version: 20` to use LangGraph.js.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
    | <span style={{ whiteSpace: "nowrap" }}>`dockerfile_lines`</span> | Array of additional lines to add to Dockerfile following the import from parent image.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | <span style={{ whiteSpace: "nowrap" }}>`checkpointer`</span>     | Configuration for the checkpointer. Supports: <ul><li>`ttl` (optional): Object with `strategy`, `sweep_interval_minutes`, `default_ttl` controlling checkpoint expiry.</li><li>`serde` (optional, 0.5+): Object with `allowed_json_modules` and `pickle_fallback` to tune deserialization behavior.</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
    | <span style={{ whiteSpace: "nowrap" }}>`http`</span>             | HTTP server configuration mirroring the Python options: <ul><li>`cors` with `allow_origins`, `allow_methods`, `allow_headers`, `allow_credentials`, `allow_origin_regex`, `expose_headers`, `max_age`.</li><li>`configurable_headers` and `logging_headers` pattern lists.</li><li>`middleware_order` (`auth_first` or `middleware_first`).</li><li>`enable_custom_route_auth` plus the same boolean route toggles as above.</li></ul>                                                                                                                                                                                                                                                                                                                                                                                     |
    | <span style={{ whiteSpace: "nowrap" }}>`api_version`</span>      | *(Added in v0.3.7)* Which semantic version of the LangGraph API server to use (e.g., `"0.3"`). Defaults to latest. Check the server [changelog](/langsmith/agent-server-changelog) for details on each release.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
  </Tab>
</Tabs>

<Tabs>
  <Tab title="Python">
    #### Basic configuration

#### Using Wolfi base images

You can specify the Linux distribution for your base image using the `image_distro` field. Valid options are `debian`, `wolfi`, `bookworm`, or `bullseye`. Wolfi is the recommended option as it provides smaller and more secure images. This is available in `langgraph-cli>=0.2.11`.

#### Adding semantic search to the store

All deployments come with a DB-backed BaseStore. Adding an "index" configuration to your `langgraph.json` will enable [semantic search](/langsmith/semantic-search) within the BaseStore of your deployment.

The `index.fields` configuration determines which parts of your documents to embed:

* If omitted or set to `["$"]`, the entire document will be embedded
    * To embed specific fields, use JSON path notation: `["metadata.title", "content.text"]`
    * Documents missing specified fields will still be stored but won't have embeddings for those fields
    * You can still override which fields to embed on a specific item at `put` time using the `index` parameter

<Note>
      **Common model dimensions**

* `openai:text-embedding-3-large`: 3072
      * `openai:text-embedding-3-small`: 1536
      * `openai:text-embedding-ada-002`: 1536
      * `cohere:embed-english-v3.0`: 1024
      * `cohere:embed-english-light-v3.0`: 384
      * `cohere:embed-multilingual-v3.0`: 1024
      * `cohere:embed-multilingual-light-v3.0`: 384
    </Note>

#### Semantic search with a custom embedding function

If you want to use semantic search with a custom embedding function, you can pass a path to a custom embedding function:

The `embed` field in store configuration can reference a custom function that takes a list of strings and returns a list of embeddings. Example implementation:

#### Adding custom authentication

See the [authentication conceptual guide](/langsmith/auth) for details, and the [setting up custom authentication](/langsmith/set-up-custom-auth) guide for a practical walk through of the process.

#### Configuring store item Time-to-Live

You can configure default data expiration for items/memories in the BaseStore using the `store.ttl` key. This determines how long items are retained after they are last accessed (with reads potentially refreshing the timer based on `refresh_on_read`). Note that these defaults can be overwritten on a per-call basis by modifying the corresponding arguments in `get`, `search`, etc.

The `ttl` configuration is an object containing optional fields:

* `refresh_on_read`: If `true` (the default), accessing an item via `get` or `search` resets its expiration timer. Set to `false` to only refresh TTL on writes (`put`).
    * `default_ttl`: The default lifespan of an item in **minutes**. Applies only to newly created items; existing items are not modified. If not set, items do not expire by default.
    * `sweep_interval_minutes`: How frequently (in minutes) the system should run a background process to delete expired items. If not set, sweeping does not occur automatically.

Here is an example enabling a 7-day TTL (10080 minutes), refreshing on reads, and sweeping every hour:

#### Configuring checkpoint Time-to-Live

You can configure the time-to-live (TTL) for checkpoints using the `checkpointer` key. This determines how long checkpoint data is retained before being automatically handled according to the specified strategy (e.g., deletion). Two optional sub-objects are supported:

* `ttl`: Includes `strategy`, `sweep_interval_minutes`, and `default_ttl`, which collectively set how checkpoints expire.
    * `serde` *(Agent server 0.5+)* : Lets you control deserialization behavior for checkpoint payloads.

Here's an example setting a default TTL of 30 days (43200 minutes):

In this example, checkpoints older than 30 days will be deleted, and the check runs every 10 minutes.

#### Configuring checkpointer serde

The `checkpointer.serde` object shapes deserialization:

* `allowed_json_modules` defines an allow list for custom Python objects you want the server to be able to deserialize from payloads saved in "json" mode. This is a list of `[path, to, module, file, symbol]` sequences. If omitted, only LangChain-safe defaults are allowed. You can unsafely set to `true` to allow any module to be deserialized.
    * `pickle_fallback`: Whether to fall back to pickle deserialization when JSON decoding fails.

#### Customizing HTTP middleware and headers

The `http` block lets you fine-tune request handling:

* `middleware_order`: Choose `"auth_first"` to run authentication before your middleware, or `"middleware_first"` (default) to invert that order.
    * `enable_custom_route_auth`: Extend authentication to routes you mount through `http.app`.
    * `configurable_headers` / `logging_headers`: Each accepts an object with optional `includes` and `excludes` arrays; wildcards are supported and exclusions run before inclusions.
    * `cors`: In addition to `allow_origins`, `allow_methods`, and `allow_headers`, you can set `allow_credentials`, `allow_origin_regex`, `expose_headers`, and `max_age` for detailed browser control.

<a id="api-version" />

#### Pinning API version

You can pin the API version of the Agent Server by using the `api_version` key. This is useful if you want to ensure that your server uses a specific version of the API.
    By default, builds in Cloud deployments use the latest stable version of the server. This can be pinned by setting the `api_version` key to a specific version.

<Tab title="JS">
    #### Basic configuration

<a id="api-version" />

#### Pinning API version

You can pin the API version of the Agent Server by using the `api_version` key. This is useful if you want to ensure that your server uses a specific version of the API.
    By default, builds in Cloud deployments use the latest stable version of the server. This can be pinned by setting the `api_version` key to a specific version.

<Tabs>
  <Tab title="Python">
    The base command for the LangGraph CLI is `langgraph`.

<Tab title="JS">
    The base command for the LangGraph.js CLI is `langgraphjs`.

We recommend using `npx` to always use the latest version of the CLI.
  </Tab>
</Tabs>

<Tabs>
  <Tab title="Python">
    Run LangGraph API server in development mode with hot reloading and debugging capabilities. This lightweight server requires no Docker installation and is suitable for development and testing. State is persisted to a local directory.

<Note>Currently, the CLI only supports Python >= 3.11.</Note>

This command requires the "inmem" extra to be installed:

| Option                        | Default          | Description                                                                                                                                                                  |
    | ----------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `-c, --config FILE`           | `langgraph.json` | Path to configuration file declaring dependencies, graphs and environment variables                                                                                          |
    | `--host TEXT`                 | `127.0.0.1`      | Host to bind the server to                                                                                                                                                   |
    | `--port INTEGER`              | `2024`           | Port to bind the server to                                                                                                                                                   |
    | `--no-reload`                 |                  | Disable auto-reload                                                                                                                                                          |
    | `--n-jobs-per-worker INTEGER` |                  | Number of jobs per worker. Default is 10                                                                                                                                     |
    | `--debug-port INTEGER`        |                  | Port for debugger to listen on                                                                                                                                               |
    | `--wait-for-client`           | `False`          | Wait for a debugger client to connect to the debug port before starting the server                                                                                           |
    | `--no-browser`                |                  | Skip automatically opening the browser when the server starts                                                                                                                |
    | `--studio-url TEXT`           |                  | URL of the Studio instance to connect to. Defaults to [https://smith.langchain.com](https://smith.langchain.com)                                                             |
    | `--allow-blocking`            | `False`          | Do not raise errors for synchronous I/O blocking operations in your code (added in `0.2.6`)                                                                                  |
    | `--tunnel`                    | `False`          | Expose the local server via a public tunnel (Cloudflare) for remote frontend access. This avoids issues with browsers like Safari or networks blocking localhost connections |
    | `--help`                      |                  | Display command documentation                                                                                                                                                |
  </Tab>

<Tab title="JS">
    Run LangGraph API server in development mode with hot reloading capabilities. This lightweight server requires no Docker installation and is suitable for development and testing. State is persisted to a local directory.

| Option                        | Default          | Description                                                                                                                                                      |
    | ----------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `-c, --config FILE`           | `langgraph.json` | Path to configuration file declaring dependencies, graphs and environment variables                                                                              |
    | `--host TEXT`                 | `127.0.0.1`      | Host to bind the server to                                                                                                                                       |
    | `--port INTEGER`              | `2024`           | Port to bind the server to                                                                                                                                       |
    | `--no-reload`                 |                  | Disable auto-reload                                                                                                                                              |
    | `--n-jobs-per-worker INTEGER` |                  | Number of jobs per worker. Default is 10                                                                                                                         |
    | `--debug-port INTEGER`        |                  | Port for debugger to listen on                                                                                                                                   |
    | `--wait-for-client`           | `False`          | Wait for a debugger client to connect to the debug port before starting the server                                                                               |
    | `--no-browser`                |                  | Skip automatically opening the browser when the server starts                                                                                                    |
    | `--studio-url TEXT`           |                  | URL of the Studio instance to connect to. Defaults to [https://smith.langchain.com](https://smith.langchain.com)                                                 |
    | `--allow-blocking`            | `False`          | Do not raise errors for synchronous I/O blocking operations in your code                                                                                         |
    | `--tunnel`                    | `False`          | Expose the local server via a public tunnel (Cloudflare) for remote frontend access. This avoids issues with browsers or networks blocking localhost connections |
    | `--help`                      |                  | Display command documentation                                                                                                                                    |
  </Tab>
</Tabs>

<Tabs>
  <Tab title="Python">
    Build LangSmith API server Docker image.

| Option                                | Default          | Description                                                                                                                                             |
    | ------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `--platform TEXT`                     |                  | Target platform(s) to build the Docker image for. Example: `langgraph build --platform linux/amd64,linux/arm64`                                         |
    | `-t, --tag TEXT`                      |                  | **Required**. Tag for the Docker image. Example: `langgraph build -t my-image`                                                                          |
    | `--pull / --no-pull`                  | `--pull`         | Build with latest remote Docker image. Use `--no-pull` for running the LangSmith API server with locally built images.                                  |
    | `-c, --config FILE`                   | `langgraph.json` | Path to configuration file declaring dependencies, graphs and environment variables.                                                                    |
    | `--build-command TEXT`<sup>\*</sup>   |                  | Build command to run. Runs from the directory where your `langgraph.json` file lives. Example: `langgraph build --build-command "yarn run turbo build"` |
    | `--install-command TEXT`<sup>\*</sup> |                  | Install command to run. Runs from the directory where you call `langgraph build` from. Example: `langgraph build --install-command "yarn install"`      |
    | `--help`                              |                  | Display command documentation.                                                                                                                          |

<sup>\*</sup>Only supported for JS deployments, will have no impact on Python deployments.
  </Tab>

<Tab title="JS">
    Build LangSmith API server Docker image.

| Option              | Default          | Description                                                                                                     |
    | ------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------- |
    | `--platform TEXT`   |                  | Target platform(s) to build the Docker image for. Example: `langgraph build --platform linux/amd64,linux/arm64` |
    | `-t, --tag TEXT`    |                  | **Required**. Tag for the Docker image. Example: `langgraph build -t my-image`                                  |
    | `--no-pull`         |                  | Use locally built images. Defaults to `false` to build with latest remote Docker image.                         |
    | `-c, --config FILE` | `langgraph.json` | Path to configuration file declaring dependencies, graphs and environment variables.                            |
    | `--help`            |                  | Display command documentation.                                                                                  |
  </Tab>
</Tabs>

<Tabs>
  <Tab title="Python">
    Start LangGraph API server. For local testing, requires a LangSmith API key with access to LangSmith. Requires a license key for production use.

| Option                       | Default                   | Description                                                                                                             |
    | ---------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
    | `--wait`                     |                           | Wait for services to start before returning. Implies --detach                                                           |
    | `--base-image TEXT`          | `langchain/langgraph-api` | Base image to use for the LangGraph API server. Pin to specific versions using version tags.                            |
    | `--image TEXT`               |                           | Docker image to use for the langgraph-api service. If specified, skips building and uses this image directly.           |
    | `--postgres-uri TEXT`        | Local database            | Postgres URI to use for the database.                                                                                   |
    | `--watch`                    |                           | Restart on file changes                                                                                                 |
    | `--debugger-base-url TEXT`   | `http://127.0.0.1:[PORT]` | URL used by the debugger to access LangGraph API.                                                                       |
    | `--debugger-port INTEGER`    |                           | Pull the debugger image locally and serve the UI on specified port                                                      |
    | `--verbose`                  |                           | Show more output from the server logs.                                                                                  |
    | `-c, --config FILE`          | `langgraph.json`          | Path to configuration file declaring dependencies, graphs and environment variables.                                    |
    | `-d, --docker-compose FILE`  |                           | Path to docker-compose.yml file with additional services to launch.                                                     |
    | `-p, --port INTEGER`         | `8123`                    | Port to expose. Example: `langgraph up --port 8000`                                                                     |
    | `--pull / --no-pull`         | `pull`                    | Pull latest images. Use `--no-pull` for running the server with locally-built images. Example: `langgraph up --no-pull` |
    | `--recreate / --no-recreate` | `no-recreate`             | Recreate containers even if their configuration and image haven't changed                                               |
    | `--help`                     |                           | Display command documentation.                                                                                          |
  </Tab>

<Tab title="JS">
    Start LangGraph API server. For local testing, requires a LangSmith API key with access to LangSmith. Requires a license key for production use.

| Option                                                                    | Default                                                                 | Description                                                                                                   |
    | ------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
    | <span style={{ whiteSpace: "nowrap" }}>`--wait`</span>                    |                                                                         | Wait for services to start before returning. Implies --detach                                                 |
    | <span style={{ whiteSpace: "nowrap" }}>`--base-image TEXT`</span>         | <span style={{ whiteSpace: "nowrap" }}>`langchain/langgraph-api`</span> | Base image to use for the LangGraph API server. Pin to specific versions using version tags.                  |
    | <span style={{ whiteSpace: "nowrap" }}>`--image TEXT`</span>              |                                                                         | Docker image to use for the langgraph-api service. If specified, skips building and uses this image directly. |
    | <span style={{ whiteSpace: "nowrap" }}>`--postgres-uri TEXT`</span>       | Local database                                                          | Postgres URI to use for the database.                                                                         |
    | <span style={{ whiteSpace: "nowrap" }}>`--watch`</span>                   |                                                                         | Restart on file changes                                                                                       |
    | <span style={{ whiteSpace: "nowrap" }}>`-c, --config FILE`</span>         | `langgraph.json`                                                        | Path to configuration file declaring dependencies, graphs and environment variables.                          |
    | <span style={{ whiteSpace: "nowrap" }}>`-d, --docker-compose FILE`</span> |                                                                         | Path to docker-compose.yml file with additional services to launch.                                           |
    | <span style={{ whiteSpace: "nowrap" }}>`-p, --port INTEGER`</span>        | `8123`                                                                  | Port to expose. Example: `langgraph up --port 8000`                                                           |
    | <span style={{ whiteSpace: "nowrap" }}>`--no-pull`</span>                 |                                                                         | Use locally built images. Defaults to `false` to build with latest remote Docker image.                       |
    | <span style={{ whiteSpace: "nowrap" }}>`--recreate`</span>                |                                                                         | Recreate containers even if their configuration and image haven't changed                                     |
    | <span style={{ whiteSpace: "nowrap" }}>`--help`</span>                    |                                                                         | Display command documentation.                                                                                |
  </Tab>
</Tabs>

<Tabs>
  <Tab title="Python">
    Generate a Dockerfile for building a LangSmith API server Docker image.

| Option              | Default          | Description                                                                                                     |
    | ------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------- |
    | `-c, --config FILE` | `langgraph.json` | Path to the [configuration file](#configuration-file) declaring dependencies, graphs and environment variables. |
    | `--help`            |                  | Show this message and exit.                                                                                     |

This generates a Dockerfile that looks similar to:

<Note>The `langgraph dockerfile` command translates all the configuration in your `langgraph.json` file into Dockerfile commands. When using this command, you will have to re-run it whenever you update your `langgraph.json` file. Otherwise, your changes will not be reflected when you build or run the dockerfile.</Note>
  </Tab>

<Tab title="JS">
    Generate a Dockerfile for building a LangSmith API server Docker image.

| Option              | Default          | Description                                                                                                     |
    | ------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------- |
    | `-c, --config FILE` | `langgraph.json` | Path to the [configuration file](#configuration-file) declaring dependencies, graphs and environment variables. |
    | `--help`            |                  | Show this message and exit.                                                                                     |

This generates a Dockerfile that looks similar to:

<Note>The `npx @langchain/langgraph-cli dockerfile` command translates all the configuration in your `langgraph.json` file into Dockerfile commands. When using this command, you will have to re-run it whenever you update your `langgraph.json` file. Otherwise, your changes will not be reflected when you build or run the dockerfile.</Note>
  </Tab>
</Tabs>

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/cli.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown

```

Example 2 (unknown):
```unknown
</CodeGroup>

3. Verify the install

   <CodeGroup>
```

Example 3 (unknown):
```unknown

```

Example 4 (unknown):
```unknown
</CodeGroup>

### Quick commands

| Command                               | What it does                                                                                                                         |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| [`langgraph dev`](#dev)               | Starts a lightweight local dev server (no Docker required), ideal for rapid testing.                                                 |
| [`langgraph build`](#build)           | Builds a Docker image of your LangGraph API server for deployment.                                                                   |
| [`langgraph dockerfile`](#dockerfile) | Emits a Dockerfile derived from your config for custom builds.                                                                       |
| [`langgraph up`](#up)                 | Starts the LangGraph API server locally in Docker. Requires Docker running; LangSmith API key for local dev; license for production. |

For JS, use `npx @langchain/langgraph-cli <command>` (or `langgraphjs` if installed globally).

## Configuration file

To build and run a valid application, the LangGraph CLI requires a JSON configuration file that follows this [schema](https://raw.githubusercontent.com/langchain-ai/langgraph/refs/heads/main/libs/cli/schemas/schema.json). It contains the following properties:

<Note>The LangGraph CLI defaults to using the configuration file named <strong>langgraph.json</strong> in the current directory.</Note>

<Tabs>
  <Tab title="Python">
    | Key                                                              | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
    | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | <span style={{ whiteSpace: "nowrap" }}>`dependencies`</span>     | **Required**. Array of dependencies for LangSmith API server. Dependencies can be one of the following: <ul><li>A single period (`"."`), which will look for local Python packages.</li><li>The directory path where `pyproject.toml`, `setup.py` or `requirements.txt` is located.<br />For example, if `requirements.txt` is located in the root of the project directory, specify `"./"`. If it's located in a subdirectory called `local_package`, specify `"./local_package"`. Do not specify the string `"requirements.txt"` itself.</li><li>A Python package name.</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | <span style={{ whiteSpace: "nowrap" }}>`graphs`</span>           | **Required**. Mapping from graph ID to path where the compiled graph or a function that makes a graph is defined. Example: <ul><li>`./your_package/your_file.py:variable`, where `variable` is an instance of `langgraph.graph.state.CompiledStateGraph`</li><li>`./your_package/your_file.py:make_graph`, where `make_graph` is a function that takes a config dictionary (`langchain_core.runnables.RunnableConfig`) and returns an instance of `langgraph.graph.state.StateGraph` or `langgraph.graph.state.CompiledStateGraph`. See [how to rebuild a graph at runtime](/langsmith/graph-rebuild) for more details.</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | <span style={{ whiteSpace: "nowrap" }}>`auth`</span>             | *(Added in v0.0.11)* Auth configuration containing the path to your authentication handler. Example: `./your_package/auth.py:auth`, where `auth` is an instance of `langgraph_sdk.Auth`. See [authentication guide](/langsmith/auth) for details.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | <span style={{ whiteSpace: "nowrap" }}>`base_image`</span>       | Optional. Base image to use for the LangGraph API server. Defaults to `langchain/langgraph-api` or `langchain/langgraphjs-api`. Use this to pin your builds to a particular version of the langgraph API, such as `"langchain/langgraph-server:0.2"`. See [https://hub.docker.com/r/langchain/langgraph-server/tags](https://hub.docker.com/r/langchain/langgraph-server/tags) for more details. (added in `langgraph-cli==0.2.8`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | <span style={{ whiteSpace: "nowrap" }}>`image_distro`</span>     | Optional. Linux distribution for the base image. Must be one of `"debian"`, `"wolfi"`, `"bookworm"`, or `"bullseye"`. If omitted, defaults to `"debian"`. Available in `langgraph-cli>=0.2.11`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | <span style={{ whiteSpace: "nowrap" }}>`env`</span>              | Path to `.env` file or a mapping from environment variable to its value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
    | <span style={{ whiteSpace: "nowrap" }}>`store`</span>            | Configuration for adding semantic search and/or time-to-live (TTL) to the BaseStore. Contains the following fields: <ul><li>`index` (optional): Configuration for semantic search indexing with fields `embed`, `dims`, and optional `fields`.</li><li>`ttl` (optional): Configuration for item expiration. An object with optional fields: `refresh_on_read` (boolean, defaults to `true`), `default_ttl` (float, lifespan in **minutes**; applied to newly created items only; existing items are unchanged; defaults to no expiration), and `sweep_interval_minutes` (integer, how often to check for expired items, defaults to no sweeping).</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
    | <span style={{ whiteSpace: "nowrap" }}>`ui`</span>               | Optional. Named definitions of UI components emitted by the agent, each pointing to a JS/TS file. (added in `langgraph-cli==0.1.84`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
    | <span style={{ whiteSpace: "nowrap" }}>`python_version`</span>   | `3.11`, `3.12`, or `3.13`. Defaults to `3.11`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
    | <span style={{ whiteSpace: "nowrap" }}>`node_version`</span>     | Specify `node_version: 20` to use LangGraph.js.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | <span style={{ whiteSpace: "nowrap" }}>`pip_config_file`</span>  | Path to `pip` config file.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
    | <span style={{ whiteSpace: "nowrap" }}>`pip_installer`</span>    | *(Added in v0.3)* Optional. Python package installer selector. It can be set to `"auto"`, `"pip"`, or `"uv"`. From version 0.3 onward the default strategy is to run `uv pip`, which typically delivers faster builds while remaining a drop-in replacement. In the uncommon situation where `uv` cannot handle your dependency graph or the structure of your `pyproject.toml`, specify `"pip"` here to revert to the earlier behaviour.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
    | <span style={{ whiteSpace: "nowrap" }}>`keep_pkg_tools`</span>   | *(Added in v0.3.4)* Optional. Control whether to retain Python packaging tools (`pip`, `setuptools`, `wheel`) in the final image. Accepted values: <ul><li><code>true</code> : Keep all three tools (skip uninstall).</li><li><code>false</code> / omitted : Uninstall all three tools (default behaviour).</li><li><code>list\[str]</code> : Names of tools <strong>to retain</strong>. Each value must be one of "pip", "setuptools", "wheel".</li></ul>. By default, all three tools are uninstalled.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
    | <span style={{ whiteSpace: "nowrap" }}>`dockerfile_lines`</span> | Array of additional lines to add to Dockerfile following the import from parent image.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
    | <span style={{ whiteSpace: "nowrap" }}>`checkpointer`</span>     | Configuration for the checkpointer. Supports: <ul><li>`ttl` (optional): Object with `strategy`, `sweep_interval_minutes`, `default_ttl` controlling checkpoint expiry.</li><li>`serde` (optional, 0.5+): Object with `allowed_json_modules` and `pickle_fallback` to tune deserialization behavior.</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
    | <span style={{ whiteSpace: "nowrap" }}>`http`</span>             | HTTP server configuration with the following fields: <ul><li>`app`: Path to custom Starlette/FastAPI app (e.g., `"./src/agent/webapp.py:app"`). See [custom routes guide](/langsmith/custom-routes).</li><li>`cors`: CORS configuration with fields such as `allow_origins`, `allow_methods`, `allow_headers`, `allow_credentials`, `allow_origin_regex`, `expose_headers`, and `max_age`.</li><li>`configurable_headers`: Define which request headers to expose as configurable values via `includes` / `excludes` patterns.</li><li>`logging_headers`: Mirror of `configurable_headers` for excluding sensitive headers from logs.</li><li>`middleware_order`: Choose how custom middleware and auth interact. `auth_first` runs authentication hooks before custom middleware, while `middleware_first` (default) runs your middleware first.</li><li>`enable_custom_route_auth`: Apply auth checks to routes added through `app`.</li><li>`disable_assistants`, `disable_mcp`, `disable_meta`, `disable_runs`, `disable_store`, `disable_threads`, `disable_ui`, `disable_webhooks`: Disable built-in routes or hooks.</li><li>`mount_prefix`: Prefix for mounted routes (e.g., "/my-deployment/api").</li></ul> |
    | <span style={{ whiteSpace: "nowrap" }}>`api_version`</span>      | *(Added in v0.3.7)* Which semantic version of the LangGraph API server to use (e.g., `"0.3"`). Defaults to latest. Check the server [changelog](/langsmith/agent-server-changelog) for details on each release.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
  </Tab>

  <Tab title="JS">
    | Key                                                              | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
    | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | <span style={{ whiteSpace: "nowrap" }}>`graphs`</span>           | **Required**. Mapping from graph ID to path where the compiled graph or a function that makes a graph is defined. Example: <ul><li>`./src/graph.ts:variable`, where `variable` is an instance of [`CompiledStateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph)</li><li>`./src/graph.ts:makeGraph`, where `makeGraph` is a function that takes a config dictionary (`LangGraphRunnableConfig`) and returns an instance of [`StateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.StateGraph) or [`CompiledStateGraph`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph). See [how to rebuild a graph at runtime](/langsmith/graph-rebuild) for more details.</li></ul> |
    | <span style={{ whiteSpace: "nowrap" }}>`env`</span>              | Path to `.env` file or a mapping from environment variable to its value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | <span style={{ whiteSpace: "nowrap" }}>`store`</span>            | Configuration for adding semantic search and/or time-to-live (TTL) to the BaseStore. Contains the following fields: <ul><li>`index` (optional): Configuration for semantic search indexing with fields `embed`, `dims`, and optional `fields`.</li><li>`ttl` (optional): Configuration for item expiration. An object with optional fields: `refresh_on_read` (boolean, defaults to `true`), `default_ttl` (float, lifespan in **minutes**; applied to newly created items only; existing items are unchanged; defaults to no expiration), and `sweep_interval_minutes` (integer, how often to check for expired items, defaults to no sweeping).</li></ul>                                                                                                                                                                |
    | <span style={{ whiteSpace: "nowrap" }}>`node_version`</span>     | Specify `node_version: 20` to use LangGraph.js.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
    | <span style={{ whiteSpace: "nowrap" }}>`dockerfile_lines`</span> | Array of additional lines to add to Dockerfile following the import from parent image.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | <span style={{ whiteSpace: "nowrap" }}>`checkpointer`</span>     | Configuration for the checkpointer. Supports: <ul><li>`ttl` (optional): Object with `strategy`, `sweep_interval_minutes`, `default_ttl` controlling checkpoint expiry.</li><li>`serde` (optional, 0.5+): Object with `allowed_json_modules` and `pickle_fallback` to tune deserialization behavior.</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
    | <span style={{ whiteSpace: "nowrap" }}>`http`</span>             | HTTP server configuration mirroring the Python options: <ul><li>`cors` with `allow_origins`, `allow_methods`, `allow_headers`, `allow_credentials`, `allow_origin_regex`, `expose_headers`, `max_age`.</li><li>`configurable_headers` and `logging_headers` pattern lists.</li><li>`middleware_order` (`auth_first` or `middleware_first`).</li><li>`enable_custom_route_auth` plus the same boolean route toggles as above.</li></ul>                                                                                                                                                                                                                                                                                                                                                                                     |
    | <span style={{ whiteSpace: "nowrap" }}>`api_version`</span>      | *(Added in v0.3.7)* Which semantic version of the LangGraph API server to use (e.g., `"0.3"`). Defaults to latest. Check the server [changelog](/langsmith/agent-server-changelog) for details on each release.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
  </Tab>
</Tabs>

### Examples

<Tabs>
  <Tab title="Python">
    #### Basic configuration
```

---

## Get the tool call

**URL:** llms-txt#get-the-tool-call

**Contents:**
- Prompt chaining
- Parallelization
- Routing
- Orchestrator-worker
  - Creating workers in LangGraph

msg.tool_calls
python Graph API theme={null}
  from typing_extensions import TypedDict
  from langgraph.graph import StateGraph, START, END
  from IPython.display import Image, display

# Graph state
  class State(TypedDict):
      topic: str
      joke: str
      improved_joke: str
      final_joke: str

# Nodes
  def generate_joke(state: State):
      """First LLM call to generate initial joke"""

msg = llm.invoke(f"Write a short joke about {state['topic']}")
      return {"joke": msg.content}

def check_punchline(state: State):
      """Gate function to check if the joke has a punchline"""

# Simple check - does the joke contain "?" or "!"
      if "?" in state["joke"] or "!" in state["joke"]:
          return "Pass"
      return "Fail"

def improve_joke(state: State):
      """Second LLM call to improve the joke"""

msg = llm.invoke(f"Make this joke funnier by adding wordplay: {state['joke']}")
      return {"improved_joke": msg.content}

def polish_joke(state: State):
      """Third LLM call for final polish"""
      msg = llm.invoke(f"Add a surprising twist to this joke: {state['improved_joke']}")
      return {"final_joke": msg.content}

# Build workflow
  workflow = StateGraph(State)

# Add nodes
  workflow.add_node("generate_joke", generate_joke)
  workflow.add_node("improve_joke", improve_joke)
  workflow.add_node("polish_joke", polish_joke)

# Add edges to connect nodes
  workflow.add_edge(START, "generate_joke")
  workflow.add_conditional_edges(
      "generate_joke", check_punchline, {"Fail": "improve_joke", "Pass": END}
  )
  workflow.add_edge("improve_joke", "polish_joke")
  workflow.add_edge("polish_joke", END)

# Compile
  chain = workflow.compile()

# Show workflow
  display(Image(chain.get_graph().draw_mermaid_png()))

# Invoke
  state = chain.invoke({"topic": "cats"})
  print("Initial joke:")
  print(state["joke"])
  print("\n--- --- ---\n")
  if "improved_joke" in state:
      print("Improved joke:")
      print(state["improved_joke"])
      print("\n--- --- ---\n")

print("Final joke:")
      print(state["final_joke"])
  else:
      print("Joke failed quality gate - no punchline detected!")
  python Functional API theme={null}
  from langgraph.func import entrypoint, task

# Tasks
  @task
  def generate_joke(topic: str):
      """First LLM call to generate initial joke"""
      msg = llm.invoke(f"Write a short joke about {topic}")
      return msg.content

def check_punchline(joke: str):
      """Gate function to check if the joke has a punchline"""
      # Simple check - does the joke contain "?" or "!"
      if "?" in joke or "!" in joke:
          return "Fail"

@task
  def improve_joke(joke: str):
      """Second LLM call to improve the joke"""
      msg = llm.invoke(f"Make this joke funnier by adding wordplay: {joke}")
      return msg.content

@task
  def polish_joke(joke: str):
      """Third LLM call for final polish"""
      msg = llm.invoke(f"Add a surprising twist to this joke: {joke}")
      return msg.content

@entrypoint()
  def prompt_chaining_workflow(topic: str):
      original_joke = generate_joke(topic).result()
      if check_punchline(original_joke) == "Pass":
          return original_joke

improved_joke = improve_joke(original_joke).result()
      return polish_joke(improved_joke).result()

# Invoke
  for step in prompt_chaining_workflow.stream("cats", stream_mode="updates"):
      print(step)
      print("\n")
  python Graph API theme={null}
  # Graph state
  class State(TypedDict):
      topic: str
      joke: str
      story: str
      poem: str
      combined_output: str

# Nodes
  def call_llm_1(state: State):
      """First LLM call to generate initial joke"""

msg = llm.invoke(f"Write a joke about {state['topic']}")
      return {"joke": msg.content}

def call_llm_2(state: State):
      """Second LLM call to generate story"""

msg = llm.invoke(f"Write a story about {state['topic']}")
      return {"story": msg.content}

def call_llm_3(state: State):
      """Third LLM call to generate poem"""

msg = llm.invoke(f"Write a poem about {state['topic']}")
      return {"poem": msg.content}

def aggregator(state: State):
      """Combine the joke and story into a single output"""

combined = f"Here's a story, joke, and poem about {state['topic']}!\n\n"
      combined += f"STORY:\n{state['story']}\n\n"
      combined += f"JOKE:\n{state['joke']}\n\n"
      combined += f"POEM:\n{state['poem']}"
      return {"combined_output": combined}

# Build workflow
  parallel_builder = StateGraph(State)

# Add nodes
  parallel_builder.add_node("call_llm_1", call_llm_1)
  parallel_builder.add_node("call_llm_2", call_llm_2)
  parallel_builder.add_node("call_llm_3", call_llm_3)
  parallel_builder.add_node("aggregator", aggregator)

# Add edges to connect nodes
  parallel_builder.add_edge(START, "call_llm_1")
  parallel_builder.add_edge(START, "call_llm_2")
  parallel_builder.add_edge(START, "call_llm_3")
  parallel_builder.add_edge("call_llm_1", "aggregator")
  parallel_builder.add_edge("call_llm_2", "aggregator")
  parallel_builder.add_edge("call_llm_3", "aggregator")
  parallel_builder.add_edge("aggregator", END)
  parallel_workflow = parallel_builder.compile()

# Show workflow
  display(Image(parallel_workflow.get_graph().draw_mermaid_png()))

# Invoke
  state = parallel_workflow.invoke({"topic": "cats"})
  print(state["combined_output"])
  python Functional API theme={null}
  @task
  def call_llm_1(topic: str):
      """First LLM call to generate initial joke"""
      msg = llm.invoke(f"Write a joke about {topic}")
      return msg.content

@task
  def call_llm_2(topic: str):
      """Second LLM call to generate story"""
      msg = llm.invoke(f"Write a story about {topic}")
      return msg.content

@task
  def call_llm_3(topic):
      """Third LLM call to generate poem"""
      msg = llm.invoke(f"Write a poem about {topic}")
      return msg.content

@task
  def aggregator(topic, joke, story, poem):
      """Combine the joke and story into a single output"""

combined = f"Here's a story, joke, and poem about {topic}!\n\n"
      combined += f"STORY:\n{story}\n\n"
      combined += f"JOKE:\n{joke}\n\n"
      combined += f"POEM:\n{poem}"
      return combined

# Build workflow
  @entrypoint()
  def parallel_workflow(topic: str):
      joke_fut = call_llm_1(topic)
      story_fut = call_llm_2(topic)
      poem_fut = call_llm_3(topic)
      return aggregator(
          topic, joke_fut.result(), story_fut.result(), poem_fut.result()
      ).result()

# Invoke
  for step in parallel_workflow.stream("cats", stream_mode="updates"):
      print(step)
      print("\n")
  python Graph API theme={null}
  from typing_extensions import Literal
  from langchain.messages import HumanMessage, SystemMessage

# Schema for structured output to use as routing logic
  class Route(BaseModel):
      step: Literal["poem", "story", "joke"] = Field(
          None, description="The next step in the routing process"
      )

# Augment the LLM with schema for structured output
  router = llm.with_structured_output(Route)

# State
  class State(TypedDict):
      input: str
      decision: str
      output: str

# Nodes
  def llm_call_1(state: State):
      """Write a story"""

result = llm.invoke(state["input"])
      return {"output": result.content}

def llm_call_2(state: State):
      """Write a joke"""

result = llm.invoke(state["input"])
      return {"output": result.content}

def llm_call_3(state: State):
      """Write a poem"""

result = llm.invoke(state["input"])
      return {"output": result.content}

def llm_call_router(state: State):
      """Route the input to the appropriate node"""

# Run the augmented LLM with structured output to serve as routing logic
      decision = router.invoke(
          [
              SystemMessage(
                  content="Route the input to story, joke, or poem based on the user's request."
              ),
              HumanMessage(content=state["input"]),
          ]
      )

return {"decision": decision.step}

# Conditional edge function to route to the appropriate node
  def route_decision(state: State):
      # Return the node name you want to visit next
      if state["decision"] == "story":
          return "llm_call_1"
      elif state["decision"] == "joke":
          return "llm_call_2"
      elif state["decision"] == "poem":
          return "llm_call_3"

# Build workflow
  router_builder = StateGraph(State)

# Add nodes
  router_builder.add_node("llm_call_1", llm_call_1)
  router_builder.add_node("llm_call_2", llm_call_2)
  router_builder.add_node("llm_call_3", llm_call_3)
  router_builder.add_node("llm_call_router", llm_call_router)

# Add edges to connect nodes
  router_builder.add_edge(START, "llm_call_router")
  router_builder.add_conditional_edges(
      "llm_call_router",
      route_decision,
      {  # Name returned by route_decision : Name of next node to visit
          "llm_call_1": "llm_call_1",
          "llm_call_2": "llm_call_2",
          "llm_call_3": "llm_call_3",
      },
  )
  router_builder.add_edge("llm_call_1", END)
  router_builder.add_edge("llm_call_2", END)
  router_builder.add_edge("llm_call_3", END)

# Compile workflow
  router_workflow = router_builder.compile()

# Show the workflow
  display(Image(router_workflow.get_graph().draw_mermaid_png()))

# Invoke
  state = router_workflow.invoke({"input": "Write me a joke about cats"})
  print(state["output"])
  python Functional API theme={null}
  from typing_extensions import Literal
  from pydantic import BaseModel
  from langchain.messages import HumanMessage, SystemMessage

# Schema for structured output to use as routing logic
  class Route(BaseModel):
      step: Literal["poem", "story", "joke"] = Field(
          None, description="The next step in the routing process"
      )

# Augment the LLM with schema for structured output
  router = llm.with_structured_output(Route)

@task
  def llm_call_1(input_: str):
      """Write a story"""
      result = llm.invoke(input_)
      return result.content

@task
  def llm_call_2(input_: str):
      """Write a joke"""
      result = llm.invoke(input_)
      return result.content

@task
  def llm_call_3(input_: str):
      """Write a poem"""
      result = llm.invoke(input_)
      return result.content

def llm_call_router(input_: str):
      """Route the input to the appropriate node"""
      # Run the augmented LLM with structured output to serve as routing logic
      decision = router.invoke(
          [
              SystemMessage(
                  content="Route the input to story, joke, or poem based on the user's request."
              ),
              HumanMessage(content=input_),
          ]
      )
      return decision.step

# Create workflow
  @entrypoint()
  def router_workflow(input_: str):
      next_step = llm_call_router(input_)
      if next_step == "story":
          llm_call = llm_call_1
      elif next_step == "joke":
          llm_call = llm_call_2
      elif next_step == "poem":
          llm_call = llm_call_3

return llm_call(input_).result()

# Invoke
  for step in router_workflow.stream("Write me a joke about cats", stream_mode="updates"):
      print(step)
      print("\n")
  python Graph API theme={null}
  from typing import Annotated, List
  import operator

# Schema for structured output to use in planning
  class Section(BaseModel):
      name: str = Field(
          description="Name for this section of the report.",
      )
      description: str = Field(
          description="Brief overview of the main topics and concepts to be covered in this section.",
      )

class Sections(BaseModel):
      sections: List[Section] = Field(
          description="Sections of the report.",
      )

# Augment the LLM with schema for structured output
  planner = llm.with_structured_output(Sections)
  python Functional API theme={null}
  from typing import List

# Schema for structured output to use in planning
  class Section(BaseModel):
      name: str = Field(
          description="Name for this section of the report.",
      )
      description: str = Field(
          description="Brief overview of the main topics and concepts to be covered in this section.",
      )

class Sections(BaseModel):
      sections: List[Section] = Field(
          description="Sections of the report.",
      )

# Augment the LLM with schema for structured output
  planner = llm.with_structured_output(Sections)

@task
  def orchestrator(topic: str):
      """Orchestrator that generates a plan for the report"""
      # Generate queries
      report_sections = planner.invoke(
          [
              SystemMessage(content="Generate a plan for the report."),
              HumanMessage(content=f"Here is the report topic: {topic}"),
          ]
      )

return report_sections.sections

@task
  def llm_call(section: Section):
      """Worker writes a section of the report"""

# Generate section
      result = llm.invoke(
          [
              SystemMessage(content="Write a report section."),
              HumanMessage(
                  content=f"Here is the section name: {section.name} and description: {section.description}"
              ),
          ]
      )

# Write the updated section to completed sections
      return result.content

@task
  def synthesizer(completed_sections: list[str]):
      """Synthesize full report from sections"""
      final_report = "\n\n---\n\n".join(completed_sections)
      return final_report

@entrypoint()
  def orchestrator_worker(topic: str):
      sections = orchestrator(topic).result()
      section_futures = [llm_call(section) for section in sections]
      final_report = synthesizer(
          [section_fut.result() for section_fut in section_futures]
      ).result()
      return final_report

# Invoke
  report = orchestrator_worker.invoke("Create a report on LLM scaling laws")
  from IPython.display import Markdown
  Markdown(report)
  python  theme={null}
from langgraph.types import Send

**Examples:**

Example 1 (unknown):
```unknown
## Prompt chaining

Prompt chaining is when each LLM call processes the output of the previous call. It's often used for performing well-defined tasks that can be broken down into smaller, verifiable steps. Some examples include:

* Translating documents into different languages
* Verifying generated content for consistency

<img src="https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/prompt_chain.png?fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=762dec147c31b8dc6ebb0857e236fc1f" alt="Prompt chaining" data-og-width="1412" width="1412" data-og-height="444" height="444" data-path="oss/images/prompt_chain.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/prompt_chain.png?w=280&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=fda27cf4f997e350d4ce48be16049c47 280w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/prompt_chain.png?w=560&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=1374b6de11900d394fc73722a3a6040e 560w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/prompt_chain.png?w=840&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=25246c7111a87b5df5a2af24a0181efe 840w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/prompt_chain.png?w=1100&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=0c57da86a49cf966cc090497ade347f1 1100w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/prompt_chain.png?w=1650&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=a1b5c8fc644d7a80c0792b71769c97da 1650w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/prompt_chain.png?w=2500&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=8a3f66f0e365e503a85b30be48bc1a76 2500w" />

<CodeGroup>
```

Example 2 (unknown):
```unknown

```

Example 3 (unknown):
```unknown
</CodeGroup>

## Parallelization

With parallelization, LLMs work simultaneously on a task. This is either done by running multiple independent subtasks at the same time, or running the same task multiple times to check for different outputs. Parallelization is commonly used to:

* Split up subtasks and run them in parallel, which increases speed
* Run tasks multiple times to check for different outputs, which increases confidence

Some examples include:

* Running one subtask that processes a document for keywords, and a second subtask to check for formatting errors
* Running a task multiple times that scores a document for accuracy based on different criteria, like the number of citations, the number of sources used, and the quality of the sources

<img src="https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/parallelization.png?fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=8afe3c427d8cede6fed1e4b2a5107b71" alt="parallelization.png" data-og-width="1020" width="1020" data-og-height="684" height="684" data-path="oss/images/parallelization.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/parallelization.png?w=280&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=88e51062b14d9186a6f0ea246bc48635 280w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/parallelization.png?w=560&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=934941ca52019b7cbce7fbdd31d00f0f 560w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/parallelization.png?w=840&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=30b5c86c545d0e34878ff0a2c367dd0a 840w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/parallelization.png?w=1100&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=6227d2c39f332eaeda23f7db66871dd7 1100w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/parallelization.png?w=1650&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=283f3ee2924a385ab88f2cbfd9c9c48c 1650w, https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/parallelization.png?w=2500&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=69f6a97716b38998b7b399c3d8ac7d9c 2500w" />

<CodeGroup>
```

Example 4 (unknown):
```unknown

```

---

## LangGraph SDK

**URL:** llms-txt#langgraph-sdk

Source: https://docs.langchain.com/oss/python/reference/langgraph-python

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/reference/langgraph-python.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## {'graph_output': 'My name is Lance'}

**URL:** llms-txt#{'graph_output':-'my-name-is-lance'}

**Contents:**
  - Reducers
  - Working with Messages in Graph State

python  theme={null}
   StateGraph(
       OverallState,
       input_schema=InputState,
       output_schema=OutputState
   )
   python Example A theme={null}
from typing_extensions import TypedDict

class State(TypedDict):
    foo: int
    bar: list[str]
python Example B theme={null}
from typing import Annotated
from typing_extensions import TypedDict
from operator import add

class State(TypedDict):
    foo: int
    bar: Annotated[list[str], add]
python  theme={null}

**Examples:**

Example 1 (unknown):
```unknown
There are two subtle and important points to note here:

1. We pass `state: InputState` as the input schema to `node_1`. But, we write out to `foo`, a channel in `OverallState`. How can we write out to a state channel that is not included in the input schema? This is because a node *can write to any state channel in the graph state.* The graph state is the union of the state channels defined at initialization, which includes `OverallState` and the filters `InputState` and `OutputState`.

2. We initialize the graph with:
```

Example 2 (unknown):
```unknown
So, how can we write to `PrivateState` in `node_2`? How does the graph gain access to this schema if it was not passed in the `StateGraph` initialization?

   We can do this because `_nodes` can also declare additional state `channels_` as long as the state schema definition exists. In this case, the `PrivateState` schema is defined, so we can add `bar` as a new state channel in the graph and write to it.

### Reducers

Reducers are key to understanding how updates from nodes are applied to the `State`. Each key in the `State` has its own independent reducer function. If no reducer function is explicitly specified then it is assumed that all updates to that key should override it. There are a few different types of reducers, starting with the default type of reducer:

#### Default Reducer

These two examples show how to use the default reducer:
```

Example 3 (unknown):
```unknown
In this example, no reducer functions are specified for any key. Let's assume the input to the graph is:

`{"foo": 1, "bar": ["hi"]}`. Let's then assume the first `Node` returns `{"foo": 2}`. This is treated as an update to the state. Notice that the `Node` does not need to return the whole `State` schema - just an update. After applying this update, the `State` would then be `{"foo": 2, "bar": ["hi"]}`. If the second node returns `{"bar": ["bye"]}` then the `State` would then be `{"foo": 2, "bar": ["bye"]}`
```

Example 4 (unknown):
```unknown
In this example, we've used the `Annotated` type to specify a reducer function (`operator.add`) for the second key (`bar`). Note that the first key remains unchanged. Let's assume the input to the graph is `{"foo": 1, "bar": ["hi"]}`. Let's then assume the first `Node` returns `{"foo": 2}`. This is treated as an update to the state. Notice that the `Node` does not need to return the whole `State` schema - just an update. After applying this update, the `State` would then be `{"foo": 2, "bar": ["hi"]}`. If the second node returns `{"bar": ["bye"]}` then the `State` would then be `{"foo": 2, "bar": ["hi", "bye"]}`. Notice here that the `bar` key is updated by adding the two lists together.

#### Overwrite

<Tip>
  In some cases, you may want to bypass a reducer and directly overwrite a state value. LangGraph provides the [`Overwrite`](https://reference.langchain.com/python/langgraph/types/) type for this purpose. [Learn how to use `Overwrite` here](/oss/python/langgraph/use-graph-api#bypass-reducers-with-overwrite).
</Tip>

### Working with Messages in Graph State

#### Why use messages?

Most modern LLM providers have a chat model interface that accepts a list of messages as input. LangChain's [chat model interface](/oss/python/langchain/models) in particular accepts a list of message objects as inputs. These messages come in a variety of forms such as [`HumanMessage`](https://reference.langchain.com/python/langchain/messages/#langchain.messages.HumanMessage) (user input) or [`AIMessage`](https://reference.langchain.com/python/langchain/messages/#langchain.messages.AIMessage) (LLM response).

To read more about what message objects are, please refer to the [Messages conceptual guide](/oss/python/langchain/messages).

#### Using Messages in your Graph

In many cases, it is helpful to store prior conversation history as a list of messages in your graph state. To do so, we can add a key (channel) to the graph state that stores a list of `Message` objects and annotate it with a reducer function (see `messages` key in the example below). The reducer function is vital to telling the graph how to update the list of `Message` objects in the state with each state update (for example, when a node sends an update). If you don't specify a reducer, every state update will overwrite the list of messages with the most recently provided value. If you wanted to simply append messages to the existing list, you could use `operator.add` as a reducer.

However, you might also want to manually update messages in your graph state (e.g. human-in-the-loop). If you were to use `operator.add`, the manual state updates you send to the graph would be appended to the existing list of messages, instead of updating existing messages. To avoid that, you need a reducer that can keep track of message IDs and overwrite existing messages, if updated. To achieve this, you can use the prebuilt [`add_messages`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.message.add_messages) function. For brand new messages, it will simply append to existing list, but it will also handle the updates for existing messages correctly.

#### Serialization

In addition to keeping track of message IDs, the [`add_messages`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.message.add_messages) function will also try to deserialize messages into LangChain `Message` objects whenever a state update is received on the `messages` channel.

See more information on LangChain serialization/deserialization [here](https://python.langchain.com/docs/how_to/serialization/). This allows sending graph inputs / state updates in the following format:
```

---

## We now add a conditional edge

**URL:** llms-txt#we-now-add-a-conditional-edge

workflow.add_conditional_edges(
    # First, we define the start node. We use 'agent'.
    # This means these are the edges taken after the 'agent' node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
)

---

## Graph state.

**URL:** llms-txt#graph-state.

class State(TypedDict):
    """Agent state."""
    messages: Annotated[list[AnyMessage], add_messages]
    followup: str | None

invoice_id: int | None
    invoice_line_ids: list[int] | None
    customer_first_name: str | None
    customer_last_name: str | None
    customer_phone: str | None
    track_name: str | None
    album_title: str | None
    artist_name: str | None
    purchase_date_iso_8601: str | None

---

## The `authenticate` decorator tells LangGraph to call this function as middleware

**URL:** llms-txt#the-`authenticate`-decorator-tells-langgraph-to-call-this-function-as-middleware

---

## How to use Studio

**URL:** llms-txt#how-to-use-studio

**Contents:**
- Run application
- Manage assistants
- Manage threads
- Next steps

Source: https://docs.langchain.com/langsmith/use-studio

This page describes the core workflows you’ll use in Studio. It explains how to run your application, manage assistant configurations, and work with conversation threads. Each section includes steps in both graph mode (full-featured view of your graph’s execution) and chat mode (lightweight conversational interface):

* [Run application](#run-application): Execute your application or agent and observe its behavior.
* [Manage assistants](#manage-assistants): Create, edit, and select the assistant configuration used by your application.
* [Manage threads](#manage-threads): View and organize the threads, including forking or editing past runs for debugging.

<Tabs>
  <Tab title="Graph">
    ### Specify input

1. Define the input to your graph in the **Input** section on the left side of the page, below the graph interface. Studio will attempt to render a form for your input based on the graph's defined [state schema](/oss/python/langgraph/graph-api/#schema). To disable this, click the **View Raw** button, which will present you with a JSON editor.
    2. Click the up or down arrows at the top of the **Input** section to toggle through and use previously submitted inputs.

To specify the [assistant](/langsmith/assistants) that is used for the run:

1. Click the **Settings** button in the bottom left corner. If an assistant is currently selected the button will also list the assistant name. If no assistant is selected it will say **Manage Assistants**.
    2. Select the assistant to run.
    3. Click the **Active** toggle at the top of the modal to activate it.

For more information, refer to [Manage assistants](#manage-assistants).

Click the dropdown next to **Submit** and click the toggle to enable or disable streaming.

To run your graph with breakpoints:

1. Click **Interrupt**.
    2. Select a node and whether to pause before or after that node has executed.
    3. Click **Continue** in the thread log to resume execution.

For more information on breakpoints, refer to [Human-in-the-loop](/oss/python/langchain/human-in-the-loop).

To submit the run with the specified input and run settings:

1. Click the **Submit** button. This will add a [run](/langsmith/assistants#execution) to the existing selected [thread](/oss/python/langgraph/persistence#threads). If no thread is currently selected, a new one will be created.
    2. To cancel the ongoing run, click the **Cancel** button.
  </Tab>

<Tab title="Chat">
    Specify the input to your chat application in the bottom of the conversation panel.

1. Click the **Send message** button to submit the input as a Human message and have the response streamed back.

To cancel the ongoing run:

1. Click **Cancel**.
    2. Click the **Show tool calls** toggle to hide or show tool calls in the conversation.
  </Tab>
</Tabs>

Studio lets you view, edit, and update your assistants, and allows you to run your graph using these assistant configurations.

For more conceptual details, refer to the [Assistants overview](/langsmith/assistants/).

<Tabs>
  <Tab title="Graph">
    To view your assistants:

1. Click **Manage Assistants** in the bottom left corner. This opens a modal for you to view all the assistants for the selected graph.
    2. Specify the assistant and its version you would like to mark as **Active**. LangSmith will use this assistant when runs are submitted.

The **Default configuration** option will be active, which reflects the default configuration defined in your graph. Edits made to this configuration will be used to update the run-time configuration, but will not update or create a new assistant unless you click **Create new assistant**.
  </Tab>

<Tab title="Chat">
    Chat mode enables you to switch through the different assistants in your graph via the dropdown selector at the top of the page. To create, edit, or delete assistants, use Graph mode.
  </Tab>
</Tabs>

Studio provides tools to view all [threads](/oss/python/langgraph/persistence#threads) saved on the server and edit their state. You can create new threads, switch between threads, and modify past states both in graph mode and chat mode.

<Tabs>
  <Tab title="Graph">
    ### View threads

1. In the top of the right-hand pane, select the dropdown menu to view existing threads.
    2. Select the desired thread, and the thread history will populate in the right-hand side of the page.
    3. To create a new thread, click **+ New Thread** and [submit a run](#run-application).
    4. To view more granular information in the thread, drag the slider at the top of the page to the right. To view less information, drag the slider to the left. Additionally, collapse or expand individual turns, nodes, and keys of the state.
    5. Switch between `Pretty` and `JSON` mode for different rendering formats.

### Edit thread history

To edit the state of the thread:

1. Select <Icon icon="pencil" /> **Edit node state** next to the desired node.
    2. Edit the node's output as desired and click **Fork** to confirm. This will create a new forked run from the checkpoint of the selected node.

If you instead want to re-run the thread from a given checkpoint without editing the state, click **Re-run from here**. This will again create a new forked run from the selected checkpoint. This is useful for re-running with changes that are not specific to the state, such as the selected assistant.
  </Tab>

<Tab title="Chat">
    1. View all threads in the right-hand pane of the page.
    2. Select the desired thread and the thread history will populate in the center panel.
    3. To create a new thread, click **+** and submit a run.

To edit a human message in the thread:

1. Click <Icon icon="pencil" /> **Edit node state** below the human message.
    2. Edit the message as desired and submit. This will create a new fork of the conversation history.
    3. To re-generate an AI message, click the retry icon below the AI message.
  </Tab>
</Tabs>

Refer to the following guides for more detail on tasks you can complete in Studio:

* [Iterate on prompts](/langsmith/observability-studio)
* [Run experiments over datasets](/langsmith/observability-studio#run-experiments-over-a-dataset)

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/use-studio.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## Data storage and privacy

**URL:** llms-txt#data-storage-and-privacy

**Contents:**
- CLI
- Agent Server
  - LangSmith Tracing
  - In-memory development server
  - Standalone Server
- Studio
- Quick reference

Source: https://docs.langchain.com/langsmith/data-storage-and-privacy

This document describes how data is processed in the LangGraph CLI and the Agent Server for both the in-memory server (`langgraph dev`) and the local Docker server (`langgraph up`). It also describes what data is tracked when interacting with the hosted Studio frontend.

LangGraph **CLI** is the command-line interface for building and running LangGraph applications; see the [CLI guide](/langsmith/cli) to learn more.

By default, calls to most CLI commands log a single analytics event upon invocation. This helps us better prioritize improvements to the CLI experience. Each telemetry event contains the calling process's OS, OS version, Python version, the CLI version, the command name (`dev`, `up`, `run`, etc.), and booleans representing whether a flag was passed to the command. You can see the full analytics logic [here](https://github.com/langchain-ai/langgraph/blob/main/libs/cli/langgraph-cli/analytics.py).

You can disable all CLI telemetry by setting `LANGGRAPH_CLI_NO_ANALYTICS=1`.

<a id="in-memory-docker" />

The [Agent Server](/langsmith/agent-server) provides a durable execution runtime that relies on persisting checkpoints of your application state, long-term memories, thread metadata, assistants, and similar resources to the local file system or a database. Unless you have deliberately customized the storage location, this information is either written to local disk (for `langgraph dev`) or a PostgreSQL database (for `langgraph up` and in all deployments).

### LangSmith Tracing

When running the Agent server (either in-memory or in Docker), LangSmith tracing may be enabled to facilitate faster debugging and offer observability of graph state and LLM prompts in production. You can always disable tracing by setting `LANGSMITH_TRACING=false` in your server's runtime environment.

<a id="langgraph-dev" />

### In-memory development server

`langgraph dev` runs an [in-memory development server](/langsmith/local-server) as a single Python process, designed for quick development and testing. It saves all checkpointing and memory data to disk within a `.langgraph_api` directory in the current working directory. Apart from the telemetry data described in the [CLI](#cli) section, no data leaves the machine unless you have enabled tracing or your graph code explicitly contacts an external service.

<a id="langgraph-up" />

### Standalone Server

`langgraph up` builds your local package into a Docker image and runs the server as the [data plane](/langsmith/self-hosted) consisting of three containers: the API server, a PostgreSQL container, and a Redis container. All persistent data (checkpoints, assistants, etc.) are stored in the PostgreSQL database. Redis is used as a pubsub connection for real-time streaming of events. You can encrypt all checkpoints before saving to the database by setting a valid `LANGGRAPH_AES_KEY` environment variable. You can also specify [TTLs](/langsmith/configure-ttl) for checkpoints and cross-thread memories in `langgraph.json` to control how long data is stored. All persisted threads, memories, and other data can be deleted via the relevant API endpoints.

Additional API calls are made to confirm that the server has a valid license and to track the number of executed runs and tasks. Periodically, the API server validates the provided license key (or API key).

If you've disabled [tracing](#langsmith-tracing), no user data is persisted externally unless your graph code explicitly contacts an external service.

[Studio](/langsmith/studio) is a graphical interface for interacting with your Agent Server. It does not persist any private data (the data you send to your server is not sent to LangSmith). Though the Studio interface is served at [smith.langchain.com](https://smith.langchain.com), it is run in your browser and connects directly to your local Agent Server so that no data needs to be sent to LangSmith.

If you are logged in, LangSmith does collect some usage analytics to help improve the debugging user experience. This includes:

* Page visits and navigation patterns
* User actions (button clicks)
* Browser type and version
* Screen resolution and viewport size

Importantly, no application data or code (or other sensitive configuration details) are collected. All of that is stored in the persistence layer of your Agent Server. When using Studio anonymously, no account creation is required and usage analytics are not collected.

In summary, you can opt-out of server-side telemetry by turning off CLI analytics and disabling tracing.

| Variable                       | Purpose                   | Default                |
| ------------------------------ | ------------------------- | ---------------------- |
| `LANGGRAPH_CLI_NO_ANALYTICS=1` | Disable CLI analytics     | Analytics enabled      |
| `LANGSMITH_API_KEY`            | Enable LangSmith tracing  | Tracing disabled       |
| `LANGSMITH_TRACING=false`      | Disable LangSmith tracing | Depends on environment |

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/langsmith/data-storage-and-privacy.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

---

## Define the nodes we will cycle between

**URL:** llms-txt#define-the-nodes-we-will-cycle-between

workflow.add_node(generate_query_or_respond)
workflow.add_node("retrieve", ToolNode([retriever_tool]))
workflow.add_node(rewrite_question)
workflow.add_node(generate_answer)

workflow.add_edge(START, "generate_query_or_respond")

---

## Create a custom LangGraph graph

**URL:** llms-txt#create-a-custom-langgraph-graph

def create_weather_graph():
    workflow = StateGraph(...)
    # Build your custom graph
    return workflow.compile()

weather_graph = create_weather_graph()

---

## ... Define the graph ...

**URL:** llms-txt#...-define-the-graph-...

**Contents:**
- Capabilities
  - Human-in-the-loop
  - Memory
  - Time Travel
  - Fault-tolerance

graph.compile(
    checkpointer=InMemorySaver(serde=JsonPlusSerializer(pickle_fallback=True))
)
python  theme={null}
import sqlite3

from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from langgraph.checkpoint.sqlite import SqliteSaver

serde = EncryptedSerializer.from_pycryptodome_aes()  # reads LANGGRAPH_AES_KEY
checkpointer = SqliteSaver(sqlite3.connect("checkpoint.db"), serde=serde)
python  theme={null}
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from langgraph.checkpoint.postgres import PostgresSaver

serde = EncryptedSerializer.from_pycryptodome_aes()
checkpointer = PostgresSaver.from_conn_string("postgresql://...", serde=serde)
checkpointer.setup()
```

When running on LangSmith, encryption is automatically enabled whenever `LANGGRAPH_AES_KEY` is present, so you only need to provide the environment variable. Other encryption schemes can be used by implementing [`CipherProtocol`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.base.CipherProtocol) and supplying it to [`EncryptedSerializer`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.encrypted.EncryptedSerializer).

### Human-in-the-loop

First, checkpointers facilitate [human-in-the-loop workflows](/oss/python/langgraph/interrupts) workflows by allowing humans to inspect, interrupt, and approve graph steps. Checkpointers are needed for these workflows as the human has to be able to view the state of a graph at any point in time, and the graph has to be to resume execution after the human has made any updates to the state. See [the how-to guides](/oss/python/langgraph/interrupts) for examples.

Second, checkpointers allow for ["memory"](/oss/python/concepts/memory) between interactions. In the case of repeated human interactions (like conversations) any follow up messages can be sent to that thread, which will retain its memory of previous ones. See [Add memory](/oss/python/langgraph/add-memory) for information on how to add and manage conversation memory using checkpointers.

Third, checkpointers allow for ["time travel"](/oss/python/langgraph/use-time-travel), allowing users to replay prior graph executions to review and / or debug specific graph steps. In addition, checkpointers make it possible to fork the graph state at arbitrary checkpoints to explore alternative trajectories.

Lastly, checkpointing also provides fault-tolerance and error recovery: if one or more nodes fail at a given superstep, you can restart your graph from the last successful step. Additionally, when a graph node fails mid-execution at a given superstep, LangGraph stores pending checkpoint writes from any other nodes that completed successfully at that superstep, so that whenever we resume graph execution from that superstep we don't re-run the successful nodes.

Additionally, when a graph node fails mid-execution at a given superstep, LangGraph stores pending checkpoint writes from any other nodes that completed successfully at that superstep, so that whenever we resume graph execution from that superstep we don't re-run the successful nodes.

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/langgraph/persistence.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>

**Examples:**

Example 1 (unknown):
```unknown
#### Encryption

Checkpointers can optionally encrypt all persisted state. To enable this, pass an instance of [`EncryptedSerializer`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.encrypted.EncryptedSerializer) to the `serde` argument of any [`BaseCheckpointSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.base.BaseCheckpointSaver) implementation. The easiest way to create an encrypted serializer is via [`from_pycryptodome_aes`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.encrypted.EncryptedSerializer.from_pycryptodome_aes), which reads the AES key from the `LANGGRAPH_AES_KEY` environment variable (or accepts a `key` argument):
```

Example 2 (unknown):
```unknown

```

---
