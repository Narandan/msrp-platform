from datetime import date
from app.services.market_data.stooq_provider import StooqProvider


def main():
    provider = StooqProvider()

    candles = provider.get_candles(
        symbol="AAPL",
        start=date(2023, 1, 1),
        end=date(2023, 3, 1),
    )

    print("Total candles:", len(candles))

    if not candles:
        print("No candles returned. Check symbol format and date range.")
        return

    print("First:", candles[0])
    print("Last:", candles[-1])


if __name__ == "__main__":
    main()
