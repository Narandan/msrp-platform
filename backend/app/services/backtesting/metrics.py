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
    mean_return = sum(returns) / n
    
    # Calculate variance
    variance = sum((r - mean_return) ** 2 for r in returns) / n
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


def compute_metrics(*, equity_curve: List[EquityPoint], trades: List[Trade]) -> BacktestMetrics:
    return BacktestMetrics(
        total_return_pct=float(_total_return_pct(equity_curve)),
        max_drawdown_pct=float(_max_drawdown_pct(equity_curve)),
        win_rate_pct=float(_win_rate_pct(trades)),
        num_trades=len(trades),
        sharpe_ratio=float(_sharpe_ratio(equity_curve)),
    )
