"""Ralph-loop skill: contracts.py domain logic and workflow.py end-to-end on the fake adapter.

`ralph-loop` and `deep-research` each ship a same-named `contracts.py`/`workflow.py`; both
are loaded here by file path under distinct sys.modules names (`ralph_contracts`,
`ralph_workflow`) rather than `import contracts`/`import workflow`, so this file cannot
silently bind to whichever module test_deep_research.py already cached under those bare
names.
"""

from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path

import pytest
from conftest import RALPH_LOOP, make_run, routes, rows

from workflow_engine.engine import AgentError, load_workflow
from workflow_engine.harness import Route

WORKFLOW = RALPH_LOOP / "workflow.py"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, RALPH_LOOP / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ralph_contracts = _load("ralph_contracts", "contracts.py")
ralph_workflow = _load("ralph_workflow", "workflow.py")


def _write_task(ralph_dir: Path, name: str, verification: str, extra: str = "") -> Path:
    ralph_dir.mkdir(parents=True, exist_ok=True)
    path = ralph_dir / f"{name}.md"
    path.write_text(
        f"# Task\n\n## Goal\nDo the thing. {extra}\n\n## Verification\ncommand: {verification}\n",
        encoding="utf-8",
    )
    return path


# --- contracts ---------------------------------------------------------------------------


def test_child_directive_precedence() -> None:
    both = f"done. {ralph_contracts.PAUSE_MARKER} {ralph_contracts.COMPLETE_MARKER}"
    assert ralph_contracts.child_directive(both) == "pause"
    assert ralph_contracts.child_directive(f"done. {ralph_contracts.COMPLETE_MARKER}") == "complete"
    assert ralph_contracts.child_directive("still working") == "continue"


def test_parse_verification_command_fenced_block() -> None:
    content = "# Task\n\n## Verification\n\n```bash\nmake test\n```\n"
    assert ralph_contracts.parse_verification_command(content) == "make test"


def test_parse_verification_command_section_line_stops_at_next_heading() -> None:
    content = "# Task\n\n## Verification\ncommand: npm test\n\n## Commit\nDo not commit.\n"
    assert ralph_contracts.parse_verification_command(content) == "npm test"


def test_parse_verification_command_top_level_fallback() -> None:
    content = "# Task\n\nverify: pytest -q\n"
    assert ralph_contracts.parse_verification_command(content) == "pytest -q"


# --- workflow.py end to end ---------------------------------------------------------------


def test_workflow_imports_cleanly() -> None:
    assert asyncio.iscoroutinefunction(load_workflow(WORKFLOW))
    assert asyncio.iscoroutinefunction(ralph_workflow.run)


def test_missing_task_file_raises(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    workdir = tmp_path / "work"
    workdir.mkdir()
    run = make_run(tmp_path, campaign_dir=campaign, workdir=workdir, routes=routes(mode="ralph-complete", names=("worker",)))
    with pytest.raises(AgentError, match="task file not found"):
        asyncio.run(run.execute(WORKFLOW, {"name": "ghost"}))


def test_completes_when_complete_marker_and_verification_passes(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    workdir = tmp_path / "work"
    workdir.mkdir()
    _write_task(campaign, "loop1", verification="true")
    run = make_run(tmp_path, campaign_dir=campaign, workdir=workdir, routes=routes(mode="ralph-complete", names=("worker",)))

    result = asyncio.run(run.execute(WORKFLOW, {"name": "loop1"}))

    assert result == {"name": "loop1", "status": "completed", "iterations": 1, "verification_passed": True}
    state = ralph_contracts.load_state(campaign / "loop1.state.json")
    assert state["status"] == "completed" and "completedAt" in state


def test_completes_after_verification_failure_records_reflection_and_retries(tmp_path: Path) -> None:
    """COMPLETE with a failing verification must not pause: it continues into a fresh
    iteration with the failure recorded in the reflection file, and can complete later."""
    campaign = tmp_path / "campaign"
    workdir = tmp_path / "work"
    workdir.mkdir()
    _write_task(campaign, "loop1", verification="test -f .verified || { touch .verified; exit 1; }")
    run = make_run(tmp_path, campaign_dir=campaign, workdir=workdir, routes=routes(mode="ralph-complete", names=("worker",)))

    result = asyncio.run(run.execute(WORKFLOW, {"name": "loop1", "max_iterations": "5"}))

    assert result == {"name": "loop1", "status": "completed", "iterations": 2, "verification_passed": True}
    reflection = (campaign / "loop1.reflection.md").read_text(encoding="utf-8")
    assert "Verification failed" in reflection
    assert "Verification passed" in reflection
    assert sorted(r["label"] for r in rows(run.run_dir, "call_end")) == ["iter-1", "iter-2"]


def test_continues_without_marker_then_completes(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    workdir = tmp_path / "work"
    workdir.mkdir()
    _write_task(campaign, "loop1", verification="true")
    counter = tmp_path / "child-calls.txt"
    route = {"worker": Route(harness="fake", extra_flags=["ralph-continue-then-complete", str(counter)])}
    run = make_run(tmp_path, campaign_dir=campaign, workdir=workdir, routes=route)

    result = asyncio.run(run.execute(WORKFLOW, {"name": "loop1", "max_iterations": "5"}))

    assert result == {"name": "loop1", "status": "completed", "iterations": 2, "verification_passed": True}


def test_pause_marker_pauses_with_last_error(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    workdir = tmp_path / "work"
    workdir.mkdir()
    _write_task(campaign, "loop1", verification="true")
    run = make_run(tmp_path, campaign_dir=campaign, workdir=workdir, routes=routes(mode="ralph-pause", names=("worker",)))

    result = asyncio.run(run.execute(WORKFLOW, {"name": "loop1"}))

    assert result["status"] == "paused" and result["iterations"] == 1
    state = ralph_contracts.load_state(campaign / "loop1.state.json")
    assert "pause" in state["lastError"].lower()


def test_max_iterations_reached_pauses(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    workdir = tmp_path / "work"
    workdir.mkdir()
    # @@EMIT@@ keeps the fake worker's echoed reply free of the literal markers that
    # build_prompt's own instructions text contains -- otherwise "echo" would parrot them
    # back and every iteration would look like a false completion/pause.
    _write_task(campaign, "loop1", verification="true", extra="@@EMIT:still working@@")
    run = make_run(tmp_path, campaign_dir=campaign, workdir=workdir, routes=routes(mode="echo", names=("worker",)))

    result = asyncio.run(run.execute(WORKFLOW, {"name": "loop1", "max_iterations": "2"}))

    assert result["status"] == "paused"
    state = ralph_contracts.load_state(campaign / "loop1.state.json")
    assert "Max iterations reached" in state["lastError"]
    assert state["iteration"] == 3


def test_rerun_on_paused_state_resumes_at_stored_iteration(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    workdir = tmp_path / "work"
    workdir.mkdir()
    _write_task(campaign, "loop1", verification="true")
    counter = tmp_path / "child-calls.txt"
    first_routes = {"worker": Route(harness="fake", extra_flags=["ralph-continue-then-pause", str(counter)])}
    first = make_run(tmp_path, campaign_dir=campaign, workdir=workdir, routes=first_routes, run_id="run-1")

    first_result = asyncio.run(first.execute(WORKFLOW, {"name": "loop1", "max_iterations": "5"}))
    assert first_result["status"] == "paused" and first_result["iterations"] == 2

    second = make_run(
        tmp_path, campaign_dir=campaign, workdir=workdir, routes=routes(mode="ralph-complete", names=("worker",)), run_id="run-2"
    )
    second_result = asyncio.run(second.execute(WORKFLOW, {"name": "loop1", "max_iterations": "5"}))

    assert second_result == {"name": "loop1", "status": "completed", "iterations": 2, "verification_passed": True}
    # Resumed straight at the stored iteration -- iteration 1 never re-ran.
    assert sorted(r["label"] for r in rows(second.run_dir, "call_end")) == ["iter-2"]
