"""Unit tests for RSI threshold signal generation."""
from datetime import date, timedelta
import pytest

from app.services.strategies.rsi_threshold import generate_rsi_threshold_signals


def _dates(n, base=date(2023, 1, 1)):
    return [base + timedelta(days=i) for i in range(n)]


# ─── 4.2  BUY when RSI drops below oversold ──────────────────────────────────

def test_buy_when_rsi_below_oversold():
    dates = _dates(3)
    closes = [100.0, 98.0, 96.0]
    rsi = [None, 35.0, 25.0]  # 25 < 30 (default oversold)
    signals = generate_rsi_threshold_signals(dates=dates, closes=closes, rsi=rsi)
    assert len(signals) == 1
    assert signals[0].signal == 1
    assert signals[0].date == dates[2]


# ─── 4.3  SELL when RSI rises above overbought (after a BUY) ─────────────────

def test_sell_when_rsi_above_overbought_after_buy():
    dates = _dates(4)
    closes = [100.0, 98.0, 102.0, 105.0]
    rsi = [None, 25.0, 50.0, 75.0]  # buy at idx 1, sell at idx 3
    signals = generate_rsi_threshold_signals(dates=dates, closes=closes, rsi=rsi)
    assert len(signals) == 2
    assert signals[0].signal == 1
    assert signals[0].date == dates[1]
    assert signals[1].signal == -1
    assert signals[1].date == dates[3]


# ─── 4.4  Hold when RSI stays between thresholds ─────────────────────────────

def test_no_signal_when_rsi_between_thresholds():
    dates = _dates(5)
    closes = [100.0] * 5
    rsi = [50.0] * 5  # always between 30 and 70
    signals = generate_rsi_threshold_signals(dates=dates, closes=closes, rsi=rsi)
    assert signals == []


# ─── 4.5  No signals when all RSI values are None ────────────────────────────

def test_no_signals_for_all_none_rsi():
    signals = generate_rsi_threshold_signals(
        dates=_dates(5), closes=[100.0] * 5, rsi=[None] * 5
    )
    assert signals == []


# ─── 4.6  No duplicate BUY signals ───────────────────────────────────────────

def test_no_duplicate_buy_signals():
    dates = _dates(5)
    closes = [100.0] * 5
    rsi = [25.0, 22.0, 20.0, 18.0, 15.0]  # stays below oversold the whole time
    signals = generate_rsi_threshold_signals(dates=dates, closes=closes, rsi=rsi)
    buy_signals = [s for s in signals if s.signal == 1]
    assert len(buy_signals) == 1


# ─── 4.7  No duplicate SELL signals ──────────────────────────────────────────

def test_no_duplicate_sell_signals():
    dates = _dates(6)
    closes = [100.0] * 6
    # buy first, then RSI stays above overbought for multiple bars
    rsi = [25.0, 50.0, 75.0, 80.0, 85.0, 90.0]
    signals = generate_rsi_threshold_signals(dates=dates, closes=closes, rsi=rsi)
    sell_signals = [s for s in signals if s.signal == -1]
    assert len(sell_signals) == 1


# ─── 4.8  No SELL before first BUY ───────────────────────────────────────────

def test_no_sell_before_first_buy():
    dates = _dates(4)
    closes = [100.0] * 4
    # RSI starts above overbought with no prior oversold crossing
    rsi = [75.0, 80.0, 85.0, 90.0]
    signals = generate_rsi_threshold_signals(dates=dates, closes=closes, rsi=rsi)
    assert signals == []


# ─── 4.9  Multiple alternating BUY/SELL cycles ───────────────────────────────

def test_multiple_alternating_buy_sell_cycles():
    dates = _dates(6)
    closes = [100.0] * 6
    # oversold -> overbought -> oversold -> overbought
    rsi = [25.0, 50.0, 75.0, 50.0, 25.0, 75.0]
    signals = generate_rsi_threshold_signals(dates=dates, closes=closes, rsi=rsi)
    assert [s.signal for s in signals] == [1, -1, 1, -1]
    assert signals[0].date == dates[0]
    assert signals[1].date == dates[2]
    assert signals[2].date == dates[4]
    assert signals[3].date == dates[5]


# ─── 4.10  Custom threshold values ───────────────────────────────────────────

def test_custom_thresholds_fire_at_correct_levels():
    dates = _dates(4)
    closes = [100.0] * 4
    # With oversold=40, overbought=60: rsi=45 is NOT oversold, rsi=35 IS
    rsi = [45.0, 35.0, 50.0, 65.0]
    signals = generate_rsi_threshold_signals(
        dates=dates, closes=closes, rsi=rsi, oversold=40.0, overbought=60.0
    )
    assert len(signals) == 2
    assert signals[0].signal == 1
    assert signals[0].date == dates[1]   # 35 < 40
    assert signals[1].signal == -1
    assert signals[1].date == dates[3]   # 65 > 60


# ─── 4.11  Validation errors ─────────────────────────────────────────────────

def test_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        generate_rsi_threshold_signals(
            dates=_dates(3), closes=[100.0, 101.0], rsi=[None, None, None]
        )


def test_unsorted_dates_raises():
    dates = [date(2023, 1, 2), date(2023, 1, 1)]
    with pytest.raises(ValueError, match="sorted ascending"):
        generate_rsi_threshold_signals(
            dates=dates, closes=[100.0, 101.0], rsi=[None, None]
        )


def test_oversold_gte_overbought_raises():
    with pytest.raises(ValueError, match="oversold must be < overbought"):
        generate_rsi_threshold_signals(
            dates=_dates(3), closes=[100.0] * 3, rsi=[None] * 3,
            oversold=70.0, overbought=30.0
        )


def test_oversold_equal_overbought_raises():
    with pytest.raises(ValueError, match="oversold must be < overbought"):
        generate_rsi_threshold_signals(
            dates=_dates(3), closes=[100.0] * 3, rsi=[None] * 3,
            oversold=50.0, overbought=50.0
        )
