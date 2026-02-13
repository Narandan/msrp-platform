from fastapi import FastAPI

app = FastAPI(title="MSRP Platform", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}
