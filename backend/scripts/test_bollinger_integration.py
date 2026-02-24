"""
Integration test for Bollinger Bands through the API endpoint.
Requires:
1. Backend server running (uvicorn app.main:app --reload)
2. At least one user registered
3. Some symbols ingested in the database
"""

import requests
import sys

BASE_URL = "http://127.0.0.1:8000"


def test_bollinger_integration():
    print("=== Testing Bollinger Bands Integration ===\n")
    
    # Step 1: Register/Login
    print("1. Setting up authentication...")
    register_data = {
        "email": "test_bb@example.com",
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
            f"{BASE_URL}/stocks/AAPL/ingest?start=2023-01-01&end=2023-02-28",
            headers=headers
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"   [OK] Ingested: {data['inserted']} new, {data['skipped']} skipped")
        else:
            print(f"   [WARN]  Ingest response: {resp.status_code}")
    except Exception as e:
        print(f"   [WARN]  Ingest error: {e}")
    
    # Step 3: Test indicators endpoint with Bollinger Bands
    print("\n3. Testing indicators endpoint with Bollinger Bands...")
    
    try:
        # Test with just Bollinger Bands
        resp = requests.get(
            f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&bb_period=20&bb_std=2.0",
            headers=headers
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   [OK] Status: 200")
            print(f"   Symbol: {data['symbol']}")
            print(f"   Points returned: {len(data['points'])}")
            
            # Check that Bollinger Bands are present
            points_with_bb = [p for p in data['points'] if p.get('bb_middle') is not None]
            print(f"   Points with BB values: {len(points_with_bb)}")
            
            if points_with_bb:
                sample = points_with_bb[0]
                print(f"\n   Sample point (date: {sample['date']}):")
                print(f"      Close:     {sample['close']:.2f}")
                print(f"      BB Middle: {sample['bb_middle']:.2f}")
                print(f"      BB Upper:  {sample['bb_upper']:.2f}")
                print(f"      BB Lower:  {sample['bb_lower']:.2f}")
                
                # Verify ordering
                if sample['bb_upper'] >= sample['bb_middle'] >= sample['bb_lower']:
                    print(f"   [OK] Band ordering correct")
                else:
                    print(f"   [FAIL] Band ordering incorrect")
                    return False
            else:
                print(f"   [WARN]  No Bollinger Bands values found")
        else:
            print(f"   [FAIL] Status: {resp.status_code}")
            print(f"      Response: {resp.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Request error: {e}")
        return False
    
    # Step 4: Test with multiple indicators
    print("\n4. Testing with multiple indicators (SMA + RSI + BB)...")
    
    try:
        resp = requests.get(
            f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&sma_period=20&rsi_period=14&bb_period=20",
            headers=headers
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   [OK] Status: 200")
            
            # Find a point with all indicators
            complete_points = [
                p for p in data['points'] 
                if all(p.get(k) is not None for k in ['sma', 'rsi', 'bb_middle', 'bb_upper', 'bb_lower'])
            ]
            
            if complete_points:
                sample = complete_points[0]
                print(f"\n   Sample point with all indicators (date: {sample['date']}):")
                print(f"      Close:     {sample['close']:.2f}")
                print(f"      SMA:       {sample['sma']:.2f}")
                print(f"      RSI:       {sample['rsi']:.2f}")
                print(f"      BB Middle: {sample['bb_middle']:.2f}")
                print(f"      BB Upper:  {sample['bb_upper']:.2f}")
                print(f"      BB Lower:  {sample['bb_lower']:.2f}")
                print(f"   [OK] All indicators working together")
            else:
                print(f"   [WARN]  No points with all indicators")
        else:
            print(f"   [FAIL] Status: {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Request error: {e}")
        return False
    
    print("\n=== All integration tests passed! ===")
    return True


if __name__ == "__main__":
    try:
        success = test_bollinger_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
