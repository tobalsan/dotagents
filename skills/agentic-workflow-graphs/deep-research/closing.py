"""Engine-managed closing graph for an existing deep-research campaign.

Run with ``wfe run closing.py --campaign CAMPAIGN_DIR --routing routes.json``. It snapshots
campaign evidence before its first call and never changes campaign research state.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from workflow_engine import Ctx, agent, phase

MAX_TARGETS = 8
SNAPSHOT_FILES = ("brief.md", "notes.jsonl", "source-ledger.jsonl", "coverage-map.json")

VERIFY_SCHEMA = {
    "type": "object",
    "required": ["targets"],
    "properties": {
        "targets": {
            "type": "array", "maxItems": MAX_TARGETS,
            "items": {
                "type": "object",
                "required": ["target", "status", "evidence_references", "execution_claimed", "artifact_paths"],
                "properties": {
                    "target": {"type": "string"},
                    "status": {"enum": ["confirmed", "conditional", "unresolved"]},
                    "evidence_references": {"type": "array", "items": {"type": "string"}},
                    "execution_claimed": {"type": "boolean"},
                    "artifact_paths": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    },
}

REVIEW_SCHEMA = {
    "type": "object",
    "required": ["status", "blockers", "material_claims", "citation_issues"],
    "properties": {
        "status": {"enum": ["confirmed", "conditional", "unresolved"]},
        "blockers": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
        "material_claims": {"type": "array", "maxItems": 20, "items": {"type": "object"}},
        "citation_issues": {"type": "array", "maxItems": 20, "items": {"type": "object"}},
    },
}


def _read_json(path: Path, default: Any) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [row for line in path.read_text(encoding="utf-8").splitlines() if line.strip() for row in [json.loads(line)]]


def _latest_gap_path(campaign_dir: Path) -> Path | None:
    reports = sorted(
        (campaign_dir / "passes").glob("pass-*/gap-report.json") if (campaign_dir / "passes").is_dir() else [],
        key=lambda path: int(path.parent.name.removeprefix("pass-")),
    )
    return reports[-1] if reports else None


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot(closing_dir: Path, campaign_dir: Path) -> dict[str, Any]:
    """Create once; resumes always reuse this closing run's immutable evidence."""
    evidence_path = closing_dir / "evidence.json"
    if evidence_path.is_file():
        return _read_json(evidence_path, {})

    snapshot_dir = closing_dir / "snapshot"
    manifest_path = snapshot_dir / "manifest.json"
    if manifest_path.is_file():
        manifest = _read_json(manifest_path, {"files": {}})
        evidence = _summary(snapshot_dir, manifest, campaign_dir)
        evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
        return evidence
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    copied: dict[str, dict[str, Any]] = {}
    for name in SNAPSHOT_FILES:
        source = campaign_dir / name
        destination = snapshot_dir / name
        if source.is_file():
            shutil.copyfile(source, destination)
            copied[name] = {"path": str(destination.relative_to(campaign_dir)), "sha256": _digest(destination), "bytes": destination.stat().st_size}
    gap = _latest_gap_path(campaign_dir)
    if gap is not None:
        destination = snapshot_dir / "latest-gap-report.json"
        shutil.copyfile(gap, destination)
        copied["latest-gap-report.json"] = {"path": str(destination.relative_to(campaign_dir)), "sha256": _digest(destination), "bytes": destination.stat().st_size}

    manifest = {"files": copied}
    (snapshot_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    evidence = _summary(snapshot_dir, manifest, campaign_dir)
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    return evidence


def _terms(value: str) -> set[str]:
    return {word.lower() for word in value.split() if len(word) > 3}


def _summary(snapshot_dir: Path, manifest: dict[str, Any], campaign_dir: Path) -> dict[str, Any]:
    notes = _read_jsonl(snapshot_dir / "notes.jsonl")
    sources = _read_jsonl(snapshot_dir / "source-ledger.jsonl")
    coverage = _read_json(snapshot_dir / "coverage-map.json", {"branches": []})
    gap = _read_json(snapshot_dir / "latest-gap-report.json", {})
    brief = (snapshot_dir / "brief.md").read_text(encoding="utf-8") if (snapshot_dir / "brief.md").is_file() else ""
    source_ids = {str(row.get("canonical_id")) for row in sources if row.get("canonical_id")}
    candidates: list[tuple[int, int, dict[str, Any]]] = []
    brief_terms = _terms(brief)
    for index, item in enumerate(gap.get("gaps", [])):
        if isinstance(item, str) and item.strip():
            candidates.append((100 + len(_terms(item) & brief_terms), index, {"target": item.strip(), "kind": "gap"}))
    for index, note in enumerate(notes):
        claim = note.get("claim")
        if note.get("strength") in {"thin", "disputed"} and isinstance(claim, str) and claim.strip():
            citation = str(note.get("citation", ""))
            score = 80 + len(_terms(claim) & brief_terms) + (5 if citation in source_ids else 0)
            candidates.append((score, index, {"target": claim, "kind": "note", "citation": citation}))
    for index, branch in enumerate(coverage.get("branches", [])):
        if isinstance(branch, dict) and branch.get("status") in {"thin", "disputed"}:
            target = str(branch.get("focus") or branch.get("id") or "").strip()
            if target:
                candidates.append((70 + len(_terms(target) & brief_terms), index, {"target": target, "kind": "coverage"}))
    candidates.sort(key=lambda item: (-item[0], item[1], item[2]["target"]))
    targets: list[dict[str, Any]] = []
    seen: set[str] = set()
    for _, _, target in candidates:
        key = target["target"].lower()
        if key not in seen:
            seen.add(key)
            targets.append(target)
        if len(targets) == MAX_TARGETS:
            break
    return {
        "snapshot_manifest": manifest,
        "snapshot_root": str(snapshot_dir.relative_to(campaign_dir)),
        "brief_summary": brief[:2000],
        "coverage_summary": coverage,
        "latest_gap_report": gap,
        "verification_targets": targets,
        "counts": {"notes": len(notes), "source_rows": len(sources), "target_limit": MAX_TARGETS},
    }


def _verification_prompt(evidence: dict[str, Any], closing_dir: Path, campaign_dir: Path) -> str:
    artifacts = closing_dir / "verification-artifacts"
    return (
        "You are closing a deep-research campaign. Campaign working directory contains immutable full evidence at "
        f"{evidence['snapshot_root']}; read relevant snapshot files, not only this bounded summary. Perform only up to eight "
        "named decision-changing targets. You may targeted-fetch a primary source already referenced by snapshot evidence and run "
        "reproducible calculations. Do not search broadly, plan a new pass, or mutate ledger, notes, coverage, or passes. "
        f"Save fetch/calculation artifacts beneath {artifacts.relative_to(campaign_dir)}. For every target return confirmed, conditional, "
        "or unresolved with evidence_references (note claim/citation or source canonical_id) and artifact_paths. Claim execution only "
        "when saved script and result artifacts exist (list both paths); missing evidence or artifacts is unresolved.\n\n"
        f"Bounded summary:\n{json.dumps(evidence, indent=2, sort_keys=True)}"
    )


def _validate_verification(verification: dict[str, Any], closing_dir: Path, campaign_dir: Path) -> dict[str, Any]:
    artifacts_root = (closing_dir / "verification-artifacts").resolve()
    for target in verification["targets"]:
        paths = target.get("artifact_paths", [])
        valid_paths: set[Path] = set()
        missing = False
        for value in paths:
            path = (campaign_dir / value).resolve()
            if not path.is_relative_to(artifacts_root) or not path.is_file():
                missing = True
            else:
                valid_paths.add(path)
        if not target.get("evidence_references") or missing or (target.get("execution_claimed") and len(valid_paths) < 2):
            target["status"] = "unresolved"
    return verification


def _synthesis_prompt(evidence: dict[str, Any], verification: dict[str, Any]) -> str:
    return (
        "Write complete final research report from immutable full snapshot named in bounded summary and targeted verification. "
        "Read relevant full snapshot files. Regenerate from evidence, not prior reports. Distinguish confirmed, conditional, and "
        "unresolved outcomes; cite note citations or source canonical_ids for material claims. Do not conduct new research.\n\n"
        f"Bounded summary:\n{json.dumps(evidence, indent=2, sort_keys=True)}\n\nVerification:\n{json.dumps(verification, indent=2, sort_keys=True)}"
    )


def _review_prompt(evidence: dict[str, Any], verification: dict[str, Any], synthesis: str) -> str:
    return (
        "Perform one final review. Check report material claims and citations against immutable full snapshot and verification. "
        "Do not revise, retry, or conduct research. Return confirmed only when blockers and material citation issues are both empty; "
        "otherwise conditional or unresolved.\n\n"
        f"Bounded summary:\n{json.dumps(evidence, indent=2, sort_keys=True)}\n\nVerification:\n{json.dumps(verification, indent=2, sort_keys=True)}\n\nReport:\n{synthesis}"
    )


async def run(args: dict[str, str], ctx: Ctx) -> Any:
    closing_dir = ctx.campaign_dir / "closing" / ctx.run_dir.name
    closing_dir.mkdir(parents=True, exist_ok=True)
    evidence = _snapshot(closing_dir, ctx.campaign_dir)
    # Never leave a prior published final beside a re-entered closing phase.
    (closing_dir / "final.md").unlink(missing_ok=True)

    with phase("closing: verification"): 
        verification = await agent(_verification_prompt(evidence, closing_dir, ctx.campaign_dir), schema=VERIFY_SCHEMA, route="strong", label="verify-close")
        verification = _validate_verification(verification, closing_dir, ctx.campaign_dir)
        (closing_dir / "verification.json").write_text(json.dumps(verification, indent=2, sort_keys=True), encoding="utf-8")

    (closing_dir / "final.md").unlink(missing_ok=True)
    with phase("closing: synthesis"):
        synthesis = await agent(_synthesis_prompt(evidence, verification), route="strong", label="synthesize-close")
        (closing_dir / "synthesis.md").write_text(synthesis, encoding="utf-8")

    (closing_dir / "final.md").unlink(missing_ok=True)
    with phase("closing: final review"):
        review = await agent(_review_prompt(evidence, verification, synthesis), schema=REVIEW_SCHEMA, route="strong", label="review-close")
        if review["status"] == "confirmed" and (review["blockers"] or review["citation_issues"]):
            review["status"] = "conditional"
        (closing_dir / "review.json").write_text(json.dumps(review, indent=2, sort_keys=True), encoding="utf-8")
        (closing_dir / "final.md").write_text(synthesis + "\n\n## Final review\n\n" + json.dumps(review, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {"closing_dir": str(closing_dir), "status": review["status"], "targets": len(evidence["verification_targets"])}
