#!/usr/bin/env bash
# ralph_codex.sh
#
# Usage:
#   ./ralph_codex.sh <iterations> [workdir] [prompt_file]
#
# Examples:
#   ./ralph_codex.sh 10
#   ./ralph_codex.sh 10 ./my-project
#   ./ralph_codex.sh 10 ./my-project ./prompts/ralph.md
#
# Requires:
#   - codex CLI in PATH

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <iterations> [workdir] [prompt_file]"
  exit 1
fi

ITERATIONS="$1"
WORKDIR="${2:-$(pwd)}"
PROMPT_FILE="${3:-prompt.md}"
MODEL="${RALPH_MODEL:-o3}"
MAX_RETRIES="${RALPH_MAX_RETRIES:-3}"
RETRY_DELAY="${RALPH_RETRY_DELAY:-2}"

cd "$WORKDIR" || {
  echo "Error: cannot cd into $WORKDIR"
  exit 1
}

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "Error: prompt file not found: $PROMPT_FILE"
  exit 1
fi

LOG_DIR="${WORKDIR}/.ralph-logs"
mkdir -p "$LOG_DIR"

extract_result() {
  # Extract the last assistant message from codex JSONL output.
  python3 - "$1" <<'PY'
import json,sys
path=sys.argv[1]
last_message=""
try:
    with open(path,"r",errors="ignore") as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            try:
                obj=json.loads(line)
            except Exception:
                continue
            # Codex outputs various event types; look for assistant messages
            msg_type = obj.get("type","")
            if msg_type == "message" and obj.get("role") == "assistant":
                content = obj.get("content", [])
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "output_text":
                        last_message = block.get("text", "")
            elif msg_type == "assistant":
                # Alternative format
                message = obj.get("message", {})
                content = message.get("content", [])
                for block in content:
                    if isinstance(block, dict) and block.get("type") in ("text", "output_text"):
                        last_message = block.get("text", "")
    sys.stdout.write(last_message)
except FileNotFoundError:
    pass
PY
}

run_codex() {
  local attempt=1
  local status=0
  local result_text=""

  while (( attempt <= MAX_RETRIES )); do
    local err_file="${LOG_DIR}/iter-${i}-attempt-${attempt}.err"
    local out_file="${LOG_DIR}/iter-${i}-attempt-${attempt}.out"
    local stream_file="${LOG_DIR}/iter-${i}-attempt-${attempt}.stream.jsonl"

    : > "$stream_file"
    result_text=""

    local prompt
    prompt="$(<"$PROMPT_FILE")"

    set +e
    codex \
      --yolo \
      exec \
      --json \
      -m "$MODEL" \
      -C "$WORKDIR" \
      "$prompt" \
      > "$stream_file" 2> "$err_file"
    status=$?
    set -e

    result_text="$(extract_result "$stream_file")"
    result="$result_text"
    printf '%s' "$result_text" > "$out_file"

    if [[ $status -eq 0 && -n "$result_text" ]]; then
      return 0
    fi

    if [[ $status -ne 0 ]]; then
      echo "codex failed (attempt $attempt/$MAX_RETRIES, exit $status). See $err_file and $stream_file" >&2
    else
      echo "codex returned empty result (attempt $attempt/$MAX_RETRIES). See $stream_file" >&2
    fi

    sleep "$RETRY_DELAY"
    attempt=$((attempt + 1))
  done

  return 1
}

for ((i=1; i<=ITERATIONS; i++)); do
  echo "=== Ralph iteration $i/$ITERATIONS (cwd: $WORKDIR) ==="

  result=""
  if ! run_codex; then
    echo "Skipping iteration $i due to repeated codex failures." >&2
    continue
  fi

  echo "$result"

  if [[ "$result" == *"<promise>COMPLETE</promise>"* ]]; then
    echo "Scope complete, exiting."
    exit 0
  fi

  if [[ "$result" == *"<promise>END_OF_STORY</promise>"* ]]; then
    echo "Iteration complete."
  fi
done
