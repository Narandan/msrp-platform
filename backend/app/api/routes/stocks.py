from fastapi import APIRouter

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/ping")
def stocks_ping():
    """
    Temporary placeholder endpoint so the stocks router is valid.
    Replace with real stocks endpoints later.
    """
    return {"status": "stocks ok"}
