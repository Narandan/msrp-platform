"""Feature engineering for ML price direction predictor."""
from __future__ import annotations

from datetime import date
from typing import List, Tuple

import numpy as np

from app.schemas.stock import CandleDTO
from app.services.indicators.rsi import compute_rsi
from app.services.indicators.macd import compute_macd
from app.services.indicators.bollinger import compute_bollinger_bands

FEATURE_NAMES = [
    "return_1d",
    "return_2d",
    "return_3d",
    "return_5d",
    "rsi_norm",
    "macd_hist",
    "bb_zscore",
]


class FeatureBuilder:
    def __init__(
        self,
        rsi_period: int = 14,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        bb_period: int = 20,
        bb_std: float = 2.0,
    ):
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bb_period = bb_period
        self.bb_std = bb_std

    def _compute_indicators(self, candles: List[CandleDTO]):
        """Compute all indicators causally over the full candle array."""
        rsi = compute_rsi(candles, period=self.rsi_period)
        _, _, histogram = compute_macd(
            candles,
            fast_period=self.macd_fast,
            slow_period=self.macd_slow,
            signal_period=self.macd_signal,
        )
        middle, upper, lower = compute_bollinger_bands(
            candles, period=self.bb_period, num_std=self.bb_std
        )
        return rsi, histogram, middle, upper, lower

    def build(
        self, candles: List[CandleDTO]
    ) -> Tuple[np.ndarray, np.ndarray, List[date]]:
        """
        Returns X (n_samples, 7), y (n_samples,), dates.

        For each bar i (from max_warmup to n-2 inclusive):
          - return_1d = (close[i] / close[i-1]) - 1  (if i >= 1, else 0)
          - return_2d = (close[i] / close[i-2]) - 1  (if i >= 2, else 0)
          - return_3d = (close[i] / close[i-3]) - 1  (if i >= 3, else 0)
          - return_5d = (close[i] / close[i-5]) - 1  (if i >= 5, else 0)
          - rsi_norm  = rsi[i] / 100.0  (0.0 if rsi[i] is None)
          - macd_hist = histogram[i]    (0.0 if None)
          - bb_zscore = (close[i] - middle[i]) / (upper[i] - lower[i])  (0.0 if any band is None or upper==lower)

        Target y[i] = 1 if close[i+1] > close[i] else 0.
        Excludes bars where ALL indicators are None (pure warm-up).
        The last bar is excluded (no target available).
        """
        n = len(candles)
        if n < 2:
            return np.empty((0, 7)), np.empty((0,)), []

        closes = [float(c.close) for c in candles]
        dates_all = [c.date for c in candles]

        rsi, histogram, middle, upper, lower = self._compute_indicators(candles)

        # max_warmup: first index where at least one indicator is non-None
        # MACD signal warmup = macd_slow - 1 + macd_signal - 1
        max_warmup = self.macd_slow - 1 + self.macd_signal - 1

        X_rows = []
        y_rows = []
        date_rows = []

        for i in range(max_warmup, n - 1):
            # Skip bars where ALL indicators are None (pure warm-up)
            rsi_val = rsi[i]
            hist_val = histogram[i]
            mid_val = middle[i]

            if rsi_val is None and hist_val is None and mid_val is None:
                continue

            # Lagged returns
            r1 = (closes[i] / closes[i - 1] - 1.0) if i >= 1 else 0.0
            r2 = (closes[i] / closes[i - 2] - 1.0) if i >= 2 else 0.0
            r3 = (closes[i] / closes[i - 3] - 1.0) if i >= 3 else 0.0
            r5 = (closes[i] / closes[i - 5] - 1.0) if i >= 5 else 0.0

            # RSI normalised
            rsi_norm = (rsi_val / 100.0) if rsi_val is not None else 0.0

            # MACD histogram
            macd_h = hist_val if hist_val is not None else 0.0

            # Bollinger z-score
            if mid_val is not None and upper[i] is not None and lower[i] is not None:
                band_width = upper[i] - lower[i]
                bb_z = (closes[i] - mid_val) / band_width if band_width != 0.0 else 0.0
            else:
                bb_z = 0.0

            X_rows.append([r1, r2, r3, r5, rsi_norm, macd_h, bb_z])
            y_rows.append(1 if closes[i + 1] > closes[i] else 0)
            date_rows.append(dates_all[i])

        if not X_rows:
            return np.empty((0, 7)), np.empty((0,)), []

        return np.array(X_rows, dtype=float), np.array(y_rows, dtype=int), date_rows

    def build_latest(self, candles: List[CandleDTO]) -> np.ndarray:
        """Returns feature vector for the most recent bar as shape (1, 7)."""
        n = len(candles)
        if n == 0:
            return np.zeros((1, 7))

        closes = [float(c.close) for c in candles]
        rsi, histogram, middle, upper, lower = self._compute_indicators(candles)

        i = n - 1

        r1 = (closes[i] / closes[i - 1] - 1.0) if i >= 1 else 0.0
        r2 = (closes[i] / closes[i - 2] - 1.0) if i >= 2 else 0.0
        r3 = (closes[i] / closes[i - 3] - 1.0) if i >= 3 else 0.0
        r5 = (closes[i] / closes[i - 5] - 1.0) if i >= 5 else 0.0

        rsi_val = rsi[i]
        rsi_norm = (rsi_val / 100.0) if rsi_val is not None else 0.0

        hist_val = histogram[i]
        macd_h = hist_val if hist_val is not None else 0.0

        mid_val = middle[i]
        if mid_val is not None and upper[i] is not None and lower[i] is not None:
            band_width = upper[i] - lower[i]
            bb_z = (closes[i] - mid_val) / band_width if band_width != 0.0 else 0.0
        else:
            bb_z = 0.0

        return np.array([[r1, r2, r3, r5, rsi_norm, macd_h, bb_z]], dtype=float)
