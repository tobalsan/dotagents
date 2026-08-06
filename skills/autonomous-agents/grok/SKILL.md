---
name: grok
description: Delegate coding work to the Grok Build CLI from any agent or harness — one-shot headless `grok -p` runs, multi-turn tmux TUI sessions, PR reviews, parallel worktree workers. Use when asked to hand a feature, refactor, bug fix, or code review to Grok, or when you need an autonomous xAI coding subprocess that can read, edit, run commands, and manage git.
---

# Grok Build — Orchestration Guide

Delegate coding tasks to [Grok Build](https://x.ai) (`grok`), xAI's autonomous coding agent CLI. Grok reads files, writes code, runs shell commands, spawns subagents, searches the web, and manages git workflows.

This guide is harness-agnostic: everything is a shell command you run with whatever command-execution tool you have.

Local docs (installed with the binary): `~/.grok/docs/user-guide/` — especially `14-headless-mode.md`, `15-agent-mode.md`, `18-sandbox.md`, `22-permissions-and-safety.md`.

## Harness mapping

| Need | Generic form | Typical mappings |
|------|--------------|------------------|
| Run a command in a directory | `cd <dir> && <cmd>` or `grok --cwd <dir> …` | shell/exec tool with `cwd`/`workdir` |
| One-shot headless run | plain command, no PTY needed | any exec tool |
| Long background run | background flag, or `nohup … > /tmp/run.log 2>&1 &`, or tmux | `background=true`, `run_in_background` |
| Drive interactive TUI | tmux `send-keys` / `capture-pane` | PTY-capable exec, or tmux |
| Poll / read output | process log, `tmux capture-pane`, or `tail` a log | `process(action="log")` |
| Stop it | kill process or `tmux kill-session` | `process(action="kill")` |

**tmux is the portable fallback** for interactive TUI. Headless mode (`-p`) needs no PTY.

## Prerequisites

- **Install:** `curl -fsSL https://x.ai/cli/install.sh | bash` (binary lands in `~/.grok/bin/grok`)
- **Version:** `grok --version` (this skill targets the current Grok Build CLI, v0.2+)
- **Update:** `grok update`
- **Auth (pick one):**
  - Browser OAuth: `grok login` → credentials in `~/.grok/auth.json`
  - Headless/remote: `grok login --device-auth` (alias `--device-code`)
  - CI/API key: `export XAI_API_KEY="xai-..."` (from [console.x.ai](https://console.x.ai))
- **Health:** `grok doctor`
- **Models:** `grok models` — list available model IDs for the current auth

OAuth/API credentials live under the invoking user's `HOME` / `GROK_HOME`. If the harness rewrites `HOME` or runs as another user, auth looks missing — verify before blaming the task.

Pin the binary if PATH differs across environments:

```bash
which -a grok
GROK_BIN="${GROK_BIN:-$(command -v grok)}"
"$GROK_BIN" --version
```

## Two Orchestration Modes

### Mode 1: Headless (`-p` / `--single`) — PREFERRED for most tasks

One-shot (or resumed) non-interactive run. Prints the result, exits. No PTY. Best for automation.

```bash
cd /path/to/project && grok -p 'Add error handling to all API calls in src/' \
  --always-approve --max-turns 20
```

**When to use headless:**
- One-shot coding tasks (fix, feature, refactor, review)
- CI/CD and scripting
- Structured JSON / schema output
- Parallel workers (one process per worktree)
- Any task that does not need a live multi-turn TUI

Also triggers headless: `--prompt-file <path>`, `--prompt-json <json>`.

### Mode 2: Interactive TUI via tmux — Multi-turn sessions

Full conversational TUI for follow-ups, slash commands, and live monitoring. Needs a PTY; tmux is reliable.

```bash
tmux new-session -d -s grok-work -x 140 -y 40
tmux send-keys -t grok-work 'cd /path/to/project && grok --always-approve' Enter
sleep 4 && tmux send-keys -t grok-work 'Refactor the auth module to use JWT tokens' Enter
sleep 20 && tmux capture-pane -t grok-work -p -S -60
tmux send-keys -t grok-work 'Now add unit tests for the new JWT code' Enter
# Exit
tmux send-keys -t grok-work '/quit' Enter
tmux kill-session -t grok-work
```

Initial prompt without waiting for the composer:

```bash
cd /path/to/project && grok --always-approve 'Refactor the auth module to use JWT'
```

**When to use interactive:**
- Multi-turn iterative work
- Human-in-the-loop decisions
- Slash commands (`/compact`, `/review`, `/model`, `/dashboard`)
- Exploratory sessions

## Headless Deep Dive

### Basic patterns

```bash
# Plain text result (default)
cd ~/project && grok -p 'Summarize the architecture of src/' --always-approve

# Cap agentic loops
cd ~/project && grok -p 'Fix failing tests' --always-approve --max-turns 15

# Working directory without cd
grok -p 'Run make test and fix failures' --cwd ~/project --always-approve

# Prompt from file / verbatim
grok --prompt-file ./task.md --always-approve
grok -p "$(cat task.md)" --verbatim --always-approve
```

### JSON output (scripting)

```bash
cd ~/project && grok -p 'List security issues in auth/' \
  --output-format json --always-approve --max-turns 10 > /tmp/grok-out.json

jq -r '.text' /tmp/grok-out.json
jq -r '.sessionId' /tmp/grok-out.json
jq '.usage, .total_cost_usd, .num_turns, .stopReason' /tmp/grok-out.json
```

Success object includes `text`, `stopReason`, `sessionId`, `num_turns`, `usage`, `modelUsage`, and cost fields when the server reports them. On failure: non-zero exit and/or `{"type":"error","message":"..."}`.

**Cost caveats:** `total_cost_usd` may be absent (unreported ≠ free). When partial, cost floats are omitted and `cost_is_partial` / `usage_is_incomplete` may be set. Prefer `total_cost_usd_ticks` for exact reconciliation when present.

### Streaming JSON

```bash
# Native ACP-shaped NDJSON
grok -p 'Explain src/main' --output-format streaming-json --always-approve \
  | jq -rj 'select(.type=="text") | .data'

# Messages API wire format (Claude-compatible consumers)
grok -p 'Explain src/main' --output-format streaming-messages-json --always-approve
```

`streaming-json` event types include: `text`, `thought`, `tool_call`, `tool_call_update`, `usage`, `plan`, `end`, `error`. Always ends with `end` (or `error`).

### Structured output (`--json-schema`)

```bash
cd ~/project && grok -p 'List all exported functions in src/' \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}' \
  --always-approve --max-turns 8
```

Implies `--output-format json`. Parse structured fields from the result.

### Session continuation

```bash
# Start and capture session id
SID=$(cd ~/project && grok -p 'Start refactoring the DB layer' \
  --output-format json --always-approve --max-turns 12 | jq -r '.sessionId')

# Resume by id
cd ~/project && grok -p 'Add connection pooling' --resume "$SID" \
  --always-approve --max-turns 10

# Most recent session in this directory
cd ~/project && grok -p 'What did you change last?' -c --always-approve --max-turns 3

# Fork on resume (new id, keep history)
cd ~/project && grok -p 'Try a different approach' --resume "$SID" \
  --fork-session --always-approve --max-turns 10

# Client-chosen UUID for a brand-new session only (must not exist)
cd ~/project && grok -p 'hello' \
  --session-id "$(uuidgen | tr '[:upper:]' '[:lower:]')" \
  --output-format json --always-approve
```

**`-s/--session-id` does not resume.** It only names a **new** UUID session. Resume with `-r/--resume` or `-c/--continue`. With `-r`/`-c`, `-s` is only valid together with `--fork-session`.

### Context via command substitution (not stdin)

Headless does **not** read piped stdin into the prompt. Inject content explicitly:

```bash
grok -p "Review this diff:

$(git diff main...HEAD)" --always-approve --max-turns 5

grok -p "Review staged changes:

$(git diff --staged)" --always-approve --output-format json
```

### Tool allow/deny lists (headless-only)

Internal tool IDs (not Claude-style `Read`/`Bash`). Common: `read_file`, `search_replace`, `grep`, `list_dir`, `web_search`, `web_fetch`, `todo_write`, `spawn_subagent`. Shell ID is documented as both `run_terminal_cmd` (headless examples) and `run_terminal_command` (hooks/TUI) — if a filter errors, try the other.

```bash
# Read-only review
grok -p 'Explain this codebase' --tools 'read_file,grep,list_dir' --always-approve

# No shell, no web
grok -p 'Review auth for bugs' \
  --disallowed-tools 'run_terminal_command,web_search,web_fetch' --always-approve

# Block all subagents, or one type
grok -p 'Fix this bug' --disallowed-tools 'Agent' --always-approve
grok -p 'Refactor' --disallowed-tools 'Agent(explore)' --always-approve
```

When both are set, `--disallowed-tools` wins. MCP meta-tools stay available unless denied.

### Permission rules (`--allow` / `--deny`)

Leave tools installed but gate invocations. Syntax: `Prefix(glob)`.

| Prefix | Controls |
|--------|----------|
| `Bash(...)` | Shell commands (`*` matches freely) |
| `Edit(...)` / `Write(...)` / `Read(...)` / `Grep(...)` | Path globs (`*` one level, `**` recursive) |
| `WebFetch(...)` | URL / `domain:host` |
| `MCPTool(...)` | MCP tool names |

```bash
grok -p 'Set up the project' --always-approve \
  --allow 'Bash(npm*)' --deny 'Bash(sudo*)' --deny 'Bash(rm -rf *)'
```

Deny beats allow. Deny/hooks still apply under `--always-approve`.

## Always-approve & permission modes

For automation, **always pass `--always-approve`** (alias `--yolo`, same as `--permission-mode bypassPermissions`). Without it, headless runs can stall on permission prompts.

| Mode | Behavior | Best for |
|------|----------|----------|
| `default` (ask) | Prompts on writes/shell | Interactive TUI |
| `acceptEdits` | Auto file edits | Local coding |
| `auto` | Safety-checked auto; blocks escalate | Fewer TUI prompts |
| `dontAsk` | Only pre-approved / read-only | Strict CI allowlists |
| `bypassPermissions` | Auto tools (`--always-approve`) | Scripts, CI, workers |
| `plan` | Compat; prefer real plan mode | Claude settings compat |

```bash
grok -p 'Run tests and fix failures' --always-approve
grok -p 'Run tests and fix failures' --yolo          # identical
grok -p '…' --permission-mode dontAsk --allow 'Bash(npm test*)'
```

Interactive toggles: `Ctrl+O` or `/always-approve`; `Shift+Tab` cycles modes.

## Complete CLI flags (orchestration-relevant)

### Session & environment
| Flag | Effect |
|------|--------|
| `-p, --single <PROMPT>` | Headless one-shot; print and exit |
| `--prompt-file <PATH>` | Headless prompt from file |
| `--prompt-json <JSON>` | Headless prompt as JSON content blocks |
| `-c, --continue` | Resume most recent session for cwd |
| `-r, --resume [ID_OR_TITLE]` | Resume by id/title (omit = most recent) |
| `-s, --session-id <UUID>` | **New** session UUID only (not resume) |
| `--fork-session` | On resume/continue, new id keeping history |
| `--cwd <PATH>` | Working directory |
| `--restore-code` | On resume, check out original session commit |
| `-w, --worktree [NAME]` | New git worktree for the session |
| `--worktree-ref <REF>` / `--ref` | Base ref for worktree (default: current HEAD) |
| `--verbatim` | Send prompt exactly as given |
| `--no-plan` | Disable plan mode |
| `--no-subagents` | Disable subagent spawning |
| `--experimental-memory` / `--no-memory` | Cross-session memory on/off |

Use `--worktree=name` with `=` when also passing a positional prompt, or the prompt is swallowed as the worktree name:

```bash
grok --worktree=feat-x --always-approve 'implement feature X'
# WRONG: grok -w "implement feature X"  → treats the sentence as the worktree label
```

### Model & limits
| Flag | Effect |
|------|--------|
| `-m, --model <ID>` | Model id (`grok models` to list) |
| `--reasoning-effort` / `--effort <LEVEL>` | `none`…`max` / model menu ids (e.g. `deep`) |
| `--max-turns <N>` | Cap agentic turns (**headless only**) |
| `--rules <TEXT>` | Append extra rules to system prompt |
| `--system-prompt-override <TEXT>` | Replace system prompt (compat: `--system-prompt`) |
| `--agent <NAME_OR_PATH>` | Agent name or definition file |
| `--agents <JSON>` | Inline subagent definitions (**headless only**) |

### Permissions & safety
| Flag | Effect |
|------|--------|
| `--always-approve` / `--yolo` | Auto-approve tools |
| `--permission-mode <MODE>` | See table above |
| `--allow <RULE>` / `--deny <RULE>` | Repeatable permission rules |
| `--tools <LIST>` | Allowlist built-ins (**headless only**) |
| `--disallowed-tools <LIST>` | Denylist built-ins (**headless only**) |
| `--disable-web-search` | Drop web search/fetch tools |
| `--sandbox <PROFILE>` | OS sandbox: `off`, `workspace`, `read-only`, `strict`, `devbox`, or custom |

### Output
| Flag | Effect |
|------|--------|
| `--output-format <FMT>` | `plain` (default), `json`, `streaming-json`, `streaming-messages-json` |
| `--json-schema <SCHEMA>` | Constrain final output; implies json |
| `--include-partial-messages` | Partial deltas; only with `streaming-messages-json` |

### Debug
| Flag | Effect |
|------|--------|
| `--debug` / `--debug-file <FILE>` | Debug logging |
| `--no-auto-update` | Skip update checks this session |

## Subcommands

| Command | Purpose |
|---------|---------|
| `grok` / `grok "prompt"` | Interactive TUI (optional initial prompt) |
| `grok -p "prompt"` | Headless print mode |
| `grok agent stdio` | ACP agent over stdio (IDEs/SDKs) |
| `grok agent serve --bind HOST:PORT --secret TOKEN` | ACP WebSocket server |
| `grok agent headless --grok-ws-url WSS_URL` | Agent via WebSocket relay |
| `grok login` / `grok login --device-auth` | Authenticate |
| `grok logout` | Clear credentials |
| `grok models` | List models |
| `grok doctor` | Terminal/environment health |
| `grok update` | Self-update |
| `grok sessions list\|search\|delete` | Manage saved sessions |
| `grok export` | Export transcript as Markdown |
| `grok mcp list\|add\|remove\|enable\|disable\|doctor` | MCP servers |
| `grok worktree list\|rm\|gc` | Managed git worktrees |
| `grok memory …` | Cross-session memory |
| `grok plugin …` | Plugins / marketplaces |
| `grok inspect` | Show discovered config for this directory |
| `grok dashboard` | Open Agent Dashboard at startup |
| `grok setup` | Fetch/install managed configuration |

### ACP agent (IDE / SDK) quick start

```bash
grok agent --always-approve stdio
grok agent --always-approve -m grok-4.5 serve --bind 127.0.0.1:2419 --secret "$TOKEN"
```

Prefer `grok -p` for one-shot shell orchestration; use `grok agent` when a client speaks ACP/JSON-RPC.

## Interactive TUI essentials

### Useful slash commands
| Command | Purpose |
|---------|---------|
| `/new` (`/clear`) | Fresh session |
| `/resume` | Session picker |
| `/compact [focus]` | Compress context |
| `/context` | Context window breakdown |
| `/session-info` (`/status`) | Session metadata + usage |
| `/model <id>` (`/m`) | Switch model |
| `/effort <level>` | Reasoning effort on current model |
| `/always-approve` | Toggle always-approve |
| `/rewind` (`/undo`) | Restore files + history to earlier turn |
| `/fork` | Branch session (optional `--worktree`) |
| `/rename` (`/title`) | Name session (resume-by-title friendly) |
| `/dashboard` | Multi-session Agent Dashboard |
| `/quit` (`/exit`) | Exit TUI |

### Key bindings (orchestration)
| Key | Action |
|-----|--------|
| `Enter` | Send prompt |
| `Esc` | Cancel running turn (when prompt empty / per mode rules) |
| `Ctrl+C` | Clear draft once, then cancel/exit behavior |
| `Ctrl+O` | Toggle always-approve |
| `Shift+Tab` | Cycle permission modes |
| `Ctrl+N` | New session |
| `@` | File attach / fuzzy picker (`@!.env` includes hidden) |
| `/` | Slash command menu |

Exit interactive sessions with `/quit` or `/exit` (not Claude's dialog flow).

## Project context (AGENTS.md)

Grok auto-loads project rules walking from repo root → cwd. Recognized names (per directory): `Agents.md`, `Claude.md`, `CLAUDE.md`, `CLAUDE.local.md`, `AGENT.md`, `AGENTS.md`. Also: `.grok/rules/*.md`, and optionally `.claude/rules/`, `.cursor/rules/` when compatibility is on. Home: `~/.grok/rules/`.

Deeper files win on conflict. Keep rules **specific** (commands, style, test runner) — vague rules waste turns.

```bash
# See what config/rules Grok will load
cd ~/project && grok inspect
```

Append one-off rules without editing files:

```bash
grok -p '…' --always-approve --rules 'Never commit. Use uv for Python.'
```

## Sandbox profiles

Optional OS-level FS/network limits (`GROK_SANDBOX` env or `--sandbox`):

| Profile | Write | Notes |
|---------|-------|-------|
| `off` (default) | Unrestricted | Normal trust |
| `workspace` | CWD + `~/.grok` + temp | Everyday dev |
| `read-only` | `~/.grok` + temp only | Reviews / explore |
| `strict` | CWD + `~/.grok` + temp; tight read | Untrusted code |
| `devbox` | Broad (not `/data`) | Disposable VMs |

```bash
grok -p 'Review for vulns only' --sandbox read-only --always-approve
grok -p 'Implement feature' --sandbox workspace --always-approve
```

Custom profiles: `~/.grok/sandbox.toml` or `.grok/sandbox.toml`.

## MCP

```bash
grok mcp list
grok mcp add github -- npx -y @modelcontextprotocol/server-github
grok mcp add -t http -s project linear https://mcp.linear.app/mcp
grok mcp add -s user postgres -- npx -y @modelcontextprotocol/server-postgres --connection-string "$DATABASE_URL"
grok mcp doctor
```

Scopes: `-s user` → `~/.grok/config.toml`; `-s project` → `./.grok/config.toml`.

## PR review patterns

### Quick headless review
```bash
cd /path/to/repo && grok -p "Review this diff for bugs, security issues, and missing tests:

$(git diff main...HEAD)" --always-approve --max-turns 8 --output-format json \
  | jq -r '.text'
```

### Review in isolated clone
```bash
REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git "$REVIEW" \
  && cd "$REVIEW" && gh pr checkout 42 \
  && grok -p 'Review this PR vs main. Report bugs, security risks, test gaps.' \
       --always-approve --max-turns 15 --output-format json | jq -r '.text'
```

### Interactive deep review + worktree
```bash
tmux new-session -d -s grok-review -x 140 -y 40
tmux send-keys -t grok-review \
  'cd /path/to/repo && grok --worktree=pr-review --always-approve' Enter
sleep 5 && tmux send-keys -t grok-review \
  'Review all changes vs main for bugs, races, and missing tests.' Enter
sleep 30 && tmux capture-pane -t grok-review -p -S -80
```

## Parallel workers

One worktree (or directory) per worker — never share a git index.

```bash
cd ~/project
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main

# Headless workers (background each)
cd /tmp/issue-78 && grok -p 'Fix issue #78: <desc>. Run tests. Commit when done.' \
  --always-approve --max-turns 25 > /tmp/g78.log 2>&1 &
cd /tmp/issue-99 && grok -p 'Fix issue #99: <desc>. Run tests. Commit when done.' \
  --always-approve --max-turns 25 > /tmp/g99.log 2>&1 &

# Or let Grok create the worktree
cd ~/project && grok --worktree=fix-78 --always-approve -p 'Fix issue #78…' --max-turns 25
```

tmux variant: one session per task, `capture-pane` to monitor.

## Sessions CLI

```bash
grok sessions list -n 20
grok sessions search 'auth refactor'
grok sessions delete <session-id>
grok export   # transcript helpers — see grok export --help
```

Sessions live under `~/.grok/sessions/` (override root with `GROK_HOME`).

## Environment variables

| Variable | Effect |
|----------|--------|
| `XAI_API_KEY` | API auth (CI-friendly) |
| `GROK_HOME` | Config/state root (default `~/.grok`) |
| `GROK_SANDBOX` | Default sandbox profile |
| `GROK_DISABLE_AUTOUPDATER=1` | Disable update checks |
| `GROK_LOG_FILE` | Log path |
| `RUST_LOG` | Log filter (e.g. `debug`); headless logs on stderr |
| `GROK_AGENT_SECRET` | Default secret for `grok agent serve` |

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Auth/network/runtime error |
| `130` | SIGINT |
| `143` | SIGTERM |

## Monitoring interactive sessions

```bash
tmux capture-pane -t grok-work -p -S -40
```

Look for: idle composer (ready for input), mid-turn tool activity, permission prompts (if not `--always-approve`), errors in the scrollback. Prefer `/session-info` or headless `json` usage fields for spend/context — don't kill slow multi-step runs without checking progress.

## Cost & performance tips

1. Prefer **headless** (`-p`) for single tasks — no TUI overhead, structured output.
2. Always set **`--max-turns`** in headless to bound runaway loops (start 8–20).
3. Always pass **`--always-approve`** in automation so runs don't block on prompts.
4. Use **`--tools` / `--disallowed-tools`** to shrink capabilities (reviews = read-only).
5. **`--sandbox read-only`** for pure review/explore.
6. Pipe context via **command substitution**, not hope-stdin.
7. **Resume** (`-c` / `--resume`) only when prior context helps; else fresh session.
8. **`/compact`** in long TUI sessions near context limits (auto-compact ~85%).
9. Pick model with `grok models` + `-m`; raise `--effort` only when needed.
10. Parallelize with **separate worktrees**, not one cwd.
11. CI: `XAI_API_KEY` + `--always-approve` + `--output-format json` + `--no-auto-update`.

## Pitfalls & gotchas

1. **Headless ignores piped stdin for the prompt** — use `$(…)` or `--prompt-file`.
2. **Without `--always-approve`, automation can hang** on permission prompts.
3. **`--max-turns` / `--tools` / `--agents` are headless-only** — ignored in TUI (warning).
4. **`-s/--session-id` never resumes** — only creates a new UUID session; use `-r`/`-c`.
5. **`--worktree` + positional prompt** — use `--worktree=name` with `=` so the prompt is not the worktree label.
6. **Tool names are Grok internal IDs** (`read_file`, `run_terminal_command`, …), not Claude's `Read`/`Bash`.
7. **Shared cwd + parallel writers = git index fights** — one worktree per worker.
8. **Auth follows HOME/GROK_HOME** — harness user mismatch looks like logged-out.
9. **Cost fields may be missing** on OAuth/pool paths — absence ≠ $0.
10. **Large monorepo `--cwd` nested deep** — Grok walks up to `.git` and may load huge context; point `--cwd` at the subproject.
11. **Interactive TUI needs a PTY** — use tmux if the harness has none.
12. **Deny/hooks still apply under yolo** — a deny rule can fail a "fully auto" run by design.

## Verification smoke test

```bash
grok -p 'Respond with exactly: GROK_SMOKE_OK' --always-approve --max-turns 2
```

Success: stdout contains `GROK_SMOKE_OK`, exit 0, no auth errors.

## Rules for orchestrating Grok

1. **Prefer `grok -p` for single tasks** — cleanest integration path.
2. **Always `--always-approve` (or equivalent) in non-interactive runs.**
3. **Always set `--max-turns` in headless** — bound cost and loops.
4. **Always set the working directory** (`cd` or `--cwd`).
5. **Use tmux (or PTY tool) only when multi-turn TUI is required.**
6. **Monitor long runs** — logs, `capture-pane`, or `streaming-json`.
7. **Don't kill slow jobs without inspecting progress first.**
8. **One worktree/directory per parallel worker.**
9. **Report concrete outcomes** — files changed, tests, session id, remaining risks.
10. **Clean up** tmux sessions, background jobs, and temp worktrees when done.
