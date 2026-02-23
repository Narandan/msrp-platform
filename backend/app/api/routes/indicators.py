from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.indicators import IndicatorsResponse
from app.services.indicators.indicator_service import get_indicator_points

router = APIRouter(prefix="/indicators", tags=["indicators"])

@router.get("/ping")
async def indicators_ping() -> dict:
    """
    Simple liveness check for smoke tests.
    """
    return {"status": "ok"}


@router.get("/{symbol}", response_model=IndicatorsResponse)
def indicators(
    symbol: str,
    start: date = Query(...),
    end: date = Query(...),
    sma_period: Optional[int] = Query(None, ge=1, le=500),
    rsi_period: Optional[int] = Query(None, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    points = get_indicator_points(
        db=db,
        symbol=symbol,
        start=start,
        end=end,
        sma_period=sma_period,
        rsi_period=rsi_period,
    )
    return IndicatorsResponse(symbol=symbol.upper(), points=points)
