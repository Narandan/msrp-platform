"""
Comprehensive test script for all changes made today.
Tests all new features without requiring a running server.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, timedelta
from app.schemas.stock import CandleDTO, SymbolSearchResult
from app.schemas.backtest import BacktestMetrics, EquityPoint, Trade
from app.services.indicators.bollinger import compute_bollinger_bands
from app.services.indicators.ema import compute_ema
from app.services.indicators.sma import compute_sma
from app.services.backtesting.metrics import compute_metrics


def test_all_changes():
    print("=== Testing All Changes Made Today ===\n")
    
    # Create test data
    candles = [
        CandleDTO(date=date(2023, 1, 1) + timedelta(days=i), open=100+i, high=105+i, low=95+i, close=100+i, volume=1000)
        for i in range(50)
    ]
    
    print("Test data created: 50 candles\n")
    
    # Test 1: Symbol Search Schema
    print("1. Testing SymbolSearchResult schema...")
    try:
        result = SymbolSearchResult(ticker="AAPL", name="Apple Inc.")
        assert result.ticker == "AAPL"
        assert result.name == "Apple Inc."
        print("   [OK] SymbolSearchResult schema works")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 2: Bollinger Bands
    print("\n2. Testing Bollinger Bands...")
    try:
        middle, upper, lower = compute_bollinger_bands(candles, period=20, num_std=2.0)
        assert len(middle) == 50
        assert middle[19] is not None
        assert upper[19] > middle[19] > lower[19]
        print(f"   [OK] Bollinger Bands calculated")
        print(f"      Sample: Middle={middle[25]:.2f}, Upper={upper[25]:.2f}, Lower={lower[25]:.2f}")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 3: EMA
    print("\n3. Testing EMA...")
    try:
        ema = compute_ema(candles, period=20)
        sma = compute_sma(candles, period=20)
        assert len(ema) == 50
        assert ema[19] is not None
        # First value should equal SMA
        assert abs(ema[19] - sma[19]) < 0.0001
        print(f"   [OK] EMA calculated")
        print(f"      EMA[25]={ema[25]:.2f}, SMA[25]={sma[25]:.2f}")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 4: Sharpe Ratio
    print("\n4. Testing Sharpe Ratio...")
    try:
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
                return_pct=0.05
            )
        ]
        
        metrics = compute_metrics(equity_curve=equity_curve, trades=trades)
        assert metrics.sharpe_ratio is not None
        assert isinstance(metrics.sharpe_ratio, float)
        assert metrics.total_return_pct is not None
        assert metrics.max_drawdown_pct is not None
        assert metrics.win_rate_pct is not None
        assert metrics.num_trades == 1
        
        print(f"   [OK] Sharpe Ratio calculated")
        print(f"      Sharpe={metrics.sharpe_ratio:.4f}")
        print(f"      Total Return={metrics.total_return_pct:.2f}%")
        print(f"      Max Drawdown={metrics.max_drawdown_pct:.2f}%")
    except Exception as e:
        print(f"   [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Integration - All indicators together
    print("\n5. Testing all indicators together...")
    try:
        sma_vals = compute_sma(candles, period=20)
        ema_vals = compute_ema(candles, period=20)
        bb_m, bb_u, bb_l = compute_bollinger_bands(candles, period=20)
        
        # Check they all have the same length
        assert len(sma_vals) == len(ema_vals) == len(bb_m) == 50
        
        # Check they all have values at the same indices
        for i in range(19, 50):
            assert sma_vals[i] is not None
            assert ema_vals[i] is not None
            assert bb_m[i] is not None
            assert bb_u[i] is not None
            assert bb_l[i] is not None
        
        print(f"   [OK] All indicators work together")
        print(f"      At index 30:")
        print(f"         SMA: {sma_vals[30]:.2f}")
        print(f"         EMA: {ema_vals[30]:.2f}")
        print(f"         BB:  {bb_l[30]:.2f} < {bb_m[30]:.2f} < {bb_u[30]:.2f}")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 6: Edge cases
    print("\n6. Testing edge cases...")
    try:
        # Empty data
        empty_bb = compute_bollinger_bands([], period=20)
        assert len(empty_bb[0]) == 0
        
        empty_ema = compute_ema([], period=20)
        assert len(empty_ema) == 0
        
        # Single point equity
        single_equity = [EquityPoint(date=date(2023, 1, 1), equity=10000)]
        single_metrics = compute_metrics(equity_curve=single_equity, trades=[])
        assert single_metrics.sharpe_ratio == 0.0
        
        print(f"   [OK] Edge cases handled correctly")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    print("\n=== All Tests Passed! ===")
    print("\nSummary of changes tested:")
    print("  - Symbol search schema (SymbolSearchResult)")
    print("  - Bollinger Bands indicator")
    print("  - EMA (Exponential Moving Average)")
    print("  - Sharpe Ratio in backtest metrics")
    print("  - Integration of all indicators")
    print("  - Edge case handling")
    print("\nNo breaking changes detected!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_all_changes()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
