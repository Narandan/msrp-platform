requiredInstalls = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "pydantic": "pydantic",
    "python-dotenv": "dotenv",
    "httpx": "httpx",
    "pytest": "pytest",
    "bcrypt": "bcrypt",
    "python-jose": "jose",
    "sqlalchemy": "sqlalchemy",
    "passlib": "passlib",
    "requests": "requests",
    "email-validator": "email_validator"
}

def checkInstalls():
    import importlib

    missing = []

    for pkg, alias in requiredInstalls.items():
        try:
            importlib.import_module(alias)
        except ImportError:
            missing.append(pkg)

    if missing:
        print("\nPREFLIGHT CHECK FAILURE:")
        print("Missing dependencies:", ", ".join(missing))
        print("Please install them using:")
        print(f"pip install {' '.join(missing)}\n")