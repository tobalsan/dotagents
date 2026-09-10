---
name: ralph-loop
description: Run a fresh-context iteration loop — one agent call per pass, working only from durable `.ralph/` files — as a deterministic wfe workflow. Use when the user asks for a "ralph loop", "fresh-context loop", to "keep iterating until tests pass", or wants a long autonomous coding task carried out over many independent passes ("set up a ralph loop for X", "ralph this until the tests pass"). NOT for one-shot edits or anything that fits in a single agent turn — use a normal agent call for those.
---

# Ralph Loop

## Core invariant

Every iteration runs in a fresh agent context (a separate `agent()` call, a fresh
subprocess); nothing carries over except durable files. Work from durable files only, never
chat history: `.ralph/<name>.md` (task), `.ralph/<name>.state.json` (loop state — the resume
truth), `.ralph/<name>.reflection.md` (rolling notes each iteration reads first).

## Layout

`WORKDIR` is the project repo the child edits — passed as `--workdir`. `--campaign
WORKDIR/.ralph` is both the engine's state dir (`runs/`, `routes.json`) and the durable ralph
files' home.

## Before the first run

Write `.ralph/<name>.md` yourself — the workflow never creates a placeholder. Use this
template (from the ported Pi extension):

```markdown
# Task

## Goal
Describe target outcome.

## Checklist
- [ ] First concrete item
- [ ] Second concrete item

## Verification
command: npm test

## Commit
Commit only when task file explicitly says to.

## Notes
Update as work proceeds.
```

Build `routes.json` with one route, `worker`, chosen with
`autonomous-agents/choose-llm-for-task`; present the pick (harness, model) and wait for the
user's confirmation before dispatching.

## Run it

```bash
uv run --project /Users/thinh/dotagents/workflow-engine wfe run \
  /Users/thinh/dotagents/skills/agentic-workflow-graphs/ralph-loop/workflow.py \
  --campaign WORKDIR/.ralph --workdir WORKDIR \
  --arg name=<loop-name> --arg max_iterations=50 --timeout 2700
```

`--timeout` is the per-iteration ceiling in seconds; the engine default (900) is often too
low for a real coding pass. `--arg` values: `name` (required, sanitized to `[a-zA-Z0-9_-]`),
`max_iterations` (default 50, `0` means unlimited).

## Status / resume / stop

```bash
uv run --project /Users/thinh/dotagents/workflow-engine wfe status WORKDIR/.ralph/runs/<run_id>
```

Ask the user whether to also launch the live dashboard —
`uv run --project /Users/thinh/dotagents/workflow-engine wfe watch --campaign WORKDIR/.ralph`
(background it) — and report the URL it prints (default `http://127.0.0.1:8799/`).

Rerunning the exact same `wfe run` command resumes: a paused loop picks up from
`.ralph/<name>.state.json`'s stored iteration — equivalent to the Pi extension's `/ralph
resume`. Ctrl-C stops a run; the engine journals it `interrupted` and the state file stays
whatever it last was (`active` or `paused`), so the next `wfe run` continues it.

## Completion rule

The loop completes only when both are true: the child emits `<promise>COMPLETE</promise>`
**and** the task file's verification command exits 0. If the marker appears but verification
fails, the loop continues into the next fresh iteration with the failure recorded in
`.ralph/<name>.reflection.md`. `<promise>PAUSE</promise>` pauses immediately regardless of
`COMPLETE` — pause always wins when both markers appear.

## Harness write permissions

Harness defaults allow the child to edit files and run verification commands inside the
engine-controlled `WORKDIR`: Codex uses `workspace-write`; Claude uses `acceptEdits`;
OpenCode adds `--auto` (no need to repeat it in `extra_flags`). Only Codex has an OS/process
sandbox selector — Claude's and OpenCode's `WORKDIR` is an intended workspace, not OS
confinement; either may write outside it under tool permissions. Never add Codex's sandbox
bypass/`--yolo` flags or Claude's skip-permission flags. See `workflow-engine/DESIGN.md` for
the full adapter list and verified argv.
