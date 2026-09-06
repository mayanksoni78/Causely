import json
import time
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def run_test():
    # Login
    res = client.post("/auth/login", json={"email": "test@gmail.com", "password": "123456"})
    if res.status_code != 200: return
    
    # Get project
    res = client.get("/projects")
    project_id = res.json()[0]["id"]
    headers = {"X-Project-ID": project_id, "x-csrf-token": client.cookies.get("csrf_token", "dummy")}
    
    # Read the actual log file with the error
    with open(r"C:\Car_Rental\server\logs\app.log", "r") as f:
        log_content = f.read()
        
    print("Uploading log...")
    files = {'file': ('app.log', log_content.encode('utf-8'), 'text/plain')}
    client.post("/sources/static-log", files=files, headers=headers)
    
    print("Starting incident investigation...")
    incident_payload = {
        "title": "Database connection failed on startup",
        "description": "The server failed to connect to the database during startup."
    }
    res = client.post("/incidents", json=incident_payload, headers=headers)
    incident_id = res.json()["id"]
    
    print("Waiting for investigation...")
    for _ in range(40):
        res = client.get(f"/incidents/{incident_id}", headers={"X-Project-ID": project_id})
        status = res.json().get("status")
        if status != "investigating": break
        time.sleep(2)
        
    res = client.get(f"/incidents/{incident_id}", headers={"X-Project-ID": project_id})
    print("\n--- FINAL REPORT ---")
    print(json.dumps(res.json().get("final_report", {}), indent=2))

if __name__ == "__main__":
    run_test()
