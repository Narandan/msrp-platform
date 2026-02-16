from typing import List, Optional
from app.schemas.stock import CandleDTO


def compute_rsi(candles: List[CandleDTO], period: int = 14) -> List[Optional[float]]:
    """
    Wilder's RSI, aligned with candles.
    First `period` values are None (not enough data).
    Returns values in [0, 100].
    """
    if period <= 0:
        raise ValueError("period must be > 0")
    n = len(candles)
    if n == 0:
        return []

    closes = [c.close for c in candles]
    rsi: List[Optional[float]] = [None] * n

    # Price changes
    changes = [0.0] * n
    for i in range(1, n):
        changes[i] = closes[i] - closes[i - 1]

    gains = [0.0] * n
    losses = [0.0] * n
    for i in range(1, n):
        delta = changes[i]
        if delta > 0:
            gains[i] = delta
        else:
            losses[i] = -delta  # positive loss magnitude

    # Initial average gain/loss over first `period` changes
    if n <= period:
        return rsi

    avg_gain = sum(gains[1 : period + 1]) / period
    avg_loss = sum(losses[1 : period + 1]) / period

    # First RSI value at index `period`
    rsi[period] = _rsi_from_avgs(avg_gain, avg_loss)

    # Wilder smoothing for the rest
    for i in range(period + 1, n):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        rsi[i] = _rsi_from_avgs(avg_gain, avg_loss)

    return rsi


def _rsi_from_avgs(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0 and avg_gain == 0:
        return 50.0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))
