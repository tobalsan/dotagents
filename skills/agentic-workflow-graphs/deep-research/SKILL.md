---
name: deep-research
description: Run a long-horizon research campaign — a full research graph re-executed over many iterations until the field is exhausted. Use when the user explicitly asks for a deep research campaign, an exhaustive/marathon investigation, or research that should keep going until it stops finding anything new ("deep research X", "run a research campaign on X", "exhaustively research X"). NOT for ordinary research requests, single-session investigations, or anything expected to answer within one context window — use multi-agent-research for those.
---

# Deep Research

A research campaign that outlives any single context window. The unit of work is **one full pass of the research graph**; the campaign is that pass, repeated, each one aimed by what the last one failed to cover.

Expensive and long-running by design. Confirm the scope with the user before starting.

```
scope (once) → [ plan → fan-out researchers → extract → skeptic → merge → persist ] ↻ → synthesize (any time)
```

## Durable state

Three artifacts in a working directory. An iteration must be able to start knowing nothing but what it reads from them — findings held only in context are lost at the next reset. **Structure them however suits the research**; these are roles, not schemas.

- **Coverage map** — a taxonomy of the question space. What territory exists, and how well each branch is covered. Updated, never regenerated.
- **Source ledger** — every source encountered. Its one hard invariant: **every source carries a canonical ID (normalized URL hash or equivalent), and dedup runs against that ID.** Without it the campaign can't tell new ground from re-tread, and never converges.
- **Notes** — claims with their evidence and citations. The raw material synthesis is built from.

Rejected sources and knocked-down claims stay in the ledger, marked. Deleting them means re-fetching them later.

Because all state is on disk, iterations are independent: they can run back-to-back in one session, or be driven by an outer harness that restarts a fresh agent each pass.

## Nodes

### Scope — runs once, before the first iteration

A cheap broad sweep to learn the terrain, then build the initial coverage map from what it found. Skipping this makes lanes mirror the user's phrasing instead of the field's actual structure.

### Plan

Read the coverage map and the last gap report. Generate **3–5 research lanes** as *diffs against the map* — thin branches, contradictions, unexplored adjacencies. Never free-form from the original question; that re-treads ground.

Five lanes while the map is broad and shallow. Three once the gaps are narrow and specific.

### Fan-out researchers

One subagent per lane, in parallel. Each searches, retrieves, and reports back. Subagents do not spawn sub-subagents.

- **10 sources is the floor, 50 the ceiling.** The real stop is dryness: a lane ends when new sources stop changing its claims.
- Check the ledger before fetching — skip anything already seen by canonical ID.
- Retrieve with the skill that matches the source type, not by improvising.

**Retrieval skills.** Each one encodes the cheap path and the traps for its source type; improvising costs a researcher several turns and often floods its context with raw text.

| Source | Skill |
| --- | --- |
| Web search | `research/exa` first, `research/firecrawl` for broader sweeps |
| A page to read | Climb only as far as you must: the harness's own fetch tool → `curl https://markdown.new/<url>` → `research/firecrawl` → `research/crawl4ai` for JS-heavy pages |
| A site to crawl, or structured extraction | `research/firecrawl`, `research/crawl4ai` |
| YouTube video, playlist, channel | `research/youtube` |
| Reddit thread or subreddit | `research/reddit` |
| arXiv paper, primary literature | `research/arxiv` |
| Finding a book | `research/find-ebooks` |
| A long PDF, book, or EPUB in hand | `research/read-long-documents` |

Long sources are where campaigns die: one book read end-to-end can outweigh a lane's entire budget. Index it, then pull only the ranges the lane actually needs — that is what `research/read-long-documents` is for.

### Extract

Turn raw sources into claims with evidence and citations. Mark evidence strength: widely agreed / likely / disputed / thin.

### Skeptic — once, before merge

Runs after every lane reports, seeing all of them at once. That placement is deliberate: it catches cross-lane contradictions and consensus illusions a per-lane critic can't.

It challenges sourcing, not conclusions it dislikes. Whatever it knocks down becomes a gap-report entry — there is no re-research bounce inside an iteration. The next iteration's planner picks it up.

### Merge

Write claims into notes, sources into the ledger, and update the coverage map with what's now covered. Emit a **gap report**: what's still thin, what contradicted, what the skeptic rejected. That report is what aims the next iteration.

Merge does **not** write prose. See below.

### Synthesize — outside the iteration, callable any time

Read the notes and regenerate the document **from scratch**. Never revise a previous synthesis in place — that anchors the whole campaign to whatever the early iterations happened to find.

Because it's regenerable, the campaign is readable at iteration 3 as well as iteration 50.

## Termination

Iterate until the research saturates: the coverage map stops gaining branches, the gap report comes back empty, and lanes go dry on arrival across several consecutive iterations. One quiet iteration is noise — look for a run of them.

If the caller supplies an external stopping condition (a source count, a deadline, a budget), honor it, but still report saturation when it arrives first. Grinding out volume past that point buys duplicates, not coverage.

## Model routing

Use `autonomous-agents/choose-llm-for-task` to route each node; it picks across the available harnesses and accounts for real quota limits — which matters here, since a campaign burns through them. As a shape: strong models for scope, plan, skeptic and merge; cheaper models for the researcher fan-out and extraction.

## Principles

- **Write it down or lose it.** Never carry state between iterations in the prompt.
- **The map is the memory.** A planner that can't see covered territory will re-research it.
- **Dryness beats counts.** Numbers here are guardrails, not goals.
- **Honest gaps.** The gap report is a deliverable, not bookkeeping.
