---
name: intraday-desk-api
description: Use the Markets Monitor HTTP API to reconstruct the Intraday Desk state — futures tape, key price levels and structure, market internals (TICK/TRIN/breadth), gamma exposure (GEX) and dealer positioning, and volume profile — as a concise day-trading briefing. Trigger whenever asked about current intraday market state, key levels, ES/NQ/YM/GC structure, VWAP/POC/value area, support/resistance, TICK/TRIN, call/put walls, gamma flip/regime, volume profile, session bias, or any pre-trade or intraday data check for futures day trading, even if the API or dashboard is never mentioned.
---

# Intraday Desk API

Reconstruct the Intraday Desk view from the Markets Monitor API as an agent-readable day-trading briefing. Focus on tradeable structure and risk conditions, not dashboard layout.

## Inputs

- API base URL. Prefer user-provided value. Else use `MARKET_API_BASE`. Else default `http://127.0.0.1:8010` (correct when running on the host that serves the API). Off-host, the Tailscale frontend `https://thinhs-mac-studio.catla-powan.ts.net:8002` proxies `/api` to the same backend.
- Futures symbol. Default `ES`. Cached symbols: `ES NQ YM GC CL TNX DX`.

## Required API calls

```txt
GET {base}/api/tv/session
GET {base}/api/tv/futures
GET {base}/api/tv/levels/{symbol}
GET {base}/api/tv/internals          # RTH only — 404 outside 09:30–16:00 ET
GET {base}/api/tv/gex/summary
GET {base}/api/tv/profile/{symbol}
```

Optional drilldowns:

```txt
GET {base}/api/tv/leaders            # NQ mega-caps, for index confirmation
GET {base}/api/tv/sectors            # sector ETF rotation
GET {base}/api/tv/gex/{SPY|QQQ}      # full per-strike, per-expiry gamma ladder
```

## Fast path

Use the bundled script when available:

```bash
python3 scripts/intraday_report.py --base http://127.0.0.1:8010 --symbol ES
```

If Python is unavailable, `curl` the same endpoints and synthesize manually.

## Payload notes

- `/futures` → `{session, last_updated, futures: {SYM: {price, change_pct, change_abs, session_high, session_low, prev_close, volume}}}`.
- `/levels/{sym}` → flat dict: `prev_day_high/low/close`, `session_high/low`, `prev_week_high/low`, `ema20`, `vwap`, `poc_1d`, `vah_1d`, `val_1d`, `poc_5d`, `vah_5d`, `val_5d`.
- `/internals` → `{tick, tick_high, tick_low, trin, adv, dec, adv_ratio, timestamp}`.
- `/gex/summary` → `{spy, qqq}`, each `{spot_price, call_wall, put_wall, gamma_wall, gamma_flip, regime, regime_implication, timestamp, source}`. `/gex/{sym}` adds `strikes[]` with per-expiration `{call_gamma, put_gamma, net_gamma, dte}`.
- `/profile/{sym}` → `{current_price, yesterday, five_day}`, each profile `{poc, vah, val, buckets[], total_volume}`; buckets carry `{price_low, price_high, volume, pct_of_total, is_poc, is_value_area}`.
- Server refresh cadence: futures/levels every 30s during RTH (5 min otherwise); volume profile 5 min; GEX 15 min; internals 30s RTH-only. `last_updated` is ET ISO.

## Report structure

ALWAYS use this template:

1. `Snapshot` — one-line read of the session (direction, where price sits in structure, gamma regime).
2. `Session & freshness` — session state, `last_updated`, staleness flags.
3. `Tape` — futures table: last, chg%, chg, session high/low.
4. `Structure` — key-level ladder for the working symbol, sorted high→low, each tagged with price ABOVE/BELOW/AT; call out nearest resistance and support.
5. `Internals` — TICK, TRIN, A/D with interpretation (omit gracefully outside RTH).
6. `Gamma (GEX)` — SPY and QQQ: regime, flip, call/put walls, implication, source, timestamp.
7. `Volume profile` — yesterday + 5-day POC/VAH/VAL; where current price sits vs value.
8. `Leaders & sectors` — mega-caps confirm/diverge vs NQ; sector rotation ranked.
9. `Caveats` — anything missing, stale, or low-quality.

## Inference rules

- Level tags: price vs level with ±0.05 tolerance → `AT`, else `ABOVE`/`BELOW` (tag describes where *price* is relative to the level).
- Nearest level above price = first resistance; nearest below = first support. Confluence (two levels within a few points) makes a level more meaningful.
- Value area: price below VAL = out of value low (acceptance below → balance lower; swift reclaim → look-below-and-fail); inside VA = balance/rotation conditions; above VAH = out of value high.
- TICK: sustained beyond ±500 = directional pressure; ±1000+ extremes = climactic, often exhaustion. Between ±200 = chop.
- TRIN: > 1.2 = selling intensity (bearish), < 0.8 = buying intensity (bullish), else neutral. `adv_ratio` < 0.4 or > 0.6 = broad one-sided breadth.
- GEX regime: `positive` = dealers fade moves — mean-reversion conditions, respect walls as magnets/pins; `negative` = dealers amplify moves — trend-day risk, moves through walls can accelerate. `gamma_flip` is the price where regime flips.
- GEX strikes are SPY/QQQ ETF prices. Do NOT convert them to ES/NQ point equivalents — use them for regime and behavior context, not as futures levels.
- Leaders vs NQ: |change_pct| < 0.3 → `mixed`; same sign as NQ → `confirms`; opposite → `diverging`. Majority diverging = index move lacks participation, fade risk.
- Internals 404 outside RTH is expected, not an error — report `internals: not available (outside RTH)`.
- Do not invent missing data. Say `not available`.

## Output constraints

- No buy/sell advice phrasing. Describe conditions, structure, and risk posture; the trader decides.
- Include exact timestamps from the API; flag futures data older than ~2 min during RTH and GEX older than ~20 min as stale.
- Keep the briefing concise unless deep analysis is requested.
