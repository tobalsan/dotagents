---
name: exa
description: "Use the exa CLI for web search, code/documentation search, or multi-query research. Trigger when a task needs web lookups or crawl-based results via exa search, exa code, or exa deep-search."
---

# Exa

## Overview
Use exa CLI to search the web, search code/docs, or run multi-query research.

## Quick start
```bash
exa search "quantum computing 2024" -n 5
exa code "FastAPI authentication middleware" -t 10000
exa deep-search "Compare renewable energy adoption rates" -q "solar 2024,wind europe"
```

## Commands
### search
Run web search with optional live crawling.

```bash
exa search "query" -n 5 -t auto -l preferred
```

Options:
- `-n` results (default 8)
- `-t` type: auto|fast|deep
- `-l` livecrawl: fallback|preferred

### code
Run SDK/documentation search optimized for code context.

```bash
exa code "query" -t 10000
```

Options:
- `-t` tokens (default 5000, range 1000-50000)

### deep-search
Run multi-query research for complex questions.

```bash
exa deep-search "main query" -q "q1,q2,q3"
```

Options:
- `-n` results (default 8)
- `-q` custom queries (comma-separated, max 5)

## Global flags
- `--raw` JSON output
- `--api-key <key>` override
- `--debug` logs
