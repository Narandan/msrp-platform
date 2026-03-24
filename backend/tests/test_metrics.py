"""Unit tests for backtest metrics (total return, drawdown, win rate, Sharpe)."""
from datetime import date, timedelta
import pytest

from app.schemas.backtest import EquityPoint, Trade
from app.services.backtesting.metrics import (
    compute_metrics,
    _total_return_pct,
    _max_drawdown_pct,
    _win_rate_pct,
    _sharpe_ratio,
)


def _equity(values, base_date=date(2023, 1, 1)):
    return [EquityPoint(date=base_date + timedelta(days=i), equity=v) for i, v in enumerate(values)]


def _trade(pnl):
    entry = 100.0
    # Keep exit_price > 0 regardless of pnl sign
    exit_price = max(entry + pnl, 0.01)
    return Trade(
        entry_date=date(2023, 1, 1),
        exit_date=date(2023, 1, 2),
        entry_price=entry,
        exit_price=exit_price,
        pnl=pnl,
        return_pct=pnl / entry,
    )


# --- Total return ---

def test_total_return_empty():
    assert _total_return_pct([]) == 0.0


def test_total_return_flat():
    assert _total_return_pct(_equity([1000, 1000, 1000])) == pytest.approx(0.0)


def test_total_return_gain():
    assert _total_return_pct(_equity([1000, 1100])) == pytest.approx(10.0)


def test_total_return_loss():
    assert _total_return_pct(_equity([1000, 900])) == pytest.approx(-10.0)


# --- Max drawdown ---

def test_max_drawdown_empty():
    assert _max_drawdown_pct([]) == 0.0


def test_max_drawdown_no_drawdown():
    assert _max_drawdown_pct(_equity([100, 110, 120])) == pytest.approx(0.0)


def test_max_drawdown_simple():
    # Peak 120, trough 90 -> drawdown = (120-90)/120 = 25%
    assert _max_drawdown_pct(_equity([100, 120, 90])) == pytest.approx(25.0)


def test_max_drawdown_multiple_peaks():
    # Peak 150, trough 100 -> 33.33%
    curve = _equity([100, 150, 130, 100, 140])
    dd = _max_drawdown_pct(curve)
    assert dd == pytest.approx((150 - 100) / 150 * 100, rel=1e-4)


# --- Win rate ---

def test_win_rate_empty():
    assert _win_rate_pct([]) == 0.0


def test_win_rate_all_wins():
    trades = [_trade(10), _trade(5), _trade(1)]
    assert _win_rate_pct(trades) == pytest.approx(100.0)


def test_win_rate_all_losses():
    trades = [_trade(-10), _trade(-5)]
    assert _win_rate_pct(trades) == pytest.approx(0.0)


def test_win_rate_mixed():
    trades = [_trade(10), _trade(-5), _trade(3), _trade(-2)]
    assert _win_rate_pct(trades) == pytest.approx(50.0)


# --- Sharpe ratio ---

def test_sharpe_empty():
    assert _sharpe_ratio([]) == 0.0


def test_sharpe_single_point():
    assert _sharpe_ratio(_equity([1000])) == 0.0


def test_sharpe_zero_volatility():
    # Flat equity -> zero std dev -> Sharpe = 0
    assert _sharpe_ratio(_equity([1000, 1000, 1000, 1000])) == 0.0


def test_sharpe_positive_for_consistent_gains():
    # Steadily increasing equity should yield positive Sharpe
    values = [1000 + i * 10 for i in range(50)]
    sharpe = _sharpe_ratio(_equity(values))
    assert sharpe > 0


def test_sharpe_negative_for_consistent_losses():
    values = [1000 - i * 10 for i in range(50)]
    sharpe = _sharpe_ratio(_equity(values))
    assert sharpe < 0


# --- compute_metrics integration ---

def test_compute_metrics_returns_all_fields():
    equity = _equity([10000, 10500, 10200, 10800])
    trades = [_trade(500), _trade(-300), _trade(600)]
    m = compute_metrics(equity_curve=equity, trades=trades)
    assert m.total_return_pct == pytest.approx(_total_return_pct(equity))
    assert m.max_drawdown_pct == pytest.approx(_max_drawdown_pct(equity))
    assert m.win_rate_pct == pytest.approx(_win_rate_pct(trades))
    assert m.num_trades == 3
    assert isinstance(m.sharpe_ratio, float)
