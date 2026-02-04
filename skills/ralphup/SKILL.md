---
name: ralphup
description: |
  Launch a ralph loop for autonomous task execution. Use when user wants to start a ralph loop, run ralph, or execute a project scope autonomously. Triggers on "ralph", "ralphup", "start loop", or references to scope files in project-manager.
---

# Ralphup

Launch autonomous ralph loops that iterate on project scopes until completion.

## Workflow

1. **Locate scope file** in `~/code/agent-company/project-manager/projects/{todo,doing}/`
2. **Generate prompt** from template with project-specific paths
3. **Launch loop** with `ralph.sh`

## Step 1: Find Scope File

List available projects:

```bash
ls ~/code/agent-company/project-manager/projects/todo/
ls ~/code/agent-company/project-manager/projects/doing/
```

User selects a project (e.g., `PRO-4_20260114_fix_ruff_mypy_runs`).

Required files for a project:
- `{project_id}.md` - main spec
- `{project_id}.scopes.md` - task scopes
- `{project_id}.progress.md` - progress log (create if missing)

## Step 2: Generate Prompt

Read [assets/prompt.template.md](assets/prompt.template.md) and replace placeholders:

| Placeholder | Value |
|-------------|-------|
| `{{PROJECT_FILE}}` | `~/code/agent-company/project-manager/projects/{status}/{project_id}.md` |
| `{{SCOPES_FILE}}` | `~/code/agent-company/project-manager/projects/{status}/{project_id}.scopes.md` |
| `{{PROGRESS_FILE}}` | `~/code/agent-company/project-manager/projects/{status}/{project_id}.progress.md` |
| `{{SOURCE_DIR}}` | Application source directory (ask user or read from spec) |

Write generated prompt to **same folder as project files**: `~/code/agent-company/project-manager/projects/{status}/{project_id}.prompt.md`

## Step 3: Launch Loop

```bash
./scripts/ralph.sh <iterations> <workspace> <prompt_file>
```

Example:
```bash
./scripts/ralph.sh 20 ~/code/algodyn/cloudifai ~/code/agent-company/project-manager/projects/doing/PRO-6_20260115_cloudifai_invoice_dashboard.prompt.md
```

The loop exits early if output contains `<promise>COMPLETE</promise>`.

## Resources

- `scripts/ralph.sh` - Main loop script
- `assets/prompt.template.md` - Prompt template with placeholders
