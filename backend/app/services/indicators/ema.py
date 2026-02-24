from typing import List, Optional

from app.schemas.stock import CandleDTO


def compute_ema(candles: List[CandleDTO], period: int) -> List[Optional[float]]:
    """
    Returns EMA (Exponential Moving Average) aligned with candle list.
    First (period - 1) values will be None.
    
    EMA uses exponential weighting, giving more weight to recent prices.
    
    Formula:
        EMA(today) = (Price(today) * k) + (EMA(yesterday) * (1 - k))
        where k = 2 / (period + 1)
        
    The first EMA value is calculated as SMA of the first 'period' values.
    """
    if period <= 0:
        raise ValueError("period must be > 0")

    closes = [float(c.close) for c in candles]
    ema: List[Optional[float]] = [None] * len(closes)

    if len(closes) < period:
        return ema

    # Calculate the smoothing multiplier
    k = 2.0 / (period + 1)

    # First EMA value is the SMA of the first 'period' values
    sma_sum = sum(closes[:period])
    ema[period - 1] = sma_sum / period

    # Calculate subsequent EMA values
    for i in range(period, len(closes)):
        ema[i] = (closes[i] * k) + (ema[i - 1] * (1 - k))

    return ema
