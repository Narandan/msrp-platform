# MSRP — Market Signal & Research Platform

Full-stack web app for stock analysis, technical indicators, backtesting, watchlists, and research tools.

---

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\Activate.ps1
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
cd backend && source venv/bin/activate   # Windows: .\venv\Scripts\Activate.ps1
python scripts/create_test_user.py
# Log in with: test@msrp.local / testpass123
```

### Smoke Tests

With the backend running:

```bash
cd backend && source venv/bin/activate   # Windows: .\venv\Scripts\Activate.ps1
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
  [OK] OK (endpoint reachable; auth required as expected)
[SMOKE] Checking backtest sma_crossover → ...
  [OK] OK (sma_crossover endpoint reachable; auth required as expected)
=== All smoke checks completed successfully ===
```

On a fresh clone the backtest checks return 401 — that's a **pass**. The smoke test accepts 401 (no token), 400 "Symbol not found" (ingested but no data), or 200 (data present). Pass `MSRP_TOKEN=<your_token>` as an env var to test with auth.

---

## Increment 2 Features

### Backend

| Feature | Description |
|--------|-------------|
| **Auth** | Register, login, JWT; password hashing (bcrypt). |
| **Stocks** | Ingest OHLCV from Stooq; `GET /stocks/{symbol}/candles`; symbol search `GET /stocks/search?q=...` (searches full NASDAQ/NYSE list; falls back to DB when offline). |
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
- **Unit:** `cd backend && pytest tests/ -v` (requires `pytest` in venv).
  - `test_rsi.py` — RSI indicator
  - `test_macd.py` — MACD indicator
  - `test_backtest_engine.py` — backtest execution engine
  - `test_metrics.py` — total return, drawdown, win rate, Sharpe
  - `test_strategies.py` — SMA threshold and SMA crossover signal generation

---

## API Reference (curl Examples)

All protected endpoints require a Bearer token. Get one by logging in first-

```bash
# 1. register
curl -s -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpassword"}'

# 2.login, copy the access_token from the response
curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpassword"}'

# Save the token 
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

# Add symbol 
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
# Get latest 5 headlines for a ticker, Google News RSS
curl -s "http://127.0.0.1:8000/news/AAPL?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

### Indicators

```bash
# SMA + EMA + RSI + Bollinger Bands + MACD
curl -s "http://127.0.0.1:8000/indicators/AAPL?start=2024-01-01&end=2024-12-31&sma_period=20&ema_period=20&rsi_period=14&bb_period=20&macd_fast=12&macd_slow=26&macd_signal=9" \
  -H "Authorization: Bearer $TOKEN"
```
```bash
# SMA threshold strategy (default)
curl -s "http://127.0.0.1:8000/backtest/AAPL?start=2024-01-01&end=2024-12-31&strategy=sma_threshold&sma_period=20&initial_cash=10000&transaction_cost_pct=0.001" \
  -H "Authorization: Bearer $TOKEN"

# SMA crossover strategy (fast/slow periods)
curl -s "http://127.0.0.1:8000/backtest/AAPL?start=2024-01-01&end=2024-12-31&strategy=sma_crossover&fast_period=10&slow_period=30&initial_cash=10000&transaction_cost_pct=0.001" \
  -H "Authorization: Bearer $TOKEN"
```

Backtest requires auth. Returns `equity_curve`, `trades`, and `metrics` (total return, max drawdown, win rate, Sharpe ratio).

# SMA crossover strategy (fast/slow periods)
curl -s "http://127.0.0.1:8000/backtest/AAPL?start=2024-01-01&end=2024-12-31&strategy=sma_crossover&fast_period=10&slow_period=30&initial_cash=10000&transaction_cost_pct=0.001" \
  -H "Authorization: Bearer $TOKEN"
```

Backtest requires auth. Returns `equity_curve`, `trades`, and `metrics` (total return, max drawdown, win rate, Sharpe ratio).

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI, SQLAlchemy, Pydantic, SQLite, httpx, bcrypt, python-jose |
| Frontend | React (Vite), Recharts |
| Data | Stooq (OHLCV), Google News RSS |

---

## Project Structure

`   └── tests/            # test_rsi, test_macd, test_backtest_engine, test_metrics, test_strategies
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
