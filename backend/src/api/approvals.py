import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.auth import get_current_user
from src.models.user import User as DBUser
from src.models.domain import Approval, Incident

router = APIRouter(prefix="/approvals", tags=["approvals"])

class ApprovalCreate(BaseModel):
    incident_id: str
    action_type: str
    action_payload: dict

@router.post("")
async def create_approval(
    payload: ApprovalCreate,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    # Verify incident belongs to user
    incident = db.query(Incident).filter(Incident.id == payload.incident_id, Incident.tenant_id == user.tenant_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    app_id = uuid.uuid4()
    approval = Approval(
        id=app_id,
        tenant_id=user.tenant_id,
        incident_id=payload.incident_id,
        action_type=payload.action_type,
        action_payload=payload.action_payload,
        status="pending"
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    
    return {"id": str(app_id), "status": "pending"}

@router.post("/{id}/approve")
async def approve_action(
    id: str,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    approval = db.query(Approval).filter(Approval.id == id, Approval.tenant_id == user.tenant_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    approval.status = "approved"
    db.commit()
    db.refresh(approval)
    
    return {
        "id": str(approval.id),
        "status": approval.status,
        "action_type": approval.action_type
    }

@router.post("/{id}/execute")
async def execute_action(
    id: str,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    approval = db.query(Approval).filter(Approval.id == id, Approval.tenant_id == user.tenant_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    if approval.status != "approved":
        raise HTTPException(status_code=400, detail="Action not approved yet")
        
    approval.status = "executed"
    db.commit()
    db.refresh(approval)
    
    return {
        "status": "executed",
        "note": "Wired to real DB, but external execution is simulated.",
        "action_type": approval.action_type
    }
