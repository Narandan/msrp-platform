from pydantic import BaseModel
import os


class Settings(BaseModel):
    DATABASE_URL: str = "sqlite:///./msrp.db"
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


def get_settings() -> Settings:
    return Settings(
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./msrp.db"),
        JWT_SECRET=os.getenv("JWT_SECRET", "change-me"),
        JWT_ALGORITHM=os.getenv("JWT_ALGORITHM", "HS256"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
    )


settings = get_settings()
