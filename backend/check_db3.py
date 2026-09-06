import json
from src.core.database import SessionLocal
from src.models.domain import Incident, InvestigationTrace

db = SessionLocal()
incident = db.query(Incident).order_by(Incident.created_at.desc()).first()
trace = db.query(InvestigationTrace).filter(InvestigationTrace.incident_id == incident.id).first()
print([c.name for c in trace.__table__.columns])
for t in db.query(InvestigationTrace).filter(InvestigationTrace.incident_id == incident.id).all():
    print(t.step, t.details)
