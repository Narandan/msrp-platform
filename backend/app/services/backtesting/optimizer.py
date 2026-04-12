from itertools import product
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.schemas.backtest import OptimizeRequest, OptimizeResult
from app.services.backtesting.backtest_service import BacktestService

MAX_COMBINATIONS = 100

STRATEGY_PARAMS = {
    "sma_threshold":      ["sma_period"],
    "sma_crossover":      ["fast_period", "slow_period"],
    "rsi_threshold":      ["rsi_period", "oversold", "overbought"],
    "macd_crossover":     ["fast_period", "slow_period", "signal_period"],
    "bollinger_breakout": ["bb_period", "bb_std"],
}


class OptimizerService:
    def __init__(self, db: Session):
        self.db = db
        self.svc = BacktestService(db)

    def run_grid_search(self, req: OptimizeRequest) -> list[OptimizeResult]:
        if req.strategy not in STRATEGY_PARAMS:
            raise ValueError(f"Unknown strategy '{req.strategy}'. Supported: {list(STRATEGY_PARAMS.keys())}")

        valid_params = STRATEGY_PARAMS[req.strategy]
        for key in req.param_grid:
            if key not in valid_params:
                raise ValueError(
                    f"Unknown param '{key}' for strategy '{req.strategy}'. Valid params: {valid_params}"
                )

        keys = list(req.param_grid.keys())
        value_lists = [req.param_grid[k] for k in keys]
        combos = list(product(*value_lists))

        if len(combos) > MAX_COMBINATIONS:
            raise ValueError(f"Too many combinations ({len(combos)}). Max is {MAX_COMBINATIONS}.")

        if len(combos) == 0:
            raise ValueError("param_grid produced no combinations")

        dispatch = {
            "sma_threshold":      self.svc.run_sma_threshold_backtest,
            "sma_crossover":      self.svc.run_sma_crossover_backtest,
            "rsi_threshold":      self.svc.run_rsi_threshold_backtest,
            "macd_crossover":     self.svc.run_macd_crossover_backtest,
            "bollinger_breakout": self.svc.run_bollinger_breakout_backtest,
        }
        run_fn = dispatch[req.strategy]

        results: list[OptimizeResult] = []
        for combo in combos:
            combo_kwargs: dict[str, Any] = dict(zip(keys, combo))
            try:
                result = run_fn(
                    symbol=req.symbol,
                    start=req.start,
                    end=req.end,
                    initial_cash=req.initial_cash,
                    **combo_kwargs,
                )
            except ValueError:
                continue

            metrics = result.metrics
            results.append(OptimizeResult(
                params=combo_kwargs,
                sharpe_ratio=metrics.sharpe_ratio if metrics.sharpe_ratio is not None else 0.0,
                total_return_pct=metrics.total_return_pct,
                max_drawdown_pct=metrics.max_drawdown_pct,
                num_trades=metrics.num_trades,
            ))

        results.sort(key=lambda r: r.sharpe_ratio, reverse=True)
        return results[: req.top_n]
