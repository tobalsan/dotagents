---
description: Create token-efficient LLM onboarding docs for a codebase.
---

Your task: generate a single high-signal `docs/llms.md` in Markdown for an LLM/coding agent that WILL have access to this repository.

Primary goal
- Create a compact but comprehensive operating brief so a new coding agent can quickly reason about this project, make safe changes, and avoid breaking invariants.
- Prioritize problem-solving rationale, architecture, design decisions, and practical change workflows.

Audience assumptions
- Reader can inspect code directly.
- Reader needs fast orientation and decision context, not exhaustive explanation.

Output rules
- Output ONLY the Markdown content of the file (no backticks, no extra commentary).
- Optimize for token efficiency:
  - Use dense headings + bullets, not long paragraphs.
  - Avoid repeating facts across sections.
  - Prefer file paths and symbol names over prose when possible.
  - Include only details that change implementation decisions.
- Include concrete file references (repo-relative paths).
- Do NOT include secrets, API keys, passwords, private URLs, or copied env contents.

Required structure

# 1. Project Mission & Problem Framing
- What problem this system solves and for whom (2–4 sentences max).
- Core product/engineering goals that shape implementation.
- Key non-goals and explicit tradeoffs.

# 2. System Model At A Glance
- Major runtime components and their responsibilities.
- One concise dependency/call graph in bullet form (`A -> B -> C`) covering the primary path.
- Deployment/runtime model (single service, multi-service, workers, scheduled jobs, etc.).

# 3. Repository Map For Agents
- Top-level directories with ownership/purpose (only meaningful ones).
- Where to start reading first (ordered list of 5–12 files).
- For each critical module/service:
  - Responsibility boundary.
  - Primary entrypoints (files + key exported symbols/classes/functions).
  - What it must NOT know/call directly (if applicable).

# 4. Core Flows & Execution Paths
Describe the 3–7 highest-value end-to-end flows. For each flow:
- Trigger.
- Path through components/modules (with file references).
- State transitions / side effects (DB writes, events, external calls, cache updates).
- Failure behavior and retry/idempotency behavior (if present).

# 5. Data, State, and Contracts
- Main state stores (DB/cache/blob/files) and what each is source-of-truth for.
- Key entities/models and why they exist (1 line each).
- Critical contracts:
  - Internal contracts (module interfaces, DTOs, events, job payloads).
  - External contracts (API schemas, webhooks, provider payloads).
- Invariants that must hold across writes/flows.

# 6. Design Rationale & Decision Record
- Most important architectural decisions and why they were made.
- Rejected alternatives or known tradeoffs (performance, complexity, cost, latency, consistency).
- Historical constraints still visible in code (legacy seams, transitional patterns).

# 7. Engineering Practices In This Repo
- Build/run/test/lint/type-check commands actually used.
- Branching/release/migration conventions if visible in repo.
- Testing strategy by layer (unit/integration/e2e) and where tests live.
- Logging/observability/error-reporting patterns and where configured.

# 8. Safe Change Guide For Coding Agents
- High-leverage extension points (where to add features cleanly).
- High-risk areas and why they are risky.
- Pre-change checklist (what to read before editing X).
- Post-change checklist (minimum verification commands).
- Common footguns and how to avoid them.

# 9. Fast Context Recovery Appendix
- “If you only have 10 minutes” reading path.
- Glossary of project-specific terms/acronyms (short, only non-obvious terms).
- Open questions/unknowns discovered during analysis.

Level-of-detail guidelines
- DO include:
  - Concrete file paths, key symbols, and cross-module call boundaries.
  - Why decisions exist, not just what exists.
  - Constraints that affect future modifications.
- DO NOT include:
  - Full endpoint inventories, full schemas, or copied large code blocks.
  - Generic explanations of frameworks/languages.
  - Speculation not grounded in repository evidence.

Now:
1. Inspect the repository directly.
2. Extract architecture + rationale + operating constraints.
3. Produce `./docs/llms.md` following the structure above.
