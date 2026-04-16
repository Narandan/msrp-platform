"""
Pytest-based unit test for Sharpe ratio calculation through compute_metrics.

What this test covers:
- Positive Sharpe ratio for a steadily increasing equity curve
- Negative Sharpe ratio for a steadily decreasing equity curve
- Zero Sharpe ratio for a flat equity curve
- Handling of volatile equity without crashing
- Edge cases such as single-point and two-point equity curves
- Presence of the full metrics payload
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.backtest import EquityPoint, Trade
from app.services.backtesting.metrics import compute_metrics


def test_sharpe_ratio():
    start_date = date(2023, 1, 1)

    # Test 1: Steady upward trend (should have positive Sharpe)
    equity_up = [
        EquityPoint(date=start_date + timedelta(days=i), equity=10000 + i * 100)
        for i in range(252)
    ]
    trades_up = [
        Trade(
            entry_date=start_date,
            exit_date=start_date + timedelta(days=100),
            entry_price=100.0,
            exit_price=110.0,
            pnl=1000.0,
            return_pct=0.10,
        )
    ]

    metrics_up = compute_metrics(equity_curve=equity_up, trades=trades_up)
    assert metrics_up.sharpe_ratio > 0

    # Test 2: Steady downward trend (should have negative Sharpe)
    equity_down = [
        EquityPoint(date=start_date + timedelta(days=i), equity=10000 - i * 50)
        for i in range(100)
    ]
    trades_down = [
        Trade(
            entry_date=start_date,
            exit_date=start_date + timedelta(days=50),
            entry_price=100.0,
            exit_price=90.0,
            pnl=-1000.0,
            return_pct=-0.10,
        )
    ]

    metrics_down = compute_metrics(equity_curve=equity_down, trades=trades_down)
    assert metrics_down.sharpe_ratio < 0

    # Test 3: Flat equity (zero volatility)
    equity_flat = [
        EquityPoint(date=start_date + timedelta(days=i), equity=10000.0)
        for i in range(50)
    ]

    metrics_flat = compute_metrics(equity_curve=equity_flat, trades=[])
    assert metrics_flat.sharpe_ratio == 0.0

    # Test 4: High volatility (should run without error)
    equity_volatile = []
    equity_val = 10000.0

    for i in range(100):
        if i % 2 == 0:
            equity_val += 200
        else:
            equity_val -= 100

        equity_volatile.append(
            EquityPoint(date=start_date + timedelta(days=i), equity=equity_val)
        )

    metrics_volatile = compute_metrics(equity_curve=equity_volatile, trades=[])
    assert metrics_volatile.sharpe_ratio is not None

    # Test 5: Edge cases

    # Single point
    equity_single = [EquityPoint(date=start_date, equity=10000.0)]
    metrics_single = compute_metrics(equity_curve=equity_single, trades=[])
    assert metrics_single.sharpe_ratio == 0.0

    # Two points
    equity_two = [
        EquityPoint(date=start_date, equity=10000.0),
        EquityPoint(date=start_date + timedelta(days=1), equity=10100.0),
    ]
    metrics_two = compute_metrics(equity_curve=equity_two, trades=[])
    assert metrics_two.sharpe_ratio is not None

    # Test 6: Verify all metrics present
    sample_equity = [
        EquityPoint(date=start_date + timedelta(days=i), equity=10000 + i * 50)
        for i in range(50)
    ]
    sample_trades = [
        Trade(
            entry_date=start_date,
            exit_date=start_date + timedelta(days=10),
            entry_price=100.0,
            exit_price=105.0,
            pnl=500.0,
            return_pct=0.05,
        ),
        Trade(
            entry_date=start_date + timedelta(days=20),
            exit_date=start_date + timedelta(days=30),
            entry_price=105.0,
            exit_price=110.0,
            pnl=500.0,
            return_pct=0.048,
        ),
    ]

    metrics = compute_metrics(equity_curve=sample_equity, trades=sample_trades)

    assert metrics.total_return_pct is not None
    assert metrics.max_drawdown_pct is not None
    assert metrics.win_rate_pct is not None
    assert metrics.num_trades is not None
    assert metrics.sharpe_ratio is not None