---
name: handoff
description: Summarize the current conversation and produce a comprehensive hand-off document so another agent or a fresh context window can pick up exactly where work stopped. Use when the user asks to "hand off", "handoff", "create a handoff", "summarize for next agent", "prepare to clear context", or otherwise wants the current session captured for continuation.
---

# Handoff

Create a hand-off document at `./docs/handoff.md` containing a comprehensive report that allows another agent (or this same agent in a fresh context window) to bootstrap and continue the work without loss of fidelity.

## Output location

- Path: `./docs/handoff.md` (relative to the current working directory).
- Create the `./docs/` directory if it does not exist.
- Overwrite any existing `handoff.md` at that path.

## Required contents

The document must capture, with high accuracy:

1. **Initial context** - The original request, repo/project state, and any relevant environment details at the start of the conversation.
2. **Discussion summary** - Everything that has been discussed, including questions raised, options considered, and clarifications received.
3. **Decisions made** - Every decision, with the rationale behind it.
4. **Work completed** - A detailed explanation of what has actually been done so far (files created/modified, commands run, results observed).
5. **Current state** - Where things stand right now, including anything in-progress or partially complete.
6. **Next steps** - If applicable, what remains to be done, in enough detail that the next agent can act immediately.

## Goal

The hand-off must serve as a foundation that fully bootstraps a new context. Optimize for accuracy and completeness over brevity - the next agent will have none of the current conversation history.
