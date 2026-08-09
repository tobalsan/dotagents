# Node execution v1

This contract is the harness-neutral seam between routing and graph execution. It defines one node attempt, not a dispatcher or harness command. After `autonomous-agents/choose-llm-for-task` selects a harness, the orchestrator **must load and follow** that harness's skill (`autonomous-agents/codex`, `autonomous-agents/claude-code`, `autonomous-agents/opencode`, or the corresponding selected harness skill). Harness-specific invocation, authentication, and sandbox rules belong there.

## Input envelope

Validate the input against the `input` definition in [`node-execution-v1.schema.json`](node-execution-v1.schema.json). It contains:

- stable `iteration_id`, `node_id`, manifest-aligned `node_kind`, optional research `lane`, and 1-based `attempt`;
- one bounded `goal` and dependency node IDs plus their result artifact paths;
- read-only campaign-state paths. Workers may read but never modify these paths;
- one isolated `output_dir`, unique to the node attempt. All worker-created files, including the result artifact, stay beneath it;
- relevant retrieval skill names the worker must load and follow when applicable;
- explicit timeout, campaign-wide concurrency ceiling, and optional budget limits.

The orchestrator supplies only dependencies whose manifest state permits this node to run. Together, dependency result paths and campaign-state paths are the attempt's exact readable-path allowlist; workspace reconnaissance and undeclared reads are forbidden. Prior-attempt paths are denied by default and appear only when explicitly declared as dependencies. Input paths are artifact-root-relative, must not escape that root after symlink resolution, and must not overlap `output_dir`. Reusing a directory across nodes or attempts is forbidden.

## Execution

One invocation performs one bounded pass toward `goal`; it does not create more agents or schedule retries. It may read only declared dependency artifacts and campaign state, then writes only inside `output_dir`. Researchers hand off candidate sources and citations; they do not write the source ledger. Merge remains the ledger's only writer.

Routing does not complete execution: after routing, load the selected autonomous-agent skill and obey its process, timeout, and cleanup guidance. Launch from the smallest common ancestor containing approved inputs and the campaign-local output directory. Do not configure a harness single-output override; stdout and stderr are diagnostic streams, while node-owned artifacts remain authoritative. The orchestrator enforces `timeout_seconds`, `max_concurrency`, and budget limits.

A sibling failure closes scheduling, not successful sibling results. For attempts already running when a sibling fails, record one bounded drain deadline. At the deadline, take one atomic orchestration snapshot of each sibling's process state, exit code, and result presence. Validate and accept every zero-exit `completed` result visible in that snapshot, and retain valid retryable checkpoints for retry classification. Only after that snapshot and validation may the orchestrator mark cancellation observed for attempts still unfinished, request termination, wait a bounded grace period, then terminate their full owned process trees and reap them. A result accepted from the cutoff snapshot remains `completed`; do not relabel or discard it because another node failed. Results first appearing after the cutoff are partial diagnostics, not successful outputs. Never kill unrelated processes. Partial artifacts may remain for diagnosis but are not successful outputs.

Environment and secrets are least-privilege inputs owned by the orchestrator. Pass only values required by the selected harness and node. Never place secrets in prompts, envelopes, artifacts, citations, stdout, manifests, or error text; redact accidental exposure before persistence. Workers must not inspect unrelated environment variables or credential stores.

## Result artifact

Worker writes exactly one result at `output_dir/node-result.json`, validated against the `result` definition in the schema. A result supplied from any other path is invalid, even when its contents match. This file is the authoritative handoff; stdout and process exit alone are never authoritative. Result identity and `attempt` must equal input. Artifact paths and citation handoffs are relative, durable references beneath `output_dir`; source handoffs include canonical ID when known, URL, title when known, and citation pointers or artifact paths supporting use downstream. Every `citation_id` must be unique across the result, every citation's `source_url` must equal at least one entry in `sources[].url`, and every ID in a source's `citation_ids` must resolve to exactly one entry in `citations` whose `source_url` equals that source's `url`. Draft-07 JSON Schema cannot express these cross-array invariants, so the orchestrator must enforce them at runtime before accepting the result.

Statuses:

- `completed`: goal finished and declared artifacts/citations exist and validate.
- `retryable`: attempt did not finish, but another attempt may reasonably succeed; include an error and retry reason.
- `failed`: non-retryable attempt failure; include an error.
- `cancelled`: orchestrator cancellation or timeout stopped work; include an error whose code distinguishes cancellation from timeout.

Exit classification is deterministic, in this precedence order:

1. Cancellation or deadline observed by the orchestrator classifies `cancelled`, even when the result is missing, unreadable, identity-mismatched, or schema-invalid.
2. Otherwise, a missing, unreadable, identity-mismatched, or schema-invalid result is `failed` at orchestration level, regardless of exit code; infrastructure policy decides whether to retry.
3. Valid `completed` plus zero exit is success. Valid `completed` plus nonzero exit is `failed` because completion is inconsistent.
4. Valid `retryable`, `failed`, or `cancelled` remains that status regardless of exit code; record nonzero exit metadata without replacing worker error.

Before accepting `completed`, orchestrator runs `scripts/validate_node_result.py` (or an equivalent stricter validator), verifies every declared artifact and citation path exists and remains in `output_dir` after symlink resolution, and checks retained outputs for secrets. An artifact labeled `counts` may expose machine-readable JSON counts for sources, citations, and artifacts; validators compare only those explicit fields and never infer counts from prose. stdout may be retained as diagnostic data only.

## Attempts and manifest mapping

`iteration_id` and `node_id` are stable; each retry increments `attempt` exactly once and gets a fresh `output_dir`. An attempt must be safe to repeat from unchanged read-only inputs. Existing attempt output is never silently overwritten or treated as current. Side effects outside `output_dir` are prohibited, making single-pass invocation and replay idempotent at campaign-state boundary. `scripts/prepare_retry.py` may prepare a fresh envelope and non-authoritative event templates from an exact readable allowlist; it never appends to the manifest.

Orchestrator is sole iteration-manifest writer and maps result to [`iteration-manifest-v1.md`](iteration-manifest-v1.md):

| Node result | Manifest event(s) |
| --- | --- |
| `completed` | append node `completed` with same identity/attempt and accepted paths in `artifact_paths` |
| `retryable` | append node `failed` with `retry_decision: retry` and `retry_reason`, then `retrying`; next `pending`/`running` uses attempt + 1 |
| `failed` | append node `failed` with `retry_decision: do_not_retry` |
| `cancelled` | append node `failed`; policy chooses `retry` or `do_not_retry`, recording cancellation/timeout in `error` and reason |

Manifest `node_kind`, dependencies, routing evidence, timing, and errors come from orchestration evidence plus this artifact; result never writes manifest events. Iteration terminal states remain `completed`, `saturated`, or `failed` and are not node-result statuses.
