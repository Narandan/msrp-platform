from datetime import date
from app.services.market_data.stooq_provider import StooqProvider
from app.services.indicators.rsi import compute_rsi


def main():
    provider = StooqProvider()

    candles = provider.get_candles(
        symbol="AAPL",
        start=date(2023, 1, 1),
        end=date(2023, 3, 1),
    )

    rsi14 = compute_rsi(candles, period=14)

    print("Total candles:", len(candles))
    print("First 20 RSI values:")
    for i in range(min(20, len(candles))):
        print(candles[i].date, rsi14[i])

    # Quick sanity: find first non-None and show it
    first_idx = next((i for i, v in enumerate(rsi14) if v is not None), None)
    if first_idx is not None:
        print("First computed RSI:", candles[first_idx].date, round(rsi14[first_idx], 2))


if __name__ == "__main__":
    main()
