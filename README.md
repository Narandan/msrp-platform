# MSRP — Market Signal & Research Platform

Full-stack web app for stock analysis, technical indicators, backtesting, watchlists, and research tools.

---

## Quick Start

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API: **http://127.0.0.1:8000**
- Docs: **http://127.0.0.1:8000/docs**

### Frontend

```bash
cd frontend
npm install
npm run dev
```

- App: **http://localhost:5173**

### Test User (optional)

If registration fails or for quick login:

```bash
cd backend && source venv/bin/activate
python scripts/create_test_user.py
# Log in with: test@msrp.local / testpass123
```

### Smoke Tests

With the backend running:

```bash
cd backend && source venv/bin/activate
python -m scripts.run_smoke_tests
```

Verifies: `/health`, `/auth/ping`, `/stocks/ping`, `/indicators/ping`, `/backtest/{symbol}` (with optional `transaction_cost_pct` and `strategy=sma_crossover`).

---

## Increment 2 Features

### Backend

| Feature | Description |
|--------|-------------|
| **Auth** | Register, login, JWT; password hashing (bcrypt). |
| **Stocks** | Ingest OHLCV from Stooq; `GET /stocks/{symbol}/candles`; symbol search `GET /stocks/search?q=...` (ticker-only from DB). |
| **Indicators** | `GET /indicators/{symbol}` — SMA, EMA, RSI, Bollinger Bands, MACD (`macd_fast`, `macd_slow`, `macd_signal`). |
| **Backtest** | `GET /backtest/{symbol}` — SMA threshold or SMA crossover strategy; `transaction_cost_pct`; returns equity curve, trades, metrics (total return, max drawdown, win rate, Sharpe). |
| **News** | `GET /news/{symbol}?limit=10` — Google News RSS for the ticker (auth required). |
| **Watchlist** | `GET /watchlist`, `POST /watchlist` (body: `{ "ticker": "AAPL" }`), `DELETE /watchlist/{ticker}` (auth required). |

### Frontend

| Feature | Description |
|--------|-------------|
| **Auth** | Login/register; token stored in `localStorage`. |
| **Dashboard** | Personalized: market status + countdown, watchlist cards (sparklines, “View chart”), “Jump back in” (recent symbols + quick actions), last backtest summary. |
| **Watchlist** | Add/remove symbols; dashboard preview with cards. |
| **Ingest** | Symbol + date range; ingest from Stooq. |
| **Chart** | Load candles; price + volume charts; symbol autocomplete; news panel. |
| **Indicators** | Symbol, date range, SMA/EMA/RSI/Bollinger/MACD toggles; charts. |
| **Backtest** | Strategy (SMA threshold / SMA crossover), transaction cost (bps), date range; equity curve + trade log. |
| **Persistence** | Form state and last-used symbols saved in `localStorage` when switching tabs. |
| **Symbol search** | Autocomplete as you type (debounced) on Ingest, Chart, Indicators, Backtest. |

### Testing

- **Smoke:** `backend/scripts/run_smoke_tests.py` (no pytest).
- **Unit (RSI/MACD):** `cd backend && pytest tests/test_rsi.py tests/test_macd.py -v` (requires `pytest` in venv).

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI, SQLAlchemy, Pydantic, SQLite, httpx, bcrypt, python-jose |
| Frontend | React (Vite), Recharts |
| Data | Stooq (OHLCV), Google News RSS |

---

## Project Structure

```
msrp-platform/
├── backend/
│   ├── app/
│   │   ├── api/routes/   # auth, stocks, indicators, backtest, news, watchlist
│   │   ├── db/models/    # User, Symbol, Candle, WatchlistItem
│   │   ├── services/     # auth, backtesting, indicators, market data, news, strategies
│   │   └── schemas/
│   ├── scripts/          # run_smoke_tests, create_test_user
│   └── tests/            # test_rsi, test_macd
├── frontend/
│   └── src/App.jsx       # Single-page app (auth, dashboard, ingest, chart, indicators, backtest, watchlist)
└── README.md
```

---

## Increment 1 (Baseline)

Increment 1 delivered the core backend: FastAPI, JWT auth, SQLite, Stooq ingestion, SMA/RSI indicators, and a long-only backtest engine. Increment 2 adds the above API extensions, React frontend, watchlist, news, second strategy, transaction costs, and UI/UX improvements.
