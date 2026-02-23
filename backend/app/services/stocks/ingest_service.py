from datetime import date
from typing import Tuple, List

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models.stock import Symbol, Candle
from app.schemas.stock import CandleDTO
from app.services.market_data.stooq_provider import StooqProvider


def _get_or_create_symbol(db: Session, ticker: str) -> Symbol:
    sym = db.execute(select(Symbol).where(Symbol.ticker == ticker)).scalar_one_or_none()
    if sym is None:
        sym = Symbol(ticker=ticker, name=None)
        db.add(sym)
        db.commit()
        db.refresh(sym)
    return sym


def ingest_symbol_candles(
    db: Session,
    symbol: str,
    start: date,
    end: date,
    provider: StooqProvider | None = None,
) -> Tuple[int, int, int]:
    """
    Fetch candles from provider and insert into DB.
    Returns: (inserted, skipped, total_seen)
    Skipped = duplicates blocked by UNIQUE(symbol_id, date)
    """
    provider = provider or StooqProvider()
    candles: List[CandleDTO] = provider.get_candles(symbol=symbol, start=start, end=end)

    if not candles:
        return (0, 0, 0)

    canonical_ticker = symbol.strip().upper()
    sym = _get_or_create_symbol(db, canonical_ticker)

    inserted = 0
    skipped = 0

    for c in candles:
        row = Candle(
            symbol_id=sym.id,
            date=c.date,
            open=c.open,
            high=c.high,
            low=c.low,
            close=c.close,
            volume=c.volume,
        )
        db.add(row)
        try:
            db.commit()
            inserted += 1
        except IntegrityError:
            db.rollback()
            skipped += 1

    return (inserted, skipped, len(candles))
