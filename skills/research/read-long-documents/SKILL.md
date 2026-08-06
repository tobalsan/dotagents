---
name: read-long-documents
description: "Reason over long PDFs and ebooks (EPUB, MOBI, FB2, AZW3) without embeddings or a vector store. Index a document once with PageIndex Flash to get its table-of-contents-like tree, then let the calling agent pick page ranges and pull only that prose. Trigger on: reading/QA over long PDFs or books, EPUBs, MOBI, vectorless RAG, PageIndex, \"what does this book say about X\", indexing a document for retrieval, document search without embeddings."
---

# Read Long Documents

## Overview
PageIndex Flash turns a PDF or ebook (EPUB, MOBI, FB2, AZW3) into a tree of titled nodes with page ranges — no
embeddings, no vector DB. The calling agent (you) is the retrieval engine: read the
tree, reason about which nodes are relevant, then pull only those pages. A 332-page
book's whole structure is ~1.1K tokens, so it fits in context alongside your reasoning.

This skill wraps two scripts around a pinned local checkout of PageIndex
(`~/code/playground/PageIndex`, commit `d5c4e62`). **Do not `git pull` that
repo** — Flash's structure output can change and invalidate research in progress. If a
newer version is genuinely needed, re-verify the whole workflow before trusting it.

## Prerequisites
This skill depends on a real checkout + venv of PageIndex. It will NOT auto-install
anything. Run this preflight check before anything else. If the repo isn't found, ask
the user for its actual path and re-run with `PAGEINDEX_REPO` set — don't guess or
clone unprompted. For other failures, follow the printed instructions and stop.

```bash
REPO="${PAGEINDEX_REPO:-$HOME/code/playground/PageIndex}"

test -d "$REPO" || { echo "MISSING REPO. Ask the user where PageIndex is checked out, then re-run with PAGEINDEX_REPO=<path>. Only if they say it isn't installed anywhere: git clone https://github.com/VectifyAI/PageIndex \"$REPO\" && git -C \"$REPO\" checkout d5c4e62"; exit 1; }

test -d "$REPO/.venv" || { echo "MISSING VENV. Run: cd \"$REPO\" && uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt"; exit 1; }

"$REPO/.venv/bin/python" -c "import sys; sys.path.insert(0,'$REPO'); import pageindex" \
  || { echo "IMPORT FAILED. Run: cd \"$REPO\" && uv pip install --python .venv/bin/python -r requirements.txt"; exit 1; }

"$REPO/.venv/bin/python" -c "
import sys, os; sys.path.insert(0, '$REPO')
from dotenv import load_dotenv
load_dotenv('$REPO/.env', override=True)
assert os.getenv('OPENAI_API_KEY'), 'No key in PageIndex/.env'
print('API key resolves OK')
" || { echo "NO API KEY. Put OPENAI_API_KEY / OPENAI_API_BASE in \"$REPO/.env\""; exit 1; }

echo "PREFLIGHT OK"
```

One more one-time repo-level fix if you cloned fresh: `pageindex/config.yaml`'s
`model`, `summary_model`, `retrieve_model` must name a model your endpoint actually
serves (the shipped defaults, e.g. `gpt-4o-2024-11-20`, are placeholders and will
403/404 against most non-OpenAI endpoints). This checkout already has all three set to
`deepseek-v4-flash` to match its `.env`'s `https://api.deepseek.com` endpoint — if you
point `.env` at a different provider, update `config.yaml` to match.

Both scripts below handle the remaining two blockers themselves on every run: they add
`$PAGEINDEX_REPO` to `sys.path`, and — only when about to make an LLM call (node
summaries) — call `load_dotenv(<repo>/.env, override=True)` and copy
`OPENAI_API_BASE` into `OPENAI_BASE_URL` (the OpenAI SDK reads `OPENAI_BASE_URL`, not
`OPENAI_API_BASE`, and an ambient shell `OPENAI_API_KEY` would otherwise shadow the
repo's own key). Read-only retrieval (`list`/`meta`/`structure`/`pages`) makes no LLM
call and needs none of this.

## Quick start
```bash
PY="${PAGEINDEX_REPO:-$HOME/code/playground/PageIndex}/.venv/bin/python"

# Index once (summaries ON by default — good synopsis per node, ~2min/300pg book)
$PY scripts/index_book.py mybook.epub   # PDF, MOBI, FB2, AZW3 also work
# -> prints a doc_id

# Get the map (cheap: whole tree, no page text)
$PY scripts/read_doc.py structure <doc_id>

# Pull only the pages you actually need
$PY scripts/read_doc.py pages <doc_id> "42-45"
```

Run scripts with the PageIndex repo's own venv interpreter (`$PAGEINDEX_REPO/.venv/bin/python`)
— it has the pinned dependency versions this skill was verified against.

## Commands

### `index_book.py <path> [--workspace DIR] [--no-summary]`
Indexes a PDF, EPUB, MOBI, FB2, or AZW3 with PageIndex Flash (layout-statistics tree
extraction, no LLM; ~seconds even for 300+ pages). Non-PDF formats are converted to
PDF in memory first (drops the embedded TOC, but Flash still recovers chapter
structure from layout) — prefer a PDF edition when one exists. Prints the `doc_id` on
stdout.

- `--workspace DIR` — workspace directory. Default: `$PAGEINDEX_WORKSPACE` env var, else
  `~/.pageindex/workspace`.
- `--no-summary` — skip LLM node summaries (fast one-shot triage; no API key needed
  when the tree is used purely for page-range navigation). Summaries are **ON by
  default** — they're worth the ~2 min for a 300-page book because they let you decide
  which nodes matter without opening any pages.
- **Idempotent**: re-running on a path already indexed in the workspace prints the
  existing `doc_id` and exits immediately — it does not re-index.

### `read_doc.py [--workspace DIR] list`
Lists every document in the workspace as JSON: `doc_id`, `doc_name`, `doc_description`,
`page_count`, `path`. `doc_name` is always the original source filename (not a
conversion temp name), so agents can identify books in a shared workspace.

### `read_doc.py [--workspace DIR] meta <doc_id>`
Document metadata JSON: `doc_id`, `doc_name`, `doc_description`, `type`, `page_count`.

### `read_doc.py [--workspace DIR] structure <doc_id>`
Full tree JSON: nested `{title, node_id, start_index, end_index, summary?, nodes}`.
This is the map — read it whole, it's small.

### `read_doc.py [--workspace DIR] pages <doc_id> <range>`
Raw page text as JSON `[{page, content}, ...]`. Range syntax: `"12"`, `"5-7"`, `"3,8"`.
Pull only the pages a node's `start_index`–`end_index` says you need.

## Workflow
1. **Index once**: `index_book.py book.pdf` → `doc_id`. Re-runs are free (idempotent).
2. **Get the map**: `read_doc.py structure <doc_id>` — hold the whole tree in context.
3. **Reason about which nodes matter** for the question, using titles (and summaries,
   if generated) — no tool call needed for this step, it's just you reading the JSON.
4. **Pull only those page ranges**: `read_doc.py pages <doc_id> "<start>-<end>"` per
   relevant node. Keep ranges tight — a node's own `start_index`/`end_index`, not the
   whole chapter's neighborhood.
5. **Cite by node title + page range** (e.g. "Ch. 4, 'Dynamic Refinement Ordering', pp.
   88-91") so the answer is traceable back to a specific, re-fetchable slice of the
   source — this is the point of skipping embeddings: every retrieval is exact and
   inspectable, not a similarity-score guess.

Repeat steps 3-4 as your reasoning uncovers more nodes worth checking — the tree is
cheap to hold, so re-consult it rather than guessing page numbers.
