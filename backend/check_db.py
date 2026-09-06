from src.core.database import SessionLocal
from src.models.domain import Incident
db = SessionLocal()
incident = db.query(Incident).order_by(Incident.created_at.desc()).first()
print(f"Status: {incident.status}")
print(f"Confidence: {incident.confidence_score}")
print(f"Report: {incident.final_report}")
