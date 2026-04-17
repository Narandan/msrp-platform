"""
High-impact edge case test: constant price data.

Why this matters:
- No volatility → std = 0
- No returns → risk of division by zero
- Indicators must still behave correctly

This test validates:
- Bollinger Bands collapse correctly
- EMA/SMA remain stable
- Sharpe ratio returns 0 instead of crashing
"""

import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.stock import CandleDTO
from app.schemas.backtest import EquityPoint
from app.services.indicators.bollinger import compute_bollinger_bands
from app.services.indicators.ema import compute_ema
from app.services.indicators.sma import compute_sma
from app.services.backtesting.metrics import compute_metrics


def test_constant_price_edge_case():
    # --- Create constant price data ---
    candles = [
        CandleDTO(
            date=date(2023, 1, 1) + timedelta(days=i),
            open=100,
            high=100,
            low=100,
            close=100,
            volume=1000,
        )
        for i in range(50)
    ]

    # --- Indicators ---
    sma = compute_sma(candles, period=20)
    ema = compute_ema(candles, period=20)
    bb_m, bb_u, bb_l = compute_bollinger_bands(candles, period=20)

    # All computed values should equal the constant price
    for i in range(19, 50):
        assert sma[i] == 100
        assert ema[i] == 100
        assert bb_m[i] == 100

        # With zero std deviation, bands collapse
        assert bb_u[i] == 100
        assert bb_l[i] == 100

    # --- Sharpe ratio ---
    equity = [
        EquityPoint(date=date(2023, 1, 1) + timedelta(days=i), equity=10000)
        for i in range(50)
    ]

    metrics = compute_metrics(equity_curve=equity, trades=[])

    # No returns → Sharpe should be 0, not NaN or crash
    assert metrics.sharpe_ratio == 0.0