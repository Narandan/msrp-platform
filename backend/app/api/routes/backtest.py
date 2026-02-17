from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.backtest import BacktestResult
from app.services.backtesting.backtest_service import BacktestService

router = APIRouter(prefix="/backtest", tags=["backtest"])


@router.get("/{symbol}", response_model=BacktestResult)
def backtest_symbol(
    symbol: str,
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    sma_period: int = Query(20, ge=1, description="SMA period"),
    initial_cash: float = Query(10_000.0, gt=0.0, description="Starting cash"),
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BacktestResult:
    try:
        return BacktestService(db).run_sma_threshold_backtest(
            symbol=symbol,
            start=start,
            end=end,
            sma_period=sma_period,
            initial_cash=initial_cash,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
