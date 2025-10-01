#!/usr/bin/env python3
"""
Test script to verify all backend endpoints are working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data if data else {})
        
        print(f"{method} {endpoint}: Status {response.status_code}")
        if response.status_code < 500:  # Don't print server errors content
            try:
                print(f"  Response: {response.json()}")
            except:
                print(f"  Response: {response.text[:100]}...")
        return response.status_code
    except requests.exceptions.ConnectionError:
        print(f"{method} {endpoint}: Connection Error - Server not running?")
        return None
    except Exception as e:
        print(f"{method} {endpoint}: Error - {e}")
        return None

def main():
    print("Testing AUBEVENTS Backend Endpoints")
    print("=" * 40)
    
    # Test basic connectivity
    print("\n1. Testing basic connectivity:")
    test_endpoint("GET", "/")
    test_endpoint("GET", "/auth/")
    
    # Test authentication endpoints
    print("\n2. Testing authentication endpoints:")
    test_endpoint("POST", "/auth/signup/")
    test_endpoint("POST", "/auth/verify/")
    test_endpoint("POST", "/auth/login/")
    test_endpoint("POST", "/auth/password-reset-request/")
    test_endpoint("POST", "/auth/password-reset-confirm/")
    test_endpoint("GET", "/auth/me/")
    
    print("\n3. Testing with sample data:")
    # Test signup with sample data
    signup_data = {
        "email": "test@aub.edu.lb",
        "password": "TestPass123!"
    }
    test_endpoint("POST", "/auth/signup/", signup_data)

if __name__ == "__main__":
    main()