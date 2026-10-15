"""
ENRUTADOR DE AUTENTICACIÓN Y SEGURIDAD
Endpoints: /api/login, /api/change-password, /api/status, /api/auth/me
"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_authenticated_user
from app.services import auth_service

router = APIRouter(tags=["Autenticación"])

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str

@router.get("/status")
def get_status():
    return {"status": "success", "message": "API UCO Analytics operativa."}

@router.post("/login")
def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    ip = req.client.host if req.client else "127.0.0.1"
    user_agent = req.headers.get("user-agent", "")
    return auth_service.authenticate_user(
        db=db,
        username=request.username,
        password=request.password,
        ip_address=ip,
        user_agent=user_agent
    )

@router.post("/change-password")
def change_password(request: ChangePasswordRequest, req: Request, db: Session = Depends(get_db)):
    ip = req.client.host if req.client else "127.0.0.1"
    user_agent = req.headers.get("user-agent", "")
    return auth_service.change_password(
        db=db,
        username=request.username,
        old_password=request.old_password,
        new_password=request.new_password,
        ip_address=ip,
        user_agent=user_agent
    )

@router.get("/auth/me")
def get_current_user_profile(user_payload: dict = Depends(require_authenticated_user)):
    return {
        "success": True,
        "user": user_payload
    }
