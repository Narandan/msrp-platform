"""Unit tests for OptimizerService.run_grid_search."""
from __future__ import annotations

import sys
from datetime import date
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Stub out the DB-dependent modules before importing OptimizerService so
# that the tests run on Python 3.9 without SQLAlchemy / DB models loaded.
# ---------------------------------------------------------------------------

def _make_stub_module(name: str) -> ModuleType:
    mod = ModuleType(name)
    sys.modules[name] = mod
    return mod


# Stub app.db.models.stock so BacktestService can be imported
_stock_mod = _make_stub_module("app.db.models.stock")
_stock_mod.Symbol = MagicMock()
_stock_mod.Candle = MagicMock()

_models_mod = _make_stub_module("app.db.models")
_models_mod.stock = _stock_mod

# Stub app.db.session
_session_mod = _make_stub_module("app.db.session")
_session_mod.engine = MagicMock()

# Stub app.db.base
_base_mod = _make_stub_module("app.db.base")
_base_mod.Base = MagicMock()

# Now we can safely import our schemas and service
from app.schemas.backtest import (  # noqa: E402
    BacktestMetrics,
    BacktestResult,
    BuyHoldBenchmark,
    EquityPoint,
    OptimizeRequest,
    Trade,
)
from app.services.backtesting.optimizer import MAX_COMBINATIONS, OptimizerService  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(
    sharpe: float,
    total_return: float = 10.0,
    max_dd: float = 5.0,
    num_trades: int = 3,
) -> BacktestResult:
    equity_curve = [
        EquityPoint(date=date(2023, 1, 1), equity=10_000.0),
        EquityPoint(date=date(2023, 12, 31), equity=11_000.0),
    ]
    metrics = BacktestMetrics(
        total_return_pct=total_return,
        max_drawdown_pct=max_dd,
        win_rate_pct=60.0,
        num_trades=num_trades,
        sharpe_ratio=sharpe,
    )
    benchmark = BuyHoldBenchmark(
        total_return_pct=5.0,
        cagr_pct=5.0,
        sharpe_ratio=0.5,
        equity_curve=list(equity_curve),
    )
    return BacktestResult(equity_curve=equity_curve, trades=[], metrics=metrics, benchmark=benchmark)


def _make_req(**overrides) -> OptimizeRequest:
    defaults = dict(
        symbol="AAPL",
        strategy="sma_threshold",
        start=date(2023, 1, 1),
        end=date(2023, 12, 31),
        param_grid={"sma_period": [10, 20]},
        top_n=5,
        initial_cash=10_000.0,
    )
    defaults.update(overrides)
    return OptimizeRequest(**defaults)


def _make_svc() -> OptimizerService:
    """Return an OptimizerService with a mocked inner BacktestService."""
    svc = OptimizerService(MagicMock())
    svc.svc = MagicMock()
    return svc


# ---------------------------------------------------------------------------
# 1. Correct number of combinations are run
# ---------------------------------------------------------------------------

def test_correct_number_of_combinations_run():
    """2 values × 2 values = 4 combos → run_sma_crossover_backtest called 4 times."""
    req = _make_req(
        strategy="sma_crossover",
        param_grid={"fast_period": [5, 10], "slow_period": [20, 30]},
    )
    svc = _make_svc()
    svc.svc.run_sma_crossover_backtest.return_value = _make_result(sharpe=1.0)

    results = svc.run_grid_search(req)

    assert svc.svc.run_sma_crossover_backtest.call_count == 4
    assert len(results) == 4


# ---------------------------------------------------------------------------
# 2. Results are sorted by sharpe_ratio descending
# ---------------------------------------------------------------------------

def test_results_sorted_by_sharpe_descending():
    sharpes = [0.5, 2.0, 1.5, 0.1]
    req = _make_req(
        strategy="sma_threshold",
        param_grid={"sma_period": [10, 20, 30, 40]},
        top_n=10,
    )
    svc = _make_svc()
    svc.svc.run_sma_threshold_backtest.side_effect = [_make_result(s) for s in sharpes]

    results = svc.run_grid_search(req)

    returned_sharpes = [r.sharpe_ratio for r in results]
    assert returned_sharpes == sorted(returned_sharpes, reverse=True)


# ---------------------------------------------------------------------------
# 3. top_n limits the number of results returned
# ---------------------------------------------------------------------------

def test_top_n_limits_results():
    req = _make_req(
        strategy="sma_threshold",
        param_grid={"sma_period": [10, 20, 30, 40, 50]},
        top_n=3,
    )
    svc = _make_svc()
    svc.svc.run_sma_threshold_backtest.return_value = _make_result(sharpe=1.0)

    results = svc.run_grid_search(req)

    assert len(results) == 3


# ---------------------------------------------------------------------------
# 4. Combination cap (>100) raises ValueError
# ---------------------------------------------------------------------------

def test_combination_cap_raises_value_error():
    # 11 × 11 = 121 > 100
    req = _make_req(
        strategy="sma_crossover",
        param_grid={
            "fast_period": list(range(1, 12)),   # 11 values
            "slow_period": list(range(20, 31)),  # 11 values
        },
    )
    svc = _make_svc()

    with pytest.raises(ValueError, match=str(MAX_COMBINATIONS)):
        svc.run_grid_search(req)


# ---------------------------------------------------------------------------
# 5. Unsupported strategy raises ValueError
# ---------------------------------------------------------------------------

def test_unsupported_strategy_raises_value_error():
    req = _make_req(strategy="nonexistent_strategy")
    svc = _make_svc()

    with pytest.raises(ValueError, match="Unknown strategy"):
        svc.run_grid_search(req)


# ---------------------------------------------------------------------------
# 6. Unknown param name raises ValueError
# ---------------------------------------------------------------------------

def test_unknown_param_name_raises_value_error():
    req = _make_req(
        strategy="sma_threshold",
        param_grid={"bad_param": [10, 20]},
    )
    svc = _make_svc()

    with pytest.raises(ValueError, match="Unknown param"):
        svc.run_grid_search(req)


# ---------------------------------------------------------------------------
# 7. Invalid combos (fast_period >= slow_period) are skipped, not crashed
# ---------------------------------------------------------------------------

def test_invalid_combos_are_skipped():
    """fast_period=20, slow_period=10 is invalid → BacktestService raises ValueError → skipped."""
    req = _make_req(
        strategy="sma_crossover",
        param_grid={"fast_period": [5, 20], "slow_period": [10]},
        top_n=10,
    )
    svc = _make_svc()

    def side_effect(*, symbol, start, end, initial_cash, fast_period, slow_period):
        if fast_period >= slow_period:
            raise ValueError("fast_period must be < slow_period")
        return _make_result(sharpe=1.0)

    svc.svc.run_sma_crossover_backtest.side_effect = side_effect

    # (5, 10) is valid; (20, 10) is invalid → only 1 result
    results = svc.run_grid_search(req)
    assert len(results) == 1
    assert results[0].params == {"fast_period": 5, "slow_period": 10}
