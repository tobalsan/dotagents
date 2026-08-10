"""Deep-research skill: contracts.py domain logic and workflow.py end-to-end on the fake adapter."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

import contracts
import workflow
from conftest import DEEP_RESEARCH, make_run, routes, rows, spawns

WORKFLOW = DEEP_RESEARCH / "workflow.py"


# --- contracts: URL normalization -----------------------------------------


def test_normalize_strips_tracking_and_sorts_query() -> None:
    a = contracts.normalize("https://Example.COM/a//b?z=1&utm_source=x&fbclid=y&a=2")
    assert a["normalized_url"] == "https://example.com/a/b?a=2&z=1"
    assert a["content_id"] is None and a["canonical_id"].startswith("sha256:")
    assert contracts.normalize("https://example.com/a/b?a=2&z=1")["canonical_id"] == a["canonical_id"]


def test_normalize_default_ports_and_case() -> None:
    assert contracts.normalize("HTTPS://Example.com:443/x")["normalized_url"] == "https://example.com/x"
    assert contracts.normalize("http://example.com:8080/x")["normalized_url"] == "http://example.com:8080/x"


@pytest.mark.parametrize(
    ("url", "content_id"),
    [
        ("https://youtu.be/dQw4w9WgXcQ", "youtube:dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42", "youtube:dQw4w9WgXcQ"),
        ("https://arxiv.org/pdf/2401.00001v3.pdf", "arxiv:2401.00001"),
        ("https://arxiv.org/abs/2401.00001", "arxiv:2401.00001"),
        ("https://dx.doi.org/10.1000/XYZ123", "doi:10.1000/xyz123"),
    ],
)
def test_normalize_extracts_provider_content_ids(url: str, content_id: str) -> None:
    identity = contracts.normalize(url)
    assert identity["content_id"] == content_id
    assert identity["canonical_id"] == content_id


def test_normalize_collapses_aliases_of_the_same_content() -> None:
    ids = {
        contracts.normalize(u)["canonical_id"]
        for u in (
            "https://youtu.be/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&utm_source=nl",
        )
    }
    assert ids == {"youtube:dQw4w9WgXcQ"}
    reddit = {
        contracts.normalize(u)["canonical_id"]
        for u in ("https://old.reddit.com/r/x/comments/AB12/title/", "https://www.reddit.com/r/y/comments/ab12/other/")
    }
    assert len(reddit) == 1


def test_normalize_rejects_non_http_urls() -> None:
    for bad in ("ftp://example.com/x", "not a url", "mailto:a@b.c"):
        with pytest.raises(ValueError):
            contracts.normalize(bad)


# --- contracts: ledger fold + saturation -----------------------------------


def test_fold_ledger_last_row_wins(tmp_path: Path) -> None:
    ledger = tmp_path / "source-ledger.jsonl"
    assert contracts.fold_ledger(ledger) == {}

    contracts.append_ledger(ledger, {"canonical_id": "doi:10.1/a", "status": "seen"})
    contracts.append_ledger(ledger, {"canonical_id": "doi:10.1/b", "status": "seen"})
    contracts.append_ledger(ledger, {"canonical_id": "doi:10.1/a", "status": "extracted"})

    folded = contracts.fold_ledger(ledger)
    assert folded["doi:10.1/a"]["status"] == "extracted"
    assert contracts.known_canonical_ids(ledger) == {"doi:10.1/a", "doi:10.1/b"}
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 3  # append-only, nothing rewritten


def test_saturation_needs_a_streak_of_quiet_passes() -> None:
    assert contracts.pass_is_quiet({"gaps": [], "new_branches": [], "new_sources": []})
    # a lingering gap (skeptic rejection, thin lane) alone must not block saturation forever --
    # only fresh sources or fresh coverage do. Otherwise saturation is unreachable: a real
    # campaign practically always has *some* rejection or thin lane every pass.
    assert contracts.pass_is_quiet({"gaps": ["single secondary source"], "new_branches": [], "new_sources": []})
    assert not contracts.pass_is_quiet({"gaps": [], "new_branches": ["lane-c"], "new_sources": []})
    assert not contracts.pass_is_quiet({"gaps": [], "new_branches": [], "new_sources": ["sha256:a"]})

    assert not contracts.is_saturated([True], 2)
    assert not contracts.is_saturated([True, False], 2)
    assert contracts.is_saturated([False, True, True], 2)


# --- workflow.py end to end -------------------------------------------------


def test_workflow_imports_cleanly() -> None:
    from workflow_engine.engine import load_workflow

    assert asyncio.iscoroutinefunction(load_workflow(WORKFLOW))


def test_workflow_runs_a_two_lane_pass(tmp_path: Path, counter: Path) -> None:
    campaign = tmp_path / "campaign"
    run = make_run(tmp_path, campaign_dir=campaign, routes=routes(mode="research"))
    result = asyncio.run(run.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "1"}))

    assert result == {"passes_run": 1, "saturated": False, "coverage_branches": 4}
    assert run.counts["error"] == 0
    # scope + plan + 2 research + 2 extract + skeptic
    assert sorted(r["label"] for r in rows(run.run_dir, "call_end")) == [
        "extract-lane-a-pass1",
        "extract-lane-b-pass1",
        "plan-pass1",
        "research-lane-a-pass1",
        "research-lane-b-pass1",
        "scope",
        "skeptic-pass1",
    ]

    ledger = contracts.fold_ledger(campaign / "source-ledger.jsonl")
    assert "arxiv:2401.00001" in ledger  # provider identity survived the merge
    assert any(cid.startswith("sha256:") for cid in ledger)
    assert all(row["pass_id"] == "pass-1" for row in ledger.values())

    notes = [json.loads(line) for line in (campaign / "notes.jsonl").read_text().splitlines()]
    assert [n["lane_id"] for n in notes] == ["lane-a"]  # lane-b's only claim was rejected

    gaps = json.loads((campaign / "passes" / "pass-1" / "gap-report.json").read_text())
    assert gaps["new_branches"] == ["lane-a", "lane-b"]
    assert gaps["rejections"][0]["claim_ref"] == "lane-b:0"

    coverage = json.loads((campaign / "coverage-map.json").read_text())
    assert [b["id"] for b in coverage["branches"]] == ["branch-x", "branch-y", "lane-a", "lane-b"]


def test_workflow_second_pass_reads_prior_state(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    run = make_run(tmp_path, campaign_dir=campaign, routes=routes(mode="research"))
    result = asyncio.run(run.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "2"}))

    assert result["passes_run"] == 2
    assert result["coverage_branches"] == 4  # same scope/lane ids, no duplicate branches
    labels = {r["label"] for r in rows(run.run_dir, "call_end")}
    assert "plan-pass2" in labels and "skeptic-pass2" in labels
    assert json.loads((campaign / "passes" / "pass-2" / "gap-report.json").read_text())["new_branches"] == []


def test_merge_skips_a_malformed_source_url_instead_of_crashing(tmp_path: Path) -> None:
    """One bad URL from a worker must not sink the whole pass's merge."""
    campaign = tmp_path / "campaign"
    campaign.mkdir()
    lane_results = [
        {
            "lane": {"id": "lane-a", "focus": "x"},
            "claims": [{"claim": "c", "evidence": "e", "strength": "likely", "citation": "https://example.com/a"}],
            "sources": [
                {"url": "internal notes, no URL", "status": "seen"},
                {"url": "https://example.com/a", "status": "extracted"},
            ],
        }
    ]
    gap_report = workflow._merge(
        campaign, campaign / "source-ledger.jsonl", campaign / "notes.jsonl",
        {"branches": []}, lane_results, {"rejections": [], "summary": "ok"}, 1,
    )
    ledger = contracts.fold_ledger(campaign / "source-ledger.jsonl")
    assert len(ledger) == 1  # the malformed source was skipped, not fatal
    assert gap_report["new_sources"] == list(ledger)


def test_workflow_skeptic_failure_does_not_discard_completed_lanes(tmp_path: Path) -> None:
    """A skeptic that exhausts its schema retries must not discard the lanes' completed work."""
    from workflow_engine.harness import Route

    campaign = tmp_path / "campaign"
    mixed = {
        "strong": Route(harness="fake", extra_flags=["research", "badskeptic"]),
        "throughput": Route(harness="fake", extra_flags=["research"]),
        "default": Route(harness="fake", extra_flags=["research"]),
    }
    run = make_run(tmp_path, campaign_dir=campaign, routes=mixed)
    result = asyncio.run(run.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "1"}))

    assert result["passes_run"] == 1
    assert run.counts["error"] == 1  # the skeptic call itself failed
    notes = [json.loads(line) for line in (campaign / "notes.jsonl").read_text().splitlines()]
    assert {n["lane_id"] for n in notes} == {"lane-a", "lane-b"}  # nothing rejected: skeptic never ran
    assert len(contracts.fold_ledger(campaign / "source-ledger.jsonl")) > 0


def test_workflow_saturates_once_no_new_sources_or_branches(tmp_path: Path) -> None:
    """With a deterministic worker the field goes dry by pass 3; the run must stop early."""
    campaign = tmp_path / "campaign"
    run = make_run(tmp_path, campaign_dir=campaign, routes=routes(mode="research"))
    result = asyncio.run(run.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "4"}))
    assert result == {"passes_run": 3, "saturated": True, "coverage_branches": 4}


def test_workflow_resume_of_a_completed_run_makes_zero_live_calls(tmp_path: Path, counter: Path) -> None:
    """Resuming a completed run must replay, not rebuild prompts from campaign state _merge
    already mutated -- that mismatch used to re-spawn the plan and cascade downstream."""
    campaign = tmp_path / "campaign"
    first = make_run(tmp_path, campaign_dir=campaign, routes=routes(mode="research"), run_id="run-1")
    first_result = asyncio.run(first.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "1"}))
    spawns_after_first = spawns(counter)
    assert spawns_after_first > 0
    ledger_before = (campaign / "source-ledger.jsonl").read_text()
    notes_before = (campaign / "notes.jsonl").read_text()

    second = make_run(tmp_path, campaign_dir=campaign, routes=routes(mode="research"), run_id="run-1", resume=True)
    second_result = asyncio.run(second.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "1"}))

    assert second_result == first_result
    assert spawns(counter) == spawns_after_first  # zero live calls on resume
    assert (campaign / "source-ledger.jsonl").read_text() == ledger_before  # not re-appended
    assert (campaign / "notes.jsonl").read_text() == notes_before


def test_workflow_scope_seeds_coverage_map_when_empty(tmp_path: Path) -> None:
    """An empty campaign gets one scope sweep before pass 1, seeding the map's taxonomy."""
    campaign = tmp_path / "campaign"
    run = make_run(tmp_path, campaign_dir=campaign, routes=routes(mode="research"))
    asyncio.run(run.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "1"}))

    scope_calls = [r for r in rows(run.run_dir, "call_end") if r["label"] == "scope"]
    assert len(scope_calls) == 1
    coverage = json.loads((campaign / "coverage-map.json").read_text())
    seeded = {"id": "branch-x", "focus": "branch-x", "status": "thin"}
    assert seeded in coverage["branches"]


def test_workflow_resume_does_not_rerun_scope_or_duplicate_branches(tmp_path: Path, counter: Path) -> None:
    """A resumed, already-seeded campaign must skip scope outright, not just replay it -- and
    the seed must never duplicate branches on re-entry."""
    campaign = tmp_path / "campaign"
    first = make_run(tmp_path, campaign_dir=campaign, routes=routes(mode="research"), run_id="run-1")
    asyncio.run(first.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "1"}))

    second = make_run(tmp_path, campaign_dir=campaign, routes=routes(mode="research"), run_id="run-1", resume=True)
    asyncio.run(second.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "1"}))

    scope_starts = [r for r in rows(second.run_dir, "call_start") if r["label"] == "scope"]
    assert len(scope_starts) == 1  # only the first run's attempt -- resume never re-entered scope
    coverage = json.loads((campaign / "coverage-map.json").read_text())
    ids = [b["id"] for b in coverage["branches"]]
    assert ids.count("branch-x") == 1 and ids.count("branch-y") == 1


def test_workflow_second_run_continues_without_clobbering_prior_passes(tmp_path: Path, counter: Path) -> None:
    """A fresh `wfe run` against the same campaign dir must continue, not restart pass numbering."""
    campaign = tmp_path / "campaign"
    first = make_run(tmp_path, campaign_dir=campaign, routes=routes(mode="research"), run_id="run-1")
    asyncio.run(first.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "1"}))
    pass1_report = (campaign / "passes" / "pass-1" / "gap-report.json").read_text()
    spawns_after_first = spawns(counter)

    second = make_run(tmp_path, campaign_dir=campaign, routes=routes(mode="research"), run_id="run-2")
    result = asyncio.run(second.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "2"}))

    assert (campaign / "passes" / "pass-1" / "gap-report.json").read_text() == pass1_report  # untouched
    assert (campaign / "passes" / "pass-2" / "gap-report.json").is_file()  # fresh, newly-numbered work
    assert spawns(counter) > spawns_after_first
    assert result["passes_run"] == 2


def test_all_lanes_dead_fails_the_pass(tmp_path: Path) -> None:
    """When every lane dies, the pass must fail loudly, not merge an empty gap report."""
    from workflow_engine.engine import AgentError
    from workflow_engine.harness import Route

    campaign = tmp_path / "campaign"
    mixed = {
        "strong": Route(harness="fake", extra_flags=["research"]),
        "throughput": Route(harness="fake", extra_flags=["echo"]),  # cannot satisfy EXTRACT_SCHEMA
        "default": Route(harness="fake", extra_flags=["research"]),
    }
    run = make_run(tmp_path, campaign_dir=campaign, routes=mixed)
    with pytest.raises(AgentError, match="all research lanes failed"):
        asyncio.run(run.execute(WORKFLOW, {"topic": "ai safety", "max_passes": "1"}))

    assert not (campaign / "notes.jsonl").exists()
    assert not (campaign / "passes" / "pass-1" / "gap-report.json").exists()
