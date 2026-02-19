from fastapi import APIRouter

router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("/ping")
def indicators_ping():
    """
    Temporary placeholder endpoint so the indicators router is valid.
    Replace with real indicator endpoints later.
    """
    return {"status": "indicators ok"}
