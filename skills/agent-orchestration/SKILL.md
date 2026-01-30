---
name: agent-orchestration
description: |
  Orchestrate coding agents via tmux for software engineering tasks. Use when dispatching subagents to work on issues, implementing features across repos, or coordinating multi-agent workflows. Covers: tmux session management, agent selection (Claude Code, Codex, Droid, Pi), and Linear project integration.
---

# Agent Orchestration

## Prerequisites

1. Register with amsg communication hub if `.amsg-info` doesn't exist
2. Read `../../../../repos.json` for available repos and working directories (single source of truth)
3. Read `./../../../agent-config.json` for agent profiles and recurring task commands

## Dispatching Agents

Use the `tmux` skill to dispatch agents. Always specify working directory with `-c` flag.

When dispatching with free-form prompts (not slash commands), explicitly instruct agents to post updates on relevant Linear issues describing actions and outcomes.

## Socket Path

TMPDIR varies between Bash invocations. On first session creation, **always print the full socket path** so it's in conversation history for later reuse:

```bash
SOCKET_DIR="${TMPDIR:-/tmp}/claude-tmux-sockets"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/claude.sock"
echo "SOCKET=$SOCKET"  # Print for conversation history
```

## Task Workflow

1. **Complex tasks**: First dispatch investigator agent to understand codebase/problem
2. **Non-trivial tasks**: Dispatch PRP creation agent (`/task-prp-create <issue>`) before implementation
3. **Implementation**: Only after PRP exists, dispatch (`/task-prp-execute <issue>`)

Never dispatch `/task-prp-execute` directly without existing PRP.

## Agent Selection

See [references/agents.md](references/agents.md) for detailed agent specs and launch commands.

**Quick reference:**

| Agent | Best For | Launch |
|-------|----------|--------|
| Claude Code (haiku) | Simple analysis, low-complexity | `claude "<prompt>" --model haiku` |
| Claude Code (sonnet) | Everyday tasks | `claude "<prompt>" --model sonnet` |
| Claude Code (opus) | Complex, difficult tasks | `claude "<prompt>" --model opus` |
| Codex | Deep reasoning, fast coding | `codex "<prompt>"` |
| Droid | Interactive model/mode selection | `droid` (then configure) |
| Pi | Multi-provider flexibility | `pi "<prompt>"` |

**Permission flags are critical** - always use proper flags to enable agents to work without permission prompts.

## Linear Integration

Use `linctl` CLI for project management:
- `linctl issue list --team ENG` - List issues
- `linctl issue get LIN-123` - Get issue details
- `linctl comment create LIN-123 --body "..."` - Post updates
