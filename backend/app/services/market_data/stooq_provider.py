from datetime import date, datetime, timezone
from typing import List
import httpx

from app.schemas.stock import CandleDTO


class StooqProvider:
    """
    Fetches daily historical OHLCV data from Yahoo Finance (v8 chart API).
    Drop-in replacement for the original Stooq provider.
    """

    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    def get_candles(self, symbol: str, start: date, end: date) -> List[CandleDTO]:
        symbol = symbol.strip().upper()
        # Remove .US suffix if present (Yahoo uses plain tickers)
        if symbol.endswith(".US"):
            symbol = symbol[:-3]

        period1 = int(datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp())
        # Add one day to end so the end date is inclusive
        end_dt = datetime(end.year, end.month, end.day, 23, 59, 59, tzinfo=timezone.utc)
        period2 = int(end_dt.timestamp())

        url = self.BASE_URL.format(symbol=symbol)
        params = {"interval": "1d", "period1": period1, "period2": period2}

        response = httpx.get(url, params=params, headers=self.HEADERS, timeout=15.0)
        response.raise_for_status()

        data = response.json()
        result = data.get("chart", {}).get("result")
        if not result:
            return []

        result = result[0]
        timestamps = result.get("timestamp", [])
        quote = result.get("indicators", {}).get("quote", [{}])[0]

        opens = quote.get("open", [])
        highs = quote.get("high", [])
        lows = quote.get("low", [])
        closes = quote.get("close", [])
        volumes = quote.get("volume", [])

        candles: List[CandleDTO] = []
        prev_close: float | None = None

        for i, ts in enumerate(timestamps):
            try:
                row_date = datetime.fromtimestamp(ts, tz=timezone.utc).date()
                o = opens[i]
                h = highs[i]
                l = lows[i]
                c = closes[i]
                v = volumes[i]

                # Skip rows with None values (market holidays / missing data)
                if any(x is None for x in (o, h, l, c)):
                    continue

                open_p = float(o)
                high_p = float(h)
                low_p = float(l)
                close_p = float(c)
                volume = int(v) if v is not None else 0

                # Basic sanity checks
                if open_p <= 0 or high_p <= 0 or low_p <= 0 or close_p <= 0:
                    continue

                # OHLC consistency checks
                if high_p < max(open_p, close_p):
                    continue
                if low_p > min(open_p, close_p):
                    continue
                if low_p > high_p:
                    continue

                # Reject obvious bad outliers versus previous close
                if prev_close is not None:
                    pct_change = abs(close_p - prev_close) / prev_close
                    if pct_change > 0.50:
                        continue

                candles.append(
                    CandleDTO(
                        date=row_date,
                        open=open_p,
                        high=high_p,
                        low=low_p,
                        close=close_p,
                        volume=volume,
                    )
                )

                prev_close = close_p

            except (IndexError, TypeError, ValueError):
                continue

        candles.sort(key=lambda c: c.date)
        return candles