from typing import List, Optional

from app.schemas.stock import CandleDTO


def compute_sma(candles: List[CandleDTO], period: int) -> List[Optional[float]]:
    """
    Returns SMA aligned with candle list.
    First (period - 1) values will be None.
    """
    if period <= 0:
        raise ValueError("period must be > 0")

    closes = [float(c.close) for c in candles]
    sma: List[Optional[float]] = [None] * len(closes)

    window_sum = 0.0

    for i in range(len(closes)):
        window_sum += closes[i]

        if i >= period:
            window_sum -= closes[i - period]

        if i >= period - 1:
            sma[i] = window_sum / period

    return sma
