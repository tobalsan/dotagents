---
name: aihub-projects
description: "Manage AIHub projects via the `aihub projects` CLI. Use when creating, listing, updating, starting, resuming, archiving, or checking status of projects. Triggers on requests involving project management, project runs, project specs, moving project status, commenting on projects, or any `aihub projects` command."
---

# aihub/projects

CLI: `aihub projects <command> [options]`

## Quick Reference

| Command | Purpose |
|---------|---------|
| `list` | List projects (frontmatter only) |
| `create` | Create a new project |
| `get <id>` | Fetch full project details |
| `update <id>` | Update project fields or docs |
| `move <id> <status>` | Change project status |
| `comment <id>` | Add a comment to a project |
| `start <id>` | Start a project run |
| `resume <id>` | Resume an existing run |
| `status <id>` | Show run status + recent messages |
| `ralph <id>` | Start a Ralph loop run |
| `rename <id>` | Rename a run or change model |
| `archive <id>` | Archive a project |
| `unarchive <id>` | Unarchive a project |
| `config` | Manage local AIHub config |

All commands support `-j, --json` for JSON output.

## Statuses

`not_now` → `maybe` → `shaping` → `todo` → `in_progress` → `review` → `done`

## Commands

### list

```
aihub projects list [--status <status>] [-j]
```

### create

```
aihub projects create -t "Title Here" [description] [--specs <content>] [--status <status>] [--area <area>] [-j]
```

- Title required, must be ≥2 words.
- `--specs`: raw markdown for SPECS.md. Use `-` for stdin.
- `--area`: validated against `GET /api/areas`.

### get

```
aihub projects get <id> [-j]
```

### update

```
aihub projects update <id> [options]
```

Field options: `--title`, `--status`, `--run-agent`, `--run-mode <main-run|worktree>`, `--repo <path>`.

Doc options: `--readme <content>`, `--specs <content>`. Use `-` for stdin. Default stdin target is SPECS.md.

### move

```
aihub projects move <id> <status> [--agent <name>] [-j]
```

### comment

```
aihub projects comment <id> -m <message> [--author <author>] [-j]
```

Use `-` for stdin message.

### start

```
aihub projects start <id> [options]
```

Key options:
- `--agent <agent>`: `codex`, `claude`, `pi`, or `aihub:<id>`. Default: `codex`.
- `--mode <mode>`: `main-run|clone|worktree|none`. Default: `clone`.
- `--branch <branch>`: base branch (default `main`).
- `--slug <slug>`: slug override for worktree.
- `--prompt-role <role>`: `coordinator|worker|reviewer|legacy`.
- `--custom-prompt <prompt>`: one-off prompt (use `-` for stdin).
- `--include-default-prompt` / `--exclude-default-prompt`
- `--include-role-instructions` / `--exclude-role-instructions`
- `--include-post-run` / `--exclude-post-run`

Run agent formats:
- `cli:codex`, `cli:claude`, `cli:pi` — external CLI agents
- `aihub:<agentId>` — AIHub agents
- Use `aihub projects agent list` to see configured agents.

### resume

```
aihub projects resume <id> -m <message> [--slug <slug>] [-j]
```

Sends only the follow-up message (no project summary re-prepend).

### status

```
aihub projects status <id> [--limit <n>] [--slug <slug>] [-j]
```

Default: last 10 messages.

### ralph

```
aihub projects ralph <id> [--cli <codex|claude>] [--iterations <n>] [--prompt-file <path>] [--mode <main-run|worktree>] [--branch <branch>] [-j]
```

### rename

```
aihub projects rename <id> [--slug <slug>] [--name <name>] [--model <id>] [--reasoning-effort <level>] [--thinking <level>] [-j]
```

### archive / unarchive

```
aihub projects archive <id> [-j]
aihub projects unarchive <id> [-j]
```

## Common Patterns

```bash
# List in-progress projects
aihub projects list --status in_progress

# Create with specs
aihub projects create -t "Add Kill Tool" "Implement kill command" --specs "## Tasks\n- [ ] Implement"

# Pipe specs from file
cat SPECS.md | aihub projects update PRO-19 --specs -

# Start a worktree run with codex
aihub projects start PRO-19 --agent codex --mode worktree --slug my-feature

# Start a lead-agent run on AIHub agent
aihub projects start PRO-19 --agent aihub:cloud --custom-prompt "Plan the rollout."

# Resume a run
aihub projects resume PRO-19 -m "Continue from where you left off."

# Quick status move
aihub projects move PRO-19 done

# Add a comment
aihub projects comment PRO-19 -m "Blocked on API review" --author pom
```

## Environment

- `AIHUB_API_URL`: override API base URL (highest precedence).
- `AIHUB_URL`: fallback alias.
- `$AIHUB_HOME/aihub.json`: file config fallback (default home: `~/.aihub/`).
