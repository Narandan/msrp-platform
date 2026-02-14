from pydantic import BaseModel


class IngestResponse(BaseModel):
    symbol: str
    inserted: int
    skipped: int
    total_seen: int
