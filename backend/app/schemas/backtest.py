from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class EquityPoint(BaseModel):
    date: date
    equity: float = Field(..., ge=0.0)


class Trade(BaseModel):
    entry_date: date
    exit_date: date
    entry_price: float = Field(..., gt=0.0)
    exit_price: float = Field(..., gt=0.0)
    pnl: float
    return_pct: float
    reason: Optional[str] = None

# ISSUE #29: When you implement Sharpe ratio in metrics.py,
# add a `sharpe_ratio: float | None = None` field to BacktestMetrics.
class BacktestMetrics(BaseModel):
    total_return_pct: float
    max_drawdown_pct: float = Field(..., ge=0.0)
    win_rate_pct: float = Field(..., ge=0.0, le=100.0)
    num_trades: int = Field(..., ge=0)


class BacktestResult(BaseModel):
    equity_curve: List[EquityPoint]
    trades: List[Trade]
    metrics: BacktestMetrics
