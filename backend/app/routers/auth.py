"""
AUTENTICACIÓN
POST /api/auth/login            (público, con límite de intentos)
POST /api/auth/change-password  (usuario autenticado, incluso con clave temporal)
GET  /api/auth/me               (usuario autenticado)
"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_allow_pending
from app.routers.deps import client_info
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=200)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1, max_length=200)
    new_password: str = Field(..., min_length=1, max_length=200)


@router.post("/login")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip, ua = client_info(request)
    return auth_service.authenticate_user(db, body.username, body.password, ip, ua)


@router.post("/change-password")
def change_password(body: ChangePasswordRequest, request: Request, db: Session = Depends(get_db),
                    user=Depends(get_current_user_allow_pending)):
    ip, ua = client_info(request)
    return auth_service.change_password(db, user, body.old_password, body.new_password, ip, ua)


@router.get("/me")
def me(user=Depends(get_current_user_allow_pending)):
    return {"id": user.id, "username": user.username, "nombre": user.nombre or user.username,
            "role": user.role, "must_change_password": bool(user.must_change_password)}
