import os
import secrets
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.api.incidents import router as incidents_router
from src.api.sources import router as sources_router
from src.api.approvals import router as approvals_router
from src.api.auth import router as auth_router
from src.api.settings import router as settings_router
from src.api.projects import router as projects_router
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing backend...")
    # Base.metadata.create_all(bind=engine)  # Disabled: using Alembic now
    print("Database ready.")
    yield
    print("Shutting down...")

app = FastAPI(title="Causely", lifespan=lifespan)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSRF_EXEMPT_PATHS = ["/auth/login", "/auth/signup", "/health"]

@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    # Set new CSRF token if one doesn't exist
    csrf_cookie = request.cookies.get("csrf_token")
    
    # Check CSRF on mutating requests
    if request.method in ["POST", "PUT", "PATCH", "DELETE"] and request.url.path not in CSRF_EXEMPT_PATHS:
        csrf_header = request.headers.get("x-csrf-token")
        if not csrf_header or not csrf_cookie or csrf_header != csrf_cookie:
            return JSONResponse(
                status_code=403, 
                content={"detail": "CSRF token missing or invalid"}
            )
            
    response = await call_next(request)
    
    if not csrf_cookie:
        is_prod = os.getenv("ENVIRONMENT", "local") == "production"
        response.set_cookie(
            key="csrf_token",
            value=secrets.token_urlsafe(32),
            httponly=False, # JS needs to read this
            secure=is_prod,
            samesite="lax",
            path="/"
        )
        
    return response

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(incidents_router)
app.include_router(sources_router)
app.include_router(approvals_router)
app.include_router(settings_router)

@app.get("/health")
def health_check():
    from src.core.database import SessionLocal
    from sqlalchemy import text
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "degraded", "database": "unavailable"}
