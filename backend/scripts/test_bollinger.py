"""
Test script for Bollinger Bands indicator.
Tests the compute_bollinger_bands function directly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date
from app.schemas.stock import CandleDTO
from app.services.indicators.bollinger import compute_bollinger_bands


def test_bollinger_bands():
    print("=== Testing Bollinger Bands Calculation ===\n")
    
    # Create sample candle data with known values
    candles = [
        CandleDTO(date=date(2023, 1, i+1), open=100+i, high=105+i, low=95+i, close=100+i, volume=1000)
        for i in range(30)
    ]
    
    print(f"Testing with {len(candles)} candles")
    print(f"Close prices: {[c.close for c in candles[:10]]}... (first 10)")
    
    # Test with default parameters (period=20, std=2.0)
    print("\n1. Testing with default parameters (period=20, std=2.0):")
    middle, upper, lower = compute_bollinger_bands(candles, period=20, num_std=2.0)
    
    # First 19 should be None
    none_count = sum(1 for x in middle if x is None)
    print(f"   None values: {none_count} (expected 19)")
    
    # Check that we have values after period-1
    if middle[19] is not None:
        print(f"   [OK] First valid value at index 19")
        print(f"      Middle: {middle[19]:.2f}")
        print(f"      Upper:  {upper[19]:.2f}")
        print(f"      Lower:  {lower[19]:.2f}")
    else:
        print(f"   [FAIL] Expected value at index 19")
        return False
    
    # Check last value
    if middle[-1] is not None:
        print(f"   Last value:")
        print(f"      Middle: {middle[-1]:.2f}")
        print(f"      Upper:  {upper[-1]:.2f}")
        print(f"      Lower:  {lower[-1]:.2f}")
    
    # Verify upper > middle > lower
    for i in range(19, len(candles)):
        if upper[i] is not None and middle[i] is not None and lower[i] is not None:
            if not (upper[i] >= middle[i] >= lower[i]):
                print(f"   [FAIL] Band ordering violated at index {i}")
                return False
    print(f"   [OK] Band ordering correct (upper >= middle >= lower)")
    
    # Test with smaller period
    print("\n2. Testing with period=5:")
    middle5, upper5, lower5 = compute_bollinger_bands(candles, period=5, num_std=2.0)
    none_count5 = sum(1 for x in middle5 if x is None)
    print(f"   None values: {none_count5} (expected 4)")
    if middle5[4] is not None:
        print(f"   [OK] First valid value at index 4")
        print(f"      Middle: {middle5[4]:.2f}")
    
    # Test with different std
    print("\n3. Testing with num_std=1.0:")
    middle1, upper1, lower1 = compute_bollinger_bands(candles, period=20, num_std=1.0)
    if upper1[19] is not None and upper[19] is not None:
        # Bands should be narrower with smaller std
        width_std2 = upper[19] - lower[19]
        width_std1 = upper1[19] - lower1[19]
        print(f"   Width with std=2.0: {width_std2:.2f}")
        print(f"   Width with std=1.0: {width_std1:.2f}")
        if width_std1 < width_std2:
            print(f"   [OK] Bands narrower with smaller std")
        else:
            print(f"   [FAIL] Expected narrower bands")
            return False
    
    # Test edge cases
    print("\n4. Testing edge cases:")
    
    # Empty list
    try:
        m, u, l = compute_bollinger_bands([], period=20)
        if len(m) == 0:
            print("   [OK] Empty list handled correctly")
    except Exception as e:
        print(f"   [FAIL] Empty list error: {e}")
        return False
    
    # Period larger than data
    short_candles = candles[:5]
    m_short, u_short, l_short = compute_bollinger_bands(short_candles, period=20)
    if all(x is None for x in m_short):
        print("   [OK] Period > data length handled correctly")
    
    print("\n=== All Bollinger Bands tests passed! ===")
    return True


if __name__ == "__main__":
    import sys
    try:
        success = test_bollinger_bands()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
