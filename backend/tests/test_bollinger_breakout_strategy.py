"""Unit tests for Bollinger Band breakout signal generation."""
from datetime import date, timedelta
from typing import List, Optional

import pytest

from app.services.strategies.bollinger_breakout import generate_bollinger_breakout_signals


def _dates(n: int, base: date = date(2023, 1, 1)) -> List[date]:
    return [base + timedelta(days=i) for i in range(n)]


# ── BUY when close touches lower band ──────────────────────────────────

def test_buy_when_close_touches_lower_band():
    """close <= lower_band while flat → BUY signal emitted."""
    dates = _dates(3)
    closes = [100.0, 95.0, 90.0]
    upper: List[Optional[float]] = [110.0, 110.0, 110.0]
    lower: List[Optional[float]] = [90.0,  90.0,  90.0]
    signals = generate_bollinger_breakout_signals(
        dates=dates, closes=closes, upper_band=upper, lower_band=lower
    )
    assert len(signals) == 1
    assert signals[0].signal == 1
    assert signals[0].date == dates[2]
    assert "lower band" in signals[0].reason


# ── SELL when close touches upper band (only after a BUY) ──────────────

def test_sell_when_close_touches_upper_band_after_buy():
    """After a BUY, close >= upper_band → SELL signal emitted."""
    dates = _dates(4)
    closes = [100.0, 88.0, 100.0, 112.0]
    upper: List[Optional[float]] = [110.0, 110.0, 110.0, 110.0]
    lower: List[Optional[float]] = [90.0,  90.0,  90.0,  90.0]
    signals = generate_bollinger_breakout_signals(
        dates=dates, closes=closes, upper_band=upper, lower_band=lower
    )
    assert [s.signal for s in signals] == [1, -1]
    assert signals[0].date == dates[1]
    assert signals[1].date == dates[3]
    assert "upper band" in signals[1].reason


# ── Hold when price is between bands ───────────────────────────────────

def test_hold_when_price_between_bands():
    """Price stays between bands → no signals emitted."""
    dates = _dates(5)
    closes = [100.0, 101.0, 99.0, 100.5, 98.0]
    upper: List[Optional[float]] = [110.0] * 5
    lower: List[Optional[float]] = [90.0] * 5
    signals = generate_bollinger_breakout_signals(
        dates=dates, closes=closes, upper_band=upper, lower_band=lower
    )
    assert signals == []


# ── None warm-up bars are skipped ──────────────────────────────────────

def test_none_warmup_bars_are_skipped():
    """Bars with None bands are skipped; signal detected after warm-up."""
    dates = _dates(5)
    closes = [100.0, 100.0, 100.0, 100.0, 88.0]
    upper: List[Optional[float]] = [None, None, None, None, 110.0]
    lower: List[Optional[float]] = [None, None, None, None, 90.0]
    signals = generate_bollinger_breakout_signals(
        dates=dates, closes=closes, upper_band=upper, lower_band=lower
    )
    assert len(signals) == 1
    assert signals[0].signal == 1
    assert signals[0].date == dates[4]


# ── No SELL before first BUY ───────────────────────────────────────────

def test_no_sell_before_first_buy():
    """Price starts above upper band with no prior lower touch → no SELL."""
    dates = _dates(3)
    closes = [115.0, 112.0, 111.0]
    upper: List[Optional[float]] = [110.0, 110.0, 110.0]
    lower: List[Optional[float]] = [90.0,  90.0,  90.0]
    signals = generate_bollinger_breakout_signals(
        dates=dates, closes=closes, upper_band=upper, lower_band=lower
    )
    assert signals == []


# ── Alternating BUY/SELL cycles ────────────────────────────────────────

def test_alternating_buy_sell_cycles():
    """Multiple complete BUY/SELL cycles alternate correctly."""
    dates = _dates(6)
    # bar 0: between bands (hold)
    # bar 1: touches lower → BUY
    # bar 2: between bands (hold)
    # bar 3: touches upper → SELL
    # bar 4: touches lower → BUY
    # bar 5: touches upper → SELL
    closes = [100.0, 88.0, 100.0, 112.0, 88.0, 112.0]
    upper: List[Optional[float]] = [110.0] * 6
    lower: List[Optional[float]] = [90.0] * 6
    signals = generate_bollinger_breakout_signals(
        dates=dates, closes=closes, upper_band=upper, lower_band=lower
    )
    assert [s.signal for s in signals] == [1, -1, 1, -1]
    assert signals[0].date == dates[1]
    assert signals[1].date == dates[3]
    assert signals[2].date == dates[4]
    assert signals[3].date == dates[5]


# ── Mismatched array lengths raises ValueError ──────────────────────────

def test_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        generate_bollinger_breakout_signals(
            dates=_dates(3),
            closes=[100.0, 101.0],  # length 2 ≠ 3
            upper_band=[None, None, None],
            lower_band=[None, None, None],
        )


# ── Unsorted dates raises ValueError ───────────────────────────────────

def test_unsorted_dates_raises():
    dates = [date(2023, 1, 3), date(2023, 1, 1)]
    with pytest.raises(ValueError, match="sorted ascending"):
        generate_bollinger_breakout_signals(
            dates=dates,
            closes=[100.0, 101.0],
            upper_band=[110.0, 110.0],
            lower_band=[90.0, 90.0],
        )
