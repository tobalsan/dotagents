"""Ralph loop as a wfe workflow script: fresh-context iteration over durable `.ralph/<name>`
files until the child emits the completion marker and verification passes, or it pauses.

Ported from the Pi extension's runLoop/startLoop (index.ts) into a harness-agnostic wfe
workflow -- one agent() call per iteration, one route ("worker"). Resume truth lives in
state.json's iteration counter, not engine call replay: the prompt embeds the reflection
file, so its content -- and therefore its call_key -- changes every iteration and would
never hit the replay map anyway.

Run with:
    wfe run workflow.py \
        --campaign WORKDIR/.ralph --workdir WORKDIR --arg name=<loop-name>
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Load contracts.py by file path rather than `import contracts`: multiple wfe skills each
# ship a same-named contracts.py/workflow.py, and a bare import would silently bind to
# whichever one another already-loaded workflow happened to cache under that module name.
_HERE = Path(__file__).resolve().parent
_contracts_spec = importlib.util.spec_from_file_location("ralph_loop_contracts", _HERE / "contracts.py")
assert _contracts_spec and _contracts_spec.loader
contracts = importlib.util.module_from_spec(_contracts_spec)
sys.modules[_contracts_spec.name] = contracts
_contracts_spec.loader.exec_module(contracts)

from workflow_engine import AgentError, Ctx, agent, phase

DEFAULT_MAX_ITERATIONS = 50
DEFAULT_PAUSE_THRESHOLD = 3


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _summary(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": state["name"],
        "status": state["status"],
        "iterations": state["iteration"],
        "verification_passed": state.get("lastVerificationPassed"),
    }


async def run(args: dict[str, str], ctx: Ctx) -> dict[str, Any]:
    name = contracts.safe_name(args["name"])
    max_iterations = int(args.get("max_iterations", str(DEFAULT_MAX_ITERATIONS)))
    pause_threshold = int(args.get("pause_threshold", str(DEFAULT_PAUSE_THRESHOLD)))

    ralph_dir = ctx.campaign_dir
    workdir = ctx.workdir
    task_path = ralph_dir / f"{name}.md"
    state_path = ralph_dir / f"{name}.state.json"
    reflection_path = ralph_dir / f"{name}.reflection.md"

    if not task_path.is_file():
        # The workflow never creates placeholders -- the host agent writes the task file
        # (Goal / Checklist / Verification / Commit / Notes) before running the loop.
        raise AgentError(
            f"ralph-{name}-missing-task",
            "workflow",
            f"task file not found: {task_path} -- write it before running the loop",
        )

    state = contracts.load_state(state_path)
    if state is None:
        now = _now()
        state = {
            "name": name,
            "taskFile": str(task_path),
            "status": "active",
            "iteration": 1,
            "maxIterations": max_iterations,
            "startedAt": now,
            "updatedAt": now,
        }
    elif state["status"] == "completed":
        ctx.log(f"ralph loop {name} already completed at iteration {state['iteration']}")
        return _summary(state)
    elif state["status"] == "paused":
        # `wfe run` again on a paused loop is `/ralph resume`: flip to active and keep
        # looping from the stored iteration. Persist immediately so dashboards don't
        # show the stale paused status and error for the whole first iteration.
        # Adopt the current max_iterations arg so a loop paused at the cap can be
        # resumed with a raised ceiling.
        state["status"] = "active"
        state["lastError"] = None
        state["maxIterations"] = max_iterations
        state["blockedStreak"] = 0
        contracts.save_state(state_path, state)

    while True:
        if state["maxIterations"] > 0 and state["iteration"] > state["maxIterations"]:
            state["status"] = "paused"
            state["lastError"] = f"Max iterations reached without verified completion ({state['maxIterations']})."
            contracts.save_state(state_path, state)
            ctx.log(f"ralph loop {name} paused: {state['lastError']}")
            break

        if not task_path.is_file():
            state["status"] = "paused"
            state["lastError"] = f"Could not read task file: {task_path}"
            contracts.save_state(state_path, state)
            break
        task_content = task_path.read_text(encoding="utf-8")
        reflection = reflection_path.read_text(encoding="utf-8") if reflection_path.is_file() else ""

        with phase(f"iteration {state['iteration']}"):
            try:
                text = await agent(
                    contracts.build_prompt(state, task_content, reflection),
                    route="worker",
                    label=f"iter-{state['iteration']}",
                )
                error_message = None
            except AgentError as exc:
                text = ""
                error_message = exc.message

        contracts.append_reflection(reflection_path, state["iteration"], text or error_message or "No assistant text.")

        directive = "pause" if error_message else contracts.child_directive(text)
        if directive == "pause":
            blocker = error_message or "Child requested pause. See reflection for diagnostics."
            streak = state.get("blockedStreak", 0) + 1
            state["blockedStreak"] = streak
            state["lastError"] = blocker
            if streak >= pause_threshold:
                state["status"] = "paused"
                state["lastError"] = f"{blocker} (blocked {streak} consecutive iterations)"
                contracts.save_state(state_path, state)
                ctx.log(f"ralph loop {name} paused: {state['lastError']}")
                break
            ctx.log(f"ralph loop {name} blocked ({streak}/{pause_threshold}); continuing with fresh context")
            contracts.append_reflection(
                reflection_path,
                state["iteration"],
                f"[loop] Iteration blocked ({streak}/{pause_threshold}). Blocker: {blocker}\n\n"
                "Next iteration: diagnose and attempt to resolve this blocker first, then continue the task.",
            )
        else:
            state["blockedStreak"] = 0
            state["lastError"] = None
            if directive == "complete":
                latest_task_content = task_path.read_text(encoding="utf-8") if task_path.is_file() else task_content
                verification_command = contracts.parse_verification_command(latest_task_content)
                state["lastVerificationCommand"] = verification_command
                if verification_command is None:
                    state["lastVerificationPassed"] = False
                    state["lastVerificationOutput"] = "Completion marker emitted but no verification command found."
                    contracts.append_verification_note(reflection_path, False, None, "")
                else:
                    passed, output = contracts.run_verification(verification_command, workdir)
                    output = output[-4000:]
                    state["lastVerificationPassed"] = passed
                    state["lastVerificationOutput"] = output
                    contracts.append_verification_note(reflection_path, passed, verification_command, output)
                    if passed:
                        state["status"] = "completed"
                        state["completedAt"] = _now()
                        contracts.save_state(state_path, state)
                        ctx.log(f"ralph loop {name} complete at iteration {state['iteration']}")
                        break

        state["iteration"] += 1
        contracts.save_state(state_path, state)

    return _summary(state)
