from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/ping")
def auth_ping():
    """
    Temporary placeholder endpoint so the auth router is valid.
    Replace with real auth endpoints later.
    """
    return {"status": "auth ok"}
