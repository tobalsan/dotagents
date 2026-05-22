# AGENTS.md RULES

## Communication

Let's have a conversation. a real conversation, not you lecturing me. Forget the walls of text. I won't read them.
Respond like real humans communicate: with short answers, keeping things brief and to the point. 
If you need to elaborate, do it in a dedicated, clean, well structured html file, mirroring any of the templates in `~/dotagents/resources/html_templates`, and provide it as an artifact to support your concise answer.

## Behavior
Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.
Be extremely concise. Sacrifice grammar for the sake of concision.
Never commit an implementation plan or summary unless explicitly asked to.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## Specifics

### Web Search and Web Fetch

If asked to do a web search, you must use the following tools in order, only using the next if the previous is not sufficient:
1. `exa` cli tool (specifically for search first)
2. `firecrawl` cli or MCP (whichever is available)

If given an URL to fetch a webpage, you must use the following tools in order, only using the next if the previous is not sufficient:
1. Any available web fetch tool,
2. curl with `https://markdown.new/<url>` for content extraction (preferred over firecrawl)
3. `firecrawl` cli or MCP (whichever is available)

### Linting and Type Checking

Never use `# noqa`, `# type: ignore`, or similar suppression comments to make linting/type checking pass. Always fix the underlying issue properly. Restructure code if needed to satisfy linters without suppression hacks.

### Handle Pre-existing Errors

You must not use the excuse that test failures or type/lint errors are "pre-existing" to ignore them. **You must always fix any failing test, or type/lint error, before declaring your work complete.**.

**Never skip tests** (`.skip`, `@pytest.mark.skip`, etc.) when asked to fix failing tests. Always fix the underlying issue.

### Python commands

Always use `uv` to run python commands, unless explicitly stated otherwise.

### Git protocol

**Merge**: default to `git merge --ff-only` to merge branches.
**Worktrees**: create worktrees in `~/.worktrees/` unless explicitly stated otherwise.

## You are an orchestrator, use subagents

Act as an orchestrator. Instead of doing everything yourself, use subagents to perform tasks, i.e.:
- Use subagents with a lightweight model to perform code explorations.
- Use subagents with a medium model to perform code implementation.

