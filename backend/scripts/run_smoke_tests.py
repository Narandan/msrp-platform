import sys
from typing import Iterable

import requests


BASE_URL = "http://127.0.0.1:8000"


def _check_endpoint(
    path: str,
    *,
    expected_status: Iterable[int] = (200,),
    description: str | None = None,
) -> None:
    url = f"{BASE_URL}{path}"
    desc = description or path
    print(f"[SMOKE] Checking {desc} → {url}")

    try:
        resp = requests.get(url, timeout=5)
    except Exception as e:
        print(f"  [FAIL] FAILED: request error: {e}")
        raise

    if resp.status_code not in expected_status:
        print(f"  [FAIL] FAILED: status {resp.status_code}, body={resp.text[:200]}")
        raise RuntimeError(f"Unexpected status {resp.status_code} for {path}")

    print(f"  [OK] OK (status {resp.status_code})")


def main() -> None:
    print("=== MSRP Backend Smoke Tests ===")
    print(f"Base URL: {BASE_URL}")
    print("NOTE: Make sure `uvicorn app.main:app --reload` is running first.\n")

    # 1. Health
    _check_endpoint("/health", description="health check")

    # 2. Auth stub
    _check_endpoint("/auth/ping", description="auth ping")

    # 3. Stocks stub
    _check_endpoint("/stocks/ping", description="stocks ping")

    # 4. Indicators stub
    _check_endpoint("/indicators/ping", description="indicators ping")

    # 5. Backtest:
    #    Backtest now requires auth. Without a token we expect 401.
    #    If a token is available (MSRP_TOKEN env var), we also accept 200 or 400 "Symbol not found".
    import os
    token = os.environ.get("MSRP_TOKEN", "")
    symbol = "AAPL"
    path = f"/backtest/{symbol}?start=2023-01-01&end=2023-01-10&sma_period=5&initial_cash=10000&transaction_cost_pct=0"
    url = f"{BASE_URL}{path}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    print(f"[SMOKE] Checking backtest endpoint → {url}")

    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"  [FAIL] FAILED: request error: {e}")
        raise

    if resp.status_code == 200:
        print("  [OK] OK (backtest returned 200)")
    elif resp.status_code == 400 and "Symbol not found" in resp.text:
        print("  [OK] OK (endpoint reachable; symbol not yet ingested)")
    elif resp.status_code == 401 and not token:
        print("  [OK] OK (endpoint reachable; auth required as expected)")
    else:
        print(f"  [FAIL] FAILED: status {resp.status_code}, body={resp.text[:200]}")
        raise RuntimeError("Unexpected response from backtest endpoint")

    # 6. Backtest SMA crossover (same symbol/date logic)
    path_crossover = f"/backtest/{symbol}?start=2023-01-01&end=2023-01-10&strategy=sma_crossover&fast_period=5&slow_period=10&initial_cash=10000"
    print(f"[SMOKE] Checking backtest sma_crossover → {BASE_URL}{path_crossover}")
    try:
        resp2 = requests.get(f"{BASE_URL}{path_crossover}", headers=headers, timeout=10)
    except Exception as e:
        print(f"  [FAIL] FAILED: request error: {e}")
        raise
    if resp2.status_code == 200:
        print("  [OK] OK (sma_crossover endpoint reachable)")
    elif resp2.status_code == 400 and "Symbol not found" in resp2.text:
        print("  [OK] OK (sma_crossover endpoint reachable; symbol not yet ingested)")
    elif resp2.status_code == 401 and not token:
        print("  [OK] OK (sma_crossover endpoint reachable; auth required as expected)")
    else:
        print(f"  [FAIL] FAILED: status {resp2.status_code}, body={resp2.text[:200]}")
        raise RuntimeError("Unexpected response from backtest sma_crossover")

    print("\n=== All smoke checks completed successfully ===")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\nSMOKE TESTS FAILED")
        sys.exit(1)
