---
name: opencode
description: Delegate coding work to the OpenCode CLI from any agent or harness — one-shot `opencode run` tasks, background TUI sessions, PR reviews, parallel workdirs. Use when asked to use OpenCode, or when you need a provider-agnostic autonomous coding agent to implement, refactor, or review code.
---

# OpenCode CLI

Use [OpenCode](https://opencode.ai) as an autonomous coding worker. OpenCode is a provider-agnostic, open-source AI coding agent with both a TUI and a non-interactive CLI.

This guide is harness-agnostic: everything is a shell command you run with whatever command-execution tool you have.

## When to Use

- The user explicitly asks for OpenCode
- You want an external coding agent to implement/refactor/review code
- You need long-running coding sessions with progress checks
- You want parallel task execution in isolated workdirs/worktrees

## Harness mapping

| Need | Generic form | Typical mappings |
|------|--------------|------------------|
| One-shot run | plain command, no PTY needed | any exec tool |
| Interactive TUI | PTY + background | `pty=true, background=true`, or tmux |
| Poll / read output | process log tool, `tmux capture-pane`, or `tail -f` a log | `process(action="log")` |
| Send a prompt to a live session | write to stdin, or `tmux send-keys` | `process(action="submit", data="…")` |
| Exit | `Ctrl+C` (`\x03`) or kill | `process(action="write", data="\x03")` |

**tmux is the portable fallback** — every interactive pattern below works through tmux alone.

## Prerequisites

- OpenCode installed: `npm i -g opencode-ai@latest` or `brew install anomalyco/tap/opencode`
- Auth configured: `opencode auth login`, or provider env vars (`OPENROUTER_API_KEY`, etc.)
- Verify: `opencode auth list` shows at least one provider
- Git repository for code tasks (recommended)
- A PTY for interactive TUI sessions (`opencode run` does **not** need one)

## Binary Resolution (Important)

Shell environments may resolve different OpenCode binaries. If behavior differs between your own terminal and the agent's, check:

```bash
which -a opencode
opencode --version
```

If needed, pin an explicit binary path:

```bash
cd ~/project && "$HOME/.opencode/bin/opencode" run '...'
```

## One-Shot Tasks

Use `opencode run` for bounded, non-interactive tasks:

```bash
cd ~/project && opencode run 'Add retry logic to API calls and update tests'
```

Attach context files with `-f`:

```bash
cd ~/project && opencode run 'Review this config for security issues' -f config.yaml -f .env.example
```

Show model thinking with `--thinking`:

```bash
cd ~/project && opencode run 'Debug why tests fail in CI' --thinking
```

Force a specific model:

```bash
cd ~/project && opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4
```

## Interactive Sessions (Background)

For iterative work requiring multiple exchanges, start the TUI in the background with a PTY:

```bash
# With harness flags: run `opencode` in ~/project with background + pty
cd ~/project && opencode

# Portable equivalent with tmux
tmux new-session -d -s oc -x 140 -y 40
tmux send-keys -t oc 'cd ~/project && opencode' Enter

# Send a prompt (Enter may need pressing twice: once to finalize, once to send)
sleep 4 && tmux send-keys -t oc 'Implement OAuth refresh flow and add tests' Enter

# Monitor progress
tmux capture-pane -t oc -p -S -80

# Follow-up
tmux send-keys -t oc 'Now add error handling for token expiry' Enter

# Exit cleanly — Ctrl+C
tmux send-keys -t oc C-c
tmux kill-session -t oc
```

If your harness has a process tool: `submit` prompts, `poll`/`log` for progress, `write` `\x03` or `kill` to exit.

**Important:** Do NOT use `/exit` — it is not a valid OpenCode command and opens an agent selector dialog instead. Use Ctrl+C (`\x03`) or kill the process.

### TUI Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Submit message (press twice if needed) |
| `Tab` | Switch between agents (build/plan) |
| `Ctrl+P` | Open command palette |
| `Ctrl+X L` | Switch session |
| `Ctrl+X M` | Switch model |
| `Ctrl+X N` | New session |
| `Ctrl+X E` | Open editor |
| `Ctrl+C` | Exit OpenCode |

### Resuming Sessions

After exiting, OpenCode prints a session ID. Resume with:

```bash
cd ~/project && opencode -c              # continue last session
cd ~/project && opencode -s ses_abc123   # specific session
```

(Both are TUI sessions — run them backgrounded with a PTY.)

## Common Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `--continue` / `-c` | Continue the last OpenCode session |
| `--session <id>` / `-s` | Continue a specific session |
| `--agent <name>` | Choose OpenCode agent (build or plan) |
| `--model provider/model` | Force specific model |
| `--format json` | Machine-readable output/events |
| `--file <path>` / `-f` | Attach file(s) to the message |
| `--thinking` | Show model thinking blocks |
| `--variant <level>` | Reasoning effort (high, max, minimal) |
| `--title <name>` | Name the session |
| `--attach <url>` | Connect to a running opencode server |

## Procedure

1. Verify tool readiness: `opencode --version`, `opencode auth list`.
2. For bounded tasks, use `opencode run '...'` (no PTY needed).
3. For iterative tasks, start `opencode` backgrounded with a PTY.
4. Monitor long tasks via process logs or `tmux capture-pane`.
5. If OpenCode asks for input, respond by writing to stdin / `send-keys`.
6. Exit with Ctrl+C (`\x03`) or by killing the process.
7. Summarize file changes, test results, and next steps back to the user.

## PR Review Workflow

OpenCode has a built-in PR command:

```bash
cd ~/project && opencode pr 42
```

Or review in a temporary clone for isolation:

```bash
REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git "$REVIEW" && cd "$REVIEW" \
  && opencode run 'Review this PR vs main. Report bugs, security risks, test gaps, and style issues.' \
       -f $(git diff origin/main --name-only | head -20 | tr '\n' ' ')
```

## Parallel Work Pattern

Use separate workdirs/worktrees to avoid collisions:

```bash
cd /tmp/issue-101 && opencode run 'Fix issue #101 and commit'   # backgrounded
cd /tmp/issue-102 && opencode run 'Add parser regression tests and commit'   # backgrounded
```

Then poll each run's log (or tmux pane) until both finish.

## Session & Cost Management

```bash
opencode session list
opencode stats
opencode stats --days 7 --models anthropic/claude-sonnet-4
```

## Pitfalls

- Interactive `opencode` (TUI) sessions require a PTY. `opencode run` does NOT.
- `/exit` is NOT a valid command — it opens an agent selector. Use Ctrl+C to exit the TUI.
- PATH mismatch can select the wrong OpenCode binary/model config.
- If OpenCode appears stuck, inspect logs before killing it.
- Avoid sharing one working directory across parallel OpenCode sessions.
- Enter may need to be pressed twice to submit in the TUI (once to finalize text, once to send).

## Verification

Smoke test:

```bash
opencode run 'Respond with exactly: OPENCODE_SMOKE_OK'
```

Success criteria:
- Output includes `OPENCODE_SMOKE_OK`
- Command exits without provider/model errors
- For code tasks: expected files changed and tests pass

## Rules

1. Prefer `opencode run` for one-shot automation — simpler, no PTY.
2. Use interactive background mode only when iteration is needed.
3. Always scope OpenCode sessions to a single repo/workdir.
4. For long tasks, provide progress updates from the logs.
5. Report concrete outcomes (files changed, tests, remaining risks).
6. Exit interactive sessions with Ctrl+C or kill, never `/exit`.
