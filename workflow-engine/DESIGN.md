# wfe — workflow engine design

Deterministic replacement for the prose-driven orchestration state machine. The engine owns
progress truth, retries, concurrency, timeouts and resume. Workflows are plain Python.

**Non-goals.** No DAG DSL, no scheduler, no cost model, no worker-writable state. Research-domain
logic (URL normalization, ledger fold — see `deep-research-legacy/scripts/research_state.py`) stays
in the skill, not the engine.

## Layout

```
/Users/thinh/dotagents/workflow-engine/
  pyproject.toml
  src/workflow_engine/{__init__.py, engine.py, harness.py, schema.py, cli.py}
  tests/            (fake adapter only; no network)
```

Import graph is strictly acyclic: `cli -> engine -> {harness, schema}`; `__init__` re-exports from
`engine`. `harness` and `schema` import nothing from the package.

## Public script API

A workflow is a file defining `async def run(args: dict[str, str], ctx: Ctx) -> Any`. It imports the
API explicitly (no injected globals):

```python
from workflow_engine import agent, parallel, pipeline, phase
```

Those free functions resolve the active `Run` through a `ContextVar` set by `Run.execute`; calling
them outside a run raises `RuntimeError`.

```python
# workflow_engine/engine.py  (re-exported from __init__)
async def agent(
    prompt: str,
    schema: dict[str, Any] | None = None,
    route: str = "default",
    label: str | None = None,
    timeout_s: float | None = None,
) -> dict[str, Any] | list[Any] | str: ...
# schema=None -> returns raw text. schema given -> returns parsed+validated JSON.
# Raises AgentError on exhaustion/timeout/harness failure.

async def parallel(thunks: Iterable[Awaitable[Any] | Callable[[], Awaitable[Any]]]) -> list[Any]: ...
# Accepts coroutines or zero-arg callables returning coroutines. Order preserved.
# Any item raising anything resolves to None; the batch never raises.

async def pipeline(items: Sequence[Any], *stages: Callable[[Any], Awaitable[Any]]) -> list[Any]: ...
# Per-item chain, all items in flight at once, NO barrier between stages.
# A stage raising (or returning None) drops that item to None and skips its remaining stages.

@contextlib.contextmanager
def phase(title: str) -> Iterator[None]: ...
# Sets Run.current_phase, journals {"event":"phase", ...} on enter, restores previous on exit.

@dataclasses.dataclass
class Ctx:
    run_dir: pathlib.Path
    campaign_dir: pathlib.Path
    journal: pathlib.Path          # run_dir / "journal.jsonl"
    args: dict[str, str]
    def log(self, msg: str) -> None: ...   # stderr line + journal {"event":"log","msg":...}
```

Concurrency cap applies per logical `agent()` call (the semaphore wraps all schema retries), so
`parallel`/`pipeline` can be handed hundreds of thunks safely.

## engine.py

```python
Result = dict[str, Any] | list[Any] | str

class AgentError(RuntimeError):
    kind: str      # "timeout" | "harness" | "parse" | "schema" | "route"
    call_key: str
    def __init__(self, call_key: str, kind: str, message: str) -> None: ...

def call_key(prompt: str, schema: dict[str, Any] | None, route: str, label: str | None) -> str: ...

class Run:
    def __init__(
        self,
        *,
        run_dir: pathlib.Path,
        campaign_dir: pathlib.Path,
        routes: dict[str, harness.Route],
        concurrency: int = 6,
        default_timeout_s: float = 900.0,
        resume: bool = False,
    ) -> None: ...
    async def execute(self, workflow: pathlib.Path, args: dict[str, str]) -> Any: ...
    async def call(self, prompt, schema, route, label, timeout_s) -> Result: ...   # agent() body
    def journal_row(self, row: dict[str, Any]) -> None: ...   # append + flush + fsync
    def write_status(self) -> None: ...                       # atomic rewrite

def load_workflow(path: pathlib.Path) -> Callable[[dict[str, str], Ctx], Awaitable[Any]]: ...
# importlib.util.spec_from_file_location; requires a coroutine function named `run`.
```

### call_key

Stable identity across processes and Python versions. Exactly:

```python
payload = {"prompt": prompt, "route": route, "label": label, "schema": schema}
blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
key = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]
```

`schema` is embedded as-is (sorted keys make it order-independent); `label` and `schema` may be
`null`. Retry attempts do **not** change the key — the key is derived from the *original* prompt.

Two calls with an identical key inside one run are the same call: the second `await` returns the
first one's result (in-run memoization keyed by `call_key`, guarded by an `asyncio.Lock` per key).
Deliberate duplicates must differ by `label`.

### Executing one call

1. `sem.acquire()`.
2. If `resume` and key in the replay map → return replayed result immediately, mark
   `state="ok", replayed=true` in status.json, no journal row.
3. Resolve route (`harness.resolve`); unknown name → `AgentError(kind="route")`.
4. Journal `call_start`. For attempt in 1..3:
   - prompt for attempt 1 = `prompt` (+ `schema.json_instruction(schema)` appended when schema given);
     for attempt k>1 = attempt-1 prompt + `schema.repair_suffix(error, previous_text)`.
   - `await harness.spawn(route, prompt_k, timeout_s, log_prefix=run_dir/"logs"/f"{key}.a{k}")`.
   - non-zero exit → `AgentError(kind="harness")`, no further attempts (harness failure is not a
     format error).
   - no schema → success with `result.text`.
   - schema → `schema.extract_json` then `schema.validate`; `SchemaError` → record and continue loop.
5. Journal `call_end` with terminal status; `write_status()`; return or raise.

`timeout_s` defaults to `default_timeout_s` (CLI `--timeout`, default 900).

Schema-retry exhaustion after 3 attempts raises `AgentError(kind="schema")` with the last
jsonschema message. It is journaled `status="error"`; `parallel` yields `None` for it and
`pipeline` drops the item. Format errors therefore never appear as *node* failures inside
`parallel`/`pipeline` — only as a dropped lane the workflow can re-plan.

### Concurrency, timeout, kill

- `asyncio.Semaphore(concurrency)` created in `Run.__init__` (default 6, `--concurrency`).
- Children spawned in `harness.spawn` with `asyncio.create_subprocess_exec(*argv,
  stdin=PIPE, stdout=PIPE, stderr=PIPE, start_new_session=True, cwd=campaign_dir)`.
- Timeout: `await asyncio.wait_for(proc.communicate(stdin_bytes), timeout_s)`. On `TimeoutError`:
  `os.killpg(os.getpgid(proc.pid), SIGTERM)`, `await asyncio.wait_for(proc.wait(), 5)`, then
  `os.killpg(..., SIGKILL)` on second timeout; raise `TimeoutError` up to `Run.call`, which converts
  it to `AgentError(kind="timeout")`. No GNU `timeout` binary is used.
- `KeyboardInterrupt`/cancellation: `Run.execute` cancels pending tasks, kills live process groups,
  journals `run_end` with `state="interrupted"`, and leaves the journal resumable.

### Resume

`wfe run ... --resume RUN_ID` reuses `<campaign>/runs/<RUN_ID>/` instead of creating a new one.

1. Read `journal.jsonl` line by line, ignoring unparsable lines (crash-truncated tail).
2. Fold last-write-wins by `call_key` over `event == "call_end"` rows.
3. Replay map = `{key: result}` for folded rows with `status == "ok"`, loading `result_path` when
   the row carries one instead of an inline `result`.
4. Run the workflow normally. Steps whose key hits the replay map do not spawn anything; everything
   else runs live and appends to the same journal.

Key-based, not sequence-based: reordering, added lanes, and partially-failed `parallel` batches all
resume correctly, and a failed lane never discards its completed siblings.

## journal.jsonl

One JSON object per line, append-only, engine-written only (`open(..., "a")`, `write`, `flush`,
`os.fsync`). Workers never touch it. Common fields: `ts` (RFC3339 UTC, `Z`), `event`.

| event | fields |
| --- | --- |
| `run_start` | `run_id`, `workflow`, `args`, `concurrency`, `timeout_s`, `routes` (name → `{harness,model}`) |
| `phase` | `title` |
| `log` | `msg` |
| `call_start` | `call_key`, `label`, `route`, `harness`, `model`, `started_at` |
| `call_end` | `call_key`, `label`, `route`, `harness`, `model`, `attempts` (int), `status` (`"ok"`/`"error"`), `started_at`, `finished_at`, `duration_ms`, `cost_hint` (float\|null), and `result` **or** `result_path`, and `error` on failure |
| `run_end` | `state` (`"completed"`/`"failed"`/`"interrupted"`), `duration_ms`, `counts` |

`error` is `{"kind": str, "message": str}`. Results serializing to more than 64 KiB are written to
`results/<call_key>.json` and referenced by `result_path` (relative to `run_dir`); smaller results
are inlined under `result`.

## status.json

Rewritten atomically after every state change (`json.dump` to `status.json.tmp` in `run_dir`, then
`os.replace`). Never read by the engine; it exists so `wfe status` is instant.

```json
{
  "run_id": "20260809T201430Z-research",
  "workflow": "/abs/path/research.py",
  "state": "running",
  "phase": "fan-out researchers",
  "started_at": "2026-08-09T20:14:30Z",
  "updated_at": "2026-08-09T20:18:02Z",
  "elapsed_s": 212.4,
  "counts": {"total": 12, "running": 4, "ok": 7, "error": 1, "replayed": 3},
  "calls": [
    {"call_key": "9f2c…", "label": "lane-2", "route": "throughput",
     "harness": "codex", "model": "gpt-5.6", "state": "running",
     "attempt": 1, "started_at": "…", "duration_ms": null, "error": null}
  ]
}
```

`counts.total` counts distinct call keys seen; `replayed` is a subset of `ok`.

## harness.py

```python
@dataclasses.dataclass(frozen=True)
class Route:
    harness: str
    model: str | None = None
    extra_flags: list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class HarnessResult:
    text: str
    exit: int
    cost_hint: float | None

class Adapter(typing.Protocol):
    name: str
    def command(self, route: Route, prompt: str) -> tuple[list[str], str | None]: ...
    # -> (argv, stdin_text); stdin_text None means the prompt is already in argv.
    def parse(self, stdout: str, stderr: str, exit_code: int) -> HarnessResult: ...
    # Optional, not a Protocol member: def env(self, route: Route, call_dir: pathlib.Path)
    #   -> dict[str, str] | None. See "Per-call adapter env hook" below.

ADAPTERS: dict[str, Adapter]        # "claude", "codex", "pi", "opencode", "fake"

def load_routes(path: pathlib.Path) -> dict[str, Route]: ...
def resolve(routes: dict[str, Route], name: str) -> Route: ...   # KeyError -> ValueError listing names
async def spawn(route: Route, prompt: str, timeout_s: float, log_prefix: pathlib.Path,
                cwd: pathlib.Path, call_dir: pathlib.Path | None = None) -> HarnessResult: ...
                # cwd is the campaign dir; call_dir is per-call scratch (run_dir/"calls"/call_key)
```

`spawn` owns the subprocess, the timeout and the kill; it writes `<log_prefix>.stdout.txt` and
`<log_prefix>.stderr.txt` verbatim, then returns `parse(...)`. A parse failure (no assistant text
found) returns `HarnessResult(text="", exit=exit_code or 1, cost_hint=None)`; the engine turns an
empty text into `AgentError(kind="parse")`. (`OpencodeAdapter.parse` is an exception: on failure it
returns diagnostic text — `type == "error"` JSONL events plus the stderr tail — instead of `""`, so
failures surface instead of reading as a generic empty-text parse error.)

### Per-call adapter env hook

`opencode run` subprocesses that share `~/.local/share/opencode/opencode.db` (SQLite) fail with
"database is locked" when run concurrently. Rather than special-casing the harness in `engine.py`,
`Adapter` supports an **optional** hook — `def env(self, route: Route, call_dir: pathlib.Path) ->
dict[str, str] | None` — that is not a required Protocol member; `spawn` looks it up with
`getattr(adapter, "env", None)` and only calls it when present, so adapters without it (all of them,
today, except `opencode`) need no change. `spawn` merges the returned mapping over `os.environ` for
that one subprocess only; it does not create `call_dir` or anything under it — the adapter owns that.
`OpencodeAdapter.env` creates `<call_dir>/xdg-data/opencode/`, symlinks (never copies) the shared
`auth.json` into it, and returns `{"XDG_DATA_HOME": str(<call_dir>/xdg-data)}`, giving each call its
own `opencode.db` while still authenticating off the one real `auth.json`.

`routes.json`:

```json
{
  "default":    {"harness": "claude",   "model": "sonnet",        "extra_flags": []},
  "strong":     {"harness": "codex",    "model": "gpt-5.6",       "extra_flags": []},
  "throughput": {"harness": "claude",   "model": "haiku",         "extra_flags": []}
}
```

### Verified invocations

All four verified locally on 2026-08-09 (macOS, `which` found every binary). Model flag values are
whatever the route supplies; `extra_flags` is appended immediately before the prompt/stdin marker.

**claude** — VERIFIED (`claude -p "…" --output-format json --model haiku`).
argv: `claude -p --output-format json --model <model> <extra_flags>`; prompt on **stdin**.
stdout is a single JSON object. `text = obj["result"]`, `cost_hint = obj.get("total_cost_usd")`.
Treat `obj.get("is_error") is True` or `obj.get("subtype") != "success"` as failure (`exit` = 1).
Observed keys: `type:"result"`, `subtype:"success"`, `is_error`, `result`, `total_cost_usd`,
`duration_ms`, `usage`, `modelUsage`, `session_id`.

**codex** — VERIFIED (`codex exec --json --skip-git-repo-check -s read-only "…"`).
argv: `codex exec --json --skip-git-repo-check -s read-only -m <model> <extra_flags> -`; the
trailing `-` makes it read the prompt from **stdin**.
stdout is JSONL. Take the last `{"type":"item.completed","item":{"type":"agent_message","text":…}}`
→ `text = item["text"]`. Terminal event `{"type":"turn.completed","usage":{…}}` carries tokens only;
`cost_hint = None`. `{"type":"turn.failed"}` or a missing `agent_message` ⇒ failure.

**pi** — VERIFIED (`pi -p --mode json`, prompt on stdin).
argv: `pi -p --mode json --model <model> <extra_flags>`; prompt on **stdin**.
(`--provider <name>` and `--thinking <level>` belong in `extra_flags`.)
stdout is JSONL session events. Take the last `{"type":"message_end","message":{"role":"assistant"}}`
→ `text = "".join(part["text"] for part in message["content"] if part["type"] == "text")`;
`cost_hint = message["usage"]["cost"]["total"]`.

**opencode** — VERIFIED (`opencode run --format json "…"`).
argv: `opencode run --format json -m <provider/model> <extra_flags> <prompt>` — prompt is a
**positional** argument (stdin support UNVERIFIED; do not rely on it).
stdout is JSONL. `text` = concatenation of `part["text"]` for events with `type == "text"`, in
order. `cost_hint` = `part["cost"]` from the last `{"type":"step_finish"}` event.

**fake** (tests) — `command()` returns `([os.environ["WFE_FAKE_CMD"], *route.extra_flags], prompt)`;
`parse()` returns `HarnessResult(text=stdout, exit=exit_code, cost_hint=None)`. Tests point
`WFE_FAKE_CMD` at a script that echoes canned output, can emit invalid JSON on its first invocation
(to exercise the schema-retry loop) and can `sleep` (to exercise the timeout kill path).

## schema.py

```python
class SchemaError(ValueError): ...

def json_instruction(schema: dict[str, Any]) -> str: ...
def extract_json(text: str) -> Any: ...                       # raises SchemaError
def validate(data: Any, schema: dict[str, Any]) -> None: ...  # raises SchemaError
def repair_suffix(error: str, previous: str) -> str: ...
```

- `json_instruction` appends, on its own paragraph: the literal schema (`json.dumps(schema,
  indent=2)`) plus `"Reply with ONLY that JSON object. No prose, no markdown fences."`
- `extract_json` tries, in order: `json.loads(text)`; the first ```` ```json ```` / ```` ``` ````
  fenced block; the widest balanced `{…}` or `[…]` span in the text. Failure → `SchemaError`.
- `validate` uses `jsonschema.Draft202012Validator`, collects `sorted(v.iter_errors(data),
  key=jsonschema.exceptions.relevance)` and raises `SchemaError` with the first 3 errors formatted
  as `"$.a.b: <message>"`.
- `repair_suffix(error, previous)` →
  `"\n\nYour previous reply was REJECTED by schema validation:\n<error>\n\nRejected output (first
  2000 chars):\n<previous[:2000]>\n\nReturn the corrected JSON only."`

## cli.py

```python
def main(argv: list[str] | None = None) -> int: ...   # [project.scripts] wfe = "workflow_engine.cli:main"
```

```
wfe run WORKFLOW.py --campaign DIR [--routing routes.json] [--arg k=v]...
                    [--resume RUN_ID] [--concurrency N] [--timeout SECONDS]
wfe status RUN_DIR [--json]
wfe list [--campaign DIR]
wfe watch --campaign DIR [--run RUN_ID] [--port 8799]
```

- `--arg k=v` is repeatable; values are **raw strings** (workflows cast). A missing `=` is a usage
  error. Result is `args: dict[str, str]`.
- `--routing` defaults to `<campaign>/routes.json`; missing file is a usage error.
- `--concurrency` default 6, `--timeout` default 900.
- `run_id` = `f"{datetime.now(UTC):%Y%m%dT%H%M%SZ}-{workflow.stem}"`.
- `wfe status` prints `state phase elapsed counts` plus one line per call
  (`state route/model label duration`), newest last; `--json` dumps `status.json` verbatim. Missing
  `status.json` → exit 2.
- `wfe list` scans `<campaign>/runs/*/status.json`, newest first: `run_id state ok/err/total elapsed`.
- `wfe watch` (`watch.py`, stdlib-only, imports nothing from the package) serves a read-only
  dashboard on `127.0.0.1`: journal fold scoped to the last resume segment unioned with
  `status.json` calls, phases as groups, in-flight calls animated, stale-journal banner from
  journal mtime — never invented liveness. Deep-research overlay activates only when the
  campaign dir has `coverage-map.json`; it reads campaign JSON files directly.
- Exit codes: `0` run completed with no failed calls; `1` workflow raised, was interrupted, or ended
  with ≥1 failed call; `2` usage/config error.

### run_dir layout

```
<campaign>/runs/<run_id>/
  journal.jsonl     # append-only, engine-owned; its run_start row is the run's manifest
                    # (workflow path, args, routes snapshot, concurrency, timeout)
  status.json       # atomically rewritten
  results/<call_key>.json          # oversized results only
  logs/<call_key>.a<attempt>.stdout.txt
  logs/<call_key>.a<attempt>.stderr.txt
  calls/<call_key>/                # per-call scratch, adapter-owned; only populated when an
                                    # adapter's optional env() hook uses it (e.g. opencode)
```

Workflow-authored artifacts belong under `ctx.campaign_dir`, never under `run_dir`.

## pyproject.toml

```toml
[project]
name = "workflow-engine"
version = "0.1.0"
description = "Deterministic multi-agent workflow engine"
requires-python = ">=3.11"
dependencies = ["jsonschema>=4.21"]

[project.scripts]
wfe = "workflow_engine.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/workflow_engine"]
```

Everything runs through `uv` (`uv run wfe …`, `uv run pytest`). No other runtime dependency.

## Implementer split

Four parallel lanes, file-isolated: **A** `harness.py` (adapters + `spawn` + fake), **B**
`schema.py`, **C** `engine.py` (Run, call_key, journal, status, resume, parallel/pipeline/phase),
**D** `cli.py` + `pyproject.toml` + tests. B and A have no package imports; C depends only on the
signatures above; D depends only on `Run`/`load_routes`/`load_workflow`.
