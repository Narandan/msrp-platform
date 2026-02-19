# msrp-platform

Market Signal & Research Platform — a full-stack web app for stock analysis, technical indicators, pattern-based screeners, watchlists, and light ML trend predictions.

---

## Backend Setup (Increment 1)

### 1. Clone the Repository

- `git clone <repo-url>`
- `cd msrp-platform`

### 2. Create and Activate Virtual Environment

- `cd backend`
- `python3 -m venv venv`
- `source venv/bin/activate` (macOS / Linux)  
- `venv\Scripts\activate` (Windows)

### 3. Install Dependencies (Pinned)

- `pip install -r requirements.txt`

Dependencies are pinned to reduce version conflicts between teammates.

### 4. Run the Backend

- `uvicorn app.main:app --reload`

Backend runs at:

- `http://127.0.0.1:8000`

Interactive API documentation:

- `http://127.0.0.1:8000/docs`

---

## Smoke Tests

With the backend running in one terminal, open another terminal and run:

- `cd backend`
- `source venv/bin/activate`
- `python -m scripts.run_smoke_tests`

This verifies:

- `GET /health`
- `GET /auth/ping`
- `GET /stocks/ping`
- `GET /indicators/ping`
- `GET /backtest/{symbol}`

If everything is working correctly, you should see:

- `=== All smoke checks completed successfully ===`

---

## Increment 1 Scope

Backend currently includes:

- Symbol & Candle database models  
- SMA threshold backtesting engine  
- Technical indicator services  
- Structured API routing  
- Dependency guardrails (pinned requirements + smoke test runner)  

---

## Tech Stack

**Backend**

- FastAPI  
- SQLAlchemy  
- Pydantic  
- SQLite (Increment 1)  

---

## Future Increments

Planned features:

- RSS news endpoint  
- Symbol search with autocomplete  
- UI integration improvements  
- Additional trading strategies  
- Authentication hardening  
