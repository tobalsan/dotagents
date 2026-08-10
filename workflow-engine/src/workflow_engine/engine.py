"""Workflow runtime: agent()/parallel()/pipeline()/phase(), journal, status, resume."""

from __future__ import annotations

import asyncio
import contextlib
import contextvars
import dataclasses
import hashlib
import importlib.util
import inspect
import json
import os
import sys
import time
from collections.abc import Awaitable, Callable, Iterable, Iterator, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workflow_engine import harness
from workflow_engine import schema as schema_mod

Result = dict[str, Any] | list[Any] | str

MAX_ATTEMPTS = 3
INLINE_RESULT_LIMIT = 64 * 1024


class AgentError(RuntimeError):
    """A logical agent() call that could not produce a valid result."""

    def __init__(self, call_key: str, kind: str, message: str) -> None:
        super().__init__(f"{kind}: {message}")
        self.call_key = call_key
        self.kind = kind
        self.message = message


@dataclasses.dataclass
class Ctx:
    run_dir: Path
    campaign_dir: Path
    journal: Path
    args: dict[str, str]

    def log(self, msg: str) -> None:
        print(f"[wfe] {msg}", file=sys.stderr, flush=True)
        run = _CURRENT.get()
        if run is not None:
            run.journal_row({"event": "log", "msg": msg})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def call_key(prompt: str, schema: dict[str, Any] | None, route: str, label: str | None) -> str:
    payload = {"prompt": prompt, "route": route, "label": label, "schema": schema}
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def load_workflow(path: Path) -> Callable[[dict[str, str], Ctx], Awaitable[Any]]:
    path = Path(path).resolve()
    spec = importlib.util.spec_from_file_location(f"wfe_workflow_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import workflow: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    fn = getattr(module, "run", None)
    if not inspect.iscoroutinefunction(fn):
        raise ValueError(f"workflow {path} must define 'async def run(args, ctx)'")
    return fn


def _replay_map(journal: Path, run_dir: Path) -> dict[str, Any]:
    """Fold call_end rows last-write-wins by call_key; keep results of successful calls."""
    folded: dict[str, dict[str, Any]] = {}
    if not journal.exists():
        return {}
    with open(journal, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue  # crash-truncated tail
            if not isinstance(row, dict) or row.get("event") != "call_end":
                continue
            key = row.get("call_key")
            if isinstance(key, str) and key:
                folded[key] = row

    replay: dict[str, Any] = {}
    for key, row in folded.items():
        if row.get("status") != "ok":
            continue
        rel = row.get("result_path")
        if rel:
            try:
                replay[key] = json.loads((run_dir / rel).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue  # result file lost -> re-run this call
        else:
            replay[key] = row.get("result")
    return replay


class Run:
    def __init__(
        self,
        *,
        run_dir: Path,
        campaign_dir: Path,
        routes: dict[str, harness.Route],
        concurrency: int = 6,
        default_timeout_s: float = 900.0,
        resume: bool = False,
    ) -> None:
        self.run_dir = Path(run_dir)
        self.campaign_dir = Path(campaign_dir)
        self.routes = routes
        self.concurrency = concurrency
        self.default_timeout_s = default_timeout_s
        self.resume = resume

        self.run_id = self.run_dir.name
        self.journal = self.run_dir / "journal.jsonl"
        self.workflow: Path | None = None
        self.current_phase: str | None = None
        self.state = "running"
        self.counts: dict[str, int] = {"total": 0, "running": 0, "ok": 0, "error": 0, "replayed": 0}

        (self.run_dir / "logs").mkdir(parents=True, exist_ok=True)
        (self.run_dir / "results").mkdir(parents=True, exist_ok=True)

        self._calls: dict[str, dict[str, Any]] = {}
        self._memo: dict[str, tuple[bool, Any]] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._sem = asyncio.Semaphore(concurrency)
        self._started_at = _now()
        self._started_mono = time.monotonic()
        self._replay = _replay_map(self.journal, self.run_dir) if resume else {}

    # --- persistence -------------------------------------------------------

    def journal_row(self, row: dict[str, Any]) -> None:
        line = json.dumps({"ts": _now(), **row}, ensure_ascii=False, default=str)
        with open(self.journal, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def write_status(self) -> None:
        counts = {"total": len(self._calls), "running": 0, "ok": 0, "error": 0, "replayed": 0}
        for entry in self._calls.values():
            counts[entry["state"]] = counts.get(entry["state"], 0) + 1
            if entry.get("replayed"):
                counts["replayed"] += 1
        self.counts = counts
        status = {
            "run_id": self.run_id,
            "workflow": str(self.workflow) if self.workflow else None,
            "state": self.state,
            "phase": self.current_phase,
            "started_at": self._started_at,
            "updated_at": _now(),
            "elapsed_s": round(time.monotonic() - self._started_mono, 1),
            "counts": counts,
            "calls": [
                {
                    "call_key": e["call_key"],
                    "label": e["label"],
                    "route": e["route"],
                    "harness": e["harness"],
                    "model": e["model"],
                    "state": e["state"],
                    "attempt": e["attempt"],
                    "started_at": e["started_at"],
                    "duration_ms": e["duration_ms"],
                    "error": e["error"],
                }
                for e in self._calls.values()
            ],
        }
        tmp = self.run_dir / "status.json.tmp"
        tmp.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.run_dir / "status.json")

    def _store_result(self, key: str, result: Any) -> tuple[Any, str | None]:
        blob = json.dumps(result, ensure_ascii=False, default=str)
        if len(blob.encode("utf-8")) <= INLINE_RESULT_LIMIT:
            return result, None
        rel = f"results/{key}.json"
        (self.run_dir / rel).write_text(blob, encoding="utf-8")
        return None, rel

    # --- calls -------------------------------------------------------------

    async def call(
        self,
        prompt: str,
        schema: dict[str, Any] | None = None,
        route: str = "default",
        label: str | None = None,
        timeout_s: float | None = None,
    ) -> Result:
        key = call_key(prompt, schema, route, label)
        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            if key in self._memo:  # identical call already awaited in this run
                ok, payload = self._memo[key]
                if ok:
                    return payload
                raise payload
            try:
                result = await self._run_call(key, prompt, schema, route, label, timeout_s)
            except AgentError as exc:
                self._memo[key] = (False, exc)
                raise
            self._memo[key] = (True, result)
            return result

    async def _run_call(
        self,
        key: str,
        prompt: str,
        schema: dict[str, Any] | None,
        route: str,
        label: str | None,
        timeout_s: float | None,
    ) -> Result:
        async with self._sem:
            if key in self._replay:
                self._calls[key] = {
                    "call_key": key,
                    "label": label,
                    "route": route,
                    "harness": None,
                    "model": None,
                    "state": "ok",
                    "attempt": 0,
                    "started_at": _now(),
                    "duration_ms": 0,
                    "error": None,
                    "replayed": True,
                }
                self.write_status()
                return self._replay[key]

            try:
                rt = harness.resolve(self.routes, route)
            except (ValueError, KeyError) as exc:
                self._calls[key] = {
                    "call_key": key,
                    "label": label,
                    "route": route,
                    "harness": None,
                    "model": None,
                    "state": "error",
                    "attempt": 0,
                    "started_at": _now(),
                    "duration_ms": 0,
                    "error": f"route: {exc}",
                }
                self.write_status()
                raise AgentError(key, "route", str(exc)) from exc

            timeout = self.default_timeout_s if timeout_s is None else timeout_s
            started_at = _now()
            started_mono = time.monotonic()
            entry: dict[str, Any] = {
                "call_key": key,
                "label": label,
                "route": route,
                "harness": rt.harness,
                "model": rt.model,
                "state": "running",
                "attempt": 1,
                "started_at": started_at,
                "duration_ms": None,
                "error": None,
            }
            self._calls[key] = entry
            self.journal_row(
                {
                    "event": "call_start",
                    "call_key": key,
                    "label": label,
                    "route": route,
                    "harness": rt.harness,
                    "model": rt.model,
                    "started_at": started_at,
                }
            )
            self.write_status()

            attempt_prompt = prompt if schema is None else prompt + schema_mod.json_instruction(schema)
            error: AgentError | None = None
            result: Any = None
            cost_hint: float | None = None
            attempts = 0

            for attempt in range(1, MAX_ATTEMPTS + 1):
                attempts = attempt
                entry["attempt"] = attempt
                self.write_status()
                log_prefix = self.run_dir / "logs" / f"{key}.a{attempt}"
                call_dir = self.run_dir / "calls" / key
                try:
                    res = await harness.spawn(
                        rt, attempt_prompt, timeout, log_prefix, self.campaign_dir, call_dir=call_dir
                    )
                except TimeoutError:
                    error = AgentError(key, "timeout", f"no result within {timeout:g}s")
                    break
                except (asyncio.CancelledError, KeyboardInterrupt):
                    entry["state"] = "error"
                    entry["error"] = "interrupted"
                    raise
                except Exception as exc:
                    error = AgentError(key, "harness", f"{type(exc).__name__}: {exc}")
                    break

                cost_hint = res.cost_hint
                if not res.text.strip():
                    error = AgentError(key, "parse", f"no assistant text (exit {res.exit})")
                    break
                if res.exit != 0:
                    # res.text carries the adapter's diagnostic on failure -- keep it.
                    error = AgentError(key, "harness", f"exit {res.exit}: {res.text.strip()[:300]}")
                    break
                if schema is None:
                    error, result = None, res.text
                    break

                try:
                    data = schema_mod.extract_json(res.text)
                    schema_mod.validate(data, schema)
                except schema_mod.SchemaError as exc:
                    error = AgentError(key, "schema", str(exc))
                    attempt_prompt += schema_mod.repair_suffix(str(exc), res.text)
                    continue
                error, result = None, data
                break

            finished_at = _now()
            duration_ms = int((time.monotonic() - started_mono) * 1000)
            entry["duration_ms"] = duration_ms
            row: dict[str, Any] = {
                "event": "call_end",
                "call_key": key,
                "label": label,
                "route": route,
                "harness": rt.harness,
                "model": rt.model,
                "attempts": attempts,
                "status": "ok" if error is None else "error",
                "started_at": started_at,
                "finished_at": finished_at,
                "duration_ms": duration_ms,
                "cost_hint": cost_hint,
            }

            if error is None:
                inline, rel = self._store_result(key, result)
                if rel is None:
                    row["result"] = inline
                else:
                    row["result_path"] = rel
                entry["state"] = "ok"
                self.journal_row(row)
                self.write_status()
                return result

            row["error"] = {"kind": error.kind, "message": error.message}
            entry["state"] = "error"
            entry["error"] = f"{error.kind}: {error.message}"
            self.journal_row(row)
            self.write_status()
            raise error

    # --- run lifecycle -----------------------------------------------------

    async def execute(self, workflow: Path, args: dict[str, str]) -> Any:
        """Run the workflow. Returns its value; check .counts["error"] for failed calls."""
        self.workflow = Path(workflow).resolve()
        fn = load_workflow(self.workflow)
        ctx = Ctx(
            run_dir=self.run_dir,
            campaign_dir=self.campaign_dir,
            journal=self.journal,
            args=dict(args),
        )
        self.journal_row(
            {
                "event": "run_start",
                "run_id": self.run_id,
                "workflow": str(self.workflow),
                "args": args,
                "concurrency": self.concurrency,
                "timeout_s": self.default_timeout_s,
                "routes": {n: {"harness": r.harness, "model": r.model} for n, r in self.routes.items()},
            }
        )
        self.write_status()

        token = _CURRENT.set(self)
        try:
            result = await fn(args, ctx)
        except (asyncio.CancelledError, KeyboardInterrupt):
            await self._shutdown()
            self._finish("interrupted")
            raise
        except BaseException:
            await self._shutdown()
            self._finish("failed")
            raise
        else:
            self._finish("failed" if self.counts["error"] else "completed")
            return result
        finally:
            _CURRENT.reset(token)

    async def _shutdown(self) -> None:
        """Cancel sibling tasks so harness.spawn can kill its process groups."""
        current = asyncio.current_task()
        pending = [t for t in asyncio.all_tasks() if t is not current and not t.done()]
        for task in pending:
            task.cancel()
        if pending:
            with contextlib.suppress(asyncio.CancelledError):
                await asyncio.wait(pending, timeout=10)

    def _finish(self, state: str) -> None:
        for entry in self._calls.values():
            if entry["state"] == "running":
                entry["state"] = "error"
                entry["error"] = entry["error"] or "interrupted"
        self.state = state
        self.write_status()
        self.journal_row(
            {
                "event": "run_end",
                "state": state,
                "duration_ms": int((time.monotonic() - self._started_mono) * 1000),
                "counts": dict(self.counts),
            }
        )


_CURRENT: contextvars.ContextVar[Run | None] = contextvars.ContextVar("wfe_run", default=None)


def _current_run() -> Run:
    run = _CURRENT.get()
    if run is None:
        raise RuntimeError("workflow_engine API used outside of a run")
    return run


async def agent(
    prompt: str,
    schema: dict[str, Any] | None = None,
    route: str = "default",
    label: str | None = None,
    timeout_s: float | None = None,
) -> Result:
    return await _current_run().call(prompt, schema, route, label, timeout_s)


async def parallel(thunks: Iterable[Awaitable[Any] | Callable[[], Awaitable[Any]]]) -> list[Any]:
    coros = [t() if callable(t) else t for t in thunks]
    if not coros:
        return []
    settled = await asyncio.gather(*coros, return_exceptions=True)
    out: list[Any] = []
    for item in settled:
        if isinstance(item, (asyncio.CancelledError, KeyboardInterrupt)):
            raise item
        out.append(None if isinstance(item, BaseException) else item)
    return out


async def pipeline(items: Sequence[Any], *stages: Callable[[Any], Awaitable[Any]]) -> list[Any]:
    async def chain(item: Any) -> Any:
        current = item
        for stage in stages:
            if current is None:
                return None
            try:
                current = await stage(current)
            except (asyncio.CancelledError, KeyboardInterrupt):
                raise
            except Exception:
                return None
        return current

    return await parallel([chain(item) for item in items])


@contextlib.contextmanager
def phase(title: str) -> Iterator[None]:
    run = _current_run()
    previous = run.current_phase
    run.current_phase = title
    run.journal_row({"event": "phase", "title": title})
    run.write_status()
    try:
        yield
    finally:
        run.current_phase = previous
        run.write_status()
