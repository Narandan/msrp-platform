from datetime import date
from sqlalchemy import select

from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.db.models import Symbol, Candle


def main():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        ticker = "AAPL"

        sym = db.execute(select(Symbol).where(Symbol.ticker == ticker)).scalar_one_or_none()
        if sym is None:
            sym = Symbol(ticker=ticker, name="Apple Inc.")
            db.add(sym)
            db.commit()
            db.refresh(sym)

        c = Candle(
            symbol_id=sym.id,
            date=date(2026, 2, 1),
            open=100.0,
            high=110.0,
            low=95.0,
            close=105.0,
            volume=123456,
        )
        db.add(c)
        db.commit()

        candles = db.execute(
            select(Candle).where(Candle.symbol_id == sym.id).order_by(Candle.date.desc())
        ).scalars().all()

        print(f"OK: symbol={sym.ticker}, candles={len(candles)}")
        print(f"Latest candle: {candles[0].date} close={candles[0].close}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
