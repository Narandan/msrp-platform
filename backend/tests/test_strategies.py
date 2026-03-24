"""Unit tests for SMA threshold and SMA crossover signal generation."""
from datetime import date, timedelta
import pytest

from app.services.strategies.sma_threshold import generate_sma_threshold_signals
from app.services.strategies.sma_crossover import generate_sma_crossover_signals


def _dates(n, base=date(2023, 1, 1)):
    return [base + timedelta(days=i) for i in range(n)]


# ─── SMA Threshold ───────────────────────────────────────────────────────────

def test_threshold_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        generate_sma_threshold_signals(dates=_dates(3), closes=[1, 2], sma=[None, None, None])


def test_threshold_unsorted_dates_raises():
    dates = [date(2023, 1, 2), date(2023, 1, 1)]
    with pytest.raises(ValueError, match="sorted ascending"):
        generate_sma_threshold_signals(dates=dates, closes=[100.0, 101.0], sma=[None, None])


def test_threshold_all_none_sma_no_signals():
    signals = generate_sma_threshold_signals(
        dates=_dates(5), closes=[100.0] * 5, sma=[None] * 5
    )
    assert signals == []


def test_threshold_buy_when_close_above_sma():
    dates = _dates(3)
    closes = [100.0, 105.0, 110.0]
    sma = [None, 100.0, 100.0]
    signals = generate_sma_threshold_signals(dates=dates, closes=closes, sma=sma)
    assert len(signals) == 1
    assert signals[0].signal == 1
    assert signals[0].date == dates[1]


def test_threshold_sell_when_close_drops_below_sma():
    dates = _dates(4)
    closes = [105.0, 110.0, 95.0, 90.0]
    sma = [100.0, 100.0, 100.0, 100.0]
    signals = generate_sma_threshold_signals(dates=dates, closes=closes, sma=sma)
    # Day 0: buy (105 > 100), Day 2: sell (95 < 100)
    assert signals[0].signal == 1
    assert signals[1].signal == -1
    assert signals[1].date == dates[2]


def test_threshold_no_duplicate_signals():
    # Close stays above SMA the whole time — only one BUY, no repeated signals
    dates = _dates(5)
    closes = [110.0] * 5
    sma = [100.0] * 5
    signals = generate_sma_threshold_signals(dates=dates, closes=closes, sma=sma)
    assert len(signals) == 1
    assert signals[0].signal == 1


def test_threshold_alternating_signals():
    dates = _dates(6)
    closes = [110, 90, 110, 90, 110, 90]
    sma = [100.0] * 6
    signals = generate_sma_threshold_signals(dates=dates, closes=closes, sma=sma)
    expected = [1, -1, 1, -1, 1, -1]
    assert [s.signal for s in signals] == expected


# ─── SMA Crossover ───────────────────────────────────────────────────────────

def test_crossover_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        generate_sma_crossover_signals(
            dates=_dates(3), closes=[1, 2, 3],
            fast_sma=[None, None], slow_sma=[None, None, None]
        )


def test_crossover_all_none_no_signals():
    signals = generate_sma_crossover_signals(
        dates=_dates(5), closes=[100.0] * 5,
        fast_sma=[None] * 5, slow_sma=[None] * 5
    )
    assert signals == []


def test_crossover_buy_when_fast_crosses_above_slow():
    dates = _dates(3)
    closes = [100.0] * 3
    fast = [None, 95.0, 105.0]
    slow = [None, 100.0, 100.0]
    signals = generate_sma_crossover_signals(dates=dates, closes=closes, fast_sma=fast, slow_sma=slow)
    assert len(signals) == 1
    assert signals[0].signal == 1
    assert signals[0].date == dates[2]


def test_crossover_sell_when_fast_drops_below_slow():
    dates = _dates(4)
    closes = [100.0] * 4
    fast = [None, 105.0, 105.0, 95.0]
    slow = [None, 100.0, 100.0, 100.0]
    signals = generate_sma_crossover_signals(dates=dates, closes=closes, fast_sma=fast, slow_sma=slow)
    assert signals[0].signal == 1   # buy at index 1
    assert signals[1].signal == -1  # sell at index 3


def test_crossover_no_duplicate_signals():
    dates = _dates(5)
    closes = [100.0] * 5
    fast = [None, 110.0, 110.0, 110.0, 110.0]
    slow = [None, 100.0, 100.0, 100.0, 100.0]
    signals = generate_sma_crossover_signals(dates=dates, closes=closes, fast_sma=fast, slow_sma=slow)
    assert len(signals) == 1
    assert signals[0].signal == 1
