from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.db.models.stock import Symbol, Candle
from app.db.models.user import User
from app.schemas.stock import CandleDTO
from app.schemas.stocks import IngestResponse
from app.services.stocks.ingest_service import ingest_symbol_candles

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("/ping")
async def stocks_ping() -> dict:
    """
    Simple liveness check for smoke tests.
    """
    return {"status": "ok"}


@router.post("/{symbol}/ingest", response_model=IngestResponse)
def ingest(
    symbol: str,
    start: date = Query(...),
    end: date = Query(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),  # auth required
):
    inserted, skipped, total_seen = ingest_symbol_candles(db=db, symbol=symbol, start=start, end=end)
    return IngestResponse(symbol=symbol.upper(), inserted=inserted, skipped=skipped, total_seen=total_seen)


@router.get("/{symbol}/candles", response_model=List[CandleDTO])
def list_candles(
    symbol: str,
    limit: int = Query(200, ge=1, le=5000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),  # auth required
):
    sym = db.execute(select(Symbol).where(Symbol.ticker == symbol.upper())).scalar_one_or_none()
    if sym is None:
        return []

    rows = (
        db.execute(
            select(Candle)
            .where(Candle.symbol_id == sym.id)
            .order_by(Candle.date.asc())
            .limit(limit)
        )
        .scalars()
        .all()
    )

    return [
        CandleDTO(
            date=r.date,
            open=r.open,
            high=r.high,
            low=r.low,
            close=r.close,
            volume=r.volume,
        )
        for r in rows
    ]
