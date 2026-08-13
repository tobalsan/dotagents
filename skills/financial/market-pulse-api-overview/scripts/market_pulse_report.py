#!/usr/bin/env python3
"""Build Markets Monitor Market Pulse report from HTTP API."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def fetch_json(base: str, path: str) -> Any:
    url = base.rstrip("/") + path
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GET {url} failed: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GET {url} failed: {exc.reason}") from exc


def as_pct(value: Any) -> str:
    return "not available" if value is None else f"{round(float(value) * 100)}%"


def text(value: Any, fallback: str = "not available") -> str:
    return fallback if value is None or value == "" else str(value)


def latest_signal(signals: list[dict[str, Any]], agent: str) -> dict[str, Any] | None:
    return next((s for s in signals if s.get("agent") == agent), None)


def signal_headline(signal: dict[str, Any]) -> str:
    payload = signal.get("payload") or {}
    for key in ("headline", "signal", "narrative"):
        if payload.get(key):
            return str(payload[key])
    events = payload.get("key_events")
    if isinstance(events, list) and events:
        first = events[0]
        if isinstance(first, dict) and first.get("event"):
            return str(first["event"])
        return str(first)
    return str(signal.get("agent", "signal"))


def normalize_top_signal(item: dict[str, Any]) -> dict[str, Any]:
    payload = item.get("payload") or {}
    return {
        "headline": item.get("headline") or signal_headline(item),
        "impact": item.get("impact") or payload.get("impact") or "medium",
        "direction": item.get("direction") or payload.get("direction") or payload.get("drift_direction"),
        "markets": item.get("affected_markets") or payload.get("affected_markets") or payload.get("asset_class") or [],
    }


def trend(history: list[dict[str, Any]]) -> str:
    if len(history) < 2:
        return "not enough history"
    newest = history[0]
    oldest = history[-1]
    return (
        f"{text(oldest.get('regime'))} → {text(newest.get('regime'))}; "
        f"confidence {as_pct(oldest.get('confidence'))} → {as_pct(newest.get('confidence'))}"
    )


def build_report(base: str, days: int, limit: int) -> str:
    health = fetch_json(base, "/api/health")
    regime = fetch_json(base, "/api/regime")
    history = fetch_json(base, f"/api/regime/history?days={days}").get("items", [])
    signals = fetch_json(base, f"/api/signals/latest?limit={limit}").get("items", [])

    top = regime.get("top_signals") or [normalize_top_signal(s) for s in signals[:5]]
    policy = latest_signal(signals, "policy_velocity") or {}
    geo = latest_signal(signals, "geopolitical_risk") or {}
    pp = policy.get("payload") or {}
    gp = geo.get("payload") or {}
    last_run = health.get("last_run") or {}
    sources = health.get("sources") or {}

    conf = regime.get("confidence")
    weather = regime.get("trading_weather")
    one_line = f"{text(regime.get('regime'))} regime, {as_pct(conf)} confidence, trading weather {text(weather)}."

    lines = [
        "# Market Pulse",
        "",
        one_line,
        "",
        "## Regime",
        f"- Regime: {text(regime.get('regime'))}",
        f"- Confidence: {as_pct(conf)}",
        f"- Trading weather: {text(weather)}",
        f"- Updated: {text(regime.get('updated_at'))}",
        "",
        "## Interpretation",
        f"- Narrative: {text(regime.get('narrative'))}",
        "",
        "## Top Signals",
    ]
    if top:
        for i, item in enumerate(top[:5], 1):
            markets = item.get("affected_markets") or item.get("markets") or []
            if isinstance(markets, str):
                markets = [markets]
            lines.append(
                f"{i}. {text(item.get('headline'))} — impact {text(item.get('impact'))}; "
                f"direction {text(item.get('direction'))}; markets {', '.join(markets) or 'not available'}"
            )
    else:
        lines.append("- not available")

    events = pp.get("key_events") if isinstance(pp.get("key_events"), list) else []
    lines += [
        "",
        "## Policy Velocity",
        f"- Hawkish/dovish score: {text(pp.get('hawkish_dovish_score'))}",
        f"- Drift: {text(pp.get('drift_direction'))}",
        f"- Velocity: {text(pp.get('velocity'))}",
        f"- Reasoning: {text(pp.get('reasoning') or pp.get('narrative'))}",
    ]
    for event in events[:5]:
        if isinstance(event, dict):
            lines.append(f"  - {text(event.get('event'))}")
        else:
            lines.append(f"  - {text(event)}")

    themes = gp.get("top_themes") if isinstance(gp.get("top_themes"), list) else []
    escalation = gp.get("escalation_signals") if isinstance(gp.get("escalation_signals"), list) else []
    lines += [
        "",
        "## Geopolitical Risk",
        f"- Risk level: {text(gp.get('risk_level'))}/10",
        f"- Themes: {', '.join(map(str, themes)) if themes else 'not available'}",
        f"- Escalation: {' · '.join(map(str, escalation)) if escalation else 'not available'}",
        "",
        "## Trend",
        f"- {trend(history)}",
        "",
        "## Freshness",
        f"- Last run status: {text(last_run.get('status'))}",
        f"- Last run completed: {text(last_run.get('completed_at'))}",
        f"- Sources healthy/stale/broken: {sources.get('healthy', 0)}/{sources.get('stale', 0)}/{sources.get('broken', 0)}",
        "",
        "## Caveats",
    ]
    caveats: list[str] = []
    if conf is None or float(conf) < 0.5:
        caveats.append("Regime confidence low or missing.")
    if not top:
        caveats.append("Top signals missing.")
    if not policy:
        caveats.append("Policy velocity signal missing.")
    if not geo:
        caveats.append("Geopolitical risk signal missing.")
    if not caveats:
        caveats.append("No major data caveats from required endpoints.")
    lines.extend(f"- {c}" for c in caveats)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=os.environ.get("MARKET_API_BASE", "http://127.0.0.1:8010"))
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    try:
        print(build_report(args.base, args.days, args.limit))
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
