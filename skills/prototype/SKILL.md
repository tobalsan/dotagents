---
name: prototype
description: "Rapid prototyping skill — turn fuzzy idea into fastest viable visible result. Handles two modes: (A) brownfield — adding/exploring a feature inside an existing project (default, most common); (B) greenfield — fresh throwaway from scratch. Use when user asks to 'prototype X', 'mock up X', '/prototype', 'quick spike', 'try X in this app', 'add X quickly', 'rough version', 'just want to see it'. Opposite of /create-frp: no scale probing, no validation gates, no quality bar. Output is discardable, low-commitment, iterable."
---

# Prototype

Idea → visible result, fastest path.

## Prime Directive

**See fast.** Cleanliness, completeness, robustness, edge cases — all secondary. Optimize for time-to-first-render, not maintainability. The artifact (or the diff) is meant to be thrown away or rewritten properly later.

## Mode Detection — do this first

Before anything else, decide which mode applies:

- **Brownfield** (default, most common): user is in an existing project and wants to try a feature/improvement *inside it*. Signals: cwd is a real repo, request mentions "this app", "our X", "add to the dashboard", references existing files. **→ go to Brownfield workflow.**
- **Greenfield**: fresh idea with no existing codebase context. Signals: cwd is empty / `~`, no repo, request describes a standalone concept, user explicitly says "from scratch" / "new project". **→ go to Greenfield workflow.**

If ambiguous: **assume brownfield**. One quick "are we prototyping inside `<repo>` or starting fresh?" if truly unclear.

---

## Brownfield Workflow (default)

Goal: add a tryable version of the feature with **minimum plumbing**, blending into the existing stack so iteration is cheap.

### B1. Echo + quick scan

Restate the request in 2–3 sentences. In parallel (or just before, via subagents if non-trivial), do a fast scan of the existing project to learn:

- **Stack**: framework, language, build tool, package manager
- **Where similar things live**: nearest analogous feature/component/route/endpoint
- **Conventions**: how routes/components/handlers/styles are structured
- **Existing utilities**: state management, fetch wrapper, UI kit, mock/fixture system, dev/test routes
- **Mocking story**: how does the project already fake data? (msw, fixtures, env flag, dev-only seed)
- **Where to mount a throwaway**: a `/dev/`, `/playground/`, `/__scratch__/` route, a Storybook story, a feature flag, a hidden page

Goal of scan: **don't introduce anything the project doesn't already have**. Use what's there.

Confirm understanding with user in one beat, then proceed.

### B2. Offer 3–5 variations

Same as greenfield, but axes are tuned to the existing project. Examples:

- **Mount point**: new `/dev/<name>` route vs Storybook story vs replace existing screen behind flag vs sidebar entry
- **Integration depth**: pure UI mock (no backend) vs UI + faked API vs UI + real API vs full end-to-end
- **Reuse vs new**: extend existing component vs new component cloned from nearest sibling vs ground-up
- **Data**: hardcoded fixture vs reuse existing mock layer vs hit real endpoint
- **Scope**: happy-path screen only vs core interaction loop vs full flow

Format: `**N. Name** — what it shows, key tradeoff (e.g. "fastest but no real data" / "more real but needs auth wired").`

User picks. Default if silent: highest see-fast ratio that still uses real stack.

### B3. Build with the grain

Constraints — different from greenfield because the stack is given:

- **Match the existing stack exactly.** No new frameworks, no new state libs, no new CSS systems. If the app uses Tailwind, use Tailwind. If it uses Redux, use Redux. Even if you'd pick differently for a fresh project.
- **Fewest files possible.** Ideal: one new file, or one file edit. Worst case: a small dir under an existing `dev/`, `playground/`, `__scratch__/`, or `experiments/` folder.
- **Copy the nearest sibling.** Find the closest existing component/route/handler and clone its shape. Don't invent new patterns.
- **Hide it.** Mount under a dev-only route, feature flag, or a path that's obviously not user-facing (`/dev/<slug>`, `/__playground__/<slug>`). Easy to delete = easy to throw away.
- **Reuse the project's mocking layer** (fixtures, msw handlers, faker setup). Don't bolt on a second one.
- **Hardcode aggressively** for anything the prototype doesn't need to prove (auth, perms, IDs, timestamps).
- **Don't touch shared code.** No edits to design tokens, base components, shared types, build config, lockfiles. If you *must* touch one, flag it to the user first.
- **No tests, no types-strictness commitments, no docs.** A single one-line comment is fine if it marks the playground entry as throwaway.
- **No new dependencies.** If a real lib is genuinely needed, ask the user first — most of the time, fake it inline.

Pick the dumbest-possible-thing-that-shows-it within the existing stack.

### B4. Show it

Use the project's normal dev loop:
- `pnpm dev` / `npm run dev` / `bun dev` and navigate to the throwaway route
- Storybook: start it, open the new story
- Backend prototype: hit the dev endpoint with the project's existing client or a one-liner curl
- Notebook / script in repo: run it via the project's runner

State the exact URL or command. If safe, run it. For browser flows, the user is the fastest QA — give them the URL and say what to look at.

### B5. Iterate or rip out

Default endpoint = throwaway. After showing, ask: "keep iterating, try another variation, or rip it out?" Ripping out should be one delete or one revert because the prototype is isolated.

If user wants to keep it → mention `/create-frp` to graduate it into a real, validated implementation. Don't promote it in place — the prototype's shortcuts (no auth, hardcoded data, hidden route) are wrong for production.

---

## Greenfield Workflow (fresh project)

Use when there's genuinely no existing codebase.

### G1. Echo the request

Restate the idea in 2–3 sentences. Confirm. No drilling.

### G2. Offer 3–5 variations

Axes for greenfield:
- **Visual style**: minimal vs rich vs retro vs dashboard
- **Interaction model**: form vs chat vs drag-drop vs CLI
- **Tech stack**: single HTML file vs single-file React (CDN) vs Streamlit vs Python script vs notebook
- **Scope angle**: happy-path-only vs core-loop vs edge-case demo
- **Data**: hardcoded vs faker-generated vs real API

Format: `**N. Name** — what it shows, key tradeoff.`

User picks. Default if silent: highest see-fast ratio.

### G3. Build, fast

- **One file** when possible (single HTML, single Python script, single notebook).
- **Hardcoded data** over fetching/auth/storage. Mock everything external.
- **Inline styles** OK. Inline everything OK.
- **CDN imports** over `npm install` when feasible.
- **No project scaffolding** unless the chosen stack literally requires it.
- **No tests, no lint config, no typechecking commitment, no README.**
- **Skip auth, DBs, env vars** — fake them.

Default location: `~/code/playground/<slug>/`. Don't pollute other repos.

### G4. Show it

- HTML: `open file.html` or `python -m http.server` and a URL
- Python: run it, show output
- Notebook: launch + execute
- CLI: run with sample args
- React/Vue/Svelte: prefer single-file CDN React over `npm create vite` unless reactive build is required

State the exact command. Run it if safe.

### G5. Iterate or discard

Same as brownfield B5: throwaway by default, `/create-frp` if it earns promotion.

---

## What This Skill is NOT

- Not for production features → `/create-frp`
- Not for features going to real users → `/create-frp`
- Not for refactors, bug fixes, or shippable changes → normal workflow
- Not "let me just add tests / clean up / type this properly while I'm here" — resist scope creep aggressively

## Anti-patterns to refuse

- (Brownfield) Introducing a new framework / state lib / CSS system the project doesn't use
- (Brownfield) Editing shared design tokens, base components, or build config "while you're at it"
- (Brownfield) Spinning up a new repo when the feature belongs inside the current one
- (Greenfield) Setting up a full project scaffold for a 50-line idea
- Writing tests "just to be safe"
- Adding strict types when loose JS would render in 30 seconds
- Pulling in state management, routers, ORMs for a one-screen demo
- "Let me also add error handling" — no, not in a prototype
