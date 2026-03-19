from typing import List, Optional
from pydantic import BaseModel


class WatchlistEntry(BaseModel):
    ticker: str
    name: Optional[str] = None

    model_config = {"from_attributes": True}


class WatchlistResponse(BaseModel):
    symbols: List[WatchlistEntry]


class AddWatchlistRequest(BaseModel):
    ticker: str
