import requests

BASE_URL = "http://localhost:8000"
session = requests.Session()
try:
    csrf_res = session.get(f"{BASE_URL}/auth/csrf")
    print(csrf_res.json())
    print(session.cookies)
except Exception as e:
    print(e)
