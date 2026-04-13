from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CandleDTO(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: Optional[int] = None

    model_config = {"from_attributes": True}
    model_config = ConfigDict(from_attributes=True)


class SymbolSearchResult(BaseModel):
    ticker: str
    name: Optional[str] = None

    model_config = {"from_attributes": True}
    model_config = ConfigDict(from_attributes=True)
