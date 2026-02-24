"""
Test script for symbol search endpoint.
Requires:
1. Backend server running (uvicorn app.main:app --reload)
2. At least one user registered
3. Some symbols ingested in the database
"""

import requests
import sys

BASE_URL = "http://127.0.0.1:8000"


def test_symbol_search():
    print("=== Testing Symbol Search Endpoint ===\n")
    
    # Step 1: Register a test user
    print("1. Registering test user...")
    register_data = {
        "email": "test_search@example.com",
        "password": "testpass123"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if resp.status_code == 200:
            print("   [OK] User registered")
        elif resp.status_code == 400 and "already registered" in resp.text.lower():
            print("   [INFO]  User already exists")
        else:
            print(f"   [WARN]  Unexpected response: {resp.status_code}")
    except Exception as e:
        print(f"   [FAIL] Registration failed: {e}")
        return False
    
    # Step 2: Login to get token
    print("\n2. Logging in...")
    try:
        login_data = {
            "username": register_data["email"],
            "password": register_data["password"]
        }
        resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if resp.status_code != 200:
            print(f"   [FAIL] Login failed: {resp.status_code} - {resp.text}")
            return False
        
        token = resp.json()["access_token"]
        print("   [OK] Login successful")
    except Exception as e:
        print(f"   [FAIL] Login error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: Ingest a test symbol (AAPL)
    print("\n3. Ingesting AAPL data...")
    try:
        resp = requests.post(
            f"{BASE_URL}/stocks/AAPL/ingest?start=2023-01-01&end=2023-01-10",
            headers=headers
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"   [OK] Ingested: {data['inserted']} new, {data['skipped']} skipped")
        else:
            print(f"   [WARN]  Ingest response: {resp.status_code}")
    except Exception as e:
        print(f"   [WARN]  Ingest error (may be ok if already exists): {e}")
    
    # Step 4: Test symbol search
    print("\n4. Testing symbol search...")
    
    test_queries = ["AA", "A", "AAPL", "XYZ"]
    
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        try:
            resp = requests.get(
                f"{BASE_URL}/stocks/search?q={query}&limit=5",
                headers=headers
            )
            
            if resp.status_code == 200:
                results = resp.json()
                print(f"   [OK] Status: 200, Found {len(results)} results")
                for result in results:
                    name_str = f" - {result['name']}" if result.get('name') else ""
                    print(f"      • {result['ticker']}{name_str}")
            else:
                print(f"   [FAIL] Status: {resp.status_code}")
                print(f"      Response: {resp.text[:200]}")
                return False
                
        except Exception as e:
            print(f"   [FAIL] Search error: {e}")
            return False
    
    print("\n=== All tests passed! ===")
    return True


if __name__ == "__main__":
    try:
        success = test_symbol_search()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        sys.exit(1)
