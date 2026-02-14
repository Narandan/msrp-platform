from fastapi import FastAPI
from app.api.routes.auth import router as auth_router
from app.api.routes.stocks import router as stocks_router

app = FastAPI(title="MSRP Platform", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(stocks_router)
