from pydantic import BaseModel
import os
import sys

_DEFAULT_SECRET = "change-me"


class Settings(BaseModel):
    DATABASE_URL: str = "sqlite:///./msrp.db"
    JWT_SECRET: str = _DEFAULT_SECRET
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


def get_settings() -> Settings:
    secret = os.getenv("JWT_SECRET", _DEFAULT_SECRET)
    if secret == _DEFAULT_SECRET:
        print(
            "WARNING: JWT_SECRET is using the default insecure value. "
            "Set the JWT_SECRET environment variable before deploying.",
            file=sys.stderr,
        )
    return Settings(
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./msrp.db"),
        JWT_SECRET=secret,
        JWT_ALGORITHM=os.getenv("JWT_ALGORITHM", "HS256"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        CORS_ORIGINS=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    )


settings = get_settings()
