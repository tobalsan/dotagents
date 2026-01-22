---
description: Create a project overview document for a codebase.
---

Your task: generate a single concise ARCHITECTURE_OVERVIEW.md in Markdown that I can paste into another AI chat which WILL NOT have access to this codebase.

General goals
- Explain the system like you’re briefing a senior engineer who hasn’t seen the repo.
- Focus on *architecture and responsibilities*, not implementation details.
- Keep it under ~1,200 words. Be selective.

Output rules
- Output ONLY the Markdown content of the file (no backticks, no extra commentary).
- Use clear headings and bullet lists.
- Do NOT include any secrets, API keys, passwords, or private URLs.

Required structure

# 1. Project Snapshot
- 2–4 sentences: what this project is, who uses it, and the main problem it solves.
- Key high-level constraints (scale, single-tenant vs multi-tenant, main interface like Slack/Web/etc.).

# 2. Tech Stack & Runtime
- Languages, main frameworks, and key infrastructure pieces (e.g. FastAPI, LangGraph, Redis, Postgres, Inngest, MinIO, etc., if present).
- How it is typically run (e.g. Docker Compose services, entrypoint commands).

# 3. Top-Level Structure
- Brief description of the top-level directories and what they own.
- For each major service/module (e.g. “edge service”, “orchestrator”, “shared libs”), give:
  - Responsibility in 1–2 sentences.
  - Key entrypoints (file paths) and important submodules (only the important ones).
- Mention any clear architectural patterns (e.g. layered architecture, hexagonal, event-driven, etc.).

# 4. Core Workflows / Data Flows
Describe the 3–6 most important end-to-end flows at a high level. For each:

- Name of the workflow (e.g. “Slack message → intent routing → agent run → Slack reply”).
- Step-by-step, but short, focusing on:
  - Which components/services are involved.
  - How data moves between them (HTTP, events, queues, function calls).
  - Any important background jobs / schedulers / workers.

Avoid:
- Listing every route or function.
- Pseudo-code or long algorithm explanations.

# 5. Data & State
- Main databases and storage systems used and what they store (high level).
- Important models/entities and their role (1 line each; no full schema).
- How state is shared across services (e.g. DB, message bus, in-memory cache).

# 6. Integrations & External Dependencies
- External APIs / services (e.g. Slack, payment providers, CRMs, etc.).
- For each: what it’s used for and which parts of the code talk to it.

# 7. Extension Points, Constraints, and Gotchas
- Where a future developer/AI could plug in new features cleanly (e.g. adding a new agent, new workflow, new integration).
- Known limitations, fragile areas, or important invariants to respect.
- Any non-obvious design decisions that matter for future changes.

Level of detail guidelines
- DO include: names of key services, modules, directories, and a few critical classes/functions where they define important boundaries.
- DO include: high-level contracts between parts of the system (who calls whom and why).
- DO NOT include: long lists of endpoints, every config option, or test details.
- DO NOT paste raw code.

Now:
1. Inspect the repository.
2. Synthesize the information.
3. Produce the `./ai_docs/ARCHITECTURE_OVERVIEW.md` following the instructions above.
