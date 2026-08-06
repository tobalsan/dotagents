---
name: arxiv
description: Find, download, and read arXiv papers as research sources — semantic discovery, abstract-level triage, PDF-to-text, and citation-chasing to expand a search frontier. Use whenever a research lane needs primary literature, an arxiv.org link needs to be read or cited, or a question calls for "what does the paper actually say". NOT for general web search or non-arXiv publishers.
---

# arXiv

`arxiv.py` (this skill's directory, stdlib only) is the base tool. Run it as:

```bash
A="$(dirname "$0")/arxiv.py"   # or the absolute path to this skill's arxiv.py
uv run --no-project --quiet python "$A" --help
```

**A paper is ~30k tokens of full text and ~300 tokens of abstract.** Chain-of-Thought Prompting is 133 KB as extracted text; its abstract answers "is this relevant?" for 1/100th of that. The whole job is spending abstract-sized tokens on triage and full-text tokens only on the few papers that survive. Work in a scratch dir (`-o $DIR`), not the current one — `get` writes files.

## 1. Find candidates

**Natural-language question → `exa`.** arXiv's own relevance ranking is keyword matching, not semantics: `search "chain of thought faithfulness"` returns a solar-physics paper about the CHAIN telescope network in the top 4. Exa returns the right papers in under a second.

```bash
exa search -n 10 -m 200 "arxiv.org paper on <the question, phrased as a question>"
```

**Structured or exhaustive sweeps → the arXiv API.** Author, exact phrase, category, date window — things exa can't guarantee coverage on.

```bash
uv run --no-project --quiet python "$A" search "in-context learning" -n 20
uv run --no-project --quiet python "$A" search 'cat:cs.CL AND abs:"retrieval augmented"' \
  -n 50 --sort date --since 2025-01 --until 2025-03
uv run --no-project --quiet python "$A" search 'au:"Jason Wei"' --sort date
```

A bare query is wrapped as `all:`. Raw syntax passes through: `ti:` `abs:` `au:` `cat:` joined by `AND` / `OR` / `ANDNOT`, phrases in double quotes. `--sort date` is submission date descending; relevance is the default and is the weak one.

Output is one line per paper — `id | date | title | authors | categories` — ~120 bytes each, against ~2.5 KB per entry of raw Atom XML.

## 2. Triage on abstracts, not papers

```bash
uv run --no-project --quiet python "$A" search "<query>" -n 20 --abs
uv run --no-project --quiet python "$A" meta <ids-or-urls...> --abs
```

`meta` takes anything containing an arXiv id — `https://arxiv.org/html/2402.13950v3`, `arXiv:2201.11903`, `cs/0102003`, a bare id — and resolves it to canonical metadata. This is how you turn exa's mixed bag of `/abs/`, `/html/`, and `/pdf/` URLs into dedupable ids. Batch them in one call; it is one HTTP request regardless of count.

Decide from the abstract. Most candidates die here, and that is the point.

## 3. Full text for the survivors

```bash
uv run --no-project --quiet python "$A" get <ids...> -o "$DIR"
```

Downloads the PDF and converts it, printing `id | size | path`. Idempotent — an already-converted paper is a no-op, so a crawl can re-request freely. Three papers cold takes about half a second.

Two things this gets right that a hand-rolled `curl | pdftotext` does not:

- **No `-layout`.** On a two-column paper (ACL, IEEE) `-layout` interleaves both columns line by line into unreadable text. Plain `pdftotext` follows the columns correctly. On single-column papers `-layout` just adds ~26% in whitespace padding.
- **Versionless ids.** `2502.14829v1` and `2502.14829` are the same source; storing them separately corrupts any dedup count.

The LaTeXML renderings (`arxiv.org/html/<id>` for papers from ~Dec 2023, `ar5iv.org/abs/<id>` for older) are an alternative when the PDF extracts badly — heavy tables, unusual typesetting. Neither is *smaller* than the PDF text (markdown conversion of one paper ran 149 KB against 67 KB from `pdftotext`), so reach for them for fidelity, not economy. Both 404 or return a stub for some papers; check the response size before trusting it.

## 4. Navigate, don't swallow

Never read a whole `.txt` unless you are genuinely summarizing the whole paper.

```bash
head -120 "$DIR/<id>.txt"                                  # title, abstract, intro — ~4 KB
grep -inE "<concept>|<method name>" "$DIR/<id>.txt"        # where it's discussed
sed -n '426,461p' "$DIR/<id>.txt"                          # read that window — ~2 KB
```

For the 133 KB CoT paper: front matter is 3.8 KB, and three grep-anchored windows are 5 KB. That is 7% of the file for the parts that answer the question. Section headers survive extraction unreliably — small caps come out as `I NTRODUCTION` — so anchor on the concept words, not on a header regex.

## 5. Expand the frontier

A paper's reference list is the cheapest source of new candidates in the whole pipeline.

```bash
uv run --no-project --quiet python "$A" refs <id-or-txt-path...> -o "$DIR"
```

Returns the cited arXiv ids, deduped, self-references removed — 27 from the CoT paper, 38 from a typical recent one. Feed them back into step 2. Papers only cite backwards; for forward citations you need an external index, and both free ones are unreliable (see below).

## Failure modes

| Symptom | What to do |
| --- | --- |
| Empty response from `export.arxiv.org` | You used `http://`. It 301s and a plain `curl` without `-L` writes zero bytes. Always `https://`. |
| Search returns an obviously off-topic paper | Expected — arXiv relevance is keyword matching. Re-run through exa, or tighten with `abs:"exact phrase"` and `cat:`. |
| Many requests in one run | arXiv asks for roughly one API request every three seconds. A fleet of parallel researchers all hitting it is exactly what earns a 503 with `Retry-After`. Batch ids into single `meta` calls, and serialize the search lane. |
| `pdftotext: command not found` | `brew install poppler`. |
| Extracted text is empty or gibberish | Scanned or image-only PDF, most common in older submissions. Try `arxiv.org/html/<id>` or `ar5iv.org/abs/<id>`; if both are stubs, record it with metadata only and move on. |
| Semantic Scholar API for citation counts | Returns `429` unauthenticated, essentially always. Needs a key. |
| OpenAlex for citation counts | Free and keyless, but arXiv records carry polluted metadata — the DOI for the CoT paper resolves to a record titled "BNAI, NO-TOKEN, and MIND-UNITY". Use the count as a weak signal at most, and never trust its title over arXiv's. |
| `--sort date` returns nothing for a date window | `--since` / `--until` take `YYYY-MM`. A malformed value silently narrows the range to empty. |

## Reporting a paper as a source

Cite it by canonical URL, `https://arxiv.org/abs/<id>`, using the **versionless** id. That id is the dedup key: `/abs/`, `/pdf/`, `/html/`, `ar5iv`, `v1`…`v6`, and the `10.48550/arXiv.<id>` DOI are all the same source and will otherwise inflate a unique-source count sixfold.

Carry the submission date and first author with any claim. arXiv is not peer reviewed — a preprint is a claim by named people on a known date, and both halves are what let a reader weigh it. Say when a finding comes from an unreviewed preprint rather than a published version.
