---
name: workmux
description: Manage git worktrees with tmux windows for parallel development workflows. Use when user wants to create isolated development environments, run multiple AI agents in parallel on different tasks, manage worktree-based workflows, or delegate tasks to background agents. Triggers on "worktree", "workmux", "parallel development", "run agents in parallel", or when managing isolated branches.
---

# workmux

CLI tool for managing git worktrees with tmux windows. Creates isolated development environments perfect for parallel AI agent workflows.

## Quick Reference

### Create worktree + tmux window
```bash
workmux add <branch-name>              # Create and switch to new worktree
workmux add feature -b                 # Create in background (don't switch)
workmux add feature -p "Task prompt"   # With inline prompt for AI agent
workmux add feature -P task.md         # With prompt from file
workmux add feature -A -p "Add auth"   # Auto-generate branch name from prompt
```

### Multiple parallel worktrees
```bash
workmux add task -a claude -a gemini   # One worktree per agent
workmux add task -n 3 -p "Task #{{ num }}"  # Create N worktrees
```

### Merge and cleanup
```bash
workmux merge                          # Merge current branch to main, cleanup
workmux merge --rebase                 # Rebase before merge
workmux merge --squash                 # Squash commits
workmux merge --keep                   # Keep worktree after merge
```

### Remove without merging
```bash
workmux remove                         # Remove current worktree
workmux rm feature                     # Remove specific worktree
workmux rm --gone                      # Remove worktrees with deleted remote branches
workmux rm --all                       # Remove all worktrees
workmux rm -k                          # Remove but keep branch
```

### Other commands
```bash
workmux list                           # List worktrees with status
workmux list --pr                      # Include GitHub PR status
workmux open <name>                    # Open/switch to worktree window
workmux close <name>                   # Close window, keep worktree
workmux dashboard                      # TUI for monitoring agents
workmux path <name>                    # Print worktree filesystem path
workmux init                           # Generate .workmux.yaml config
```

## Add Command Options

Key flags for `workmux add`:

| Flag | Description |
|------|-------------|
| `-b, --background` | Create in background without switching |
| `-p, --prompt <text>` | Inline prompt for AI agent panes |
| `-P, --prompt-file <path>` | Prompt from file |
| `-e, --prompt-editor` | Open editor to write prompt |
| `-A, --auto-name` | Generate branch name from prompt via LLM |
| `-a, --agent <name>` | Specify agent (multiple for parallel) |
| `-n, --count <N>` | Create N worktree instances |
| `--base <branch>` | Branch from specific base |
| `-w, --with-changes` | Move uncommitted changes to new worktree |
| `-W, --wait` | Block until window closes |
| `--pr <number>` | Checkout GitHub PR |
| `-H, --no-hooks` | Skip post_create hooks |
| `-F, --no-file-ops` | Skip file copy/symlink |

## Delegating Tasks

To delegate tasks to parallel agents:

1. Write prompt to temp file with full task context
2. Use relative paths (each worktree has own root)
3. Run in background with `-b` flag

```bash
# Single task delegation
workmux add auth-feature -b -P /tmp/auth-task.md

# Multiple parallel tasks
workmux add refactor -a claude -a gemini -b -P task.md
```

For scripted batch workflows with completion notification:
```bash
workmux add task -W -p "Complete task, then run: workmux remove --keep-branch"
```

## Dashboard

`workmux dashboard` shows all active agents across tmux sessions.

Key bindings:
- `1-9`: Jump to agent
- `d`: View diff
- `i`: Input mode (type to agent)
- `s`: Cycle sort mode
- `Enter`: Go to selected agent
- `q`: Quit

Requires agent status tracking via Claude Code plugin:
```bash
claude plugin marketplace add raine/workmux
claude plugin install workmux-status
```

## Configuration

See [references/config.md](references/config.md) for full configuration options.

Basic `.workmux.yaml`:
```yaml
agent: claude
window_prefix: "wm-"

panes:
  - command: <agent>
    focus: true
  - split: horizontal

files:
  symlink:
    - node_modules
  copy:
    - .env

post_create:
  - direnv allow
```
