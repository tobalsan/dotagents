---
name: tailscale-preview
description: Expose a local dev server over Tailscale for previewing from another device on the same tailnet. Use when you need to share a local preview (web app, API, dashboard) with a teammate or access it from a different machine. Handles port selection, existing config preservation, multi-endpoint setups, and cleanup.
---

# Tailscale Preview

Expose local dev servers to other devices on the same Tailscale tailnet using `tailscale serve`. No SSH tunnels, no port forwarding, no router config.

## Prerequisites

- Tailscale installed and connected (`tailscale status`)
- The local service must be running and listening on `127.0.0.1`

## Before You Start

**Always check existing serve config first** to avoid clobbering:

```bash
tailscale serve status
```

Note what's already mapped. Never remove or overwrite existing entries.

## Find an Available Port

Pick an HTTPS port that isn't already used by Tailscale or any local service:

```bash
# Check which ports tailscale is already using (parse from serve status)
tailscale serve status

# Check a candidate port is free locally too
lsof -i :<port> || echo "port free"
```

Common convention: use 8443, 8444, 8445, etc. for previews.

## Simple Case: Single Service

For a basic web app, API, or dashboard running on one port:

```bash
tailscale serve --bg --https <ts-port> http://127.0.0.1:<local-port>
```

Access at: `https://<hostname>.<tailnet>:<ts-port>`

Example — a Vite dev server on port 5173:

```bash
tailscale serve --bg --https 8443 http://127.0.0.1:5173
```

## Complex Case: Multi-Endpoint Setup

When the app has multiple components (e.g., a web UI that proxies API/WebSocket calls to a separate backend), you need multiple path-based routes on the same Tailscale port — otherwise API calls and WebSocket connections will fail.

```bash
# Web UI at root
tailscale serve --bg --https <ts-port> --set-path / http://127.0.0.1:<ui-port>

# API backend
tailscale serve --bg --https <ts-port> --set-path /api http://127.0.0.1:<backend-port>/api

# WebSocket endpoint
tailscale serve --bg --https <ts-port> --set-path /ws http://127.0.0.1:<backend-port>/ws
```

This ensures the browser hits the web UI at `/`, but `/api/*` and `/ws` requests route directly to the backend — bypassing the UI server's proxy layer.

**When do you need this?**
- The web UI and backend run on different ports
- The app uses WebSockets (Tailscale serve supports WS proxying, but the path must be explicit)
- The UI dev server (e.g., Vite) proxies `/api` to the backend — but you want Tailscale to handle it directly for reliability

## Vite Dev Server: allowedHosts

Vite blocks requests from unknown hostnames by default. If you see `"This host is not allowed"`, you need to add the Tailscale hostname:

- **CLI flag:** `--allowed-hosts <hostname>`
- **vite.config.ts:** `server: { allowedHosts: ["<hostname>.<tailnet>"] }`
- **Nuclear option:** `server: { allowedHosts: true }` (allows all — fine for dev)

The hostname is your machine's Tailscale MagicDNS name, e.g., `my-machine.tail12345.ts.net`.

## Cleanup After Preview

When the preview session is done, **always clean up** — don't leave stale serve configs around.

### 1. Remove the Tailscale serve config

Remove the entire port:

```bash
tailscale serve --https <ts-port> off
```

Or remove individual paths if you only own some of them:

```bash
tailscale serve --https <ts-port> --set-path /some-path off
```

### 2. Kill the local dev processes

Stop any services you started for the preview:

```bash
# Kill by port
kill $(lsof -ti :<port>) 2>/dev/null
```

Watch for orphaned child processes (e.g., Slack bots, WebSocket servers) that survive after the main process dies — they hold ports open:

```bash
# Verify ports are actually free
lsof -i :<port> || echo "free"
```

### 3. Revert any temporary config changes

If you modified `vite.config.ts` (e.g., `allowedHosts`) or other config files for the preview, revert them:

```bash
git checkout <file>
```

### 4. Verify

```bash
tailscale serve status
```

Confirm only the pre-existing entries remain — nothing you added should be left.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Refused to connect" | Local service not running | Start/restart the service |
| Blank page, 404 on assets | Subpath serving without `base` config | Use a dedicated port instead of a subpath, or set `base` in build tool |
| WebSocket errors | WS path not explicitly mapped | Add `--set-path /ws` pointing to backend |
| API 502 Bad Gateway | Backend not running or wrong port | Verify backend is listening on the expected port |
| "Host not allowed" (Vite) | Vite's `allowedHosts` check | Add tailnet hostname to allowedHosts |
| Port conflict | Orphaned processes from previous runs | `kill $(lsof -ti :<port>)` then retry |
