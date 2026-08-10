"""Engine behaviour: journal + resume, schema retry, isolation, concurrency, timeout."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

import pytest

from conftest import make_run, read_journal, routes, rows, spawns, write_workflow
from workflow_engine.engine import AgentError, call_key

TWO_CALLS = """
from workflow_engine import agent, parallel, phase

async def run(args, ctx):
    with phase("work"):
        out = await parallel([
            agent("alpha @@EMIT:A@@", label="a"),
            agent("beta @@EMIT:B@@", label="b"),
        ])
    ctx.log("done")
    return out
"""


# --- journal + resume ------------------------------------------------------


def test_journal_records_every_call(tmp_path: Path, counter: Path) -> None:
    wf = write_workflow(tmp_path, TWO_CALLS)
    run = make_run(tmp_path)
    result = asyncio.run(run.execute(wf, {}))

    assert result == ["A", "B"]
    assert spawns(counter) == 2
    ends = rows(run.run_dir, "call_end")
    assert {r["result"] for r in ends} == {"A", "B"}
    assert all(r["status"] == "ok" and r["attempts"] == 1 for r in ends)
    assert len(rows(run.run_dir, "call_start")) == 2
    assert [r["title"] for r in rows(run.run_dir, "phase")] == ["work"]
    assert [r["msg"] for r in rows(run.run_dir, "log")] == ["done"]
    assert rows(run.run_dir, "run_end")[0]["state"] == "completed"

    manifest = rows(run.run_dir, "run_start")[0]  # the run_start row is the run manifest
    assert manifest["workflow"] == str(wf)
    assert manifest["concurrency"] == 6 and manifest["timeout_s"] == 900.0
    assert manifest["routes"]["default"] == {"harness": "fake", "model": None}


def test_resume_replays_without_live_calls(tmp_path: Path, counter: Path) -> None:
    wf = write_workflow(tmp_path, TWO_CALLS)
    first = make_run(tmp_path)
    asyncio.run(first.execute(wf, {}))
    assert spawns(counter) == 2

    second = make_run(tmp_path, resume=True)
    assert asyncio.run(second.execute(wf, {})) == ["A", "B"]

    assert spawns(counter) == 2  # zero live calls on the resumed run
    assert second.counts == {"total": 2, "running": 0, "ok": 2, "error": 0, "replayed": 2}
    assert len(rows(second.run_dir, "call_end")) == 2  # no new call_end rows appended


def test_resume_reruns_only_failed_lanes(tmp_path: Path, counter: Path) -> None:
    body = """
from workflow_engine import agent, parallel

async def run(args, ctx):
    marker = "@@FAIL@@" if args.get("break") else "@@EMIT:fixed@@"
    return await parallel([
        agent("ok lane @@EMIT:kept@@", label="ok"),
        agent("flaky lane " + marker, label="flaky"),
    ])
"""
    wf = write_workflow(tmp_path, body)
    first = make_run(tmp_path)
    assert asyncio.run(first.execute(wf, {"break": "1"})) == ["kept", None]
    assert first.counts["ok"] == 1 and first.counts["error"] == 1
    assert spawns(counter) == 2

    second = make_run(tmp_path, resume=True)
    assert asyncio.run(second.execute(wf, {"break": "1"})) == ["kept", None]
    # sibling survived in the journal; only the failed lane ran again
    assert spawns(counter) == 3
    assert second.counts["replayed"] == 1


def test_resume_ignores_truncated_journal_tail(tmp_path: Path, counter: Path) -> None:
    wf = write_workflow(tmp_path, TWO_CALLS)
    first = make_run(tmp_path)
    asyncio.run(first.execute(wf, {}))
    with open(first.run_dir / "journal.jsonl", "a", encoding="utf-8") as fh:
        fh.write('{"event": "call_end", "call_k')  # crash-truncated line

    second = make_run(tmp_path, resume=True)
    assert asyncio.run(second.execute(wf, {})) == ["A", "B"]
    assert spawns(counter) == 2


def test_call_key_is_stable_and_label_sensitive() -> None:
    schema = {"type": "object", "properties": {"b": {}, "a": {}}}
    assert call_key("p", schema, "default", None) == call_key("p", dict(reversed(list(schema.items()))), "default", None)
    assert call_key("p", None, "default", "x") != call_key("p", None, "default", "y")


def test_large_result_spills_to_results_dir(tmp_path: Path) -> None:
    body = """
from workflow_engine import agent

async def run(args, ctx):
    return await agent("big @@EMIT:" + "z" * 70000 + "@@", label="big")
"""
    run = make_run(tmp_path)
    result = asyncio.run(run.execute(write_workflow(tmp_path, body), {}))
    assert len(result) == 70000

    end = rows(run.run_dir, "call_end")[0]
    assert "result" not in end and end["result_path"].startswith("results/")
    assert (run.run_dir / end["result_path"]).is_file()

    resumed = make_run(tmp_path, resume=True)
    assert asyncio.run(resumed.execute(write_workflow(tmp_path, body), {})) == result


# --- schema retry ----------------------------------------------------------


SCHEMA_WF = """
from workflow_engine import agent

SCHEMA = {"type": "object", "required": ["n"], "properties": {"n": {"type": "integer"}}}

async def run(args, ctx):
    return await agent("produce a number", schema=SCHEMA, label="num")
"""


def test_schema_retry_loop_recovers_inside_the_call(tmp_path: Path, counter: Path) -> None:
    flaky_counter = tmp_path / "flaky.txt"
    run = make_run(tmp_path, routes=routes(mode="flaky", extra=[str(flaky_counter)]))
    result = asyncio.run(run.execute(write_workflow(tmp_path, SCHEMA_WF), {}))

    assert result == {"n": 3, "saw_repair": True}  # repair suffix was fed back to the worker
    assert spawns(counter) == 3  # two rejected attempts + one good one
    end = rows(run.run_dir, "call_end")[0]
    assert end["status"] == "ok" and end["attempts"] == 3
    assert run.counts["error"] == 0  # a format error is never a failed node
    assert len(rows(run.run_dir, "call_start")) == 1  # one logical call


def test_schema_exhaustion_fails_the_call(tmp_path: Path, counter: Path) -> None:
    body = """
from workflow_engine import agent

SCHEMA = {"type": "object", "required": ["n"], "properties": {"n": {"type": "integer"}}}

async def run(args, ctx):
    return await agent("no json here @@EMIT:just prose@@", schema=SCHEMA, label="bad")
"""
    run = make_run(tmp_path)
    with pytest.raises(AgentError) as excinfo:
        asyncio.run(run.execute(write_workflow(tmp_path, body), {}))

    assert excinfo.value.kind == "schema"
    assert spawns(counter) == 3
    end = rows(run.run_dir, "call_end")[0]
    assert end["status"] == "error" and end["attempts"] == 3 and end["error"]["kind"] == "schema"
    assert rows(run.run_dir, "run_end")[0]["state"] == "failed"


def test_schema_result_is_parsed_from_fenced_json(tmp_path: Path) -> None:
    body = """
from workflow_engine import agent

SCHEMA = {"type": "object", "required": ["n"], "properties": {"n": {"type": "integer"}}}

async def run(args, ctx):
    fenced = "here you go:\\n```json\\n{\\"n\\": 7}\\n```\\n"
    return await agent("x @@EMIT:" + fenced + "@@", schema=SCHEMA, label="fenced")
"""
    run = make_run(tmp_path)
    assert asyncio.run(run.execute(write_workflow(tmp_path, body), {})) == {"n": 7}


# --- parallel / pipeline isolation -----------------------------------------


def test_parallel_yields_none_for_failures(tmp_path: Path) -> None:
    body = """
from workflow_engine import agent, parallel

async def run(args, ctx):
    return await parallel([
        agent("one @@EMIT:1@@", label="1"),
        agent("two @@FAIL@@", label="2"),
        agent("three @@EMIT:3@@", label="3"),
    ])
"""
    run = make_run(tmp_path)
    assert asyncio.run(run.execute(write_workflow(tmp_path, body), {})) == ["1", None, "3"]
    assert run.counts["ok"] == 2 and run.counts["error"] == 1


def test_parallel_accepts_thunks_and_empty_batches(tmp_path: Path) -> None:
    body = """
from workflow_engine import agent, parallel

async def run(args, ctx):
    empty = await parallel([])
    thunked = await parallel([lambda: agent("t @@EMIT:T@@", label="t")])
    return [empty, thunked]
"""
    run = make_run(tmp_path)
    assert asyncio.run(run.execute(write_workflow(tmp_path, body), {})) == [[], ["T"]]


def test_pipeline_isolates_per_item_failures(tmp_path: Path) -> None:
    body = """
from workflow_engine import agent, pipeline

async def stage1(item):
    return await agent(item + " s1", label="s1-" + item[:4])

async def stage2(text):
    return await agent(text + " s2 @@EMIT:done-" + text + "@@", label="s2-" + text[:4])

async def run(args, ctx):
    return await pipeline(["ok1 @@EMIT:ok1@@", "bad @@FAIL@@", "ok2 @@EMIT:ok2@@"], stage1, stage2)
"""
    run = make_run(tmp_path)
    result = asyncio.run(run.execute(write_workflow(tmp_path, body), {}))

    assert result == ["done-ok1", None, "done-ok2"]
    # the failed item never reached stage 2, siblings completed both stages
    labels = {r["label"] for r in rows(run.run_dir, "call_end")}
    assert not any(label.startswith("s2-bad") for label in labels)
    assert run.counts["error"] == 1 and run.counts["ok"] == 4


def test_pipeline_drops_item_when_stage_returns_none(tmp_path: Path) -> None:
    body = """
from workflow_engine import agent, pipeline

async def gate(item):
    return None if item == "drop" else item

async def finish(item):
    return await agent(item + " @@EMIT:" + item + "@@", label="f-" + item)

async def run(args, ctx):
    return await pipeline(["keep", "drop"], gate, finish)
"""
    run = make_run(tmp_path)
    assert asyncio.run(run.execute(write_workflow(tmp_path, body), {})) == ["keep", None]
    assert run.counts["total"] == 1


# --- concurrency, timeout, routing -----------------------------------------


def test_concurrency_cap_is_respected(tmp_path: Path) -> None:
    body = """
from workflow_engine import agent, parallel

async def run(args, ctx):
    return await parallel([agent("job %d" % i, label="j%d" % i) for i in range(8)])
"""
    traces = tmp_path / "traces.jsonl"
    run = make_run(tmp_path, routes=routes(mode="trace", extra=[str(traces)]), concurrency=3)
    asyncio.run(run.execute(write_workflow(tmp_path, body), {}))

    events = [json.loads(line) for line in traces.read_text(encoding="utf-8").splitlines()]
    events.sort(key=lambda e: e["t"])
    live = peak = 0
    for event in events:
        live += 1 if event["event"] == "start" else -1
        peak = max(peak, live)
    assert len(events) == 16
    assert peak <= 3
    assert peak > 1  # the cap is a ceiling, not a serializer


def test_timeout_kills_the_child_and_journals_failure(tmp_path: Path) -> None:
    marker = tmp_path / "survived.txt"
    body = f"""
from workflow_engine import agent

async def run(args, ctx):
    return await agent("slow @@SLEEP:5@@ @@MARK:{marker}@@", label="slow", timeout_s=0.4)
"""
    run = make_run(tmp_path)
    started = time.monotonic()
    with pytest.raises(AgentError) as excinfo:
        asyncio.run(run.execute(write_workflow(tmp_path, body), {}))
    elapsed = time.monotonic() - started

    assert excinfo.value.kind == "timeout"
    assert elapsed < 4  # we did not wait out the child's sleep
    end = rows(run.run_dir, "call_end")[0]
    assert end["status"] == "error" and end["error"]["kind"] == "timeout"

    time.sleep(1.0)
    assert not marker.exists()  # the child was killed, not merely abandoned


def test_cancellation_kills_the_child_not_just_abandons_it(tmp_path: Path) -> None:
    """A workflow exception must cancel in-flight agent() calls' child processes, not orphan them."""
    marker = tmp_path / "survived.txt"
    body = f"""
import asyncio
from workflow_engine import agent

async def run(args, ctx):
    task = asyncio.create_task(agent("slow @@SLEEP:2@@ @@MARK:{marker}@@", label="slow", timeout_s=10))
    await asyncio.sleep(0.2)
    raise RuntimeError("kaboom")
"""
    run = make_run(tmp_path)
    with pytest.raises(RuntimeError):
        asyncio.run(run.execute(write_workflow(tmp_path, body), {}))

    time.sleep(2.0)  # long enough for the child's sleep to finish if it wasn't killed
    assert not marker.exists()  # the child was killed, not merely abandoned


def test_workers_run_in_the_campaign_dir(tmp_path: Path) -> None:
    """Workers are told to read campaign files (e.g. source-ledger.jsonl) by bare name."""
    body = """
from workflow_engine import agent

async def run(args, ctx):
    return await agent("where am i @@CWD@@", label="cwd")
"""
    run = make_run(tmp_path)
    result = asyncio.run(run.execute(write_workflow(tmp_path, body), {}))
    assert Path(result).resolve() == run.campaign_dir.resolve()


def test_unknown_route_fails_the_call_not_the_engine(tmp_path: Path) -> None:
    body = """
from workflow_engine import agent, parallel

async def run(args, ctx):
    return await parallel([
        agent("fine @@EMIT:fine@@", label="fine"),
        agent("nope", route="missing", label="nope"),
    ])
"""
    run = make_run(tmp_path)
    assert asyncio.run(run.execute(write_workflow(tmp_path, body), {})) == ["fine", None]
    assert run.counts["error"] == 1


def test_identical_calls_are_memoized_within_a_run(tmp_path: Path, counter: Path) -> None:
    body = """
from workflow_engine import agent, parallel

async def run(args, ctx):
    return await parallel([agent("same @@EMIT:S@@", label="dup") for _ in range(3)])
"""
    run = make_run(tmp_path)
    assert asyncio.run(run.execute(write_workflow(tmp_path, body), {})) == ["S", "S", "S"]
    assert spawns(counter) == 1


def test_status_json_tracks_state(tmp_path: Path) -> None:
    run = make_run(tmp_path)
    asyncio.run(run.execute(write_workflow(tmp_path, TWO_CALLS), {}))
    status = json.loads((run.run_dir / "status.json").read_text(encoding="utf-8"))

    assert status["state"] == "completed"
    assert status["counts"]["ok"] == 2 and status["counts"]["total"] == 2
    assert {c["label"] for c in status["calls"]} == {"a", "b"}
    assert all(c["harness"] == "fake" and c["duration_ms"] is not None for c in status["calls"])


def test_api_outside_a_run_raises(tmp_path: Path) -> None:
    from workflow_engine import agent

    with pytest.raises(RuntimeError):
        asyncio.run(agent("hi"))


def test_journal_is_engine_owned_and_append_only(tmp_path: Path) -> None:
    run = make_run(tmp_path)
    asyncio.run(run.execute(write_workflow(tmp_path, TWO_CALLS), {}))
    before = read_journal(run.run_dir)

    resumed = make_run(tmp_path, resume=True)
    asyncio.run(resumed.execute(write_workflow(tmp_path, TWO_CALLS), {}))
    after = read_journal(resumed.run_dir)

    assert after[: len(before)] == before  # earlier rows untouched
    assert [r["event"] for r in after[len(before) :]] == ["run_start", "phase", "log", "run_end"]
