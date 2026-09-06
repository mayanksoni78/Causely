import json
from datetime import datetime

from src.core.database import SessionLocal
from src.models.domain import Incident, InvestigationTrace

db = SessionLocal()
incident = db.query(Incident).order_by(Incident.created_at.desc()).first()
traces = db.query(InvestigationTrace).filter(InvestigationTrace.incident_id == incident.id).all()

print("\n--- STAGE TIMINGS ---")
for t in traces:
    snap = t.state_snapshot
    if not snap: continue
    for st in snap.get("trace", []):
        try:
            start = datetime.fromisoformat(st["started_at"])
            end = datetime.fromisoformat(st["ended_at"])
            dur = (end - start).total_seconds()
            print(f"{st['step_name']:<25} {dur:.2f}s")
        except Exception as e:
            pass
    break
