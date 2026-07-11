---
name: council
description: Run multi-LLM deliberation via the `council` CLI. Use when user asks to query multiple LLMs, get consensus answers, run council deliberations, or test individual LLM members/head. Triggers on "council", "ask the council", "deliberate", or any request to fan out a question to multiple models and synthesize.
---

# Council CLI

`council` orchestrates a 3-round deliberation: parallel member queries → optional revision after seeing peers → head model synthesis.

Note: the `~/.council/council.json` config file is required to run this skill.

## Usage

```bash
# Full deliberation
council "Your question here"

# Skip revision round
council --no-revise "Quick question"

# Show each member's answer before synthesis
council --verbose "Design question"

# Neutral members (no stances) — preferred for ideation / open-ended exploration
council --no-stance "Brainstorm approaches to X"

# Attach file context (files, directories, globs; comma-separated)
council --file "src/**/*.ts,!src/**/*.test.ts" "Review architecture risks"

# Pipe input
cat file.txt | council

# Test a single member or head (also supports --file)
council test <member-id> "prompt"
council test head "prompt" --file src/index.ts
```

## Flags

- `-f, --file <patterns>` — attach file/directory/glob context to the prompt. Supports comma-separated values and repeated flags. Prefix with `!` to exclude (e.g. `!src/**/*.test.ts`). Fails fast on missing paths, zero matches, or files >1 MB.
- `--no-stance` — disable per-member stance mandates, making all members neutral. Preferred for ideation and open-ended exploration. Without this flag, members adopt their configured stances (e.g. Devil's Advocate), which is preferred for critical review of an existing idea or plan.
- `--no-revise` — skip round 2 (revision)
- `--verbose` — print member answers before head synthesis
- `--help` — show usage

## Config

Located at `~/.council/council.json`. Structure:

```json
{
  "members": [
    { "id": "grok", "base_url": "https://...", "model": "...", "api_key": "$ENV_VAR", "timeout": 180 }
  ],
  "head": { "base_url": "https://...", "model": "...", "api_key": "$ENV_VAR" },
  "timeout": 120
}
```

- `api_key`: literal key or `$ENV_VAR` reference
- `stance` (optional, per member): a hard behavioral mandate (e.g. Devil's Advocate) injected as the member's highest-priority instruction. Active by default; disable per run with `--no-stance`.
- `timeout`: per-node overrides global, global overrides default (120s)
- OpenAI/xAI endpoints use Responses API; others use Chat Completions

## Output Contract

- `stdout`: final answer only (+ member blocks with `--verbose`)
- `stderr`: status/progress/errors
- Exit `0` on success, `1` on failure
