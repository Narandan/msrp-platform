from __future__ import annotations

from math import sqrt
from typing import List

from app.schemas.backtest import BacktestMetrics, BuyHoldBenchmark, EquityPoint, Trade


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


def _sharpe_ratio(equity_curve: List[EquityPoint], risk_free_rate: float = 0.0) -> float:
    """
    Calculate annualized Sharpe ratio from equity curve.
    
    Args:
        equity_curve: List of equity points over time
        risk_free_rate: Annual risk-free rate (default 0.0 for Increment 1)
    
    Returns:
        Annualized Sharpe ratio, or 0.0 if insufficient data or zero volatility
    
    Formula:
        Sharpe = (mean_return - risk_free_rate) / std_dev_return * sqrt(252)
        
    Assumes daily returns and 252 trading days per year for annualization.
    """
    if len(equity_curve) < 2:
        return 0.0
    
    # Calculate daily returns
    returns: List[float] = []
    for i in range(1, len(equity_curve)):
        prev_equity = float(equity_curve[i - 1].equity)
        curr_equity = float(equity_curve[i].equity)
        
        if prev_equity <= 0.0:
            continue
            
        daily_return = (curr_equity - prev_equity) / prev_equity
        returns.append(daily_return)
    
    if not returns:
        return 0.0
    
    # Calculate mean and standard deviation
    n = len(returns)
    if n < 2:
        return 0.0
    mean_return = sum(returns) / n
    
    # Calculate variance using Bessel's correction (n-1)
    variance = sum((r - mean_return) ** 2 for r in returns) / (n - 1)
    std_dev = variance ** 0.5
    
    # Handle zero volatility
    if std_dev == 0.0:
        return 0.0
    
    # Annualize: multiply by sqrt(252) for daily data
    # 252 = typical number of trading days per year
    annualization_factor = 252 ** 0.5
    
    # Daily risk-free rate (annual rate / 252)
    daily_rf = risk_free_rate / 252.0
    
    sharpe = ((mean_return - daily_rf) / std_dev) * annualization_factor
    
    return float(sharpe)


def _sortino_ratio(equity_curve: List[EquityPoint], risk_free_rate: float = 0.0) -> float:
    """Annualized Sortino ratio using downside semi-deviation."""
    if len(equity_curve) < 2:
        return 0.0

    returns: List[float] = []
    for i in range(1, len(equity_curve)):
        prev = float(equity_curve[i - 1].equity)
        curr = float(equity_curve[i].equity)
        if prev <= 0.0:
            continue
        returns.append((curr - prev) / prev)

    if len(returns) < 2:
        return 0.0

    n = len(returns)
    mean_return = sum(returns) / n
    daily_rf = risk_free_rate / 252.0

    downside = [r for r in returns if r < 0]
    if len(downside) < 2:
        return 0.0

    downside_variance = sum(r ** 2 for r in downside) / (len(downside) - 1)
    downside_std = sqrt(downside_variance)

    if downside_std == 0.0:
        return 0.0

    return float(((mean_return - daily_rf) / downside_std) * sqrt(252))


def _cagr_pct(equity_curve: List[EquityPoint]) -> float:
    """CAGR: (end_equity / start_equity) ^ (1 / years) - 1, expressed as %."""
    if len(equity_curve) < 2:
        return 0.0
    start_equity = float(equity_curve[0].equity)
    end_equity = float(equity_curve[-1].equity)
    if start_equity <= 0.0:
        return 0.0
    days = (equity_curve[-1].date - equity_curve[0].date).days
    years = days / 365.25
    if years <= 0.0:
        return 0.0
    return ((end_equity / start_equity) ** (1.0 / years) - 1.0) * 100.0


def _calmar_ratio(equity_curve: List[EquityPoint]) -> float:
    """Calmar ratio: annualized return / max drawdown."""
    if len(equity_curve) < 2:
        return 0.0

    max_dd = _max_drawdown_pct(equity_curve)
    if max_dd == 0.0:
        return 0.0

    start_date = equity_curve[0].date
    end_date = equity_curve[-1].date
    years = (end_date - start_date).days / 365.25
    if years <= 0:
        return 0.0

    annualized_return = _total_return_pct(equity_curve) / years
    return float(annualized_return / max_dd)


def compute_metrics(*, equity_curve: List[EquityPoint], trades: List[Trade]) -> BacktestMetrics:
    return BacktestMetrics(
        total_return_pct=float(_total_return_pct(equity_curve)),
        max_drawdown_pct=float(_max_drawdown_pct(equity_curve)),
        win_rate_pct=float(_win_rate_pct(trades)),
        num_trades=len(trades),
        sharpe_ratio=float(_sharpe_ratio(equity_curve)),
        sortino_ratio=float(_sortino_ratio(equity_curve)),
        calmar_ratio=float(_calmar_ratio(equity_curve)),
        cagr_pct=float(_cagr_pct(equity_curve)),
    )


def compute_buy_hold_benchmark(*, equity_curve: List[EquityPoint]) -> BuyHoldBenchmark:
    """Metrics for a buy-and-hold equity curve (same formulas as strategy metrics where applicable)."""
    return BuyHoldBenchmark(
        total_return_pct=float(_total_return_pct(equity_curve)),
        cagr_pct=float(_cagr_pct(equity_curve)),
        sharpe_ratio=float(_sharpe_ratio(equity_curve)),
        equity_curve=list(equity_curve),
    )
