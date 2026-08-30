import os
import jwt
import time
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.user import User as DBUser
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-default-key-for-dev")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def create_access_token(user_id: str, tenant_id: str, email: str) -> str:
    """Helper to generate a JWT token."""
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "email": email,
        "exp": time.time() + 3600 * 24 * 7 # 7 days expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> DBUser:
    """
    Dependency that decodes the JWT token from the HttpOnly cookie and fetches the user from the database.
    """
    token = request.cookies.get("causely_access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_aud": False})
        
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
            
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
            
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

from src.models.domain import Project, ProjectMember

def get_current_project(
    request: Request,
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    project_id = request.headers.get("X-Project-ID")
    if not project_id:
        raise HTTPException(status_code=400, detail="X-Project-ID header is missing")

    project = db.query(Project).filter(Project.id == project_id, Project.tenant_id == user.tenant_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project.id,
        ProjectMember.user_id == user.id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Attach the membership role to the project object temporarily for convenience downstream
    project.current_user_role = membership.role
    return project

def require_role(roles: list[str]):
    def role_checker(project: Project = Depends(get_current_project)):
        if getattr(project, "current_user_role", None) not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return project
    return role_checker
