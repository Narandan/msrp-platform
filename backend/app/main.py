from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.stocks import router as stocks_router
from app.api.routes.indicators import router as indicators_router
from app.api.routes.backtest import router as backtest_router

app = FastAPI(title="MSRP Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(stocks_router)
app.include_router(indicators_router)
app.include_router(backtest_router)