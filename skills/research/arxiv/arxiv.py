#!/usr/bin/env python3
"""arXiv retrieval for research agents. Stdlib only — run via `uv run --no-project`."""
import argparse
import os
import pathlib
import re
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}
ID_RE = re.compile(r"([0-9]{4}\.[0-9]{4,5}|[a-z-]+(?:\.[A-Z]{2})?/[0-9]{7})(v[0-9]+)?", re.IGNORECASE)
FIELD_RE = re.compile(r"\b(all|ti|abs|au|cat|co|jr|rn|id):")


def canonical(s):
    """Any arXiv URL / citation / bare id -> versionless id."""
    m = ID_RE.search(s)
    return m.group(1) if m else None


def fetch(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "research-agent/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return ET.fromstring(r.read())


def entries(root):
    for e in root.findall("a:entry", NS):
        get = lambda t, e=e: (e.findtext("a:" + t, "", NS) or "").strip()
        authors = [a.findtext("a:name", "", NS) for a in e.findall("a:author", NS)]
        yield {
            "id": canonical(get("id")) or "?",
            "date": get("published")[:10],
            "title": " ".join(get("title").split()),
            "authors": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""),
            "cats": " ".join(sorted({c.get("term") for c in e.findall("a:category", NS)})),
            "abstract": " ".join(get("summary").split()),
        }


def show(rows, with_abs):
    for r in rows:
        print(f"{r['id']} | {r['date']} | {r['title']} | {r['authors']} | {r['cats']}")
        if with_abs:
            print(f"    {r['abstract']}\n")
    print(f"-- {len(rows)} results", file=sys.stderr)


def cmd_search(a):
    q = a.query if FIELD_RE.search(a.query) else f"all:{a.query}"
    if a.since or a.until:
        lo = (a.since or "1991-01").replace("-", "") + "010000"
        hi = (a.until or "2999-12").replace("-", "") + "312359"
        q = f"({q}) AND submittedDate:[{lo} TO {hi}]"
    root = fetch({
        "search_query": q,
        "max_results": a.n,
        "sortBy": {"relevance": "relevance", "date": "submittedDate"}[a.sort],
        "sortOrder": "descending",
    })
    show(list(entries(root)), a.abstracts)


def cmd_meta(a):
    ids = [canonical(x) for x in a.ids]
    ids = [i for i in ids if i]
    root = fetch({"id_list": ",".join(ids), "max_results": len(ids)})
    show(list(entries(root)), a.abstracts)


def cmd_get(a):
    os.makedirs(a.out, exist_ok=True)
    for raw in a.ids:
        aid = canonical(raw)
        if not aid:
            print(f"SKIP {raw}: not an arXiv id", file=sys.stderr)
            continue
        stem = aid.replace("/", "_")
        pdf, txt = f"{a.out}/{stem}.pdf", f"{a.out}/{stem}.txt"
        if not os.path.exists(txt):
            req = urllib.request.Request(
                f"https://arxiv.org/pdf/{aid}", headers={"User-Agent": "research-agent/1.0"}
            )
            try:
                with urllib.request.urlopen(req, timeout=120) as r, open(pdf, "wb") as f:
                    f.write(r.read())
            except (OSError, ValueError) as exc:
                print(f"FAIL {aid}: {exc}", file=sys.stderr)
                continue
            # no -layout: it interleaves the columns of two-column papers into garbage
            subprocess.run(["pdftotext", pdf, txt], check=True)
        kb = os.path.getsize(txt) // 1024
        print(f"{aid} | {kb}KB (~{kb // 4}k tokens) | {txt}")


def cmd_refs(a):
    text = ""
    for src in a.sources:
        if os.path.exists(src):
            text += pathlib.Path(src).read_text(errors="ignore")
        else:
            aid = canonical(src)
            p = f"{a.out}/{aid.replace('/', '_')}.txt"
            if not os.path.exists(p):
                cmd_get(argparse.Namespace(ids=[aid], out=a.out))
            text += pathlib.Path(p).read_text(errors="ignore")
    self_ids = {canonical(s) for s in a.sources}
    found = {m.group(1) for m in ID_RE.finditer(text)} - self_ids
    print("\n".join(sorted(found)))
    print(f"-- {len(found)} cited arXiv ids", file=sys.stderr)


p = argparse.ArgumentParser(prog="arxiv.py")
sub = p.add_subparsers(required=True)

s = sub.add_parser("search", help="query the arXiv API")
s.add_argument("query", help="bare terms (wrapped as all:) or raw syntax: ti: abs: au: cat:")
s.add_argument("-n", type=int, default=20)
s.add_argument("--abstracts", "--abs", action="store_true", dest="abstracts")
s.add_argument("--sort", choices=["relevance", "date"], default="relevance")
s.add_argument("--since", help="YYYY-MM")
s.add_argument("--until", help="YYYY-MM")
s.set_defaults(func=cmd_search)

m = sub.add_parser("meta", help="resolve ids/urls to canonical metadata")
m.add_argument("ids", nargs="+")
m.add_argument("--abstracts", "--abs", action="store_true", dest="abstracts")
m.set_defaults(func=cmd_meta)

g = sub.add_parser("get", help="download pdf -> text (cached, idempotent)")
g.add_argument("ids", nargs="+")
g.add_argument("-o", "--out", default="./papers")
g.set_defaults(func=cmd_get)

r = sub.add_parser("refs", help="cited arXiv ids, for frontier expansion")
r.add_argument("sources", nargs="+", help="arXiv ids or .txt paths")
r.add_argument("-o", "--out", default="./papers")
r.set_defaults(func=cmd_refs)

a = p.parse_args()
a.func(a)
