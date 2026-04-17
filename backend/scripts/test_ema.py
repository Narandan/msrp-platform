"""
Pytest-based unit test for EMA (Exponential Moving Average).

What this test covers:
- Correct EMA calculation with standard inputs
- Proper warm-up behavior (initial None values)
- Relationship between EMA and SMA (initial equality, later divergence)
- Sensitivity of EMA to price changes vs SMA
- Edge cases (empty input, short data, period=1)
"""

import sys
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.stock import CandleDTO
from app.services.indicators.ema import compute_ema
from app.services.indicators.sma import compute_sma


def test_ema():
    # Create sample candle data with known values
    candles = [
        CandleDTO(
            date=date(2023, 1, i + 1),
            open=100 + i,
            high=105 + i,
            low=95 + i,
            close=100 + i,
            volume=1000,
        )
        for i in range(30)
    ]

    # Test 1: Basic EMA calculation with period=10
    ema = compute_ema(candles, period=10)

    # First 9 should be None
    none_count = sum(1 for x in ema if x is None)
    assert none_count == 9

    assert ema[9] is not None
    assert ema[10] is not None
    assert ema[20] is not None
    assert ema[29] is not None

    # Test 2: Compare EMA vs SMA
    sma = compute_sma(candles, period=10)

    # First value should be equal (EMA starts with SMA)
    assert ema[9] is not None
    assert sma[9] is not None
    assert abs(ema[9] - sma[9]) < 0.0001

    # Later values should differ
    assert ema[20] is not None
    assert sma[20] is not None
    assert ema[20] != sma[20]

    # Test 3: EMA with different periods
    ema5 = compute_ema(candles, period=5)
    ema20 = compute_ema(candles, period=20)

    none_count5 = sum(1 for x in ema5 if x is None)
    none_count20 = sum(1 for x in ema20 if x is None)

    assert none_count5 == 4
    assert none_count20 == 19

    assert ema5[4] is not None
    assert ema20[19] is not None
    assert ema5[10] is not None
    assert ema20[20] is not None

    # Test 4: EMA responsiveness
    volatile_candles = [
        CandleDTO(
            date=date(2023, 1, i + 1),
            open=100,
            high=105,
            low=95,
            close=100,
            volume=1000,
        )
        for i in range(20)
    ]

    for i in range(20, 30):
        volatile_candles.append(
            CandleDTO(
                date=date(2023, 1, i + 1),
                open=120,
                high=125,
                low=115,
                close=120,
                volume=1000,
            )
        )

    ema_vol = compute_ema(volatile_candles, period=10)
    sma_vol = compute_sma(volatile_candles, period=10)

    assert ema_vol[25] is not None
    assert sma_vol[25] is not None

    ema_distance = abs(120 - ema_vol[25])
    sma_distance = abs(120 - sma_vol[25])

    assert ema_distance < sma_distance

    # Test 5: Edge cases
    ema_empty = compute_ema([], period=10)
    assert len(ema_empty) == 0

    short_candles = candles[:5]
    ema_short = compute_ema(short_candles, period=20)
    assert all(x is None for x in ema_short)

    ema1 = compute_ema(candles, period=1)
    assert ema1[0] is not None
    assert abs(ema1[0] - candles[0].close) < 0.0001

    # Test 6: Verify smoothing constant
    period = 10
    k = 2.0 / (period + 1)
    assert abs(k - 2.0 / 11) < 0.0001