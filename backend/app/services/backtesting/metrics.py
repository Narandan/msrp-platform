from __future__ import annotations

from typing import List

from app.schemas.backtest import BacktestMetrics, EquityPoint, Trade


def _total_return_pct(equity_curve: List[EquityPoint]) -> float:
    if not equity_curve:
        return 0.0
    start = float(equity_curve[0].equity)
    end = float(equity_curve[-1].equity)
    if start <= 0.0:
        return 0.0
    return ((end / start) - 1.0) * 100.0


def _max_drawdown_pct(equity_curve: List[EquityPoint]) -> float:
    if not equity_curve:
        return 0.0

    peak = float(equity_curve[0].equity)
    mdd = 0.0

    for p in equity_curve:
        eq = float(p.equity)
        if eq > peak:
            peak = eq
            continue
        if peak > 0.0:
            dd = (peak - eq) / peak
            if dd > mdd:
                mdd = dd

    return mdd * 100.0


def _win_rate_pct(trades: List[Trade]) -> float:
    if not trades:
        return 0.0
    wins = sum(1 for t in trades if float(t.pnl) > 0.0)
    return (wins / len(trades)) * 100.0


def compute_metrics(*, equity_curve: List[EquityPoint], trades: List[Trade]) -> BacktestMetrics:
    return BacktestMetrics(
        total_return_pct=float(_total_return_pct(equity_curve)),
        max_drawdown_pct=float(_max_drawdown_pct(equity_curve)),
        win_rate_pct=float(_win_rate_pct(trades)),
        num_trades=len(trades),
    )
