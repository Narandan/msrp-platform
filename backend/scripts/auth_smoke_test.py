from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.services.auth_service import register_user, login_user

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        email = "auth_test@example.com"
        password = "password123"

        user = register_user(db, email=email, password=password)
        print("REGISTER OK:", user.email)

        token = login_user(db, email=email, password=password)
        print("LOGIN OK: token starts with", token[:10])

    finally:
        db.close()

if __name__ == "__main__":
    main()
