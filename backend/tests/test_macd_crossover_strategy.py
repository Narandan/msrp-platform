"""Unit tests for MACD crossover signal generation."""
from datetime import date, timedelta
from typing import List, Optional

import pytest

from app.services.strategies.macd_crossover import generate_macd_crossover_signals


def _dates(n: int, base: date = date(2023, 1, 1)) -> List[date]:
    return [base + timedelta(days=i) for i in range(n)]


# ── 1. BUY on bullish cross ───────────────────────────────────────────────

def test_buy_on_bullish_cross():
    """prev_macd <= prev_signal, current macd > signal → BUY."""
    dates = _dates(3)
    closes = [100.0, 101.0, 102.0]
    # bar 0: macd=-1, signal=0  (prev state)
    # bar 1: macd=-0.5, signal=0 (prev_macd <= prev_signal still)
    # bar 2: macd=0.5, signal=0  → bullish cross
    macd_line:   List[Optional[float]] = [-1.0, -0.5, 0.5]
    signal_line: List[Optional[float]] = [ 0.0,  0.0, 0.0]
    signals = generate_macd_crossover_signals(
        dates=dates, closes=closes, macd_line=macd_line, signal_line=signal_line
    )
    assert len(signals) == 1
    assert signals[0].signal == 1
    assert signals[0].date == dates[2]


# ── 2. SELL on bearish cross (only after a BUY) ───────────────────────────

def test_sell_on_bearish_cross_after_buy():
    """prev_macd >= prev_signal, current macd < signal → SELL (only if long)."""
    dates = _dates(4)
    closes = [100.0] * 4
    # bar 0: macd=-1, signal=0
    # bar 1: macd=1, signal=0  → bullish cross → BUY
    # bar 2: macd=0.5, signal=0 (still above)
    # bar 3: macd=-0.5, signal=0 → bearish cross → SELL
    macd_line:   List[Optional[float]] = [-1.0, 1.0, 0.5, -0.5]
    signal_line: List[Optional[float]] = [ 0.0, 0.0, 0.0,  0.0]
    signals = generate_macd_crossover_signals(
        dates=dates, closes=closes, macd_line=macd_line, signal_line=signal_line
    )
    assert [s.signal for s in signals] == [1, -1]
    assert signals[0].date == dates[1]
    assert signals[1].date == dates[3]


# ── 3. No signal when MACD stays above signal throughout ─────────────────

def test_no_signal_when_no_crossover():
    """MACD stays above signal the whole time → no signals."""
    dates = _dates(5)
    closes = [100.0] * 5
    macd_line:   List[Optional[float]] = [1.0, 1.5, 2.0, 1.8, 1.2]
    signal_line: List[Optional[float]] = [0.0, 0.0, 0.0, 0.0, 0.0]
    signals = generate_macd_crossover_signals(
        dates=dates, closes=closes, macd_line=macd_line, signal_line=signal_line
    )
    assert signals == []


# ── 4. None warm-up bars are skipped ─────────────────────────────────────

def test_none_warmup_bars_are_skipped():
    """Bars with None macd or signal are skipped; cross detected after warm-up."""
    dates = _dates(5)
    closes = [100.0] * 5
    # first 2 bars are None (warm-up), cross happens at bar 4
    macd_line:   List[Optional[float]] = [None, None, -1.0, -0.5, 0.5]
    signal_line: List[Optional[float]] = [None, None,  0.0,  0.0, 0.0]
    signals = generate_macd_crossover_signals(
        dates=dates, closes=closes, macd_line=macd_line, signal_line=signal_line
    )
    assert len(signals) == 1
    assert signals[0].signal == 1
    assert signals[0].date == dates[4]


# ── 5. No SELL before first BUY ──────────────────────────────────────────

def test_no_sell_before_first_buy():
    """MACD starts above signal and crosses below → no SELL because never bought."""
    dates = _dates(3)
    closes = [100.0] * 3
    macd_line:   List[Optional[float]] = [1.0, 0.5, -0.5]
    signal_line: List[Optional[float]] = [0.0, 0.0,  0.0]
    signals = generate_macd_crossover_signals(
        dates=dates, closes=closes, macd_line=macd_line, signal_line=signal_line
    )
    assert signals == []


# ── 6. Alternating BUY/SELL cycles ───────────────────────────────────────

def test_alternating_buy_sell_cycles():
    """Multiple complete BUY/SELL cycles are generated correctly."""
    dates = _dates(6)
    closes = [100.0] * 6
    # cross up at bar 1, cross down at bar 2, cross up at bar 3, cross down at bar 4
    macd_line:   List[Optional[float]] = [-1.0,  1.0, -1.0,  1.0, -1.0, -0.5]
    signal_line: List[Optional[float]] = [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
    signals = generate_macd_crossover_signals(
        dates=dates, closes=closes, macd_line=macd_line, signal_line=signal_line
    )
    assert [s.signal for s in signals] == [1, -1, 1, -1]
    assert signals[0].date == dates[1]
    assert signals[1].date == dates[2]
    assert signals[2].date == dates[3]
    assert signals[3].date == dates[4]


# ── 7. Mismatched array lengths raises ValueError ─────────────────────────

def test_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        generate_macd_crossover_signals(
            dates=_dates(3),
            closes=[100.0, 101.0],  # length 2 ≠ 3
            macd_line=[None, None, None],
            signal_line=[None, None, None],
        )


# ── 8. Unsorted dates raises ValueError ──────────────────────────────────

def test_unsorted_dates_raises():
    dates = [date(2023, 1, 3), date(2023, 1, 1)]
    with pytest.raises(ValueError, match="sorted ascending"):
        generate_macd_crossover_signals(
            dates=dates,
            closes=[100.0, 101.0],
            macd_line=[None, None],
            signal_line=[None, None],
        )
