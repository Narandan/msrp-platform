"""
End-to-end API test — simulates a real user session.
Run: python3 e2e_test.py
"""
import json
import sys
import httpx

BASE = "http://localhost:8000"
PASS = "✅"
FAIL = "❌"
results = []

def check(name, ok, detail=""):
    status = PASS if ok else FAIL
    results.append((status, name, detail))
    print(f"  {status}  {name}" + (f"  →  {detail}" if detail else ""))

def run():
    client = httpx.Client(base_url=BASE, timeout=30)

    # ── 1. Health ──────────────────────────────────────────────────
    print("\n── Health ──")
    r = client.get("/health")
    check("GET /health", r.status_code == 200 and r.json() == {"status": "ok"})

    # ── 2. Auth ────────────────────────────────────────────────────
    print("\n── Auth ──")
    r = client.post("/auth/register", json={"email": "e2e@test.com", "password": "E2ePass99!"})
    check("POST /auth/register", r.status_code in (200, 201, 400, 409), f"status={r.status_code}")

    r = client.post("/auth/login", json={"email": "e2e@test.com", "password": "E2ePass99!"})
    check("POST /auth/login", r.status_code == 200, f"status={r.status_code}")
    token = r.json().get("access_token", "")
    check("JWT token present", bool(token))

    H = {"Authorization": f"Bearer {token}"}

    r = client.get("/auth/me", headers=H)
    check("GET /auth/me", r.status_code == 200 and r.json().get("email") == "e2e@test.com")

    # ── 3. Stocks / Ingest ─────────────────────────────────────────
    print("\n── Stocks / Ingest ──")
    r = client.post("/stocks/AAPL/ingest?start=2023-01-01&end=2024-01-01", headers=H)
    check("POST /stocks/AAPL/ingest", r.status_code == 200, str(r.json()))
    d = r.json()
    check("Ingest: total_seen > 0", d.get("total_seen", 0) > 0, f"total_seen={d.get('total_seen')}")

    r = client.get("/stocks/AAPL/candles?limit=10", headers=H)
    check("GET /stocks/AAPL/candles", r.status_code == 200)
    candles = r.json()
    check("Candles: 10 rows returned", len(candles) == 10, f"got {len(candles)}")
    check("Candle has OHLCV fields", all(k in candles[0] for k in ("date","open","high","low","close","volume")))

    r = client.get("/stocks/search?q=MSFT&limit=5", headers=H)
    check("GET /stocks/search?q=MSFT", r.status_code == 200)
    check("Search returns results", len(r.json()) > 0)

    # ── 4. Indicators ──────────────────────────────────────────────
    print("\n── Indicators ──")
    r = client.get(
        "/indicators/AAPL?start=2023-01-01&end=2024-01-01"
        "&rsi_period=14&sma_period=20&ema_period=20"
        "&macd_fast=12&macd_slow=26&macd_signal=9&bb_period=20",
        headers=H
    )
    check("GET /indicators/AAPL (all)", r.status_code == 200, f"status={r.status_code}")
    pts = r.json().get("points", [])
    check("Indicators: points returned", len(pts) > 0, f"count={len(pts)}")
    last = pts[-1]
    check("Indicator point has rsi", "rsi" in last)
    check("Indicator point has sma", "sma" in last)
    check("Indicator point has macd", "macd" in last)
    check("Indicator point has bb_upper", "bb_upper" in last)

    # ── 5. Backtest (GET with query params) ────────────────────────
    print("\n── Backtest ──")
    strategies = [
        ("sma_threshold", "strategy=sma_threshold&sma_period=20"),
        ("sma_crossover", "strategy=sma_crossover&fast_period=10&slow_period=30"),
        ("rsi_threshold", "strategy=rsi_threshold&rsi_period=14&oversold=30&overbought=70"),
        ("macd_crossover", "strategy=macd_crossover&macd_fast=12&macd_slow=26&macd_signal=9"),
        ("bollinger_breakout", "strategy=bollinger_breakout&bb_period=20&bb_std=2.0"),
    ]
    for strat, params in strategies:
        url = f"/backtest/AAPL?start=2023-01-01&end=2024-01-01&initial_cash=10000&{params}"
        r = client.get(url, headers=H)
        ok = r.status_code == 200
        detail = ""
        if ok:
            m = r.json().get("metrics", {})
            detail = f"return={m.get('total_return_pct',0):.1f}% trades={m.get('num_trades',0)}"
        else:
            detail = f"status={r.status_code} {r.text[:80]}"
        check(f"GET /backtest/AAPL?strategy={strat}", ok, detail)

    # ── 6. Optimizer ───────────────────────────────────────────────
    print("\n── Optimizer ──")
    payload = {
        "symbol": "AAPL", "start": "2023-01-01", "end": "2024-01-01",
        "strategy": "sma_threshold",
        "param_grid": {"sma_period": [10, 20, 50]},
        "top_n": 3
    }
    r = client.post("/backtest/optimize", json=payload, headers=H)
    check("POST /backtest/optimize", r.status_code == 200, f"status={r.status_code}")
    if r.status_code == 200:
        opt_results = r.json()
        check("Optimizer returns results", len(opt_results) > 0, f"count={len(opt_results)}")
        check("Optimizer sorted by sharpe desc",
              opt_results[0]["sharpe_ratio"] >= opt_results[-1]["sharpe_ratio"])

    # ── 7. Watchlist ───────────────────────────────────────────────
    print("\n── Watchlist ──")
    # Add AAPL via POST body
    r = client.post("/watchlist", json={"ticker": "AAPL"}, headers=H)
    check("POST /watchlist {ticker:AAPL}", r.status_code in (200, 201), f"status={r.status_code}")

    r = client.get("/watchlist", headers=H)
    check("GET /watchlist", r.status_code == 200)
    syms = [s["ticker"] for s in r.json().get("symbols", [])]
    check("AAPL in watchlist", "AAPL" in syms, f"symbols={syms}")

    # Remove AAPL
    r = client.delete("/watchlist/AAPL", headers=H)
    check("DELETE /watchlist/AAPL", r.status_code in (200, 204), f"status={r.status_code}")

    r = client.get("/watchlist", headers=H)
    syms_after = [s["ticker"] for s in r.json().get("symbols", [])]
    check("AAPL removed from watchlist", "AAPL" not in syms_after)

    # ── 8. News ────────────────────────────────────────────────────
    print("\n── News ──")
    r = client.get("/news/AAPL?limit=5", headers=H)
    check("GET /news/AAPL", r.status_code == 200, f"status={r.status_code}")
    if r.status_code == 200:
        articles = r.json().get("articles", [])
        # News may be empty if Google RSS is blocked; treat as warning not failure
        if articles:
            check("News: articles returned", True, f"count={len(articles)}")
            check("Article has title", bool(articles[0].get("title")))
        else:
            print("  ⚠️  News: 0 articles (Google RSS may be blocked in this environment)")

    # ── 9. ML: Train then Predict ──────────────────────────────────
    print("\n── ML Predictor ──")
    r = client.post(
        "/ml/train/AAPL",
        json={"start": "2023-01-01", "end": "2024-01-01", "model_type": "logistic_regression"},
        headers=H
    )
    check("POST /ml/train/AAPL", r.status_code == 200, f"status={r.status_code}")
    if r.status_code == 200:
        tr = r.json()
        check("Train: accuracy in [0,1]", 0 <= tr.get("test_accuracy", -1) <= 1, f"acc={tr.get('test_accuracy')}")
        check("Train: feature_names present", len(tr.get("feature_names", [])) > 0)

    r = client.get("/ml/predict/AAPL?model_type=logistic_regression", headers=H)
    check("GET /ml/predict/AAPL", r.status_code == 200, f"status={r.status_code}")
    if r.status_code == 200:
        d = r.json()
        check("Predict: up_probability in [0,1]", 0 <= d.get("up_probability", -1) <= 1, f"prob={d.get('up_probability')}")
        check("Predict: direction is up or down", d.get("direction") in ("up", "down"), f"dir={d.get('direction')}")

    # ── Summary ────────────────────────────────────────────────────
    print("\n" + "─" * 50)
    passed = sum(1 for s, _, _ in results if s == PASS)
    failed = sum(1 for s, _, _ in results if s == FAIL)
    print(f"  {PASS} {passed} passed   {FAIL} {failed} failed   (total {len(results)})")
    if failed:
        print("\nFailed checks:")
        for s, name, detail in results:
            if s == FAIL:
                print(f"  {FAIL} {name}  →  {detail}")
    print()
    return failed == 0

if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
