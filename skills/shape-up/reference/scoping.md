# Scoping 

The purpose of scoping is to analyze a shaped projectand decompose the solution into a proposed list of logical, independent, and vertically-sliced **scopes**. 
You define the high-level map of the project, not individual tasks.
All the scopes for a project goes inside the project's corresponding scope file.

## Core Principles

You MUST strictly adhere to these principles:

1. **Vertical Slices, Not Horizontal Layers:** Identify functional, end-to-end pieces of the user experience. You are forbidden from creating horizontal scopes like "API Setup," "Database Migrations," or "UI Mockups." Correct scopes integrate these layers (e.g., "User Sign-Up Flow" or "Publish First Draft").
2. **Independence is Key:** Each scope must be completable without being blocked by another scope. Identify the "fault lines" in the project that allow work to be cleanly separated.
3. **Meaningful, Concrete Results:** Each scope must represent tangible progress. When a scope is "done," a distinct part of the feature should be demonstrably working.
4. **Strictly Adhere to the Pitch:** You cannot invent new features or functionality. Every scope must be directly derived from the `Solution`, `Rabbit Holes`, and `No Gos` sections of the provided project pitch.
5. **Single-Run Scope Size:** Each scope must be small enough to complete with high confidence in one agent run and context window. If confidence is anything less than high, split the scope until it is.
6. **Standalone Verifiability:** Each scope must be verifiable without relying on any other scope. Exceptions are rare and must be called out explicitly in the verification steps.

## Instructions

When invoked, you must follow these steps:

1. **Locate and study the Pitch:** Find and study the project file in `~/projects`. This file contains the complete Shape Up project pitch.
2. **Locate and study the existing scopes:** if the scope files already exist for this project (`{PROJECT_NAME}.scopes.md` file in the same folder), study it to understand the plan so far. Skip this step if the file doesn't exist (new project).
3. **Analyze existing codebase:** If the project has existing code, study the codebase with up to 10 sub-agents to analyze it to identify the core components and user flows. Skip this step if no existing codebase (new project).
4. **Analyze the Solution Section:** Deeply understand the defined specs. This is your primary source for identifying the project's core components and user flows.
5. **Identify Vertical Slices:** Look for distinct, user-facing verbs and nouns that represent completable pieces of functionality. Examples: "User *creates* a new conversation," "Owner *views* the conversation list," "System *archives* old messages."
6. **Draft Scope Titles:** For each slice identified, create a clear, descriptive title that captures the essence of that vertical slice.
7. **Determine the First Slice:** Critically evaluate your drafted scopes. Designate exactly ONE scope as `is_first_slice: true`. This must be the most central, novel, or risky part of the project—the one that must be proven to work for the rest of the project to be viable.
8. **Define verification steps:** For each scope, define the criteria that must be met for it to be considered complete.
9. **Classify Scope Levels:** 
   - Default to `must_have` for any scope essential to solving the core problem defined in the pitch
   - Assign `nice_to_have` only if the pitch explicitly describes a feature as optional, a "stretch goal," or something that could be cut to fit the appetite
10. **Set Initial Status:** All proposed scopes at this stage have `passes: false` by default.

**Final Review:** Before generating the final scope file content, review your list against the Core Principles. Check for:
   - Any horizontal layers that should be refactored
   - True independence between scopes
   - Scope size is small enough for one agent run
   - Alignment with the pitch content

## Property Reference

### Scope Object Structure

Each scope object must contain exactly these properties:

- `title` (string): A concise, descriptive name for the scope (e.g., "User Login Flow")
- `is_first_slice` (boolean): `true` for exactly one scope (the most critical), `false` for all others
- `scope_level` (string): Either `must_have` (default) or `nice_to_have` (for optional features)
- `verification_steps` (array): A list of strings that define the criteria for the scope to be considered complete
- `passes` (boolean): `true` if the scope is complete and all acceptance criteria are met, `false` otherwise

## Output

Write your final response as clean markdown content, listing scopes separated by a new line. 

**Example Output:**

```markdown
description: Create the Conversation List View
is_first_slice: true
scope_level: must_have
verification_steps:
  - page displays the conversation
  - conversation list is not empty 
passes: false

description: Owner can clickc action buttons
is_first_slice: false 
scope_level: must_have
verification_steps:
  - buttons are displayed when logged as owner 
  - buttons are not displayed when logged as non-owner
  - buttons "archive" and "delete" are displayed when logged as owner
passes: false

description: Archive conversation 
is_first_slice: false
scope_level: nice_to_have
verification_steps:
  - conversation is archived when owner clicks "archive" button
passes: false
```

## Best Practices

- Always think in terms of user-facing functionality, not technical implementation
- Each scope should represent something a user can actually interact with or benefit from
- Consider dependencies but ensure each scope can still deliver value independently
- The first slice should be the piece that proves the core concept works
- Respect the appetite constraints mentioned in the pitch when determining scope levels
- Never add features or functionality not explicitly mentioned in the pitch

IMPORTANT: Plan only. Do NOT implement anything. Do NOT assume functionality is missing; confirm with code search first, unless it's a new project. 

