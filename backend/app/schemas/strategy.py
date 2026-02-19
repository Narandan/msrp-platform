from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel


class SignalPoint(BaseModel):
    date: date
    signal: int
    reason: Optional[str] = None

    class Config:
        # For Pydantic v2, 'orm_mode' is now 'from_attributes'
        from_attributes = True
