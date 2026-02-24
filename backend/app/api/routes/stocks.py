from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.db.models.stock import Symbol, Candle
from app.db.models.user import User
from app.schemas.stock import CandleDTO, SymbolSearchResult
from app.schemas.stocks import IngestResponse
from app.services.stocks.ingest_service import ingest_symbol_candles

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("/ping")
async def stocks_ping() -> dict:
    """
    Simple liveness check for smoke tests.
    """
    return {"status": "ok"}


@router.get("/search", response_model=List[SymbolSearchResult])
def search_symbols(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),  # auth required
):
    """
    Search for symbols by ticker.
    Returns symbols that start with or contain the query string.
    Increment 1 scope: ticker-only search from known symbols in DB.
    """
    query_upper = q.upper()
    
    # Search: starts-with gets priority
    stmt = (
        select(Symbol)
        .where(Symbol.ticker.ilike(f"{query_upper}%"))
        .order_by(Symbol.ticker)
        .limit(limit)
    )
    
    results = list(db.execute(stmt).scalars().all())
    
    # If not enough results, also search for contains
    if len(results) < limit:
        remaining = limit - len(results)
        stmt_contains = (
            select(Symbol)
            .where(
                Symbol.ticker.ilike(f"%{query_upper}%"),
                ~Symbol.ticker.ilike(f"{query_upper}%")  # exclude already found
            )
            .order_by(Symbol.ticker)
            .limit(remaining)
        )
        results.extend(db.execute(stmt_contains).scalars().all())
    
    return results


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
