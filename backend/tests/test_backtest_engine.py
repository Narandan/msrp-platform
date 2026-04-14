"""Unit tests for the backtest engine (run_long_only_all_in_out)."""
from datetime import date, timedelta
import pytest

from app.schemas.backtest import EquityPoint, Trade
from app.schemas.strategy import SignalPoint
from app.services.backtesting.engine import CandlePoint, run_long_only_all_in_out


def _candles(n, start_price=100.0, base_date=date(2023, 1, 1)):
    return [CandlePoint(date=base_date + timedelta(days=i), close=start_price + i) for i in range(n)]


def _signal(day_offset, signal, base_date=date(2023, 1, 1)):
    return SignalPoint(date=base_date + timedelta(days=day_offset), signal=signal)


# --- Validation ---

def test_empty_candles_raises():
    with pytest.raises(ValueError, match="candles must be non-empty"):
        run_long_only_all_in_out([], [])


def test_unsorted_candles_raises():
    candles = [
        CandlePoint(date=date(2023, 1, 2), close=100.0),
        CandlePoint(date=date(2023, 1, 1), close=101.0),
    ]
    with pytest.raises(ValueError, match="sorted ascending"):
        run_long_only_all_in_out(candles, [])


def test_zero_close_raises():
    candles = [CandlePoint(date=date(2023, 1, 1), close=0.0)]
    with pytest.raises(ValueError, match="close must be > 0"):
        run_long_only_all_in_out(candles, [])


def test_negative_initial_cash_raises():
    candles = _candles(5)
    with pytest.raises(ValueError, match="initial_cash must be > 0"):
        run_long_only_all_in_out(candles, [], initial_cash=-100.0)


def test_negative_transaction_cost_raises():
    candles = _candles(5)
    with pytest.raises(ValueError, match="transaction_cost_pct must be >= 0"):
        run_long_only_all_in_out(candles, [], transaction_cost_pct=-0.01)


# --- No signals ---

def test_no_signals_equity_equals_initial_cash():
    candles = _candles(5, start_price=100.0)
    equity_curve, trades = run_long_only_all_in_out(candles, [], initial_cash=10_000.0)
    assert len(equity_curve) == 5
    assert len(trades) == 0
    for ep in equity_curve:
        assert ep.equity == pytest.approx(10_000.0)


# --- Buy and hold ---

def test_buy_then_sell_produces_one_trade():
    candles = _candles(5, start_price=100.0)  # closes: 100, 101, 102, 103, 104
    signals = [_signal(0, 1), _signal(4, -1)]
    equity_curve, trades = run_long_only_all_in_out(candles, signals, initial_cash=10_000.0)
    assert len(trades) == 1
    t = trades[0]
    assert t.entry_price == pytest.approx(100.0)
    assert t.exit_price == pytest.approx(104.0)
    assert t.return_pct == pytest.approx(0.04)


def test_equity_curve_length_matches_candles():
    candles = _candles(10)
    equity_curve, _ = run_long_only_all_in_out(candles, [], initial_cash=5_000.0)
    assert len(equity_curve) == 10


def test_equity_marked_to_market_while_in_trade():
    # Buy at day 0 (close=100), hold through day 1 (close=101), sell at day 2 (close=102)
    candles = [
        CandlePoint(date=date(2023, 1, 1), close=100.0),
        CandlePoint(date=date(2023, 1, 2), close=101.0),
        CandlePoint(date=date(2023, 1, 3), close=102.0),
    ]
    signals = [
        SignalPoint(date=date(2023, 1, 1), signal=1),
        SignalPoint(date=date(2023, 1, 3), signal=-1),
    ]
    equity_curve, _ = run_long_only_all_in_out(candles, signals, initial_cash=1000.0)
    # Day 0: buy 10 shares at 100, equity = 10 * 100 = 1000
    assert equity_curve[0].equity == pytest.approx(1000.0)
    # Day 1: still holding, equity = 10 * 101 = 1010
    assert equity_curve[1].equity == pytest.approx(1010.0)
    # Day 2: sell at 102, equity = 10 * 102 = 1020
    assert equity_curve[2].equity == pytest.approx(1020.0)


# --- Transaction costs ---

def test_transaction_cost_reduces_pnl():
    candles = [
        CandlePoint(date=date(2023, 1, 1), close=100.0),
        CandlePoint(date=date(2023, 1, 2), close=100.0),
    ]
    signals = [
        SignalPoint(date=date(2023, 1, 1), signal=1),
        SignalPoint(date=date(2023, 1, 2), signal=-1),
    ]
    _, trades_no_cost = run_long_only_all_in_out(candles, signals, initial_cash=1000.0, transaction_cost_pct=0.0)
    _, trades_with_cost = run_long_only_all_in_out(candles, signals, initial_cash=1000.0, transaction_cost_pct=0.01)
    assert trades_with_cost[0].pnl < trades_no_cost[0].pnl


# --- Stop-loss / take-profit ---

def test_stop_loss_exits_before_strategy_sell():
    candles = [
        CandlePoint(date=date(2023, 1, 1), close=100.0),
        CandlePoint(date=date(2023, 1, 2), close=94.0),
        CandlePoint(date=date(2023, 1, 3), close=110.0),
    ]
    signals = [
        SignalPoint(date=date(2023, 1, 1), signal=1),
    ]
    _, trades = run_long_only_all_in_out(
        candles, signals, initial_cash=1000.0, stop_loss_pct=0.05
    )
    assert len(trades) == 1
    assert trades[0].exit_price == pytest.approx(94.0)
    assert trades[0].reason == "stop_loss"


def test_take_profit_exits_before_strategy_sell():
    candles = [
        CandlePoint(date=date(2023, 1, 1), close=100.0),
        CandlePoint(date=date(2023, 1, 2), close=115.0),
    ]
    signals = [SignalPoint(date=date(2023, 1, 1), signal=1)]
    _, trades = run_long_only_all_in_out(
        candles, signals, initial_cash=1000.0, take_profit_pct=0.10
    )
    assert len(trades) == 1
    assert trades[0].exit_price == pytest.approx(115.0)
    assert trades[0].reason == "take_profit"


# --- Multiple trades ---

def test_multiple_buy_sell_cycles():
    candles = [CandlePoint(date=date(2023, 1, 1) + timedelta(days=i), close=100.0) for i in range(6)]
    signals = [
        SignalPoint(date=date(2023, 1, 1), signal=1),
        SignalPoint(date=date(2023, 1, 2), signal=-1),
        SignalPoint(date=date(2023, 1, 3), signal=1),
        SignalPoint(date=date(2023, 1, 5), signal=-1),
    ]
    _, trades = run_long_only_all_in_out(candles, signals, initial_cash=1000.0)
    assert len(trades) == 2


def test_buy_without_sell_leaves_open_position():
    candles = _candles(5)
    signals = [_signal(0, 1)]  # buy but never sell
    equity_curve, trades = run_long_only_all_in_out(candles, signals, initial_cash=1000.0)
    assert len(trades) == 0  # no closed trade
    # equity should reflect mark-to-market
    assert equity_curve[-1].equity > 0
