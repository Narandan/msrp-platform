from __future__ import annotations

from typing import List
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import User


router = APIRouter(prefix="/news", tags=["news"])


class NewsArticle(BaseModel):
    title: str
    url: str
    source: str | None = None
    published: str | None = None


class NewsResponse(BaseModel):
    symbol: str
    articles: List[NewsArticle]


def _parse_google_news_rss(xml_text: str) -> List[NewsArticle]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise HTTPException(status_code=502, detail=f"Failed to parse news feed: {e}")

    channel = root.find("channel")
    if channel is None:
        return []

    articles: List[NewsArticle] = []

    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        url = (item.findtext("link") or "").strip()
        published = (item.findtext("pubDate") or "").strip() or None

        source = None
        source_el = item.find("{http://search.yahoo.com/mrss/}source")
        if source_el is not None and source_el.text:
            source = source_el.text.strip()

        if not source:
            source_text = item.findtext("source")
            if source_text:
                source = source_text.strip()

        if title and url:
            articles.append(
                NewsArticle(
                    title=title,
                    url=url,
                    source=source,
                    published=published,
                )
            )

    return articles


@router.get("/{symbol}", response_model=NewsResponse)
async def get_news(
    symbol: str,
    limit: int = Query(10, ge=1, le=25),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> NewsResponse:
    ticker = symbol.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Symbol is required")

    # Keep db dependency so auth/session behavior stays consistent with the rest of the app.
    _ = db

    query = quote_plus(f"{ticker} stock")
    rss_url = f"https://news.google.com/rss/search?q={query}"

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(
                rss_url,
                headers={
                    "User-Agent": "Mozilla/5.0 MSRP-News/1.0",
                    "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
                },
            )
            resp.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch news feed: {e}")

    articles = _parse_google_news_rss(resp.text)[:limit]

    return NewsResponse(symbol=ticker, articles=articles)
