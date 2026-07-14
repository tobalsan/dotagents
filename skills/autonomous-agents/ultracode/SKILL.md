---
name: ultracode
description: "Maximal multi-agent orchestration mode. Use whenever the user's prompt contains \"ultracode\", asks for exhaustive or comprehensive treatment of a substantive task (thoroughly audit, be exhaustive, leave no stone unturned), or explicitly requests multi-agent orchestration (fan out agents, orchestrate with subagents). Do NOT trigger for conversational turns or trivial mechanical edits."
---

# Ultracode

Ultracode is an orchestration discipline, not a tool. It turns one task into a structured fleet of subagents so the result is more comprehensive (parallel coverage), more confident (independent adversarial checks), and larger-scale (work no single context can hold) than solo execution. Treat an 'ultracode' request as a standing opt-in: token cost is not a constraint — spend it on coverage and verification, never on redundant identical agents.

## Prerequisites and degradation

Use the strongest parallelism primitive available, in order:

1. **A workflow/orchestration tool** (deterministic scripts spawning agents) — use it per its own docs; this skill supplies the process and patterns.
2. **A subagent/task tool** (e.g. `Agent`, `Task`) that runs agents concurrently — batch independent spawns in a single message/turn so they actually run in parallel.
3. **No subagents at all** — run the same phases yourself sequentially with fresh, self-contained checklists per phase. You lose independence between finder and verifier; compensate by writing findings down first, then attacking them in a separate pass as a hostile reviewer.

## The process

Every substantive task runs as phases. You stay the orchestrator: read each phase's results before designing the next fan-out. Never delegate the synthesis.

### 0. Scout inline

Before any fan-out, spend a few cheap searches yourself (list files, grep, read entry points, scope the diff) to discover the **work-list**: the concrete items agents will fan out over. You don't need to know the shape of the task before starting — only before each orchestration step. Fanning out blind produces overlapping, unfocused agents.

### 1. Understand

Parallel readers, one per subsystem/area of the work-list, each returning a structured summary (purpose, key files, invariants, risks). Merge into a map yourself.

### 2. Design (when the solution space is wide)

Judge panel: N agents each produce an independent approach from a distinct angle (e.g. MVP-first, risk-first, compatibility-first). Parallel judges score them. Synthesize from the winner, grafting the best ideas from runners-up. Skip when the design is obvious — phases are tools, not ceremony.

### 3. Implement

Fan out edits with **strict file isolation**: no two concurrent agents touch the same file. If isolation is impossible, serialize those agents or use worktree/branch isolation when the primitive supports it. Each agent gets a self-contained prompt (context, exact files, verifiable done-condition) — subagents share none of your context.

### 4. Review and verify

Findings that merely sound plausible are the failure mode ultracode exists to kill. Two stages:

- **Find**: parallel finders, one per dimension (correctness, security, perf, edge cases, test coverage), each blind to the others.
- **Adversarial verify**: for each fresh finding, spawn 2–3 independent skeptics prompted to *refute* it ("default to refuted if uncertain") against the actual files/logs, not the finder's excerpt. With 3 skeptics a finding survives on majority non-refutation; with 2, any refutation kills it. When a finding can fail in different ways, give each verifier a distinct lens instead of identical refuters — diversity catches what redundancy can't.

### 5. Synthesize

Integrate results yourself. Deduplicate, resolve conflicts between agents, run the final relevant checks serially. Hand off: files changed, verification evidence, unresolved risks. Never report an agent's claim as verified unless a verify stage or your own check confirmed it.

## Orchestration rules

- **Pipeline over barrier.** Let each item flow through all its stages independently; only synchronize all items when a stage genuinely needs the full prior set (dedup across findings, early-exit on zero results, "compare against the other findings"). "Conceptually separate stages" and "cleaner code" do not justify a barrier — it wastes the fast agents' wall-clock waiting on the slowest. Phase boundaries (understand → design → implement) are legitimate sync points; pipelining applies within a phase and across independent work-list items — e.g. verify each finding as soon as its finder returns.
- **Structured returns.** Tell every agent its final message is data for the orchestrator, not prose for a human. Specify an exact JSON shape and parse it. In discovery/review phases, treat missing/failed agents as `null` and filter — one dead agent must not sink the phase. In the implement phase, a failed agent must be retried or surfaced in the handoff, never silently dropped.
- **Model tiering.** Set each agent's model explicitly by difficulty: lightweight model for mechanical scouting/greps, medium model for implementation and standard review, strong model only for the hardest design/judge/verify calls. If the primitive can't set per-agent models, skip tiering.
- **Loop until dry** for unknown-size discovery (bugs, issues, edge cases): keep spawning finder rounds until K (usually 2) consecutive rounds surface nothing new. Fixed counts ("find 10 bugs") miss the tail. Dedup new findings against *everything seen*, including rejected ones, or refuted findings resurface every round and the loop never converges.
- **Multi-modal sweep** when one search angle can't find everything: parallel agents each searching a different way (by-name, by-content, by-caller, by-time).
- **Completeness critic**: end large efforts with one agent asking "what's missing — an angle not swept, a claim unverified, a file unread?" Its answer seeds the next round.
- **No silent caps.** If you bound coverage (top-N, sampling, skipped areas), say so in the handoff — silent truncation reads as full coverage.

## Scale calibration

Match fleet size to the ask: 2–3-skeptic adversarial verification is the default; "thoroughly audit" gets a large finder pool and a synthesis stage on top. A quick check may drop to a few finders and single-skeptic verification as an explicit calibration override. Solo execution remains correct for conversational answers and trivial edits — invoking agents there is waste, not rigor.

These patterns compose freely; invent new harnesses (tournaments, staged escalation, self-repair loops) when the task calls for it.
