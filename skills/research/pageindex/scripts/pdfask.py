"""Ask questions about a long PDF with PageIndex, through the Claude subscription.

    pdfask ask <pdf> "<question>"   index the PDF if needed, then answer
    pdfask index <pdf>              index only
    pdfask list                     show the indexed PDFs
"""
import os
import sys
from pathlib import Path

from pageindex import PageIndexClient
from pageindex.errors import PageIndexAPIError

STORE = Path(os.environ.get("PDFASK_STORE", "~/.local/share/pageindex")).expanduser()

client = PageIndexClient(
    index={"model": "claude-code/haiku", "storage_path": str(STORE)},
    chat="claude-code/opus",
)


def doc_id_for(pdf: Path) -> str:
    try:
        return client.get_document_id(pdf.name)
    except PageIndexAPIError:
        print(f"Indexing {pdf.name} (first time only)...", file=sys.stderr)
        doc_id = client.submit_document(str(pdf))["doc_id"]
        print(f"Indexed: {doc_id}", file=sys.stderr)
        return doc_id


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else ""
    if cmd == "list":
        for d in client.list_documents().get("documents", []):
            print(f"{d['name']}  ({d.get('pageNum')} pages)  {d['id']}")
        return 0
    if cmd in ("index", "ask") and len(argv) >= 2:
        pdf = Path(argv[1]).expanduser()
        if not pdf.is_file():
            print(f"Error: file not found: {pdf}", file=sys.stderr)
            return 1
        doc_id = doc_id_for(pdf)
        if cmd == "ask" and len(argv) >= 3:
            print(client.chat(" ".join(argv[2:]), doc_id=doc_id, show_process=False,
                              instructions="Give the page number for each fact."))
            return 0
        if cmd == "index":
            return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
