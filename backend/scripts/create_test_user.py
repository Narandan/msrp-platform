#!/usr/bin/env python3
"""
Create a test user in the database so you can log in without registering.
Usage (from backend directory, with venv activated):
  python scripts/create_test_user.py

Default test credentials:
  Email:    test@msrp.local
  Password: testpass123
"""
import sys
from pathlib import Path

# Add backend to path so app imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal
from app.db.base import Base
from app.db import models  # noqa: F401 - register models
from app.db.session import engine
from app.db.models.user import User
from sqlalchemy import select
import bcrypt


def _hash_password(password: str) -> str:
    """Hash password with bcrypt (passlib-compatible format for verify at login)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

TEST_EMAIL = "test@msrp.local"
TEST_PASSWORD = "testpass123"


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.execute(select(User).where(User.email == TEST_EMAIL)).scalar_one_or_none()
        if existing:
            print(f"Test user already exists: {TEST_EMAIL}")
            print("You can log in with:")
            print(f"  Email:    {TEST_EMAIL}")
            print(f"  Password: {TEST_PASSWORD}")
            return
        user = User(email=TEST_EMAIL, password_hash=_hash_password(TEST_PASSWORD))
        db.add(user)
        db.commit()
        print("Test user created successfully.")
        print()
        print("Log in with:")
        print(f"  Email:    {TEST_EMAIL}")
        print(f"  Password: {TEST_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
