"""SMA crossover strategy: BUY when fast SMA crosses above slow SMA, SELL when below."""
from __future__ import annotations

from datetime import date
from typing import List, Optional, Sequence

from app.schemas.strategy import SignalPoint


def generate_sma_crossover_signals(
    dates: Sequence[date],
    closes: Sequence[float],
    fast_sma: Sequence[Optional[float]],
    slow_sma: Sequence[Optional[float]],
) -> List[SignalPoint]:
    """
    Long-only SMA crossover.

    Rules:
      - Where both fast_sma and slow_sma are defined:
        - fast > slow -> long (1)
        - fast <= slow -> flat (0)
      - Emits ONLY state-change signals: 1 (BUY) when switching flat -> long, -1 (SELL) when long -> flat.
    """
    n = len(dates)
    if len(closes) != n or len(fast_sma) != n or len(slow_sma) != n:
        raise ValueError("dates, closes, fast_sma, slow_sma must be same length")

    for i in range(n - 1):
        if dates[i] > dates[i + 1]:
            raise ValueError("dates must be sorted ascending")

    signals: List[SignalPoint] = []
    position = 0  # 0=flat, 1=long

    for i in range(n):
        f = fast_sma[i]
        s = slow_sma[i]
        if f is None or s is None:
            continue
        new_position = 1 if f > s else 0
        if new_position == position:
            continue
        if new_position == 1:
            signals.append(SignalPoint(date=dates[i], signal=1, reason="fast SMA > slow SMA"))
        else:
            signals.append(SignalPoint(date=dates[i], signal=-1, reason="fast SMA <= slow SMA"))
        position = new_position

    return signals
