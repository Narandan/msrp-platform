"""
Pytest-based integration test for EMA support in the indicators API.

Requirements:
- Backend server running locally
- Auth endpoints available
- Stock ingest endpoint available
- Indicators endpoint available

What this test covers:
- Auth setup for protected API access
- Stock data ingestion for a known symbol
- EMA-only indicator requests
- Combined indicator requests (SMA + EMA + RSI)
- Full indicator payload requests including Bollinger Bands
- Backward compatibility when EMA is not requested
"""
import requests

BASE_URL = "http://127.0.0.1:8000"


def test_ema_integration():
    # Step 1: Register/Login
    register_data = {
        "email": "test_ema@example.com",
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

    # Step 2: Ingest test data
    resp = requests.post(
        f"{BASE_URL}/stocks/AAPL/ingest?start=2023-01-01&end=2023-02-28",
        headers=headers
    )
    assert resp.status_code in {200, 400, 409}

    # Step 3: EMA only
    resp = requests.get(
        f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&ema_period=20",
        headers=headers
    )
    assert resp.status_code == 200

    data = resp.json()
    assert "symbol" in data
    assert "points" in data
    assert isinstance(data["points"], list)

    points_with_ema = [p for p in data["points"] if p.get("ema") is not None]
    assert len(points_with_ema) > 0

    # Step 4: SMA + EMA + RSI
    resp = requests.get(
        f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&sma_period=20&ema_period=20&rsi_period=14",
        headers=headers
    )
    assert resp.status_code == 200

    data = resp.json()

    complete_points = [
        p for p in data["points"]
        if all(p.get(k) is not None for k in ["sma", "ema", "rsi"])
    ]

    assert len(complete_points) > 0

    sample = complete_points[0]
    assert sample["sma"] is not None
    assert sample["ema"] is not None
    assert sample["rsi"] is not None

    # Step 5: All indicators
    resp = requests.get(
        f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&sma_period=20&ema_period=20&rsi_period=14&bb_period=20",
        headers=headers
    )
    assert resp.status_code == 200

    data = resp.json()
    assert len(data["points"]) > 0

    sample = data["points"][-1]
    expected_fields = ["close", "sma", "ema", "rsi", "bb_middle", "bb_upper", "bb_lower"]

    for field in expected_fields:
        assert field in sample

    # Step 6: Backward compatibility
    resp = requests.get(
        f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&sma_period=20&rsi_period=14",
        headers=headers
    )
    assert resp.status_code == 200

    data = resp.json()
    assert len(data["points"]) > 0

    sample = data["points"][-1]
    assert sample.get("ema") is None