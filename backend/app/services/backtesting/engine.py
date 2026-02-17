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
) -> Tuple[List[EquityPoint], List[Trade]]:
    """
    Long-only execution:
      - BUY (signal=1): invest all cash at that day's close
      - SELL (signal=-1): liquidate all shares at that day's close
      - HOLD (0 or missing): do nothing

    Trades execute at the signal day's close.
    Equity is marked-to-market each candle close.
    """
    if initial_cash <= 0:
        raise ValueError("initial_cash must be > 0")

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

            entry_shares = cash / entry_price
            shares = entry_shares
            cash = 0.0
            in_trade = True

        # SELL
        elif sig == -1 and in_trade:
            exit_date = c.date
            exit_price = float(c.close)

            cash = shares * exit_price

            assert entry_date is not None and entry_price is not None
            cost_basis = entry_shares * entry_price
            pnl = cash - cost_basis
            return_pct = (exit_price / entry_price) - 1.0

            reason = (sp.reason if sp is not None else None) or entry_reason

            trades.append(
                Trade(
                    entry_date=entry_date,
                    exit_date=exit_date,
                    entry_price=float(entry_price),
                    exit_price=float(exit_price),
                    pnl=float(pnl),
                    return_pct=float(return_pct),
                    reason=reason,
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
