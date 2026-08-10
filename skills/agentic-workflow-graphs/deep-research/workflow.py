"""Deep-research graph as a wfe workflow script.

    scope (throughput, schema-forced; once, only when coverage-map.json is empty/absent)
      -> plan (strong, lanes as diffs against the coverage map)
      -> pipeline(lanes: research (throughput, reads ledger) -> extract (throughput, schema-forced))
      -> skeptic barrier over all lanes (strong, schema-forced)
      -> merge (plain code: contracts.py writes ledger/notes/coverage-map/gap-report)
    looped until saturation or --arg max_passes.

Run with:
    uv run --project /Users/thinh/dotagents/workflow-engine wfe run workflow.py \
        --campaign CAMPAIGN_DIR --routing routes.json --arg topic="..."
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import contracts
from workflow_engine import AgentError, Ctx, agent, phase, pipeline

RETRIEVAL_SKILLS = """\
| Source | Skill |
| --- | --- |
| Web search | `research/exa` first, `research/firecrawl` for broader sweeps |
| A page to read | harness fetch tool -> `curl https://markdown.new/<url>` -> `research/firecrawl` -> `research/crawl4ai` for JS-heavy pages |
| A site to crawl, or structured extraction | `research/firecrawl`, `research/crawl4ai` |
| YouTube video, playlist, channel | `research/youtube` |
| Reddit thread or subreddit | `research/reddit` |
| arXiv paper, primary literature | `research/arxiv` |
| Finding a book | `research/find-ebooks` |
| A long PDF, book, or EPUB in hand | `research/read-long-documents` (index it, pull only needed ranges) |
"""

PLAN_SCHEMA = {
    "type": "object",
    "required": ["lanes"],
    "properties": {
        "lanes": {
            "type": "array",
            "minItems": 1,
            "maxItems": 5,
            "items": {
                "type": "object",
                "required": ["id", "focus", "queries"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "focus": {"type": "string", "minLength": 1},
                    "queries": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                },
            },
        },
    },
}

EXTRACT_SCHEMA = {
    "type": "object",
    "required": ["claims", "sources"],
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["claim", "evidence", "strength", "citation"],
                "properties": {
                    "claim": {"type": "string"},
                    "evidence": {"type": "string"},
                    "strength": {"enum": ["widely agreed", "likely", "disputed", "thin"]},
                    "citation": {"type": "string"},
                },
            },
        },
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["url", "status"],
                "properties": {
                    "url": {"type": "string", "pattern": "^https?://"},
                    "status": {"enum": sorted(contracts.STATUSES)},
                    "title": {"type": "string"},
                    "source_type": {"type": "string"},
                },
            },
        },
    },
}

SCOPE_SCHEMA = {
    "type": "object",
    "required": ["branches"],
    "properties": {
        "branches": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["name", "status"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "status": {"const": "thin"},
                },
            },
        },
    },
}

SKEPTIC_SCHEMA = {
    "type": "object",
    "required": ["rejections", "summary"],
    "properties": {
        "rejections": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["claim_ref", "reason"],
                "properties": {
                    "claim_ref": {"type": "string"},
                    "reason": {"type": "string"},
                },
            },
        },
        "summary": {"type": "string"},
    },
}


def _latest_gap_report(campaign_dir: Path) -> dict[str, Any]:
    passes_dir = campaign_dir / "passes"
    if not passes_dir.is_dir():
        return {}
    numbered = sorted(
        (p for p in passes_dir.glob("pass-*/gap-report.json")),
        key=lambda p: int(p.parent.name.removeprefix("pass-")),
    )
    if not numbered:
        return {}
    return json.loads(numbered[-1].read_text(encoding="utf-8"))


def _load_coverage_map(campaign_dir: Path) -> dict[str, Any]:
    path = campaign_dir / "coverage-map.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"branches": []}


def _build_scope_prompt(topic: str) -> str:
    """Pure function of topic alone -- must stay stable across resume, before any map exists."""
    return (
        f"You are scoping a deep-research campaign on: {topic}\n\n"
        "Sketch the field's own structure before any research happens: the branches, "
        "schools of thought, or sub-topics a subject-matter map of this topic would have "
        "on its own terms -- not a rephrasing of the topic string. Return 3-8 branch "
        "names; tag every one status \"thin\" (nothing researched yet).\n"
    )


def _build_plan_prompt(topic: str, coverage_map: dict[str, Any], gap_report: dict[str, Any], brief: str) -> str:
    brief_block = f"Campaign brief (the user's verbatim request -- honor its evidence standards):\n{brief}\n\n" if brief else ""
    return (
        f"You are planning one pass of a deep-research campaign on: {topic}\n\n"
        f"{brief_block}"
        "Read the coverage map and the latest gap report below. Generate 3-5 research "
        "lanes as DIFFS against the map: thin branches, contradictions, unexplored "
        "adjacencies. Never free-form from the original topic alone; that re-treads "
        "ground already covered. Prefer 5 lanes while the map is broad and shallow, 3 "
        "once gaps are narrow and specific.\n\n"
        f"Coverage map:\n{json.dumps(coverage_map, indent=2, sort_keys=True)}\n\n"
        f"Latest gap report:\n{json.dumps(gap_report, indent=2, sort_keys=True)}\n"
    )


def _build_research_prompt(lane: dict[str, Any], topic: str) -> str:
    return (
        f"You are researcher lane '{lane['id']}' on a deep-research campaign about: {topic}\n\n"
        f"Lane focus: {lane['focus']}\n"
        f"Seed queries: {json.dumps(lane['queries'])}\n\n"
        "Before fetching anything, read source-ledger.jsonl in the working directory "
        "(if present) and skip any URL whose canonical ID you already see recorded "
        "there — merge is the ledger's only writer, you only read it. 10 sources is "
        "the floor, 50 the ceiling; the real stop is dryness — stop once new sources "
        "stop changing your claims.\n\n"
        "Retrieve with the skill that matches the source type, not by improvising:\n\n"
        f"{RETRIEVAL_SKILLS}\n"
        "Report back the raw material you found (sources, quotes, context) as plain "
        "text; a later step turns it into structured claims."
    )


def _build_extract_prompt(lane: dict[str, Any], research_text: str) -> str:
    return (
        f"Turn the raw research below (lane '{lane['id']}', focus: {lane['focus']}) "
        "into claims with evidence and citations. Mark each claim's evidence strength: "
        "widely agreed / likely / disputed / thin. List every source you drew on, each "
        "with its status (seen/fetched/extracted/rejected).\n\n"
        f"Raw research:\n{research_text}\n"
    )


def _build_skeptic_prompt(lane_results: list[dict[str, Any]]) -> str:
    lanes_blob = []
    for result in lane_results:
        lane = result["lane"]
        claims = result.get("claims", [])
        lanes_blob.append(
            {
                "lane_id": lane["id"],
                "focus": lane["focus"],
                "claims": [
                    {"claim_ref": f"{lane['id']}:{i}", **claim} for i, claim in enumerate(claims)
                ],
            }
        )
    return (
        "You are the skeptic reviewing every lane of this research pass at once — "
        "that is deliberate: catch cross-lane contradictions and consensus illusions "
        "a per-lane critic can't. Challenge sourcing, not conclusions you dislike. "
        "Check for: prose counts vs structured arrays, primary vs secondary-source "
        "inflation, duplicate URLs/aliases, and whether each claim is supported by the "
        "exact cited passage rather than a merely topically related source.\n\n"
        "Reject any claim that fails this bar by its claim_ref, with a reason. "
        "Whatever you reject becomes a gap for the next pass' planner — there is no "
        "re-research bounce inside this pass.\n\n"
        f"Lanes:\n{json.dumps(lanes_blob, indent=2, sort_keys=True)}\n"
    )


def _merge(
    campaign_dir: Path,
    ledger_path: Path,
    notes_path: Path,
    coverage_map: dict[str, Any],
    lane_results: list[Any],
    skeptic: dict[str, Any],
    pass_num: int,
) -> dict[str, Any]:
    """Plain-code merge: sole ledger writer. Writes ledger/notes/coverage-map/gap-report."""
    rejected_refs = {r["claim_ref"] for r in skeptic.get("rejections", [])}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pass_id = f"pass-{pass_num}"
    known_before = contracts.known_canonical_ids(ledger_path)
    seen_this_pass: dict[str, dict[str, Any]] = {}
    thin_lanes: list[str] = []
    covered = {b["id"] for b in coverage_map.get("branches", [])}
    new_branches: list[str] = []

    for result in lane_results:
        if not result:
            continue
        lane = result["lane"]
        if lane["id"] not in covered:
            coverage_map.setdefault("branches", []).append(
                {"id": lane["id"], "focus": lane["focus"], "status": "covered"}
            )
            new_branches.append(lane["id"])

        for source in result.get("sources", []):
            try:
                identity = contracts.normalize(source["url"])
            except ValueError:
                continue  # malformed source url must not sink the whole pass
            canonical_id = identity["canonical_id"]
            row = {
                "canonical_id": canonical_id,
                "status": source.get("status", "seen"),
                "url": identity["normalized_url"],
                "observed_at": now,
                "lane_id": lane["id"],
                "pass_id": pass_id,
            }
            if identity["content_id"]:
                row["content_id"] = identity["content_id"]
            if source.get("title"):
                row["title"] = source["title"]
            if source.get("source_type"):
                row["source_type"] = source["source_type"]
            if canonical_id in seen_this_pass:
                row["collision"] = True
            seen_this_pass[canonical_id] = row
            contracts.append_ledger(ledger_path, row)

        kept_claims = [
            claim for i, claim in enumerate(result.get("claims", [])) if f"{lane['id']}:{i}" not in rejected_refs
        ]
        if kept_claims:
            with notes_path.open("a", encoding="utf-8") as fh:
                for claim in kept_claims:
                    fh.write(json.dumps({"pass": pass_id, "lane_id": lane["id"], **claim}, sort_keys=True) + "\n")
        else:
            thin_lanes.append(lane["id"])

    new_sources = sorted(seen_this_pass.keys() - known_before)
    gap_report = {
        "pass": pass_num,
        "gaps": thin_lanes + [r["reason"] for r in skeptic.get("rejections", [])],
        "new_branches": new_branches,
        "new_sources": new_sources,
        "rejections": skeptic.get("rejections", []),
        "collisions": sorted(cid for cid, row in seen_this_pass.items() if row.get("collision")),
    }
    pass_dir = campaign_dir / "passes" / pass_id
    pass_dir.mkdir(parents=True, exist_ok=True)
    (pass_dir / "gap-report.json").write_text(json.dumps(gap_report, indent=2, sort_keys=True), encoding="utf-8")
    (campaign_dir / "coverage-map.json").write_text(json.dumps(coverage_map, indent=2, sort_keys=True), encoding="utf-8")
    return gap_report


async def run(args: dict[str, str], ctx: Ctx) -> Any:
    topic = args["topic"]
    max_passes = int(args.get("max_passes", "8"))
    saturation_streak = int(args.get("saturation_streak", "2"))

    campaign_dir = ctx.campaign_dir
    brief_path = campaign_dir / "brief.md"
    # Write-once file: read at run start so plan prompts (and their call_keys) stay stable across resume.
    brief = brief_path.read_text(encoding="utf-8") if brief_path.is_file() else ""
    ledger_path = campaign_dir / "source-ledger.jsonl"
    notes_path = campaign_dir / "notes.jsonl"
    coverage_map = _load_coverage_map(campaign_dir)
    quiet_flags: list[bool] = []
    pass_num = 0

    # Seed the map before pass 1: without it, lanes mirror the user's phrasing instead of the field's structure.
    if not coverage_map.get("branches"):
        with phase("scope"):
            try:
                scope = await agent(
                    _build_scope_prompt(topic),
                    schema=SCOPE_SCHEMA,
                    route="throughput",
                    label="scope",
                )
            except AgentError:
                # A failed sweep must not block the campaign from starting -- pass 1 plans
                # from an empty map instead of a taxonomy.
                scope = None
            if scope:
                coverage_map = {
                    "branches": [{"id": b["name"], "focus": b["name"], "status": "thin"} for b in scope["branches"]]
                }
                (campaign_dir / "coverage-map.json").write_text(
                    json.dumps(coverage_map, indent=2, sort_keys=True), encoding="utf-8"
                )

    for pass_num in range(1, max_passes + 1):
        gap_report_path = campaign_dir / "passes" / f"pass-{pass_num}" / "gap-report.json"
        if gap_report_path.is_file():
            # Already merged (a prior run of this same campaign, or an earlier attempt of
            # this same run, got this pass to completion) — re-planning and re-merging it
            # would replay a stale prompt (mutated coverage-map.json no longer matches what
            # was journaled) and double-append the ledger/notes. Reuse it verbatim instead.
            gap_report = json.loads(gap_report_path.read_text(encoding="utf-8"))
            quiet_flags.append(contracts.pass_is_quiet(gap_report))
            if contracts.is_saturated(quiet_flags, saturation_streak):
                ctx.log(f"saturated after pass {pass_num} ({saturation_streak} quiet passes in a row)")
                break
            continue

        with phase(f"pass {pass_num}: plan"):
            gap_report = _latest_gap_report(campaign_dir)
            plan = await agent(
                _build_plan_prompt(topic, coverage_map, gap_report, brief),
                schema=PLAN_SCHEMA,
                route="strong",
                label=f"plan-pass{pass_num}",
            )
            lanes = plan["lanes"]

        with phase(f"pass {pass_num}: research + extract"):

            async def research_stage(lane: dict[str, Any]) -> dict[str, Any]:
                text = await agent(
                    _build_research_prompt(lane, topic),
                    route="throughput",
                    label=f"research-{lane['id']}-pass{pass_num}",
                )
                return {"lane": lane, "research_text": text}

            async def extract_stage(item: dict[str, Any]) -> dict[str, Any]:
                lane = item["lane"]
                extracted = await agent(
                    _build_extract_prompt(lane, item["research_text"]),
                    schema=EXTRACT_SCHEMA,
                    route="throughput",
                    label=f"extract-{lane['id']}-pass{pass_num}",
                )
                return {"lane": lane, **extracted}

            lane_results = await pipeline(lanes, research_stage, extract_stage)

        with phase(f"pass {pass_num}: skeptic"):
            surviving = [r for r in lane_results if r]
            if not surviving:
                # Merging a zero-lane pass writes an empty gap report that reads as a quiet
                # pass -- false saturation. Fail the pass; resume re-runs only the lanes.
                raise AgentError(
                    f"pass-{pass_num}-merge",
                    "workflow",
                    f"pass {pass_num}: all research lanes failed, refusing to merge an empty pass",
                )
            try:
                skeptic = await agent(
                    _build_skeptic_prompt(surviving),
                    schema=SKEPTIC_SCHEMA,
                    route="strong",
                    label=f"skeptic-pass{pass_num}",
                )
            except AgentError:
                # A failed barrier must not discard completed lane work; the lanes' claims
                # still get merged, and the outage itself becomes a gap for the next planner.
                skeptic = {"rejections": [], "summary": "skeptic unavailable"}

        with phase(f"pass {pass_num}: merge"):
            gap_report = _merge(
                campaign_dir, ledger_path, notes_path, coverage_map, lane_results, skeptic, pass_num
            )
            quiet_flags.append(contracts.pass_is_quiet(gap_report))
            ctx.log(f"pass {pass_num} gap report: {json.dumps(gap_report, sort_keys=True)}")

        if contracts.is_saturated(quiet_flags, saturation_streak):
            ctx.log(f"saturated after pass {pass_num} ({saturation_streak} quiet passes in a row)")
            break

    return {
        "passes_run": pass_num,
        "saturated": contracts.is_saturated(quiet_flags, saturation_streak),
        "coverage_branches": len(coverage_map.get("branches", [])),
    }
