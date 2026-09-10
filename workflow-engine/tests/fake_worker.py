#!/usr/bin/env python3
"""Fake harness worker used by the test suite. Never talks to a network or an LLM.

Mode comes from argv[1] (supplied through a route's ``extra_flags``); the prompt
arrives on stdin, so a single route can behave differently per call by embedding
``@@...@@`` markers in the prompt.
"""

import json
import os
import re
import sys
import time
from pathlib import Path


def _count() -> None:
    path = os.environ.get("WFE_FAKE_COUNTER")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("1\n")


def _echo(prompt: str) -> int:
    """Markers: @@SLEEP:n@@, @@FAIL@@, @@EMIT:text@@, @@MARK:path@@."""
    sleep = re.search(r"@@SLEEP:([0-9.]+)@@", prompt)
    if sleep:
        time.sleep(float(sleep.group(1)))
    mark = re.search(r"@@MARK:(.*?)@@", prompt)
    if mark:
        with open(mark.group(1), "a", encoding="utf-8") as fh:
            fh.write("survived\n")
    if "@@FAIL@@" in prompt:
        sys.stdout.write("worker exploded")
        sys.stderr.write("boom\n")
        return 1
    if "@@CWD@@" in prompt:
        sys.stdout.write(os.getcwd())
        return 0
    emit = re.search(r"@@EMIT:(.*?)@@", prompt, re.DOTALL)
    sys.stdout.write(emit.group(1) if emit else prompt.strip())
    return 0


def _flaky(prompt: str, counter: str) -> int:
    """Invalid JSON on the first two attempts, valid on the third."""
    with open(counter, "a", encoding="utf-8") as fh:
        fh.write("1\n")
    with open(counter, encoding="utf-8") as fh:
        attempt = sum(1 for _ in fh)
    if attempt < 3:
        sys.stdout.write("Sure! Here is the data you asked for: n=" + str(attempt))
        return 0
    saw_repair = "REJECTED by schema validation" in prompt
    sys.stdout.write(json.dumps({"n": attempt, "saw_repair": saw_repair}))
    return 0


def _trace(traces: str) -> int:
    with open(traces, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"event": "start", "t": time.monotonic()}) + "\n")
    time.sleep(0.25)
    with open(traces, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"event": "end", "t": time.monotonic()}) + "\n")
    sys.stdout.write("traced")
    return 0


def _research(prompt: str, badskeptic: bool = False, badreview: bool = False, blocker: bool = False, missing_artifact: bool = False, execution_artifacts: bool = False) -> int:
    """Answers the five deep-research prompt shapes with schema-valid payloads."""
    if "You are the skeptic" in prompt and badskeptic:
        sys.stdout.write("not json, sorry")
        return 0
    if "You are scoping a deep-research campaign" in prompt:
        payload = {"branches": [{"name": "branch-x", "status": "thin"}, {"name": "branch-y", "status": "thin"}]}
    elif "planning one pass" in prompt:
        payload = {
            "lanes": [
                {"id": "lane-a", "focus": "origins", "queries": ["origins of X"]},
                {"id": "lane-b", "focus": "critiques", "queries": ["critiques of X"]},
            ]
        }
    elif "You are researcher lane" in prompt:
        sys.stdout.write("Found three sources discussing the topic in depth.")
        return 0
    elif "into claims with evidence" in prompt:
        lane = "lane-a" if "lane 'lane-a'" in prompt else "lane-b"
        payload = {
            "claims": [
                {
                    "claim": f"{lane} claim",
                    "evidence": "quoted passage",
                    "strength": "likely",
                    "citation": f"https://example.com/{lane}",
                }
            ],
            "sources": [
                {"url": f"https://example.com/{lane}?utm_source=x", "status": "extracted", "title": lane},
                {"url": "https://arxiv.org/abs/2401.00001v2", "status": "fetched"},
            ],
        }
    elif "You are the skeptic" in prompt:
        payload = {"rejections": [{"claim_ref": "lane-b:0", "reason": "single secondary source"}],
                   "summary": "one rejection"}
    elif "You are closing a deep-research campaign" in prompt:
        artifact_paths: list[str] = []
        if missing_artifact:
            artifact_paths = ["closing/run-1/verification-artifacts/missing.py", "closing/run-1/verification-artifacts/missing.json"]
        if execution_artifacts:
            artifacts = Path("closing/run-1/verification-artifacts")
            artifacts.mkdir(parents=True, exist_ok=True)
            (artifacts / "check.py").write_text("print(2 + 2)\n", encoding="utf-8")
            (artifacts / "result.json").write_text('{"result": 4}\n', encoding="utf-8")
            artifact_paths = [str(artifacts / "check.py"), str(artifacts / "result.json")]
        payload = {
            "targets": [{
                "target": "verified claim",
                "status": "confirmed",
                "evidence_references": ["sha256:source-a"],
                "execution_claimed": missing_artifact or execution_artifacts,
                "artifact_paths": artifact_paths,
            }],
        }
    elif "Write complete final research report" in prompt:
        sys.stdout.write("# Research report\n\nConfirmed finding [sha256:source-a].")
        return 0
    elif "Perform one final review" in prompt:
        if badreview:
            sys.stdout.write("not json, sorry")
            return 0
        payload = {"status": "confirmed", "blockers": ["unsupported conclusion"] if blocker else [], "material_claims": [], "citation_issues": []}
    else:
        sys.stderr.write(f"unrecognized prompt: {prompt[:120]}\n")
        return 1
    sys.stdout.write(json.dumps(payload))
    return 0


_RALPH_COMPLETE_MARKER = "<promise>COMPLETE</promise>"
_RALPH_PAUSE_MARKER = "<promise>PAUSE</promise>"


def _ralph_complete(_prompt: str) -> int:
    sys.stdout.write(f"Done.\n{_RALPH_COMPLETE_MARKER}")
    return 0


def _ralph_pause(_prompt: str) -> int:
    sys.stdout.write(f"Need help.\n{_RALPH_PAUSE_MARKER}")
    return 0


def _ralph_marker_on_second_call(counter: str, marker: str) -> int:
    """Plain continue text on the first call, then the given marker on every call after."""
    with open(counter, "a", encoding="utf-8") as fh:
        fh.write("1\n")
    with open(counter, encoding="utf-8") as fh:
        call_num = sum(1 for _ in fh)
    if call_num < 2:
        sys.stdout.write("Made progress, continuing.")
    else:
        sys.stdout.write(f"Done.\n{marker}")
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "echo"
    prompt = sys.stdin.read()
    _count()
    if mode == "echo":
        return _echo(prompt)
    if mode == "flaky":
        return _flaky(prompt, sys.argv[2])
    if mode == "trace":
        return _trace(sys.argv[2])
    if mode == "research":
        badskeptic = len(sys.argv) > 2 and sys.argv[2] == "badskeptic"
        return _research(prompt, badskeptic)
    if mode == "close-timeout":
        time.sleep(0.2)
        return _research(prompt)
    if mode == "badclose-review":
        return _research(prompt, badreview=True)
    if mode == "close-blocker":
        return _research(prompt, blocker=True)
    if mode == "close-missing-artifact":
        return _research(prompt, missing_artifact=True)
    if mode == "close-execution-artifacts":
        return _research(prompt, execution_artifacts=True)
    if mode == "ralph-complete":
        return _ralph_complete(prompt)
    if mode == "ralph-pause":
        return _ralph_pause(prompt)
    if mode == "ralph-continue-then-complete":
        return _ralph_marker_on_second_call(sys.argv[2], _RALPH_COMPLETE_MARKER)
    if mode == "ralph-continue-then-pause":
        return _ralph_marker_on_second_call(sys.argv[2], _RALPH_PAUSE_MARKER)
    sys.stderr.write(f"unknown fake mode: {mode}\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
