---
name: find-ebooks
description: "Search for and download ebooks/books from Z-Library via a local CLI. Trigger when finding or downloading a book/ebook, acquiring source material for research, or getting a text to read/analyze — including 'find me a book on X', 'download the PDF of X', 'get an ebook of X'."
---

# Find Ebooks (Z-Library)

## Overview
A local CLI (`zlib`) searches Z-Library and downloads books. It solves Z-Library's
self-hosted SHA-1 proof-of-work in-process (~0.02s) — no browser, no Playwright,
no `--no-headless` flag (that flag was removed along with the old Playwright path).

## Prerequisites
The `zlib` CLI must already be installed at the repo below with dependencies synced.
Run this preflight check first. If the repo isn't found, ask the user for its actual
path and re-run with `ZLIBRARY_REPO` set — don't guess or clone unprompted. For other
failures, run the fix it prints and STOP.

```bash
ZLIBRARY_REPO="${ZLIBRARY_REPO:-$HOME/code/playground/zlibrary}"

if [ ! -d "$ZLIBRARY_REPO" ]; then
  echo "FAIL: repo not found at $ZLIBRARY_REPO"
  echo "Ask the user where the zlibrary repo is, then re-run with ZLIBRARY_REPO=<path>. Only if they say it isn't installed anywhere, offer to clone it."
  exit 1
fi

cd "$ZLIBRARY_REPO"

if ! uv run zlib --help >/dev/null 2>&1; then
  echo "FAIL: 'uv run zlib' does not work in $ZLIBRARY_REPO"
  echo "Fix: run 'cd $ZLIBRARY_REPO && uv sync'. STOP."
  exit 1
fi

if [ -f "$ZLIBRARY_REPO/.env" ] && grep -q '^ZLIBRARY_EMAIL=' "$ZLIBRARY_REPO/.env" && grep -q '^ZLIBRARY_PASSWORD=' "$ZLIBRARY_REPO/.env"; then
  echo "OK: repo present, zlib runs, credentials configured (raised download cap)"
else
  echo "OK: repo present, zlib runs, no credentials configured (anonymous, 5 downloads/day cap)"
fi
```

## Quick start
```bash
cd "${ZLIBRARY_REPO:-$HOME/code/playground/zlibrary}"
uv run zlib search "deep learning"                          # numbered table of results
uv run zlib get "deep learning" 1 -o ~/.ebooks               # download result #1, always pass a selection
```

## Commands
### search
```bash
uv run zlib search "<query>" -p <page>
```
Prints a rich table numbered from 1, with columns: Title, Author, Year, **Format**, Size, Lang.
`-p/--page` (default 1) paginates.

### get
```bash
uv run zlib get "<query>" <selection> -o <dir>
```
Searches then downloads. `<selection>` is a result number (`3`) or comma-separated
numbers (`1,3,5`). **Always pass `<selection>` explicitly** — omitting it makes the
CLI block on an interactive prompt, which hangs an agent. `-o/--output` sets the
download directory (default `.`).

There is no other flag surface — only `-p/--page` on `search` and `-o/--output` on `get`.

## Workflow
1. `uv run zlib search "<query>"` and read the table — note **Format** and Size per row.
2. Pick the result number to download. Z-Library serves PDF, EPUB, MOBI, AZW3, and
   FB2 — **prefer PDF when available** (see "Downstream: read-long-documents" below).
3. `uv run zlib get "<query>" <number> -o ~/.ebooks` — same query, explicit selection,
   explicit output directory.
4. Hand the downloaded file path to the `read-long-documents` skill to index and
   query it.

Use `~/.ebooks` as the default shared library directory, overridable via
`EBOOK_LIBRARY` (e.g. `-o "${EBOOK_LIBRARY:-$HOME/.ebooks}"`). Keeping downloads in
one place lets other agents reuse them without re-downloading.

## Downstream: read-long-documents
The companion skill `read-long-documents` indexes a downloaded book with PageIndex
for reasoning-based retrieval. It handles PDF, EPUB, MOBI, FB2, and AZW3, but
converting any non-PDF format automatically drops the embedded table of contents and
degrades the structure tree. **Prefer downloading the PDF over other formats when
available for the same title** — check the Format column before picking a number.

## Failure modes
- `Daily download limit reached for your IP (anonymous access allows 5/day)` —
  anonymous cap hit. Add `ZLIBRARY_EMAIL`/`ZLIBRARY_PASSWORD` to the repo's `.env`
  to raise it.
- Yellow `<mirror> returned <code>, trying next...` (or `Timeout connecting to
  <mirror>, trying next...`) — normal mirror rotation across `1lib.sk`, `z-lib.fm`,
  `z-library.ec`, `z-lib.sk`, `z-lib.gd`. Not an error; only a problem if every
  mirror fails.
- All mirrors failing prints a red `All Z-Library mirrors failed
  (timeout/403/404/503).` and exits non-zero.
- Downloads reliably redirect on `1lib.sk`; other mirrors can serve a login-gated
  HTML page instead of the file — retry `get` if the saved file looks wrong.

## Security
Credentials live only in the repo's gitignored `.env`
(`ZLIBRARY_EMAIL`/`ZLIBRARY_PASSWORD`). Never echo, log, or pass them on a command
line — the CLI reads them from `.env` itself. Login is optional; the tool works
anonymously, just capped at 5 downloads/IP/day.
