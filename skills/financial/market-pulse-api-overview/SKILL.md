---
name: market-pulse-api-overview
description: Use Markets Monitor HTTP API to reconstruct Market Pulse state as a concise financial report for agents. Trigger when asked for current market pulse, market status, regime overview, risk posture, trading weather, policy velocity, geopolitical risk, or dashboard-equivalent market summary without frontend/UI rendering.
---

# Market Pulse API Overview

Generate agent-readable market-status report from Markets Monitor API. Focus on investable inference, not dashboard layout.

## Inputs

- API base URL. Prefer user-provided value. Else use `MARKET_API_BASE`. Else default `http://127.0.0.1:8010`.
- Optional history window. Default `7` days.
- Optional signal limit. Default `12`.

## Required API calls

Fetch these endpoints:

```txt
GET {base}/api/health
GET {base}/api/regime
GET {base}/api/regime/history?days=7
GET {base}/api/signals/latest?limit=12
```

Optional, only if user asks for provenance/source drilldown:

```txt
GET {base}/api/articles?limit=20
GET {base}/api/sources
```

## Fast path

Use bundled script when available:

```bash
python scripts/market_pulse_report.py --base http://127.0.0.1:8010 --days 7 --limit 12
```

If Python unavailable, use `curl` and synthesize manually from same endpoints.

## Report structure

Return Markdown with these sections:

1. `Market Pulse` — one-line conclusion.
2. `Regime` — regime, confidence, trading weather, updated time.
3. `Interpretation` — what current regime implies for risk appetite.
4. `Top Signals` — ranked signals with impact, direction, markets.
5. `Policy Velocity` — hawkish/dovish score, drift, velocity, key events/reasoning.
6. `Geopolitical Risk` — risk level, themes, escalation flags.
7. `Trend` — regime-history direction and confidence changes.
8. `Freshness` — last run status/completed time, API health.
9. `Caveats` — missing/stale endpoints, null fields, low confidence.

## Inference rules

- Treat `/api/regime` as source of truth for headline market state.
- Use `confidence < 0.5` as low-confidence caveat.
- Map `trading_weather`:
  - `lean_in`: risk-taking conditions favorable, but still validate against top signals.
  - `normal`: balanced/standard risk conditions.
  - `sit_out`: unfavorable/no-trade or defensive conditions.
- Interpret `policy_velocity` signal from latest signals where `agent == "policy_velocity"`:
  - `hawkish_dovish_score > 0.15`: hawkish pressure / tighter financial conditions.
  - `< -0.15`: dovish support / easier financial conditions.
  - else neutral policy drift.
- Interpret `geopolitical_risk` signal where `agent == "geopolitical_risk"`:
  - `risk_level >= 7`: high geopolitical risk.
  - `4-6`: moderate risk.
  - `0-3`: low risk.
- If `/api/regime.top_signals` exists, prefer it for ranked signals. Else use `/api/signals/latest` top 5.
- Do not invent missing data. Say `not available`.

## Output constraints

- No frontend/design commentary.
- No investment advice phrasing like “buy/sell”. Use risk posture language.
- Include exact timestamps from API where relevant.
- Keep report concise unless user asks for deep analysis.
