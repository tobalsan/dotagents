"""Process spawning and per-CLI harness adapters.

Builds argv for each headless CLI ("claude", "codex", "pi", "opencode", "fake"),
spawns the subprocess, and parses raw stdout into a normalized HarnessResult.
Imports nothing from engine.py.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import os
import pathlib
import signal
import typing


@dataclasses.dataclass(frozen=True)
class Route:
    harness: str
    model: str | None = None
    extra_flags: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class HarnessResult:
    text: str
    exit: int
    cost_hint: float | None


class Adapter(typing.Protocol):
    name: str

    def command(self, route: Route, prompt: str) -> tuple[list[str], str | None]: ...
    def parse(self, stdout: str, stderr: str, exit_code: int) -> HarnessResult: ...
    # Optional: an adapter MAY additionally define
    #   def env(self, route: Route, call_dir: pathlib.Path) -> dict[str, str] | None: ...
    # to inject extra environment for one subprocess call (merged over os.environ; not part of
    # the Protocol so existing adapters need no change). `spawn` looks it up with
    # getattr(adapter, "env", None) and creates nothing itself — the adapter owns call_dir.


def _json_lines(stdout: str) -> list[dict]:
    events = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            events.append(obj)
    return events


class ClaudeAdapter:
    name = "claude"

    def command(self, route: Route, prompt: str) -> tuple[list[str], str | None]:
        argv = ["claude", "-p", "--output-format", "json"]
        if route.model:
            argv += ["--model", route.model]
        argv += list(route.extra_flags)
        return argv, prompt

    def parse(self, stdout: str, stderr: str, exit_code: int) -> HarnessResult:
        try:
            obj = json.loads(stdout)
        except json.JSONDecodeError:
            return HarnessResult(text="", exit=exit_code or 1, cost_hint=None)
        text = obj.get("result", "")
        cost_hint = obj.get("total_cost_usd")
        if obj.get("is_error") is True or obj.get("subtype") != "success":
            return HarnessResult(text=text, exit=1, cost_hint=cost_hint)
        return HarnessResult(text=text, exit=exit_code, cost_hint=cost_hint)


class CodexAdapter:
    name = "codex"

    def command(self, route: Route, prompt: str) -> tuple[list[str], str | None]:
        argv = ["codex", "exec", "--json", "--skip-git-repo-check", "-s", "read-only"]
        if route.model:
            argv += ["-m", route.model]
        argv += list(route.extra_flags)
        argv += ["-"]
        return argv, prompt

    def parse(self, stdout: str, stderr: str, exit_code: int) -> HarnessResult:
        text = None
        failed = False
        for obj in _json_lines(stdout):
            if obj.get("type") == "item.completed":
                item = obj.get("item", {})
                if item.get("type") == "agent_message":
                    text = item.get("text", "")
            elif obj.get("type") == "turn.failed":
                failed = True
        if failed or text is None:
            return HarnessResult(text="", exit=exit_code or 1, cost_hint=None)
        return HarnessResult(text=text, exit=exit_code, cost_hint=None)


class PiAdapter:
    name = "pi"

    def command(self, route: Route, prompt: str) -> tuple[list[str], str | None]:
        argv = ["pi", "-p", "--mode", "json"]
        if route.model:
            argv += ["--model", route.model]
        argv += list(route.extra_flags)
        return argv, prompt

    def parse(self, stdout: str, stderr: str, exit_code: int) -> HarnessResult:
        text = None
        cost_hint = None
        for obj in _json_lines(stdout):
            if obj.get("type") != "message_end":
                continue
            message = obj.get("message", {})
            if message.get("role") != "assistant":
                continue
            content = message.get("content", [])
            text = "".join(p.get("text", "") for p in content if p.get("type") == "text")
            cost_hint = message.get("usage", {}).get("cost", {}).get("total")
        if text is None:
            return HarnessResult(text="", exit=exit_code or 1, cost_hint=None)
        return HarnessResult(text=text, exit=exit_code, cost_hint=cost_hint)


class OpencodeAdapter:
    name = "opencode"

    def command(self, route: Route, prompt: str) -> tuple[list[str], str | None]:
        argv = ["opencode", "run", "--format", "json"]
        if route.model:
            argv += ["-m", route.model]
        argv += list(route.extra_flags)
        argv += [prompt]
        return argv, None

    def parse(self, stdout: str, stderr: str, exit_code: int) -> HarnessResult:
        parts = []
        errors = []
        cost_hint = None
        for obj in _json_lines(stdout):
            kind = obj.get("type")
            part = obj.get("part") or obj
            if kind == "text":
                parts.append(part.get("text", ""))
            elif kind == "step_finish":
                if "cost" in part:
                    cost_hint = part["cost"]
                elif "cost" in obj:
                    cost_hint = obj["cost"]
            elif kind == "error":
                errors.append(obj)
        text = "".join(parts)
        if not text or exit_code != 0:
            diagnostics = [json.dumps(e, ensure_ascii=False) for e in errors]
            if stderr.strip():
                diagnostics.append(f"stderr: {stderr[-500:]}")
            detail = "; ".join(diagnostics) if diagnostics else "no assistant text"
            return HarnessResult(text=f"opencode failed (exit {exit_code}): {detail}", exit=exit_code or 1, cost_hint=None)
        return HarnessResult(text=text, exit=exit_code, cost_hint=cost_hint)

    def env(self, route: Route, call_dir: pathlib.Path) -> dict[str, str] | None:
        """Give this call its own XDG_DATA_HOME, symlinked to the shared auth.json.

        Concurrent `opencode run` subprocesses share ~/.local/share/opencode/opencode.db
        (SQLite) and fail with "database is locked". Pointing each call at its own
        XDG_DATA_HOME sidesteps the shared db while still authenticating via the one
        real auth.json (symlinked, never copied).
        """
        shared_data_home = pathlib.Path(os.environ.get("XDG_DATA_HOME") or (pathlib.Path.home() / ".local" / "share"))
        shared_auth = shared_data_home / "opencode" / "auth.json"
        if not shared_auth.exists():
            return None
        opencode_dir = call_dir / "xdg-data" / "opencode"
        opencode_dir.mkdir(parents=True, exist_ok=True)
        link = opencode_dir / "auth.json"
        if not link.is_symlink():
            link.symlink_to(shared_auth)
        return {"XDG_DATA_HOME": str(call_dir / "xdg-data")}


class FakeAdapter:
    name = "fake"

    def command(self, route: Route, prompt: str) -> tuple[list[str], str | None]:
        return [os.environ["WFE_FAKE_CMD"], *route.extra_flags], prompt

    def parse(self, stdout: str, stderr: str, exit_code: int) -> HarnessResult:
        return HarnessResult(text=stdout, exit=exit_code, cost_hint=None)


ADAPTERS: dict[str, Adapter] = {
    "claude": ClaudeAdapter(),
    "codex": CodexAdapter(),
    "pi": PiAdapter(),
    "opencode": OpencodeAdapter(),
    "fake": FakeAdapter(),
}


def load_routes(path: pathlib.Path) -> dict[str, Route]:
    raw = json.loads(pathlib.Path(path).read_text())
    routes: dict[str, Route] = {}
    for name, fields in raw.items():
        routes[name] = Route(
            harness=fields["harness"],
            model=fields.get("model"),
            extra_flags=list(fields.get("extra_flags", [])),
        )
    return routes


def resolve(routes: dict[str, Route], name: str) -> Route:
    try:
        return routes[name]
    except KeyError:
        raise ValueError(f"unknown route {name!r}; available: {sorted(routes)}") from None


async def spawn(
    route: Route,
    prompt: str,
    timeout_s: float,
    log_prefix: pathlib.Path,
    cwd: pathlib.Path,
    call_dir: pathlib.Path | None = None,
) -> HarnessResult:
    adapter = ADAPTERS[route.harness]
    argv, stdin_text = adapter.command(route, prompt)
    stdin_bytes = stdin_text.encode() if stdin_text is not None else None

    env = None
    env_hook = getattr(adapter, "env", None)
    if env_hook is not None and call_dir is not None:
        extra_env = env_hook(route, call_dir)
        if extra_env:
            env = {**os.environ, **extra_env}

    proc = await asyncio.create_subprocess_exec(
        *argv,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        start_new_session=True,
        cwd=cwd,
        env=env,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(stdin_bytes), timeout_s)
    except (asyncio.TimeoutError, asyncio.CancelledError) as exc:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            await asyncio.wait_for(proc.wait(), 5)
        except asyncio.TimeoutError:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            await proc.wait()
        if isinstance(exc, asyncio.CancelledError):
            raise
        raise TimeoutError(f"timed out after {timeout_s}s") from exc

    log_prefix.parent.mkdir(parents=True, exist_ok=True)
    log_prefix.with_name(log_prefix.name + ".stdout.txt").write_bytes(out)
    log_prefix.with_name(log_prefix.name + ".stderr.txt").write_bytes(err)

    stdout_text = out.decode(errors="replace")
    stderr_text = err.decode(errors="replace")
    return adapter.parse(stdout_text, stderr_text, proc.returncode)
