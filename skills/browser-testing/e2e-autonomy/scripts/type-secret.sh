#!/usr/bin/env bash
# Type a 1Password secret into the current page of a buu session.
# The value goes through a pipe only: not argv, not stdout, not a file.
# Usage: type-secret.sh <op-ref> <locator-js>
#   type-secret.sh "op://Agents/<item-id>/password" "page.getByLabel('Password')"
# Uses $BUU_SESSION (or pass --session through BUU_ARGS="--session x").
set -euo pipefail
[ $# -eq 2 ] || { echo "usage: type-secret.sh <op-ref> <locator-js>" >&2; exit 2; }
ref=$1
loc=$2
# op prints only the value; $(...) drops the final newline.
val=$(op read "$ref") || { echo "type-secret: op read failed for $ref" >&2; exit 1; }
json=$(printf '%s' "$val" | jq -Rs .)
unset val
# Line 1 holds the value. Errors point at line 2, so the value is never shown.
{
  printf 'const __v = %s;\n' "$json"
  printf 'await (%s).pressSequentially(__v, {delay: 60});\n' "$loc"
} | buu js ${BUU_ARGS:-} >/dev/null
echo "type-secret: typed $ref"
