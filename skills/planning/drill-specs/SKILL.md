---
name: drill-specs
description: Drill into a project idea via systematic interviewing to surface hidden requirements, scope, and tradeoffs. Use when user asks to "drill specs", "flesh out an idea", "interview me about requirements", or wants probing questions on a rough concept. Triggers on "/drill-specs", "help me spec out X", "what questions should I answer about this project". NOT for writing the spec document or implementing—strictly interviewing.
---

# Drill Specs

Interview the user to surface hidden requirements, scope, and tradeoffs for a project idea.

## Input

The user provides a base project idea/concept via `$ARGUMENTS`.

## Workflow

### 1. Codebase Discovery

If inside an existing codebase, launch up to 10 subagents in parallel to explore and understand the current project state. This informs which capabilities already exist vs what's new.

### 2. Structured Interview

Use `AskUserQuestion` (preferred), or sequential text questions to interview the user across these dimensions:

- **Core purpose**: What problem does this solve? Who is it for?
- **Scope & boundaries**: What's in/out of scope? MVP vs future?
- **Implementation**: Tech stack, architecture, integrations, data model
- **UI & UX**: Flows, screens, interactions, accessibility
- **Constraints**: Performance, security, compliance, budget, timeline
- **Tradeoffs**: What are you willing to sacrifice? Speed vs quality vs cost?
- **Edge cases**: Error states, empty states, concurrent access, migrations

Guidelines:
- **ONE decision per turn. Never batch.** No "Q1/Q2/Q3", no "Round 1 of N", no "while you're thinking, also...". Ask about one decision, wait for the answer, then ask the next.
  - Why: batched questions force the user to context-switch across unrelated decisions and produce shallow answers. Single questions let each answer shape the next.
  - **Sub-parts count as batching.** A "Q3" with parts (a) Push policy, (b) Status transition, (c) Cleanup, (d) Pre-flight check is FOUR questions in a trench coat — each part is a separate decision with its own option list. This is forbidden. Pick the one most-blocking decision and ask only that.
  - **The only allowed multi-choice form:** a single decision presented with mutually-exclusive options (a/b/c) where the user picks one. That is one question. Multiple sub-decisions, each with their own a/b/c options, is not.
  - Test: if the user could answer part of your message and leave another part unanswered, you batched. Cut.
- Ask non-obvious, probing questions—skip anything Claude can infer
- Go deep on the current answer before moving on; let it reshape the next question
- Challenge assumptions; surface implicit requirements
- Continue until coverage is comprehensive across the dimensions above, or the user signals stop

## Rules

- **Interview only.** Do NOT implement.
- **Do NOT assume functionality is missing.** Confirm with code search first.
- Stop when the user signals enough, or when no further non-obvious questions remain.
