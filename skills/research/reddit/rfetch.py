#!/usr/bin/env python3
"""Fetch Reddit threads to disk. Prints a manifest only — never the content.

usage: rfetch.py <outdir> <id-or-url> [<id-or-url> ...]
"""
import json, os, re, subprocess, sys

B = "https://arctic-shift.photon-reddit.com/api"


def get(url):
    r = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
    return json.loads(r.stdout or "{}")


def flatten(nodes, depth=0, out=None):
    out = [] if out is None else out
    for n in nodes:
        if n.get("kind") != "t1":
            continue
        d = n["data"]
        out.append((depth, d.get("author") or "?", (d.get("body") or "").strip()))
        r = d.get("replies")
        if isinstance(r, dict):
            flatten(r["data"]["children"], depth + 1, out)
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    outdir, args = sys.argv[1], sys.argv[2:]
    os.makedirs(outdir, exist_ok=True)

    ids, seen = [], set()
    for a in args:
        m = re.search(r"/comments/([a-z0-9]{5,9})", a) or re.fullmatch(r"([a-z0-9]{5,9})", a.strip())
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            ids.append(m.group(1))

    meta = {p["id"]: p for p in (get(f"{B}/posts/ids?ids={','.join(ids)}").get("data") or [])}

    print(f"{'id':10} {'status':12} {'cmts':>5} {'bytes':>7}  path | title")
    for i in ids:
        m = meta.get(i, {})
        sub = m.get("subreddit") or "unknown"
        title = m.get("title") or "(unresolved)"
        body = (m.get("selftext") or "").strip()
        body_ok = len(body) > 40 and body not in ("[removed]", "[deleted]")

        cs = flatten(get(f"{B}/comments/tree?link_id={i}&limit=25000").get("data") or [])
        usable = [c for c in cs if c[2] and c[2] not in ("[removed]", "[deleted]")]

        doc = [f"# {title}", f"https://www.reddit.com/r/{sub}/comments/{i}/",
               f"r/{sub} | u/{m.get('author', '?')} | posted {m.get('created_utc', 0)}"]
        if m.get("removed_by_category"):
            doc.append(f"NOTE: removed from live Reddit ({m['removed_by_category']}) — verify before citing.")
        doc += ["", body if body_ok else "(post body unavailable)", "", "## Comments"]
        doc += [f"{'  ' * d}- [u/{a}] {b}" for d, a, b in usable]
        text = "\n".join(doc)

        path = os.path.join(outdir, f"{i}.md")
        with open(path, "w") as f:
            f.write(text)

        status = m.get("removed_by_category") or ("ok" if body_ok else "no-body")
        print(f"{i:10} {status:12} {len(usable):5} {len(text):7}  {path} | {title[:52]}")

    print(f"\n{len(ids)} threads -> {outdir}/  "
          f"(content NOT loaded into this context — delegate digestion, see SKILL.md)")


if __name__ == "__main__":
    main()
