from __future__ import annotations

from datetime import date

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base, relationship


# NOTE:
# This Base is local to this models module. If you later reintroduce
# a shared Base in app/db/__init__.py or similar, you can switch these
# classes to inherit from that instead.
Base = declarative_base()


class Symbol(Base):
    __tablename__ = "symbols"  # adjust if your actual table name differs

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)

    # relationship to Candle
    candles = relationship("Candle", back_populates="symbol")


class Candle(Base):
    __tablename__ = "candles"  # adjust if your actual table name differs

    id = Column(Integer, primary_key=True, index=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), index=True, nullable=False)

    date = Column(Date, index=True, nullable=False)

    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)

    # volume type depends on your schema; BigInteger is common for volumes
    volume = Column(BigInteger, nullable=True)

    symbol = relationship("Symbol", back_populates="candles")
