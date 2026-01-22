---
name: browser-tools
description: CDP-based Chrome automation for UI debugging and web interaction. Use it when you need to automate chrome browser to perform real browser tasks and debug UIs.
---

# Browser Tools

CDP-based Chrome automation for UI debugging and web interaction.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `start` | Launch Chrome with remote debugging |
| `nav` | Navigate to URL |
| `eval` | Execute JavaScript in page |
| `screenshot` | Capture viewport |
| `pick` | Interactive element selector |
| `console` | Capture console logs |
| `content` | Extract readable text as markdown |
| `search` | Google search with optional content |
| `cookies` | Dump cookies as JSON |
| `inspect` | List Chrome instances and tabs |
| `kill` | Terminate Chrome instances |

## Commands

### start
```bash
./scripts/start.js                          # Fresh profile on :9222
./scripts/start.js --copy-existing-profile  # Copy user profile (cookies/logins) if requested by user
./scripts/start.js --port 9333              # Custom port
./scripts/start.js --kill-existing          # Kill running Chrome first
```
**Important:** Do NOT use `--copy-existing-profile` unless the user explicitly requests it.

### nav
```bash
./scripts/nav.js https://example.com       # Current tab
./scripts/nav.js https://example.com --new # New tab
```

### eval
```bash
./scripts/eval.js 'document.title'
./scripts/eval.js 'document.querySelectorAll("button").length'
./scripts/eval.js '[...document.querySelectorAll("a")].map(a => ({text: a.textContent.trim(), href: a.href}))'
```
Returns objects/arrays formatted as key-value pairs. Use `--pretty` for indented output.

### screenshot
```bash
./scripts/screenshot.js              # Viewport screenshot, prints path
```

### pick
```bash
./scripts/pick.js "Select the login button"
```
Interactive: click to select, Cmd/Ctrl+click for multi-select, Enter to finish, ESC to cancel.
Returns: tag, id, class, text, html, parents.

### console
```bash
./scripts/console.js                      # Capture 5 seconds
./scripts/console.js --timeout 10         # Capture 10 seconds
./scripts/console.js --follow             # Continuous (Ctrl+C to stop)
./scripts/console.js --types error,warn   # Filter by type
```
Types: log, error, warn, info, debug, pageerror

### content
```bash
./scripts/content.js https://example.com
./scripts/content.js https://example.com --timeout 15
```
Extracts readable content as markdown using Readability.js + Turndown.

### search
```bash
./scripts/search.js "react hooks tutorial"
./scripts/search.js "node.js streams" -n 10        # 10 results
./scripts/search.js "api docs" --content           # Include page content
```

### cookies
```bash
./scripts/cookies.js    # JSON array of cookies from active tab
```

### inspect
```bash
./scripts/inspect.js           # List all Chrome instances with DevTools ports
./scripts/inspect.js --json    # Machine-readable output
```

### kill
```bash
./scripts/kill.js --all              # Kill all debuggable Chrome instances
./scripts/kill.js --ports 9222,9333  # Kill specific ports
./scripts/kill.js --pids 1234,5678   # Kill specific PIDs
./scripts/kill.js --force            # Skip confirmation
```

## Common Options

All commands except `start`, `inspect`, `kill` accept:
- `--port <number>` - DevTools port (default: 9222)

## Workflow Example

```bash
./scripts/start.js --profile
./scripts/nav.js http://localhost:3000
./scripts/console.js --follow &
./scripts/screenshot.js
./scripts/eval.js 'document.querySelector("#submit").click()'
./scripts/content.js http://localhost:3000/result
```
