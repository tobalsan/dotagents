---
name: new-orchestrator-project
description: Bootstrap a new Linear <-> AIHub orchestrator project end-to-end. Use whenever the user wants to create, spin up, scaffold, or bootstrap a new orchestrator project, a new AIHub project, or a Linear project that the orchestrator daemon should poll — even if they only say "new orchestrator project", "set up a project for the daemon", "init-project", or name a project they want agents to start working on. Runs `aihub orchestrator init-project`, links the Linear project to an initiative and lead, then restarts and verifies the gateway so the daemon actually picks it up.
---

# New Orchestrator Project

Bootstrap a project so Linear and the AIHub orchestrator daemon are lined up: a Linear project, a local project folder, a `WORKFLOW.md`, the initiative/lead wiring, and a gateway restart so the daemon starts polling it.

`aihub orchestrator init-project` does the heavy lifting but leaves three gaps this skill closes: it does **not** link an initiative, set a lead, or restart the gateway. Without the restart the daemon never sees the project (the projects list is read once at `start()`, not hot-reloaded).

## Inputs

Gather these before acting. Ask only for what's missing — infer sensible defaults.

- **Project name** (required) — human-readable, e.g. `"Orchestrator Extension — Follow-ups"`. Becomes the Linear project name and the folder safename.
- **Host** (default `ams`) — where aihub/the gateway runs. `ams` (or any non-local host) → run over SSH. `local`/`localhost` → run commands directly.
- **Initiative** (optional, default `AIHub`) — Linear initiative to link. Skip linking if the user says none.
- **Lead** (optional, default the current user / `me`) — Linear project lead.
- **Profile** (default `worker`) — subagent profile for `WORKFLOW.md`.

## Process

### 1. Run init-project on the host

Build the command, then run it on the target host:

```bash
aihub orchestrator init-project "<name>" --profile <profile>
```

It reads `extensions.orchestrator.projectsRoot` (default `~/projects`), creates the Linear project under the inferred team, creates `<projectsRoot>/<safename>`, writes `WORKFLOW.md` with `tracker.project_slug` set to the new project's `slugId`, and appends the folder to `extensions.orchestrator.projects` in `aihub.json`.

**Preconditions it enforces** (surface the error and stop if hit): the folder must not already exist, and no Linear project with the same name may already exist.

**Capture the output line** `Created Linear project <name> (<slugId>)` — you need the name to find the project in the next step.

#### Running on a remote host (e.g. `ams`)

Two gotchas, both real:

- The plain `ssh` command is shadowed by kitty's ssh kitten and fails with `The SSH kitten is meant to run inside a kitty window`. **Use the real binary: `/usr/bin/ssh`.**
- `aihub` (and `pnpm`) are not on the non-interactive PATH; they live in the login shell (fnm). **Run through a login shell** and strip the harmless `can't change option: zle` lines:

```bash
/usr/bin/ssh ams 'zsh -lic "aihub orchestrator init-project \"<name>\" --profile worker"' 2>&1 \
  | grep -v "can't change option: zle"
```

If the global `aihub` is missing on the host, fall back to the repo runner:
`/usr/bin/ssh ams 'cd ~/code/aihub && node_modules/.bin/tsx apps/gateway/src/cli/index.ts orchestrator init-project "<name>" --profile worker'`.

#### Running locally

Run `aihub orchestrator init-project "<name>" --profile <profile>` directly — no SSH, no login-shell wrapper needed.

### 2. Link initiative + lead in Linear

`init-project` creates the project under the inferred team only. Wire the rest with the Linear MCP tools:

1. Find the project id: `mcp__claude_ai_Linear__get_project` (query by the exact name).
2. `mcp__claude_ai_Linear__save_project` with `id`, `addInitiatives: ["<initiative>"]`, and `lead: "<lead>"`.

Skip whichever the user opted out of. If the initiative name is ambiguous, confirm rather than guess.

### 3. Restart + verify the gateway

The daemon reads its projects list once at startup, so the new project stays idle until a restart.

**Check for active runs first.** A restart kills in-flight orchestrator workers. If a run might be active, confirm with the user before restarting — never restart a busy daemon silently.

```bash
# remote
/usr/bin/ssh ams 'zsh -lic "aihub gateway restart"' 2>&1 | grep -v "can't change option: zle"
/usr/bin/ssh ams 'zsh -lic "aihub gateway status"'  2>&1 | grep -v "can't change option: zle"
# local
aihub gateway restart && aihub gateway status
```

`status` should report `running pid <n>`. Note the gateway API is on its own port (e.g. `4000`); the UI port (`3000`) returns HTML, so don't curl the UI port to check health.

### 4. Report

Give the user a tight summary:

- Linear project URL + slugId
- Local folder path + that `WORKFLOW.md` was written
- Initiative / lead linked (or skipped)
- Gateway status after restart

## Notes

- **Generated `WORKFLOW.md` is minimal.** Until the richer template ships (tracked as ALG-148), the body is just a couple of lines. If the user wants the full claim/Linear/review procedure (`## DO THIS FIRST`, status rules, code+review flow), offer to append it from the canonical example at `cloudi-fi/cloudihub/config/WORKFLOW.md`. Editing `WORKFLOW.md` does not require a gateway restart only if the daemon re-reads it per tick — if unsure, restart.
- **One initiative, one team workspace.** `inferProjectTeamIds()` resolves the team automatically; you usually don't choose it.
- Reference: `packages/extensions/orchestrator/README.md` ("Create Linear Project + WORKFLOW.md") documents flags and behavior.
