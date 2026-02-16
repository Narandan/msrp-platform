from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.stock import Symbol, Candle
from app.schemas.stock import CandleDTO
from app.schemas.indicators import IndicatorPoint

from app.services.indicators.sma import compute_sma
from app.services.indicators.rsi import compute_rsi


def get_indicator_points(
    db: Session,
    symbol: str,
    start: date,
    end: date,
    sma_period: Optional[int],
    rsi_period: Optional[int],
) -> List[IndicatorPoint]:
    sym = db.execute(select(Symbol).where(Symbol.ticker == symbol.upper())).scalar_one_or_none()
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

    candles = [
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

    sma_series = compute_sma(candles, sma_period) if sma_period else [None] * len(candles)
    rsi_series = compute_rsi(candles, rsi_period or 14) if (rsi_period or rsi_period == 0) else [None] * len(candles)

    points: List[IndicatorPoint] = []
    for i, c in enumerate(candles):
        points.append(
            IndicatorPoint(
                date=c.date,
                close=c.close,
                sma=sma_series[i] if sma_period else None,
                rsi=rsi_series[i] if (rsi_period or rsi_period == 0 or rsi_period is not None) else None,
            )
        )

    return points
