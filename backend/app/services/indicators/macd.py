"""MACD (Moving Average Convergence Divergence) indicator."""
from __future__ import annotations

from typing import List, Optional, Tuple

from app.schemas.stock import CandleDTO


def _ema_values(values: List[float], period: int) -> List[Optional[float]]:
    """Compute EMA for a list of values. First (period - 1) are None."""
    n = len(values)
    out: List[Optional[float]] = [None] * n
    if n < period:
        return out
    k = 2.0 / (period + 1)
    sma_init = sum(values[:period]) / period
    out[period - 1] = sma_init
    for i in range(period, n):
        out[i] = (values[i] * k) + (out[i - 1] * (1.0 - k))
    return out


def compute_macd(
    candles: List[CandleDTO],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    """
    Compute MACD line, signal line, and histogram aligned with candles.

    MACD line = EMA(close, fast) - EMA(close, slow)
    Signal line = EMA(MACD line, signal_period)
    Histogram = MACD - Signal

    First (slow_period - 1) values are None for MACD; first (slow_period - 1 + signal_period - 1)
    are None for signal/histogram where applicable.
    """
    if fast_period <= 0 or slow_period <= 0 or signal_period <= 0:
        raise ValueError("periods must be > 0")
    if fast_period >= slow_period:
        raise ValueError("fast_period must be < slow_period")

    closes = [float(c.close) for c in candles]
    n = len(closes)

    ema_fast = _ema_values(closes, fast_period)
    ema_slow = _ema_values(closes, slow_period)

    macd_line: List[Optional[float]] = [None] * n
    for i in range(slow_period - 1, n):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            macd_line[i] = ema_fast[i] - ema_slow[i]

    # EMA of MACD for signal (only over non-None MACD values)
    macd_raw = [x if x is not None else 0.0 for x in macd_line]
    signal_line: List[Optional[float]] = [None] * n
    start_signal = slow_period - 1 + signal_period - 1
    if start_signal < n:
        slice_macd = macd_raw[slow_period - 1 : start_signal + 1]
        if len(slice_macd) >= signal_period:
            init_sma = sum(slice_macd[:signal_period]) / signal_period
            signal_line[start_signal] = init_sma
            k = 2.0 / (signal_period + 1)
            for i in range(start_signal + 1, n):
                prev = signal_line[i - 1]
                if prev is not None and macd_line[i] is not None:
                    signal_line[i] = (macd_line[i] * k) + (prev * (1.0 - k))
        for i in range(slow_period - 1, start_signal):
            signal_line[i] = None
    else:
        for i in range(slow_period - 1, n):
            signal_line[i] = None

    histogram: List[Optional[float]] = [None] * n
    for i in range(n):
        if macd_line[i] is not None and signal_line[i] is not None:
            histogram[i] = macd_line[i] - signal_line[i]

    return macd_line, signal_line, histogram
