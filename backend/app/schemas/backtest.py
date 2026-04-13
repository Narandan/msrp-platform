from datetime import date
from typing import List, Optional, Union

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
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    calmar_ratio: Optional[float] = None
    cagr_pct: Optional[float] = None


class BacktestResult(BaseModel):
    equity_curve: List[EquityPoint]
    trades: List[Trade]
    metrics: BacktestMetrics


class OptimizeRequest(BaseModel):
    symbol: str
    strategy: str
    start: date
    end: date
    param_grid: dict[str, list[Union[int, float]]]
    top_n: int = Field(5, ge=1, le=20)
    initial_cash: float = Field(10_000.0, gt=0)


class OptimizeResult(BaseModel):
    params: dict[str, Union[int, float]]
    sharpe_ratio: float
    total_return_pct: float
    max_drawdown_pct: float
    num_trades: int
