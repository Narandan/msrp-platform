"""Unit tests for MACD indicator."""
from datetime import date, timedelta

import pytest
from app.schemas.stock import CandleDTO
from app.services.indicators.macd import compute_macd


def _candles(n, base_date=date(2023, 1, 1)):
    return [
        CandleDTO(date=base_date + timedelta(days=i), open=100 + i, high=105 + i, low=95 + i, close=100 + i, volume=1000)
        for i in range(n)
    ]


def test_macd_empty_candles():
    macd, signal, hist = compute_macd([], fast_period=12, slow_period=26, signal_period=9)
    assert macd == []
    assert signal == []
    assert hist == []


def test_macd_invalid_periods_raise():
    candles = [CandleDTO(date=date(2023, 1, 1), open=100, high=105, low=95, close=100, volume=1000)]
    with pytest.raises(ValueError, match="periods must be > 0"):
        compute_macd(candles, fast_period=0, slow_period=26, signal_period=9)
    with pytest.raises(ValueError, match="fast_period must be < slow_period"):
        compute_macd(candles, fast_period=26, slow_period=12, signal_period=9)


def test_macd_output_length():
    candles = _candles(50)
    macd_line, signal_line, histogram = compute_macd(
        candles, fast_period=12, slow_period=26, signal_period=9
    )
    assert len(macd_line) == 50
    assert len(signal_line) == 50
    assert len(histogram) == 50


def test_macd_first_slow_minus_one_none():
    candles = _candles(40)
    macd_line, signal_line, histogram = compute_macd(
        candles, fast_period=12, slow_period=26, signal_period=9
    )
    for i in range(25):  # first 26-1 = 25 are None for MACD
        assert macd_line[i] is None


def test_macd_histogram_equals_macd_minus_signal():
    base = date(2023, 1, 1)
    candles = [
        CandleDTO(date=base + timedelta(days=i), open=100 + (i % 5), high=105, low=95, close=100 + (i % 5), volume=1000)
        for i in range(50)
    ]
    macd_line, signal_line, histogram = compute_macd(
        candles, fast_period=12, slow_period=26, signal_period=9
    )
    for i in range(len(candles)):
        if macd_line[i] is not None and signal_line[i] is not None and histogram[i] is not None:
            assert abs(histogram[i] - (macd_line[i] - signal_line[i])) < 1e-9


def test_macd_has_valid_values_after_warmup():
    base = date(2023, 1, 1)
    candles = [
        CandleDTO(date=base + timedelta(days=i), open=100 + i * 0.5, high=105 + i, low=95, close=100 + i * 0.5, volume=1000)
        for i in range(50)
    ]
    macd_line, signal_line, histogram = compute_macd(
        candles, fast_period=12, slow_period=26, signal_period=9
    )
    # After index 33 (26-1+9-1) we should have signal; after 25 we have MACD
    assert macd_line[26] is not None
    assert signal_line[34] is not None
    assert histogram[34] is not None
