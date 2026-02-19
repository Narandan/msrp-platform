from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


# SQLite DB file in the backend root: ./msrp.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./msrp.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a DB session
    and ensures it is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user():
    """
    TEMPORARY STUB.

    Replace this with real authentication later.
    For now, it just returns a fake user so routes depending on
    authentication can run for development/testing.
    """
    return {"id": 1, "email": "demo@example.com"}
