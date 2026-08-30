import uuid
import traceback
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.auth import get_current_project
from src.core.security import encrypt_dict, decrypt_dict
from src.models.domain import Project
from src.models.domain import Source as DBSource
from src.models.domain import Incident

from src.connectors.github import GitHubConnector
from src.connectors.static_log import StaticLogConnector
from src.connectors.generic_rest import GenericRESTConnector
from src.connectors.external.razorpay import RazorpayConnector
from src.connectors.postgres import PostgresConnector
from src.connectors.mongodb import MongoDBConnector
from src.connectors.loki import LokiConnector

router = APIRouter(prefix="/sources", tags=["sources"])

class GenericRESTRegister(BaseModel):
    name: str
    base_url: str
    auth_type: str = "none"
    auth_token: str = ""
    endpoints: list[str] = []

class RazorpayRegister(BaseModel):
    name: str
    api_key: str
    api_secret: str

@router.post("/generic-rest")
async def register_generic_rest(
    payload: GenericRESTRegister,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    config = {
        "base_url": payload.base_url,
        "auth_type": payload.auth_type,
        "auth_token": payload.auth_token,
        "endpoints": payload.endpoints
    }
    connector = GenericRESTConnector(str(uuid.uuid4()), str(project.tenant_id), config)
    health = connector.health_check()
    if not health.healthy:
        raise HTTPException(status_code=400, detail=f"Connection failed: {health.message}")

    new_source = DBSource(
        tenant_id=project.tenant_id,
        project_id=project.id,
        type="generic_rest",
        category="external_services",
        name=payload.name,
        config={"encrypted_data": encrypt_dict(config)},
        status="connected",
        capabilities=connector.list_capabilities()
    )
    db.add(new_source)
    db.commit()
    return {"id": str(new_source.id)}

@router.post("/razorpay")
async def register_razorpay(
    payload: RazorpayRegister,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    config = {
        "api_key": payload.api_key,
        "api_secret": payload.api_secret
    }
    connector = RazorpayConnector(str(uuid.uuid4()), str(project.tenant_id), config)
    health = connector.health_check()
    if not health.healthy:
        raise HTTPException(status_code=400, detail=f"Connection failed: {health.message}")

    new_source = DBSource(
        tenant_id=project.tenant_id,
        project_id=project.id,
        type="razorpay",
        provider="razorpay",
        category="external_services",
        name=payload.name,
        config={"encrypted_data": encrypt_dict(config)},
        status="connected",
        capabilities=connector.list_capabilities()
    )
    db.add(new_source)
    db.commit()
    return {"id": str(new_source.id)}

class GithubRegister(BaseModel):
    repo_url: str
    token: str

@router.post("/github")
async def register_github(
    payload: GithubRegister,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    connector = GitHubConnector(payload.repo_url, payload.token)
    perms = connector.check_permissions()
    
    if not perms.granted_scopes:
        raise HTTPException(status_code=400, detail=f"Permission check failed: {perms.warnings}")
        
    config = {"repo_url": payload.repo_url, "token": payload.token}
    new_source = DBSource(
        tenant_id=project.tenant_id,
        project_id=project.id,
        type="github",
        category="code",
        name=payload.repo_url.split("/")[-1],
        config={"encrypted_data": encrypt_dict(config)},
        status="connected"
    )
    db.add(new_source)
    db.commit()
    
    return {"id": str(new_source.id), "permissions": perms.__dict__}

@router.post("/static-log")
async def register_log(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    from src.retrieval.chunker import chunk_text
    from src.retrieval.indexer import indexer
    try:
        content = await file.read()
        text = content.decode("utf-8")
        
        # 1. Create the source first
        config = {"filename": file.filename, "size": len(text)}
        
        new_source = DBSource(
            tenant_id=project.tenant_id,
        project_id=project.id,
            type="static_log",
            category="logs",
            name=file.filename,
            config={"encrypted_data": encrypt_dict(config)},
            status="connected"
        )
        db.add(new_source)
        db.flush() # Get the new_source.id
        
        # 2. Chunk and index
        chunks = chunk_text(text)
        # Add metadata to chunks
        for c in chunks:
            c["metadata"] = {"file_path": file.filename}
            c["layer_level"] = 2
            
        count = indexer.index_chunks(db, str(project.tenant_id), str(project.id), str(new_source.id), "static_log", chunks)
        
        # Update capabilities/metadata
        new_source.capabilities = ["log_search", f"indexed_chunks:{count}"]
        db.commit()
        return {"id": str(new_source.id), "indexed": count}
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

class DbRegister(BaseModel):
    connection_string: str

class LokiRegister(BaseModel):
    url: str

@router.post("/postgres")
async def register_postgres(
    payload: DbRegister,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    connector = PostgresConnector(payload.connection_string)
    perms = connector.check_permissions()
    
    if not perms.is_read_only:
        raise HTTPException(status_code=400, detail=f"Permission check failed: PostgreSQL connection must be read-only. {perms.warnings}")
        
    config = {"connection_string": payload.connection_string}
    new_source = DBSource(
        tenant_id=project.tenant_id,
        project_id=project.id,
        type="postgres",
        category="databases",
        name="PostgreSQL DB",
        config={"encrypted_data": encrypt_dict(config)},
        status="connected"
    )
    db.add(new_source)
    db.commit()
    return {"id": str(new_source.id)}

@router.post("/mongodb")
async def register_mongodb(
    payload: DbRegister,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    connector = MongoDBConnector(payload.connection_string)
    perms = connector.check_permissions()
    if not perms.is_read_only:
        raise HTTPException(status_code=400, detail=f"Permission check failed: {perms.warnings}")

    config = {"connection_string": payload.connection_string}
    new_source = DBSource(
        tenant_id=project.tenant_id,
        project_id=project.id,
        type="mongodb",
        category="databases",
        name="MongoDB",
        config={"encrypted_data": encrypt_dict(config)},
        status="connected"
    )
    db.add(new_source)
    db.commit()
    return {"id": str(new_source.id)}

@router.post("/loki")
async def register_loki(
    payload: LokiRegister,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    connector = LokiConnector(payload.url)
    health = connector.health_check()
    if not health.healthy:
         raise HTTPException(status_code=400, detail=f"Loki connection failed: {health.message}")

    config = {"url": payload.url}
    new_source = DBSource(
        tenant_id=project.tenant_id,
        project_id=project.id,
        type="loki",
        category="logs",
        name="Grafana Loki",
        config={"encrypted_data": encrypt_dict(config)},
        status="connected"
    )
    db.add(new_source)
    db.commit()
    return {"id": str(new_source.id)}

@router.get("")
async def list_sources(
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    sources = db.query(DBSource).filter(DBSource.project_id == project.id).all()
    result = []
    for s in sources:
        safe_config = {}
        if s.config and "encrypted_data" in s.config:
            try:
                dec = decrypt_dict(s.config["encrypted_data"])
                if s.type in ("github", "github_actions"):
                    safe_config["repo_url"] = dec.get("repo_url")
                elif s.type == "static_log":
                    safe_config["filename"] = dec.get("filename")
                    safe_config["size"] = dec.get("size")
            except:
                pass
                
        result.append({
            "id": str(s.id),
            "type": s.type,
            "category": s.category,
            "provider": s.provider,
            "name": s.name,
            "status": s.status,
            "capabilities": s.capabilities,
            "config": safe_config
        })
    return result

@router.delete("/{source_id}")
async def disconnect_source(
    source_id: str,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    source = db.query(DBSource).filter(DBSource.id == source_id, DBSource.project_id == project.id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    db.delete(source)
    db.commit()
    return {"status": "success"}

@router.post("/{source_id}/test")
async def test_source_connection(
    source_id: str,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    source = db.query(DBSource).filter(DBSource.id == source_id, DBSource.project_id == project.id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    from src.pipeline.nodes import _get_connector
    connector = _get_connector(source)
    
    if connector is None:
        if source.type == "static_log":
            return {"healthy": True, "message": "Static log is indexed"}
        return {"healthy": False, "message": "Unknown connector type"}
        
    if hasattr(connector, "health_check"):
        status = connector.health_check()
        return {"healthy": status.healthy, "message": status.message}
    elif hasattr(connector, "check_permissions"):
        perms = connector.check_permissions()
        if source.type == "github" and perms.granted_scopes:
            return {"healthy": True, "message": "GitHub connection successful"}
        elif source.type == "postgres" and perms.is_read_only:
             return {"healthy": True, "message": "Postgres connection successful"}
        elif source.type == "mongodb" and perms.is_read_only:
             return {"healthy": True, "message": "MongoDB connection successful"}
        return {"healthy": False, "message": str(perms.warnings)}
    
    return {"healthy": True, "message": "Connected"}

@router.get("/readiness")
async def get_readiness(
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    sources = db.query(DBSource).filter(DBSource.project_id == project.id, DBSource.status == "connected").all()
    cats = [s.category for s in sources]
    
    has_code = "code" in cats
    has_logs = "logs" in cats
    has_db = "databases" in cats
    has_external = "external_services" in cats
    
    history_count = db.query(Incident).filter(Incident.project_id == project.id).count()
    has_history = history_count > 0
    
    score = 0
    if has_code: score += 25
    if has_logs: score += 25
    if has_db: score += 20
    if has_external: score += 20
    if has_history: score += 10
    
    return {
        "score": score,
        "code": has_code,
        "logs": has_logs,
        "database": has_db,
        "external_services": has_external,
        "history": has_history
    }
class StripeRegister(BaseModel):
    api_key: str

class Auth0Register(BaseModel):
    domain: str
    client_id: str
    client_secret: str

class GithubActionsRegister(BaseModel):
    repo_url: str
    token: str

@router.post("/stripe")
async def register_stripe(
    payload: StripeRegister,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    from src.connectors.stripe import StripeConnector
    config = {"api_key": payload.api_key}
    connector = StripeConnector(str(uuid.uuid4()), str(project.tenant_id), config)
    health = connector.health_check()
    if not health.healthy:
        raise HTTPException(status_code=400, detail=f"Connection failed: {health.message}")

    new_source = DBSource(
        tenant_id=project.tenant_id,
        project_id=project.id,
        type="stripe",
        category="external_services",
        name="Stripe",
        config={"encrypted_data": encrypt_dict(config)},
        status="connected",
        capabilities=connector.list_capabilities()
    )
    db.add(new_source)
    db.commit()
    return {"id": str(new_source.id)}

@router.post("/auth0")
async def register_auth0(
    payload: Auth0Register,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    from src.connectors.auth0 import Auth0Connector
    config = {"domain": payload.domain, "client_id": payload.client_id, "client_secret": payload.client_secret}
    connector = Auth0Connector(str(uuid.uuid4()), str(project.tenant_id), config)
    health = connector.health_check()
    if not health.healthy:
        raise HTTPException(status_code=400, detail=f"Connection failed: {health.message}")

    new_source = DBSource(
        tenant_id=project.tenant_id,
        project_id=project.id,
        type="auth0",
        category="external_services",
        name="Auth0",
        config={"encrypted_data": encrypt_dict(config)},
        status="connected",
        capabilities=connector.list_capabilities()
    )
    db.add(new_source)
    db.commit()
    return {"id": str(new_source.id)}

@router.post("/github-actions")
async def register_github_actions(
    payload: GithubActionsRegister,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project)
):
    from src.connectors.github_actions import GitHubActionsConnector
    config = {"repo_url": payload.repo_url, "token": payload.token}
    connector = GitHubActionsConnector(str(uuid.uuid4()), str(project.tenant_id), config)
    health = connector.health_check()
    if not health.healthy:
        raise HTTPException(status_code=400, detail=f"Connection failed: {health.message}")

    new_source = DBSource(
        tenant_id=project.tenant_id,
        project_id=project.id,
        type="github_actions",
        category="code",
        name="GitHub Actions",
        config={"encrypted_data": encrypt_dict(config)},
        status="connected",
        capabilities=connector.list_capabilities()
    )
    db.add(new_source)
    db.commit()
    return {"id": str(new_source.id)}
