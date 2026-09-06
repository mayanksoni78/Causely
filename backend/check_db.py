import json
from src.core.database import SessionLocal
from src.models.domain import Incident

db = SessionLocal()
incidents = db.query(Incident).order_by(Incident.created_at.desc()).limit(2).all()

for i, inc in enumerate(incidents):
    print(f"--- Incident {i}: {inc.title} ---")
    print("Final Report:", inc.final_report)
    print("Confidence:", inc.confidence_score)
