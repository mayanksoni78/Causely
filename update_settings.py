import re

with open("backend/src/api/settings.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix GET /settings: remove masking, return has_byok_key, do not return key
get_settings_old = """@router.get("")
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
        "model": settings.llm_model if settings and settings.llm_model else "gemini-3.7-flash",
        "has_byok_key": has_byok,
        "gemini_api_key": masked_key,
        "ollama_base_url": settings.ollama_base_url if settings and settings.ollama_base_url else "http://localhost:11434",
        "ollama_model": settings.ollama_model if settings and settings.ollama_model else "llama3"
    }"""

get_settings_new = """@router.get("")
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
    }"""
content = content.replace(get_settings_old, get_settings_new)

# Fix LLM Test
test_llm_old = """        raise HTTPException(status_code=500, detail="LLM connected but returned empty response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))"""
test_llm_new = """        raise HTTPException(status_code=500, detail="LLM connected but returned empty response")
    except Exception:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("LLM connection test failed")
        raise HTTPException(status_code=502, detail="Unable to connect to the configured LLM provider.")"""
content = content.replace(test_llm_old, test_llm_new)

# Fix UTC Time
usage_old = """    from datetime import datetime
    today = datetime.utcnow().date()
    start_of_day = datetime(today.year, today.month, today.day)"""
usage_new = """    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).date()
    start_of_day = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)"""
content = content.replace(usage_old, usage_new)

# Fix /clear-data authorization
clear_data_old = """async def clear_tenant_data(
    payload: ClearDataRequest,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    if payload.confirmation != "DELETE ALL DATA":
        raise HTTPException(status_code=400, detail="Invalid confirmation string")"""
clear_data_new = """async def clear_tenant_data(
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
        raise HTTPException(status_code=400, detail="Invalid confirmation string")"""
content = content.replace(clear_data_old, clear_data_new)

with open("backend/src/api/settings.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated settings.py")
