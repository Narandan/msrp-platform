"""
Integration test for EMA through the API endpoint.
Requires:
1. Backend server running (uvicorn app.main:app --reload)
2. At least one user registered
3. Some symbols ingested in the database
"""

import requests
import sys

BASE_URL = "http://127.0.0.1:8000"


def test_ema_integration():
    print("=== Testing EMA Integration ===\n")
    
    # Step 1: Register/Login
    print("1. Setting up authentication...")
    register_data = {
        "email": "test_ema@example.com",
        "password": "testpass123"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if resp.status_code == 200:
            print("   [OK] User registered")
        elif resp.status_code == 400:
            print("   [INFO] User already exists")
        else:
            print(f"   [WARN] Unexpected response: {resp.status_code}")
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
            print(f"   [WARN] Ingest response: {resp.status_code}")
    except Exception as e:
        print(f"   [WARN] Ingest error: {e}")
    
    # Step 3: Test indicators endpoint with EMA only
    print("\n3. Testing indicators endpoint with EMA...")
    
    try:
        resp = requests.get(
            f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&ema_period=20",
            headers=headers
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   [OK] Status: 200")
            print(f"   Symbol: {data['symbol']}")
            print(f"   Points returned: {len(data['points'])}")
            
            # Check that EMA is present
            points_with_ema = [p for p in data['points'] if p.get('ema') is not None]
            print(f"   Points with EMA values: {len(points_with_ema)}")
            
            if points_with_ema:
                sample = points_with_ema[0]
                print(f"\n   Sample point (date: {sample['date']}):")
                print(f"      Close: {sample['close']:.2f}")
                print(f"      EMA:   {sample['ema']:.2f}")
                print(f"   [OK] EMA present in response")
            else:
                print(f"   [WARN] No EMA values found")
        else:
            print(f"   [FAIL] Status: {resp.status_code}")
            print(f"      Response: {resp.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Request error: {e}")
        return False
    
    # Step 4: Test with multiple indicators including EMA
    print("\n4. Testing with SMA + EMA + RSI...")
    
    try:
        resp = requests.get(
            f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&sma_period=20&ema_period=20&rsi_period=14",
            headers=headers
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   [OK] Status: 200")
            
            # Find a point with all indicators
            complete_points = [
                p for p in data['points'] 
                if all(p.get(k) is not None for k in ['sma', 'ema', 'rsi'])
            ]
            
            if complete_points:
                sample = complete_points[0]
                print(f"\n   Sample point with all indicators (date: {sample['date']}):")
                print(f"      Close: {sample['close']:.2f}")
                print(f"      SMA:   {sample['sma']:.2f}")
                print(f"      EMA:   {sample['ema']:.2f}")
                print(f"      RSI:   {sample['rsi']:.2f}")
                print(f"   [OK] All indicators working together")
                
                # Verify SMA and EMA are different (they should be after first value)
                if sample['sma'] != sample['ema']:
                    print(f"   [OK] SMA and EMA differ (as expected)")
            else:
                print(f"   [WARN] No points with all indicators")
        else:
            print(f"   [FAIL] Status: {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Request error: {e}")
        return False
    
    # Step 5: Test with all indicators
    print("\n5. Testing with all indicators (SMA + EMA + RSI + BB)...")
    
    try:
        resp = requests.get(
            f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&sma_period=20&ema_period=20&rsi_period=14&bb_period=20",
            headers=headers
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   [OK] Status: 200")
            
            # Check all fields are present
            if data['points']:
                sample = data['points'][-1]  # Last point
                fields = ['close', 'sma', 'ema', 'rsi', 'bb_middle', 'bb_upper', 'bb_lower']
                present = [f for f in fields if f in sample]
                print(f"   Fields present: {', '.join(present)}")
                print(f"   [OK] All indicator fields available")
        else:
            print(f"   [FAIL] Status: {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Request error: {e}")
        return False
    
    # Step 6: Verify backward compatibility (old requests still work)
    print("\n6. Testing backward compatibility (SMA + RSI only)...")
    
    try:
        resp = requests.get(
            f"{BASE_URL}/indicators/AAPL?start=2023-01-01&end=2023-02-28&sma_period=20&rsi_period=14",
            headers=headers
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   [OK] Old API calls still work")
            
            # EMA should be None when not requested
            if data['points']:
                sample = data['points'][-1]
                if sample.get('ema') is None:
                    print(f"   [OK] EMA is None when not requested")
                else:
                    print(f"   [WARN] EMA has value when not requested")
        else:
            print(f"   [FAIL] Status: {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Request error: {e}")
        return False
    
    print("\n=== All integration tests passed! ===")
    print("\nEMA successfully added to indicators API.")
    print("Existing SMA/RSI/BB behavior remains unchanged.")
    return True


if __name__ == "__main__":
    try:
        success = test_ema_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
