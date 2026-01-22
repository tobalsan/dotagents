# Agent Tools

Single source of truth for all coding-agent configuration. The canonical config lives in `~/.agents`; agent-specific folders use real `commands`/`prompts`, `rules`, and `skills` directories, with individual symlinks per resource (no top-level folder symlinks). This repo keeps shared assets organized so a future `bunx` command can create/update configs and symlinks consistently.

## Layout (canonical)

`~/.agents/`
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

1. Put new shared assets in `~/.agents/commands`, `~/.agents/skills`, `~/.agents/resources`, or `~/.agents/rules`.
2. Put agent-specific config files in `~/.agents/settings/<agent>/`.
3. Create per-resource symlinks inside each agent’s local folders
4. Use symlinks for instruction files and settings too (see mapping below).

## Symlink map (targets → link locations)

### Claude Code
- `~/.agents/CLAUDE.md` → `~/.claude/CLAUDE.md`
- `~/.agents/commands/*` → `~/.claude/commands/*`
- `~/.agents/rules/*` → `~/.claude/rules/*`
- `~/.agents/skills/*` → `~/.claude/skills/*`
- `~/.agents/settings/claude/settings.json` → `~/.claude/settings.json`

### Gemini
- `~/.agents/GEMINI.md` → `~/.gemini/GEMINI.md`
- `~/.agents/commands/*` → `~/.gemini/commands/*`
- `~/.agents/skills/*` → `~/.gemini/skills/*`
- `~/.agents/settings/gemini/settings.json` → `~/.gemini/settings.json`

### OpenAI Codex CLI
- `~/.agents/AGENTS.md` → `~/.codex/AGENTS.md`
- `~/.agents/commands/*` → `~/.codex/prompts/*`
- `~/.agents/skills/*` → `~/.codex/skills/*`

### OpenAI Factory / Droid
- `~/.agents/AGENTS.md` → `~/.factory/AGENTS.md`
- `~/.agents/commands/*` → `~/.factory/commands/*`
- `~/.agents/skills/*` → `~/.factory/skills/*`
- `~/.agents/settings/factory/mcp.json` → `~/.factory/mcp.json`

### Pi
- `~/.agents/AGENTS.md` → `~/.pi/agent/AGENTS.md`
- `~/.agents/commands/*` → `~/.pi/agent/prompts/*`
- `~/.agents/skills/*` → `~/.pi/agent/skills/*`
- `~/.agents/settings/pi/models.json` → `~/.pi/agent/models.json`

### OpenCode
- `~/.agents/AGENTS.md` → `~/.config/opencode/AGENTS.md`
- `~/.agents/commands/*` → `~/.config/opencode/commands/*`
- `~/.agents/skills/*` → `~/.config/opencode/skills/*`
- `~/.agents/settings/opencode/opencode.json` → `~/.config/opencode/opencode.json`

## Per-resource symlinks

Each agent keeps real `commands`/`prompts`, `rules`, and `skills` directories, but each file/subdir inside is a symlink to `~/.agents`. This enables per-agent selection by linking only the resources you want.

OpenCode note: `~/.config/opencode/.gitignore`, `bun.lock`, `package.json`, and `node_modules` are real files/dirs (not symlinks).

## Default instruction file

If an agent-specific instruction file is missing, use `~/.agents/AGENTS.md` as the fallback. It is a copy of `~/.agents/CLAUDE.md`.
