---
name: publish-artifact
description: Publish a static HTML/CSS/JS artifact (a single .html file or a folder with index.html) to a public URL on Cloudflare Pages. Use when you have built a web page, demo, report or visualization and need a shareable link.
---

# Publish artifact

Publishes static files to Cloudflare Pages and prints a public URL like
`https://k3x9q2m7.<project>.pages.dev`. Every publish is its own branch
deployment, so artifacts never overwrite each other.

## Usage

```bash
scripts/publish.sh <path> [--slug <name>]
```

- `<path>`: a single `.html` file, or a directory containing `index.html`
  (plus any css/js/images it references, using relative paths).
- `--slug <name>`: optional. Reuse the same slug to update an artifact in
  place at the same URL. Omit it to get a new random id.

The script prints **only the URL** on stdout on success. Give that URL to the
user. Logs go to stderr.

## Unpublishing

```bash
scripts/unpublish.mjs <slug> [--dry-run]
```

Deletes every deployment of that slug: the alias URL and all older per-deploy
hash URLs. Only unpublish when the user asks, and use `--dry-run` first if
unsure which slug is meant. Exit code 3 means nothing was found for that slug.

Note: republishing a slug leaves older versions reachable at their
`<hash>.<project>.pages.dev` URLs until the slug is unpublished.

## Rules

- Only publish self-contained static files. No server code, no build step:
  deploy what the browser should load.
- Never include secrets, API keys, tokens or private data in the published
  files. Everything published is publicly reachable by anyone with the link.
- Use relative paths for assets (`./app.js`, not `/app.js` or `file://`).
- Slugs: lowercase letters, digits and hyphens, at most 20 characters.
  Never use `main` (reserved for the production branch).
- Search indexing is already blocked: Cloudflare adds `X-Robots-Tag: noindex`
  to every preview deployment. A `<meta name="robots" content="noindex">`
  tag is fine but not required.

## Environment (set by the runtime, not by you)

| Variable | Purpose |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Token with *Account → Cloudflare Pages → Edit* |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account id |
| `ARTIFACTS_PROJECT` | Pages project name (default `artifacts`) |

Requires Node.js (the script runs wrangler through `npx`).

## Errors

- `missing CLOUDFLARE_API_TOKEN` / `ACCOUNT_ID`: report to the user; do not
  try to log in interactively.
- `Project not found`: the Pages project hasn't been created; report it.
- `no index.html`: the directory must contain `index.html` at its root.
