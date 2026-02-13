from datetime import date
from pydantic import BaseModel
from typing import List, Optional

class EquityPoint(BaseModel):
    date: date
    equity: float

class Trade(BaseModel):
    entry_date: date
    exit_date: date
    entry_price: float
    exit_price: float
    pnl: float
    return_pct: float
    reason: Optional[str] = None

class BacktestMetrics(BaseModel):
    total_return_pct: float
    max_drawdown_pct: float
    win_rate_pct: float
    num_trades: int

class BacktestResult(BaseModel):
    equity_curve: List[EquityPoint]
    trades: List[Trade]
    metrics: BacktestMetrics
