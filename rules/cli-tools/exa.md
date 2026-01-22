# exa CLI

## search
Web search with optional live crawling.

```bash
exa search "quantum computing 2024" -n 5
```

Options: `-n` results (default 8), `-t` type (auto|fast|deep), `-l` livecrawl (fallback|preferred)

## code
SDK/documentation search optimized for code context.

```bash
exa code "FastAPI authentication middleware" -t 10000
```

Options: `-t` tokens (default 5000, range 1000-50000)

## deep-search
Multi-query research for complex questions.

```bash
exa deep-search "Compare renewable energy adoption rates" -q "solar 2024,wind europe"
```

Options: `-n` results (default 8), `-q` custom queries (comma-separated, max 5)

---

Global: `--raw` for JSON, `--api-key <key>` override, `--debug` for logs.
