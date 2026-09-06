import json
from src.core.database import SessionLocal
from src.models.domain import InvestigationTrace, Incident

db = SessionLocal()
incident = db.query(Incident).order_by(Incident.created_at.desc()).first()
traces = db.query(InvestigationTrace).filter(InvestigationTrace.incident_id == incident.id).order_by(InvestigationTrace.created_at.asc()).all()

for t in traces:
    s = t.state_snapshot
    if not s: continue
    
    # Check if the step_name is correct
    step_name = s.get("step_name", "unknown")
    if step_name == "unknown":
        print(f"Unknown step: {json.dumps(s)[:100]}")
    else:
        print(f"[{step_name}]")
        
    if step_name == "evidence_verification":
        print(f"Verified hypotheses: {s.get('outputs', {}).get('verified_count', 'unknown')}")
    elif step_name == "confidence_scoring":
        print(f"Confidence state: {json.dumps(s.get('outputs', {}), indent=2)}")

hypotheses = db.execute("SELECT state_snapshot FROM investigation_traces WHERE incident_id = :id AND state_snapshot->>'step_name' = 'evidence_verification'", {"id": incident.id}).scalar()
if hypotheses:
    print("\nEvidence verification snapshot:")
    # It seems the state snapshot only saves what we pass to StepTrace outputs, not the entire state.

