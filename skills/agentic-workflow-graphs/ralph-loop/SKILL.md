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

Requires `wfe` on PATH. If `wfe --help` fails, install the engine as a uv tool:
`uv tool install <path to workflow-engine>` (the `workflow-engine` directory that ships
alongside `skills/` in this repo).

```bash
wfe run \
  <path to the ralph-loop skill>/workflow.py \
  --campaign WORKDIR/.ralph --workdir WORKDIR \
  --arg name=<loop-name> --arg max_iterations=50 --timeout 2700
```

`--timeout` is the per-iteration ceiling in seconds; the engine default (900) is often too
low for a real coding pass. `--arg` values: `name` (required, sanitized to `[a-zA-Z0-9_-]`),
`max_iterations` (default 50, `0` means unlimited), `pause_threshold` (default 3 — see
Completion rule below).

## Status / resume / stop

```bash
wfe status WORKDIR/.ralph/runs/<run_id>
```

Ask the user whether to also launch the live dashboard —
`wfe watch --campaign WORKDIR/.ralph`
(background it) — and report the URL it prints (default `http://127.0.0.1:8799/`).

Rerunning the exact same `wfe run` command resumes: a paused loop picks up from
`.ralph/<name>.state.json`'s stored iteration — equivalent to the Pi extension's `/ralph
resume`. Ctrl-C stops a run; the engine journals it `interrupted` and the state file stays
whatever it last was (`active` or `paused`), so the next `wfe run` continues it.

## Completion rule

The loop completes only when both are true: the child emits `<promise>COMPLETE</promise>`
**and** the task file's verification command exits 0. If the marker appears but verification
fails, the loop continues into the next fresh iteration with the failure recorded in
`.ralph/<name>.reflection.md`. Within a single iteration's directive, pause still wins if both
markers appear.

A single blocked iteration (`<promise>PAUSE</promise>` or a harness error) no longer stops the
loop: it's recorded in the reflection with a note for the next iteration to diagnose and
retry, and the loop continues with a fresh context. The loop only pauses after
`pause_threshold` consecutive blocked iterations (default 3, `--arg pause_threshold=N`;
`pause_threshold=1` restores immediate pause on the first block). A productive iteration
(continue or complete) resets the streak to zero.

## Harness write permissions

Harness defaults allow the child to edit files and run verification commands inside the
engine-controlled `WORKDIR`: Codex uses `workspace-write`; Claude uses `acceptEdits`;
OpenCode adds `--auto` (no need to repeat it in `extra_flags`). Only Codex has an OS/process
sandbox selector — Claude's and OpenCode's `WORKDIR` is an intended workspace, not OS
confinement; either may write outside it under tool permissions. Never add Codex's sandbox
bypass/`--yolo` flags or Claude's skip-permission flags. See `workflow-engine/DESIGN.md` for
the full adapter list and verified argv.
