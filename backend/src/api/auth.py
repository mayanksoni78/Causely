import os
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
import bcrypt

from src.core.database import get_db
from src.core.auth import create_access_token, get_current_user
from src.models.user import User as DBUser, Tenant

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

class AuthResponse(BaseModel):
    user_id: str
    tenant_id: str
    email: str
    name: str

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=4)
    pwd_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)

def set_auth_cookie(response: Response, token: str):
    is_prod = os.getenv("ENVIRONMENT", "local") == "production"
    response.set_cookie(
        key="causely_access_token",
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        path="/",
        max_age=3600 * 24 * 7
    )

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(req: SignupRequest, response: Response, db: Session = Depends(get_db)):
    email = req.email.lower().strip()

    if req.password != req.confirm_password:
        raise HTTPException(status_code=422, detail="Passwords do not match")

    if len(req.password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters")
        
    if not req.name.strip():
        raise HTTPException(status_code=422, detail="Name is required")

    if db.query(DBUser).filter(DBUser.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    try:
        new_tenant = Tenant(name=f"{req.name}'s Workspace")
        db.add(new_tenant)
        db.flush()

        new_user = DBUser(
            tenant_id=new_tenant.id,
            email=email,
            password_hash=hash_password(req.password),
            name=req.name.strip()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        # Log actual error to backend console
        print(f"Signup Database Error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed due to a server error")

    token = create_access_token(str(new_user.id), str(new_tenant.id), new_user.email)
    set_auth_cookie(response, token)

    return AuthResponse(
        user_id=str(new_user.id),
        tenant_id=str(new_tenant.id),
        email=new_user.email,
        name=new_user.name
    )

@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    email = req.email.lower().strip()
    user = db.query(DBUser).filter(DBUser.email == email).first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(str(user.id), str(user.tenant_id), user.email)
    set_auth_cookie(response, token)

    return AuthResponse(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        email=user.email,
        name=user.name
    )

@router.get("/me", response_model=AuthResponse)
def get_me(user: DBUser = Depends(get_current_user)):
    return AuthResponse(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        email=user.email,
        name=user.name
    )

@router.post("/logout")
def logout(response: Response):
    response.set_cookie(
        key="causely_access_token",
        value="",
        httponly=True,
        secure=os.getenv("ENVIRONMENT", "local") == "production",
        samesite="lax",
        path="/",
        expires=0,
        max_age=0
    )
    return {"message": "Logged out successfully"}
