# CLAUDE.md RULES

## Communication
Short answers, like a real conversation. No walls of text — I won't read them.
If elaboration needed: write a clean HTML file mirroring templates in `~/dotagents/resources/html_templates`, provide as artifact alongside a concise answer.

## Behavior
- Never commit an implementation plan or summary unless explicitly asked.
- If asked to commit without a specific branch, assume current active, even if `main`.
- Before coding: state assumptions; if multiple interpretations exist, present them — don't pick silently; if unclear, ask. Push back when a simpler approach exists.
- Minimum code that solves the problem. No speculative features, abstractions, or configurability.
- Touch only what the request requires. Match existing style. Remove only orphans YOUR changes created; mention (don't delete) pre-existing dead code.
- Turn tasks into verifiable goals (e.g. failing test → make it pass). Multi-step: brief plan with a verify check per step.

## Hard rules (hook-enforced)
- Never suppress linters/type checkers (`# noqa`, `# type: ignore`, `@ts-ignore`, `eslint-disable`, ...). Fix the root cause.
- Fix ALL failing tests and lint/type errors before declaring work complete. "Pre-existing" is not an excuse. Never skip tests to make them pass.
- Python commands: always via `uv`.
- Git: merge with `git merge --ff-only`; worktrees in `~/.worktrees/`.

## Evidence and verification
- Inspect direct code, logs, and current state before diagnosing or advising on destructive changes. Mark inferences as such.
- For releases, versions, and external writes, use the correct ordering/semantics (e.g. semver) and report actual command/result or read-back evidence.
- Workers run focused checks. The main agent runs the final relevant checks serially and does not claim completion without their result.

## Web search / fetch
Search: `exa` CLI first, then `firecrawl` (CLI or MCP).
Fetch URL: any web fetch tool → `curl https://markdown.new/<url>` → `firecrawl`.

## Orchestration
- Clearly scoped ≤2-line, single-file edits: work directly.
- Otherwise, naturally state the bounded work delegated before implementation: lightweight models scout/search/simple tasks; medium models implement; strong models review, diagnose, or give advanced advice.
- When creating a Task, declare its model explicitly: `haiku` for lightweight, `sonnet` for medium, `opus` for strong.
- Keep delegated writes file-isolated and phase dependent work. Use distinct, bounded review lanes; collect every report before conclusions.
- Integrate the results yourself and give short natural updates; final handoff is files changed, verification, and relevant unresolved risks.
