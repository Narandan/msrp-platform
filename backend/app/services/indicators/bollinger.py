from typing import List, Optional, Tuple
from app.schemas.stock import CandleDTO


def compute_bollinger_bands(
    candles: List[CandleDTO], 
    period: int = 20, 
    num_std: float = 2.0
) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    """
    Compute Bollinger Bands (middle, upper, lower).
    
    Args:
        candles: List of candle data
        period: Moving average period (default 20)
        num_std: Number of standard deviations for bands (default 2.0)
    
    Returns:
        Tuple of (middle_band, upper_band, lower_band)
        First (period - 1) values will be None.
    
    Formula:
        Middle Band = SMA(period)
        Upper Band = Middle Band + (num_std * std_dev)
        Lower Band = Middle Band - (num_std * std_dev)
    """
    if period <= 0:
        raise ValueError("period must be > 0")
    if num_std < 0:
        raise ValueError("num_std must be >= 0")

    n = len(candles)
    closes = [float(c.close) for c in candles]
    
    middle: List[Optional[float]] = [None] * n
    upper: List[Optional[float]] = [None] * n
    lower: List[Optional[float]] = [None] * n

    for i in range(period - 1, n):
        # Get window of closes
        window = closes[i - period + 1 : i + 1]
        
        # Calculate SMA (middle band)
        sma = sum(window) / period
        
        # Calculate standard deviation
        variance = sum((x - sma) ** 2 for x in window) / period
        std_dev = variance ** 0.5
        
        # Set band values
        middle[i] = sma
        upper[i] = sma + (num_std * std_dev)
        lower[i] = sma - (num_std * std_dev)

    return middle, upper, lower
