from datetime import date
from pydantic import BaseModel, Field

class CandleDTO(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int = Field(ge=0)
