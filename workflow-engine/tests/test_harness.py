"""harness.py: spawn's optional per-call adapter env hook, OpencodeAdapter.env/parse."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

from workflow_engine import harness
from workflow_engine.harness import (
    ClaudeAdapter,
    CodexAdapter,
    HarnessResult,
    OpencodeAdapter,
    Route,
)


class _CwdProbeAdapter:
    name = "cwdprobe"

    def command(self, route: Route, prompt: str) -> tuple[list[str], str | None]:
        return [sys.executable, "-c", "import pathlib; print(pathlib.Path.cwd())"], None

    def parse(self, stdout: str, stderr: str, exit_code: int) -> HarnessResult:
        return HarnessResult(text=stdout.strip(), exit=exit_code, cost_hint=None)


class _EnvProbeAdapter:
    """Test double: echoes one env var back on stdout, and defines the optional env() hook."""

    name = "envprobe"

    def command(self, route: Route, prompt: str) -> tuple[list[str], str | None]:
        code = "import os, sys; sys.stdout.write(os.environ.get('WFE_TEST_VAR', ''))"
        return [sys.executable, "-c", code], None

    def parse(self, stdout: str, stderr: str, exit_code: int) -> HarnessResult:
        return HarnessResult(text=stdout, exit=exit_code, cost_hint=None)

    def env(self, route: Route, call_dir: Path) -> dict[str, str] | None:
        return {"WFE_TEST_VAR": "from-adapter-hook"}


# --- spawn: optional adapter env hook ---------------------------------------


def test_spawn_without_env_hook_still_works(tmp_path: Path) -> None:
    """FakeAdapter defines no env() hook; spawn must work fine without one."""
    route = Route(harness="fake", extra_flags=["echo"])
    log_prefix = tmp_path / "logs" / "k.a1"
    result = asyncio.run(harness.spawn(route, "hi @@EMIT:ok@@", 5.0, log_prefix, tmp_path))
    assert result.text == "ok" and result.exit == 0


def test_spawn_merges_adapter_env_hook_into_the_subprocess(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setitem(harness.ADAPTERS, "envprobe", _EnvProbeAdapter())
    route = Route(harness="envprobe")
    log_prefix = tmp_path / "logs" / "k.a1"
    call_dir = tmp_path / "calls" / "k"
    result = asyncio.run(harness.spawn(route, "prompt", 5.0, log_prefix, tmp_path, call_dir=call_dir))
    assert result.text == "from-adapter-hook"


def test_spawn_uses_supplied_workspace_as_child_cwd(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setitem(harness.ADAPTERS, "cwdprobe", _CwdProbeAdapter())
    cwd = tmp_path / "campaign"
    cwd.mkdir()
    result = asyncio.run(harness.spawn(Route(harness="cwdprobe"), "prompt", 5.0, tmp_path / "logs" / "k.a1", cwd))
    assert result.text == str(cwd)


# --- write-capable adapter defaults ------------------------------------------


def test_claude_defaults_to_edit_acceptance_without_duplicate_override() -> None:
    argv, stdin = ClaudeAdapter().command(Route(harness="claude", model="sonnet"), "prompt")
    assert argv == ["claude", "-p", "--output-format", "json", "--model", "sonnet", "--permission-mode", "acceptEdits"]
    assert stdin == "prompt"


def test_codex_defaults_to_workspace_write_sandbox() -> None:
    argv, stdin = CodexAdapter().command(Route(harness="codex", model="gpt"), "prompt")
    assert argv == ["codex", "exec", "--json", "--skip-git-repo-check", "-m", "gpt", "-s", "workspace-write", "-"]
    assert stdin == "prompt"


def test_opencode_defaults_to_auto_without_duplicate_flag() -> None:
    argv, stdin = OpencodeAdapter().command(Route(harness="opencode", extra_flags=["--auto"]), "prompt")
    assert argv.count("--auto") == 1
    assert argv[-1] == "prompt" and stdin is None


def test_opencode_spawn_command_sets_controlled_workspace_dir(tmp_path: Path) -> None:
    argv, stdin = OpencodeAdapter().command_with_cwd(Route(harness="opencode"), "prompt", tmp_path)
    assert argv[argv.index("--dir") + 1] == str(tmp_path)
    assert argv[-1] == "prompt" and stdin is None


@pytest.mark.parametrize("extra_flags", [["--dir", "/tmp/other"], ["--dir=/tmp/other"]])
def test_opencode_rejects_route_dir_override(tmp_path: Path, extra_flags: list[str]) -> None:
    with pytest.raises(ValueError, match="--dir"):
        OpencodeAdapter().command_with_cwd(Route(harness="opencode", extra_flags=extra_flags), "prompt", tmp_path)


@pytest.mark.parametrize(
    ("adapter", "route"),
    [
        (CodexAdapter(), Route(harness="codex", extra_flags=["--dangerously-bypass-approvals-and-sandbox"])),
        (CodexAdapter(), Route(harness="codex", extra_flags=["-s", "read-only"])),
        (CodexAdapter(), Route(harness="codex", extra_flags=["-s", "workspace-write", "--sandbox=read-only"])),
        (ClaudeAdapter(), Route(harness="claude", extra_flags=["--dangerously-skip-permissions"])),
        (ClaudeAdapter(), Route(harness="claude", extra_flags=["--permission-mode", "bypassPermissions"])),
        (
            ClaudeAdapter(),
            Route(harness="claude", extra_flags=["--permission-mode=acceptEdits", "--permission-mode", "bypassPermissions"]),
        ),
    ],
)
def test_write_defaults_reject_bypass_or_non_write_sandbox(adapter, route: Route) -> None:
    with pytest.raises(ValueError):
        adapter.command(route, "prompt")


# --- OpencodeAdapter.env ------------------------------------------------------


def test_opencode_env_symlinks_shared_auth_and_returns_xdg_data_home(tmp_path: Path, monkeypatch) -> None:
    shared_home = tmp_path / "shared"
    shared_auth = shared_home / "opencode" / "auth.json"
    shared_auth.parent.mkdir(parents=True)
    shared_auth.write_text('{"fake": "creds"}', encoding="utf-8")
    monkeypatch.setenv("XDG_DATA_HOME", str(shared_home))

    call_dir = tmp_path / "calls" / "abc123"
    adapter = OpencodeAdapter()
    result = adapter.env(Route(harness="opencode"), call_dir)

    assert result == {"XDG_DATA_HOME": str(call_dir / "xdg-data")}
    link = call_dir / "xdg-data" / "opencode" / "auth.json"
    assert link.is_symlink()
    assert link.resolve() == shared_auth.resolve()
    assert link.read_text(encoding="utf-8") == '{"fake": "creds"}'


def test_opencode_env_skips_existing_symlink(tmp_path: Path, monkeypatch) -> None:
    shared_home = tmp_path / "shared"
    shared_auth = shared_home / "opencode" / "auth.json"
    shared_auth.parent.mkdir(parents=True)
    shared_auth.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("XDG_DATA_HOME", str(shared_home))

    call_dir = tmp_path / "calls" / "abc123"
    adapter = OpencodeAdapter()
    adapter.env(Route(harness="opencode"), call_dir)
    link = call_dir / "xdg-data" / "opencode" / "auth.json"
    before = link.lstat()
    adapter.env(Route(harness="opencode"), call_dir)  # second call must not recreate/fail
    assert link.lstat() == before


def test_opencode_env_skips_silently_when_shared_auth_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "no-such-shared-home"))
    call_dir = tmp_path / "calls" / "abc123"
    adapter = OpencodeAdapter()
    assert adapter.env(Route(harness="opencode"), call_dir) is None
    assert not call_dir.exists()


# --- OpencodeAdapter.parse: surfacing real failures --------------------------


def test_opencode_parse_surfaces_error_events_and_stderr_tail_on_failure() -> None:
    stdout = "\n".join(
        [
            json.dumps({"type": "error", "message": "provider auth failed"}),
            json.dumps({"type": "step_finish"}),
        ]
    )
    stderr = "x" * 600 + "TAIL_MARKER"
    result = OpencodeAdapter().parse(stdout, stderr, exit_code=1)

    assert result.text != ""
    assert "provider auth failed" in result.text
    assert "TAIL_MARKER" in result.text
    assert result.exit == 1


def test_opencode_parse_flat_shape_fallback_still_works(tmp_path: Path) -> None:
    """Legacy/synthetic flat events (no "part" nesting) must still parse."""
    stdout = "\n".join(
        [
            json.dumps({"type": "text", "text": "hello "}),
            json.dumps({"type": "text", "text": "world"}),
            json.dumps({"type": "step_finish", "cost": 0.01}),
        ]
    )
    result = OpencodeAdapter().parse(stdout, "", exit_code=0)
    assert result.text == "hello world" and result.exit == 0 and result.cost_hint == 0.01


def test_opencode_parse_nested_part_shape_from_real_cli() -> None:
    """Real `opencode run --format json` output nests the payload under "part"."""
    stdout = "\n".join(
        [
            json.dumps(
                {
                    "type": "step_start",
                    "timestamp": 1786368800816,
                    "sessionID": "ses_x",
                    "part": {"id": "prt_1", "messageID": "m", "sessionID": "s", "type": "step-start"},
                }
            ),
            json.dumps(
                {
                    "type": "text",
                    "timestamp": 1786368801224,
                    "sessionID": "ses_x",
                    "part": {
                        "id": "prt_2",
                        "messageID": "m",
                        "sessionID": "s",
                        "type": "text",
                        "text": "ping",
                        "time": {"start": 1, "end": 2},
                    },
                }
            ),
            json.dumps(
                {
                    "type": "step_finish",
                    "timestamp": 1786368801224,
                    "sessionID": "ses_x",
                    "part": {
                        "id": "prt_3",
                        "reason": "stop",
                        "messageID": "m",
                        "sessionID": "s",
                        "type": "step-finish",
                        "tokens": {"total": 9763},
                        "cost": 0.000551838,
                    },
                }
            ),
        ]
    )
    result = OpencodeAdapter().parse(stdout, "", exit_code=0)
    assert result.text == "ping" and result.exit == 0 and result.cost_hint == 0.000551838
