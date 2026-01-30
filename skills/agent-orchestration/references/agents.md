# Agent Reference

## Claude Code

Launch: `claude "<prompt>" [--model <opus|sonnet|haiku> --allowedTools "<tools>"]`

**⚠️ Argument order matters:** Prompt must come immediately after `claude`, flags come after.

**Permission flags:**
- Read-only: `--allowedTools "Bash,Glob,Grep,Read,WebFetch,WebSearch,Skill,SlashCommand,firecrawl_*"`
- Write: `--allowedTools "Bash,Glob,Grep,Read,Edit,Write,WebFetch,WebSearch,Skill,SlashCommand,Write,firecrawl_*"`

**Model selection:** `--model <model>`

| Model | Use Case |
|-------|----------|
| `haiku` | Simple analysis, low-complexity |
| `sonnet` | Everyday tasks |
| `opus` | Complex, difficult tasks |

Do not use `-p` flag (enables headless mode).

---

## Codex

Launch: `codex "<prompt>"`

**Permission flags:**
- Read-only: `--sandbox read-only`
- Write: `--full-auto true`

**Model selection:** `--model <model>`

| Model | Use Case |
|-------|----------|
| `gpt-5.2-codex` | Best for most tasks, particularly coding, optimized for deep/fast reasoning |
| `gpt-5.2` | Latest frontier, hard/complex tasks |

**Reasoning effort:** `-c model_reasoning_effort="<level>"` (medium or high)

---

## Droid

Launch: `droid` (no prompt - interactive mode required)

Droid requires interactive configuration before sending prompts.

**Model selection:**
1. `tmux send-keys -t <pane> "/model" Enter`
2. Navigate with arrow keys: `tmux send-keys -t <pane> <Up|Down>`
3. Confirm: `tmux send-keys -t <pane> Enter`
4. View list: `tmux capture-pane -pt <pane> -S -100`

Prefer `gpt-` or `claude-` models unless otherwise specified.

**Mode selection:**
- Switch modes: `tmux send-keys -t <pane> "BTab"` (Shift+Tab)
- Verify: `tmux capture-pane -pt <pane> -S -100`

| Mode | Use Case |
|------|----------|
| Specification mode | Planning specs |
| Auto (Low) | Read-only, light edits |
| Auto (Medium) | Write operations, reversible |
| Auto (High) | All operations |

After configuration, send prompt: `tmux send-keys -t <pane> "<prompt>"`

---

## Pi

Launch: `pi "<prompt>"`

No permission flags available.

**Model selection:** `--provider "cliproxyapi" --model "<model>"`

| Model |
|-------|
| `gpt-5.2-codex(medium)` |
| `gpt-5.2-codex(high)` |
| `gpt-5.2(medium)` |
| `gpt-5.2(high)` |
| `claude-opus-4-5-20251101` |
| `claude-sonnet-4-5-20250929` |
| `claude-haiku-4-5-20251001` |

Prefer `gpt-` or `claude-` models unless otherwise specified.
