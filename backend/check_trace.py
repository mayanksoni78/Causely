import json
from src.core.database import SessionLocal
from src.models.domain import Incident, InvestigationTrace

db = SessionLocal()
incident = db.query(Incident).order_by(Incident.created_at.desc()).first()
traces = db.query(InvestigationTrace).filter(InvestigationTrace.incident_id == incident.id).order_by(InvestigationTrace.timestamp.asc()).all()

for trace in traces:
    if trace.step == "hypothesis_generation":
        print("Hypotheses generated:")
        print(json.dumps(trace.details, indent=2))
    elif trace.step == "confidence_scoring":
        print("Confidence Scoring:")
        print(json.dumps(trace.details, indent=2))
