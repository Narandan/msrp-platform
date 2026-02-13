from typing import List
from app.schemas.stock import CandleDTO
from app.schemas.strategy import SignalPoint
from app.schemas.backtest import BacktestResult

def run_via_qbacktester(
    candles: List[CandleDTO],
    signals: List[SignalPoint],
    initial_cash: float = 10_000.0,
) -> BacktestResult:
    """
    Adapter boundary ONLY. Converts MSRP contracts <-> teammate library contracts.
    """
    raise NotImplementedError
