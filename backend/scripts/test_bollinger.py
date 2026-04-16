"""
Pytest-based unit test for the Bollinger Bands indicator.

What this test covers:
- Basic Bollinger Bands calculation on predictable sample data
- Correct warm-up behavior (initial None values before enough candles exist)
- Proper band ordering: upper >= middle >= lower
- Behavior with different periods and standard deviation multipliers
- Edge cases such as empty input and period > data length
"""

import sys
from pathlib import Path
from datetime import date

# Allow this test file to import application modules when run from backend/
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.stock import CandleDTO
from app.services.indicators.bollinger import compute_bollinger_bands


def test_bollinger_bands():
    # Build simple monotonic candle data so the expected behavior is stable
    # and easy to reason about.
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

    # Standard Bollinger Bands configuration.
    middle, upper, lower = compute_bollinger_bands(candles, period=20, num_std=2.0)

    # With a 20-period window, the first 19 outputs should be None because
    # there is not enough history yet to compute the bands.
    none_count = sum(1 for x in middle if x is None)
    assert none_count == 19

    # The first complete window should produce valid values.
    assert middle[19] is not None
    assert upper[19] is not None
    assert lower[19] is not None

    # The final point should also have valid band values.
    assert middle[-1] is not None
    assert upper[-1] is not None
    assert lower[-1] is not None

    # For all fully computed points, the bands must be ordered correctly:
    # upper band >= middle band >= lower band.
    for i in range(19, len(candles)):
        if upper[i] is not None and middle[i] is not None and lower[i] is not None:
            assert upper[i] >= middle[i] >= lower[i], f"Band ordering violated at index {i}"

    # Verify warm-up behavior for a smaller period as well.
    middle5, upper5, lower5 = compute_bollinger_bands(candles, period=5, num_std=2.0)
    none_count5 = sum(1 for x in middle5 if x is None)
    assert none_count5 == 4
    assert middle5[4] is not None
    assert upper5[4] is not None
    assert lower5[4] is not None

    # A smaller standard deviation multiplier should produce narrower bands.
    middle1, upper1, lower1 = compute_bollinger_bands(candles, period=20, num_std=1.0)
    assert upper1[19] is not None
    assert lower1[19] is not None
    assert upper[19] is not None
    assert lower[19] is not None

    width_std2 = upper[19] - lower[19]
    width_std1 = upper1[19] - lower1[19]
    assert width_std1 < width_std2

    # Empty input should return empty outputs instead of raising.
    m, u, l = compute_bollinger_bands([], period=20)
    assert len(m) == 0
    assert len(u) == 0
    assert len(l) == 0

    # If the requested period is larger than the available data,
    # no bands should be computable yet.
    short_candles = candles[:5]
    m_short, u_short, l_short = compute_bollinger_bands(short_candles, period=20)
    assert all(x is None for x in m_short)
    assert all(x is None for x in u_short)
    assert all(x is None for x in l_short)