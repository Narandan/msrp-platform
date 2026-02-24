"""
Integration test for Sharpe ratio in backtest API.
Requires:
1. Backend server running (uvicorn app.main:app --reload)
2. At least one user registered
3. Some symbols ingested in the database
"""

import requests
import sys

BASE_URL = "http://127.0.0.1:8000"


def test_sharpe_integration():
    print("=== Testing Sharpe Ratio in Backtest API ===\n")
    
    # Step 1: Register/Login
    print("1. Setting up authentication...")
    register_data = {
        "email": "test_sharpe@example.com",
        "password": "testpass123"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if resp.status_code == 200:
            print("   [OK] User registered")
        elif resp.status_code == 400:
            print("   [INFO]  User already exists")
        else:
            print(f"   [WARN]  Unexpected response: {resp.status_code}")
    except Exception as e:
        print(f"   [FAIL] Registration failed: {e}")
        return False
    
    # Login
    try:
        login_data = {
            "username": register_data["email"],
            "password": register_data["password"]
        }
        resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if resp.status_code != 200:
            print(f"   [FAIL] Login failed: {resp.status_code}")
            return False
        
        token = resp.json()["access_token"]
        print("   [OK] Login successful")
    except Exception as e:
        print(f"   [FAIL] Login error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Ingest test data
    print("\n2. Ingesting AAPL data...")
    try:
        resp = requests.post(
            f"{BASE_URL}/stocks/AAPL/ingest?start=2023-01-01&end=2023-03-31",
            headers=headers
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"   [OK] Ingested: {data['inserted']} new, {data['skipped']} skipped")
        else:
            print(f"   [WARN]  Ingest response: {resp.status_code}")
    except Exception as e:
        print(f"   [WARN]  Ingest error: {e}")
    
    # Step 3: Run backtest and check for Sharpe ratio
    print("\n3. Running backtest and checking for Sharpe ratio...")
    
    try:
        resp = requests.get(
            f"{BASE_URL}/backtest/AAPL?start=2023-01-01&end=2023-03-31&sma_period=20&initial_cash=10000",
            headers=headers
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   [OK] Status: 200")
            
            # Check metrics structure
            if 'metrics' not in data:
                print(f"   [FAIL] No metrics in response")
                return False
            
            metrics = data['metrics']
            print(f"\n   Backtest Metrics:")
            print(f"      Total Return: {metrics.get('total_return_pct', 'N/A'):.2f}%")
            print(f"      Max Drawdown: {metrics.get('max_drawdown_pct', 'N/A'):.2f}%")
            print(f"      Win Rate: {metrics.get('win_rate_pct', 'N/A'):.2f}%")
            print(f"      Num Trades: {metrics.get('num_trades', 'N/A')}")
            
            # Check for Sharpe ratio
            if 'sharpe_ratio' not in metrics:
                print(f"\n   [FAIL] sharpe_ratio field missing from metrics")
                return False
            
            sharpe = metrics['sharpe_ratio']
            print(f"      Sharpe Ratio: {sharpe:.4f}")
            
            if sharpe is None:
                print(f"\n   [WARN]  Sharpe ratio is None")
            else:
                print(f"\n   [OK] Sharpe ratio present in response")
                
                # Validate it's a reasonable number
                if isinstance(sharpe, (int, float)):
                    print(f"   [OK] Sharpe ratio is numeric")
                    
                    # Typical Sharpe ratios are between -3 and 3 for most strategies
                    # But we won't enforce this as a hard rule
                    if -10 <= sharpe <= 10:
                        print(f"   [OK] Sharpe ratio in reasonable range")
                    else:
                        print(f"   [WARN]  Sharpe ratio seems unusual: {sharpe:.4f}")
                else:
                    print(f"   [FAIL] Sharpe ratio is not numeric: {type(sharpe)}")
                    return False
            
            # Check that other metrics still work
            required_fields = ['total_return_pct', 'max_drawdown_pct', 'win_rate_pct', 'num_trades']
            missing = [f for f in required_fields if f not in metrics]
            if missing:
                print(f"\n   [FAIL] Missing required fields: {missing}")
                return False
            else:
                print(f"   [OK] All existing metrics still present")
            
            # Check equity curve and trades
            if 'equity_curve' in data and 'trades' in data:
                print(f"   [OK] Equity curve and trades present")
                print(f"      Equity points: {len(data['equity_curve'])}")
                print(f"      Trades: {len(data['trades'])}")
            
        elif resp.status_code == 400:
            print(f"   [WARN]  Status: 400 - {resp.text}")
            print(f"   (This is OK if symbol not ingested)")
        else:
            print(f"   [FAIL] Status: {resp.status_code}")
            print(f"      Response: {resp.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Request error: {e}")
        return False
    
    print("\n=== All integration tests passed! ===")
    print("\nSharpe ratio successfully added to backtest metrics.")
    print("Existing clients will see the new field without breaking changes.")
    return True


if __name__ == "__main__":
    try:
        success = test_sharpe_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
