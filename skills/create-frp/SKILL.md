---
name: create-frp
description: "Create a Feature Requirement Prompt (FRP) — hybrid of PRP (Product Requirement Prompt) and a specs-drilling interview. Use when user asks to 'create an FRP', 'draft an FRP', '/create-frp', 'write a feature requirement prompt', or wants to turn a fuzzy feature idea into an implementable spec with concrete validation steps. Runs a strict 3-step probing process — Goal, Scale, Validation. NOT for implementing the feature — strictly produces the FRP document."
---

# Create FRP (Feature Requirement Prompt)

Turn fuzzy feature request into concrete, implementable FRP via 3-step probing.

## Input

User provides fuzzy/high-level feature request via `$ARGUMENTS`.

## Core Rules

- **Plan only.** Never implement the feature. Only produce FRP document.
- **Probe iteratively.** Use `AskUserQuestion` (preferred) or text questions, 1–3 per round. Never dump all questions at once.
- **Don't infer past user intent.** When ambiguous, ask. Don't pick silently.
- **Three steps are sequential gates.** Don't advance until current step has clear, concrete answers.
- **Validation is the make-or-break step.** FRP not done until Step 3 yields a runnable, step-by-step plan another agent can execute blindly.

## Workflow

### Step 0: Codebase Discovery (if applicable)

If inside an existing codebase, dispatch parallel subagents (Explore type) to map current state relevant to the feature. Goal: know what exists vs what's new before probing. Skip for greenfield.

### Step 1: Goal — clarify the end result

Drill the fuzzy request into a concrete description of "what does done look like."

Probe across:
- **Problem**: what concrete pain does this solve?
- **End-user behavior**: what can the user do after the feature ships that they couldn't before?
- **Inputs / outputs**: what data flows in, what comes out?
- **In-scope vs out-of-scope**: what's *explicitly* not part of this?
- **Success definition**: how will we know it works?

Surface hidden complexity. Challenge vague verbs ("manage", "handle", "support") — force concrete behavior.

**Gate**: Can you state in 2–3 sentences what the feature does, for whom, with measurable success? If no, keep probing.

### Step 2: Scale — define profile and minimum viable quality

Probe target deployment profile. This bounds scope and quality bar.

Probe across:
- **User count / load**: solo dev tool? MVP for <100 users? Production w/ high availability?
- **Environment**: local-only? Staging? Multi-region prod?
- **Failure tolerance**: what happens if it breaks — annoyance, lost revenue, page oncall?
- **Performance budget**: latency, throughput targets if any
- **Security / compliance**: auth, PII, audit trails required?
- **Persistence / data**: ephemeral, single-user store, shared DB?
- **Rollback / migration concerns**

Each answer narrows what's worth building. Solo MVP ≠ production HA. Don't gold-plate solo tools; don't ship prod features without proper guardrails.

**Gate**: Profile articulated as one of {solo dev, internal MVP, production-low-criticality, production-HA, ...} with concrete constraints. If no, keep probing.

### Step 3: Validation — runnable verification plan (CRITICAL)

This is the most important step. The FRP is **not done** until validation is concrete enough that an unfamiliar agent can execute it without guessing.

Probe until you have answers for all of:

- **Where to run**: exact path, branch, worktree to use (e.g. `~/projects/.workspaces/feature-x`)
- **How to set up**: install commands, env vars, secrets, services to start
- **What to run**:
  - Test commands (exact: `pnpm test path/to/file.test.ts`, `uv run pytest tests/feature_x.py`)
  - Lint / typecheck commands
  - Build commands
- **Testing modality**:
  - Pure unit/integration? Then which framework, which test files.
  - CLI? Then exact command to invoke and expected output.
  - Browser? Then which URL, which flow to navigate, what to look for. Specify if a browser-automation skill should be used (e.g. `agent-browser`, `browser-tools`, `claude-in-chrome`, `webapp-testing`).
  - HTTP API? Then curl/HTTPie commands and expected status codes / response shape.
- **Skills / tools to use**: name them explicitly (e.g. `webapp-testing`, `agent-browser`, `verification-before-completion`)
- **Acceptance criteria**: bullet list of concrete observable behaviors the agent must verify, each tied to a command or check
- **Success vs failure signals**: what output proves success; what output indicates regression

**Anti-patterns to reject**:
- "Make sure it works"
- "Run the tests" (which tests?)
- "Verify in the browser" (which URL? what flow?)
- "Check edge cases" (which ones?)

**Gate**: A fresh agent could execute the validation plan top-to-bottom without asking a single clarifying question. If not, keep probing.

### Step 4: Write FRP

Once all three gates pass, write FRP using the template at [references/frp_template.md](references/frp_template.md).

Before writing, ask user where to save:
1. **Workspace/repo** — `docs/frp/<slug>.md` in active workspace
2. **AIHub project** — use `apm` skill
3. **Linear comment** — if tied to a Linear issue, use `linctl comment update <COMMENT_ID> --body "..."`
4. Custom path if user specifies

Default to option 1 if unclear.

### Step 5: Quality gates

Before declaring FRP done, verify against [references/quality_gates.md](references/quality_gates.md). If any gate fails, loop back to relevant step.

## When to dispatch subagents

- **Step 0 codebase discovery**: parallel Explore agents — yes, when codebase non-trivial
- **External research**: only if validation requires unfamiliar libraries/APIs — keep targeted (1–2 lookups)
- **Don't over-engineer**: match research depth to feature complexity. Login button doesn't need 10 subagents.
