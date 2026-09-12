---
name: pi
description: Delegate coding work to Pi from any agent or shell harness. Use for bounded print-mode tasks, machine-monitored JSON event runs, iterative tmux sessions, reviews, or isolated parallel workers.
---

# Pi CLI

Delegate work through shell commands. Prefer print mode for bounded tasks; use tmux for iterative TUI work. Treat Pi as an autonomous worker, not a substitute for verification.

## Check readiness

```bash
pi --version
pi --help
```

Confirm provider configuration without printing credentials. Never pass keys in prompts, command arguments, logs, or artifacts.

## Run bounded tasks

Run from target repository and give explicit scope, constraints, tests, and reporting requirements:

```bash
cd /path/to/repo && pi -p \
  "Implement X. Touch only Y. Run test Z. Report changed files and results."
```

Use `pi -p`, not `pi exec`; Pi has no `exec` subcommand. Print mode needs no PTY and exits after processing.

Capture machine-readable events when harness must monitor progress:

```bash
cd /path/to/repo && pi --mode json -p \
  "Implement X; run tests; report evidence." \
  >pi-events.jsonl 2>pi-stderr.log
```

Parse output line by line. `--mode json` emits JSONL events, not one guaranteed result object. Inspect event types before depending on fields. Use `--mode rpc` only when building bidirectional process integration.

## Restrict tools

Make review-only work truly read-only:

```bash
cd /path/to/repo && pi --tools read,grep,find,ls -p \
  "Review code. Do not modify files. Report findings with file and line references."
```

Use `--no-tools` when no repository access is needed. Remember `grep`, `find`, and `ls` are off by default unless enabled; `--tools` allowlists all built-in, extension, and custom tools and can accidentally omit needed `bash`, `edit`, or `write`. Tool restriction is not a filesystem sandbox. Use container or OS isolation for untrusted work; Pi has no built-in permission popups.

## Select model and thinking

Choose explicitly when task or budget requires it:

```bash
pi --model openai/gpt-4o --thinking high -p "Diagnose this failure"
pi --provider openai --model gpt-4o -p "Implement the approved fix"
pi --model sonnet:high -p "Review this design"
```

Use supported thinking levels: `off`, `minimal`, `low`, `medium`, `high`, `xhigh`, or `max`. Check available models with `pi --list-models` without starting a provider-consuming task.

## Control project trust

Set trust explicitly in automation:

```bash
cd /path/to/repo && pi --approve -p "Use project configuration and implement X"
cd /path/to/repo && pi --no-approve -p "Review without project-local resources"
```

Treat `--approve` as permission to load project-local settings, resources, packages, and extensions—not blanket tool authorization. Noninteractive modes show no trust prompt. Without saved trust or an override, `defaultProjectTrust=ask` and `never` ignore project resources; `always` trusts them. Inspect unfamiliar project-local code before approving it.

## Run iterative sessions in tmux

Use tmux because TUI requires a PTY and Pi has no built-in background bash:

```bash
tmux new-session -d -s pi-worker -x 140 -y 40
tmux send-keys -t pi-worker 'cd /path/to/repo && pi' Enter
sleep 3
tmux capture-pane -t pi-worker -p -S -80
tmux send-keys -t pi-worker 'Implement X; run tests; report files changed.' Enter

# Monitor and follow up
tmux has-session -t pi-worker
tmux capture-pane -t pi-worker -p -S -100
tmux send-keys -t pi-worker 'Now address the failing edge case and rerun tests.' Enter

# Stop and clean up
tmux send-keys -t pi-worker '/quit' Enter
tmux kill-session -t pi-worker
```

Inspect pane output before sending prompts. Use Pi's documented `/quit` command or kill the session.

## Continue or fork sessions

```bash
pi --continue -p "Follow up on the previous task"
pi --resume                         # choose interactively; verify selection
pi --session /path/to/session.jsonl -p "Continue this session"
pi --session-id worker-a -p "Use exact project session ID"
pi --fork /path/to/session.jsonl -p "Try an alternate approach"
pi --session-dir /tmp/pi-worker-a -p "Run in isolated session storage"
pi --no-session -p "Perform an ephemeral review"
```

Use `--continue` for most recent history, `--resume` for interactive selection, and `--fork` for an alternate branch. Treat `--session-id` as exact project session selection or creation, not history lookup. Never share one session file or session directory between concurrent workers.

## Run parallel workers

Give each worker an independent Git worktree, branch, session directory, tmux session, and output path:

```bash
git worktree add "$HOME/.worktrees/pi-a" -b worker/a HEAD
git worktree add "$HOME/.worktrees/pi-b" -b worker/b HEAD
mkdir -p /tmp/pi-sessions/{a,b} /tmp/pi-logs

tmux new-session -d -s pi-a \
  "cd '$HOME/.worktrees/pi-a' && pi -p --session-dir /tmp/pi-sessions/a 'Fix issue A; run targeted tests' >/tmp/pi-logs/a.log 2>&1"
tmux new-session -d -s pi-b \
  "cd '$HOME/.worktrees/pi-b' && pi -p --session-dir /tmp/pi-sessions/b 'Fix issue B; run targeted tests' >/tmp/pi-logs/b.log 2>&1"
```

Never run concurrent writers in shared cwd or Git index. Assign non-overlapping tasks. Monitor each lane independently, review diffs, then integrate deliberately.

## Verify outcomes

Do not accept process exit or final prose as proof. Check concrete artifacts:

```bash
tail -n 100 /tmp/pi-logs/a.log
git -C "$HOME/.worktrees/pi-a" status --short
git -C "$HOME/.worktrees/pi-a" diff --check
git -C "$HOME/.worktrees/pi-a" diff --stat
cd "$HOME/.worktrees/pi-a"
# Run the repository's actual targeted test command.
```

Require expected files, scope-limited diff, passing targeted tests, and clean `git diff --check`. Inspect JSONL/stderr or pane logs for errors and unresolved requests. Review all changes before merging.

## Pitfalls

- Invoke root `pi` with `-p`; no `pi exec` exists.
- Read JSON mode as event JSONL, not one result object.
- Give interactive sessions a PTY; use tmux for observability and follow-up.
- Separate worktrees and session storage across parallel writers.
- Do not confuse project trust with tool permission or sandboxing.
- Enable `grep`, `find`, and `ls` explicitly when read-only work needs them.
- Use `--continue`, `--resume`, or `--fork` for history; exact `--session-id` may create a session.
- Avoid provider-consuming smoke prompts; validate CLI readiness, artifacts, diffs, and requested tests instead.
