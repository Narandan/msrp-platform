"""Unit tests for RSI indicator."""
from datetime import date

import pytest
from app.schemas.stock import CandleDTO
from app.services.indicators.rsi import compute_rsi


def test_rsi_empty_candles():
    assert compute_rsi([], period=14) == []


def test_rsi_period_zero_raises():
    candles = [CandleDTO(date=date(2023, 1, 1), open=100, high=105, low=95, close=100, volume=1000)]
    with pytest.raises(ValueError, match="period must be > 0"):
        compute_rsi(candles, period=0)


def test_rsi_first_period_values_none():
    candles = [
        CandleDTO(date=date(2023, 1, i + 1), open=100, high=105, low=95, close=100 + (i % 3) - 1, volume=1000)
        for i in range(20)
    ]
    result = compute_rsi(candles, period=14)
    assert len(result) == 20
    for i in range(14):
        assert result[i] is None
    assert result[14] is not None


def test_rsi_bounded_0_100():
    candles = [
        CandleDTO(date=date(2023, 1, i + 1), open=100, high=105, low=95, close=100 + i * 2, volume=1000)
        for i in range(30)
    ]
    result = compute_rsi(candles, period=14)
    for v in result:
        if v is not None:
            assert 0 <= v <= 100


def test_rsi_all_gains_high_rsi():
    # Monotonically increasing closes -> RSI should be high (e.g. 100 or near)
    candles = [
        CandleDTO(date=date(2023, 1, i + 1), open=100, high=105, low=95, close=100 + i, volume=1000)
        for i in range(30)
    ]
    result = compute_rsi(candles, period=14)
    assert result[14] is not None
    assert result[14] >= 90


def test_rsi_all_losses_low_rsi():
    # Monotonically decreasing closes -> RSI should be low (e.g. 0 or near)
    candles = [
        CandleDTO(date=date(2023, 1, i + 1), open=100, high=105, low=95, close=100 - i, volume=1000)
        for i in range(30)
    ]
    result = compute_rsi(candles, period=14)
    assert result[14] is not None
    assert result[14] <= 10


def test_rsi_flat_prices_mid_rsi():
    candles = [
        CandleDTO(date=date(2023, 1, i + 1), open=100, high=100, low=100, close=100, volume=1000)
        for i in range(20)
    ]
    result = compute_rsi(candles, period=14)
    assert result[14] is not None
    assert 45 <= result[14] <= 55
