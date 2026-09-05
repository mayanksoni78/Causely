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

SUPPORTED_GEMINI_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite"
]
SUPPORTED_OLLAMA_MODELS = ["llama3", "llama3.2", "mistral", "phi3"]

class SettingsUpdate(BaseModel):
    provider: str
    model: str = "gemini-3.7-flash"
    gemini_api_key: str = ""
    ollama_base_url: str = ""
    ollama_model: str = "llama3"
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
    
    if payload.provider == "gemini":
        if payload.model not in SUPPORTED_GEMINI_MODELS:
            raise HTTPException(status_code=400, detail=f"Unsupported Gemini model: {payload.model}")
        settings.llm_model = payload.model
    elif payload.provider == "ollama":
        if payload.ollama_model not in SUPPORTED_OLLAMA_MODELS:
            raise HTTPException(status_code=400, detail=f"Unsupported Ollama model: {payload.ollama_model}")
        settings.ollama_model = payload.ollama_model
        settings.ollama_base_url = payload.ollama_base_url
        
    if payload.remove_key:
        settings.llm_api_key = None
    elif payload.provider == "gemini" and payload.gemini_api_key and not payload.gemini_api_key.startswith("••••"):
        encrypted = encrypt_dict({"key": payload.gemini_api_key})
        settings.llm_api_key = encrypted
        
    db.commit()
    return {"status": "success", "message": "Settings updated"}

@router.get("")
async def get_settings(
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    settings = db.query(TenantSettings).filter(TenantSettings.tenant_id == user.tenant_id).first()
    has_byok = False
    if settings and settings.llm_api_key:
        has_byok = True
        
    return {
        "configured": True,
        "provider": settings.llm_provider if settings else "gemini",
        "model": settings.llm_model if settings and settings.llm_model else "gemini-3.7-flash",
        "has_byok_key": has_byok,
        "supported_gemini_models": SUPPORTED_GEMINI_MODELS,
        "supported_ollama_models": SUPPORTED_OLLAMA_MODELS,
        "ollama_base_url": settings.ollama_base_url if settings and settings.ollama_base_url else "http://localhost:11434",
        "ollama_model": settings.ollama_model if settings and settings.ollama_model else "llama3"
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
            settings = db.query(TenantSettings).filter(TenantSettings.tenant_id == user.tenant_id).first()
            provider = settings.llm_provider if settings else "gemini"
            if provider == "gemini":
                model_used = settings.llm_model if settings and settings.llm_model else "gemini-3.7-flash"
            else:
                model_used = settings.ollama_model if settings and settings.ollama_model else "llama3"
                
            return {
                "status": "ok", 
                "model": model_used, 
                "response_time": f"{elapsed}ms", 
                "message": "Connection successful"
            }
        raise HTTPException(status_code=500, detail="LLM connected but returned empty response")
    except Exception:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("LLM connection test failed")
        raise HTTPException(status_code=502, detail="Unable to connect to the configured LLM provider.")

@router.get("/usage")
async def get_usage(
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    
    daily_count = db.query(Incident).filter(
        Incident.tenant_id == user.tenant_id,
        Incident.created_at >= start_of_day
    ).count()
    
    active_count = db.query(Incident).filter(
        Incident.tenant_id == user.tenant_id,
        Incident.status.in_(["queued", "investigating"])
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
    from src.models.domain import ProjectMember
    has_admin = db.query(ProjectMember).filter(
        ProjectMember.user_id == user.id,
        ProjectMember.role.in_(["OWNER", "ADMIN"])
    ).first()
    if not has_admin:
        raise HTTPException(status_code=403, detail="Must be an OWNER or ADMIN to clear tenant data")

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
