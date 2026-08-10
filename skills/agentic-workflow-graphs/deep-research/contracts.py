"""Deep-research domain contracts: URL identity, ledger fold, saturation.

Plain functions, no CLI, no cross-process locking — the workflow graph's merge
step is the ledger's only writer and runs once per pass inside one process, so
the append-only file just needs an fsync, not a lock. Ported from the retired
scripts/research_state.py guardrail script (kept in git history).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, parse_qsl, quote, urlencode, urlsplit, urlunsplit

STATUSES = {"seen", "fetched", "extracted", "rejected"}
TRACKING = {"fbclid", "gclid", "dclid", "mc_cid", "mc_eid", "ref", "ref_source", "share_id", "context"}


def normalize(url: str) -> dict[str, str | None]:
    """Normalize a URL and derive its source-ledger identity.

    Returns {"normalized_url", "content_id", "canonical_id"}. canonical_id is
    a namespaced content id (doi:/arxiv:/youtube:/isbn:) when the URL matches
    a known provider, else "sha256:<hex>" of the normalized URL.
    """
    p = urlsplit(url.strip())
    host = p.hostname
    if p.scheme.lower() not in {"http", "https"} or not host:
        raise ValueError("url must be absolute http(s) URL")
    host = host.lower()
    path = re.sub(r"/{2,}", "/", p.path) or "/"
    query = parse_qsl(p.query, keep_blank_values=True)
    content_id = None
    if host in {"youtu.be", "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}:
        video = path.strip("/").split("/")[0] if host == "youtu.be" else (parse_qs(p.query).get("v") or [None])[0]
        if not video and path.startswith("/shorts/"):
            video = path.split("/")[2]
        if not video and path.startswith("/embed/"):
            video = path.split("/")[2]
        if video and re.fullmatch(r"[A-Za-z0-9_-]{6,}", video):
            content_id = f"youtube:{video}"
            host = "youtube.com"
            path = "/watch"
            query = [("v", video)]
    elif host in {"arxiv.org", "export.arxiv.org"}:
        m = re.match(r"/(?:abs|pdf)/([^/?]+?)(?:\.pdf)?$", path)
        if m:
            ident = re.sub(r"v\d+$", "", m.group(1), flags=re.I)
            content_id = f"arxiv:{ident.lower()}"
            host = "arxiv.org"
            path = f"/abs/{ident.lower()}"
            query = []
    elif host in {"doi.org", "dx.doi.org"}:
        doi = path.lstrip("/").lower()
        if doi.startswith("10."):
            content_id = f"doi:{doi}"
            host = "doi.org"
            path = "/" + doi
            query = []
    elif host in {"reddit.com", "www.reddit.com", "old.reddit.com", "new.reddit.com", "np.reddit.com", "redd.it"}:
        short_id = path.strip("/").split("/")[0] if host == "redd.it" else None
        host = "reddit.com"
        m = re.search(r"/comments/([a-z0-9]+)", path, re.I)
        if m or short_id:
            path = f"/comments/{(m.group(1) if m else short_id).lower()}"
        query = []
    query = sorted((k, v) for k, v in query if not k.lower().startswith("utm_") and k.lower() not in TRACKING)
    port = p.port
    display_host = f"[{host}]" if ":" in host else host
    default_port = (p.scheme.lower() == "http" and port == 80) or (p.scheme.lower() == "https" and port == 443)
    netloc = display_host + (f":{port}" if port and not default_port else "")
    canonical_url = urlunsplit((p.scheme.lower(), netloc, quote(path, safe="/%:@-._~!$&'()*+,;="), urlencode(query), ""))
    canonical_id = content_id or "sha256:" + hashlib.sha256(canonical_url.encode()).hexdigest()
    return {"normalized_url": canonical_url, "content_id": content_id, "canonical_id": canonical_id}


def fold_ledger(path: Path) -> dict[str, dict[str, Any]]:
    """Fold an append-only source-ledger JSONL: last row wins per canonical_id."""
    result: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return result
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                row = json.loads(line)
                result[row["canonical_id"]] = row
    return result


def known_canonical_ids(path: Path) -> set[str]:
    """Canonical IDs already recorded in the ledger — researchers skip these."""
    return set(fold_ledger(path))


def append_ledger(path: Path, row: dict[str, Any]) -> None:
    """Append one row to the ledger, fsync'd for durability. Merge is the only writer."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def pass_is_quiet(gap_report: dict[str, Any]) -> bool:
    """A pass is quiet when it found nothing new: no new sources, no new coverage branches.

    Rejections and thin lanes stay in the gap report for the next planner, but don't gate
    saturation themselves -- a single skeptic rejection would otherwise make every pass
    non-quiet forever, since a real campaign practically always has *some* live gap.
    """
    return not gap_report.get("new_sources") and not gap_report.get("new_branches")


def is_saturated(quiet_flags: list[bool], streak: int) -> bool:
    """True once the last `streak` passes were all quiet. One quiet pass is noise."""
    return len(quiet_flags) >= streak and all(quiet_flags[-streak:])
