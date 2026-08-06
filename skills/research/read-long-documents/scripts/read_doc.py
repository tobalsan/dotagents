#!/usr/bin/env python3
"""Read from a PageIndex Flash workspace: the three vectorless retrieval primitives.

Usage:
    python read_doc.py [--workspace DIR] list
    python read_doc.py [--workspace DIR] meta <doc_id>
    python read_doc.py [--workspace DIR] structure <doc_id>
    python read_doc.py [--workspace DIR] pages <doc_id> <range>   # e.g. "5-7", "3,8", "12"

Prints JSON (or plain text for errors) to stdout. Read-only: makes no LLM
calls and needs no API key.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _pageindex_env import resolve_repo, default_workspace


def load_meta(workspace: Path) -> dict:
    meta_path = workspace / "_meta.json"
    if not meta_path.exists():
        return {}
    return json.loads(meta_path.read_text(encoding="utf-8"))


def load_full(workspace: Path, doc_id: str) -> dict | None:
    path = workspace / f"{doc_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Read a PageIndex Flash workspace.")
    parser.add_argument(
        "--workspace", default=None,
        help="Workspace directory (default: $PAGEINDEX_WORKSPACE or ~/.pageindex/workspace)",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List all documents in the workspace")
    p_meta = sub.add_parser("meta", help="Document metadata (doc_id, name, description, page_count)")
    p_meta.add_argument("doc_id")
    p_struct = sub.add_parser("structure", help="Full tree structure (node titles + page ranges)")
    p_struct.add_argument("doc_id")
    p_pages = sub.add_parser("pages", help="Raw page content for a page range")
    p_pages.add_argument("doc_id")
    p_pages.add_argument("range", help='e.g. "5-7", "3,8", or "12"')
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser() if args.workspace else default_workspace()

    if args.command == "list":
        meta = load_meta(workspace)
        docs = [dict(entry, doc_id=doc_id) for doc_id, entry in meta.items()]
        print(json.dumps(docs, ensure_ascii=False, indent=2))
        return

    meta = load_meta(workspace)
    if args.doc_id not in meta:
        sys.exit(f"Unknown doc_id: {args.doc_id} (run 'list' to see indexed docs)")
    documents = {args.doc_id: dict(meta[args.doc_id], id=args.doc_id)}

    resolve_repo()
    from pageindex.retrieve import get_document, get_document_structure, get_page_content

    if args.command == "meta":
        print(get_document(documents, args.doc_id))
        return

    full = load_full(workspace, args.doc_id)
    if full is None:
        sys.exit(f"Missing document record: {workspace / (args.doc_id + '.json')}")
    documents[args.doc_id]["structure"] = full.get("structure", [])

    if args.command == "structure":
        print(get_document_structure(documents, args.doc_id))
    elif args.command == "pages":
        documents[args.doc_id]["pages"] = full.get("pages", [])
        print(get_page_content(documents, args.doc_id, args.range))


if __name__ == "__main__":
    main()
