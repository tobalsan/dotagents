---
name: deep-research
description: Run a long-horizon research campaign — a full research graph re-executed over many passes until the field saturates — as a deterministic wfe workflow. Use when the user explicitly asks for a deep research campaign, an exhaustive/marathon investigation, or research that should keep going until it stops finding anything new ("deep research X", "run a research campaign on X", "exhaustively research X"). NOT for ordinary research requests, single-session investigations, or anything expected to answer within one context window — use multi-agent-research for those.
---

# Deep Research

A research campaign driven by the `wfe` workflow engine, not a prose state machine. A one-time
`scope` sweep seeds the coverage map, then one pass of `plan -> research+extract -> skeptic ->
merge`, repeated until saturation. The engine owns
progress truth, retries, concurrency, timeouts, and resume; `workflow.py` and `contracts.py`
in this directory own the research-domain logic (routing, lane prompts, ledger identity,
saturation).

Expensive and long-running by design. Confirm scope and expected pass count with the user
before starting.

Before the first run, write `CAMPAIGN_DIR/brief.md` containing the user's research request
**verbatim** plus any presentation/style intent — the `topic` arg is a paraphrase that feeds
prompts; the brief is the durable record of what was actually asked. Synthesis reads it first.

## Agent team confirmation

Before the first run, build `routes.json` by routing each route name with
`autonomous-agents/choose-llm-for-task`, then present the team as one concise table —
route → harness, model, and which graph nodes it serves (`strong`: plan, skeptic;
`throughput`: scope [first run on an empty coverage map only], research, extract lanes) —
plus pass count, and wait for the user's confirmation before dispatching. Note that merge
is plain code, not an agent — it has no route or model. If `throughput` resolves to a strong or scarce model,
warn and require explicit confirmation of that fan-out. Reconfirm only when routing
changes; never re-approve an unchanged team on later runs or resumes.

After confirmation, **always** offer an optional preflight: one trivial smoke call per route in
`routes.json` — **through the engine** (`wfe run` against a tiny inline check), not a direct
harness CLI call: direct calls miss adapter parse bugs the engine path exercises. Catches
auth/CLI/model/parse problems before spending on the campaign; include 2-3
concurrent calls for the `throughput` route since serial-only smoke misses concurrency faults like
shared-state locks. Run it only if the user confirms; otherwise rely on the engine's fail-fast per call.

## Run it

```bash
uv run --project /Users/thinh/dotagents/workflow-engine wfe run \
  /Users/thinh/dotagents/skills/agentic-workflow-graphs/deep-research/workflow.py \
  --campaign CAMPAIGN_DIR \
  --routing CAMPAIGN_DIR/routes.json \
  --arg topic="the research question" \
  --arg max_passes=8 \
  --arg saturation_streak=2 \
  --timeout 2700
```

`--timeout` is the per-call ceiling in seconds; the engine default (900) is too low for
research lanes, which legitimately spend 15-40 min fetching and reading sources.


`CAMPAIGN_DIR` holds the durable state: `source-ledger.jsonl`, `notes.jsonl`,
`coverage-map.json`, and `passes/pass-N/gap-report.json`. It persists across runs — a second
`wfe run` against the same campaign directory continues research, reading what earlier passes
already found (lanes skip sources already in the ledger).

`routes.json` maps route names to harness/model. Route `strong` (plan, skeptic — reasoning
work) and `throughput` (research, extract — cheap fan-out) must both be defined. Note: an
`opencode` throughput route needs `"extra_flags": ["--auto"]` — headless opencode
auto-rejects permission asks (e.g. writing outside cwd) and kills the lane mid-research
otherwise. See
`workflow-engine/DESIGN.md` for the format and adapter list. Route researcher/extraction fan-out
to cheap models; escalate only if lane complexity specifically warrants it — never guess a cost.

`--arg` values are raw strings the workflow casts itself: `topic` (required), `max_passes`
(default 8), `saturation_streak` (default 2, quiet passes in a row before stopping).

When dispatching a run, ask the user whether to also launch the live dashboard —
`uv run --project /Users/thinh/dotagents/workflow-engine wfe watch --campaign CAMPAIGN_DIR`
(background it) — and report the URL it prints (default `http://127.0.0.1:8799/`). It is
read-only: phases, per-call status, and campaign coverage, straight from the journal.

## Check progress / resume

```bash
uv run --project /Users/thinh/dotagents/workflow-engine wfe status CAMPAIGN_DIR/runs/<run_id>
uv run --project /Users/thinh/dotagents/workflow-engine wfe list --campaign CAMPAIGN_DIR
```

If a run was interrupted or a lane failed, resume it — completed lanes are never re-run, only
what's missing or failed:

```bash
uv run --project /Users/thinh/dotagents/workflow-engine wfe run workflow.py \
  --campaign CAMPAIGN_DIR --routing CAMPAIGN_DIR/routes.json \
  --arg topic="the research question" --resume <run_id>
```

## Synthesize

Synthesis is not a graph node — it's a separate step you run any time by reading
`CAMPAIGN_DIR/brief.md` (the verbatim request and its style intent), then
`CAMPAIGN_DIR/notes.jsonl` (and, if useful, `coverage-map.json`), and writing the document. Regenerate it **from scratch** every time; never revise a previous synthesis in
place — that anchors the whole campaign to whatever the early passes happened to find. Because
it's regenerable, the campaign is readable after pass 3 as well as pass 50.

## Termination

The workflow stops when `contracts.is_saturated` sees `saturation_streak` consecutive quiet
passes (empty gap report, no new coverage branches) or `max_passes` is reached, whichever comes
first. One quiet pass is noise; a run of them means the field is dry.
