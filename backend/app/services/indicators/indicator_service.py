from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.stock import Candle, Symbol
from app.schemas.indicators import IndicatorPoint
from app.schemas.stock import CandleDTO
from app.services.indicators.rsi import compute_rsi
from app.services.indicators.sma import compute_sma


def get_indicator_points(
    db: Session,
    symbol: str,
    start: date,
    end: date,
    sma_period: Optional[int],
    rsi_period: Optional[int],
) -> List[IndicatorPoint]:
    ticker = symbol.strip().upper()

    sym = db.execute(select(Symbol).where(Symbol.ticker == ticker)).scalar_one_or_none()
    if sym is None:
        return []

    rows = (
        db.execute(
            select(Candle)
            .where(Candle.symbol_id == sym.id, Candle.date >= start, Candle.date <= end)
            .order_by(Candle.date.asc())
        )
        .scalars()
        .all()
    )
    if not rows:
        return []

    candles: List[CandleDTO] = [
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

    sma_series = compute_sma(candles, sma_period) if sma_period is not None else [None] * len(candles)
    rsi_series = compute_rsi(candles, rsi_period) if rsi_period is not None else [None] * len(candles)

    return [
        IndicatorPoint(
            date=candles[i].date,
            close=candles[i].close,
            sma=sma_series[i],
            rsi=rsi_series[i],
        )
        for i in range(len(candles))
    ]
