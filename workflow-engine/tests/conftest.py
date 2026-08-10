"""Shared fixtures. Every test uses the `fake` harness adapter; nothing spawns a real CLI."""

from __future__ import annotations

import json
import stat
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
FAKE_WORKER = TESTS_DIR / "fake_worker.py"
DEEP_RESEARCH = Path("/Users/thinh/dotagents/skills/agentic-workflow-graphs/deep-research")

if str(DEEP_RESEARCH) not in sys.path:
    sys.path.insert(0, str(DEEP_RESEARCH))


@pytest.fixture(autouse=True)
def fake_cmd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the fake adapter at fake_worker.py, executed by this interpreter."""
    shim = tmp_path / "fake-worker"
    shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{FAKE_WORKER}" "$@"\n', encoding="utf-8")
    shim.chmod(shim.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    monkeypatch.setenv("WFE_FAKE_CMD", str(shim))
    monkeypatch.chdir(tmp_path)
    return shim


@pytest.fixture
def counter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Counts every fake-worker invocation, i.e. every live child process."""
    path = tmp_path / "invocations.txt"
    monkeypatch.setenv("WFE_FAKE_COUNTER", str(path))
    return path


def spawns(counter: Path) -> int:
    return len(counter.read_text(encoding="utf-8").splitlines()) if counter.exists() else 0


def write_workflow(tmp_path: Path, body: str, name: str = "wf.py") -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def read_journal(run_dir: Path) -> list[dict]:
    text = (run_dir / "journal.jsonl").read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def rows(run_dir: Path, event: str) -> list[dict]:
    return [r for r in read_journal(run_dir) if r.get("event") == event]


def routes(*, mode: str = "echo", extra: list[str] | None = None) -> dict:
    from workflow_engine.harness import Route

    flags = [mode, *(extra or [])]
    return {name: Route(harness="fake", extra_flags=list(flags)) for name in ("default", "strong", "throughput")}


def make_run(tmp_path: Path, **kwargs):
    from workflow_engine.engine import Run

    campaign = kwargs.pop("campaign_dir", tmp_path / "campaign")
    run_id = kwargs.pop("run_id", "run-1")
    campaign.mkdir(parents=True, exist_ok=True)
    kwargs.setdefault("routes", routes())
    return Run(run_dir=campaign / "runs" / run_id, campaign_dir=campaign, **kwargs)
