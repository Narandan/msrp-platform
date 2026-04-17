"""
Pytest-based integration test for Bollinger Bands support in the indicators API.

Requirements:
- Backend server running locally
- Auth endpoints available
- Stock ingest endpoint available
- Indicators endpoint available

What this test covers:
- Auth setup for protected API access
- Stock data ingestion for a known symbol
- Bollinger Bands-only indicator requests
- Validation of band ordering (upper >= middle >= lower)
- Combined indicator requests (SMA + RSI + Bollinger Bands)
"""
import requests

BASE_URL = "http://127.0.0.1:8000"


def test_bollinger_integration():
    # Step 1: Register/Login
    register_data = {
        "email": "test_bb@example.com",
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
        f"{BASE_URL}/stocks/AAPL/ingest?start=2023-01-01&end=2023-02-28",
        headers=headers
    )
    assert resp.status_code in {200, 400, 409}

    # Step 3: Bollinger Bands only
    resp = requests.get(
        f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&bb_period=20&bb_std=2.0",
        headers=headers
    )
    assert resp.status_code == 200

    data = resp.json()
    assert "points" in data
    assert isinstance(data["points"], list)

    points_with_bb = [p for p in data["points"] if p.get("bb_middle") is not None]
    assert len(points_with_bb) > 0

    sample = points_with_bb[0]

    # Validate ordering
    assert sample["bb_upper"] >= sample["bb_middle"] >= sample["bb_lower"]

    # Step 4: Multiple indicators
    resp = requests.get(
        f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&sma_period=20&rsi_period=14&bb_period=20",
        headers=headers
    )
    assert resp.status_code == 200

    data = resp.json()

    complete_points = [
        p for p in data["points"]
        if all(p.get(k) is not None for k in ["sma", "rsi", "bb_middle", "bb_upper", "bb_lower"])
    ]

    # Don’t over-enforce — just ensure it works
    assert len(complete_points) > 0