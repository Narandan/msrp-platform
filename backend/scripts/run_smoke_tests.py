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
        print(f"  ❌ FAILED: request error: {e}")
        raise

    if resp.status_code not in expected_status:
        print(f"  ❌ FAILED: status {resp.status_code}, body={resp.text[:200]}")
        raise RuntimeError(f"Unexpected status {resp.status_code} for {path}")

    print(f"  ✅ OK (status {resp.status_code})")


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
    #    For now, we don't know what symbols are ingested on a fresh clone.
    #    So we accept either:
    #      - 200 OK (backtest ran)
    #      - 400 with "Symbol not found" (endpoint wiring is correct)
    symbol = "AAPL"
    path = f"/backtest/{symbol}?start=2023-01-01&end=2023-01-10&sma_period=5&initial_cash=10000"

    url = f"{BASE_URL}{path}"
    print(f"[SMOKE] Checking backtest endpoint → {url}")

    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        print(f"  ❌ FAILED: request error: {e}")
        raise

    if resp.status_code == 200:
        print("  ✅ OK (backtest returned 200)")
    elif resp.status_code == 400 and "Symbol not found" in resp.text:
        print("  ✅ OK (endpoint reachable; symbol not yet ingested)")
    else:
        print(f"  ❌ FAILED: status {resp.status_code}, body={resp.text[:200]}")
        raise RuntimeError("Unexpected response from backtest endpoint")

    print("\n=== All smoke checks completed successfully ===")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\nSMOKE TESTS FAILED")
        sys.exit(1)
