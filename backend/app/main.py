# Check for dependencies happens before imports so it will run in time, however,
# this means that if there are missing dependencies, this error will show at the top of the error pile.
from app.core.preflight import checkInstalls
checkInstalls()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import engine
import app.db.models  # noqa: F401 - register all models for create_all
from app.core.config import settings
from app.api.routes.auth import router as auth_router
from app.api.routes.stocks import router as stocks_router
from app.api.routes.indicators import router as indicators_router
from app.api.routes.backtest import router as backtest_router
from app.api.routes.news import router as news_router
from app.api.routes.watchlist import router as watchlist_router

app = FastAPI(title="MSRP Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "server": app.title,
        "version": app.version,
        "docs": "/docs",
        "health": "/health"
    }

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(stocks_router)
app.include_router(indicators_router)
app.include_router(backtest_router)
app.include_router(news_router)
app.include_router(watchlist_router)