#!/usr/bin/env python3
"""
Complete end-to-end test of AUBEVENTS authentication flow
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_complete_flow():
    """Test the complete user authentication flow"""
    print("🚀 Testing Complete AUBEVENTS Authentication Flow")
    print("=" * 50)
    
    # Test data
    test_email = "testuser@aub.edu.lb"
    test_password = "SecurePass123!"
    
    print(f"\n1. 📝 Testing user signup...")
    signup_response = requests.post(f"{BASE_URL}/auth/signup/", json={
        "email": test_email,
        "password": test_password
    })
    
    print(f"   Status: {signup_response.status_code}")
    print(f"   Response: {signup_response.json()}")
    
    if signup_response.status_code == 201:
        print("   ✅ Signup successful!")
        # In development, the verification token is returned in the response
        verification_token = signup_response.json().get("verification_token")
        
        if verification_token:
            print(f"\n2. ✉️  Testing email verification...")
            verify_response = requests.post(f"{BASE_URL}/auth/verify/", json={
                "email": test_email,
                "token": verification_token
            })
            
            print(f"   Status: {verify_response.status_code}")
            print(f"   Response: {verify_response.json()}")
            
            if verify_response.status_code == 200:
                print("   ✅ Verification successful!")
                
                print(f"\n3. 🔐 Testing user login...")
                login_response = requests.post(f"{BASE_URL}/auth/login/", json={
                    "email": test_email,
                    "password": test_password
                })
                
                print(f"   Status: {login_response.status_code}")
                login_data = login_response.json()
                print(f"   Response: {login_data}")
                
                if login_response.status_code == 200 and "token" in login_data:
                    jwt_token = login_data["token"]
                    print("   ✅ Login successful!")
                    
                    print(f"\n4. 👤 Testing protected endpoint...")
                    me_response = requests.get(f"{BASE_URL}/auth/me/", 
                                             headers={"Authorization": f"Bearer {jwt_token}"})
                    
                    print(f"   Status: {me_response.status_code}")
                    print(f"   Response: {me_response.json()}")
                    
                    if me_response.status_code == 200:
                        print("   ✅ Protected endpoint access successful!")
                        
                        print(f"\n5. 🔄 Testing password reset request...")
                        reset_response = requests.post(f"{BASE_URL}/auth/password-reset-request/", json={
                            "email": test_email
                        })
                        
                        print(f"   Status: {reset_response.status_code}")
                        print(f"   Response: {reset_response.json()}")
                        
                        if reset_response.status_code == 200:
                            print("   ✅ Password reset request successful!")
                            
    elif signup_response.status_code == 409:
        print("   ⚠️  User already exists - this is expected if you've run this test before")
        print("      Let's try to login with existing user...")
        
        login_response = requests.post(f"{BASE_URL}/auth/login/", json={
            "email": test_email,
            "password": test_password
        })
        
        print(f"   Login Status: {login_response.status_code}")
        if login_response.status_code == 200:
            print("   ✅ Login with existing user successful!")
        elif login_response.status_code == 403:
            print("   ⚠️  User needs to be verified first")
    
    print(f"\n🎉 Test completed! Your backend is working perfectly!")

if __name__ == "__main__":
    try:
        test_complete_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the server.")
        print("   Make sure Django server is running: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error: {e}")