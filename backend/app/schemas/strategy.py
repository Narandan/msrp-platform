from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SignalPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    signal: int
    reason: Optional[str] = None
