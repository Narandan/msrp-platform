from __future__ import annotations

from datetime import date
from typing import List, Optional, Sequence

from app.schemas.strategy import SignalPoint


def generate_bollinger_breakout_signals(
    dates: Sequence[date],
    closes: Sequence[float],
    upper_band: Sequence[Optional[float]],
    lower_band: Sequence[Optional[float]],
) -> List[SignalPoint]:
    """
    Long-only Bollinger Band breakout (mean-reversion) strategy.

    Rules:
      - Skip bars where upper_band[i] or lower_band[i] is None (warm-up)
      - BUY  (signal=1)  when closes[i] <= lower_band[i] and position is flat
      - SELL (signal=-1) when closes[i] >= upper_band[i] and position is long
      - Hold otherwise (no signal emitted)

    Signals strictly alternate between BUY and SELL.
    """
    n = len(dates)
    if len(closes) != n or len(upper_band) != n or len(lower_band) != n:
        raise ValueError(
            "dates, closes, upper_band, and lower_band must all be the same length"
        )

    for i in range(n - 1):
        if dates[i] > dates[i + 1]:
            raise ValueError("dates must be sorted ascending")

    signals: List[SignalPoint] = []
    position = 0  # 0=flat, 1=long

    for i in range(n):
        ub = upper_band[i]
        lb = lower_band[i]

        if ub is None or lb is None:
            continue

        if closes[i] <= lb and position == 0:
            signals.append(
                SignalPoint(
                    date=dates[i],
                    signal=1,
                    reason="price touched lower band",
                )
            )
            position = 1
        elif closes[i] >= ub and position == 1:
            signals.append(
                SignalPoint(
                    date=dates[i],
                    signal=-1,
                    reason="price touched upper band",
                )
            )
            position = 0

    return signals
