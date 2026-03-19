"""RSS news fetch for stock symbols (Google News)."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from typing import List
from urllib.parse import quote_plus

import httpx

GOOGLE_NEWS_RSS_BASE = "https://news.google.com/rss/search"


@dataclass
class NewsItem:
    title: str
    url: str
    published: str | None
    source: str | None


def _parse_iso_date(s: str | None) -> str | None:
    """Return date string as-is for API response; normalize if needed."""
    if not s:
        return None
    try:
        # Google RSS often uses RFC 822 style, e.g. "Wed, 18 Mar 2026 20:00:00 GMT"
        for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                datetime.strptime(s.replace(" GMT", "").strip(), fmt.replace(" %Z", "").replace(" %z", "").strip())
                return s
            except ValueError:
                continue
    except Exception:
        pass
    return s


def fetch_stock_news(symbol: str, limit: int = 10) -> List[NewsItem]:
    """
    Fetch stock-related news from Google News RSS.
    Returns list of NewsItem with title, url, published, source.
    """
    query = f"{symbol.upper()} stock"
    params = {
        "q": query,
        "hl": "en-US",
        "gl": "US",
        "ceid": "US:en",
    }
    url = f"{GOOGLE_NEWS_RSS_BASE}?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    items: List[NewsItem] = []
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
    except Exception:
        return items

    # RSS 2.0: channel/item; Atom-style: entry
    for item_el in list(root.iter("item")) + list(root.iter("{http://www.w3.org/2005/Atom}entry")):
        title_el = item_el.find("title") or item_el.find("{http://www.w3.org/2005/Atom}title")
        link_el = item_el.find("link") or item_el.find("{http://www.w3.org/2005/Atom}link")
        pub_el = item_el.find("pubDate") or item_el.find("published") or item_el.find("{http://www.w3.org/2005/Atom}published")
        source_el = item_el.find("source") or item_el.find("{http://www.w3.org/2005/Atom}source")
        title = title_el.text if title_el is not None and title_el.text else ""
        url_str = ""
        if link_el is not None:
            url_str = link_el.text or link_el.get("href") or ""
        published = pub_el.text if pub_el is not None and pub_el.text else None
        source = None
        if source_el is not None:
            source = source_el.text or (source_el.find("title") or source_el.find("{http://www.w3.org/2005/Atom}title"))
            if hasattr(source, "text"):
                source = source.text if source is not None else None
        if title:
            items.append(NewsItem(title=title, url=url_str, published=_parse_iso_date(published), source=source))
        if len(items) >= limit:
            break
    return items[:limit]
