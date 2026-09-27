#!/usr/bin/env bash
# Publish a static artifact to Cloudflare Pages as a branch deployment.
# Usage: publish.sh <file.html | dir> [--slug <name>]
# Prints the public URL on stdout; everything else goes to stderr.
set -euo pipefail

die() { echo "publish-artifact: $*" >&2; exit 1; }

[[ $# -ge 1 ]] || die "usage: publish.sh <file.html|dir> [--slug <name>]"
SRC="$1"; shift
SLUG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --slug) SLUG="${2:-}"; shift 2 ;;
    *) die "unknown argument: $1" ;;
  esac
done

: "${CLOUDFLARE_API_TOKEN:?publish-artifact: missing CLOUDFLARE_API_TOKEN}"
: "${CLOUDFLARE_ACCOUNT_ID:?publish-artifact: missing CLOUDFLARE_ACCOUNT_ID}"
PROJECT="${ARTIFACTS_PROJECT:-artifacts}"
command -v npx >/dev/null || die "npx not found (Node.js is required)"

# Stage the files: a single .html becomes index.html in a temp dir.
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
if [[ -f "$SRC" ]]; then
  cp "$SRC" "$TMP/index.html"
  DIR="$TMP"
elif [[ -d "$SRC" ]]; then
  [[ -f "$SRC/index.html" ]] || die "no index.html in $SRC"
  DIR="$SRC"
else
  die "not found: $SRC"
fi

# Slug: random 8 chars unless given. Pages lowercases and hyphenates branch
# names for the alias URL, so normalise it the same way up front.
if [[ -z "$SLUG" ]]; then
  SLUG="$(LC_ALL=C tr -dc 'a-z0-9' </dev/urandom | head -c 8 || true)"
fi
SLUG="$(echo "$SLUG" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g' | cut -c1-20)"
[[ -n "$SLUG" && "$SLUG" != "main" ]] || die "invalid slug"

echo "publishing $SRC -> branch '$SLUG' of project '$PROJECT'" >&2
OUT="$(npx --yes wrangler@4 pages deploy "$DIR" \
  --project-name "$PROJECT" --branch "$SLUG" --commit-dirty=true 2>&1)" \
  || { echo "$OUT" >&2; die "wrangler deploy failed"; }
echo "$OUT" >&2

# Prefer the stable branch alias URL; fall back to the per-deploy URL.
URL="$(echo "$OUT" | grep -Eo "https://${SLUG}\.[a-z0-9.-]+\.pages\.dev" | head -n1 || true)"
[[ -n "$URL" ]] || URL="$(echo "$OUT" | grep -Eo 'https://[a-z0-9.-]+\.pages\.dev' | tail -n1 || true)"
[[ -n "$URL" ]] || die "deployed, but could not find the URL in wrangler output"
echo "$URL"
