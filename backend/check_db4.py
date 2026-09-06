import json
from src.core.database import SessionLocal
from src.models.domain import Incident, InvestigationTrace

db = SessionLocal()
incident = db.query(Incident).order_by(Incident.created_at.desc()).first()
traces = db.query(InvestigationTrace).filter(InvestigationTrace.incident_id == incident.id).all()
for t in traces:
    if t.step_name in ("hypothesis_generation", "confidence_scoring"):
        print(f"--- {t.step_name} ---")
        snap = t.state_snapshot
        if t.step_name == "hypothesis_generation":
            print(json.dumps(snap.get("hypotheses"), indent=2))
        else:
            print(json.dumps(snap.get("verified_hypotheses"), indent=2))
