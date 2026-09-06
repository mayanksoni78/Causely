import json
import time
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def run():
    # Login
    res = client.post("/auth/login", json={"email": "test@gmail.com", "password": "123456"})
    
    # Get project
    res = client.get("/projects")
    project_id = res.json()[0]["id"]
    headers = {"X-Project-ID": project_id, "x-csrf-token": client.cookies.get("csrf_token", "dummy")}
    
    print("Starting incident investigation...")
    t0 = time.time()
    incident_payload = {
        "title": "Database connection failed on startup",
        "description": "The server failed to connect to the database during startup. Authentication failed."
    }
    res = client.post("/incidents", json=incident_payload, headers=headers)
    incident_id = res.json()["id"]
    
    print("Waiting for investigation...")
    while True:
        res = client.get(f"/incidents/{incident_id}", headers=headers)
        status = res.json().get("status")
        if status != "investigating": 
            break
        time.sleep(2)
        
    t1 = time.time()
    print(f"Total time via API: {t1-t0:.2f}s")
    
    # Fetch traces from DB to see breakdown
    from src.core.database import SessionLocal
    from src.models.domain import InvestigationTrace
    from dateutil import parser
    
    db = SessionLocal()
    traces = db.query(InvestigationTrace).filter(InvestigationTrace.incident_id == incident_id).all()
    
    print("\n--- STAGE TIMINGS ---")
    for t in traces:
        snap = t.state_snapshot
        if not snap: continue
        # The trace is in state_snapshot["trace"]
        for st in snap.get("trace", []):
            start = parser.parse(st["started_at"])
            end = parser.parse(st["ended_at"])
            dur = (end - start).total_seconds()
            print(f"{st['step_name']:<25} {dur:.2f}s")
        break

if __name__ == "__main__":
    run()
