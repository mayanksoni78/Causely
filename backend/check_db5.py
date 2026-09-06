import json
from src.core.database import SessionLocal
from src.models.domain import Incident, InvestigationTrace

db = SessionLocal()
incident = db.query(Incident).order_by(Incident.created_at.desc()).first()
traces = db.query(InvestigationTrace).filter(InvestigationTrace.incident_id == incident.id).all()
print([t.step_name for t in traces])
