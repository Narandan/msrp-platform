from fastapi import APIRouter, Depends, Query
from app.api.deps import get_current_user
from app.db.models.user import User
from app.schemas.news import NewsItemDTO, NewsResponse
from app.services.news.rss_service import fetch_stock_news, NewsItem

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/{symbol}", response_model=NewsResponse)
def get_news(
    symbol: str,
    limit: int = Query(10, ge=1, le=50),
    _: User = Depends(get_current_user),
) -> NewsResponse:
    """Fetch RSS stock news for the given symbol (Google News)."""
    items: list[NewsItem] = fetch_stock_news(symbol.strip().upper(), limit=limit)
    return NewsResponse(
        symbol=symbol.strip().upper(),
        articles=[NewsItemDTO(title=i.title, url=i.url, published=i.published, source=i.source) for i in items],
    )
