import json
import time
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def run():
    res = client.post("/auth/login", json={"email": "test@gmail.com", "password": "123456"})
    res = client.get("/projects")
    project_id = res.json()[0]["id"]
    headers = {"X-Project-ID": project_id, "x-csrf-token": client.cookies.get("csrf_token", "dummy")}
    
    print("Starting incident investigation (Test 1)...")
    t0 = time.time()
    incident_payload = {
        "title": "Database connection failed on startup",
        "description": "The server failed to connect to the database during startup. Authentication failed."
    }
    res = client.post("/incidents", json=incident_payload, headers=headers)
    
    if res.status_code != 200:
        print(f"Failed to create incident: {res.status_code} {res.text}")
        return
        
    incident_id = res.json()["id"]
    
    while True:
        res = client.get(f"/incidents/{incident_id}", headers=headers)
        if res.json().get("status") != "investigating": 
            break
        time.sleep(1)
        
    t1 = time.time()
    data = res.json()
    print(f"Total time: {t1-t0:.2f}s")
    print(f"Confidence Level: {data.get('confidence_level')}")
    print(f"Confidence Score: {data.get('confidence_score')}")
    
    # Print traces for debugging
    from src.core.database import SessionLocal
    from src.models.domain import InvestigationTrace
    db = SessionLocal()
    traces = db.query(InvestigationTrace).filter(InvestigationTrace.incident_id == incident_id).order_by(InvestigationTrace.created_at.asc()).all()
    
    for t in traces:
        s = t.state_snapshot
        print(f"\n[{t.step_name}]")
        if t.step_name == "retrieval":
            print(f"Chunks retrieved: {s.get('outputs', {}).get('chunk_count', 'unknown')}")
        elif t.step_name == "reranking":
            print(f"Chunks reranked: {s.get('outputs', {}).get('output_count', 'unknown')}")
        elif t.step_name == "hypothesis_generation":
            print(f"Hypotheses generated: {s.get('outputs', {}).get('count', 'unknown')}")
        elif t.step_name == "evidence_verification":
            print(f"Verified hypotheses: {s.get('outputs', {}).get('verified_count', 'unknown')}")
        elif t.step_name == "confidence_scoring":
            print(f"Confidence state: {json.dumps(s.get('outputs', {}), indent=2)}")

if __name__ == "__main__":
    run()
