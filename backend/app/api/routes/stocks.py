from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.db.models.stock import Symbol, Candle
from app.db.models.user import User
from app.schemas.stock import CandleDTO, SymbolSearchResult
from app.schemas.stocks import IngestResponse
from app.services.stocks.ingest_service import ingest_symbol_candles
from app.services.stocks.symbol_list_service import search_symbols as search_symbols_full

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("/ping")
async def stocks_ping() -> dict:
    """
    Simple liveness check for smoke tests.
    """
    return {"status": "ok"}


def _search_symbols_db(db: Session, query_upper: str, limit: int) -> List[SymbolSearchResult]:
    """Fallback: search only symbols already in DB (e.g. when external list unavailable)."""
    stmt = (
        select(Symbol)
        .where(Symbol.ticker.ilike(f"{query_upper}%"))
        .order_by(Symbol.ticker)
        .limit(limit)
    )
    results = list(db.execute(stmt).scalars().all())
    if len(results) < limit:
        stmt_contains = (
            select(Symbol)
            .where(
                Symbol.ticker.ilike(f"%{query_upper}%"),
                ~Symbol.ticker.ilike(f"{query_upper}%"),
            )
            .order_by(Symbol.ticker)
            .limit(limit - len(results))
        )
        results.extend(db.execute(stmt_contains).scalars().all())
    return [SymbolSearchResult(ticker=s.ticker, name=s.name) for s in results]


@router.get("/search", response_model=List[SymbolSearchResult])
def search_symbols(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),  # auth required
):
    """
    Search for symbols by ticker across all available NASDAQ/NYSE symbols.
    When the full list is unavailable (e.g. offline), falls back to symbols in DB.
    """
    query_upper = q.strip().upper()
    results = search_symbols_full(query=q, limit=limit)
    if not results:
        results = _search_symbols_db(db, query_upper, limit)
    return results


@router.post("/{symbol}/ingest", response_model=IngestResponse)
def ingest(
    symbol: str,
    start: date = Query(...),
    end: date = Query(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),  # auth required
):
    if start >= end:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="start must be before end")
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
        raise HTTPException(status_code=404, detail=f"Symbol {symbol.upper()} not found. Ingest it first.")

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
