---
name: drill-specs
description: Drill into a project idea via systematic interviewing to surface the goal, intended outcome, and tradeoffs—the "why", not the "how". Use when user asks to "drill specs", "flesh out an idea", "interview me about requirements", or wants probing questions on a rough concept. Triggers on "/drill-specs", "help me spec out X", "what questions should I answer about this project". NOT for writing the spec document, designing the implementation, or coding—strictly interviewing for intent.
---

# Drill Specs

Interview the user to pin down what they actually want and why—the intended end-state and tradeoffs—not how it gets built.

## Input

The user provides a base project idea/concept via `$ARGUMENTS`.

## Workflow

### 1. Codebase Discovery

If inside an existing codebase, explore first (subagents in parallel) only to avoid asking about context that is already settled. Do not let code discovery turn the interview toward implementation.

### 2. Outcome Interview

Use `AskUserQuestion` (preferred), or sequential text questions. Drill these lenses—they are angles to probe, not a checklist to march through:

- **The win**: What does the world look like when this works? What observably changes?
- **Who & why**: Who feels what differently? Why does this matter enough to build?
- **Definition of done**: What observable outcome must it nail vs merely improve? What's the one non-negotiable end-state?
- **Failure**: What would make you call this a failure even if it shipped on time?
- **Tradeoffs**: Which outcomes can degrade, and which cannot? What are you willing to sacrifice—speed, cost, scope, polish—to protect the core outcome?
- **Boundaries**: What's deliberately out of scope, now and maybe forever?

Guidelines:
- **Every "how" question is a smell.** Tech stack, screens, data model, edge cases—skip them. Ask a how-question ONLY when the answer would change the *goal* itself. Default: don't.
- **ONE decision per turn. Never batch.** No "Q1/Q2/Q3", no "Round 1 of N", no "while you're thinking, also...". Ask one decision, wait, then ask the next.
  - Why: batched questions force context-switching across unrelated decisions and produce shallow answers. Single questions let each answer reshape the next.
  - **Sub-parts count as batching.** A "Q3" with parts (a)(b)(c)(d) is four questions in a trench coat. Pick the single most-blocking decision; ask only that.
  - **Allowed:** one decision with mutually-exclusive options (a/b/c), user picks one. Multiple sub-decisions each with their own options is not.
  - Test: if the user could answer part and leave the rest, you batched. Cut.
- Ask non-obvious, probing questions—skip anything Claude can infer
- Go deep on the current answer before moving on; let it reshape the next question
- Challenge assumptions; surface the implicit intent behind a stated feature
- Do not ask what to build next. Ask what must become true for the user, customer, or business.

## Rules

- **Interview only.** Do NOT implement or design.
- **Stay on "why".** Surface intent and outcome; treat implementation detail as out of scope unless it defines the goal.
- **Do NOT assume functionality is missing.** Confirm with code search first.
- **Done when** you could hand the "why" to three engineers and they'd agree on the goal—even if they'd build it three different ways. Stop there, or when the user signals enough.
