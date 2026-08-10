---
name: deep-research-legacy
description: LEGACY prose-state-machine version, superseded by the engine-based deep-research skill. Run a long-horizon research campaign — a full research graph re-executed over many iterations until the field is exhausted. Use when the user explicitly asks for a deep research campaign, an exhaustive/marathon investigation, or research that should keep going until it stops finding anything new ("deep research X", "run a research campaign on X", "exhaustively research X"). NOT for ordinary research requests, single-session investigations, or anything expected to answer within one context window — use multi-agent-research for those.
---

# Deep Research

A research campaign that outlives any single context window. The unit of work is **one full pass of the research graph**; the campaign is that pass, repeated, each one aimed by what the last one failed to cover.

Expensive and long-running by design. Confirm the scope with the user before starting.

```
scope (once) → [ plan → fan-out researchers → extract → skeptic → merge → persist ] ↻ → synthesize (any time)
```

## Start confirmation

Before creating campaign state or dispatching any node, route the planned graph with `autonomous-agents/choose-llm-for-task`, then ask the user to confirm one concise list containing each node kind or lane, coding harness, model, and thinking level. Reconfirm only entries whose routing later changes; do not repeatedly approve unchanged routes.

After routing confirmation, separately offer an optional full graph-node preflight covering provider/auth availability, model smoke calls, required tools and CLI binaries, regional eligibility, resolved paths, filesystem permissions, and launcher dependencies. Run it only when the user confirms. Without it, rely on graph fail-fast behavior rather than silently performing mandatory smoke tests.

Before researcher fan-out, classify planned routes by model tier. Scope, plan, skeptic, and merge normally use strong reasoning routes; researcher and extraction fan-out normally use cheaper throughput routes. If three or more researcher lanes resolve to strong or scarce models, warn and block dispatch until the user explicitly confirms that fan-out. Do not invent a cost estimate.

## Durable state

Five durable artifact roles live in a working directory. An iteration must be able to start knowing nothing but what it reads from them — findings held only in context are lost at the next reset. **Structure them however suits the research** except where a contract is named.

- **Coverage map** — a taxonomy of the question space. What territory exists, and how well each branch is covered. Updated, never regenerated.
- **Source ledger** — every source encountered, each under a canonical ID. See the contract below and [`references/source-ledger-v1.md`](references/source-ledger-v1.md) ([schema](references/source-ledger-v1.schema.json)); it's the one part of this skill that isn't negotiable.
- **Notes** — claims with their evidence and citations. The raw material synthesis is built from.
- **Gap reports** — one durable report per iteration, at a stable path recorded in its manifest. The next planner reads the latest verified report.
- **Iteration manifests** — one event stream per iteration recording graph execution and terminal outcome.

Rejected sources and knocked-down claims stay in the ledger, marked. Deleting them means re-fetching them later.

### The ledger contract

Structure the rest as you see fit. Get this part wrong and the campaign either re-treads ground forever or reports a source count that isn't real.

**Merge is the only writer.** Researchers read the ledger to skip what they've already seen; they never append to it. Writes stay single-threaded — one pass, one writer — so parallel lanes can't race. Two lanes fetching the same URL in the same pass is tolerated: Merge dedups before writing, so it costs a wasted fetch, not a wrong count. Merge reports those collisions in the gap report, and the planner stops issuing overlapping lanes — the fix belongs in planning, not in worker coordination.

**Identity.** Every source carries a canonical ID: a normalized URL hash by default, and a namespaced content ID when one exists — `doi:…`, `arxiv:…`, `youtube:…`, `isbn:…` — which dedup prefers. That's what collapses aliases of one work: an arXiv abstract page, its PDF, and a journal mirror are one source. Genuinely different manifestations stay separate — a conference talk and a podcast recording of the same argument are two sources — joined by an optional `work_id` when the link matters. Normalization is mechanical and unforgiving (`youtu.be` vs `watch?v=`, `/abs` vs `/pdf` vs `v2`, tracking params, Reddit share links); compute it with a script rather than asking a model to judge it consistently across thousands of rows.

**The fold.** The ledger is append-only, and a source's status moves as it goes — seen, fetched, extracted, rejected. Reading it means reducing last-write-wins per canonical ID: the current state of a source is its most recent row, not its first.

**Counting.** Any target is a predicate over that fold, and it must name which statuses count. "N sources" means nothing until you've decided whether rejected ones are among them.

### The iteration manifest contract

Each iteration has one append-only JSONL manifest, with one event per line validated against [`references/iteration-manifest-v1.schema.json`](references/iteration-manifest-v1.schema.json). Follow [`references/iteration-manifest-v1.md`](references/iteration-manifest-v1.md) for states, attempts, routing evidence, artifact references, errors, retries, dependencies, timing, and terminal outcomes. Readers fold file order last-write-wins by `node_id`; event uniqueness, ordering, and legal transitions are runtime invariants.

The main orchestrator is the manifest's sole writer and owns transitions and retries. A single-pass caller stops after a verified terminal event. A campaign caller starts another pass only from `completed`, evaluates termination from `saturated`, and stops advancement on `failed`; no caller infers completion from prose, ledger rows, or a partial manifest.

**Graph fail-fast.** On the first node failure, cancellation, timeout, missing result, or failed acceptance check, stop scheduling new downstream nodes and stop launching new siblings. Do not discard work that already succeeded: validate every sibling attempt that had already started, and append `completed` for each valid `completed` result with zero exit even if its result becomes observable after another sibling fails. Give still-running siblings one bounded drain window to finish or publish a retryable checkpoint. Record its deadline when failure is observed. At that deadline, atomically snapshot each sibling's process exit and result presence, validate every zero-exit `completed` result visible in that snapshot, then mark cancellation observed only for the remaining unfinished attempts and cancel/reap those processes. Persist the failing attempt and diagnostics, classify retryability, then retry only failed, cancelled, or incomplete nodes. Resume from all manifest-verified dependencies, including completed siblings from the failed wave; never restart a successful node merely because another sibling failed.

Because all state is on disk, iterations are independent: they can run back-to-back in one session, or be driven by an outer harness that restarts a fresh agent each pass.

### State guardrail CLI

Use stdlib-only `scripts/research_state.py` with Python 3.11+. Campaign files and artifact roots are always explicit; the CLI validates and persists state but never plans, routes, retries, or dispatches work.

```bash
python3 scripts/research_state.py normalize 'https://youtu.be/VIDEO_ID'
python3 scripts/research_state.py ledger-append CAMPAIGN/source-ledger.jsonl --row '{...}'
python3 scripts/research_state.py ledger-fold CAMPAIGN/source-ledger.jsonl
python3 scripts/research_state.py ledger-count CAMPAIGN/source-ledger.jsonl --status extracted --source-type paper
python3 scripts/research_state.py manifest-append CAMPAIGN/passes/pass-1/iteration-manifest.jsonl --row '{...}'
python3 scripts/research_state.py manifest-verify CAMPAIGN/passes/pass-1/iteration-manifest.jsonl --artifact-root CAMPAIGN
python3 scripts/research_state.py campaign-evaluate --config CAMPAIGN/termination.json --ledger CAMPAIGN/source-ledger.jsonl --manifest CAMPAIGN/passes/pass-1/iteration-manifest.jsonl --artifact-root CAMPAIGN --usage CAMPAIGN/usage.json --now 2026-01-31T00:00:00Z
```

Append commands lock the stream, validate existing and new events, append one line, and `fsync`. JSON goes to stdout; invalid input exits 2 and an unverified terminal state exits 3.

### Harness-neutral node launch pattern

For every routed attempt, materialize the `node-execution-v1` input envelope in a fresh campaign-local attempt directory. Enumerate exact readable dependency and campaign-state paths; prior-attempt paths are denied except for the contract-repair path below. Before launch, run `scripts/prepare_node_contract.py --input ATTEMPT/node-input.json --artifact-root CAMPAIGN`. Treat failure as a hard launch blocker. It creates the exact schema, identity-filled result template, validator, `worker-contract.json`, and `self-validate.sh` in the attempt directory. Every worker prompt must name and require reading those contract files before substantive work, then require `./self-validate.sh` before exit and forbid completion unless it returns `"valid":true`. Start the selected harness from the smallest common ancestor containing approved inputs and outputs, write only beneath the isolated `output_dir`, and retain stdout/stderr plus process metadata as diagnostics. Never set a harness single-output override: worker-owned artifacts and `node-result.json` remain authoritative. Harness commands, authentication, and sandbox details belong only in the selected autonomous-harness skill. Enforce deadlines with harness-native supervision or owned-process control; never assume GNU `timeout` exists.

After process exit, run the stdlib-only acceptance check before appending `completed`:

```bash
python3 scripts/validate_node_result.py --input ATTEMPT/node-input.json --result ATTEMPT/node-result.json --schema references/node-execution-v1.schema.json --artifact-root CAMPAIGN --process-exit 0
```

The validator checks the contract's structural subset plus identity, attempt, result status, process exit, citation uniqueness and URL equality, path existence, and symlink containment. If an artifact named `counts` is declared, it must be machine-readable JSON with any of `sources`, `citations`, or `artifacts`; those values are checked against the result. Prose counts are never parsed heuristically.

For a retry, use `scripts/prepare_retry.py` with the read-only iteration `--manifest` to create only a fresh input bundle and event templates. Invoke it while the current folded node event is still `failed` with `retry_decision: retry`; only after preparation succeeds append `retrying`. It never mutates the manifest; the orchestrator remains sole writer. Supply the exact dependency and campaign-state allowlist and use `--allow-prior-attempts` only when previous-attempt artifacts are intentional inputs.

**Format-only repair.** If independent acceptance proves all substantive evidence and declared files are present and the only defect is field names, types, required/extra fields, or envelope shape, classify it with the distinct orchestration error code `invalid_node_result_format`. Generic `invalid_node_result` is not repairable. If identity, evidence completeness, path containment, citation/source agreement, process exit, or status semantics are uncertain, use ordinary retry or fail. For `invalid_node_result_format`, do not repeat retrieval or source analysis. Prepare a fresh attempt with `prepare_retry.py --contract-repair`, listing only the prior `node-result.json` and required declared artifact files through `--repair-read`. Then run `prepare_node_contract.py` and route the repair to a cheap model. Repair envelopes have empty dependencies, campaign state, and retrieval skills. Prompts prohibit retrieval, network, workspace discovery, and subagents, and the orchestrator must enforce the selected harness's tool allowlist so only declared-file reads plus fresh-output writes are available; if the harness cannot enforce that boundary, block repair. The worker may only normalize schema fields and copy declared evidence into the fresh output directory, then must pass `self-validate.sh`. Identity mismatch, missing evidence, unsafe paths, citation/source disagreement, nonzero completion, timeout, or substantive errors require an ordinary isolated retry or terminal failure—never contract repair.

## Nodes

### Scope — runs once, before the first iteration

A cheap broad sweep to learn the terrain, then build the initial coverage map from what it found. Skipping this makes lanes mirror the user's phrasing instead of the field's actual structure.

### Plan

Read the coverage map and the last gap report. Generate **3–5 research lanes** as *diffs against the map* — thin branches, contradictions, unexplored adjacencies. Never free-form from the original question; that re-treads ground. The orchestrator records the plan node and its artifact path in the manifest.

Once the plan node completes, the orchestrator appends a `pending` manifest event for every node the plan declares — every researcher lane plus extract, skeptic, merge, and persist — each with `dependencies` populated. This makes the full graph visible before any work starts; the existing `None -> pending -> running` transition already permits it.

Five lanes while the map is broad and shallow. Three once the gaps are narrow and specific.

### Fan-out researchers

One subagent per lane, in parallel. Each searches, retrieves, and reports back. Subagents do not spawn sub-subagents.

- **10 sources is the floor, 50 the ceiling.** The real stop is dryness: a lane ends when new sources stop changing its claims.
- Read the ledger before fetching and skip anything already seen by canonical ID. Researchers never write to it.
- The orchestrator records each lane as a stable researcher `node_id`, including dependencies, attempt, routing evidence, artifacts, and terminal state.
- Execute every routed node through [`references/node-execution-v1.md`](references/node-execution-v1.md) ([schema](references/node-execution-v1.schema.json)); use an isolated attempt output directory and accept its result artifact, not stdout, as the handoff.
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

Turn raw sources into claims with evidence and citations. Mark evidence strength: widely agreed / likely / disputed / thin. Extraction is a bounded transformation: enumerate exact input files, prohibit workspace reconnaissance and web/search/list tools, and require an early write checkpoint before extensive processing. A final zero-token event with unknown reason and no result artifact is retryable infrastructure failure, not successful empty extraction.

### Skeptic — once, before merge

Runs after every lane reports, seeing all of them at once. That placement is deliberate: it catches cross-lane contradictions and consensus illusions a per-lane critic can't.

It challenges sourcing, not conclusions it dislikes. Its checklist must include: prose counts versus structured arrays; primary evidence versus secondary-source inflation; duplicate URLs, aliases, and manifestations; and whether each material claim is supported by the exact cited passage rather than merely by a topically related source. Whatever it knocks down becomes a gap-report entry — there is no re-research bounce inside an iteration. The next iteration's planner picks it up. The orchestrator records the skeptic transition and report artifact after cross-lane review.

### Merge

Write claims into notes, sources into the ledger — Merge is the ledger's only writer — and update the coverage map with what's now covered. Emit a **gap report**: what's still thin, what contradicted, what the skeptic rejected, and which sources two lanes fetched twice. That report is what aims the next iteration. The orchestrator records merge/persist transitions, output paths, duration, and errors; persist is the final durable-write stage, not a separate research result.

Merge does **not** write prose. See below.

### Synthesize — outside the iteration, callable any time

Read the notes and regenerate the document **from scratch**. Never revise a previous synthesis in place — that anchors the whole campaign to whatever the early iterations happened to find.

Because it's regenerable, the campaign is readable at iteration 3 as well as iteration 50.

## Termination

Campaign termination is optional and follows [`references/campaign-termination-v1.md`](references/campaign-termination-v1.md) ([config schema](references/campaign-termination-v1.schema.json), [result schema](references/campaign-evaluation-result-v1.schema.json)). Without a configured target, execution remains one pass. With one, evaluate only explicit state paths and explicit `--now`; exit codes distinguish continue, complete, and failed. Exceeded hard deadline/budget limits fail unless an identical positive target predicate contributes to a completed target; nesting beneath `not` or an incomplete compound target grants no exemption. Invalid or missing state always fails, never completes.

Iterate until the research saturates: the coverage map stops gaining branches, the gap report comes back empty, and lanes go dry on arrival across several consecutive iterations. One quiet iteration is noise — look for a run of them.

If the caller supplies an external stopping condition (a source count, a deadline, a budget), honor it, but still report saturation when it arrives first. Grinding out volume past that point buys duplicates, not coverage.

After durable outputs are verified, the orchestrator appends the terminal iteration event: `completed`, `saturated`, or `failed`, with the gap-report path. Incomplete node folds resume from recorded attempts; callers act only from the verified terminal event.

## Model routing

Use `autonomous-agents/choose-llm-for-task` to route each node; it picks across available harnesses and accounts for real quota limits. Map scope, plan, skeptic, and merge to strong reasoning categories; map researcher and extraction fan-out to cheaper throughput categories unless lane complexity specifically warrants elevation. Apply the start-confirmation and three-strong-researcher guardrail above.

Then follow the harness-neutral [`references/node-execution-v1.md`](references/node-execution-v1.md) contract ([schema](references/node-execution-v1.schema.json)): load and obey the selected `autonomous-agents/<harness>` skill rather than embedding harness commands here. Record chosen harness, model, thinking level, rationale, and policy reference in manifest events; keep routing policy out of the schema.

## Observability

Execution and observability are separate. Workers publish attempt-local artifacts and diagnostic logs; the orchestrator alone publishes manifest state. Before launch, offer monitoring modes supported by the current coding harness: on-demand log/manifest checks, a harness-native scheduled read-only monitor, or an external scheduler. Monitoring must never mutate research artifacts or stand in for acceptance validation. Record the chosen mode and clean up recurring monitors when the campaign reaches a verified terminal state; if no scheduler exists, use on-demand checks.

For on-demand checks, `scripts/graph_view.py --campaign <root> --serve` — read-only campaign graph dashboard on 127.0.0.1.

Every `failed` event MUST carry `error.code` drawn from the closed set documented in [`references/iteration-manifest-v1.md`](references/iteration-manifest-v1.md) ([schema](references/iteration-manifest-v1.schema.json)), with `error.message` as free prose explaining the specific failure.

## Principles

- **Write it down or lose it.** Never carry state between iterations in the prompt.
- **The map is the memory.** A planner that can't see covered territory will re-research it.
- **Dryness beats counts.** Numbers here are guardrails, not goals.
- **Honest gaps.** The gap report is a deliverable, not bookkeeping.
