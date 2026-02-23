from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserPublic
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/ping")
async def auth_ping() -> dict:
    """
    Simple liveness check for smoke tests.
    """
    return {"status": "ok"}


@router.post("/register", response_model=UserPublic)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(db=db, email=payload.email, password=payload.password)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = login_user(db=db, email=payload.email, password=payload.password)
    return TokenResponse(access_token=token)

from app.api.deps import get_current_user
from app.db.models.user import User

@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)):
    return current_user

