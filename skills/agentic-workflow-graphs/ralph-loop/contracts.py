"""Ralph-loop domain contracts: markers, task-file parsing, state, prompt, verification.

Pure functions, no engine import. Ported from the Pi extension at
the pi-ralph-wiggum extension (index.ts, protocol.ts) -- harness-agnostic here: no
sessions, no child extensions/tools/model, no `.log.jsonl` (the engine journal covers that).
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

COMPLETE_MARKER = "<promise>COMPLETE</promise>"
PAUSE_MARKER = "<promise>PAUSE</promise>"

_SECTION_RE = re.compile(r"^##\s+Verification\s*$(.*?)(?=^##\s+|\Z)", re.IGNORECASE | re.MULTILINE | re.DOTALL)
_FENCED_RE = re.compile(r"```(?:bash|sh|shell)?\s*\n(.*?)```", re.DOTALL)
_COMMAND_LINE_RE = re.compile(r"^\s*command\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_FALLBACK_RE = re.compile(r"^\s*(?:verification|verify|command)\b\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)


def safe_name(name: str) -> str:
    """Same regex as index.ts: collapse anything but [a-zA-Z0-9_-] to underscores."""
    return re.sub(r"_+", "_", re.sub(r"[^a-zA-Z0-9_-]", "_", name))


def child_directive(text: str) -> str:
    """"pause" | "complete" | "continue". Pause wins when both markers appear."""
    if PAUSE_MARKER in text:
        return "pause"
    if COMPLETE_MARKER in text:
        return "complete"
    return "continue"


def parse_verification_command(task_content: str) -> str | None:
    """Port of index.ts parseVerificationCommand: prefer a `## Verification` section's
    fenced bash block, then its `command:` line; fall back to a top-level
    verification|verify|command: line anywhere in the task file."""
    section_match = _SECTION_RE.search(task_content)
    section = section_match.group(1) if section_match else ""
    if section:
        fenced_match = _FENCED_RE.search(section)
        if fenced_match:
            fenced = fenced_match.group(1).strip()
            if fenced:
                return fenced
        command_match = _COMMAND_LINE_RE.search(section)
        if command_match:
            command = command_match.group(1).strip()
            if command:
                return command
    fallback_match = _FALLBACK_RE.search(task_content)
    return fallback_match.group(1).strip() if fallback_match else None


def load_state(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict[str, Any]) -> None:
    state["updatedAt"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def append_reflection(path: Path, iteration: int, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n\n## Iteration {iteration}\n\n{text}\n")


def append_verification_note(path: Path, passed: bool, command: str | None, output: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if command is None:
        block = "\n\n### Verification failed\n\nNo verification command found.\n"
    else:
        status = "passed" if passed else "failed"
        block = f"\n\n### Verification {status}\n\nCommand: {command}\n\n```\n{output}\n```\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(block)


def build_prompt(state: dict[str, Any], task_content: str, reflection: str) -> str:
    """Port of index.ts buildPrompt, nearly verbatim: same 7 instructions, same marker rules."""
    verification_command = parse_verification_command(task_content) or "No verification command found."
    max_iterations = state["maxIterations"]
    of_max = f" of {max_iterations}" if max_iterations > 0 else ""
    return f"""# Ralph Loop Fresh-Context Iteration

You are iteration {state["iteration"]}{of_max} for loop "{state["name"]}".

Core rule: work from durable files only. Parent chat history is unavailable by design.

## Task File ({state["taskFile"]})

{task_content}

## Durable Reflection / Recent Notes

{reflection or "No reflection yet."}

## Verification Command

{verification_command}

## Instructions

1. Work autonomously on the next useful task from the task file.
2. Update {state["taskFile"]} with progress.
3. Update notes/checklist in durable files when useful.
4. Follow commit instructions from the task file, if any.
5. If the entire task is complete, include exactly: {COMPLETE_MARKER}
6. If task protocol requires immediate human intervention, include exactly: {PAUSE_MARKER}
7. Otherwise, stop after meaningful progress and summarize what changed.

Never emit both markers. Pause takes precedence if both appear. Do not ask for human input unless pausing. Preserve momentum."""


def run_verification(command: str, cwd: Path, timeout_s: float = 600) -> tuple[bool, str]:
    """Run the verification command via `sh -c`, capturing stdout+stderr. Exit 0 -> passed."""
    try:
        proc = subprocess.run(
            ["sh", "-c", command],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        return proc.returncode == 0, (proc.stdout + proc.stderr).strip()
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        return False, f"{stdout}{stderr}\ntimed out after {timeout_s:g}s".strip()
