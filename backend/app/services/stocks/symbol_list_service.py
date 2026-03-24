"""
Load and search a full list of US symbols (NASDAQ + NYSE) for autocomplete.
Symbols are fetched from public CSV sources and cached in memory.
"""
from __future__ import annotations

import csv
from io import StringIO
from typing import List, Optional

import httpx

from app.schemas.stock import SymbolSearchResult

# Public CSV sources (no API key required)
NASDAQ_LIST_URL = "https://raw.githubusercontent.com/datasets/nasdaq-listings/main/data/nasdaq-listed.csv"
NYSE_LIST_URL = "https://raw.githubusercontent.com/datasets/nyse-listings/main/data/nyse-listed.csv"

_CACHE: Optional[List[tuple[str, Optional[str]]]] = None  # [(ticker, name), ...]
_LOAD_ATTEMPTED = False


def _fetch_csv(url: str) -> List[tuple[str, Optional[str]]]:
    """Fetch a CSV from url and return list of (ticker, name)."""
    out: List[tuple[str, Optional[str]]] = []
    with httpx.Client(timeout=15.0) as client:
        resp = client.get(url)
        resp.raise_for_status()
        text = resp.text
    reader = csv.DictReader(StringIO(text))
    rows = list(reader)
    if not rows:
        return out
    # NASDAQ: Symbol, Security Name
    # NYSE: ACT Symbol, Company Name
    ticker_key = "Symbol" if "Symbol" in rows[0] else "ACT Symbol"
    name_key = "Security Name" if "Security Name" in rows[0] else "Company Name"
    for row in rows:
        ticker = (row.get(ticker_key) or "").strip()
        name = (row.get(name_key) or "").strip() or None
        if ticker and not ticker.startswith("$"):  # skip test/placeholder symbols
            out.append((ticker.upper(), name))
    return out


def _load_all_symbols() -> List[tuple[str, Optional[str]]]:
    """Load NASDAQ + NYSE symbols; cache in memory."""
    global _CACHE, _LOAD_ATTEMPTED
    if _CACHE is not None:
        return _CACHE
    if _LOAD_ATTEMPTED:
        return []  # already tried and failed
    _LOAD_ATTEMPTED = True
    combined: dict[str, Optional[str]] = {}  # ticker -> name (dedupe by ticker)
    for url in (NASDAQ_LIST_URL, NYSE_LIST_URL):
        try:
            for ticker, name in _fetch_csv(url):
                if ticker not in combined:
                    combined[ticker] = name
        except Exception:
            continue
    _CACHE = [(t, n) for t, n in sorted(combined.items())]
    return _CACHE


def search_symbols(query: str, limit: int = 50) -> List[SymbolSearchResult]:
    """
    Search the full symbol list by ticker (starts-with first, then contains).
    Returns up to `limit` results. Uses all available NASDAQ/NYSE symbols.
    """
    if not query or not query.strip():
        return []
    q = query.strip().upper()
    symbols = _load_all_symbols()
    starts_with: List[SymbolSearchResult] = []
    contains: List[SymbolSearchResult] = []
    for ticker, name in symbols:
        if ticker.startswith(q):
            starts_with.append(SymbolSearchResult(ticker=ticker, name=name))
            if len(starts_with) >= limit:
                return starts_with[:limit]
        elif q in ticker:
            contains.append(SymbolSearchResult(ticker=ticker, name=name))
    result = starts_with
    for s in contains:
        if len(result) >= limit:
            break
        result.append(s)
    return result[:limit]
