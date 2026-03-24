from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.backtest import BacktestResult
from app.services.backtesting.backtest_service import BacktestService

router = APIRouter(prefix="/backtest", tags=["backtest"])


@router.get("/{symbol}", response_model=BacktestResult)
def backtest_symbol(
    symbol: str,
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    strategy: str = Query("sma_threshold", description="Strategy: sma_threshold or sma_crossover"),
    sma_period: int = Query(20, ge=1, description="SMA period (sma_threshold)"),
    fast_period: int = Query(10, ge=1, description="Fast SMA period (sma_crossover)"),
    slow_period: int = Query(20, ge=1, description="Slow SMA period (sma_crossover)"),
    initial_cash: float = Query(10_000.0, gt=0.0, description="Starting cash"),
    transaction_cost_pct: float = Query(0.0, ge=0.0, le=0.1, description="Transaction cost as decimal (e.g. 0.001 = 0.1%)"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> BacktestResult:
    if start >= end:
        raise HTTPException(status_code=400, detail="start must be before end")
    if strategy not in ("sma_threshold", "sma_crossover"):
        raise HTTPException(status_code=400, detail=f"Unknown strategy '{strategy}'. Use sma_threshold or sma_crossover.")
    try:
        svc = BacktestService(db)
        if strategy == "sma_crossover":
            return svc.run_sma_crossover_backtest(
                symbol=symbol,
                start=start,
                end=end,
                fast_period=fast_period,
                slow_period=slow_period,
                initial_cash=initial_cash,
                transaction_cost_pct=transaction_cost_pct,
            )
        return svc.run_sma_threshold_backtest(
            symbol=symbol,
            start=start,
            end=end,
            sma_period=sma_period,
            initial_cash=initial_cash,
            transaction_cost_pct=transaction_cost_pct,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
