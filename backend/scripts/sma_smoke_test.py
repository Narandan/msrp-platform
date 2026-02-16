from datetime import date
from app.services.market_data.stooq_provider import StooqProvider
from app.services.indicators.sma import compute_sma


def main():
    provider = StooqProvider()

    candles = provider.get_candles(
        symbol="AAPL",
        start=date(2023, 1, 1),
        end=date(2023, 3, 1),
    )

    sma_5 = compute_sma(candles, period=5)

    print("Total candles:", len(candles))
    print("First 10 SMA values:")
    for i in range(10):
        print(candles[i].date, sma_5[i])


if __name__ == "__main__":
    main()
