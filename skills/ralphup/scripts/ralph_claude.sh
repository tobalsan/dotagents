#!/usr/bin/env bash
# ralph.sh
#
# Usage:
#   ./ralph.sh <iterations> [workdir] [prompt_file]
#
# Examples:
#   ./ralph.sh 10
#   ./ralph.sh 10 ./my-project
#   ./ralph.sh 10 ./my-project ./prompts/ralph.md
#
# Requires:
#   - claude CLI in PATH

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <iterations> [workdir] [prompt_file]"
  exit 1
fi

ITERATIONS="$1"
WORKDIR="${2:-$(pwd)}"
PROMPT_FILE="${3:-prompt.md}"
MODEL="opus"
MAX_RETRIES="${RALPH_MAX_RETRIES:-3}"
RETRY_DELAY="${RALPH_RETRY_DELAY:-2}"
KILL_GRACE_SECONDS="${RALPH_KILL_GRACE_SECONDS:-2}"
STREAM_VERBOSE="${RALPH_STREAM_VERBOSE:-1}"

cd "$WORKDIR" || {
  echo "Error: cannot cd into $WORKDIR"
  exit 1
}

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "Error: prompt file not found: $PROMPT_FILE"
  exit 1
fi

unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN

LOG_DIR="${WORKDIR}/.ralph-logs"
mkdir -p "$LOG_DIR"

extract_result() {
  # Extract the first stream-json result payload (assistant text).
  # Uses python to avoid jq dependency.
  python3 - "$1" <<'PY'
import json,sys
path=sys.argv[1]
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
            if obj.get("type")=="result":
                result=obj.get("result") or ""
                sys.stdout.write(result)
                break
except FileNotFoundError:
    pass
PY
}

run_claude() {
  local attempt=1
  local status=0
  local result_received=false
  local result_text=""

  while (( attempt <= MAX_RETRIES )); do
    local err_file="${LOG_DIR}/iter-${i}-attempt-${attempt}.err"
    local out_file="${LOG_DIR}/iter-${i}-attempt-${attempt}.out"
    local stream_file="${LOG_DIR}/iter-${i}-attempt-${attempt}.stream.jsonl"
    local killer_pid=""

    unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN

    : > "$stream_file"
    result_received=false
    result_text=""

    local prompt
    prompt="$(<"$PROMPT_FILE")"

    # stream-json emits a {"type":"result"} before the hang; kill after we see it.
    # Use a named pipe for bash 3.2 compatibility (no coproc)
    local fifo="${LOG_DIR}/iter-${i}-attempt-${attempt}.fifo"
    rm -f "$fifo"
    mkfifo "$fifo"

    set +e
    if [[ "$STREAM_VERBOSE" == "1" ]]; then
      claude \
        --dangerously-skip-permissions \
        --model "$MODEL" \
        --output-format stream-json \
        --verbose \
        -p "$prompt" 2> "$err_file" > "$fifo" &
    else
      claude \
        --dangerously-skip-permissions \
        --model "$MODEL" \
        --output-format stream-json \
        -p "$prompt" 2> "$err_file" > "$fifo" &
    fi
    local claude_pid=$!
    set -e

    while IFS= read -r line < "$fifo"; do
      echo "$line" >> "$stream_file"
      if [[ "$line" == *'"type":"result"'* ]]; then
        result_received=true
        ( sleep "$KILL_GRACE_SECONDS"; kill "$claude_pid" 2>/dev/null ) &
        killer_pid=$!
        break
      fi
    done

    set +e
    wait "$claude_pid" 2>/dev/null
    status=$?
    set -e

    rm -f "$fifo"

    if [[ -n "$killer_pid" ]]; then
      kill "$killer_pid" 2>/dev/null || true
    fi

    result_text="$(extract_result "$stream_file")"
    result="$result_text"
    printf '%s' "$result_text" > "$out_file"

    if [[ "$result_received" == true && -n "$result_text" ]]; then
      return 0
    fi

    if [[ "$result_received" != true ]]; then
      echo "claude produced no result (attempt $attempt/$MAX_RETRIES, exit $status). See $err_file and $stream_file" >&2
    else
      echo "claude returned empty result (attempt $attempt/$MAX_RETRIES). See $stream_file" >&2
    fi

    sleep "$RETRY_DELAY"
    attempt=$((attempt + 1))
  done

  return 1
}

for ((i=1; i<=ITERATIONS; i++)); do
  echo "=== Ralph iteration $i/$ITERATIONS (cwd: $WORKDIR) ==="

  result=""
  if ! run_claude; then
    echo "Skipping iteration $i due to repeated claude failures." >&2
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
