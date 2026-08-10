# Iteration manifest v1

Each iteration owns one append-only `iteration-manifest.jsonl` stream. Each line is one node-state event validated independently against [`iteration-manifest-v1.schema.json`](iteration-manifest-v1.schema.json). Never update or delete an event.

One stream contains exactly one `iteration_id`, identifying its pass. `node_id` is stable across attempts of one graph node; `node_kind` identifies its role. `attempt` starts at 1. A `retrying` event retains the failed attempt number, and the following `pending` or `running` event increments it by exactly one. Readers fold events in file order, taking the last event for each `node_id`. `event_id` must be unique within the stream, timestamps must not move backwards, and transitions must be legal. One stable iteration `node_id` owns at most one terminal event, which must be the current final stream event; these ordering and uniqueness rules are runtime invariants rather than schema constraints.

The main orchestrator is the sole writer. Appends use advisory process locking on POSIX and Windows; unsupported platforms fail explicitly rather than writing unlocked. New streams are file-synced and their parent directory is synced where POSIX supports directory sync. It records node transitions, retry decisions, dependencies, routing metadata, artifact paths, errors, and the terminal iteration event. Researchers and callers never write the stream. A single-pass caller stops after observing and verifying a terminal iteration event. A campaign caller may start the next pass only from `completed`, treats `saturated` as evidence for its termination predicate, and stops advancement on `failed` for recovery or operator action.

A node completed in a fan-out wave remains completed when a sibling fails. If its valid result becomes observable during the bounded sibling drain window, append its `completed` event normally even after the sibling's failed event; event timestamps still remain monotonic. Retry transitions apply only to failed, cancelled, or incomplete node IDs. Downstream nodes remain unscheduled until every required dependency is manifest-verified; they may depend on preserved completed siblings plus later successful retries of the failed nodes.

Events carry routing evidence, not routing policy: `harness`, `model`, `thinking`, `routing_rationale`, and `routing_policy_ref` record the decision used. Policy remains external and may change without changing this schema. Artifact paths are relative references beneath the configured artifact root; verification resolves symlinks and rejects any escape. Do not embed notes, claims, source rows, or gap-report contents in events.

Required fields identify the event, iteration, node, state, attempt, observation time, and dependencies. `started_at`, `finished_at`, and `duration_ms` record execution timing when applicable. A failed event requires `error`; a retry decision records `retry_decision` and may include `retry_reason`. Terminal iteration events require `terminal_outcome` and `artifact_paths.gap_report`.

Minimal lifecycle:

```jsonl
{"event_id":"evt-plan-1","iteration_id":"pass-2","node_id":"plan","node_kind":"plan","state":"running","attempt":1,"observed_at":"2026-01-01T00:00:00Z","dependencies":[],"harness":"codex","model":"gpt-5","thinking":"high","routing_rationale":"Planning needs broad synthesis","routing_policy_ref":"autonomous-agents/choose-llm-for-task","started_at":"2026-01-01T00:00:00Z"}
{"event_id":"evt-plan-2","iteration_id":"pass-2","node_id":"plan","node_kind":"plan","state":"completed","attempt":1,"observed_at":"2026-01-01T00:01:00Z","dependencies":[],"artifact_paths":{"plan":"passes/pass-2/plan.json"},"finished_at":"2026-01-01T00:01:00Z","duration_ms":60000}
```

## Error codes

A `failed` event's `error.code` names why, so failures are groupable and the graph stays nameable across passes.

| code | when to use it |
| --- | --- |
| `invalid_node_result` | node result violates the contract and is not repairable |
| `invalid_node_result_format` | node result is malformed but repairable (field names, types, required/extra fields, envelope shape only) |
| `harness_infrastructure` | the harness, launcher, or provider broke, or the process exited without an authoritative node-result.json |
| `provider_empty_termination` | provider returned nothing / terminated empty |
| `nonzero_exit` | process exited non-zero with no more specific cause |
| `timeout` | wall-clock budget exceeded |
| `cancelled` | externally cancelled or blocked |
| `precondition_failed` | a required input or path was rejected before the node ran |

This enum is enforced on the **write path** only, i.e. by `manifest-append`. Readers (`manifest-validate`, `manifest-fold`, `manifest-verify`, `campaign-evaluate`) accept any non-empty string for `error.code`, so historical manifests written before this taxonomy existed keep validating.

Terminal event:

```jsonl
{"event_id":"evt-terminal","iteration_id":"pass-2","node_id":"iteration","node_kind":"iteration","state":"saturated","attempt":1,"observed_at":"2026-01-01T01:00:00Z","dependencies":["merge"],"artifact_paths":{"gap_report":"passes/pass-2/gap-report.md"},"terminal_outcome":"saturated","finished_at":"2026-01-01T01:00:00Z","duration_ms":3600000}
```
