from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Sequence, Tuple

from app.schemas.backtest import EquityPoint, Trade
from app.schemas.strategy import SignalPoint


@dataclass(frozen=True)
class CandlePoint:
    date: date
    close: float


def _signal_map(signals: Sequence[SignalPoint]) -> Dict[date, SignalPoint]:
    m: Dict[date, SignalPoint] = {}
    for s in signals:
        m[s.date] = s
    return m


def _validate_candles(candles: Sequence[CandlePoint]) -> None:
    if not candles:
        raise ValueError("candles must be non-empty")

    for i in range(len(candles) - 1):
        if candles[i].date > candles[i + 1].date:
            raise ValueError("candles must be sorted ascending by date")

    for c in candles:
        if c.close is None:
            raise ValueError("candle.close cannot be None")
        if float(c.close) <= 0.0:
            raise ValueError("candle.close must be > 0")


def run_long_only_all_in_out(
    candles: Sequence[CandlePoint],
    signals: Sequence[SignalPoint],
    *,
    initial_cash: float = 10_000.0,
    transaction_cost_pct: float = 0.0,
    stop_loss_pct: float = 0.0, # Both are default disabled
    take_profit_pct: float = 0.0, # ^^^
) -> Tuple[List[EquityPoint], List[Trade]]:
    """
    Long-only execution:
      - BUY (signal=1): invest all cash at that day's close
      - SELL (signal=-1): liquidate all shares at that day's close
      - HOLD (0 or missing): do nothing

    Trades execute at the signal day's close.
    Equity is marked-to-market each candle close.
    transaction_cost_pct: applied per trade as a fraction of notional (e.g. 0.001 = 0.1%).
    stop_loss_pct: exit trade if price drops below entry_price * (1 - stop_loss_pct). Both stop_loss_pct and take_profit_pct are disabled by 0.0
    take_profit_pct: exit trade if price rises above entry_price * (1 + take_profit_pct).
    """
    if initial_cash <= 0:
        raise ValueError("initial_cash must be > 0")
    if transaction_cost_pct < 0.0:
        raise ValueError("transaction_cost_pct must be >= 0")
    if stop_loss_pct < 0.0:
        raise ValueError("stop_loss_pct must be >= 0")
    if take_profit_pct < 0.0:
        raise ValueError("take_profit_pct must be >= 0")

    _validate_candles(candles)
    sig_by_date = _signal_map(signals)

    cash = float(initial_cash)
    shares = 0.0

    equity_curve: List[EquityPoint] = []
    trades: List[Trade] = []

    in_trade = False
    entry_date: Optional[date] = None
    entry_price: Optional[float] = None
    entry_reason: Optional[str] = None
    entry_shares: float = 0.0

    for c in candles:
        sp = sig_by_date.get(c.date)
        sig = int(sp.signal) if sp is not None else 0

        # BUY
        if sig == 1 and not in_trade:
            entry_date = c.date
            entry_price = float(c.close)
            entry_reason = sp.reason if sp is not None else None
            # Spend cash including transaction cost: shares * price * (1 + cost_pct) = cash
            entry_shares = cash / (entry_price * (1.0 + transaction_cost_pct)) if transaction_cost_pct > 0 else cash / entry_price
            shares = entry_shares
            cash = 0.0
            in_trade = True

        if in_trade:
            exit_reason = None
            if sig == -1:
                exit_reason = (sp.reason if sp is not None else None) or entry_reason or "strategy"
            elif stop_loss_pct > 0 and c.close <= entry_price * (1 - stop_loss_pct):
                exit_reason = "stop_loss"
            elif take_profit_pct > 0 and c.close >= entry_price * (1 + take_profit_pct):
                exit_reason = "take_profit"
            if exit_reason is not None:
                exit_date = c.date
                exit_price = float(c.close)

                cash = shares * exit_price * (1.0 - transaction_cost_pct) if transaction_cost_pct > 0 else shares * exit_price

                assert entry_date is not None and entry_price is not None
                cost_basis = entry_shares * entry_price
                pnl = cash - cost_basis
                return_pct = (exit_price / entry_price) - 1.0

                trades.append(
                    Trade(
                        entry_date=entry_date,
                        exit_date=exit_date,
                        entry_price=float(entry_price),
                        exit_price=float(exit_price),
                        pnl=float(pnl),
                        return_pct=float(return_pct),
                        reason=exit_reason,
                    )
                )

                # Reset
                shares = 0.0
                entry_shares = 0.0
                in_trade = False
                entry_date = None
                entry_price = None
                entry_reason = None

        equity = cash + shares * float(c.close)
        equity_curve.append(EquityPoint(date=c.date, equity=float(equity)))

    return equity_curve, trades


def run_buy_and_hold_equity(
    candles: Sequence[CandlePoint],
    *,
    initial_cash: float = 10_000.0,
    transaction_cost_pct: float = 0.0,
) -> List[EquityPoint]:
    """
    Invest all cash at the first candle's close (same fee model as a BUY in run_long_only_all_in_out),
    then mark equity to market at each subsequent close.
    """
    if initial_cash <= 0:
        raise ValueError("initial_cash must be > 0")
    if transaction_cost_pct < 0.0:
        raise ValueError("transaction_cost_pct must be >= 0")

    _validate_candles(candles)
    first_close = float(candles[0].close)
    if transaction_cost_pct > 0:
        shares = initial_cash / (first_close * (1.0 + transaction_cost_pct))
    else:
        shares = initial_cash / first_close

    return [EquityPoint(date=c.date, equity=float(shares * float(c.close))) for c in candles]
