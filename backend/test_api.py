import subprocess
import time
import urllib.request
import urllib.error
import json
import sys

def test_endpoints():
    print("Starting uvicorn server...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    time.sleep(5)  # wait for server to start

    try:
        # Test health
        print("Testing /health...")
        req = urllib.request.Request("http://127.0.0.1:8000/health")
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        print("Health Check Response:", data)
        if data.get("status") != "ok":
            print("Health check failed!")
            
        # Test signup
        print("Testing /auth/signup...")
        signup_data = {
            "name": "Test User",
            "email": f"test_{int(time.time())}@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
        signup_req = urllib.request.Request(
            "http://127.0.0.1:8000/auth/signup", 
            data=json.dumps(signup_data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            signup_resp = urllib.request.urlopen(signup_req, timeout=10)
            print("Signup Response Code:", signup_resp.getcode())
            print("Signup Headers:", signup_resp.headers.items())
            signup_resp_data = json.loads(signup_resp.read().decode())
            print("Signup Response Data:", signup_resp_data)
            
            cookie = signup_resp.headers.get("Set-Cookie")
            if not cookie or "causely_access_token=" not in cookie or "HttpOnly" not in cookie:
                print("Missing HttpOnly cookie in signup response!")
            else:
                print("HttpOnly cookie found.")
                
            # Get token to test /auth/me
            token_part = cookie.split(";")[0].split("=")[1]
            me_req = urllib.request.Request(
                "http://127.0.0.1:8000/auth/me",
                headers={"Cookie": cookie.split(";")[0]}
            )
            me_resp = urllib.request.urlopen(me_req, timeout=10)
            me_data = json.loads(me_resp.read().decode())
            print("Me Response Data:", me_data)
            
            # Test logout
            print("Testing /auth/logout...")
            logout_req = urllib.request.Request(
                "http://127.0.0.1:8000/auth/logout",
                data=b"",
                headers={"Cookie": cookie.split(";")[0]}
            )
            logout_resp = urllib.request.urlopen(logout_req, timeout=10)
            print("Logout Response Code:", logout_resp.getcode())
            
        except urllib.error.HTTPError as e:
            print("HTTP Error:", e.code, e.read().decode())
            
    finally:
        print("Stopping uvicorn...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        
        # print uvicorn logs
        stdout, _ = proc.communicate()
        print("\n--- Uvicorn Logs ---")
        print(stdout)

if __name__ == "__main__":
    test_endpoints()
