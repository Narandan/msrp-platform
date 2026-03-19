from typing import List, Optional
from pydantic import BaseModel


class NewsItemDTO(BaseModel):
    title: str
    url: str
    published: Optional[str] = None
    source: Optional[str] = None


class NewsResponse(BaseModel):
    symbol: str
    articles: List[NewsItemDTO]
