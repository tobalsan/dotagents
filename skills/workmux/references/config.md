# workmux Configuration Reference

Two-level config system:
- **Global**: `~/.config/workmux/config.yaml`
- **Project**: `.workmux.yaml` (overrides global)

Use `"<global>"` in project config to include global values.

## Basic Options

| Option | Description | Default |
|--------|-------------|---------|
| `main_branch` | Branch to merge into | Auto-detected |
| `worktree_dir` | Directory for worktrees | `<project>__worktrees/` |
| `window_prefix` | Prefix for tmux window names | `wm-` |
| `agent` | Default agent for `<agent>` placeholder | `claude` |
| `merge_strategy` | Default: `merge`, `rebase`, or `squash` | `merge` |
| `worktree_naming` | `full` or `basename` | `full` |
| `worktree_prefix` | Prefix for worktree dirs/windows | none |

## Panes Configuration

```yaml
panes:
  - command: <agent>      # Use configured agent
    focus: true           # Focus this pane
  - command: npm run dev
    split: horizontal     # or vertical
    size: 15              # Absolute lines/cells
    percentage: 30        # Or percentage (1-100)
```

Pane options:
- `command`: Command to run (`<agent>` substitutes configured agent)
- `focus`: Whether pane receives focus (default: false)
- `split`: `horizontal` or `vertical`
- `size`: Absolute size in lines/cells
- `percentage`: Size as percentage (1-100)

## File Operations

```yaml
files:
  copy:
    - .env
    - .env.local
  symlink:
    - node_modules
    - .pnpm-store
```

Both support glob patterns. Symlinks are faster but only work if worktrees share identical dependencies.

## Lifecycle Hooks

All hooks run with worktree as working directory. Environment vars available: `WM_HANDLE`, `WM_WORKTREE_PATH`, `WM_PROJECT_ROOT`.

```yaml
post_create:
  - '<global>'
  - direnv allow
  - mise use

pre_merge:
  - just check          # Aborts merge on failure

pre_remove:
  - ./cleanup.sh        # Aborts remove on failure
```

| Hook | When | Extra env vars |
|------|------|----------------|
| `post_create` | After worktree creation, before tmux window | — |
| `pre_merge` | Before merging (aborts on failure) | `WM_BRANCH_NAME`, `WM_TARGET_BRANCH` |
| `pre_remove` | Before worktree removal (aborts on failure) | — |

## Agent Status Icons

```yaml
status_icons:
  working: '🤖'    # Agent is processing
  waiting: '💬'    # Agent needs input
  done: '✅'       # Agent finished

status_format: false  # Disable auto tmux format modification
```

## Auto-naming Configuration

Requires `llm` CLI (`pipx install llm`).

```yaml
auto_name:
  model: 'gemini-2.5-flash-lite'  # or gpt-5-nano
  system_prompt: |
    Generate a concise git branch name based on the task description.
    Rules:
    - Use kebab-case (lowercase with hyphens)
    - Keep it short: 1-3 words, max 4 if necessary
    - No prefixes like feat/, fix/, chore/
    Output ONLY the branch name, nothing else.
```

## Full Example

```yaml
# .workmux.yaml
agent: claude
window_prefix: "wm-"
merge_strategy: rebase

panes:
  - command: pnpm install && pnpm run dev
  - command: <agent>
    split: horizontal
    focus: true

files:
  copy:
    - .env
  symlink:
    - '<global>'
    - node_modules
    - .pnpm-store

post_create:
  - '<global>'
  - direnv allow

pre_merge:
  - pnpm test
  - pnpm build
```
