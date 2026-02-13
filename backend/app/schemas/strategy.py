from datetime import date
from pydantic import BaseModel
from typing import Optional

class SignalPoint(BaseModel):
    date: date
    signal: int  # 1=BUY, 0=HOLD, -1=SELL
    reason: Optional[str] = None
