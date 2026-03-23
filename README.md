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

Checks: `/health`, `/auth/ping`, `/stocks/ping`, `/indicators/ping`, `/backtest/AAPL` (both `sma_threshold` and `sma_crossover`).

Expected output (fresh clone, no data ingested yet):

```
=== MSRP Backend Smoke Tests ===
[SMOKE] Checking health check → http://127.0.0.1:8000/health
  [OK] OK (status 200)
[SMOKE] Checking auth ping → http://127.0.0.1:8000/auth/ping
  [OK] OK (status 200)
[SMOKE] Checking stocks ping → http://127.0.0.1:8000/stocks/ping
  [OK] OK (status 200)
[SMOKE] Checking indicators ping → http://127.0.0.1:8000/indicators/ping
  [OK] OK (status 200)
[SMOKE] Checking backtest endpoint → ...
  [OK] OK (endpoint reachable; symbol not yet ingested)
[SMOKE] Checking backtest sma_crossover → ...
  [OK] OK (sma_crossover endpoint reachable)
=== All smoke checks completed successfully ===
```

A 400 "Symbol not found" on the backtest checks is a **pass** — it means the endpoint is wired correctly, AAPL just hasn't been ingested yet. Once you ingest data the same checks return 200.

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

## API Reference (curl Examples)

All protected endpoints require a Bearer token. Get one by logging in first:

```bash
# 1. Register
curl -s -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpassword"}'

# 2. Login — copy the access_token from the response
curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpassword"}'

# Save the token (replace <TOKEN> in all examples below)
TOKEN="eyJ..."
```

### Stocks & Search

```bash
# Ingest OHLCV data for a symbol
curl -s -X POST "http://127.0.0.1:8000/stocks/AAPL/ingest?start=2024-01-01&end=2024-12-31" \
  -H "Authorization: Bearer $TOKEN"

# Get candles
curl -s "http://127.0.0.1:8000/stocks/AAPL/candles?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Search symbols (online: searches full NASDAQ/NYSE list; offline: falls back to DB only)
curl -s "http://127.0.0.1:8000/stocks/search?q=AAP" \
  -H "Authorization: Bearer $TOKEN"
```

### Watchlist

```bash
# List watchlist
curl -s http://127.0.0.1:8000/watchlist \
  -H "Authorization: Bearer $TOKEN"

# Add symbol (must be ingested first)
curl -s -X POST http://127.0.0.1:8000/watchlist \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ticker":"AAPL"}'

# Remove symbol
curl -s -X DELETE http://127.0.0.1:8000/watchlist/AAPL \
  -H "Authorization: Bearer $TOKEN"
```

### News

```bash
# Get latest 5 headlines for a ticker (Google News RSS)
curl -s "http://127.0.0.1:8000/news/AAPL?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

### Indicators

```bash
# SMA + EMA + RSI + Bollinger Bands + MACD
curl -s "http://127.0.0.1:8000/indicators/AAPL?start=2024-01-01&end=2024-12-31&sma_period=20&ema_period=20&rsi_period=14&bb_period=20&macd_fast=12&macd_slow=26&macd_signal=9" \
  -H "Authorization: Bearer $TOKEN"
```

### Backtest

`transaction_cost_pct` is a decimal fraction of trade value charged per transaction (e.g. `0.001` = 0.1%, `0.0` = no cost). Valid range: 0.0 – 0.1.

```bash
# SMA threshold strategy (default)
curl -s "http://127.0.0.1:8000/backtest/AAPL?start=2024-01-01&end=2024-12-31&strategy=sma_threshold&sma_period=20&initial_cash=10000&transaction_cost_pct=0.001"

# SMA crossover strategy (fast/slow periods)
curl -s "http://127.0.0.1:8000/backtest/AAPL?start=2024-01-01&end=2024-12-31&strategy=sma_crossover&fast_period=10&slow_period=30&initial_cash=10000&transaction_cost_pct=0.001"
```

Backtest does not require auth. Returns `equity_curve`, `trades`, and `metrics` (total return, max drawdown, win rate, Sharpe ratio).

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
