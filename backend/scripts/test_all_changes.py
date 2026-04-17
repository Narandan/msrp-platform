"""
Comprehensive pytest regression test for the Increment 3 changes.

What this test covers:
- Symbol search schema validity
- Bollinger Bands calculation
- EMA calculation and EMA/SMA initialization relationship
- Sharpe ratio presence in computed metrics
- Compatibility of multiple indicators together
- Basic empty/single-point edge cases
- Constant-price / zero-volatility behavior across indicators and metrics
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.stock import CandleDTO, SymbolSearchResult
from app.schemas.backtest import EquityPoint, Trade
from app.services.indicators.bollinger import compute_bollinger_bands
from app.services.indicators.ema import compute_ema
from app.services.indicators.sma import compute_sma
from app.services.backtesting.metrics import compute_metrics


def test_all_changes():
    # Create a simple upward-trending dataset used by the core regression checks.
    candles = [
        CandleDTO(
            date=date(2023, 1, 1) + timedelta(days=i),
            open=100 + i,
            high=105 + i,
            low=95 + i,
            close=100 + i,
            volume=1000,
        )
        for i in range(50)
    ]

    # Test 1: SymbolSearchResult schema
    result = SymbolSearchResult(ticker="AAPL", name="Apple Inc.")
    assert result.ticker == "AAPL"
    assert result.name == "Apple Inc."

    # Test 2: Bollinger Bands
    middle, upper, lower = compute_bollinger_bands(candles, period=20, num_std=2.0)
    assert len(middle) == 50
    assert middle[19] is not None
    assert upper[19] > middle[19] > lower[19]

    # Test 3: EMA
    ema = compute_ema(candles, period=20)
    sma = compute_sma(candles, period=20)

    assert len(ema) == 50
    assert ema[19] is not None

    # EMA is initialized from SMA at the first valid index.
    assert abs(ema[19] - sma[19]) < 0.0001

    # Test 4: Sharpe Ratio
    equity_curve = [
        EquityPoint(date=date(2023, 1, 1) + timedelta(days=i), equity=10000 + i * 100)
        for i in range(50)
    ]

    trades = [
        Trade(
            entry_date=date(2023, 1, 1),
            exit_date=date(2023, 1, 10),
            entry_price=100.0,
            exit_price=105.0,
            pnl=500.0,
            return_pct=0.05,
        )
    ]

    metrics = compute_metrics(equity_curve=equity_curve, trades=trades)

    assert metrics.sharpe_ratio is not None
    assert isinstance(metrics.sharpe_ratio, float)
    assert metrics.total_return_pct is not None
    assert metrics.max_drawdown_pct is not None
    assert metrics.win_rate_pct is not None
    assert metrics.num_trades == 1

    # Test 5: All indicators together
    sma_vals = compute_sma(candles, period=20)
    ema_vals = compute_ema(candles, period=20)
    bb_m, bb_u, bb_l = compute_bollinger_bands(candles, period=20)

    assert len(sma_vals) == len(ema_vals) == len(bb_m) == 50

    # All indicators should begin producing values after the shared warm-up window.
    for i in range(19, 50):
        assert sma_vals[i] is not None
        assert ema_vals[i] is not None
        assert bb_m[i] is not None
        assert bb_u[i] is not None
        assert bb_l[i] is not None

    # Test 6: Basic edge cases
    empty_bb = compute_bollinger_bands([], period=20)
    assert len(empty_bb[0]) == 0

    empty_ema = compute_ema([], period=20)
    assert len(empty_ema) == 0

    single_equity = [EquityPoint(date=date(2023, 1, 1), equity=10000)]
    single_metrics = compute_metrics(equity_curve=single_equity, trades=[])
    assert single_metrics.sharpe_ratio == 0.0

    # Test 7: Constant price edge case
    # This validates zero-volatility behavior across indicators and metrics.
    constant_candles = [
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

    constant_sma = compute_sma(constant_candles, period=20)
    constant_ema = compute_ema(constant_candles, period=20)
    constant_bb_m, constant_bb_u, constant_bb_l = compute_bollinger_bands(
        constant_candles, period=20, num_std=2.0
    )

    # After the warm-up window, all indicator values should remain flat at 100.
    for i in range(19, 50):
        assert constant_sma[i] == 100
        assert constant_ema[i] == 100
        assert constant_bb_m[i] == 100
        assert constant_bb_u[i] == 100
        assert constant_bb_l[i] == 100

    constant_equity = [
        EquityPoint(date=date(2023, 1, 1) + timedelta(days=i), equity=10000)
        for i in range(50)
    ]
    constant_metrics = compute_metrics(equity_curve=constant_equity, trades=[])

    # Zero returns / zero volatility should yield Sharpe ratio 0.0, not crash.
    assert constant_metrics.sharpe_ratio == 0.0