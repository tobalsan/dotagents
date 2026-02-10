---
name: drill-specs
description: Build comprehensive specs for a project idea through systematic interviewing. Use when user asks to "drill specs", "flesh out an idea", "build specs", "interview me about requirements", or wants to turn a rough project concept into a detailed specification. Triggers on requests like "/drill-specs", "help me spec out X", "what questions should I answer about this project". NOT for implementing features—strictly planning and specification.
---

# Drill Specs

Build a comprehensive specification for the user's project idea through structured interviewing.

## Input

The user provides a base project idea/concept via `$ARGUMENTS`.

## Workflow

### 1. Codebase Discovery

If inside an existing codebase, launch up to 10 subagents in parallel to explore and understand the current project state. This informs which capabilities already exist vs what's new.

### 2. Structured Interview

Use `AskUserQuestion` (preferred) or sequential text questions to interview the user across these dimensions:

- **Core purpose**: What problem does this solve? Who is it for?
- **Scope & boundaries**: What's in/out of scope? MVP vs future?
- **Implementation**: Tech stack, architecture, integrations, data model
- **UI & UX**: Flows, screens, interactions, accessibility
- **Constraints**: Performance, security, compliance, budget, timeline
- **Tradeoffs**: What are you willing to sacrifice? Speed vs quality vs cost?
- **Edge cases**: Error states, empty states, concurrent access, migrations

Guidelines:
- Ask non-obvious, probing questions—skip anything Claude can infer
- Go deep on answers that reveal hidden complexity
- Challenge assumptions; surface implicit requirements
- Do NOT ask all questions at once—interview iteratively, 1-3 questions per round
- Adapt follow-up questions based on previous answers

### 3. Spec Documentation

Once the interview is complete, write a structured spec document to the project directory. Include:

- Problem statement
- Goals & non-goals
- User stories / use cases
- Technical architecture
- Data model
- UI/UX flows
- Open questions / risks

## Rules

- **Plan only.** Do NOT implement anything.
- **Do NOT assume functionality is missing.** Confirm with code search first.
- Continue interviewing until the spec is comprehensive—don't stop early.
