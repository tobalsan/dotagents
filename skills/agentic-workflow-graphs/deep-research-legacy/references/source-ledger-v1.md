# Source ledger v1

The source ledger is append-only JSONL: one JSON object per line. Validate each line, not the whole file, against [`source-ledger-v1.schema.json`](source-ledger-v1.schema.json).

Each row requires `canonical_id`, `status`, `url`, and `observed_at`. `status` is one of `seen`, `fetched`, `extracted`, or `rejected`. Optional fields are `content_id`, `work_id`, `title`, `source_type`, `retrieved_at`, `reason`, `lane_id`, `pass_id`, and `collision`.

Use `sha256:<64 lowercase hex characters>` of the mechanically normalized URL as the canonical ID fallback. Generic normalization lowercases scheme and host, removes default ports and fragments, sorts query parameters, removes known tracking parameters, and collapses duplicate path separators; it does not strip `www` or decode reserved escapes such as `%2F`. Known provider aliases may normalize to one namespaced identity. A namespaced content ID (`doi:…`, `arxiv:…`, `youtube:…`, or `isbn:…`) may instead own `canonical_id` only when the identical value is recorded in `content_id`; otherwise `canonical_id` must equal the identity derived from `url`. Use `work_id` to link distinct manifestations of one work without collapsing them.

Merge is the sole writer. Researchers only read the folded ledger and skip canonical IDs already present. Merge appends status events; it never updates or deletes rows, including rejected rows. Readers derive current state by taking the last row for each `canonical_id`.

Every target or source count must state its predicate and the folded statuses it includes. For example, “usable sources” may mean rows whose current status is `extracted`; rejected rows remain available for other explicit counts.

Merge deduplicates intra-pass canonical-ID collisions before writing and reports them in the gap report. A written event may set `collision: true` and identify its `pass_id` and `lane_id`; collision reporting must also identify all colliding lanes.

Minimal row:

```jsonl
{"canonical_id":"sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef","status":"seen","url":"https://example.com/source","observed_at":"2026-01-01T00:00:00Z"}
```

Rejected row:

```jsonl
{"canonical_id":"doi:10.1000/example","status":"rejected","url":"https://doi.org/10.1000/example","observed_at":"2026-01-01T00:10:00Z","reason":"Retracted","lane_id":"evidence-quality","pass_id":"pass-2"}
```
