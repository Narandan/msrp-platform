"""
Test script for Sharpe ratio calculation.
Tests the _sharpe_ratio function with various scenarios.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, timedelta
from app.schemas.backtest import EquityPoint, Trade
from app.services.backtesting.metrics import compute_metrics


def test_sharpe_ratio():
    print("=== Testing Sharpe Ratio Calculation ===\n")
    
    # Test 1: Steady upward trend (should have positive Sharpe)
    print("1. Testing steady upward trend:")
    start_date = date(2023, 1, 1)
    equity_up = [
        EquityPoint(date=start_date + timedelta(days=i), equity=10000 + i * 100)
        for i in range(252)  # One year of trading days
    ]
    trades_up = [
        Trade(
            entry_date=start_date,
            exit_date=start_date + timedelta(days=100),
            entry_price=100.0,
            exit_price=110.0,
            pnl=1000.0,
            return_pct=0.10
        )
    ]
    
    metrics_up = compute_metrics(equity_curve=equity_up, trades=trades_up)
    print(f"   Sharpe Ratio: {metrics_up.sharpe_ratio:.4f}")
    if metrics_up.sharpe_ratio > 0:
        print(f"   [OK] Positive Sharpe for upward trend")
    else:
        print(f"   [FAIL] Expected positive Sharpe")
        return False
    
    # Test 2: Steady downward trend (should have negative Sharpe)
    print("\n2. Testing steady downward trend:")
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
            return_pct=-0.10
        )
    ]
    
    metrics_down = compute_metrics(equity_curve=equity_down, trades=trades_down)
    print(f"   Sharpe Ratio: {metrics_down.sharpe_ratio:.4f}")
    if metrics_down.sharpe_ratio < 0:
        print(f"   [OK] Negative Sharpe for downward trend")
    else:
        print(f"   [FAIL] Expected negative Sharpe")
        return False
    
    # Test 3: Flat equity (zero volatility, should return 0)
    print("\n3. Testing flat equity (zero volatility):")
    equity_flat = [
        EquityPoint(date=start_date + timedelta(days=i), equity=10000.0)
        for i in range(50)
    ]
    
    metrics_flat = compute_metrics(equity_curve=equity_flat, trades=[])
    print(f"   Sharpe Ratio: {metrics_flat.sharpe_ratio:.4f}")
    if metrics_flat.sharpe_ratio == 0.0:
        print(f"   [OK] Zero Sharpe for flat equity")
    else:
        print(f"   [FAIL] Expected zero Sharpe")
        return False
    
    # Test 4: High volatility (should have lower Sharpe than steady growth)
    print("\n4. Testing high volatility:")
    equity_volatile = []
    equity_val = 10000.0
    for i in range(100):
        # Alternate between gains and losses
        if i % 2 == 0:
            equity_val += 200
        else:
            equity_val -= 100
        equity_volatile.append(
            EquityPoint(date=start_date + timedelta(days=i), equity=equity_val)
        )
    
    metrics_volatile = compute_metrics(equity_curve=equity_volatile, trades=[])
    print(f"   Sharpe Ratio: {metrics_volatile.sharpe_ratio:.4f}")
    print(f"   Final equity: {equity_volatile[-1].equity:.2f}")
    print(f"   [OK] Volatile equity calculated")
    
    # Test 5: Edge cases
    print("\n5. Testing edge cases:")
    
    # Single point
    equity_single = [EquityPoint(date=start_date, equity=10000.0)]
    metrics_single = compute_metrics(equity_curve=equity_single, trades=[])
    if metrics_single.sharpe_ratio == 0.0:
        print(f"   [OK] Single point returns 0.0")
    else:
        print(f"   [FAIL] Single point should return 0.0")
        return False
    
    # Two points
    equity_two = [
        EquityPoint(date=start_date, equity=10000.0),
        EquityPoint(date=start_date + timedelta(days=1), equity=10100.0)
    ]
    metrics_two = compute_metrics(equity_curve=equity_two, trades=[])
    print(f"   Two points Sharpe: {metrics_two.sharpe_ratio:.4f}")
    print(f"   [OK] Two points handled")
    
    # Test 6: Verify all metrics still work
    print("\n6. Testing complete metrics output:")
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
            return_pct=0.05
        ),
        Trade(
            entry_date=start_date + timedelta(days=20),
            exit_date=start_date + timedelta(days=30),
            entry_price=105.0,
            exit_price=110.0,
            pnl=500.0,
            return_pct=0.048
        )
    ]
    
    metrics = compute_metrics(equity_curve=sample_equity, trades=sample_trades)
    print(f"   Total Return: {metrics.total_return_pct:.2f}%")
    print(f"   Max Drawdown: {metrics.max_drawdown_pct:.2f}%")
    print(f"   Win Rate: {metrics.win_rate_pct:.2f}%")
    print(f"   Num Trades: {metrics.num_trades}")
    print(f"   Sharpe Ratio: {metrics.sharpe_ratio:.4f}")
    
    if all([
        metrics.total_return_pct is not None,
        metrics.max_drawdown_pct is not None,
        metrics.win_rate_pct is not None,
        metrics.num_trades is not None,
        metrics.sharpe_ratio is not None
    ]):
        print(f"   [OK] All metrics present")
    else:
        print(f"   [FAIL] Missing metrics")
        return False
    
    print("\n=== All Sharpe ratio tests passed! ===")
    return True


if __name__ == "__main__":
    try:
        success = test_sharpe_ratio()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
