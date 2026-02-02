# CLAUDE.md RULES

## Behavior
Be extremely concise. Sacrifice grammar for the sake of concision.

Never commit an implementation plan or summary unless explicitly asked to.

## Coding
Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused.

Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability.

Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). Don't use backwards-compatibility shims when you can just change the code.

**Don't create helpers, utilities, or abstractions for one-time operations**. Don't design for hypothetical future requirements. The right amount of complexity is the minimum needed for the current task. Reuse existing abstractions where possible and follow the DRY principle.

## Web Search

Whenever making a web search, you must use the following tools in order, only using the next if the previous is not sufficient:

1. `exa`
2. `firecrawl` MCP
3. `WebSearch` / `WebFetch`

## Linting and Type Checking

Never use `# noqa`, `# type: ignore`, or similar suppression comments to make linting/type checking pass. Always fix the underlying issue properly. Restructure code if needed to satisfy linters without suppression hacks.

## Handle Pre-existing Errors

You must not use the excuse that test failures or type/lint errors are "pre-existing" to ignore them. **You must always fix any failing test, or type/lint error, before declaring your work complete.**.

## Python commands

Always use `uv` to run python commands, unless explicitly stated otherwise.
