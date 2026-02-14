from datetime import date
from typing import List
import httpx
import csv
from io import StringIO

from app.schemas.stock import CandleDTO


class StooqProvider:
    """
    Fetches daily historical data from Stooq.
    Returns normalized CandleDTO objects.
    """

    BASE_URL = "https://stooq.com/q/d/l/"

    def get_candles(self, symbol: str, start: date, end: date) -> List[CandleDTO]:
        symbol = symbol.strip().lower()
        if "." not in symbol:
            symbol = f"{symbol}.us"


        params = {
            "s": symbol,
            "i": "d"  # daily interval
        }

        response = httpx.get(self.BASE_URL, params=params, timeout=10.0)
        response.raise_for_status()

        candles: List[CandleDTO] = []

        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)

        for row in reader:
            row_date = date.fromisoformat(row["Date"])

            if row_date < start or row_date > end:
                continue

            candles.append(
                CandleDTO(
                    date=row_date,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(float(row["Volume"])) if row["Volume"] else 0,
                )
            )

        candles.sort(key=lambda c: c.date)
        return candles
