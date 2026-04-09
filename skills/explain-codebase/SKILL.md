---
name: explain-codebase
description: Explore an unfamiliar codebase and produce a concise high-level explanation of its purpose, main concepts, inner workings, and a flow diagram from input to output through the main actor components. Use when the user asks to "explain this codebase", "give me a high-level overview", "what does this repo do", "help me understand this project", or wants onboarding-style understanding of a repository. Supports optional focus arguments (e.g., a specific subsystem, directory, or aspect to emphasize).
---

# Explain Codebase

Goal: give the user a high-level understanding of the codebase — the main problem it solves, the core concepts, and how data/control flows from input to output through the main actor components.

## Inputs

- The current codebase (working directory).
- Optional user-provided focus arguments: a specific area, subsystem, directory, language, or question to emphasize. If provided, scope the exploration and explanation around that focus while still giving overall context.

## Procedure

1. **Survey the repo structure**
   - List top-level files and directories.
   - Read entry points and metadata: `README*`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, `Dockerfile`, `docker-compose*`, `AGENTS.md`, `CLAUDE.md`, etc.
   - Identify language(s), framework(s), and build/run commands.

2. **Identify the main purpose**
   - From README and config metadata, extract what problem the project solves and who it is for.
   - If no README, infer from package name, dependencies, and entry points.

3. **Find entry points and main actors**
   - Locate `main`, `index`, `app`, CLI definitions, server bootstrap, route handlers, job runners, etc.
   - Map the major modules/packages and their responsibilities.
   - Identify external boundaries: user input, HTTP/API, CLI args, queues, databases, third-party services.

4. **Trace the primary flow**
   - Pick the most representative use case (or the user's focus if provided).
   - Trace it from input through the main components to output. Note key transformations and the components responsible.

5. **Apply optional focus**
   - If the user provided focus arguments, bias steps 3–4 toward that area: go deeper there, summarize the rest only as needed for context.

## Output

Respond concisely with these sections:

1. **Purpose** — 1–3 sentences on the problem the codebase solves.
2. **Tech stack** — language(s), key frameworks, notable dependencies.
3. **Main concepts** — bullet list of core domain/architectural concepts.
4. **Main actor components** — bullet list of major modules/services and their responsibilities, with file paths.
5. **High-level flow diagram** — ASCII or Mermaid diagram showing input → main components → output for the primary use case.
6. **How to run / entry points** — minimal commands or files to start exploring.
7. **Focus notes** — only if focus arguments were given; deeper details on the requested area.

## Style

- Be concise. Prefer bullets over prose.
- Use repo-relative or absolute file paths so the user can jump to them.
- Do not dump code; quote only short load-bearing snippets if essential.
- Do not invent components — only describe what exists in the repo.
