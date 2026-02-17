from __future__ import annotations

from datetime import date
from typing import List, Optional, Sequence

from app.schemas.strategy import SignalPoint


def generate_sma_threshold_signals(
    dates: Sequence[date],
    closes: Sequence[float],
    sma: Sequence[Optional[float]],
) -> List[SignalPoint]:
    """
    Long-only SMA threshold strategy.

    Rules:
      - Ignore periods where SMA is None
      - If close > sma  -> go long
      - Else            -> go flat

    Emits ONLY state-change signals:
      - 1  (BUY)  when switching flat -> long
      - -1 (SELL) when switching long -> flat
    """
    n = len(dates)
    if len(closes) != n or len(sma) != n:
        raise ValueError("dates, closes, sma must be same length")

    # Ensure dates are sorted ascending (backtest assumes chronological order)
    for i in range(n - 1):
        if dates[i] > dates[i + 1]:
            raise ValueError("dates must be sorted ascending")

    signals: List[SignalPoint] = []
    position = 0  # 0=flat, 1=long

    for i in range(n):
        s = sma[i]
        if s is None:
            continue

        new_position = 1 if closes[i] > s else 0
        if new_position == position:
            continue

        if new_position == 1:
            signals.append(SignalPoint(date=dates[i], signal=1, reason="close > sma"))
        else:
            signals.append(SignalPoint(date=dates[i], signal=-1, reason="close <= sma"))

        position = new_position

    return signals
