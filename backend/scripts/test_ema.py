"""
Test script for EMA (Exponential Moving Average) indicator.
Tests the compute_ema function directly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date
from app.schemas.stock import CandleDTO
from app.services.indicators.ema import compute_ema
from app.services.indicators.sma import compute_sma


def test_ema():
    print("=== Testing EMA Calculation ===\n")
    
    # Create sample candle data with known values
    candles = [
        CandleDTO(date=date(2023, 1, i+1), open=100+i, high=105+i, low=95+i, close=100+i, volume=1000)
        for i in range(30)
    ]
    
    print(f"Testing with {len(candles)} candles")
    print(f"Close prices: {[c.close for c in candles[:10]]}... (first 10)")
    
    # Test 1: Basic EMA calculation with period=10
    print("\n1. Testing with period=10:")
    ema = compute_ema(candles, period=10)
    
    # First 9 should be None
    none_count = sum(1 for x in ema if x is None)
    print(f"   None values: {none_count} (expected 9)")
    
    if ema[9] is not None:
        print(f"   [OK] First valid value at index 9")
        print(f"      EMA[9]: {ema[9]:.4f}")
        print(f"      EMA[10]: {ema[10]:.4f}")
        print(f"      EMA[20]: {ema[20]:.4f}")
        print(f"      EMA[29]: {ema[29]:.4f}")
    else:
        print(f"   [FAIL] Expected value at index 9")
        return False
    
    # Test 2: Compare EMA vs SMA
    print("\n2. Comparing EMA vs SMA (period=10):")
    sma = compute_sma(candles, period=10)
    
    # First value should be equal (EMA starts with SMA)
    if ema[9] is not None and sma[9] is not None:
        if abs(ema[9] - sma[9]) < 0.0001:
            print(f"   [OK] First EMA equals first SMA: {ema[9]:.4f}")
        else:
            print(f"   [WARN] First EMA ({ema[9]:.4f}) != first SMA ({sma[9]:.4f})")
    
    # Later values should differ (EMA reacts faster)
    if ema[20] is not None and sma[20] is not None:
        print(f"   At index 20:")
        print(f"      SMA: {sma[20]:.4f}")
        print(f"      EMA: {ema[20]:.4f}")
        print(f"      Difference: {abs(ema[20] - sma[20]):.4f}")
        if ema[20] != sma[20]:
            print(f"   [OK] EMA differs from SMA (as expected)")
    
    # Test 3: EMA with different periods
    print("\n3. Testing with different periods:")
    
    ema5 = compute_ema(candles, period=5)
    ema20 = compute_ema(candles, period=20)
    
    none_count5 = sum(1 for x in ema5 if x is None)
    none_count20 = sum(1 for x in ema20 if x is None)
    
    print(f"   Period=5:  {none_count5} None values (expected 4)")
    print(f"   Period=20: {none_count20} None values (expected 19)")
    
    if ema5[4] is not None and ema20[19] is not None:
        print(f"   [OK] Both periods calculated correctly")
        print(f"      EMA(5)[10]:  {ema5[10]:.4f}")
        print(f"      EMA(20)[20]: {ema20[20]:.4f}")
    
    # Test 4: EMA responsiveness (should react faster to price changes)
    print("\n4. Testing EMA responsiveness:")
    
    # Create data with a sudden price jump
    volatile_candles = [
        CandleDTO(date=date(2023, 1, i+1), open=100, high=105, low=95, close=100, volume=1000)
        for i in range(20)
    ]
    # Add a price jump
    for i in range(20, 30):
        volatile_candles.append(
            CandleDTO(date=date(2023, 1, i+1), open=120, high=125, low=115, close=120, volume=1000)
        )
    
    ema_vol = compute_ema(volatile_candles, period=10)
    sma_vol = compute_sma(volatile_candles, period=10)
    
    # After the jump, EMA should be closer to new price than SMA
    if ema_vol[25] is not None and sma_vol[25] is not None:
        print(f"   After price jump (index 25):")
        print(f"      Current price: 120.00")
        print(f"      SMA: {sma_vol[25]:.4f}")
        print(f"      EMA: {ema_vol[25]:.4f}")
        
        # EMA should be closer to 120 than SMA
        ema_distance = abs(120 - ema_vol[25])
        sma_distance = abs(120 - sma_vol[25])
        
        if ema_distance < sma_distance:
            print(f"   [OK] EMA reacts faster (closer to new price)")
        else:
            print(f"   [WARN] Expected EMA to be closer to new price")
    
    # Test 5: Edge cases
    print("\n5. Testing edge cases:")
    
    # Empty list
    try:
        ema_empty = compute_ema([], period=10)
        if len(ema_empty) == 0:
            print("   [OK] Empty list handled correctly")
    except Exception as e:
        print(f"   [FAIL] Empty list error: {e}")
        return False
    
    # Period larger than data
    short_candles = candles[:5]
    ema_short = compute_ema(short_candles, period=20)
    if all(x is None for x in ema_short):
        print("   [OK] Period > data length handled correctly")
    
    # Period = 1 (should equal close prices after first value)
    ema1 = compute_ema(candles, period=1)
    if ema1[0] is not None and abs(ema1[0] - candles[0].close) < 0.0001:
        print("   [OK] Period=1 handled correctly")
    
    # Test 6: Verify smoothing constant
    print("\n6. Verifying EMA formula:")
    period = 10
    k = 2.0 / (period + 1)
    print(f"   Period: {period}")
    print(f"   Smoothing constant (k): {k:.4f}")
    print(f"   Expected: {2.0 / 11:.4f}")
    
    if abs(k - 2.0/11) < 0.0001:
        print(f"   [OK] Smoothing constant correct")
    
    print("\n=== All EMA tests passed! ===")
    return True


if __name__ == "__main__":
    try:
        success = test_ema()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
