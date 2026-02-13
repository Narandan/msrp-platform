from abc import ABC, abstractmethod
from datetime import date
from typing import List
from app.schemas.stock import CandleDTO

class MarketDataProvider(ABC):
    @abstractmethod
    def get_candles(self, symbol: str, start: date, end: date) -> List[CandleDTO]:
        raise NotImplementedError
