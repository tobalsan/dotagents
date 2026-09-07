# wfe — workflow engine

Deterministic multi-agent workflow engine. A workflow is a Python script defining
`async def run(args: dict[str, str], ctx: Ctx) -> Any`. The engine owns progress truth,
retries, concurrency, per-call timeouts, journaling, and resume; domain logic (prompts, schemas,
merge logic, saturation, etc.) stays in the workflow script, not in the engine.

## Quickstart

```bash
uv run --project /Users/thinh/dotagents/workflow-engine wfe run \
  /path/to/workflow.py \
  --campaign CAMPAIGN_DIR \
  --routing CAMPAIGN_DIR/routes.json \
  --arg key=value \
  --timeout 2700
```

`--timeout` is the per-call ceiling in seconds, default **900**. Bump it for lanes that
legitimately run long (research/fetch-heavy calls).

Worked example: `/Users/thinh/dotagents/skills/agentic-workflow-graphs/deep-research/workflow.py`
+ its `SKILL.md`.

## CLI reference

```
wfe run WORKFLOW.py --campaign DIR [--routing routes.json] [--arg k=v]...
                    [--resume RUN_ID] [--concurrency N] [--timeout SECONDS]
wfe status RUN_DIR [--json]
wfe list [--campaign DIR]
wfe watch --campaign DIR [--run RUN_ID] [--port 8799]
```

- `wfe run` — executes `WORKFLOW.py`. `--campaign` required. `--routing` defaults to
  `<campaign>/routes.json`. `--arg k=v` repeatable, values are raw strings (workflow casts).
  `--resume RUN_ID` reuses `<campaign>/runs/RUN_ID/` instead of creating a new run dir.
  `--concurrency` default 6. `--timeout` default 900. Exit codes: `0` completed with no
  failed calls, `1` workflow raised / was interrupted / has ≥1 failed call, `2` usage/config
  error.
- `wfe status RUN_DIR [--json]` — prints `state phase elapsed counts` plus one line per call
  (`state route/model label duration`); `--json` dumps `status.json` verbatim. Persisted run states
  are `running`, `completed`, `completed_with_errors` (workflow returned but tolerated call errors),
  `failed` (workflow raised), and `interrupted`. Missing `status.json` → exit 2.
- `wfe list [--campaign DIR]` — scans `<campaign>/runs/*/status.json`, newest first:
  `run_id state ok/error/total elapsed`.
- `wfe watch --campaign DIR [--run RUN_ID] [--port 8799]` — read-only localhost dashboard
  (see Observability below).

## routes.json

Maps route **names** (workflow-defined, e.g. `strong`/`throughput` in deep-research) to a
harness + model:

```json
{
  "default":    {"harness": "claude",   "model": "sonnet",  "extra_flags": []},
  "strong":     {"harness": "codex",    "model": "gpt-5.6", "extra_flags": []},
  "throughput": {"harness": "claude",   "model": "haiku",   "extra_flags": []}
}
```

Adapters: `claude`, `codex`, `pi`, `opencode`, `fake` (tests only). See `DESIGN.md` for
verified argv/parsing per adapter.

Write-capable defaults:
- Codex runs in `workspace-write` sandbox. This is OS/process sandbox setting; do not add
  `--dangerously-bypass-approvals-and-sandbox`, `--yolo`, or another sandbox mode.
- Claude runs with `--permission-mode acceptEdits`; installed CLI has no equivalent OS sandbox
  selector. Engine-controlled cwd is intended workspace, not OS confinement; Claude may write
  outside it under tool permissions.
- OpenCode runs with `--auto` (added once even when route already includes it); this approves
  application permission prompts, not an OS sandbox. Engine-controlled cwd is intended workspace,
  not OS confinement; OpenCode may write outside it under tool permissions.
- Model must be provider-qualified: `"model": "opencode-go/<model>"` (bare model names don't
  resolve).
- Concurrent `opencode run` calls share one SQLite db and hit "database is locked"; the engine
  isolates each call's `XDG_DATA_HOME` automatically (per-call scratch dir, symlinked
  `auth.json`) — no config needed.

## Run directory layout

```
CAMPAIGN_DIR/runs/<run_id>/
  journal.jsonl     # append-only events: run_start, phase, call_start, call_end, log, run_end
  status.json       # atomically rewritten snapshot; wfe status/list read only this
  results/<call_key>.json          # oversized (>64KiB) call results only
  logs/<call_key>.a<attempt>.stdout.txt / .stderr.txt
  calls/<call_key>/                # per-call scratch, adapter-owned (e.g. opencode XDG_DATA_HOME)
```

Workflow-authored artifacts (ledgers, notes, coverage maps, ...) belong under
`ctx.campaign_dir`, never under `run_dir`.

## Resume semantics

`call_key = sha256(prompt, schema, route NAME, label)[:16]`. `wfe run --resume RUN_ID`:

1. Folds `journal.jsonl` `call_end` rows last-write-wins by `call_key`.
2. Builds a replay map of `status == "ok"` results.
3. Re-runs the workflow; any `agent()` call whose key hits the replay map returns instantly
   with no subprocess spawned. Everything else runs live, appended to the same journal.

Route **config** changes (model, `extra_flags`) do **not** invalidate the cache — the key is
derived from the route *name*, not its resolved fields. This is deliberate: swapping a model
mid-campaign doesn't discard already-completed calls. Deliberate duplicate calls (same
prompt/schema/route) must differ by `label` or they memoize to the same result.

## Writing a workflow

```python
from workflow_engine import agent, parallel, pipeline, phase, AgentError

async def run(args: dict[str, str], ctx) -> dict:
    with phase("plan"):
        plan = await agent(prompt, schema=PLAN_SCHEMA, route="strong", label="plan")

    with phase("fan-out"):
        async def stage(item):
            return await agent(build_prompt(item), route="throughput", label=f"lane-{item['id']}")
        results = await pipeline(plan["lanes"], stage)   # or parallel([...])

    return {"done": True}
```

- `agent(prompt, schema=None, route="default", label=None, timeout_s=None)` — `schema=None`
  returns raw text; schema given returns parsed+validated JSON. Raises `AgentError(call_key,
  kind, message)` on exhaustion/timeout/harness failure (`kind` in `timeout`/`harness`/`parse`/
  `schema`/`route`).
- `parallel(thunks)` — runs coroutines/zero-arg callables concurrently, order preserved; a
  failing item resolves to `None`, the batch itself never raises.
- `pipeline(items, *stages)` — per-item chain, all items in flight at once, no barrier between
  stages; a stage raising or returning `None` drops that item for its remaining stages.
- `phase(title)` — context manager, journals a `phase` event, shown in `wfe status`/`watch`.

Worked example: `deep-research/workflow.py` (scope → plan → pipeline(research, extract) →
skeptic → merge, looped to saturation). Testing: `tests/` fake harness (`WFE_FAKE_CMD` +
`FakeAdapter`) — see `tests/test_engine.py` / `tests/conftest.py` for the pattern.

## Observability

`wfe watch --campaign DIR [--run RUN_ID] [--port 8799]` serves a read-only dashboard on
`127.0.0.1:PORT` (Host-gated to `127.0.0.1`/`localhost`, refuses other Host headers). Without
`--run` it auto-picks the latest run under `<campaign>/runs/`. Reads only `journal.jsonl` +
`status.json`; never invents liveness.

## Testing

```bash
cd /Users/thinh/dotagents/workflow-engine
uv run pytest
```

Must `cd` first — running `uv run --project /Users/thinh/dotagents/workflow-engine pytest`
from elsewhere collects 0 tests.

## Full design

`DESIGN.md` in this directory — full contracts, journal/status.json schemas, per-adapter argv
and parse rules, call execution/attempt semantics, kill/timeout mechanics.
