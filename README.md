# Agent Tools

Single source of truth for all coding-agent configuration. The canonical config lives in `~/dotagents` (moved from `~/.agents` so agents that auto-load `~/.agents` do not load everything by default); agent-specific folders use real `commands`/`prompts`, `rules`, and `skills` directories, with individual symlinks per resource (no top-level folder symlinks). This repo keeps shared assets organized so a future `bunx` command can create/update configs and symlinks consistently.

## Layout (canonical)

`~/dotagents/`
- `commands/` shared prompt/command files
- `skills/` shared skills
- `resources/` shared docs/templates
- `rules/` shared rules (e.g. Claude rules)
- `settings/` per-agent config files
  - `claude/`
  - `factory/`
  - `gemini/`
  - `pi/`
  - `opencode/`

## LLM instructions (add/update flow)

1. Put new shared assets in `~/dotagents/commands`, `~/dotagents/skills`, `~/dotagents/resources`, or `~/dotagents/rules`.
2. Put agent-specific config files in `~/dotagents/settings/<agent>/`.
3. Create per-resource symlinks inside each agent’s local folders
4. Use symlinks for instruction files and settings too (see mapping below).

## Symlink map (targets → link locations)

### Claude Code
- `~/dotagents/CLAUDE.md` → `~/.claude/CLAUDE.md`
- `~/dotagents/commands/*` → `~/.claude/commands/*`
- `~/dotagents/rules/*` → `~/.claude/rules/*`
- `~/dotagents/skills/*` → `~/.claude/skills/*`
- `~/dotagents/settings/claude/settings.json` → `~/.claude/settings.json`

### Gemini
- `~/dotagents/GEMINI.md` → `~/.gemini/GEMINI.md`
- `~/dotagents/commands/*` → `~/.gemini/commands/*`
- `~/dotagents/skills/*` → `~/.gemini/skills/*`
- `~/dotagents/settings/gemini/settings.json` → `~/.gemini/settings.json`

### OpenAI Codex CLI
- `~/dotagents/AGENTS.md` → `~/.codex/AGENTS.md`
- `~/dotagents/commands/*` → `~/.codex/prompts/*`
- `~/dotagents/skills/*` → `~/.codex/skills/*`

### OpenAI Factory / Droid
- `~/dotagents/AGENTS.md` → `~/.factory/AGENTS.md`
- `~/dotagents/commands/*` → `~/.factory/commands/*`
- `~/dotagents/skills/*` → `~/.factory/skills/*`
- `~/dotagents/settings/factory/mcp.json` → `~/.factory/mcp.json`

### Pi
- `~/dotagents/AGENTS.md` → `~/.pi/agent/AGENTS.md`
- `~/dotagents/commands/*` → `~/.pi/agent/prompts/*`
- `~/dotagents/skills/*` → `~/.pi/agent/skills/*`
- `~/dotagents/settings/pi/models.json` → `~/.pi/agent/models.json`

### OpenCode
- `~/dotagents/AGENTS.md` → `~/.config/opencode/AGENTS.md`
- `~/dotagents/commands/*` → `~/.config/opencode/commands/*`
- `~/dotagents/skills/*` → `~/.config/opencode/skills/*`
- `~/dotagents/settings/opencode/opencode.json` → `~/.config/opencode/opencode.json`

## Per-resource symlinks

Each agent keeps real `commands`/`prompts`, `rules`, and `skills` directories, but each file/subdir inside is a symlink to `~/dotagents`. This enables per-agent selection by linking only the resources you want.

OpenCode note: `~/.config/opencode/.gitignore`, `bun.lock`, `package.json`, and `node_modules` are real files/dirs (not symlinks).

## Default instruction file

If an agent-specific instruction file is missing, use `~/dotagents/AGENTS.md` as the fallback. It is a copy of `~/dotagents/CLAUDE.md`.
