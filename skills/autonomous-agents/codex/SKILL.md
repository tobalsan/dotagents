---
name: codex
description: Delegate coding work to the OpenAI Codex CLI from any agent or harness — one-shot `codex exec` runs, background long tasks, PR reviews, parallel worktree fixes. Use when asked to hand a feature, refactor, bug fix, or diff review to Codex, or when you need a second autonomous coding agent alongside your own.
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex), OpenAI's autonomous coding agent CLI.

This guide is harness-agnostic: everything is a shell command you run with whatever command-execution tool you have.

## When to use

- Building features
- Refactoring
- PR reviews
- Batch issue fixing
- Getting a second, independent implementation or opinion

## Harness mapping

Codex is an interactive terminal app: **it needs a PTY**, or it hangs. Map these to your harness:

| Need | Generic form | Typical mappings |
|------|--------------|------------------|
| PTY | a PTY-capable exec tool, or tmux | `pty=true`; otherwise `tmux new-session -d …` |
| Background run | background flag, or tmux, or `nohup … > /tmp/codex.log 2>&1 &` | `background=true`, `run_in_background` |
| Poll / read output | process log tool, or `tmux capture-pane`, or `tail -f` the log | `process(action="log")` |
| Answer a prompt from Codex | write to the process stdin, or `tmux send-keys` | `process(action="submit", data="yes")` |
| Stop it | kill the process, or `tmux kill-session` | `process(action="kill")` |

**tmux is the portable fallback** — if you have no PTY or process tool, every pattern below works through tmux alone.

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- Authenticated: `codex login` (ChatGPT subscription OAuth) or a provider API key. Credentials live in the invoking user's home directory — if your harness rewrites `HOME` or runs as another user, auth will look missing.
- **Must run inside a git repository** — Codex refuses to run outside one
- A PTY (see harness mapping)

## One-Shot Tasks

```bash
cd ~/project && codex exec 'Add dark mode toggle to settings'
```

For scratch work (Codex needs a git repo):
```bash
cd "$(mktemp -d)" && git init && codex exec 'Build a snake game in Python'
```

## Background Mode (Long Tasks)

Start it detached, then poll:

```bash
# With a harness background flag: run this with background + pty enabled
cd ~/project && codex exec --full-auto 'Refactor the auth module'

# Portable equivalent with tmux
tmux new-session -d -s codex-refactor -x 140 -y 40
tmux send-keys -t codex-refactor 'cd ~/project && codex exec --full-auto "Refactor the auth module"' Enter

# Monitor
tmux capture-pane -t codex-refactor -p -S -80

# Answer a question Codex asks
tmux send-keys -t codex-refactor 'yes' Enter

# Stop
tmux kill-session -t codex-refactor
```

If your harness has a process tool, use `poll` / `log` / `submit` / `kill` instead of the tmux equivalents.

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--model <name>` | Override model. See "Model Conventions" below. **Avoid pro models** (`o3-pro` etc.) — they fail with ChatGPT OAuth |
| `-c model_reasoning_effort=<level>` | Reasoning effort: `low`, `medium`, `high`, `xhigh` |
| `--full-auto` | Sandboxed but auto-approves file changes in the workspace (deprecated alias for `--sandbox workspace-write`) |
| `--sandbox workspace-write` | Preferred form of the above |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |
| `review --base <ref>` | Built-in diff review against a base ref |

## Model Conventions

Pick the model by the role the run is playing, not by preference. Substitute the current model IDs your account has access to (`codex --help` / provider docs); the roles are what matter:

| Role | Model tier | Reasoning effort | When |
|------|-----------|------------------|------|
| Worker (implements) | fast/cheap coding model | `low` | Runs that write code, fix bugs, build features |
| Reviewer (reviews diffs) | stronger reasoning model | `medium` | Runs that review PRs or diffs |
| Deep analysis (no impl) | latest default | `xhigh`, 300s+ timeout | Architecture opinions, hard diagnosis |

```bash
# Worker
codex exec --yolo --model <fast-model> -c model_reasoning_effort=low "implement X"
# Reviewer
codex exec --yolo --model <strong-model> -c model_reasoning_effort=medium "review PR #42"
```

**Never use pro models** (`o3-pro` and similar) unless the user explicitly asks — they fail with ChatGPT OAuth.

## PR Reviews

Clone to a temp directory for safe review:

```bash
REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git "$REVIEW" \
  && cd "$REVIEW" && gh pr checkout 42 && codex review --base origin/main
```

## Parallel Issue Fixing with Worktrees

```bash
# Create worktrees
cd ~/project
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main

# Launch Codex in each (background + pty; one session per worktree)
cd /tmp/issue-78 && codex --yolo exec 'Fix issue #78: <description>. Commit when done.'
cd /tmp/issue-99 && codex --yolo exec 'Fix issue #99: <description>. Commit when done.'

# After completion, push and open PRs
cd /tmp/issue-78 && git push -u origin fix/issue-78
gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'

# Cleanup
cd ~/project && git worktree remove /tmp/issue-78
```

Never point two Codex runs at the same working directory — they will collide on the git index.

## Batch PR Reviews

```bash
# Fetch all PR refs
cd ~/project && git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'

# Review multiple PRs in parallel (each backgrounded with a PTY)
codex exec 'Review PR #86. git diff origin/main...origin/pr/86'
codex exec 'Review PR #87. git diff origin/main...origin/pr/87'

# Post results
gh pr comment 86 --body '<review>'
```

## Pitfalls

1. **Pro models don't work with ChatGPT OAuth** — `o3-pro` and similar return `400 invalid_request_error: model not supported when using Codex with a ChatGPT account`. Use the role-appropriate model unless the user explicitly requests otherwise.
2. **Sandbox mode can't commit in git worktrees** — under `--sandbox workspace-write` / `--full-auto`, Codex can only write inside the workdir and `/tmp`. A worktree keeps its metadata in the parent repo's `.git/worktrees/`, outside the writable roots, so edits succeed but committing fails with `Operation not permitted` on `index.lock`. Workaround: let Codex edit, then commit yourself from outside the sandbox.
3. **`--full-auto` is deprecated** — prefer `--sandbox workspace-write`. Both work.
4. **`pnpm install` may break native modules** — if Codex runs `pnpm install` inside its sandbox, native modules like `better-sqlite3` can rebuild incorrectly. Re-run `CI=true pnpm install` from outside the sandbox afterward.
5. **Verify failures are actually regressions before dispatching** — before sending Codex to "fix a test failure from the refactoring", check whether the test also fails on `main` (`git stash && <test-runner> <test-file>`). Pre-existing failures waste tokens and produce confusing results.
6. **No PTY = hang** — a plain non-PTY exec of `codex` will appear to stall forever.

## Rules

1. **Always give it a PTY** — Codex is an interactive terminal app and hangs without one.
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch work.
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly.
4. **`--sandbox workspace-write` for building** — auto-approves changes inside the sandbox; `--yolo` only when you accept no sandbox.
5. **Background long tasks** — and monitor via logs/pane capture.
6. **Don't interfere** — poll the logs, be patient with long-running tasks.
7. **Parallel is fine** — run multiple Codex processes at once, one working directory each.
8. **Report concrete outcomes** — files changed, tests run, remaining risks.
