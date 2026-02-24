from datetime import date
from pydantic import BaseModel
from typing import List, Optional


class IndicatorPoint(BaseModel):
    date: date
    close: float
    sma: Optional[float] = None
    ema: Optional[float] = None
    rsi: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None


class IndicatorsResponse(BaseModel):
    symbol: str
    points: List[IndicatorPoint]

