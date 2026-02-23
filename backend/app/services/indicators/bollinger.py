"""
Bollinger Bands indicator.

Issue #27 (Increment 1)

Goal:
- Given a series of closing prices and a window length,
  compute middle, upper, and lower bands.

Related:
- app/services/indicators/sma.py   (for moving average logic)
- app/schemas/stock.CandleDTO      (source of price data)
- Future strategies may call this module directly.
"""

# === IMPLEMENTATION ZONE: ISSUE #27 (Bollinger Bands) ===
# TODO:
#   Implement:
#     compute_bollinger(
#         prices: Sequence[float],
#         window: int,
#         k: float = 2.0,
#     ) -> list[tuple[middle: float, upper: float, lower: float]]
#
# Constraints:
#   - Mirror the pattern of compute_sma for windowing.
#   - No FastAPI, no DB imports here.