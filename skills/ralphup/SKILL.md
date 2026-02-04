---
name: ralphup
description: |
  Launch a ralph loop for autonomous task execution. Use when user wants to start a ralph loop, run ralph, or execute a project scope autonomously. Triggers on "ralph", "ralphup", "start loop", or references to scope files in project-manager.
---

# Ralphup

Launch autonomous ralph loops that iterate on project scopes until completion.

## Workflow

1. **Get project details** via `apm get <project_id> --json`
2. **Generate prompt** from template with project-specific paths
3. **Launch loop** with chosen agent (claude or codex)

## Step 1: Get Project Details

List available projects:

```bash
apm list --status todo
apm list --status in_progress
```

Get project details:

```bash
apm get <project_id> --json
```

This returns project metadata including path. Project files live at `~/projects/<project_id>_<slug>/`.

Required files for a ralph loop:
- `README.md` - main spec (in project folder)
- `SPECS.md` - detailed specs (in project folder)
- `SCOPES.md` - task scopes (in project folder)
- `progress.md` - progress log (create if missing)

## Step 2: Generate Prompt

Choose the appropriate template based on the CLI being used:
- **Claude**: [assets/prompt.claude.template.md](assets/prompt.claude.template.md)
- **Codex**: [assets/prompt.codex.template.md](assets/prompt.codex.template.md)

Read the template and replace placeholders:

| Placeholder | Value |
|-------------|-------|
| `{{PROJECT_FILE}}` | `~/projects/<project_folder>/README.md` |
| `{{SCOPES_FILE}}` | `~/projects/<project_folder>/SCOPES.md` |
| `{{PROGRESS_FILE}}` | `~/projects/<project_folder>/progress.md` |
| `{{SOURCE_DIR}}` | Repo path from project frontmatter (or ask user) |

Write generated prompt to project folder: `~/projects/<project_folder>/prompt.md`

## Step 3: Launch Loop

Choose the appropriate script based on user preference:

### Using Claude (default)

```bash
./scripts/ralph_claude.sh <iterations> <workspace> <prompt_file>
```

Example:
```bash
./scripts/ralph_claude.sh 20 ~/code/aihub ~/projects/PRO-58_aihub_persist_sessions/prompt.md
```

### Using Codex

```bash
./scripts/ralph_codex.sh <iterations> <workspace> <prompt_file>
```

Example:
```bash
./scripts/ralph_codex.sh 20 ~/code/aihub ~/projects/PRO-58_aihub_persist_sessions/prompt.md
```

**Choose based on user's request:**
- "ralph loop with codex" / "use codex" → `ralph_codex.sh`
- "ralph loop with claude" / "use claude" / default → `ralph_claude.sh`

The loop exits early if output contains `<promise>COMPLETE</promise>`.

## Environment Variables

Both scripts support:
- `RALPH_MAX_RETRIES` - Max retry attempts per iteration (default: 3)
- `RALPH_RETRY_DELAY` - Seconds between retries (default: 2)

Claude-specific:
- `RALPH_STREAM_VERBOSE` - Enable verbose streaming (default: 1)
- `RALPH_KILL_GRACE_SECONDS` - Grace period before killing hung process (default: 2)

Codex-specific:
- `RALPH_MODEL` - Model to use (default: `gpt-5.2-codex`)
- `RALPH_REASONING_EFFORT` - Reasoning effort level (default: `medium`)

## Resources

- `scripts/ralph_claude.sh` - Loop script using Claude CLI
- `scripts/ralph_codex.sh` - Loop script using Codex CLI
- `assets/prompt.claude.template.md` - Prompt template for Claude (references Sonnet/Opus subagents)
- `assets/prompt.codex.template.md` - Prompt template for Codex (uses spawn_agent/send_input/close_agent)
