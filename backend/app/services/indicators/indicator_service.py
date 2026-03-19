from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.stock import Candle, Symbol
from app.schemas.indicators import IndicatorPoint
from app.schemas.stock import CandleDTO
from app.services.indicators.rsi import compute_rsi
from app.services.indicators.sma import compute_sma
from app.services.indicators.ema import compute_ema
from app.services.indicators.bollinger import compute_bollinger_bands
from app.services.indicators.macd import compute_macd


def get_indicator_points(
    db: Session,
    symbol: str,
    start: date,
    end: date,
    sma_period: Optional[int],
    ema_period: Optional[int],
    rsi_period: Optional[int],
    bb_period: Optional[int] = None,
    bb_std: Optional[float] = 2.0,
    macd_fast: Optional[int] = None,
    macd_slow: Optional[int] = None,
    macd_signal: Optional[int] = None,
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
    ema_series = compute_ema(candles, ema_period) if ema_period is not None else [None] * len(candles)
    rsi_series = compute_rsi(candles, rsi_period) if rsi_period is not None else [None] * len(candles)
    
    # Compute Bollinger Bands if requested
    if bb_period is not None:
        bb_middle, bb_upper, bb_lower = compute_bollinger_bands(candles, bb_period, bb_std or 2.0)
    else:
        bb_middle = [None] * len(candles)
        bb_upper = [None] * len(candles)
        bb_lower = [None] * len(candles)

    # MACD
    if macd_fast is not None and macd_slow is not None and macd_signal is not None:
        macd_line, macd_sig_line, macd_hist = compute_macd(
            candles, fast_period=macd_fast, slow_period=macd_slow, signal_period=macd_signal
        )
    else:
        macd_line = [None] * len(candles)
        macd_sig_line = [None] * len(candles)
        macd_hist = [None] * len(candles)

    return [
        IndicatorPoint(
            date=candles[i].date,
            close=candles[i].close,
            sma=sma_series[i],
            ema=ema_series[i],
            rsi=rsi_series[i],
            bb_middle=bb_middle[i],
            bb_upper=bb_upper[i],
            bb_lower=bb_lower[i],
            macd=macd_line[i],
            macd_signal=macd_sig_line[i],
            macd_histogram=macd_hist[i],
        )
        for i in range(len(candles))
    ]
