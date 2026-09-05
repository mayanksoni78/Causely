import requests

BASE_URL = "http://localhost:8000"
session = requests.Session()

print("1. Testing Signup...")
signup_data = {
    "name": "Test User",
    "email": "testuser@example.com",
    "password": "password123",
    "confirm_password": "password123"
}
try:
    res = session.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print("Signup Status:", res.status_code)
    print("Signup Body:", res.json())
except Exception as e:
    print("Signup Request Error:", e)

print("\n2. Testing /auth/me...")
try:
    res = session.get(f"{BASE_URL}/auth/me")
    print("Me Status:", res.status_code)
    print("Me Body:", res.json())
except Exception as e:
    print("Me Request Error:", e)

print("\n3. Testing Logout...")
try:
    res = session.post(f"{BASE_URL}/auth/logout")
    print("Logout Status:", res.status_code)
    print("Logout Body:", res.json())
except Exception as e:
    print("Logout Request Error:", e)

print("\n4. Testing Login...")
login_data = {
    "email": "testuser@example.com",
    "password": "password123"
}
try:
    res = session.post(f"{BASE_URL}/auth/login", json=login_data)
    print("Login Status:", res.status_code)
    print("Login Body:", res.json())
except Exception as e:
    print("Login Request Error:", e)
