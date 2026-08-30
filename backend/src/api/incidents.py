import uuid
import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.core.database import get_db, SessionLocal
from src.core.auth import get_current_user, get_current_project
from src.models.user import User as DBUser
from src.models.domain import Incident, InvestigationTrace, Project
from src.pipeline.state import InvestigationState
from src.pipeline.graph import investigation_graph

router = APIRouter(prefix="/incidents", tags=["incidents"])

class IncidentCreate(BaseModel):
    description: str
    title: str = "New Investigation"

def run_investigation_sync(incident_id: str, tenant_id: str, project_id: str, description: str):
    db = SessionLocal()
    try:
        initial_state = {
            "incident_id": incident_id,
            "tenant_id": tenant_id,
            "project_id": project_id,
            "description": description,
            "entities": {},
            "source_plan": {},
            "retrieved_chunks": [],
            "reranked_chunks": [],
            "hypotheses": [],
            "verified_hypotheses": [],
            "confidence": None,
            "final_report": None,
            "trace": [],
            "insufficient_evidence": False
        }
        
        # Run the graph
        try:
            final_state = asyncio.run(investigation_graph.ainvoke(initial_state))
            final_state["status"] = "completed"
        except Exception as e:
            final_state = initial_state
            print(f"Server-side investigation error: {e}"); final_state["final_report"] = {"report": "Investigation failed. Please check the connected sources and try again."}
            final_state["status"] = "failed"
            
        # Update incident in DB
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if incident:
            incident.status = final_state["status"]
            if final_state.get("confidence"):
                incident.confidence_level = final_state["confidence"].get("bucket")
                incident.confidence_score = final_state["confidence"].get("score")
            incident.final_report = final_state["final_report"]
            db.commit()
            
        # Store traces
        if final_state.get("trace"):
            for step in final_state["trace"]:
                trace_entry = InvestigationTrace(
                    incident_id=incident_id,
                    project_id=project_id,
                    step_name=step.get("step", "unknown"),
                    state_snapshot=step
                )
                db.add(trace_entry)
            db.commit()

    except Exception as e:
        print(f"Background task error: {e}")
    finally:
        db.close()

@router.post("")
async def create_incident(
    payload: IncidentCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    from datetime import datetime, timedelta
    
    # 1. Concurrent Investigation Limit
    active_count = db.query(Incident).filter(
        Incident.project_id == project.id,
        Incident.status.in_(["created", "investigating"])
    ).count()
    if active_count >= 2:
        raise HTTPException(status_code=429, detail="Maximum concurrent investigations reached. Please wait for an active investigation to complete.")
        
    # 2. Daily Quota Limit (tenant level for now)
    today = datetime.utcnow().date()
    start_of_day = datetime(today.year, today.month, today.day)
    daily_count = db.query(Incident).filter(
        Incident.tenant_id == project.tenant_id,
        Incident.created_at >= start_of_day
    ).count()
    if daily_count >= 10:
        raise HTTPException(status_code=429, detail="Daily investigation limit (10) reached. Try again later.")

    incident_id = uuid.uuid4()
    
    new_incident = Incident(
        id=incident_id,
        tenant_id=project.tenant_id,
        project_id=project.id,
        title=payload.title,
        description=payload.description,
        status="investigating"
    )
    db.add(new_incident)
    
    from src.models.domain import UsageTracking
    # usage tracking linked to the user who requested it, via project context?
    # the user is not directly injected here because Depends(get_current_project) already validates user
    # but we can get it manually or just skip passing user_id for now, or just retrieve the user.
    # To keep it simple, I'll let UsageTracking user_id be nullable or fetch the owner of the project.
    
    db.commit()
    db.refresh(new_incident)
    
    background_tasks.add_task(run_investigation_sync, str(incident_id), str(project.tenant_id), str(project.id), payload.description)
    return {"id": str(incident_id), "status": "investigating"}

@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    from sqlalchemy import func
    from src.models.domain import Source
    
    total = db.query(Incident).filter(Incident.project_id == project.id).count()
    resolved = db.query(Incident).filter(
        Incident.project_id == project.id, 
        Incident.status.in_(["completed", "failed", "insufficient_evidence"])
    ).count()
    active = total - resolved
    
    completed_with_score = db.query(Incident).filter(
        Incident.project_id == project.id,
        Incident.status == "completed",
        Incident.confidence_score.isnot(None)
    ).all()
    
    avg_conf = 0
    if completed_with_score:
        avg_conf = sum([inc.confidence_score for inc in completed_with_score]) / len(completed_with_score)
        
    sources_count = db.query(Source).filter(Source.project_id == project.id, Source.status == "connected").count()
    
    # Simple logic for text representation of confidence
    avg_conf_level = "None"
    if avg_conf > 0:
        if avg_conf >= 0.85:
            avg_conf_level = "High"
        elif avg_conf >= 0.60:
            avg_conf_level = "Medium"
        else:
            avg_conf_level = "Low"
    
    return {
        "total_incidents": total,
        "completed_investigations": resolved,
        "active": active,
        "avg_confidence": avg_conf,
        "avg_confidence_level": avg_conf_level,
        "sources_connected": sources_count
    }

@router.get("")
async def list_incidents(
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    incidents = db.query(Incident).filter(Incident.project_id == project.id).order_by(Incident.created_at.desc()).all()
    return [
        {
            "id": str(inc.id), 
            "title": inc.title, 
            "status": inc.status, 
            "confidence_level": inc.confidence_level,
            "confidence_score": inc.confidence_score,
            "createdAt": inc.created_at.isoformat() if inc.created_at else None
        } for inc in incidents
    ]

@router.get("/{id}")
async def get_incident(
    id: str, 
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    incident = db.query(Incident).filter(Incident.id == id, Incident.project_id == project.id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    traces = db.query(InvestigationTrace).filter(InvestigationTrace.incident_id == id).order_by(InvestigationTrace.created_at.asc()).all()
    trace_data = [t.state_snapshot for t in traces]

    return {
        "incident_id": str(incident.id),
        "title": incident.title,
        "description": incident.description,
        "status": incident.status,
        "confidence_level": incident.confidence_level,
        "confidence_score": incident.confidence_score,
        "final_report": incident.final_report,
        "trace": trace_data,
        "createdAt": incident.created_at.isoformat() if incident.created_at else None
    }

@router.get("/{id}/trace")
async def get_incident_trace(
    id: str, 
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    incident = db.query(Incident).filter(Incident.id == id, Incident.project_id == project.id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    traces = db.query(InvestigationTrace).filter(InvestigationTrace.incident_id == id).order_by(InvestigationTrace.created_at.asc()).all()
    return [t.state_snapshot for t in traces]

