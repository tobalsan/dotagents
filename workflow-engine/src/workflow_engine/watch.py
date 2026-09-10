"""wfe watch — localhost-only, read-only dashboard over a run's journal + status."""

from __future__ import annotations

import argparse
import http.server
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

DEFAULT_TIMEOUT_S = 900.0  # engine's default per-call timeout; run_start carries the real one
STALE_MARGIN_S = 60.0  # a healthy run journals nothing while one call is in flight
LIVE_TAIL_BYTES = 4 * 1024 * 1024  # pi events repeat the full message per line; single lines exceed 64KB
CALL_STATES = ("ok", "error", "running", "interrupted")
ZERO_COUNTS = {"total": 0, "ok": 0, "error": 0, "running": 0, "interrupted": 0, "replayed": 0, "unknown": 0}


class WatchError(RuntimeError):
    """A condition the page can state plainly instead of the server crashing."""


# --- reading ---------------------------------------------------------------


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _count_lines(path: Path) -> int | None:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return sum(1 for line in fh if line.strip())
    except OSError:
        return None


def read_journal(path: Path) -> list[dict[str, Any]]:
    """Parse journal.jsonl, skipping blank and crash-truncated lines."""
    rows: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue  # crash-truncated tail
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        return rows
    return rows


_PI_EVENT_TYPES = {
    "session",
    "agent_start",
    "turn_start",
    "message_start",
    "message_update",
    "message_end",
    "tool_execution_start",
    "tool_execution_update",
    "tool_execution_end",
    "turn_end",
    "agent_end",
    "agent_settled",
}


def _compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _codex_live(row: dict[str, Any]) -> tuple[str, str] | None:
    """`codex exec --json`: {"type": "item.completed"/"item.started", "item": {...}}."""
    if row.get("type") not in ("item.completed", "item.started"):
        return None
    item = row.get("item")
    if not isinstance(item, dict):
        return None
    item_type = item.get("type")
    if item_type == "agent_message":
        return "assistant", str(item.get("text") or "")
    if item_type == "reasoning":
        return "reasoning", str(item.get("text") or item.get("summary") or "")
    if item_type == "command_execution":
        return "command", str(item.get("command") or item.get("aggregated_output") or "")
    if item_type == "file_change":
        changes = item.get("changes") or []
        paths = [str(c.get("path")) for c in changes if isinstance(c, dict) and c.get("path")]
        return "edit", ", ".join(paths)
    if item_type == "collab_tool_call":
        bits = [str(item.get("tool") or ""), str(item.get("status") or "")]
        prompt = item.get("prompt")
        if prompt:
            bits.append(str(prompt))
        return "collab", " ".join(b for b in bits if b)
    return str(item_type), str(item.get("text") or "")


def _pi_content_block(block: dict[str, Any]) -> tuple[str, str] | None:
    block_type = block.get("type")
    if block_type == "text" and block.get("text"):
        return "assistant", str(block["text"])
    if block_type == "thinking" and block.get("thinking"):
        return "reasoning", str(block["thinking"])
    if block_type == "toolCall":
        name = str(block.get("name") or "")
        return "tool", (name + " " + _compact_json(block.get("arguments") or {})).strip()
    return None


def _pi_live(row: dict[str, Any]) -> tuple[str, str] | None:
    """`pi -p --mode json`: session/message_*/tool_execution_*/turn_*/agent_* events."""
    if row.get("type") not in _PI_EVENT_TYPES:
        return None
    message = row.get("message")
    if not isinstance(message, dict):
        return None
    role = message.get("role")
    if role == "assistant":
        content = message.get("content")
        if not isinstance(content, list):
            return None
        for block in reversed(content):
            if isinstance(block, dict):
                found = _pi_content_block(block)
                if found:
                    return found
        return None
    if role == "toolResult":
        content = message.get("content")
        texts = [
            str(block["text"])
            for block in (content if isinstance(content, list) else [])
            if isinstance(block, dict) and block.get("type") == "text" and block.get("text")
        ]
        return ("tool_result", " ".join(texts)) if texts else None
    return None  # user/custom roles carry nothing worth tailing


def _claude_tool_result_text(content: Any) -> str:
    if isinstance(content, list):
        return " ".join(
            str(block["text"])
            for block in content
            if isinstance(block, dict) and block.get("type") == "text" and block.get("text")
        )
    return str(content) if content else ""


def _claude_live(row: dict[str, Any]) -> tuple[str, str] | None:
    """`claude -p --output-format stream-json`: {"type": "assistant"/"user", "message": {...}}."""
    if row.get("type") not in ("assistant", "user"):
        return None
    message = row.get("message")
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    if not isinstance(content, list):
        return None
    for block in reversed(content):
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text" and block.get("text"):
            return "assistant", str(block["text"])
        if block_type == "thinking" and block.get("thinking"):
            return "reasoning", str(block["thinking"])
        if block_type == "tool_use":
            name = str(block.get("name") or "")
            return "tool", (name + " " + _compact_json(block.get("input") or {})).strip()
        if block_type == "tool_result":
            text = _claude_tool_result_text(block.get("content"))
            if text:
                return "tool_result", text
    return None


def _opencode_live(row: dict[str, Any]) -> tuple[str, str] | None:
    """`opencode run --format json`: flat or `{"part": {...}}`-nested events."""
    row_type = row.get("type")
    if not isinstance(row_type, str) or row_type == "step_finish":
        return None
    part = row.get("part") if isinstance(row.get("part"), dict) else row
    if row_type == "text":
        text = part.get("text") or ""
        return ("assistant", str(text)) if text else None
    if row_type == "error":
        return "error", _compact_json(row)
    if "tool" in row_type.lower():
        name = part.get("tool") or part.get("name")
        if name:
            state = part.get("state")
            return "tool", str(name) + (f" {state}" if state else "")
        return "tool", _compact_json(part)
    return None


def _line_live(row: dict[str, Any]) -> dict[str, Any] | None:
    """Try each harness's disjoint JSONL shape in turn; None if this row has nothing to show."""
    for shape in (_codex_live, _pi_live, _claude_live, _opencode_live):
        found = shape(row)
        if found is None:
            continue
        kind, text = found
        if text:
            return {"kind": kind, "text": _truncate_live(text)}
    return None


def _truncate_live(text: str) -> str:
    return text if len(text) <= 400 else text[:400] + "…"


def read_live(run_dir: Path, call_key: str) -> dict[str, Any] | None:
    """Tail the running call's latest-attempt stdout log; None when there is nothing to show yet."""
    try:
        candidates = list((Path(run_dir) / "logs").glob(f"{call_key}.a*.stdout.txt"))
    except OSError:
        return None
    best: tuple[int, Path] | None = None
    for path in candidates:
        match = re.search(r"\.a(\d+)\.stdout\.txt$", path.name)
        if match and (best is None or int(match.group(1)) > best[0]):
            best = (int(match.group(1)), path)
    if best is None:
        return None

    try:
        with open(best[1], "rb") as fh:
            fh.seek(0, os.SEEK_END)
            fh.seek(max(0, fh.tell() - LIVE_TAIL_BYTES))
            text = fh.read().decode(errors="replace")
    except OSError:
        return None

    last_line = None
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        if last_line is None:
            last_line = line
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        live = _line_live(row)
        if live is not None:
            return live

    if last_line is not None:
        return {"kind": "raw", "text": _truncate_live(last_line)}
    return None


def list_runs(campaign_dir: Path) -> list[str]:
    """Names of run dirs holding a journal, lexicographically sorted."""
    runs_dir = Path(campaign_dir) / "runs"
    try:
        names = os.listdir(runs_dir)
    except OSError:
        return []
    return sorted(n for n in names if (runs_dir / n / "journal.jsonl").is_file())


def resolve_run_id(campaign_dir: Path, run_id: str | None) -> str:
    """Default to the lexicographic latest run; validate an explicit one by name."""
    runs = list_runs(campaign_dir)
    if run_id is None:
        if not runs:
            raise WatchError(f"no runs with a journal under {Path(campaign_dir) / 'runs'}")
        return runs[-1]
    if "/" in run_id or "\\" in run_id or ".." in run_id:
        raise WatchError(f"invalid run id: {run_id!r}")
    if run_id not in runs:
        raise WatchError(f"unknown run: {run_id}")
    return run_id


# --- folding ---------------------------------------------------------------


def _error_of(raw: Any) -> dict[str, str] | None:
    """Normalize both engine shapes: journal's {kind, message} dict and status.json's "kind: message"."""
    if isinstance(raw, dict):
        return {"kind": str(raw.get("kind") or "error"), "message": str(raw.get("message") or "")}
    if isinstance(raw, str) and raw.strip():
        text = raw.strip()
        kind, sep, message = text.partition(":")
        kind = kind.strip()
        if sep and kind and " " not in kind:
            return {"kind": kind, "message": message.strip()}
        return {"kind": "error", "message": text}
    return None


def _new_call(key: str, row: dict[str, Any], phase: str | None, segment: int, order: int) -> dict[str, Any]:
    return {
        "call_key": key,
        "label": row.get("label"),
        "route": row.get("route"),
        "harness": row.get("harness"),
        "model": row.get("model"),
        "started_at": row.get("started_at") or row.get("ts"),
        "finished_at": None,
        "duration_ms": None,
        "attempts": None,
        "cost_hint": None,
        "error": None,
        "state": "running",
        "phase": phase,
        "replayed": False,
        "segment": segment,
        "order": order,
    }


def fold_journal(rows: list[dict[str, Any]], attempt: int | None = None) -> dict[str, Any]:
    """Fold one numbered run_start segment, defaulting to the latest."""
    segments: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_phase: str | None = None

    for order, row in enumerate(rows):
        event = row.get("event")

        if event == "run_start":
            if current is not None:
                for key in current["open_keys"]:
                    current["calls"][key]["state"] = "interrupted"
            current = {
                "run_start": row,
                "run_end": None,
                "calls": {},
                "phases": [],
                "open_keys": set(),
                "segment": len(segments) + 1,
            }
            segments.append(current)
            current_phase = None
            continue

        if current is None:
            continue
        if event == "phase":
            title = row.get("title")
            if isinstance(title, str):
                current_phase = title
                if title not in current["phases"]:
                    current["phases"].append(title)
            continue

        if event == "run_end":
            for key in current["open_keys"]:
                current["calls"][key]["state"] = "interrupted"
            current["open_keys"].clear()
            current["run_end"] = row
            continue

        key = row.get("call_key")
        if not isinstance(key, str) or not key:
            continue

        if event == "call_start":
            current["calls"][key] = _new_call(key, row, current_phase, current["segment"], order)
            current["open_keys"].add(key)
            continue

        if event == "call_end":
            entry = current["calls"].get(key)
            if entry is None:
                entry = _new_call(key, row, current_phase, current["segment"], order)
                current["calls"][key] = entry
            entry.update(
                {
                    "label": row.get("label", entry["label"]),
                    "route": row.get("route", entry["route"]),
                    "harness": row.get("harness", entry["harness"]),
                    "model": row.get("model", entry["model"]),
                    "started_at": row.get("started_at") or entry["started_at"],
                    "finished_at": row.get("finished_at"),
                    "duration_ms": row.get("duration_ms"),
                    "attempts": row.get("attempts"),
                    "cost_hint": row.get("cost_hint"),
                    "state": "ok" if row.get("status") == "ok" else "error",
                    "error": _error_of(row.get("error")),
                }
            )
            current["open_keys"].discard(key)

    if not segments:
        return {"run_start": None, "run_end": None, "calls": {}, "phases": [], "segment": 0, "attempts": []}
    selected = attempt or len(segments)
    if selected < 1 or selected > len(segments):
        raise WatchError(f"unknown attempt: {selected}")
    folded = dict(segments[selected - 1])
    folded.pop("open_keys")
    folded["attempts"] = list(range(1, len(segments) + 1))
    return folded


def merge_calls(folded: dict[str, Any], status: dict[str, Any]) -> list[dict[str, Any]]:
    """Current attempt = the journal's last segment plus the calls only status.json knows about.

    The engine journals nothing for a replayed call (state "ok") nor for a call whose route failed
    to resolve (state "error"), so status-present + journal-absent is a replay only when it is "ok".
    """
    by_key: dict[str, dict[str, Any]] = folded["calls"]
    segment = folded["segment"]
    out = {k: dict(v) for k, v in by_key.items()}

    rows = status.get("calls")
    rows = rows if isinstance(rows, list) else []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        key = row.get("call_key")
        if not isinstance(key, str) or not key or key in out:
            continue
        prior = by_key.get(key)
        attempt = row.get("attempt")
        state = row.get("state") if row.get("state") in CALL_STATES else "unknown"
        out[key] = {
            "call_key": key,
            "label": row.get("label"),
            "route": row.get("route"),
            "harness": row.get("harness"),
            "model": row.get("model"),
            "started_at": row.get("started_at"),
            "finished_at": None,
            "duration_ms": row.get("duration_ms"),
            "attempts": attempt if isinstance(attempt, int) and attempt > 1 else None,
            "cost_hint": None,
            "error": _error_of(row.get("error")),
            "state": state,
            "phase": prior["phase"] if prior else None,
            "replayed": state == "ok",
            "segment": segment,
            "order": i - len(rows),  # replays precede the calls this attempt actually ran
        }

    return sorted(out.values(), key=lambda c: (c["order"], c["call_key"]))


# --- overlay ---------------------------------------------------------------


def _size_of(value: Any) -> int | None:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, int):
        return value
    return None


def _latest_gap_report(campaign_dir: Path) -> dict[str, Any] | None:
    passes = campaign_dir / "passes"
    try:
        names = os.listdir(passes)
    except OSError:
        return None
    best: tuple[int, str] | None = None
    for name in names:
        tail = name[5:] if name.startswith("pass-") else ""
        if tail.isdigit() and (best is None or int(tail) > best[0]):
            best = (int(tail), name)
    if best is None:
        return None
    data = _read_json(passes / best[1] / "gap-report.json")
    if not isinstance(data, dict):
        return None
    number = data.get("pass")
    return {
        "pass": number if isinstance(number, int) else best[0],
        "gaps": _size_of(data.get("gaps")),
        "new_sources": _size_of(data.get("new_sources")),
        "rejections": _size_of(data.get("rejections")),
        "new_branches": _size_of(data.get("new_branches")),
    }


def read_overlay(campaign_dir: Path) -> dict[str, Any] | None:
    """Deep-research campaign summary; active only when coverage-map.json exists."""
    coverage = _read_json(campaign_dir / "coverage-map.json")
    if not isinstance(coverage, dict):
        return None

    branches: list[dict[str, Any]] = []
    branch_counts: dict[str, int] = {}
    raw = coverage.get("branches")
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            state = item.get("status")
            state = state if isinstance(state, str) else "unknown"
            branch_counts[state] = branch_counts.get(state, 0) + 1
            branches.append(
                {
                    "id": str(item.get("id") or item.get("name") or "?"),
                    "name": str(item.get("name") or item.get("id") or "?"),
                    "status": state,
                    "note": str(item.get("note") or ""),
                }
            )

    topic = coverage.get("topic")
    return {
        "topic": topic if isinstance(topic, str) else None,
        "branches": branches,
        "branch_counts": branch_counts,
        "sources": _count_lines(campaign_dir / "source-ledger.jsonl"),
        "notes": _count_lines(campaign_dir / "notes.jsonl"),
        "gap_report": _latest_gap_report(campaign_dir),
    }


def read_ralph_overlay(campaign_dir: Path) -> dict[str, Any] | None:
    """Ralph-loop campaign summary; active only when *.state.json sits directly in campaign_dir."""
    campaign_dir = Path(campaign_dir)
    try:
        names = os.listdir(campaign_dir)
    except OSError:
        return None
    state_files = sorted(n for n in names if n.endswith(".state.json") and (campaign_dir / n).is_file())
    if not state_files:
        return None

    loops: list[dict[str, Any]] = []
    for filename in state_files:
        data = _read_json(campaign_dir / filename)
        if not isinstance(data, dict):
            continue  # unparsable JSON -- skip this loop
        name = filename[: -len(".state.json")]
        try:
            reflection_bytes = (campaign_dir / f"{name}.reflection.md").stat().st_size
        except OSError:
            reflection_bytes = 0
        output = data.get("lastVerificationOutput")
        passed = data.get("lastVerificationPassed")
        command = data.get("lastVerificationCommand")
        error = data.get("lastError")
        loops.append(
            {
                "name": name,
                "status": data.get("status"),
                "iteration": data.get("iteration"),
                "max_iterations": data.get("maxIterations"),
                "last_verification_passed": passed if isinstance(passed, bool) else None,
                "last_verification_command": command if isinstance(command, str) else None,
                "last_error": error if isinstance(error, str) else None,
                "updated_at": data.get("updatedAt"),
                "reflection_bytes": reflection_bytes,
                "last_verification_output_tail": output[-800:] if isinstance(output, str) and output else None,
            }
        )
    loops.sort(key=lambda entry: entry["name"])
    return {"kind": "ralph", "loops": loops}


# --- state -----------------------------------------------------------------


def build_state(campaign_dir: Path, run_id: str | None, attempt: int | str | None = None) -> dict[str, Any]:
    """Full dashboard payload for one run. Reports problems in "error"; never raises."""
    campaign_dir = Path(campaign_dir)
    state: dict[str, Any] = {
        "campaign": str(campaign_dir),
        "run_id": None,
        "runs": list_runs(campaign_dir),
        "workflow": None,
        "attempt": None,
        "attempts": [],
        "state": "unknown",
        "raw_state": "unknown",
        "phase": None,
        "started_at": None,
        "updated_at": None,
        "elapsed_s": None,
        "counts": dict(ZERO_COUNTS),
        "phases": [],
        "calls": [],
        "journal_age_s": None,
        "stale_after_s": DEFAULT_TIMEOUT_S + STALE_MARGIN_S,
        "stale": False,
        "overlay": read_overlay(campaign_dir),
        "ralph": read_ralph_overlay(campaign_dir),
        "error": None,
    }

    try:
        resolved = resolve_run_id(campaign_dir, run_id)
    except WatchError as exc:
        state["error"] = str(exc)
        return state

    run_dir = campaign_dir / "runs" / resolved
    journal = run_dir / "journal.jsonl"
    status = _read_json(run_dir / "status.json")  # first: a call started between reads must not read as a replay
    status = status if isinstance(status, dict) else {}
    if isinstance(attempt, str):
        try:
            attempt = int(attempt)
        except ValueError:
            state["error"] = f"invalid attempt: {attempt!r}"
            return state
    if attempt is not None and (isinstance(attempt, bool) or attempt < 1):
        state["error"] = f"invalid attempt: {attempt!r}"
        return state
    try:
        folded = fold_journal(read_journal(journal), attempt)
    except WatchError as exc:
        state["error"] = str(exc)
        return state
    latest = folded["segment"] == len(folded["attempts"])
    calls = merge_calls(folded, status if latest else {})
    if latest:
        for call in calls:
            if call["state"] == "running":
                call["live"] = read_live(run_dir, call["call_key"])

    counts = dict(ZERO_COUNTS)  # one source of truth: tiles can never disagree with the cards
    counts["total"] = len(calls)
    for call in calls:
        counts[call["state"] if call["state"] in counts else "unknown"] += 1
        if call["replayed"]:
            counts["replayed"] += 1

    run_start = folded["run_start"] or {}
    run_end = folded["run_end"] or {}
    run_state = (status.get("state") if latest else None) or run_end.get("state")
    if not isinstance(run_state, str):
        run_state = "running" if any(c["state"] == "running" for c in calls) else "unknown"

    used = [c["phase"] for c in calls]
    phases = [p for p in folded["phases"] if p in used]
    phases += [p for p in used if isinstance(p, str) and p not in phases]

    try:
        age = round(time.time() - journal.stat().st_mtime, 1)
    except OSError:
        age = None

    timeout_s = run_start.get("timeout_s")
    if not isinstance(timeout_s, (int, float)) or isinstance(timeout_s, bool) or timeout_s <= 0:
        timeout_s = DEFAULT_TIMEOUT_S
    stale_after = float(timeout_s) + STALE_MARGIN_S
    stale = run_state == "running" and age is not None and age > stale_after

    state.update(
        {
            "run_id": resolved,
            "workflow": (status.get("workflow") if latest else None) or run_start.get("workflow"),
            "attempt": folded["segment"],
            "attempts": folded["attempts"],
            "state": "stale" if stale else run_state,  # status.json keeps saying "running" after a SIGKILL
            "raw_state": run_state,
            "phase": status.get("phase") if latest else None,
            "started_at": (status.get("started_at") if latest else None) or run_start.get("ts"),
            "updated_at": (status.get("updated_at") if latest else None) or run_end.get("ts"),
            "elapsed_s": (status.get("elapsed_s") if latest else None)
            or (run_end.get("duration_ms") / 1000 if isinstance(run_end.get("duration_ms"), (int, float)) else None),
            "counts": counts,
            "phases": phases,
            "calls": calls,
            "journal_age_s": age,
            "stale_after_s": stale_after,
            "stale": stale,
        }
    )
    return state


# --- server ----------------------------------------------------------------


class WatchServer(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, addr: tuple[str, int], handler_cls: type, campaign_dir: Path, run_id: str | None) -> None:
        super().__init__(addr, handler_cls)
        self.campaign_dir = campaign_dir
        self.run_id = run_id


class WatchHandler(http.server.BaseHTTPRequestHandler):
    server: WatchServer

    def log_message(self, format: str, *args: Any) -> None:
        pass  # a dashboard, not a request log

    def _send(self, body: bytes, status: int, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _host_allowed(self) -> bool:
        """Loopback names only, so a page on another origin cannot read this run via DNS rebinding."""
        host = self.headers.get("Host")
        if host is None:
            return True  # HTTP/1.0 clients may omit it; the socket is bound to loopback anyway
        port = self.server.server_address[1]
        return host.strip() in ("127.0.0.1", "localhost", f"127.0.0.1:{port}", f"localhost:{port}")

    def do_GET(self) -> None:
        if not self._host_allowed():
            self._send(b"forbidden\n", 403, "text/plain; charset=utf-8")
            return
        parsed = urlsplit(self.path)
        if parsed.path == "/":
            self._send(PAGE.encode("utf-8"), 200, "text/html; charset=utf-8")
            return
        if parsed.path == "/api/state":
            query = parse_qs(parsed.query)
            requested = (query.get("run") or [None])[0]
            attempt = (query.get("attempt") or [None])[0]
            payload = build_state(self.server.campaign_dir, requested or self.server.run_id, attempt)
            body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
            self._send(body, 200, "application/json; charset=utf-8")
            return
        self._send(b"not found\n", 404, "text/plain; charset=utf-8")

    def _not_allowed(self) -> None:
        self._send(b"method not allowed\n", 405, "text/plain; charset=utf-8")

    do_HEAD = _not_allowed
    do_POST = _not_allowed
    do_PUT = _not_allowed
    do_PATCH = _not_allowed
    do_DELETE = _not_allowed
    do_OPTIONS = _not_allowed


def make_server(campaign_dir: Path, run_id: str | None, port: int) -> WatchServer:
    """Bind the dashboard to loopback only; the caller drives serve_forever."""
    return WatchServer(("127.0.0.1", port), WatchHandler, Path(campaign_dir), run_id)


def serve(campaign_dir: Path, run_id: str | None, port: int) -> int:
    """Serve the dashboard on 127.0.0.1 until Ctrl-C."""
    httpd = make_server(campaign_dir, run_id, port)
    print(f"[wfe] watch http://127.0.0.1:{httpd.server_address[1]}/", file=sys.stderr, flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


def cmd_watch(ns: argparse.Namespace) -> int:
    campaign_dir = Path(ns.campaign).resolve()
    if not campaign_dir.is_dir():
        print(f"error: campaign not found: {campaign_dir}", file=sys.stderr)
        return 2
    try:
        return serve(campaign_dir, ns.run, ns.port)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>wfe watch</title>
<style>
:root {
  --bg: #f5f5f2;
  --panel: #ffffff;
  --raised: #eceae4;
  --border: #d9d7d0;
  --text: #1b1b18;
  --dim: #6b6b64;
  --accent: #3b5bdb;
  --ok: #1f8a4c;
  --warn: #a8790a;
  --bad: #b3261e;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #17181c;
    --panel: #1f2126;
    --raised: #272930;
    --border: #34363d;
    --text: #e7e7e2;
    --dim: #9a9a92;
    --accent: #8aa4ff;
    --ok: #4cbf7c;
    --warn: #d9a441;
    --bad: #e2695c;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 20px 22px 60px;
  background: var(--bg);
  color: var(--text);
  font: 13px/1.45 var(--mono);
}
h1 { font-size: 15px; margin: 0; font-weight: 600; letter-spacing: -.01em; }
h2 {
  font-size: 10px; text-transform: uppercase; letter-spacing: .08em;
  color: var(--dim); font-weight: 600; margin: 22px 0 8px;
}
.num { font-variant-numeric: tabular-nums; }
header { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.sub { color: var(--dim); font-size: 12px; }
.pill {
  border-radius: 999px; padding: 2px 10px; font-size: 11px; letter-spacing: .04em;
  text-transform: uppercase; border: 1px solid var(--border); background: var(--raised); color: var(--dim);
}
.pill.running { color: var(--accent); border-color: var(--accent); animation: breathe 1.8s ease-in-out infinite; }
.pill.completed { color: var(--ok); border-color: var(--ok); }
.pill.completed_with_errors { color: var(--warn); border-color: var(--warn); }
.pill.failed { color: var(--bad); border-color: var(--bad); }
.pill.interrupted { color: var(--warn); border-color: var(--warn); }
.pill.stale { color: var(--warn); border-color: var(--warn); }
select {
  font: 11px/1.4 var(--mono); color: var(--dim); background: var(--raised);
  border: 1px solid var(--border); border-radius: 4px; padding: 2px 6px;
}
@keyframes breathe { 0%, 100% { opacity: 1; } 50% { opacity: .45; } }

.banner {
  margin: 12px 0 0; padding: 8px 12px; border-radius: 6px; font-size: 12px;
  border: 1px solid var(--border); background: var(--panel);
}
.banner.warn { color: var(--warn); border-color: var(--warn); }
.banner.bad { color: var(--bad); border-color: var(--bad); }
.hidden { display: none; }

.tiles { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
.tile {
  background: var(--panel); border: 1px solid var(--border); border-radius: 6px;
  padding: 8px 14px; min-width: 78px;
}
.tile .k { font-size: 9px; text-transform: uppercase; letter-spacing: .07em; color: var(--dim); }
.tile .v { font-size: 18px; font-variant-numeric: tabular-nums; }
.tile.ok .v { color: var(--ok); }
.tile.error .v { color: var(--bad); }
.tile.running .v { color: var(--accent); }
.tile.interrupted .v { color: var(--warn); }
.tile.unknown .v { color: var(--dim); }

.panel { background: var(--panel); border: 1px solid var(--border); border-radius: 6px; padding: 12px 14px; }
.chips { display: flex; gap: 6px; flex-wrap: wrap; }
.chip {
  border: 1px solid var(--border); border-radius: 999px; padding: 2px 9px; font-size: 11px;
  background: var(--raised); color: var(--dim);
}
.chip.covered { color: var(--ok); border-color: var(--ok); }
.chip.partial { color: var(--warn); border-color: var(--warn); }
.chip.thin { color: var(--bad); border-color: var(--bad); }
.facts { display: flex; gap: 18px; flex-wrap: wrap; margin-top: 10px; color: var(--dim); font-size: 12px; }
.facts b { color: var(--text); font-weight: 600; font-variant-numeric: tabular-nums; }
#ralph .panel + .panel { margin-top: 8px; }
#ralph pre {
  margin: 8px 0 0; padding: 8px 10px; background: var(--raised); border: 1px solid var(--border);
  border-radius: 4px; font-size: 11px; white-space: pre-wrap; overflow-wrap: anywhere;
  color: var(--dim); max-height: 200px; overflow-y: auto;
}

.cards { display: flex; flex-wrap: wrap; gap: 8px; }
.card {
  background: var(--panel); border: 1px solid var(--border); border-left: 3px solid var(--dim);
  border-radius: 5px; padding: 8px 10px; width: 340px; overflow: hidden;
}
.card.ok { border-left-color: var(--ok); }
.card.error { border-left-color: var(--bad); background: color-mix(in srgb, var(--bad) 7%, var(--panel)); }
.card.running { border-left-color: var(--accent); animation: breathe 1.8s ease-in-out infinite; }
.card.interrupted { border-left-color: var(--warn); }
.card.unknown { border-left-color: var(--dim); }
.card .label { font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card .meta {
  color: var(--dim); font-size: 10px; margin-top: 3px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.card .live {
  margin-top: 5px; font-size: 11px; color: var(--dim); background: var(--raised);
  border: 1px solid var(--border); border-radius: 4px; padding: 5px 7px;
  white-space: pre-wrap; overflow-wrap: anywhere; max-height: 72px; overflow: hidden;
}
.card .foot { display: flex; gap: 6px; align-items: center; margin-top: 5px; flex-wrap: wrap; }
.card .dur { font-variant-numeric: tabular-nums; font-size: 11px; }
.badge {
  font-size: 9px; text-transform: uppercase; letter-spacing: .05em; color: var(--dim);
  border: 1px solid var(--border); border-radius: 3px; padding: 0 4px;
}
.card .err { color: var(--bad); font-size: 10px; margin-top: 5px; overflow-wrap: anywhere; }
.empty { color: var(--dim); }
@media (prefers-reduced-motion: reduce) {
  .card.running, .pill.running { animation: none; }
}
</style>
</head>
<body>
<header>
  <h1 id="run">—</h1>
  <span class="pill" id="state">…</span>
  <select id="runs" class="hidden" title="switch run"></select>
  <select id="attempts" class="hidden" title="switch attempt"></select>
  <span class="sub" id="workflow"></span>
  <span class="sub num" id="elapsed"></span>
</header>
<div class="banner bad hidden" id="error"></div>
<div class="banner bad hidden" id="offline">disconnected — showing last known state</div>
<div class="banner warn hidden" id="stale"></div>
<div class="tiles" id="tiles"></div>
<div id="overlay"></div>
<div id="ralph"></div>
<div id="phases"></div>

<script>
"use strict";
const $ = (id) => document.getElementById(id);
const NO_PHASE = "\u0000unphased";
let last = null;

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined && text !== null) n.textContent = String(text);
  return n;
}

function humanSeconds(s) {
  if (s === null || s === undefined || isNaN(s)) return "";
  s = Math.round(s);
  if (s < 60) return s + "s";
  const m = Math.floor(s / 60), rs = s % 60;
  if (m < 60) return rs ? m + "m " + rs + "s" : m + "m";
  const h = Math.floor(m / 60), rm = m % 60;
  return rm ? h + "h " + rm + "m" : h + "h";
}

function humanMs(ms) {
  if (ms === null || ms === undefined) return "";
  return humanSeconds(ms / 1000);
}

function tile(parent, key, value, cls) {
  const t = el("div", "tile " + (cls || ""));
  t.appendChild(el("div", "k", key));
  t.appendChild(el("div", "v", value === null || value === undefined ? "–" : value));
  parent.appendChild(t);
}

function renderOverlay(o) {
  const root = $("overlay");
  root.textContent = "";
  if (!o) return;
  root.appendChild(el("h2", null, "deep research"));
  const panel = el("div", "panel");
  const chips = el("div", "chips");
  const order = ["covered", "partial", "thin"];
  const keys = Object.keys(o.branch_counts || {}).sort(
    (a, b) => (order.indexOf(a) + 9) % 9 - (order.indexOf(b) + 9) % 9
  );
  for (const k of keys) chips.appendChild(el("span", "chip " + k, k + " " + o.branch_counts[k]));
  if (!keys.length) chips.appendChild(el("span", "empty", "no branches"));
  panel.appendChild(chips);

  const facts = el("div", "facts");
  const fact = (label, value) => {
    const f = el("span", null, label + " ");
    f.appendChild(el("b", null, value === null || value === undefined ? "–" : value));
    facts.appendChild(f);
  };
  fact("sources", o.sources);
  fact("notes", o.notes);
  const g = o.gap_report;
  if (g) {
    fact("pass", g.pass);
    fact("gaps", g.gaps);
    fact("new sources", g.new_sources);
    fact("rejections", g.rejections);
  }
  panel.appendChild(facts);

  if ((o.branches || []).length) {
    const list = el("div", "chips");
    list.style.marginTop = "10px";
    for (const b of o.branches) {
      const c = el("span", "chip " + b.status, b.name);
      if (b.note) c.title = b.note;
      list.appendChild(c);
    }
    panel.appendChild(list);
  }
  root.appendChild(panel);
}

const RALPH_STATUS_CHIP = { completed: "covered", active: "partial", paused: "thin" };

function renderRalph(r) {
  const root = $("ralph");
  root.textContent = "";
  if (!r) return;
  root.appendChild(el("h2", null, "ralph loop"));
  for (const loop of r.loops) {
    const panel = el("div", "panel");
    const chips = el("div", "chips");
    chips.appendChild(el("span", "chip " + (RALPH_STATUS_CHIP[loop.status] || ""), loop.name + " · " + loop.status));
    panel.appendChild(chips);

    const facts = el("div", "facts");
    const fact = (label, value) => {
      const f = el("span", null, label + " ");
      f.appendChild(el("b", null, value === null || value === undefined ? "–" : value));
      facts.appendChild(f);
    };
    fact("iteration", loop.iteration + " / " + (loop.max_iterations ? loop.max_iterations : "∞"));
    fact(
      "verification",
      loop.last_verification_passed === true ? "passed" : loop.last_verification_passed === false ? "failed" : "–"
    );
    fact("command", loop.last_verification_command || "–");
    fact("updated", loop.updated_at || "–");
    panel.appendChild(facts);

    if (loop.last_error) panel.appendChild(el("div", "sub", loop.last_error));
    if (loop.last_verification_output_tail) panel.appendChild(el("pre", null, loop.last_verification_output_tail));

    root.appendChild(panel);
  }
}

function card(c) {
  const n = el("div", "card " + c.state);
  n.appendChild(el("div", "label", c.label || c.call_key));
  const bits = [c.route, c.model].filter(Boolean);
  n.appendChild(el("div", "meta", bits.join(" · ") || c.call_key));

  if (c.live && c.live.text) {
    const live = el("div", "live", "[" + c.live.kind + "] " + c.live.text);
    live.title = c.live.text;
    n.appendChild(live);
  }

  const foot = el("div", "foot");
  const dur = humanMs(c.duration_ms);
  if (dur) foot.appendChild(el("span", "dur", dur));
  if (c.attempts && c.attempts > 1) foot.appendChild(el("span", "badge", "×" + c.attempts));
  if (typeof c.cost_hint === "number") foot.appendChild(el("span", "badge", "$" + c.cost_hint.toFixed(2)));
  if (c.replayed) foot.appendChild(el("span", "badge", "replayed"));
  if (c.state === "running") foot.appendChild(el("span", "badge", "in flight"));
  if (c.state === "interrupted") foot.appendChild(el("span", "badge", "interrupted"));
  n.appendChild(foot);

  if (c.error) {
    const msg = c.error.kind + ": " + (c.error.message || "");
    const e = el("div", "err", msg.length > 140 ? msg.slice(0, 140) + "…" : msg);
    e.title = msg;
    n.appendChild(e);
  }
  return n;
}

function renderPhases(data) {
  const root = $("phases");
  root.textContent = "";
  const groups = new Map();
  for (const t of data.phases) groups.set(t, []);
  for (const c of data.calls) {
    const key = c.phase === null || c.phase === undefined ? NO_PHASE : c.phase;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(c);
  }
  for (const [title, calls] of groups) {
    if (!calls.length) continue;
    root.appendChild(el("h2", null, (title === NO_PHASE ? "unphased" : title) + "  (" + calls.length + ")"));
    const wrap = el("div", "cards");
    for (const c of calls) wrap.appendChild(card(c));
    root.appendChild(wrap);
  }
  if (!data.calls.length && !data.error) root.appendChild(el("div", "empty", "no calls yet"));
}

function renderRuns(data) {
  const sel = $("runs");
  const runs = data.runs || [];
  const key = runs.join("\n");
  if (sel.dataset.runs !== key) {
    sel.textContent = "";
    for (const r of runs) {
      const o = el("option", null, r);   // textContent only: run ids are journal-derived data
      o.value = r;
      sel.appendChild(o);
    }
    sel.dataset.runs = key;
  }
  if (data.run_id) sel.value = data.run_id;
  sel.classList.toggle("hidden", !runs.length);
}

function renderAttempts(data) {
  const sel = $("attempts");
  const attempts = data.attempts || [];
  const key = attempts.join("\n");
  if (sel.dataset.attempts !== key) {
    sel.textContent = "";
    for (const attempt of attempts) {
      const o = el("option", null, "attempt " + attempt);
      o.value = attempt;
      sel.appendChild(o);
    }
    sel.dataset.attempts = key;
  }
  if (data.attempt) sel.value = data.attempt;
  sel.classList.toggle("hidden", attempts.length < 2);
}

function render(data) {
  $("run").textContent = data.run_id || data.campaign.split("/").pop();
  const pill = $("state");
  pill.textContent = data.state;
  pill.className = "pill " + data.state;
  pill.title = data.stale
    ? "no journal activity for " + humanSeconds(data.journal_age_s) + "; process may be gone"
    : "";
  renderRuns(data);
  renderAttempts(data);
  $("workflow").textContent = data.workflow ? data.workflow.split("/").pop() : "";
  $("elapsed").textContent = data.elapsed_s ? humanSeconds(data.elapsed_s) : "";

  const err = $("error");
  err.textContent = data.error || "";
  err.classList.toggle("hidden", !data.error);

  const stale = $("stale");
  stale.textContent = data.stale ? "stale — journal untouched for " + humanSeconds(data.journal_age_s) : "";
  stale.classList.toggle("hidden", !data.stale);

  const tiles = $("tiles");
  tiles.textContent = "";
  const c = data.counts || {};
  const ALWAYS = ["total", "ok", "error"];
  for (const k of ["total", "ok", "error", "running", "interrupted", "replayed", "unknown"]) {
    if (!c[k] && ALWAYS.indexOf(k) < 0) continue;
    tile(tiles, k, c[k], k);
  }

  renderOverlay(data.overlay);
  renderRalph(data.ralph);
  renderPhases(data);
}

function currentQuery() {
  return new URLSearchParams(window.location.search);
}

$("runs").addEventListener("change", (ev) => {
  window.location.search = "?run=" + encodeURIComponent(ev.target.value);
});

$("attempts").addEventListener("change", (ev) => {
  const query = currentQuery();
  if (last && last.run_id) query.set("run", last.run_id);
  query.set("attempt", ev.target.value);
  window.location.search = "?" + query.toString();
});

async function poll() {
  try {
    const query = currentQuery().toString();
    const url = query ? "/api/state?" + query : "/api/state";
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) throw new Error("http " + res.status);
    last = await res.json();
    $("offline").classList.add("hidden");
    render(last);
  } catch (e) {
    $("offline").classList.remove("hidden");
  }
}

poll();
setInterval(poll, 2000);
</script>
</body>
</html>
"""
