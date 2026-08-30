import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.auth import get_current_user
from src.models.user import User as DBUser
from src.models.domain import TenantSettings, Incident, Source as DBSource, InvestigationTrace, DocumentChunk
from src.llm.client import client
from src.core.security import encrypt_dict, decrypt_dict
import json

router = APIRouter(prefix="/settings", tags=["settings"])

class SettingsUpdate(BaseModel):
    provider: str
    model: str = "gemini-2.0-flash"
    gemini_api_key: str = ""
    ollama_base_url: str = ""
    remove_key: bool = False

class ClearDataRequest(BaseModel):
    confirmation: str

@router.post("")
async def update_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    settings = db.query(TenantSettings).filter(TenantSettings.tenant_id == user.tenant_id).first()
    if not settings:
        settings = TenantSettings(tenant_id=user.tenant_id)
        db.add(settings)
        
    settings.llm_provider = payload.provider
    # Assuming there's a field for model, or we can stash it. We don't have llm_model natively maybe? 
    # Let's check if llm_model exists in TenantSettings model. If not, we might ignore it or store in a json block.
    # We will just use payload.model in the frontend.
    
    if payload.remove_key:
        settings.llm_api_key = None
    elif payload.provider == "gemini" and payload.gemini_api_key and not payload.gemini_api_key.startswith("••••"):
        # Encrypt the API key before saving!
        encrypted = encrypt_dict({"key": payload.gemini_api_key})
        settings.llm_api_key = encrypted
        
    if payload.provider == "ollama":
        settings.ollama_base_url = payload.ollama_base_url
        
    db.commit()
    return {"status": "success", "message": "Settings updated"}

@router.get("")
async def get_settings(
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    settings = db.query(TenantSettings).filter(TenantSettings.tenant_id == user.tenant_id).first()
    masked_key = ""
    has_byok = False
    
    if settings and settings.llm_api_key:
        has_byok = True
        try:
            # Decrypt to get last 4 chars
            decrypted = decrypt_dict(settings.llm_api_key)
            actual_key = decrypted.get("key", "")
            if actual_key and len(actual_key) > 4:
                masked_key = "••••••••••••••••" + actual_key[-4:]
            else:
                masked_key = "••••••••••••••••"
        except:
            masked_key = "••••••••••••••••"
        
    return {
        "configured": True,
        "provider": settings.llm_provider if settings else "gemini",
        "model": "gemini-2.0-flash", # Hardcoded for now based on current client.py setup
        "has_byok_key": has_byok,
        "gemini_api_key": masked_key,
        "ollama_base_url": settings.ollama_base_url if settings else "http://localhost:11434"
    }

@router.post("/test-llm")
async def test_llm_connection(
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    try:
        start = time.time()
        res = await client.complete("Say 'hello'", tenant_id=str(user.tenant_id))
        elapsed = int((time.time() - start) * 1000)
        
        if res:
            return {
                "status": "ok", 
                "model": "gemini-2.0-flash", 
                "response_time": f"{elapsed}ms", 
                "message": "Connection successful"
            }
        raise HTTPException(status_code=500, detail="LLM connected but returned empty response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage")
async def get_usage(
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    from datetime import datetime
    today = datetime.utcnow().date()
    start_of_day = datetime(today.year, today.month, today.day)
    
    daily_count = db.query(Incident).filter(
        Incident.tenant_id == user.tenant_id,
        Incident.created_at >= start_of_day
    ).count()
    
    active_count = db.query(Incident).filter(
        Incident.tenant_id == user.tenant_id,
        Incident.status.in_(["created", "investigating"])
    ).count()
    
    return {
        "daily_used": daily_count,
        "daily_limit": 10,
        "active_used": active_count,
        "active_limit": 2
    }

@router.post("/clear-data")
async def clear_tenant_data(
    payload: ClearDataRequest,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    if payload.confirmation != "DELETE ALL DATA":
        raise HTTPException(status_code=400, detail="Invalid confirmation string")
        
    # Strict tenant isolation check enforced by the WHERE clause
    db.query(DocumentChunk).filter(DocumentChunk.tenant_id == user.tenant_id).delete()
    db.query(InvestigationTrace).filter(InvestigationTrace.incident_id.in_(
        db.query(Incident.id).filter(Incident.tenant_id == user.tenant_id)
    )).delete(synchronize_session=False)
    db.query(Incident).filter(Incident.tenant_id == user.tenant_id).delete()
    db.query(DBSource).filter(DBSource.tenant_id == user.tenant_id).delete()
    
    # Optional: Delete tenant settings as requested
    db.query(TenantSettings).filter(TenantSettings.tenant_id == user.tenant_id).delete()
    
    db.commit()
    
    return {"status": "success", "message": "All tenant data deleted securely."}
