import json
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.main import app
from src.core.database import SessionLocal
from src.models.user import User

client = TestClient(app)

def run_test():
    print("1. Creating/Verifying user test@gmail.com...")
    db = SessionLocal()
    user = db.query(User).filter(User.email == "test@gmail.com").first()
    if not user:
        print("User not found, attempting signup...")
        res = client.post("/auth/signup", json={
            "name": "Test User",
            "email": "test@gmail.com",
            "password": "123456",
            "confirm_password": "123456"
        })
        print("Signup result:", res.status_code)
    db.close()
    
    print("\n2. Logging in...")
    res = client.post("/auth/login", json={"email": "test@gmail.com", "password": "123456"})
    print("Login:", res.status_code, res.json())
    if res.status_code != 200:
        return
        
    print("\n3. Getting projects...")
    res = client.get("/projects")
    print("Projects:", res.status_code, res.json())
    if not res.json():
        print("No projects found for user!")
        return
    project_id = res.json()[0]["id"]
    print("Using project_id:", project_id)
    
    headers = {"X-Project-ID": project_id}
    csrf_token = client.cookies.get("csrf_token", "dummy")
    headers["x-csrf-token"] = csrf_token
    
    print("\n4. Connecting GitHub Source...")
    github_payload = {
        "repo_url": "https://github.com/mayanksoni78/Car_Rental",
        "token": "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"
    }
    res = client.post("/sources/github", json=github_payload, headers=headers)
    print("GitHub Connect:", res.status_code, res.json())
    
    print("\n5. Connecting Log Source...")
    log_content = """{"level":"info","message":"server.started","port":"2005","timestamp":"2026-09-05T12:52:26.549Z"}
{"level":"info","message":"database.connected","timestamp":"2026-09-05T12:52:27.594Z"}
{"level":"info","message":"server.started","port":"2005","timestamp":"2026-09-05T12:52:31.470Z"}
{"level":"info","message":"database.connected","timestamp":"2026-09-05T12:52:32.103Z"}
{"level":"info","message":"server.started","port":"2005","timestamp":"2026-09-05T12:53:40.971Z"}
{"level":"info","message":"database.connected","timestamp":"2026-09-05T12:53:41.373Z"}
{"level":"info","message":"server.started","port":"2005","timestamp":"2026-09-05T12:54:44.018Z"}
{"level":"info","message":"database.connected","timestamp":"2026-09-05T12:54:44.990Z"}
{"level":"info","message":"server.started","port":"2005","timestamp":"2026-09-05T12:56:07.980Z"}
{"level":"info","message":"database.connected","timestamp":"2026-09-05T12:56:09.141Z"}
{"level":"info","message":"server.started","port":"2005","timestamp":"2026-09-05T13:04:49.761Z"}
{"level":"info","message":"database.connected","timestamp":"2026-09-05T13:04:50.461Z"}
{"durationMs":16,"level":"info","message":"http.request","method":"GET","route":"/","status":200,"timestamp":"2026-09-05T14:56:54.324Z"}
{"level":"info","message":"server.started","port":"2005","timestamp":"2026-09-05T14:59:22.091Z"}
{"level":"info","message":"database.connected","timestamp":"2026-09-05T14:59:23.207Z"}
{"level":"info","message":"server.started","port":"2005","timestamp":"2026-09-05T15:01:02.976Z"}
{"level":"info","message":"database.connected","timestamp":"2026-09-05T15:01:04.140Z"}
{"level":"info","message":"server.started","port":"2005","timestamp":"2026-09-05T15:01:42.182Z"}
{"level":"info","message":"database.connected","timestamp":"2026-09-05T15:01:42.738Z"}"""
    
    files = {'file': ('server.log', log_content.encode('utf-8'), 'text/plain')}
    res = client.post("/sources/static-log", files=files, headers=headers)
    print("Static Log Connect:", res.status_code, res.json())
    
    print("\n6. Creating Incident...")
    incident_payload = {
        "title": "mongo is connected or not",
        "description": "mongo is connected or not with github repo and log file"
    }
    res = client.post("/incidents", json=incident_payload, headers=headers)
    print("Create Incident:", res.status_code, res.json())
    if res.status_code != 200:
        return
        
    incident_id = res.json()["id"]
    
    print("\n7. Waiting for incident investigation to complete...")
    for _ in range(30):
        res = client.get(f"/incidents/{incident_id}", headers={"X-Project-ID": project_id})
        data = res.json()
        status = data.get("status")
        print(f"Status: {status}")
        if status != "investigating":
            break
        time.sleep(2)
        
    print("\n8. Final Report:")
    res = client.get(f"/incidents/{incident_id}", headers={"X-Project-ID": project_id})
    data = res.json()
    print(json.dumps(data.get("final_report", {}), indent=2))
    print("Confidence:", data.get("confidence_score"))

if __name__ == "__main__":
    run_test()
