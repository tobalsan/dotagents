#!/usr/bin/env python3
"""Intraday day-trading briefing from the Markets Monitor API (/api/tv/*)."""
import argparse
import json
import os
import urllib.error
import urllib.request

LEVEL_NAMES = [
    ("MH", "month_high"),
    ("PMH", "prev_month_high"),
    ("PWH", "prev_week_high"),
    ("PDH", "prev_day_high"),
    ("VAH", "vah_1d"),
    ("POC", "poc_1d"),
    ("PDC", "prev_day_close"),
    ("EMA20", "ema20"),
    ("VWAP", "vwap"),
    ("VAL", "val_1d"),
    ("PDL", "prev_day_low"),
    ("PWL", "prev_week_low"),
    ("PML", "prev_month_low"),
    ("ML", "month_low"),
]


def fetch(base, path):
    try:
        with urllib.request.urlopen(base + path, timeout=15) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_error": f"HTTP {e.code}"}
    except Exception as e:
        return {"_error": str(e)}


def fmt(x, nd=2):
    return f"{x:,.{nd}f}" if isinstance(x, (int, float)) else "n/a"


def classify_leader(pct, nq_pct):
    if pct is None or nq_pct is None:
        return "n/a"
    if abs(pct) < 0.3:
        return "mixed"
    return "confirms" if (pct > 0) == (nq_pct > 0) else "diverging"


def volatility_conditions(state):
    if state == "contango":
        return "calm conditions; short-dated volatility below 3-month volatility"
    if state == "backwardation":
        return "acute stress; short-dated volatility above 3-month volatility"
    return "mixed volatility conditions"


def render_volatility(volatility):
    if "_error" in volatility:
        return [f"- not available ({volatility['_error']})"]

    vix = volatility.get("vix", {})
    term = volatility.get("term_structure", {})
    return [
        (
            f"- VIX {fmt(vix.get('last'))} | chg {fmt(vix.get('change_abs'))} "
            f"({fmt(vix.get('change_pct'))}%) | H {fmt(vix.get('session_high'))} "
            f"/ L {fmt(vix.get('session_low'))}"
        ),
        (
            f"- Term structure: {term.get('state', 'n/a')} | "
            f"9D/VIX {fmt(term.get('vix9d_vix_ratio'), 3)} | "
            f"VIX/3M {fmt(term.get('vix_vix3m_ratio'), 3)}"
        ),
        f"- {volatility_conditions(term.get('state'))}",
    ]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--base",
        default=os.environ.get("MARKET_API_BASE", "http://127.0.0.1:8010"),
        help="API base URL",
    )
    ap.add_argument("--symbol", default="ES", help="futures symbol (ES NQ YM GC CL TNX DX)")
    args = ap.parse_args()
    base = args.base.rstrip("/")
    sym = args.symbol.upper()

    session = fetch(base, "/api/tv/session")
    futures = fetch(base, "/api/tv/futures")
    levels = fetch(base, f"/api/tv/levels/{sym}")
    internals = fetch(base, "/api/tv/internals")
    volatility = fetch(base, "/api/tv/vol")
    gex = fetch(base, "/api/tv/gex/summary")
    profile = fetch(base, f"/api/tv/profile/{sym}")
    leaders = fetch(base, "/api/tv/leaders")
    sectors = fetch(base, "/api/tv/sectors")

    fut = futures.get("futures", {}) if isinstance(futures, dict) else {}
    cur = fut.get(sym, {}).get("price")

    out = []
    out.append(f"# Intraday Briefing — {sym}")
    out.append("")
    out.append(f"- Session: {session.get('session', 'n/a')} ({session.get('description', '')})")
    out.append(f"- Data updated: {futures.get('last_updated', 'n/a')}")

    out.append("")
    out.append("## Tape")
    out.append("")
    out.append("| Sym | Last | Chg% | Chg | Hi | Lo |")
    out.append("|---|---|---|---|---|---|")
    for s, q in fut.items():
        out.append(
            f"| {s} | {fmt(q.get('price'))} | {q.get('change_pct') or 0:+.2f}% "
            f"| {q.get('change_abs') or 0:+,.2f} | {fmt(q.get('session_high'))} "
            f"| {fmt(q.get('session_low'))} |"
        )

    out.append("")
    out.append(f"## Structure — {sym} (current: {fmt(cur)})")
    if "_error" in levels:
        out.append(f"- not available ({levels['_error']})")
    else:
        rows = [(n, levels.get(k)) for n, k in LEVEL_NAMES if levels.get(k) is not None]
        rows.sort(key=lambda r: r[1], reverse=True)
        out.append("")
        out.append("| Level | Price | Position |")
        out.append("|---|---|---|")
        for name, val in rows:
            pos = "n/a"
            if cur is not None:
                pos = "AT" if abs(cur - val) <= 0.05 else ("BELOW" if cur < val else "ABOVE")
            out.append(f"| {name} | {fmt(val)} | price {pos} |")
        if cur is not None:
            above = [r for r in rows if r[1] > cur]
            below = [r for r in rows if r[1] < cur]
            if above:
                n, v = above[-1]
                out.append(f"- Nearest resistance: {n} {fmt(v)} (+{v - cur:.2f})")
            if below:
                n, v = below[0]
                out.append(f"- Nearest support: {n} {fmt(v)} ({v - cur:.2f})")

    out.append("")
    out.append("## Internals")
    if "_error" in internals:
        out.append(f"- not available ({internals['_error']} — RTH only)")
    else:
        tick, trin = internals.get("tick"), internals.get("trin")
        tick_read = "neutral"
        if isinstance(tick, (int, float)):
            tick_read = (
                "bullish pressure" if tick > 500
                else "bearish pressure" if tick < -500
                else "neutral"
            )
        trin_read = "neutral"
        if isinstance(trin, (int, float)):
            trin_read = (
                "bearish (selling intensity)" if trin > 1.2
                else "bullish (buying intensity)" if trin < 0.8
                else "neutral"
            )
        out.append(
            f"- TICK {fmt(tick, 0)} (H {fmt(internals.get('tick_high'), 0)} "
            f"/ L {fmt(internals.get('tick_low'), 0)}) — {tick_read}"
        )
        out.append(f"- TRIN {fmt(trin)} — {trin_read}")
        out.append(
            f"- A/D {internals.get('adv')}/{internals.get('dec')} "
            f"({100 * (internals.get('adv_ratio') or 0):.0f}% adv)"
        )

    out.append("")
    out.append("## Volatility")
    out.extend(render_volatility(volatility))

    out.append("")
    out.append("## Gamma (GEX)")
    if "_error" in gex:
        out.append(f"- not available ({gex['_error']})")
    else:
        for key in ("spy", "qqq"):
            g = gex.get(key)
            if not g:
                continue
            out.append(
                f"- {g.get('symbol', key.upper())}: {g.get('regime')} gamma | "
                f"spot {fmt(g.get('spot_price'))} | flip {fmt(g.get('gamma_flip'))} | "
                f"call wall {fmt(g.get('call_wall'))} | put wall {fmt(g.get('put_wall'))} — "
                f"{g.get('regime_implication', '')} (src {g.get('source')}, {g.get('timestamp')})"
            )

    out.append("")
    out.append(f"## Volume profile — {sym}")
    if "_error" in profile:
        out.append(f"- not available ({profile['_error']})")
    else:
        for label, key in (("Yesterday", "yesterday"), ("5-day", "five_day")):
            vp = profile.get(key)
            if vp:
                out.append(
                    f"- {label}: POC {fmt(vp.get('poc'))} | VAH {fmt(vp.get('vah'))} "
                    f"| VAL {fmt(vp.get('val'))}"
                )
        cp = profile.get("current_price")
        vp = profile.get("yesterday")
        if cp is not None and vp:
            where = (
                "inside value" if vp["val"] <= cp <= vp["vah"]
                else "below value" if cp < vp["val"]
                else "above value"
            )
            out.append(f"- Current {fmt(cp)} — {where} vs yesterday's value area")

    out.append("")
    out.append("## Leaders vs NQ")
    nq_pct = fut.get("NQ", {}).get("change_pct")
    if isinstance(leaders, dict) and leaders.get("leaders"):
        for ldr in leaders["leaders"]:
            out.append(
                f"- {ldr.get('name')} {ldr.get('change_pct') or 0:+.2f}% — "
                f"{classify_leader(ldr.get('change_pct'), nq_pct)}"
            )
    else:
        out.append("- not available")

    out.append("")
    out.append("## Sector rotation")
    if isinstance(sectors, dict) and sectors.get("sectors"):
        ranked = sorted(sectors["sectors"], key=lambda s: s.get("change_pct") or 0, reverse=True)
        out.append("- " + " | ".join(f"{s.get('name')} {s.get('change_pct') or 0:+.2f}%" for s in ranked))
    else:
        out.append("- not available")

    errs = [
        (n, d["_error"])
        for n, d in [
            ("session", session), ("futures", futures), ("levels", levels),
            ("volatility", volatility), ("gex", gex), ("profile", profile),
        ]
        if isinstance(d, dict) and "_error" in d
    ]
    if errs:
        out.append("")
        out.append("## Caveats")
        for n, e in errs:
            out.append(f"- {n}: {e}")

    print("\n".join(out))


if __name__ == "__main__":
    main()
