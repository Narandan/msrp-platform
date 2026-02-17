from __future__ import annotations

from datetime import date
from typing import List

from sqlalchemy.orm import Session

from app.db.models.stock import Candle, Symbol
from app.schemas.backtest import BacktestResult
from app.schemas.stock import CandleDTO
from app.services.backtesting.engine import CandlePoint, run_long_only_all_in_out
from app.services.backtesting.metrics import compute_metrics
from app.services.indicators.sma import compute_sma
from app.services.strategies.sma_threshold import generate_sma_threshold_signals


class BacktestService:
    def __init__(self, db: Session):
        self.db = db

    def run_sma_threshold_backtest(
        self,
        *,
        symbol: str,
        start: date,
        end: date,
        sma_period: int = 20,
        initial_cash: float = 10_000.0,
    ) -> BacktestResult:
        if sma_period <= 0:
            raise ValueError("sma_period must be > 0")
        if start > end:
            raise ValueError("start must be <= end")
        if initial_cash <= 0:
            raise ValueError("initial_cash must be > 0")

        ticker = symbol.strip().upper()

        sym = self.db.query(Symbol).filter(Symbol.ticker == ticker).one_or_none()
        if sym is None:
            raise ValueError(f"Symbol not found in DB: {ticker}. Ingest it first.")

        rows: List[Candle] = (
            self.db.query(Candle)
            .filter(Candle.symbol_id == sym.id)
            .filter(Candle.date >= start)
            .filter(Candle.date <= end)
            .order_by(Candle.date.asc())
            .all()
        )
        if not rows:
            raise ValueError(f"No candles available for {ticker} in range {start}..{end}")

        candle_dtos: List[CandleDTO] = [
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

        sma = compute_sma(candle_dtos, period=sma_period)

        dates = [c.date for c in candle_dtos]
        closes = [float(c.close) for c in candle_dtos]

        signals = generate_sma_threshold_signals(dates=dates, closes=closes, sma=sma)

        candle_points = [CandlePoint(date=r.date, close=float(r.close)) for r in rows]

        equity_curve, trades = run_long_only_all_in_out(
            candles=candle_points,
            signals=signals,
            initial_cash=initial_cash,
        )

        metrics = compute_metrics(equity_curve=equity_curve, trades=trades)

        return BacktestResult(equity_curve=equity_curve, trades=trades, metrics=metrics)
