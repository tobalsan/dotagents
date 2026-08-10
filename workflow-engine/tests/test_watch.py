"""wfe watch — read-only dashboard: journal/status folding, overlay, HTTP surface."""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from workflow_engine.watch import (
    DEFAULT_TIMEOUT_S,
    STALE_MARGIN_S,
    WatchError,
    WatchServer,
    build_state,
    make_server,
    read_journal,
    read_overlay,
    resolve_run_id,
)

# --- fixture builders --------------------------------------------------------


def _run_dir(tmp_path: Path, run_id: str = "run-1") -> Path:
    run_dir = tmp_path / "campaign" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_journal(run_dir: Path, rows: list[dict]) -> None:
    text = "\n".join(json.dumps(r) for r in rows) + "\n"
    (run_dir / "journal.jsonl").write_text(text, encoding="utf-8")


def write_status(run_dir: Path, calls: list[dict] | None = None, **fields) -> None:
    """Same shape engine.write_status emits: counts + full per-call entries."""
    calls = list(calls or [])
    counts = {"total": len(calls), "running": 0, "ok": 0, "error": 0, "replayed": 0}
    for call in calls:
        counts[call["state"]] = counts.get(call["state"], 0) + 1
    status = {
        "run_id": run_dir.name,
        "workflow": "wf.py",
        "state": "running",
        "phase": "p1",
        "started_at": "2026-08-10T10:00:00Z",
        "updated_at": "2026-08-10T10:00:03Z",
        "elapsed_s": 3.0,
        "counts": counts,
        "calls": calls,
    }
    status.update(fields)
    (run_dir / "status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")


def run_start(**kw) -> dict:
    row = {
        "event": "run_start",
        "ts": "2026-08-10T10:00:00Z",
        "run_id": "run-1",
        "workflow": "wf.py",
        "args": {},
        "concurrency": 6,
        "timeout_s": 900.0,
        "routes": {"default": {"harness": "fake", "model": "m"}},
    }
    row.update(kw)
    return row


def phase(title: str) -> dict:
    return {"event": "phase", "ts": "2026-08-10T10:00:01Z", "title": title}


def call_start(key: str, **kw) -> dict:
    row = {
        "event": "call_start",
        "ts": "2026-08-10T10:00:02Z",
        "call_key": key,
        "label": key,
        "route": "default",
        "harness": "fake",
        "model": "m",
        "started_at": "2026-08-10T10:00:02Z",
    }
    row.update(kw)
    return row


def call_end(key: str, status: str = "ok", **kw) -> dict:
    row = {
        "event": "call_end",
        "ts": "2026-08-10T10:00:03Z",
        "call_key": key,
        "label": key,
        "route": "default",
        "harness": "fake",
        "model": "m",
        "attempts": 1,
        "status": status,
        "started_at": "2026-08-10T10:00:02Z",
        "finished_at": "2026-08-10T10:00:03Z",
        "duration_ms": 1000,
        "cost_hint": 0.01,
        "result": "ok",
    }
    row.update(kw)
    return row


def run_end(**kw) -> dict:
    row = {"event": "run_end", "ts": "2026-08-10T10:00:04Z", "state": "completed", "duration_ms": 4000}
    row.update(kw)
    return row


def status_call(key: str, **kw) -> dict:
    row = {
        "call_key": key,
        "label": key,
        "route": "default",
        "harness": "fake",
        "model": "m",
        "state": "ok",
        "attempt": 1,
        "started_at": "2026-08-10T10:00:02Z",
        "duration_ms": 1000,
        "error": None,
    }
    row.update(kw)
    return row


def replayed_call(key: str, **kw) -> dict:
    """What engine.py writes for a memo/journal replay: state ok, attempt 0, no harness."""
    return status_call(key, harness=None, model=None, attempt=0, duration_ms=0, **kw)


# --- fold / merge, via build_state -------------------------------------------


def test_fold_resume_duplicates_are_not_double_counted(tmp_path: Path) -> None:
    """Two run_start segments: attempt 1 fails A; resume reruns A ok + new B; status adds replayed C."""
    run_dir = _run_dir(tmp_path)
    write_journal(
        run_dir,
        [
            run_start(),
            phase("p1"),
            call_start("A"),
            call_end("A", status="error", error={"kind": "timeout", "message": "boom"}),
            run_end(state="failed"),
            run_start(),
            phase("p1"),
            call_start("A"),
            call_end("A", status="ok"),
            call_start("B"),
            call_end("B", status="ok"),
        ],
    )
    write_status(
        run_dir,
        state="completed",
        calls=[replayed_call("C"), status_call("A"), status_call("B")],
    )

    state = build_state(run_dir.parent.parent, "run-1")
    calls = {c["call_key"]: c for c in state["calls"]}

    assert set(calls) == {"A", "B", "C"}
    assert calls["A"]["state"] == "ok" and calls["A"]["replayed"] is False
    assert calls["B"]["state"] == "ok" and calls["B"]["replayed"] is False
    assert calls["C"]["state"] == "ok" and calls["C"]["replayed"] is True
    assert state["counts"]["total"] == 3
    assert state["counts"]["replayed"] == 1


def test_build_state_without_status_json_shows_journal_calls_only(tmp_path: Path) -> None:
    """No status.json: build_state must not crash, and can only see what the journal recorded.

    A call that exists only in status.json (a replay) is invisible without status.json —
    merge_calls has nothing to merge in.
    """
    run_dir = _run_dir(tmp_path)
    write_journal(
        run_dir,
        [
            run_start(),
            phase("p1"),
            call_start("A"),
            call_end("A", status="ok"),
            call_start("B"),
        ],
    )

    state = build_state(run_dir.parent.parent, "run-1")
    calls = {c["call_key"]: c for c in state["calls"]}

    assert state["error"] is None
    assert set(calls) == {"A", "B"}
    assert calls["A"]["state"] == "ok" and calls["A"]["replayed"] is False
    assert calls["B"]["state"] == "running" and calls["B"]["replayed"] is False
    assert state["counts"]["total"] == 2
    assert state["counts"]["ok"] == 1
    assert state["counts"]["running"] == 1
    assert state["counts"]["replayed"] == 0
    assert state["state"] == "running"


def test_in_flight_call_state_is_running(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)
    write_journal(run_dir, [run_start(), phase("p1"), call_start("A")])

    state = build_state(run_dir.parent.parent, "run-1")

    assert state["calls"][0]["state"] == "running"
    assert state["state"] == "running"


def test_open_call_survives_run_end_as_interrupted(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)
    write_journal(run_dir, [run_start(), phase("p1"), call_start("A"), run_end(state="failed")])

    state = build_state(run_dir.parent.parent, "run-1")

    assert state["calls"][0]["state"] == "interrupted"


def test_call_end_error_surfaces_kind_and_message(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)
    write_journal(
        run_dir,
        [
            run_start(),
            phase("p1"),
            call_start("A"),
            call_end("A", status="error", error={"kind": "schema", "message": "missing field: foo"}),
        ],
    )

    state = build_state(run_dir.parent.parent, "run-1")
    call = state["calls"][0]

    assert call["state"] == "error"
    assert call["error"] == {"kind": "schema", "message": "missing field: foo"}


def test_route_error_status_only_call_is_not_a_replay(tmp_path: Path) -> None:
    """Route resolution fails before any journal row: status-only, state error, error is a string."""
    run_dir = _run_dir(tmp_path)
    write_journal(run_dir, [run_start(), phase("p1")])
    write_status(
        run_dir,
        state="failed",
        calls=[
            status_call(
                "A",
                state="error",
                attempt=0,
                harness=None,
                model=None,
                route="nope",
                duration_ms=0,
                error="route: unknown route: nope",
            )
        ],
    )

    state = build_state(run_dir.parent.parent, "run-1")
    call = state["calls"][0]

    assert call["state"] == "error"
    assert call["replayed"] is False
    assert call["error"] == {"kind": "route", "message": "unknown route: nope"}
    assert state["counts"] == {
        "total": 1,
        "ok": 0,
        "error": 1,
        "running": 0,
        "interrupted": 0,
        "replayed": 0,
        "unknown": 0,
    }


def test_unrecognized_status_call_state_becomes_unknown(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)
    write_journal(run_dir, [run_start(), phase("p1")])
    write_status(run_dir, calls=[status_call("A", state="weird")])

    state = build_state(run_dir.parent.parent, "run-1")

    assert state["calls"][0]["state"] == "unknown"
    assert state["calls"][0]["replayed"] is False
    assert state["counts"]["unknown"] == 1


def test_call_ending_after_a_resume_stays_in_the_current_segment(tmp_path: Path) -> None:
    """call_start in segment 1, call_end in segment 2: the segment filter must keep it."""
    run_dir = _run_dir(tmp_path)
    write_journal(run_dir, [run_start(), phase("p1"), call_start("A"), run_start(), phase("p1"), call_end("A")])

    state = build_state(run_dir.parent.parent, "run-1")
    calls = {c["call_key"]: c for c in state["calls"]}

    assert set(calls) == {"A"}
    assert calls["A"]["state"] == "ok"


def test_counts_come_from_the_merged_calls_not_status_json(tmp_path: Path) -> None:
    """status.json's own counts are stale/segment-blind; tiles must match the cards."""
    run_dir = _run_dir(tmp_path)
    write_journal(run_dir, [run_start(), phase("p1"), call_start("A"), run_end(state="interrupted")])
    write_status(run_dir, counts={"total": 99, "running": 99, "ok": 99, "error": 99, "replayed": 99})

    state = build_state(run_dir.parent.parent, "run-1")

    assert state["counts"]["total"] == 1
    assert state["counts"]["interrupted"] == 1
    assert state["counts"]["running"] == 0


def test_killed_running_run_reports_stale_not_running(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)
    write_journal(run_dir, [run_start(), phase("p1"), call_start("A")])
    write_status(run_dir, state="running", calls=[status_call("A", state="running", duration_ms=None)])
    threshold = DEFAULT_TIMEOUT_S + STALE_MARGIN_S
    old = time.time() - threshold - 30
    os.utime(run_dir / "journal.jsonl", (old, old))

    state = build_state(run_dir.parent.parent, "run-1")

    assert state["stale"] is True
    assert state["state"] == "stale"
    assert state["raw_state"] == "running"
    assert state["stale_after_s"] == threshold
    assert state["journal_age_s"] > threshold


def test_fresh_journal_on_a_running_run_is_not_stale(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)
    write_journal(run_dir, [run_start(), phase("p1"), call_start("A")])
    write_status(run_dir, state="running", calls=[status_call("A", state="running", duration_ms=None)])

    state = build_state(run_dir.parent.parent, "run-1")

    assert state["stale"] is False
    assert state["state"] == "running"


def test_stale_threshold_follows_the_runs_own_timeout(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)
    write_journal(run_dir, [run_start(timeout_s=2700.0), phase("p1"), call_start("A")])
    write_status(run_dir, state="running", calls=[status_call("A", state="running", duration_ms=None)])
    old = time.time() - 1200  # past the 900s default, well inside this run's 2700s timeout
    os.utime(run_dir / "journal.jsonl", (old, old))

    state = build_state(run_dir.parent.parent, "run-1")

    assert state["stale_after_s"] == 2700.0 + STALE_MARGIN_S
    assert state["stale"] is False
    assert state["state"] == "running"


def test_crash_truncated_tail_line_is_skipped(tmp_path: Path) -> None:
    run_dir = _run_dir(tmp_path)
    journal = run_dir / "journal.jsonl"
    lines = [json.dumps(run_start()), json.dumps(phase("p1")), json.dumps(call_start("A")), json.dumps(call_end("A"))]
    journal.write_text("\n".join(lines) + "\n" + '{"event": "call_start", "call_key": "B", "rou', encoding="utf-8")

    rows = read_journal(journal)

    assert len(rows) == 4
    assert rows[-1]["call_key"] == "A"


# --- missing run / empty campaign --------------------------------------------


def test_resolve_run_id_raises_when_no_runs_exist(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    campaign.mkdir()

    with pytest.raises(WatchError):
        resolve_run_id(campaign, None)


def test_build_state_on_empty_campaign_reports_error_without_raising(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    campaign.mkdir()

    state = build_state(campaign, None)

    assert state["error"] is not None
    assert state["calls"] == []
    assert state["run_id"] is None


# --- overlay -------------------------------------------------------------------


def test_overlay_absent_without_coverage_map(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    campaign.mkdir()

    assert read_overlay(campaign) is None


def test_overlay_reports_branches_counts_and_latest_pass(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    campaign.mkdir()
    (campaign / "coverage-map.json").write_text(
        json.dumps(
            {
                "topic": "market makers",
                "branches": [
                    {"id": "b1", "name": "b1", "status": "covered"},
                    {"id": "b2", "name": "b2", "status": "partial"},
                    {"id": "b3", "name": "b3", "status": "thin"},
                    {"id": "b4", "name": "b4", "status": "thin"},
                ],
            }
        ),
        encoding="utf-8",
    )
    (campaign / "source-ledger.jsonl").write_text('{"a": 1}\n{"b": 2}\n\n', encoding="utf-8")
    (campaign / "notes.jsonl").write_text('{"n": 1}\n', encoding="utf-8")

    pass1 = campaign / "passes" / "pass-1"
    pass2 = campaign / "passes" / "pass-2"
    pass1.mkdir(parents=True)
    pass2.mkdir(parents=True)
    (pass1 / "gap-report.json").write_text(
        json.dumps({"pass": 1, "gaps": ["g1"], "new_sources": [], "rejections": [], "new_branches": []}),
        encoding="utf-8",
    )
    (pass2 / "gap-report.json").write_text(
        json.dumps(
            {"pass": 2, "gaps": ["g1", "g2"], "new_sources": ["s1"], "rejections": [], "new_branches": ["nb"]}
        ),
        encoding="utf-8",
    )

    overlay = read_overlay(campaign)

    assert overlay["topic"] == "market makers"
    assert overlay["branch_counts"] == {"covered": 1, "partial": 1, "thin": 2}
    assert overlay["sources"] == 2
    assert overlay["notes"] == 1
    assert overlay["gap_report"] == {"pass": 2, "gaps": 2, "new_sources": 1, "rejections": 0, "new_branches": 1}


def test_overlay_latest_pass_is_numeric_not_lexicographic(tmp_path: Path) -> None:
    """pass-10 must beat pass-2 by numeric value, not by string comparison."""
    campaign = tmp_path / "campaign"
    campaign.mkdir()
    (campaign / "coverage-map.json").write_text(json.dumps({"branches": []}), encoding="utf-8")

    for n in (2, 10):
        d = campaign / "passes" / f"pass-{n}"
        d.mkdir(parents=True)
        (d / "gap-report.json").write_text(
            json.dumps({"pass": n, "gaps": [], "new_sources": [], "rejections": [], "new_branches": []}),
            encoding="utf-8",
        )

    overlay = read_overlay(campaign)

    assert overlay["gap_report"]["pass"] == 10


# --- HTTP surface --------------------------------------------------------------


@pytest.fixture
def server():
    servers: list[WatchServer] = []

    def start(campaign_dir: Path, run_id: str | None = None) -> WatchServer:
        srv = make_server(campaign_dir, run_id, 0)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        servers.append(srv)
        return srv

    yield start
    for srv in servers:
        srv.shutdown()
        srv.server_close()


def _get(srv: WatchServer, path: str, host: str | None = None) -> tuple[int, bytes]:
    url = f"http://127.0.0.1:{srv.server_address[1]}{path}"
    req = urllib.request.Request(url, headers={"Host": host} if host else {})
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, res.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def _post(srv: WatchServer, path: str) -> int:
    req = urllib.request.Request(f"http://127.0.0.1:{srv.server_address[1]}{path}", method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            return res.status
    except urllib.error.HTTPError as exc:
        return exc.code


def test_api_state_on_empty_campaign_is_clean_json_not_500(tmp_path: Path, server) -> None:
    campaign = tmp_path / "campaign"
    campaign.mkdir()
    srv = server(campaign)

    status, body = _get(srv, "/api/state")
    payload = json.loads(body)

    assert status == 200
    assert payload["error"]
    assert payload["calls"] == []


def test_run_query_param_rejects_traversal_and_embedded_slash(tmp_path: Path, server) -> None:
    """resolve_run_id validates before any run-dir path is built, so build_state never touches those paths."""
    campaign = tmp_path / "campaign"
    campaign.mkdir()
    srv = server(campaign)

    for bad in ("../x", "a/b"):
        status, body = _get(srv, f"/api/state?run={bad}")
        payload = json.loads(body)
        assert status == 200  # build_state reports problems in "error"; it never 500s or 4xxs
        assert "invalid run id" in payload["error"]
        assert payload["calls"] == []
    assert not (campaign / "x").exists()


def test_run_query_param_rejects_a_valid_name_that_is_not_a_run(tmp_path: Path, server) -> None:
    """A name that clears the charset guard still has to be a run this campaign holds."""
    run_dir = _run_dir(tmp_path)
    write_journal(run_dir, [run_start(), phase("p1"), call_start("A"), call_end("A")])
    srv = server(run_dir.parent.parent)

    status, body = _get(srv, "/api/state?run=run-404")
    payload = json.loads(body)

    assert status == 200
    assert payload["error"] == "unknown run: run-404"
    assert payload["calls"] == []


def _snapshot(root: Path) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for path in sorted(root.rglob("*")):
        st = path.stat()
        out[str(path.relative_to(root))] = (st.st_mtime_ns, st.st_size if path.is_file() else -1)
    return out


def test_serving_a_populated_campaign_writes_nothing(tmp_path: Path, server) -> None:
    campaign = tmp_path / "campaign"
    run_dir = _run_dir(tmp_path)
    write_journal(run_dir, [run_start(), phase("p1"), call_start("A"), call_end("A"), call_start("B")])
    write_status(run_dir, calls=[status_call("A"), status_call("B", state="running", duration_ms=None)])
    (run_dir / "logs").mkdir()
    (run_dir / "logs" / "A.a1.out").write_text("hello\n", encoding="utf-8")
    (campaign / "coverage-map.json").write_text(
        json.dumps({"topic": "t", "branches": [{"id": "b1", "name": "b1", "status": "covered"}]}), encoding="utf-8"
    )
    (campaign / "source-ledger.jsonl").write_text('{"a": 1}\n', encoding="utf-8")
    (campaign / "notes.jsonl").write_text('{"n": 1}\n', encoding="utf-8")
    gap = campaign / "passes" / "pass-1"
    gap.mkdir(parents=True)
    (gap / "gap-report.json").write_text(json.dumps({"pass": 1, "gaps": ["g"]}), encoding="utf-8")

    before = _snapshot(campaign)
    srv = server(campaign)
    for path in ("/", "/api/state", "/api/state?run=run-1", "/api/state?run=run-404", "/api/state?run=../x"):
        status, _ = _get(srv, path)
        assert status == 200

    assert _snapshot(campaign) == before


def test_evil_host_header_is_403(tmp_path: Path, server) -> None:
    campaign = tmp_path / "campaign"
    campaign.mkdir()
    srv = server(campaign)

    assert _get(srv, "/", host="evil.example")[0] == 403
    assert _get(srv, "/api/state", host="evil.example")[0] == 403
    assert _get(srv, "/", host=f"127.0.0.1:{srv.server_address[1]}")[0] == 200
    assert _get(srv, "/", host=f"localhost:{srv.server_address[1]}")[0] == 200


def test_make_server_binds_loopback_only(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    campaign.mkdir()
    srv = make_server(campaign, None, 0)
    try:
        assert srv.server_address[0] == "127.0.0.1"
    finally:
        srv.server_close()


def test_unknown_path_is_404(tmp_path: Path, server) -> None:
    campaign = tmp_path / "campaign"
    campaign.mkdir()
    srv = server(campaign)

    status, _ = _get(srv, "/nope")

    assert status == 404


def test_post_is_405(tmp_path: Path, server) -> None:
    campaign = tmp_path / "campaign"
    campaign.mkdir()
    srv = server(campaign)

    assert _post(srv, "/api/state") == 405
