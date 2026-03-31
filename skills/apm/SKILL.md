---
name: apm
description: Manage AIHub projects and project-run operations with the apm CLI over gateway HTTP APIs. Use when work requires listing, reading, creating, updating, moving, archiving, commenting on projects, or starting/resuming/checking CLI subagent runs with explicit harness/model/reasoning options.
---

# APM

## Overview

Use `apm` for project CRUD and run orchestration from terminal. Prefer `--json` when output must be parsed or copied into structured updates.

## Command Map

- List/filter projects: `apm list [--status ...] [--owner ...] [--domain ...] [--json]`
- Create project: `apm create --title "..." [description] [--specs <text|->] [--domain ...] [--owner ...] [--execution-mode ...] [--appetite ...] [--status shaping]` — **Always use `--status shaping`** on create. Most new projects are being shaped/spec'd. Never use `--status in_progress` at creation time — move to `in_progress` later with `apm move` when implementation actually begins.
- Get project: `apm get PRO-123 [--json]`
- Update project: `apm update PRO-123 [--title ...] [--status ...] [--domain ...] [--owner ...] [--execution-mode ...] [--appetite ...] [--repo ...] [--readme <text|->] [--specs <text|->]`
- Move status quickly: `apm move PRO-123 review`
- Start run: `apm start PRO-123 ...`
- Resume run: `apm resume PRO-123 -m "..." [--slug ...]`
- Check run status: `apm status PRO-123 [--slug ...] [--limit N] [--json]`
- Add project comment: `apm comment PRO-123 -m "..." [--author ...]`
- Archive/unarchive project: `apm archive PRO-123`, `apm unarchive PRO-123`

## Run Control

Use `apm start` for full run config.

```bash
apm start PRO-123 \
  --name "worker-a" \
  --template worker \
  --mode worktree \
  --slug worker-a \
  --custom-prompt "Implement task 2"
```

### Start Flags

- `--agent <cli|aihub:id>`: choose harness/agent. `codex|claude|pi` maps to `cli:*`.
- `--name <run-name>`: optional custom run label.
- `--model <id>`: harness model.
- `--reasoning-effort <xhigh|high|medium|low|...>`: codex/claude effort.
- `--thinking <off|low|medium|high|xhigh>`: pi thinking level.
- `--mode <main-run|clone|worktree|none>`: run workspace strategy.
- `--branch <branch>`: base branch for clone/worktree.
- `--slug <slug>`: run slug override.
- `--template <coordinator|worker|reviewer|custom>`: apply UI template defaults for role prompt + run config.
- `--prompt-role <coordinator|worker|reviewer|legacy>`: override role prompt mapping.
- `--include-default-prompt|--exclude-default-prompt`: force toggle default project context.
- `--include-role-instructions|--exclude-role-instructions`: force toggle role instruction block.
- `--include-post-run|--exclude-post-run`: force toggle post-run checklist block.
- `--custom-prompt <text|->`: append custom prompt (`-` reads stdin).

### Template Defaults (UI parity)

When `--template` is set, `apm start` pre-fills run config the same way as UI prep form:

- `coordinator`: `--agent claude`, `--model opus`, effort `medium`, `--mode none`, base branch `main`, includes `default:on role:on post-run:off`
- `worker`: `--agent codex`, `--model gpt-5.4`, effort `medium`, `--mode worktree`, base branch `space/<projectId>`, includes `default:on role:on post-run:on`
- `reviewer`: `--agent codex`, `--model gpt-5.4`, effort `high`, `--mode none`, base branch `main`, includes `default:on role:on post-run:on`
- `custom`: `--agent codex`, `--model gpt-5.3-codex`, effort `xhigh`, `--mode clone`, base branch `main`, includes `default:on role:on post-run:on`

Notes:
- Prefer template-only commands unless you intentionally override.
- Worker template base branch is resolved server-side to `space/<projectId>`; add `--branch ...` only when intentionally overriding.
- Explicit flags override template defaults: `--agent`, `--model`, `--reasoning-effort`, `--thinking`, and include/exclude toggles.
- If overridden to `--agent pi`, template effort is translated to `--thinking`.

### Harness Model Matrix

- Codex models: `gpt-5.4`, `gpt-5.3-codex`, `gpt-5.3-codex-spark`, `gpt-5.2`
- Claude models: `opus`, `sonnet`, `haiku`
- Pi models: `qwen3.5-plus`, `qwen3-max-2026-01-23`, `MiniMax-M2.5`, `glm-5`, `kimi-k2.5`

Gateway enforces valid model/reasoning combinations; invalid combos return HTTP 400.

## Workflow

1. Inspect project and current runs.
```bash
apm get PRO-123 --json
apm status PRO-123 --json
```
2. Update metadata/content.
```bash
apm update PRO-123 --status in_progress --owner "Thinh"
cat SPECS.md | apm update PRO-123
```
3. Start or resume run.
```bash
apm start PRO-123 --agent claude --model sonnet --reasoning-effort high --mode clone
apm resume PRO-123 -m "Continue from last checkpoint" --slug worker-a
```
4. Post progress and transition status.
```bash
apm comment PRO-123 -m "Implemented API + tests, ready for review"
apm move PRO-123 review
```

## Operational Notes

- Normalize IDs to `PRO-<n>` format.
- Use `--json` for stable machine-readable output.
- Set endpoint with `AIHUB_API_URL=<url>` when needed.
- **Fallback:** if `apm` produces no output, use `cd ~/code/aihub && pnpm apm ...` instead.
