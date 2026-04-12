from __future__ import annotations

from datetime import date
from typing import List, Optional, Sequence

from app.schemas.strategy import SignalPoint


def generate_rsi_threshold_signals(
    dates: Sequence[date],
    closes: Sequence[float],
    rsi: Sequence[Optional[float]],
    *,
    oversold: float = 30.0,
    overbought: float = 70.0,
) -> List[SignalPoint]:
    """
    Long-only RSI threshold strategy.

    Rules:
      - Ignore periods where RSI is None (warm-up)
      - If rsi < oversold  and position is flat -> BUY  (signal=1)
      - If rsi > overbought and position is long -> SELL (signal=-1)
      - Otherwise hold (no signal emitted)

    Signals strictly alternate between BUY and SELL.
    """
    n = len(dates)
    if len(closes) != n or len(rsi) != n:
        raise ValueError("dates, closes, and rsi must all be the same length")

    for i in range(n - 1):
        if dates[i] > dates[i + 1]:
            raise ValueError("dates must be sorted ascending")

    if oversold >= overbought:
        raise ValueError("oversold must be < overbought")

    signals: List[SignalPoint] = []
    position = 0  # 0=flat, 1=long

    for i in range(n):
        r = rsi[i]
        if r is None:
            continue

        if r < oversold:
            new_position = 1
        elif r > overbought:
            new_position = 0
        else:
            continue  # hold — no state change

        if new_position == position:
            continue  # already in desired state

        if new_position == 1:
            signals.append(
                SignalPoint(
                    date=dates[i],
                    signal=1,
                    reason=f"RSI {r:.2f} < oversold {oversold}",
                )
            )
        else:
            signals.append(
                SignalPoint(
                    date=dates[i],
                    signal=-1,
                    reason=f"RSI {r:.2f} > overbought {overbought}",
                )
            )

        position = new_position

    return signals
