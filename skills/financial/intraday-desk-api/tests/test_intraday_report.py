from __future__ import annotations

import importlib.util
from pathlib import Path


_REPORT_PATH = Path(__file__).parents[1] / "scripts/intraday_report.py"


def test_volatility_report_handles_missing_vx_front() -> None:
    spec = importlib.util.spec_from_file_location("intraday_report", _REPORT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    lines = module.render_volatility(
        {
            "vix": {"last": 16.0, "change_abs": -1.0, "change_pct": -5.88, "session_high": 17.2, "session_low": 15.8},
            "vx_front": None,
            "term_structure": {
                "state": "contango",
                "vix9d_vix_ratio": 0.9,
                "vix_vix3m_ratio": 0.8,
                "implication": "calm regime, dips tend to get bought",
            },
        }
    )

    assert "VIX 16.00" in lines[0]
    assert "contango" in lines[1]
    assert "calm conditions" in lines[2]
