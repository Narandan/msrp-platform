"""MACD crossover strategy: BUY when MACD crosses above signal line, SELL when below."""
from __future__ import annotations

from datetime import date
from typing import List, Optional, Sequence

from app.schemas.strategy import SignalPoint


def generate_macd_crossover_signals(
    dates: Sequence[date],
    closes: Sequence[float],
    macd_line: Sequence[Optional[float]],
    signal_line: Sequence[Optional[float]],
) -> List[SignalPoint]:
    """
    Long-only MACD crossover strategy.

    Rules:
      - Skip bars where macd_line[i] or signal_line[i] is None.
      - Track prev_macd and prev_signal from the last non-None bar.
      - Bullish cross: prev_macd <= prev_signal AND macd_line[i] > signal_line[i] -> BUY (only if flat).
      - Bearish cross: prev_macd >= prev_signal AND macd_line[i] < signal_line[i] -> SELL (only if long).
      - Enforces position state machine (0=flat, 1=long) to prevent duplicates and SELL before BUY.
    """
    n = len(dates)
    if len(closes) != n or len(macd_line) != n or len(signal_line) != n:
        raise ValueError("dates, closes, macd_line, signal_line must be same length")

    for i in range(n - 1):
        if dates[i] > dates[i + 1]:
            raise ValueError("dates must be sorted ascending")

    signals: List[SignalPoint] = []
    position = 0  # 0=flat, 1=long
    prev_macd: Optional[float] = None
    prev_signal: Optional[float] = None

    for i in range(n):
        m = macd_line[i]
        s = signal_line[i]

        if m is None or s is None:
            continue

        if prev_macd is not None and prev_signal is not None:
            # Bullish cross: MACD crosses above signal
            if prev_macd <= prev_signal and m > s and position == 0:
                signals.append(SignalPoint(date=dates[i], signal=1, reason="MACD crossed above signal"))
                position = 1
            # Bearish cross: MACD crosses below signal
            elif prev_macd >= prev_signal and m < s and position == 1:
                signals.append(SignalPoint(date=dates[i], signal=-1, reason="MACD crossed below signal"))
                position = 0

        prev_macd = m
        prev_signal = s

    return signals
