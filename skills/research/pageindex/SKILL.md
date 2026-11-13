---
name: pageindex
description: Answer questions about a long PDF (report, book, manual, paper, contract) with PageIndex, which makes a table of contents of the PDF once and then reads only the pages that a question needs. Use when the user asks a question about a local PDF, asks to "ask the PDF", "search this document", "what does <file>.pdf say about", or names a PDF that is too long to read in full. It runs on the Claude subscription, with no API key.
---

# PageIndex: ask a long PDF

`scripts/pdfask` gives an answer with page numbers. The first question about a PDF makes the index (less than 1 minute for 300 pages). Later questions use the saved index and take about 10 to 20 seconds.

## Commands

Run the commands from this skill folder. Use a timeout of 600 seconds, because the first index of a large PDF can take some minutes.

```bash
scripts/pdfask ask ~/Downloads/report.pdf "What was the 2023 operating margin?"
scripts/pdfask index ~/Downloads/report.pdf    # index only
scripts/pdfask list                            # indexed PDFs
```

## Workflow

1. Get the PDF path from the user. If the user gives only a name, run `scripts/pdfask list`, then search `~/Downloads` and `~/Documents`.
2. Send the question of the user in full. One question per call gives better answers.
3. Give the answer to the user with its page numbers. Do not add facts that the answer does not contain.

## Facts

- Haiku makes the index, and Opus answers. Both run through Claude Code (`claude` must be logged in).
- The index of each PDF is in `~/.local/share/pageindex`. Set `PDFASK_STORE` to use another folder.
- The script finds a PDF by its file name. Two different PDFs with the same file name use the same index. Rename one of them before you index it.
- The script uses the Python environment of the PageIndex checkout at `~/code/playground/pageindex`. Set `PAGEINDEX_REPO` to use another checkout.
- Scanned PDFs (images with no text) do not work in local mode.

## Errors

- `Not logged in`: tell the user to run `claude`, then `/login`.
- `No such file ... .venv/bin/python`: in the checkout, run `uv venv && uv pip install -e ".[claude]"`.
