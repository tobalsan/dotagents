"""wfe — argparse CLI. Entry point: workflow_engine.cli:main."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from workflow_engine.engine import Run, load_workflow
from workflow_engine.harness import load_routes
from workflow_engine.watch import cmd_watch


def _kv(text: str) -> tuple[str, str]:
    if "=" not in text:
        raise argparse.ArgumentTypeError(f"--arg must be key=value, got: {text!r}")
    k, v = text.split("=", 1)
    return k, v


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wfe", description="Deterministic multi-agent workflow engine")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="run a workflow")
    run_p.add_argument("workflow")
    run_p.add_argument("--campaign", required=True)
    run_p.add_argument("--routing")
    run_p.add_argument("--arg", action="append", default=[], type=_kv, metavar="k=v")
    run_p.add_argument("--resume")
    run_p.add_argument("--concurrency", type=int, default=6)
    run_p.add_argument("--timeout", type=float, default=900.0)

    status_p = sub.add_parser("status", help="show run status")
    status_p.add_argument("run_dir")
    status_p.add_argument("--json", action="store_true")

    list_p = sub.add_parser("list", help="list runs")
    list_p.add_argument("--campaign")

    watch_p = sub.add_parser("watch", help="serve a read-only run dashboard on localhost")
    watch_p.add_argument("--campaign", required=True)
    watch_p.add_argument("--run")
    watch_p.add_argument("--port", type=int, default=8799)

    return parser


def cmd_run(ns: argparse.Namespace) -> int:
    workflow_path = Path(ns.workflow).resolve()
    if not workflow_path.is_file():
        print(f"error: workflow not found: {workflow_path}", file=sys.stderr)
        return 2

    try:
        load_workflow(workflow_path)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    campaign_dir = Path(ns.campaign).resolve()
    routing_path = Path(ns.routing).resolve() if ns.routing else campaign_dir / "routes.json"
    if not routing_path.is_file():
        print(f"error: routing file not found: {routing_path}", file=sys.stderr)
        return 2
    try:
        routes = load_routes(routing_path)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    args = dict(ns.arg)

    if ns.resume:
        run_id = ns.resume
    else:
        run_id = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{workflow_path.stem}"
    run_dir = campaign_dir / "runs" / run_id

    run = Run(
        run_dir=run_dir,
        campaign_dir=campaign_dir,
        routes=routes,
        concurrency=ns.concurrency,
        default_timeout_s=ns.timeout,
        resume=bool(ns.resume),
    )

    try:
        asyncio.run(run.execute(workflow_path, args))
    except KeyboardInterrupt:
        return 1
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    status = _read_status(run_dir)
    if status is None:
        return 1
    counts = status.get("counts", {})
    if status.get("state") != "completed" or counts.get("error", 0) > 0:
        return 1
    return 0


def _read_status(run_dir: Path) -> dict | None:
    status_path = run_dir / "status.json"
    if not status_path.is_file():
        return None
    try:
        return json.loads(status_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _print_status_human(status: dict) -> None:
    counts = status.get("counts", {})
    print(
        f"{status.get('state')}  phase={status.get('phase')}  "
        f"elapsed={status.get('elapsed_s')}s  "
        f"total={counts.get('total', 0)} ok={counts.get('ok', 0)} "
        f"error={counts.get('error', 0)} running={counts.get('running', 0)} "
        f"replayed={counts.get('replayed', 0)}"
    )
    for call in status.get("calls", []):
        route_model = f"{call.get('route')}/{call.get('model')}"
        label = call.get("label") or call.get("call_key", "")
        duration_ms = call.get("duration_ms")
        duration = f"{duration_ms / 1000:.1f}s" if isinstance(duration_ms, (int, float)) else "-"
        print(f"{call.get('state', '?'):10} {route_model:30} {label:20} {duration}")


def cmd_status(ns: argparse.Namespace) -> int:
    run_dir = Path(ns.run_dir).resolve()
    status = _read_status(run_dir)
    if status is None:
        print(f"error: no status.json in {run_dir}", file=sys.stderr)
        return 2
    if ns.json:
        print(json.dumps(status, indent=2))
    else:
        _print_status_human(status)
    return 0


def cmd_list(ns: argparse.Namespace) -> int:
    campaign_dir = Path(ns.campaign).resolve() if ns.campaign else Path.cwd()
    runs_dir = campaign_dir / "runs"
    rows: list[dict] = []
    if runs_dir.is_dir():
        for d in sorted(runs_dir.iterdir()):
            status = _read_status(d)
            if status is not None:
                rows.append(status)
    rows.sort(key=lambda s: s.get("started_at") or "", reverse=True)

    for s in rows:
        counts = s.get("counts", {})
        print(
            f"{s.get('run_id')}  {s.get('state')}  "
            f"{counts.get('ok', 0)}/{counts.get('error', 0)}/{counts.get('total', 0)}  "
            f"{s.get('elapsed_s')}s"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if ns.command == "run":
        return cmd_run(ns)
    if ns.command == "status":
        return cmd_status(ns)
    if ns.command == "list":
        return cmd_list(ns)
    if ns.command == "watch":
        return cmd_watch(ns)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
