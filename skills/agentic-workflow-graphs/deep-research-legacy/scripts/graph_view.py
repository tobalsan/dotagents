#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Read-only campaign graph state + liveness overlay for deep-research campaigns."""
from __future__ import annotations

import argparse
import http.server
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_state as rs

QUIET_THRESHOLD_MINUTES = 5
RUNNING_STATES = {"running", "retrying"}
PID_FILENAMES = ("pid", "opencode.pid")
DEFAULT_PORT = 8799
MAX_FILE_BYTES = 200_000


def read_manifest_tolerant(path: Path) -> tuple[list[dict[str, Any]], bool]:
    """Parse a manifest JSONL file, tolerating only a truncated (not-yet-flushed) trailing line.

    A blank line or malformed JSON anywhere else is corruption, not tolerated flush timing.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    truncated = False
    if lines and lines[-1] == "":
        lines.pop()
    elif lines:
        last = lines[-1]
        if last.strip():
            try:
                json.loads(last)
            except json.JSONDecodeError:
                truncated = True
                lines.pop()
        else:
            lines.pop()
    events = []
    for no, line in enumerate(lines, 1):
        if not line.strip():
            raise rs.Invalid(f"{path}:{no}: blank line")
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise rs.Invalid(f"{path}:{no}: invalid JSON") from exc
    return events, truncated


def build_error(error: dict[str, Any] | None) -> dict[str, Any] | None:
    if error is None:
        return None
    code = error.get("code")
    return {"code": code, "message": error.get("message"), "uncategorized": code is None or code not in rs.ERROR_CODES}


def derive_duration(snapshot: dict[str, Any]) -> int | None:
    if isinstance(snapshot.get("duration_ms"), int):
        return snapshot["duration_ms"]
    started, finished = snapshot.get("started_at"), snapshot.get("finished_at")
    if started and finished:
        return int((rs.timestamp(finished, "finished_at") - rs.timestamp(started, "started_at")).total_seconds() * 1000)
    return None


def build_node(node_id: str, latest: dict[str, Any], trail: list[dict[str, Any]], campaign_root: Path, pass_id: str) -> dict[str, Any]:
    attempt = latest["attempt"]
    snapshot: dict[str, Any] = {}
    for event in trail:
        if event["attempt"] == attempt:
            snapshot.update(event)
    log_by_attempt: dict[str, str | None] = {}
    exit_code_by_attempt: dict[str, int | None] = {}
    for a in sorted({e["attempt"] for e in trail}):
        a_snapshot: dict[str, Any] = {}
        for e in trail:
            if e["attempt"] == a:
                a_snapshot.update(e)
        a_dir = attempt_dir_for(campaign_root, pass_id, node_id, a)
        log_by_attempt[str(a)] = resolve_log_path(a_dir, a_snapshot.get("harness"))
        exit_code_by_attempt[str(a)] = read_exit_code(campaign_root, a_dir, a_snapshot.get("artifact_paths"))
    return {
        "node_id": node_id,
        "node_kind": latest["node_kind"],
        "state": latest["state"],
        "attempt": attempt,
        "dependencies": latest.get("dependencies", []),
        "harness": snapshot.get("harness"),
        "model": snapshot.get("model"),
        "duration_ms": derive_duration(snapshot),
        "error": build_error(snapshot.get("error")),
        "artifact_paths": snapshot.get("artifact_paths"),
        "log_by_attempt": log_by_attempt,
        "exit_code_by_attempt": exit_code_by_attempt,
        "attempts": trail,
        "liveness": None,
    }


def attempt_dir_for(campaign_root: Path, pass_id: str, node_id: str, attempt: int) -> Path:
    return campaign_root / "passes" / pass_id / "attempts" / f"{node_id}-{attempt}"


def resolve_log_path(attempt_dir: Path, harness: str | None) -> str | None:
    """Real harness log filenames don't always match the harness name (e.g. harness "claude-code"
    writes claude.log/claude-stderr.log; "pi-subagents" writes nothing at all). Prefer an exact
    <harness>.log match, else fall back to whatever *.log file actually exists in the attempt dir."""
    if not attempt_dir.is_dir():
        return None
    if harness:
        for name in (f"{harness}.log", f"{harness}-stderr.log"):
            if (attempt_dir / name).is_file():
                return name
    logs = sorted(attempt_dir.glob("*.log"), key=lambda p: ("stderr" in p.name, p.name))
    return logs[0].name if logs else None


def read_exit_code(campaign_root: Path, attempt_dir: Path, artifact_paths: dict[str, Any] | None) -> int | None:
    """error.exit_code in node-result.json (per node-execution-v1.schema.json) is authoritative;
    a bare exit-code file next to the attempt is only a fallback for attempts with no result yet."""
    result_rel = (artifact_paths or {}).get("result") or (artifact_paths or {}).get("node_result")
    if result_rel:
        result_path = resolve_campaign_file(campaign_root, result_rel)
        if result_path is not None and result_path.is_file():
            try:
                data = json.loads(result_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                data = None
            if isinstance(data, dict):
                exit_code = (data.get("error") or {}).get("exit_code")
                if isinstance(exit_code, int):
                    return exit_code
    fallback = attempt_dir / "exit-code"
    if fallback.is_file():
        try:
            return int(fallback.read_text(encoding="utf-8").strip())
        except (ValueError, OSError):
            return None
    return None


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def max_mtime(attempt_dir: Path) -> float | None:
    if not attempt_dir.is_dir():
        return None
    times = [p.stat().st_mtime for p in attempt_dir.rglob("*") if p.is_file()]
    return max(times) if times else None


def classify_liveness(attempt_dir: Path) -> dict[str, Any]:
    """Never fabricate 'running': absence of evidence resolves to 'unknown'."""
    pid_path = next((attempt_dir / name for name in PID_FILENAMES if (attempt_dir / name).is_file()), None)
    if pid_path is None:
        return {"liveness": "unknown", "pid": None}
    try:
        pid = int(pid_path.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return {"liveness": "unknown", "pid": None}
    if pid <= 0:
        return {"liveness": "unknown", "pid": None}
    if not pid_alive(pid):
        return {"liveness": "process_gone", "pid": pid, "exit_code_present": (attempt_dir / "exit-code").is_file()}
    mtime = max_mtime(attempt_dir)
    age = (time.time() - mtime) if mtime is not None else None
    if age is not None and age <= QUIET_THRESHOLD_MINUTES * 60:
        return {"liveness": "running", "pid": pid}
    return {"liveness": "quiet", "pid": pid, "seconds_since_last_write": age}


def source_count(campaign_root: Path) -> int | None:
    path = campaign_root / "source-ledger.jsonl"
    if not path.is_file():
        return None
    return len(rs.folded(rs.read_jsonl(path, rs.validate_ledger)))


def assemble(campaign_root: Path) -> dict[str, Any]:
    campaign_root = campaign_root.resolve()
    passes_dir = campaign_root / "passes"
    if not passes_dir.is_dir():
        raise rs.Invalid(f"no passes dir: {passes_dir}")
    pass_ids = sorted(p.name for p in passes_dir.iterdir() if p.is_dir() and (p / "iteration-manifest.jsonl").is_file())
    passes_out: dict[str, Any] = {}
    terminal_iterations: dict[str, Any] = {}
    state_counts: dict[str, int] = {}
    for pass_id in pass_ids:
        events, truncated = read_manifest_tolerant(passes_dir / pass_id / "iteration-manifest.jsonl")
        for event in events:
            rs.validate_manifest(event)
        rs.check_manifest_stream(events)
        trails: dict[str, list[dict[str, Any]]] = {}
        order: list[str] = []
        for event in events:
            nid = event["node_id"]
            if nid not in trails:
                trails[nid] = []
                order.append(nid)
            trails[nid].append(event)
        latest_by_node = rs.folded(events)  # per-pass fold only; never fold across passes
        nodes = []
        for nid in order:
            node = build_node(nid, latest_by_node[nid], trails[nid], campaign_root, pass_id)
            if node["state"] in RUNNING_STATES:
                node["liveness"] = classify_liveness(attempt_dir_for(campaign_root, pass_id, nid, node["attempt"]))
            state_counts[node["state"]] = state_counts.get(node["state"], 0) + 1
            nodes.append(node)
        terminal_iterations[pass_id] = next((e for e in latest_by_node.values() if e["node_kind"] == "iteration" and e["state"] in rs.TERMINAL), None)
        passes_out[pass_id] = {"pass_id": pass_id, "truncated_tail": truncated, "nodes": nodes}
    campaign = {
        "root": str(campaign_root),
        "pass_count": len(pass_ids),
        "terminal_iterations": terminal_iterations,
        "node_state_counts": state_counts,
        "source_count": source_count(campaign_root),
    }
    return {"campaign": campaign, "passes": passes_out}


def resolve_campaign_file(campaign_root: Path, rel_path: str | None) -> Path | None:
    """Contain a client-supplied relative path inside campaign_root. None means reject (403)."""
    if not rel_path or Path(rel_path).is_absolute():
        return None
    target = (campaign_root / rel_path).resolve()
    try:
        target.relative_to(campaign_root)
    except ValueError:
        return None
    return target


class GraphViewServer(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, addr: tuple[str, int], handler_cls: type, campaign_root: Path) -> None:
        super().__init__(addr, handler_cls)
        self.campaign_root = campaign_root


class GraphViewHandler(http.server.BaseHTTPRequestHandler):
    server: GraphViewServer

    def log_message(self, format: str, *args: Any) -> None:
        pass  # keep the terminal quiet; this is a dashboard, not a request log

    def _send(self, body: bytes, status: int, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, status: int = 200, content_type: str = "text/plain; charset=utf-8") -> None:
        self._send(text.encode("utf-8"), status, content_type)

    def _send_json(self, obj: Any, status: int = 200) -> None:
        self._send(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"), status, "application/json")

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        if parsed.path == "/":
            self._send_text(HTML_PAGE, content_type="text/html; charset=utf-8")
            return
        if parsed.path == "/api/state":
            try:
                state = assemble(self.server.campaign_root)
            except (rs.Invalid, OSError, ValueError) as exc:
                self._send_json({"error": str(exc)}, status=500)
                return
            self._send_json(state)
            return
        if parsed.path == "/api/file":
            qs = parse_qs(parsed.query)
            rel = (qs.get("path") or [None])[0]
            tail = (qs.get("tail") or [None])[0]
            try:
                target = resolve_campaign_file(self.server.campaign_root, rel)
                if target is None:
                    self._send_text("forbidden", status=403)
                    return
                if not target.is_file():
                    self._send_text("not found", status=404)
                    return
                size = target.stat().st_size
                with target.open("rb") as fh:
                    if tail:
                        start = max(0, size - MAX_FILE_BYTES)
                        fh.seek(start)
                        data = fh.read()
                        if start > 0:  # seeked into the middle of the file: drop the partial leading line
                            nl = data.find(b"\n")
                            data = data[nl + 1:] if nl != -1 else data
                    else:
                        data = fh.read(MAX_FILE_BYTES)
            except (ValueError, RuntimeError) as exc:
                self._send_text(f"bad request: {exc}", status=400)
                return
            except OSError as exc:
                self._send_text(f"not found: {exc}", status=404)
                return
            self._send_text(data.decode("utf-8", errors="replace"))
            return
        self._send_text("not found", status=404)


def serve(campaign_root: Path, port: int) -> None:
    root = campaign_root.resolve()
    if not (root / "passes").is_dir():
        raise rs.Invalid(f"no passes dir: {root / 'passes'}")
    httpd = GraphViewServer(("127.0.0.1", port), GraphViewHandler, root)
    print(f"http://127.0.0.1:{httpd.server_address[1]}/")
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()


HTML_PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>campaign graph</title>
<style>
:root {
  --bg: #f5f5f2;
  --bg-panel: #ffffff;
  --bg-raised: #ececE7;
  --border: #d8d8d2;
  --text: #1b1b18;
  --text-dim: #6b6b64;
  --accent: #3b5bdb;
  --ok: #1f8a4c;
  --warn: #b5890a;
  --dead: #b3261e;
  --unknown: #6f6f66;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #17181c;
    --bg-panel: #1f2126;
    --bg-raised: #26282e;
    --border: #33353c;
    --text: #e7e7e2;
    --text-dim: #9a9a92;
    --accent: #8aa4ff;
    --ok: #4cbf7c;
    --warn: #d9a441;
    --dead: #e2695c;
    --unknown: #9a9a90;
  }
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font: 13px/1.4 var(--mono);
  padding: 20px 24px 60px;
}
.num { font-variant-numeric: tabular-nums; }
h1 { font-size: 15px; margin: 0 0 4px; font-weight: 700; }
h1 span { color: var(--text-dim); font-weight: 400; }
h2 { font-size: 15px; margin: 0 0 2px; }
h3 { font-size: 11px; text-transform: uppercase; letter-spacing: .05em; color: var(--text-dim); margin: 18px 0 6px; }
a { color: var(--accent); }

.banner {
  margin: 10px 0 16px;
  padding: 8px 12px;
  border: 1px solid var(--dead);
  border-radius: 6px;
  background: color-mix(in srgb, var(--dead) 12%, var(--bg-panel));
  color: var(--dead);
  font-weight: 600;
}
.hidden { display: none !important; }

.rollup { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 18px; }
.tile {
  border: 1px solid var(--border);
  background: var(--bg-panel);
  border-radius: 6px;
  padding: 6px 10px;
  display: flex;
  flex-direction: column;
  min-width: 64px;
}
.tile-label { font-size: 9px; text-transform: uppercase; letter-spacing: .05em; color: var(--text-dim); }
.tile-value { font-size: 16px; font-weight: 700; }
.tile-failed .tile-value { color: var(--dead); }
.tile-running .tile-value, .tile-retrying .tile-value { color: var(--accent); }
.tile-saturated .tile-value, .tile-completed .tile-value { color: var(--ok); }
.terminal-tiles { min-width: 240px; }
.terminal-tiles .tile-value { font-size: 12px; font-weight: 400; }

.empty { color: var(--text-dim); }

details.pass {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-panel);
  margin-bottom: 10px;
  overflow: hidden;
}
details.pass > summary {
  cursor: pointer;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  list-style: none;
  background: var(--bg-raised);
}
details.pass > summary::-webkit-details-marker { display: none; }
.pass-id { font-weight: 700; }
.pass-summary { color: var(--text-dim); flex: 1; }
.tail-warn { color: var(--warn); font-size: 11px; }
.graph-wrap { overflow-x: auto; padding: 10px; }

.edge { fill: none; stroke: var(--border); stroke-width: 1.5; }

.node { cursor: pointer; outline: none; }
.node .shape { fill: var(--bg-panel); stroke: var(--text-dim); stroke-width: 1.5; }
.node:hover .shape, .node:focus .shape, .node:focus-visible .shape { stroke: var(--accent); stroke-width: 2.5; }

.state-pending .shape { fill: var(--bg-panel); stroke: var(--text-dim); stroke-dasharray: 5 4; }
.state-running .shape, .state-retrying .shape { fill: var(--bg-panel); stroke: var(--accent); stroke-width: 2; }
.state-completed .shape { fill: color-mix(in srgb, var(--ok) 16%, var(--bg-panel)); stroke: var(--ok); }
.state-failed .shape { fill: color-mix(in srgb, var(--dead) 10%, var(--bg-panel)); stroke: var(--dead); stroke-width: 3; }
.state-saturated .shape-outer { fill: none; stroke: var(--ok); }
.state-saturated .shape-inner { fill: color-mix(in srgb, var(--ok) 14%, var(--bg-panel)); stroke: var(--ok); }

.liveness-quiet .shape { stroke: var(--warn); }
.liveness-process_gone .shape { stroke: var(--dead); }
.liveness-unknown .shape, .liveness-unknown .shape-inner { fill: url(#hatch); }

.pulse-ring {
  fill: none;
  stroke: var(--accent);
  stroke-width: 2;
  transform-box: fill-box;
  transform-origin: center;
  animation: pulse 1.6s ease-out infinite;
}
@keyframes pulse {
  0% { stroke-opacity: .9; transform: scale(1); }
  70% { stroke-opacity: 0; transform: scale(1.2); }
  100% { stroke-opacity: 0; transform: scale(1.2); }
}
@media (prefers-reduced-motion: reduce) {
  .pulse-ring { animation: none; stroke-opacity: .8; }
}

.node-label { font: 10px/1.25 var(--mono); color: var(--text); display: flex; flex-direction: column; justify-content: center; height: 100%; overflow: hidden; pointer-events: none; }
.node-id { font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.node-state { color: var(--text-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-transform: uppercase; font-size: 9px; letter-spacing: .04em; }
.node-liveness { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 9px; }
.node-liveness.liveness-running { color: var(--accent); }
.node-liveness.liveness-quiet { color: var(--warn); }
.node-liveness.liveness-process_gone { color: var(--dead); }
.node-liveness.liveness-unknown { color: var(--unknown); font-weight: 700; }

#hatch rect { fill: var(--bg-panel); }
#hatch line { stroke: var(--unknown); stroke-width: 2; }

.backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.35); z-index: 10;
}
.drawer {
  position: fixed; top: 0; right: 0; bottom: 0; width: min(480px, 100vw);
  background: var(--bg-panel); border-left: 1px solid var(--border);
  transform: translateX(100%); transition: transform .15s ease-out;
  z-index: 11; overflow-y: auto; padding: 18px 20px 40px;
}
.drawer.open { transform: translateX(0); }
.drawer-close {
  position: absolute; top: 10px; right: 12px; font-size: 20px; line-height: 1;
  background: none; border: none; color: var(--text-dim); cursor: pointer; padding: 4px 8px;
}
.drawer-close:hover { color: var(--text); }
.drawer-meta { color: var(--text-dim); margin-bottom: 12px; }
.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; }
.field { display: flex; flex-direction: column; }
.field.muted { color: var(--text-dim); grid-column: 1 / -1; }
.field-label { font-size: 9px; text-transform: uppercase; letter-spacing: .05em; color: var(--text-dim); }
.field-value { font-size: 12px; }
.raw-code { color: var(--text-dim); }
.file-view {
  background: var(--bg-raised); border: 1px solid var(--border); border-radius: 6px;
  padding: 8px; font-size: 11px; white-space: pre-wrap; word-break: break-word; max-height: 240px; overflow-y: auto;
}
.artifact-row { margin-bottom: 6px; }
.artifact-link {
  background: var(--bg-raised); border: 1px solid var(--border); border-radius: 4px;
  color: var(--accent); cursor: pointer; padding: 3px 8px; font: inherit;
}
.path { color: var(--text-dim); font-size: 11px; margin-left: 6px; }
.attempt-row {
  display: block; width: 100%; text-align: left; background: var(--bg-panel);
  border: 1px solid var(--border); border-radius: 4px; color: var(--text);
  cursor: pointer; padding: 5px 8px; font: inherit; margin-bottom: 4px;
}
.attempt-row.active { border-color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, var(--bg-panel)); }
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute">
  <defs>
    <pattern id="hatch" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)">
      <rect width="6" height="6"></rect>
      <line x1="0" y1="0" x2="0" y2="6"></line>
    </pattern>
  </defs>
</svg>
<header>
  <h1>campaign graph — <span id="campaignRoot"></span></h1>
  <div id="rollup" class="rollup"></div>
</header>
<div id="banner" class="banner hidden" role="status" aria-live="polite"></div>
<main id="passes"><p class="empty">connecting…</p></main>
<div id="backdrop" class="backdrop hidden"></div>
<aside id="drawer" class="drawer" aria-hidden="true">
  <button id="drawerClose" class="drawer-close" aria-label="close detail panel">×</button>
  <div id="drawerBody" class="drawer-body"></div>
</aside>
<script>
(function () {
"use strict";
const POLL_MS = 2000;
const TERMINAL = new Set(["completed", "saturated", "failed"]);
const ERROR_CODES = new Set(["invalid_node_result", "invalid_node_result_format", "harness_infrastructure", "provider_empty_termination", "nonzero_exit", "timeout", "cancelled", "precondition_failed"]);
const COL_W = 190, ROW_H = 64, NODE_W = 150, NODE_H = 40, MARGIN = 20;

let lastGoodAt = null;
let manualOpen = new Map();
const drawerState = { passId: null, node: null, selectedAttempt: null };

function esc(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}

function fmtDuration(ms) {
  if (ms == null) return "—";
  if (ms < 1000) return ms + "ms";
  let s = ms / 1000;
  if (s < 60) return s.toFixed(1) + "s";
  let m = Math.floor(s / 60), rs = Math.round(s % 60);
  if (m < 60) return m + "m" + rs + "s";
  let h = Math.floor(m / 60), rm = m % 60;
  return h + "h" + rm + "m";
}
function fmtAgo(seconds) {
  if (seconds == null) return "unknown";
  if (seconds < 60) return Math.round(seconds) + "s";
  let m = Math.floor(seconds / 60), rs = Math.round(seconds % 60);
  if (m < 60) return m + "m" + rs + "s";
  let h = Math.floor(m / 60), rm = m % 60;
  return h + "h" + rm + "m";
}
function errUncategorized(code) { return code == null || !ERROR_CODES.has(code); }

// ---- layout ----
function computeDepths(nodes) {
  const byId = new Map(nodes.map(function (n) { return [n.node_id, n]; }));
  const memo = new Map();
  function depth(id, seen) {
    if (memo.has(id)) return memo.get(id);
    if (seen.has(id)) return 0;
    const node = byId.get(id);
    if (!node) return 0;
    const nextSeen = new Set(seen); nextSeen.add(id);
    let d = 0;
    for (const dep of (node.dependencies || [])) {
      if (byId.has(dep)) d = Math.max(d, depth(dep, nextSeen) + 1);
    }
    memo.set(id, d);
    return d;
  }
  const result = new Map();
  for (const n of nodes) result.set(n.node_id, depth(n.node_id, new Set()));
  return result;
}
function layoutPass(nodes) {
  const depths = computeDepths(nodes);
  const byDepth = new Map();
  for (const n of nodes) {
    const d = depths.get(n.node_id);
    if (!byDepth.has(d)) byDepth.set(d, []);
    byDepth.get(d).push(n);
  }
  const depthValues = [...depths.values()];
  const maxDepth = depthValues.length ? Math.max(...depthValues) : 0;
  const groupSizes = [...byDepth.values()].map(function (a) { return a.length; });
  const maxSiblings = groupSizes.length ? Math.max(...groupSizes) : 1;
  const pos = new Map();
  for (const entry of byDepth) {
    const d = entry[0], group = entry[1];
    const offset = (maxSiblings - group.length) / 2;
    group.forEach(function (n, i) {
      pos.set(n.node_id, { x: MARGIN + d * COL_W, y: MARGIN + (i + offset) * ROW_H });
    });
  }
  const width = MARGIN * 2 + maxDepth * COL_W + NODE_W;
  const height = MARGIN * 2 + Math.max(1, maxSiblings) * ROW_H;
  return { pos: pos, width: width, height: height };
}
function octagonPoints(x, y, w, h) {
  const c = Math.min(w, h) * 0.28;
  return [[x + c, y], [x + w - c, y], [x + w, y + c], [x + w, y + h - c],
          [x + w - c, y + h], [x + c, y + h], [x, y + h - c], [x, y + c]]
    .map(function (p) { return p[0] + "," + p[1]; }).join(" ");
}
function livenessLine(node) {
  if (!node.liveness) return "";
  const l = node.liveness.liveness;
  const text = l === "running" ? "● live"
    : l === "quiet" ? "◔ quiet " + fmtAgo(node.liveness.seconds_since_last_write)
    : l === "process_gone" ? "✕ process gone"
    : "▨ unknown";
  return '<span class="node-liveness liveness-' + l + '">' + text + "</span>";
}
function nodeSvg(passId, n, p) {
  const state = n.state;
  const liveness = n.liveness ? n.liveness.liveness : null;
  const cls = ["node", "state-" + state];
  if (liveness) cls.push("liveness-" + liveness);
  let shape;
  if (state === "failed") {
    shape = '<polygon class="shape" points="' + octagonPoints(p.x, p.y, NODE_W, NODE_H) + '" />';
  } else if (state === "saturated") {
    shape = '<rect class="shape shape-outer" x="' + p.x + '" y="' + p.y + '" width="' + NODE_W + '" height="' + NODE_H + '" rx="6"/>' +
      '<rect class="shape shape-inner" x="' + (p.x + 4) + '" y="' + (p.y + 4) + '" width="' + (NODE_W - 8) + '" height="' + (NODE_H - 8) + '" rx="4"/>';
  } else {
    shape = '<rect class="shape" x="' + p.x + '" y="' + p.y + '" width="' + NODE_W + '" height="' + NODE_H + '" rx="6"/>';
  }
  const pulse = (state === "running" || state === "retrying")
    ? '<rect class="pulse-ring" x="' + p.x + '" y="' + p.y + '" width="' + NODE_W + '" height="' + NODE_H + '" rx="6"/>' : "";
  return '<g class="' + cls.join(" ") + '" data-pass="' + esc(passId) + '" data-node="' + esc(n.node_id) + '" tabindex="0" role="button" ' +
    'aria-label="' + esc(n.node_id) + " " + esc(state) + (liveness ? " liveness " + esc(liveness) : "") + '">' +
    pulse + shape +
    '<foreignObject x="' + (p.x + 6) + '" y="' + (p.y + 3) + '" width="' + (NODE_W - 12) + '" height="' + (NODE_H - 6) + '">' +
      '<div xmlns="http://www.w3.org/1999/xhtml" class="node-label">' +
        '<span class="node-id">' + esc(n.node_id) + "</span>" +
        '<span class="node-state">' + esc(state) + (n.attempt > 1 ? " #" + n.attempt : "") + "</span>" +
        livenessLine(n) +
      "</div>" +
    "</foreignObject>" +
  "</g>";
}
function buildSvg(passId, nodes, pos, width, height) {
  let edges = "";
  for (const n of nodes) {
    const p2 = pos.get(n.node_id);
    for (const dep of (n.dependencies || [])) {
      const p1 = pos.get(dep);
      if (!p1) continue;
      const x1 = p1.x + NODE_W, y1 = p1.y + NODE_H / 2, x2 = p2.x, y2 = p2.y + NODE_H / 2;
      const mx = (x1 + x2) / 2;
      edges += '<path class="edge" d="M ' + x1 + " " + y1 + " C " + mx + " " + y1 + ", " + mx + " " + y2 + ", " + x2 + " " + y2 + '" />';
    }
  }
  const nodesSvg = nodes.map(function (n) { return nodeSvg(passId, n, pos.get(n.node_id)); }).join("");
  return '<svg viewBox="0 0 ' + width + " " + height + '" width="' + width + '" height="' + height + '" role="img" aria-label="dependency graph for pass ' + esc(passId) + '">' +
    '<g class="edges">' + edges + "</g>" +
    '<g class="nodes">' + nodesSvg + "</g>" +
  "</svg>";
}

// ---- rollup + passes ----
function tile(label, value, semantic) {
  const cls = semantic ? " tile-" + semantic : "";
  return '<div class="tile' + cls + '"><span class="tile-label">' + esc(label) + '</span><span class="tile-value num">' + esc(value) + "</span></div>";
}
function renderRollup(campaign) {
  document.getElementById("campaignRoot").textContent = campaign.root;
  const counts = campaign.node_state_counts || {};
  const order = ["pending", "running", "retrying", "completed", "saturated", "failed"];
  let html = "";
  html += tile("passes", campaign.pass_count);
  html += tile("sources", campaign.source_count == null ? "—" : campaign.source_count);
  for (const k of order) html += tile(k, counts[k] || 0, k);
  const terminals = Object.entries(campaign.terminal_iterations || {})
    .map(function (e) { return esc(e[0]) + ": " + (e[1] ? esc(e[1].state) : "—"); }).join("  ");
  html += '<div class="tile terminal-tiles"><span class="tile-label">terminal iterations</span><span class="tile-value">' + terminals + "</span></div>";
  document.getElementById("rollup").innerHTML = html;
}
function renderPassSection(pid, passObj, isOpen) {
  const counts = {};
  for (const n of passObj.nodes) counts[n.state] = (counts[n.state] || 0) + 1;
  const summary = Object.entries(counts).map(function (e) { return e[0] + " " + e[1]; }).join(" · ") || "no nodes";
  const warn = passObj.truncated_tail ? '<span class="tail-warn" title="manifest tail truncated (in-flight write)">⚠ truncated tail</span>' : "";
  const layout = layoutPass(passObj.nodes);
  const svg = buildSvg(pid, passObj.nodes, layout.pos, layout.width, layout.height);
  return '<details class="pass" data-pass="' + esc(pid) + '"' + (isOpen ? " open" : "") + ">" +
    '<summary><span class="pass-id">' + esc(pid) + '</span><span class="pass-summary">' + esc(summary) + "</span>" + warn + "</summary>" +
    '<div class="graph-wrap">' + svg + "</div>" +
  "</details>";
}
function renderPasses(data) {
  const order = Object.keys(data.passes);
  const newestFirst = [...order].reverse();
  let active = null;
  for (let i = order.length - 1; i >= 0; i--) {
    const p = data.passes[order[i]];
    if (p.nodes.some(function (n) { return !TERMINAL.has(n.state); })) { active = order[i]; break; }
  }
  if (active == null && order.length) active = order[order.length - 1];
  const container = document.getElementById("passes");
  if (order.length === 0) { container.innerHTML = '<p class="empty">no passes recorded yet.</p>'; return; }
  container.innerHTML = newestFirst.map(function (pid) {
    const isOpen = manualOpen.has(pid) ? manualOpen.get(pid) : (pid === active);
    return renderPassSection(pid, data.passes[pid], isOpen);
  }).join("");
  container.querySelectorAll("details.pass").forEach(function (details) {
    const pid = details.dataset.pass;
    details.addEventListener("toggle", function () { manualOpen.set(pid, details.open); });
  });
  wireNodeClicks(data);
}
function wireNodeClicks(data) {
  document.querySelectorAll(".node").forEach(function (g) {
    const open = function () {
      const pid = g.dataset.pass, nid = g.dataset.node;
      const node = data.passes[pid].nodes.find(function (n) { return n.node_id === nid; });
      openDrawer(pid, node);
    };
    g.addEventListener("click", open);
    g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } });
  });
}

// ---- drawer ----
function attemptSummaries(node) {
  const byAttempt = new Map();
  for (const ev of node.attempts) {
    if (!byAttempt.has(ev.attempt)) byAttempt.set(ev.attempt, {});
    Object.assign(byAttempt.get(ev.attempt), ev);
  }
  return [...byAttempt.keys()].sort(function (a, b) { return a - b; }).map(function (attempt) {
    const ev = byAttempt.get(attempt);
    return {
      attempt: attempt, state: ev.state, harness: ev.harness, model: ev.model,
      error: ev.error || null,
      duration_ms: (typeof ev.duration_ms === "number") ? ev.duration_ms :
        (ev.started_at && ev.finished_at) ? (new Date(ev.finished_at) - new Date(ev.started_at)) : null,
      artifact_paths: ev.artifact_paths || null,
    };
  });
}
function field(label, value) {
  return '<div class="field"><span class="field-label">' + esc(label) + '</span><span class="field-value num">' + esc(value) + "</span></div>";
}
function artifactLinks(paths) {
  if (!paths || Object.keys(paths).length === 0) return '<div class="muted">none recorded for this attempt</div>';
  return Object.entries(paths).map(function (e) {
    const label = e[0], path = e[1];
    return '<div class="artifact-row"><button class="artifact-link" data-path="' + esc(path) + '">' + esc(label) + "</button>" +
      '<span class="path">' + esc(path) + '</span><pre class="file-view hidden artifact-preview"></pre></div>';
  }).join("");
}
function attemptTrailHtml(summaries, selected) {
  return summaries.map(function (s) {
    const errPart = s.error ? " — " + esc(errUncategorized(s.error.code) ? "uncategorized" : s.error.code) : "";
    return '<button class="attempt-row' + (s.attempt === selected ? " active" : "") + '" data-attempt="' + s.attempt + '">' +
      "#" + s.attempt + " — " + esc(s.state) + errPart + "</button>";
  }).join("");
}
function loadLogSection(path, elId) {
  fetch("/api/file?path=" + encodeURIComponent(path) + "&tail=1")
    .then(function (r) { return r.ok ? r.text() : Promise.reject(r.status); })
    .then(function (t) {
      const lines = t.split("\n");
      document.getElementById(elId).textContent = lines.slice(Math.max(0, lines.length - 40)).join("\n");
    })
    .catch(function (status) {
      document.getElementById(elId).textContent = (typeof status === "number") ? "not available (HTTP " + status + ")" : "not available";
    });
}
function toggleArtifactPreview(btn) {
  const pre = btn.parentElement.querySelector(".artifact-preview");
  if (!pre.classList.contains("hidden")) { pre.classList.add("hidden"); return; }
  pre.classList.remove("hidden"); pre.textContent = "loading…";
  fetch("/api/file?path=" + encodeURIComponent(btn.dataset.path))
    .then(function (r) { return r.ok ? r.text() : Promise.reject(r.status); })
    .then(function (t) { pre.textContent = t; })
    .catch(function (status) { pre.textContent = "unavailable (" + status + ")"; });
}
function renderDrawer() {
  const passId = drawerState.passId, node = drawerState.node;
  if (!node) return;
  const summaries = attemptSummaries(node);
  const maxAttempt = summaries.reduce(function (m, s) { return Math.max(m, s.attempt); }, 1);
  const sel = summaries.find(function (s) { return s.attempt === drawerState.selectedAttempt; }) || summaries[summaries.length - 1];
  const attemptDir = "passes/" + passId + "/attempts/" + node.node_id + "-" + sel.attempt;
  const liveness = (sel.attempt === node.attempt) ? node.liveness : null;
  const errBlock = sel.error
    ? field("error.code", errUncategorized(sel.error.code) ? "uncategorized (" + (sel.error.code || "none") + ")" : sel.error.code) +
      field("error.message", sel.error.message || "")
    : '<div class="field muted">no error recorded for this attempt</div>';
  const exitCode = node.exit_code_by_attempt ? node.exit_code_by_attempt[String(sel.attempt)] : null;
  const logFile = node.log_by_attempt ? node.log_by_attempt[String(sel.attempt)] : null;
  const html =
    "<h2>" + esc(node.node_id) + "</h2>" +
    '<div class="drawer-meta">' + esc(node.node_kind) + " · pass " + esc(passId) + "</div>" +
    '<div class="field-grid">' +
      field("declared state", sel.state) +
      field("liveness", liveness ? liveness.liveness : "—") +
      field("attempt", sel.attempt + " of " + maxAttempt) +
      field("harness", sel.harness || "—") +
      field("model", sel.model || "—") +
      field("duration", fmtDuration(sel.duration_ms)) +
    "</div>" +
    "<h3>error</h3>" + errBlock +
    '<h3>exit code</h3><pre id="drawer-exitcode" class="file-view">' + esc(exitCode == null ? "not recorded" : exitCode) + '</pre>' +
    '<h3>harness log (last ~40 lines)</h3><pre id="drawer-log" class="file-view">loading…</pre>' +
    '<h3>artifacts</h3><div id="drawer-artifacts">' + artifactLinks(sel.artifact_paths) + "</div>" +
    '<h3>attempt trail</h3><div id="drawer-attempts">' + attemptTrailHtml(summaries, sel.attempt) + "</div>";
  document.getElementById("drawerBody").innerHTML = html;
  document.querySelectorAll(".attempt-row").forEach(function (row) {
    row.addEventListener("click", function () { drawerState.selectedAttempt = Number(row.dataset.attempt); renderDrawer(); });
  });
  document.querySelectorAll(".artifact-link").forEach(function (btn) {
    btn.addEventListener("click", function () { toggleArtifactPreview(btn); });
  });
  if (logFile) loadLogSection(attemptDir + "/" + logFile, "drawer-log");
  else document.getElementById("drawer-log").textContent = "no log file found for this attempt";
}
function openDrawer(passId, node) {
  drawerState.passId = passId; drawerState.node = node; drawerState.selectedAttempt = node.attempt;
  document.getElementById("backdrop").classList.remove("hidden");
  const drawer = document.getElementById("drawer");
  drawer.classList.add("open"); drawer.setAttribute("aria-hidden", "false");
  renderDrawer();
}
function closeDrawer() {
  document.getElementById("backdrop").classList.add("hidden");
  const drawer = document.getElementById("drawer");
  drawer.classList.remove("open"); drawer.setAttribute("aria-hidden", "true");
  drawerState.node = null; drawerState.passId = null;
}
document.getElementById("drawerClose").addEventListener("click", closeDrawer);
document.getElementById("backdrop").addEventListener("click", closeDrawer);
document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });

// ---- polling / freeze banner ----
function setBanner(failed) {
  const banner = document.getElementById("banner");
  if (!failed) { banner.classList.add("hidden"); return; }
  banner.classList.remove("hidden");
  tickBanner();
}
function tickBanner() {
  const banner = document.getElementById("banner");
  if (banner.classList.contains("hidden")) return;
  banner.textContent = (lastGoodAt == null)
    ? "live view not yet connected — retrying…"
    : "live view stalled — last update " + fmtAgo((Date.now() - lastGoodAt) / 1000) + " ago. data below is frozen.";
}
function render(data) {
  renderRollup(data.campaign);
  renderPasses(data);
  if (drawerState.node) {
    const passObj = data.passes[drawerState.passId];
    const fresh = passObj && passObj.nodes.find(function (n) { return n.node_id === drawerState.node.node_id; });
    if (fresh) { drawerState.node = fresh; renderDrawer(); }
  }
}
function poll() {
  fetch("/api/state")
    .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
    .then(function (data) { lastGoodAt = Date.now(); setBanner(false); render(data); })
    .catch(function () { setBanner(true); });
}
setBanner(true);
setInterval(tickBanner, 1000);
setInterval(poll, POLL_MS);
poll();
})();
</script>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--once", action="store_true", help="print the state JSON once and exit")
    parser.add_argument("--serve", action="store_true", help="serve the live dashboard on 127.0.0.1 until interrupted")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"port for --serve (default {DEFAULT_PORT})")
    args = parser.parse_args(argv)
    if args.serve:
        serve(args.campaign, args.port)
        return 0
    if not args.once:
        parser.error("one of --once or --serve is required")
    rs.emit(assemble(args.campaign))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except rs.Invalid as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
