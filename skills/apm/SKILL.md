---
name: apm
description: Manage AIHub projects and project-run operations with the apm CLI over gateway HTTP APIs. Use when work requires listing, reading, creating, updating, moving, archiving, commenting on projects, or starting/resuming/checking config-driven subagent runs and lead-agent runs with explicit harness/model/reasoning options.
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

## Creating Projects

When creating a project:

1. **Use `--readme` for high-level context** — the *why*, background, key files, links. README is the human-readable project summary.
2. **Use `--specs` for the full specification** — overview, goals, architecture, requirements, constraints, AND tasks + acceptance criteria. Specs are the comprehensive blueprint for implementation. A good spec answers: what are we building, why, how does it fit together, what are the constraints, AND what's the work breakdown.

### Task formatting (strict)

Tasks in specs MUST follow this format for the UI parser:

```md
## Tasks

- [ ] **Task title** `status:todo`
  Optional indented description.

- [ ] **Another task** `status:in_progress` `agent:worker-1`
```

Rules:
- Title must be wrapped in **bold**.
- Status must be backticked: `` `status:todo` ``, `` `status:in_progress` ``, `` `status:done` ``.
- Description lines must be indented by 2+ spaces.
- Optional H3 subgroup headings are allowed under `## Tasks`.
- See `docs/specs-task-format.md` for full spec.

### Acceptance criteria formatting

Plain checkbox items under `## Acceptance Criteria`:

```md
## Acceptance Criteria

- [ ] Criterion one
- [ ] Criterion two
```

### Stdin pattern for multi-line content

Use heredoc to avoid shell escaping issues. Do NOT use `-` as the specs/readme value in the same command line — it reads stdin but creates a stray `-` bullet. Use `$(cat <<'EOF' ... EOF)` instead:

```bash
apm update PRO-123 --specs "$(cat <<'EOF'
## Tasks
- [ ] **Do the thing** `status:todo`
EOF
)"

apm update PRO-123 --readme "$(cat <<'EOF'
# Project Title
Why this exists and how it works.
EOF
)"
```

## Run Control

Use `apm start` for full run config.

```bash
apm start PRO-123 \
  --subagent Worker \
  --slug worker-a \
  --custom-prompt "Implement task 2"
```

For lead agents:

```bash
apm start PRO-123 \
  --agent aihub:cloud \
  --custom-prompt "Plan the rollout"
```

### Start Flags

- `--agent <cli|aihub:id>`: choose harness/agent. `codex|claude|pi` maps to CLI harnesses; `aihub:<id>` launches a configured lead agent.
- `--subagent <name>`: resolve a named subagent config from top-level `subagents` in `aihub.json`.
- `--name <run-name>`: optional custom run label.
- `--model <id>`: harness model.
- `--reasoning-effort <xhigh|high|medium|low|...>`: codex/claude effort.
- `--thinking <off|low|medium|high|xhigh>`: pi thinking level.
- `--mode <main-run|clone|worktree|none>`: run workspace strategy.
- `--branch <branch>`: base branch for clone/worktree.
- `--slug <slug>`: run slug override.
- `--prompt-role <coordinator|worker|reviewer|legacy>`: override role prompt mapping.
- `--allow-overrides`: allow explicit overrides of fields locked by `--subagent`.
- `--include-default-prompt|--exclude-default-prompt`: force toggle default project context.
- `--include-role-instructions|--exclude-role-instructions`: force toggle role instruction block.
- `--include-post-run|--exclude-post-run`: force toggle post-run checklist block.
- `--custom-prompt <text|->`: append custom prompt (`-` reads stdin).

### Subagent Config Defaults

When `--subagent <name>` is set, `apm start` resolves that config from top-level `subagents` in `aihub.json`.
That config can lock `harness`, `model`, `reasoning`, `type`, and `runMode`.

Notes:
- Prefer `--subagent <name>` alone unless you intentionally override locked fields.
- Use `--allow-overrides` when overriding config-driven fields like `--agent`, `--model`, `--reasoning-effort`, `--thinking`, `--mode`, `--branch`, or `--prompt-role`.
- Worker-style subagents commonly use `runMode=worktree`; reviewer-style subagents often use `runMode=none`.
- Lead agents are separate: use `--agent aihub:<id>`, not `--subagent`.
- Lead-agent project sessions are project-scoped and use canonical keys like `project:PRO-123:cloud`.

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
apm start PRO-123 --subagent Worker --slug worker-a --custom-prompt "Implement task 2"
apm start PRO-123 --agent aihub:cloud --custom-prompt "Plan the rollout"
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
