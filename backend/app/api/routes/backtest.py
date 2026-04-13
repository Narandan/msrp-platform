from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.backtest import BacktestResult, OptimizeRequest, OptimizeResult
from app.services.backtesting.backtest_service import BacktestService
from app.services.backtesting.optimizer import OptimizerService

router = APIRouter(prefix="/backtest", tags=["backtest"])


@router.post("/optimize", response_model=list[OptimizeResult])
def optimize_backtest(
    body: OptimizeRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[OptimizeResult]:
    if body.start >= body.end:
        raise HTTPException(status_code=400, detail="start must be before end")
    try:
        svc = OptimizerService(db)
        return svc.run_grid_search(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{symbol}", response_model=BacktestResult)
def backtest_symbol(
    symbol: str,
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    strategy: str = Query("sma_threshold", description="Strategy: sma_threshold, sma_crossover, rsi_threshold, macd_crossover, or bollinger_breakout"),
    sma_period: int = Query(20, ge=1, description="SMA period (sma_threshold)"),
    fast_period: int = Query(10, ge=1, description="Fast SMA period (sma_crossover)"),
    slow_period: int = Query(20, ge=1, description="Slow SMA period (sma_crossover)"),
    rsi_period: int = Query(14, ge=1, description="RSI period (rsi_threshold)"),
    macd_fast: int = Query(12, ge=1, description="MACD fast period"),
    macd_slow: int = Query(26, ge=1, description="MACD slow period"),
    macd_signal: int = Query(9, ge=1, description="MACD signal period"),
    oversold: float = Query(30.0, ge=0.0, le=100.0, description="RSI oversold threshold (rsi_threshold)"),
    overbought: float = Query(70.0, ge=0.0, le=100.0, description="RSI overbought threshold (rsi_threshold)"),
    bb_period: int = Query(20, ge=1, description="Bollinger Band period"),
    bb_std: float = Query(2.0, ge=0.0, description="Bollinger Band std dev multiplier"),
    initial_cash: float = Query(10_000.0, gt=0.0, description="Starting cash"),
    transaction_cost_pct: float = Query(0.0, ge=0.0, le=0.1, description="Transaction cost as decimal (e.g. 0.001 = 0.1%)"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> BacktestResult:
    if start >= end:
        raise HTTPException(status_code=400, detail="start must be before end")
    if strategy not in ("sma_threshold", "sma_crossover", "rsi_threshold", "macd_crossover", "bollinger_breakout"):
        raise HTTPException(status_code=400, detail=f"Unknown strategy '{strategy}'. Use sma_threshold, sma_crossover, rsi_threshold, macd_crossover, or bollinger_breakout.")
    try:
        svc = BacktestService(db)
        if strategy == "macd_crossover":
            return svc.run_macd_crossover_backtest(
                symbol=symbol,
                start=start,
                end=end,
                fast_period=macd_fast,
                slow_period=macd_slow,
                signal_period=macd_signal,
                initial_cash=initial_cash,
                transaction_cost_pct=transaction_cost_pct,
            )
        if strategy == "bollinger_breakout":
            return svc.run_bollinger_breakout_backtest(
                symbol=symbol,
                start=start,
                end=end,
                bb_period=bb_period,
                bb_std=bb_std,
                initial_cash=initial_cash,
                transaction_cost_pct=transaction_cost_pct,
            )
        if strategy == "rsi_threshold":
            return svc.run_rsi_threshold_backtest(
                symbol=symbol,
                start=start,
                end=end,
                rsi_period=rsi_period,
                oversold=oversold,
                overbought=overbought,
                initial_cash=initial_cash,
                transaction_cost_pct=transaction_cost_pct,
            )
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
