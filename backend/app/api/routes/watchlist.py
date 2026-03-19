from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.db.models.stock import Symbol
from app.db.models.watchlist import WatchlistItem
from app.schemas.watchlist import WatchlistEntry, WatchlistResponse, AddWatchlistRequest

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=WatchlistResponse)
def list_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WatchlistResponse:
    """List current user's watchlist symbols."""
    stmt = (
        select(Symbol.ticker, Symbol.name)
        .join(WatchlistItem, WatchlistItem.symbol_id == Symbol.id)
        .where(WatchlistItem.user_id == current_user.id)
        .order_by(Symbol.ticker)
    )
    rows = db.execute(stmt).all()
    return WatchlistResponse(
        symbols=[WatchlistEntry(ticker=r.ticker, name=r.name) for r in rows]
    )


@router.post("", response_model=WatchlistResponse)
def add_to_watchlist(
    body: AddWatchlistRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WatchlistResponse:
    """Add a symbol to the watchlist (symbol must exist in DB)."""
    ticker = body.ticker.strip().upper()
    sym = db.execute(select(Symbol).where(Symbol.ticker == ticker)).scalar_one_or_none()
    if sym is None:
        raise HTTPException(status_code=404, detail=f"Symbol {ticker} not found. Ingest it first.")
    existing = (
        db.execute(
            select(WatchlistItem).where(
                WatchlistItem.user_id == current_user.id,
                WatchlistItem.symbol_id == sym.id,
            )
        )
        .scalar_one_or_none()
    )
    if existing:
        return list_watchlist(db=db, current_user=current_user)
    item = WatchlistItem(user_id=current_user.id, symbol_id=sym.id)
    db.add(item)
    db.commit()
    return list_watchlist(db=db, current_user=current_user)


@router.delete("/{ticker}")
def remove_from_watchlist(
    ticker: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Remove a symbol from the watchlist."""
    ticker = ticker.strip().upper()
    sym = db.execute(select(Symbol).where(Symbol.ticker == ticker)).scalar_one_or_none()
    if sym is None:
        raise HTTPException(status_code=404, detail=f"Symbol {ticker} not found.")
    item = db.execute(
        select(WatchlistItem).where(
            WatchlistItem.user_id == current_user.id,
            WatchlistItem.symbol_id == sym.id,
        )
    ).scalar_one_or_none()
    if item:
        db.delete(item)
        db.commit()
    return {"status": "ok"}
