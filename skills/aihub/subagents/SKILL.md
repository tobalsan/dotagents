---
name: subagents
description: Use AIHub's `aihub subagents` CLI to start, list, monitor, resume, interrupt, archive, unarchive, and delete project-agnostic CLI subagent runs. Use when an agent needs to delegate work to Codex, Claude, or Pi through AIHub, observe running subagents, manage subagent lifecycle, or scope subagents to a chat/board/project parent.
---

# AIHub Subagents

Use `aihub subagents ...` to delegate work through the AIHub subagents runtime. The gateway must be running; all commands talk to the gateway HTTP API.

In dev worktrees, `aihub` may not be installed system-wide. Run it through the worktree package script:

```sh
cd /path/to/aihub-worktree && pnpm aihub subagents list --json
```

## Core Rules

- Use the shell CLI first: `aihub subagents ...`, or `cd <worktree> && pnpm aihub subagents ...` in development.
- Always pass an existing `--cwd`; runtime only checks that it exists.
- Use `--json` when parsing output programmatically.
- Use `--parent` to keep runs visible in the right UI scope.
- Do not resume an active run; interrupt or wait first.
- Prefer `interrupt` over `delete` when stopping work you may inspect later.

## Parent Scopes

Parent format is `<type>:<id>`.

Common scopes:

```text
agent-session:<agentId>:<sessionKey>
board:<boardId>
projects:<projectId>
```

Use `agent-session:<agentId>:<sessionKey>` when delegating from a chat so the chat/Board monitor can show only that session's subagents.

## Start

Minimum direct start:

```sh
aihub subagents start \
  --cli codex \
  --cwd /path/to/repo \
  --label worker-a \
  --prompt "Implement the task"
```

Start with model controls:

```sh
aihub subagents start \
  --cli codex \
  --cwd /path/to/repo \
  --label reviewer-a \
  --model gpt-5.3-codex \
  --reasoning-effort high \
  --prompt "Review the current diff"
```

Start with a parent:

```sh
aihub subagents start \
  --cli claude \
  --cwd /path/to/repo \
  --label docs-worker \
  --parent agent-session:lead:main \
  --prompt "Draft API docs for this change"
```

Start from a configured profile:

```sh
aihub subagents start \
  --profile Worker \
  --cwd /path/to/repo \
  --label worker-b \
  --prompt "Add tests for the billing flow"
```

## Monitor

List running runs:

```sh
aihub subagents list --status running
```

List runs for one parent:

```sh
aihub subagents list --parent agent-session:lead:main
```

Get one run:

```sh
aihub subagents status <runId>
```

Read logs:

```sh
aihub subagents logs <runId> --since 0
```

For polling loops, prefer JSON:

```sh
aihub subagents list --parent agent-session:lead:main --json
aihub subagents status <runId> --json
```

## Manage

Resume a completed/interrupted run:

```sh
aihub subagents resume <runId> \
  --prompt "Continue with the remaining failures"
```

Stop an active process but keep the record:

```sh
aihub subagents interrupt <runId>
```

Hide a run from normal lists:

```sh
aihub subagents archive <runId>
```

Restore an archived run:

```sh
aihub subagents unarchive <runId>
```

Remove the run directory:

```sh
aihub subagents delete <runId>
```

## Delegation Pattern

1. Choose `cwd` and parent scope.
2. Start the run with a clear `--label` and prompt.
3. Capture the returned `runId`.
4. Poll `status` or `list --json`.
5. Read `logs` for details or latest output.
6. `resume` only after status is terminal.
7. `interrupt` if the run should stop early.

Example:

```sh
RUN_JSON=$(aihub subagents start \
  --cli codex \
  --cwd "$PWD" \
  --label worker-a \
  --parent agent-session:lead:main \
  --prompt "Implement the narrow task and report results" \
  --json)

RUN_ID=$(printf '%s' "$RUN_JSON" | jq -r '.id')
aihub subagents status "$RUN_ID" --json
aihub subagents logs "$RUN_ID" --since 0
```

## Output Expectations

Human output is compact by default. `--json` returns machine-readable data containing fields like:

```json
{
  "id": "sar_...",
  "label": "worker-a",
  "cli": "codex",
  "status": "running",
  "parent": { "type": "agent-session", "id": "lead:main" },
  "latestOutput": "..."
}
```

Statuses:

```text
starting | running | done | error | interrupted
```
