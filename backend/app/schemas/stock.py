from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel


class CandleDTO(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: Optional[int] = None

    class Config:
        orm_mode = True


class SymbolSearchResult(BaseModel):
    ticker: str
    name: Optional[str] = None

    class Config:
        orm_mode = True
