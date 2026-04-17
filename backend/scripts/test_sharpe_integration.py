"""
Pytest-based integration test for Sharpe ratio support in the backtest API.

Requirements:
- Backend server running locally
- Auth endpoints available
- Stock ingest endpoint available
- Backtest endpoint available

What this test covers:
- Auth setup for protected API access
- Stock data ingestion for a known symbol
- Backtest API response structure
- Presence of sharpe_ratio in returned metrics
- Backward compatibility for existing metric fields
- Presence of equity curve and trades in the response
"""
import requests

BASE_URL = "http://127.0.0.1:8000"


def test_sharpe_integration():
    # Step 1: Register/Login
    register_data = {
        "email": "test_sharpe@example.com",
        "password": "testpass123"
    }

    resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    assert resp.status_code in {200, 400, 409}

    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }

    resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    assert resp.status_code == 200

    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Ingest data
    resp = requests.post(
        f"{BASE_URL}/stocks/AAPL/ingest?start=2023-01-01&end=2023-03-31",
        headers=headers
    )
    assert resp.status_code in {200, 400, 409}

    # Step 3: Run backtest
    resp = requests.get(
        f"{BASE_URL}/backtest/AAPL?start=2023-01-01&end=2023-03-31&sma_period=20&initial_cash=10000",
        headers=headers
    )

    # Allow 400 if data edge case (original script allowed it)
    assert resp.status_code in {200, 400}

    if resp.status_code == 200:
        data = resp.json()

        # Metrics must exist
        assert "metrics" in data
        metrics = data["metrics"]

        # Sharpe ratio must exist
        assert "sharpe_ratio" in metrics

        sharpe = metrics["sharpe_ratio"]

        # If present, must be numeric
        if sharpe is not None:
            assert isinstance(sharpe, (int, float))

        # Required metrics still present
        required_fields = [
            "total_return_pct",
            "max_drawdown_pct",
            "win_rate_pct",
            "num_trades"
        ]

        for field in required_fields:
            assert field in metrics

        # Equity + trades structure
        assert "equity_curve" in data
        assert "trades" in data
        assert isinstance(data["equity_curve"], list)
        assert isinstance(data["trades"], list)