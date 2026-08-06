#!/usr/bin/env python3
"""Index a PDF or ebook into a PageIndex Flash workspace for vectorless retrieval.

Usage:
    python index_book.py <path-to-book> [--workspace DIR] [--no-summary]

Accepts PDF plus the ebook formats PyMuPDF can open (EPUB, MOBI, FB2, AZW3),
which is what Z-Library actually serves. Non-PDF input is converted to PDF
first; note that conversion drops the embedded table of contents, so prefer a
PDF edition when one exists.

Prints the doc_id on success (stdout). Idempotent: re-running on an already
indexed path prints the existing doc_id and exits without re-indexing.
"""
import argparse
import json
import os
import sys
import tempfile
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _pageindex_env import resolve_repo, setup_llm_env, default_workspace

# PyMuPDF sniffs by content, so these all round-trip through convert_to_pdf().
EBOOK_SUFFIXES = {".epub", ".mobi", ".fb2", ".azw3"}

# Passed explicitly so the skill never has to edit the repo's config.yaml,
# which is only consulted when summary_model is None.
DEFAULT_SUMMARY_MODEL = "deepseek-v4-flash"


def find_existing(workspace: Path, source_path: str) -> str | None:
    meta_path = workspace / "_meta.json"
    if not meta_path.exists():
        return None
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    for doc_id, entry in meta.items():
        if entry.get("path") == source_path:
            return doc_id
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Index a PDF/EPUB with PageIndex Flash.")
    parser.add_argument("path", help="Path to a PDF or EPUB file")
    parser.add_argument(
        "--workspace", default=None,
        help="Workspace directory (default: $PAGEINDEX_WORKSPACE or ~/.pageindex/workspace)",
    )
    parser.add_argument(
        "--no-summary", action="store_true",
        help="Skip LLM node summaries (fast one-shot triage; summaries are ON by default)",
    )
    args = parser.parse_args()

    source = Path(args.path).expanduser().resolve()
    if not source.is_file():
        sys.exit(f"File not found: {source}")
    if source.suffix.lower() not in EBOOK_SUFFIXES | {".pdf"}:
        sys.exit(
            f"Unsupported file type: {source.suffix} "
            f"(expected .pdf or one of {', '.join(sorted(EBOOK_SUFFIXES))})"
        )

    workspace = Path(args.workspace).expanduser() if args.workspace else default_workspace()
    workspace.mkdir(parents=True, exist_ok=True)

    existing = find_existing(workspace, str(source))
    if existing:
        print(existing)
        print(f"Already indexed as {existing} — skipping re-index ({source})", file=sys.stderr)
        return

    repo = resolve_repo()
    setup_llm_env(repo)  # harmless even when --no-summary skips all LLM calls

    from pageindex.flash import page_index_flash
    import fitz

    tmp_pdf_path = None
    pdf_path = source
    if source.suffix.lower() in EBOOK_SUFFIXES:
        src_doc = fitz.open(str(source))
        pdf_bytes = src_doc.convert_to_pdf()
        src_doc.close()
        fd, tmp_name = tempfile.mkstemp(suffix=".pdf")
        with open(fd, "wb") as f:
            f.write(pdf_bytes)
        tmp_pdf_path = Path(tmp_name)
        pdf_path = tmp_pdf_path

    try:
        tree = page_index_flash(
            str(pdf_path),
            summary=not args.no_summary,
            summary_model=os.environ.get("PAGEINDEX_SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL),
        )
        doc = fitz.open(str(pdf_path))
        pages = [{"page": i + 1, "content": doc[i].get_text()} for i in range(doc.page_count)]
        doc.close()
    finally:
        if tmp_pdf_path is not None:
            tmp_pdf_path.unlink(missing_ok=True)

    doc_id = str(uuid.uuid4())
    record = {
        "id": doc_id,
        "type": "pdf",
        "path": str(source),
        # Always the original filename: for converted ebooks tree["doc_name"]
        # is the throwaway temp PDF, which makes `list` unidentifiable.
        "doc_name": source.name,
        "doc_description": tree.get("doc_title", "") or source.stem,
        "page_count": len(pages),
        "structure": tree["structure"],
        "pages": pages,
    }
    (workspace / f"{doc_id}.json").write_text(
        json.dumps(record, ensure_ascii=False), encoding="utf-8"
    )

    meta_path = workspace / "_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta[doc_id] = {
        "type": "pdf",
        "doc_name": record["doc_name"],
        "doc_description": record["doc_description"],
        "path": record["path"],
        "page_count": record["page_count"],
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(doc_id)


if __name__ == "__main__":
    main()
