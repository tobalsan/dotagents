"""CLI surface: --arg parsing, run/status/list wiring, exit codes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import rows, spawns, write_workflow
from workflow_engine.cli import build_parser, main

ARGS_WF = """
from workflow_engine import agent

async def run(args, ctx):
    return await agent("echo @@EMIT:" + args["topic"] + "/" + args.get("depth", "?") + "@@", label="e")
"""

FAIL_WF = """
from workflow_engine import agent, parallel

async def run(args, ctx):
    return await parallel([agent("nope @@FAIL@@", label="n")])
"""


def campaign_with_routes(tmp_path: Path, mode: str = "echo") -> Path:
    campaign = tmp_path / "campaign"
    campaign.mkdir(parents=True, exist_ok=True)
    (campaign / "routes.json").write_text(
        json.dumps({name: {"harness": "fake", "extra_flags": [mode]} for name in ("default", "strong", "throughput")}),
        encoding="utf-8",
    )
    return campaign


# --- --arg parsing ---------------------------------------------------------


def test_arg_parses_repeated_key_values() -> None:
    ns = build_parser().parse_args(
        ["run", "wf.py", "--campaign", "c", "--arg", "topic=ai", "--arg", "q=a=b", "--arg", "empty="]
    )
    assert dict(ns.arg) == {"topic": "ai", "q": "a=b", "empty": ""}


def test_arg_without_equals_is_a_usage_error() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["run", "wf.py", "--campaign", "c", "--arg", "topic"])


def test_run_defaults() -> None:
    ns = build_parser().parse_args(["run", "wf.py", "--campaign", "c"])
    assert (ns.concurrency, ns.timeout, ns.arg, ns.resume, ns.routing) == (6, 900.0, [], None, None)


# --- run -------------------------------------------------------------------


def test_run_passes_args_to_the_workflow(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    campaign = campaign_with_routes(tmp_path)
    wf = write_workflow(tmp_path, ARGS_WF)
    code = main(["run", str(wf), "--campaign", str(campaign), "--arg", "topic=ai", "--arg", "depth=2"])

    assert code == 0
    run_dir = next((campaign / "runs").iterdir())
    assert rows(run_dir, "call_end")[0]["result"] == "ai/2"
    assert json.loads((run_dir / "status.json").read_text())["state"] == "completed"


def test_run_resume_reuses_the_run_dir(tmp_path: Path, counter: Path) -> None:
    campaign = campaign_with_routes(tmp_path)
    wf = write_workflow(tmp_path, ARGS_WF)
    assert main(["run", str(wf), "--campaign", str(campaign), "--arg", "topic=ai"]) == 0
    run_id = next((campaign / "runs").iterdir()).name

    assert main(["run", str(wf), "--campaign", str(campaign), "--arg", "topic=ai", "--resume", run_id]) == 0
    assert [p.name for p in (campaign / "runs").iterdir()] == [run_id]
    assert spawns(counter) == 1  # nothing re-ran


def test_run_exit_code_1_when_a_call_failed(tmp_path: Path) -> None:
    campaign = campaign_with_routes(tmp_path)
    assert main(["run", str(write_workflow(tmp_path, FAIL_WF)), "--campaign", str(campaign)]) == 1


def test_run_usage_errors(tmp_path: Path) -> None:
    campaign = campaign_with_routes(tmp_path)
    wf = write_workflow(tmp_path, ARGS_WF)
    assert main(["run", str(tmp_path / "missing.py"), "--campaign", str(campaign)]) == 2
    assert main(["run", str(wf), "--campaign", str(campaign), "--routing", str(tmp_path / "no.json")]) == 2

    bad = write_workflow(tmp_path, "value = 1\n", name="bad_wf.py")
    assert main(["run", str(bad), "--campaign", str(campaign)]) == 2


# --- status / list ---------------------------------------------------------


def test_status_and_list(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    campaign = campaign_with_routes(tmp_path)
    wf = write_workflow(tmp_path, ARGS_WF)
    main(["run", str(wf), "--campaign", str(campaign), "--arg", "topic=ai"])
    run_dir = next((campaign / "runs").iterdir())
    capsys.readouterr()

    assert main(["status", str(run_dir)]) == 0
    human = capsys.readouterr().out
    assert "completed" in human and "ok=1" in human

    assert main(["status", str(run_dir), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["run_id"] == run_dir.name

    assert main(["status", str(tmp_path / "nowhere")]) == 2
    capsys.readouterr()

    assert main(["list", "--campaign", str(campaign)]) == 0
    assert run_dir.name in capsys.readouterr().out
