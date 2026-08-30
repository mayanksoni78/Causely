import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.core.auth import get_current_user, get_current_project, require_role
from src.models.user import User as DBUser
from src.models.domain import Project, ProjectMember, ProjectInvitation

router = APIRouter(prefix="/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    environment: str = "development"

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    environment: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    slug: str
    description: Optional[str]
    environment: str
    role: str

class ProjectMemberResponse(BaseModel):
    id: str
    user_id: str
    name: str
    email: str
    role: str
    created_at: datetime

class InviteRequest(BaseModel):
    email: str
    role: str

def generate_slug(name: str) -> str:
    return name.lower().replace(" ", "-").replace("[^a-z0-9-]", "")

@router.get("", response_model=List[ProjectResponse])
def get_projects(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.query(ProjectMember).filter(ProjectMember.user_id == user.id).all()
    project_ids = [m.project_id for m in memberships]
    
    projects = db.query(Project).filter(Project.id.in_(project_ids), Project.tenant_id == user.tenant_id).all()
    
    role_map = {m.project_id: m.role for m in memberships}
    
    return [
        ProjectResponse(
            id=str(p.id),
            tenant_id=str(p.tenant_id),
            name=p.name,
            slug=p.slug,
            description=p.description,
            environment=p.environment,
            role=role_map.get(p.id, "MEMBER")
        )
        for p in projects
    ]

@router.post("", response_model=ProjectResponse)
def create_project(req: ProjectCreate, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    slug = generate_slug(req.name)
    
    # Check slug uniqueness within tenant
    if db.query(Project).filter(Project.tenant_id == user.tenant_id, Project.slug == slug).first():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        
    project = Project(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        name=req.name,
        slug=slug,
        description=req.description,
        environment=req.environment,
        created_by=user.id
    )
    db.add(project)
    db.flush()
    
    member = ProjectMember(
        id=uuid.uuid4(),
        project_id=project.id,
        user_id=user.id,
        role="OWNER"
    )
    db.add(member)
    db.commit()
    db.refresh(project)
    
    return ProjectResponse(
        id=str(project.id),
        tenant_id=str(project.tenant_id),
        name=project.name,
        slug=project.slug,
        description=project.description,
        environment=project.environment,
        role="OWNER"
    )

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, project: Project = Depends(get_current_project)):
    if str(project.id) != project_id:
        raise HTTPException(status_code=403, detail="URL project ID does not match header project ID")
        
    return ProjectResponse(
        id=str(project.id),
        tenant_id=str(project.tenant_id),
        name=project.name,
        slug=project.slug,
        description=project.description,
        environment=project.environment,
        role=project.current_user_role
    )

@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str, 
    req: ProjectUpdate, 
    project: Project = Depends(require_role(["OWNER", "ADMIN"])), 
    db: Session = Depends(get_db)
):
    if req.name is not None:
        project.name = req.name
    if req.description is not None:
        project.description = req.description
    if req.environment is not None:
        project.environment = req.environment
        
    db.commit()
    db.refresh(project)
    
    return ProjectResponse(
        id=str(project.id),
        tenant_id=str(project.tenant_id),
        name=project.name,
        slug=project.slug,
        description=project.description,
        environment=project.environment,
        role=project.current_user_role
    )

@router.delete("/{project_id}")
def delete_project(project_id: str, project: Project = Depends(require_role(["OWNER"])), db: Session = Depends(get_db)):
    db.delete(project)
    db.commit()
    return {"status": "deleted"}

@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
def get_project_members(project_id: str, project: Project = Depends(get_current_project), db: Session = Depends(get_db)):
    members = db.query(ProjectMember).filter(ProjectMember.project_id == project.id).all()
    
    res = []
    for m in members:
        user = db.query(DBUser).filter(DBUser.id == m.user_id).first()
        if user:
            res.append(ProjectMemberResponse(
                id=str(m.id),
                user_id=str(m.user_id),
                name=user.name,
                email=user.email,
                role=m.role,
                created_at=m.created_at
            ))
    return res


import hashlib
from datetime import datetime, timedelta

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

@router.post("/{project_id}/members/invite")
def invite_member(
    project_id: str, 
    req: InviteRequest, 
    project: Project = Depends(require_role(["OWNER", "ADMIN"])), 
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if req.role not in ["ADMIN", "MEMBER"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    # Check if already a member
    invited_user = db.query(DBUser).filter(DBUser.email == req.email, DBUser.tenant_id == user.tenant_id).first()
    if invited_user:
        existing = db.query(ProjectMember).filter(ProjectMember.project_id == project.id, ProjectMember.user_id == invited_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="User is already a member of this project")
            
    # Clean up old pending invites for this email + project
    db.query(ProjectInvitation).filter(
        ProjectInvitation.project_id == project.id, 
        ProjectInvitation.invited_email == req.email
    ).delete()
        
    token = uuid.uuid4().hex
    
    invitation = ProjectInvitation(
        id=uuid.uuid4(),
        project_id=project.id,
        tenant_id=project.tenant_id,
        invited_email=req.email,
        role=req.role,
        token_hash=hash_token(token),
        expires_at=datetime.utcnow() + timedelta(days=7),
        invited_by=user.id
    )
    db.add(invitation)
    db.commit()
    
    print(f"==================================================")
    print(f"DEV ONLY INVITATION EMAIL TO: {req.email}")
    print(f"Role: {req.role}")
    print(f"Accept link: http://localhost:5173/invites/{token}")
    print(f"==================================================")
    
    return {"status": "invited", "message": "Invitation sent successfully"}

@router.patch("/{project_id}/members/{member_id}")
def update_member_role(
    project_id: str,
    member_id: str,
    req: InviteRequest, # re-using for role
    project: Project = Depends(require_role(["OWNER"])),
    db: Session = Depends(get_db)
):
    if req.role not in ["OWNER", "ADMIN", "MEMBER"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    member = db.query(ProjectMember).filter(ProjectMember.id == member_id, ProjectMember.project_id == project.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
        
    member.role = req.role
    db.commit()
    return {"status": "updated"}

@router.delete("/{project_id}/members/{member_id}")
def remove_member(
    project_id: str,
    member_id: str,
    project: Project = Depends(require_role(["OWNER", "ADMIN"])),
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member = db.query(ProjectMember).filter(ProjectMember.id == member_id, ProjectMember.project_id == project.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
        
    if str(member.user_id) == str(user.id):
        raise HTTPException(status_code=400, detail="Cannot remove yourself. Transfer ownership first or leave project.")
        
    db.delete(member)
    db.commit()
    return {"status": "removed"}

@router.get("/invitations/{token}")
def get_invitation(token: str, db: Session = Depends(get_db)):
    from src.models.domain import ProjectInvitation, Project
    from src.models.user import User as DBUser
    
    hashed = hash_token(token)
    inv = db.query(ProjectInvitation).filter(ProjectInvitation.token_hash == hashed).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invalid invitation")
        
    if inv.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation expired")
        
    proj = db.query(Project).filter(Project.id == inv.project_id).first()
    inviter = db.query(DBUser).filter(DBUser.id == inv.invited_by).first()
    
    return {
        "project_name": proj.name if proj else "Unknown",
        "role": inv.role,
        "invited_email": inv.invited_email,
        "inviter_name": inviter.name if inviter else "Someone"
    }

@router.post("/invitations/{token}/accept")
def accept_invitation(token: str, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    from src.models.domain import ProjectInvitation, ProjectMember
    
    hashed = hash_token(token)
    inv = db.query(ProjectInvitation).filter(ProjectInvitation.token_hash == hashed).first()
    
    if not inv:
        raise HTTPException(status_code=404, detail="Invalid invitation")
        
    if inv.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation expired")
        
    if inv.invited_email.lower() != user.email.lower():
        raise HTTPException(status_code=400, detail="This invitation was sent to a different email address")
        
    # Create membership
    existing = db.query(ProjectMember).filter(ProjectMember.project_id == inv.project_id, ProjectMember.user_id == user.id).first()
    if not existing:
        member = ProjectMember(
            id=uuid.uuid4(),
            project_id=inv.project_id,
            user_id=user.id,
            role=inv.role
        )
        db.add(member)
    
    # Delete invite
    db.delete(inv)
    db.commit()
    
    return {"status": "accepted", "project_id": str(inv.project_id)}
