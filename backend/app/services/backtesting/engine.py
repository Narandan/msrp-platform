from typing import List
from app.schemas.stock import CandleDTO
from app.schemas.strategy import SignalPoint
from app.schemas.backtest import BacktestResult

def run_long_only_backtest(
    candles: List[CandleDTO],
    signals: List[SignalPoint],
    initial_cash: float = 10_000.0,
) -> BacktestResult:
    """
    Long-only, single-position backtest.
    Contract: returns BacktestResult with equity_curve, trades, metrics.
    """
    raise NotImplementedError
