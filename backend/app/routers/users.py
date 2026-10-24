"""
GESTIÓN DE USUARIOS (solo administrador)
GET/POST /api/users · PUT/DELETE /api/users/{id} · POST /api/users/{id}/reset-password
"""

from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.routers.deps import client_info
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Usuarios"], dependencies=[Depends(require_admin)])


class CreateUserRequest(BaseModel):
    username: str = Field(..., max_length=30)
    nombre: str = Field(..., max_length=150)
    role: str = Field("consultor", max_length=20)


class UpdateUserRequest(CreateUserRequest):
    activo: Optional[bool] = None


@router.get("")
def list_users(db: Session = Depends(get_db)):
    return user_service.get_all_users(db)


@router.post("")
def create_user(body: CreateUserRequest, request: Request, db: Session = Depends(get_db), actor=Depends(require_admin)):
    ip, ua = client_info(request)
    return user_service.create_user(db, body.username, body.nombre, body.role, actor, ip, ua)


@router.put("/{user_id}")
def update_user(user_id: int, body: UpdateUserRequest, request: Request, db: Session = Depends(get_db),
                actor=Depends(require_admin)):
    ip, ua = client_info(request)
    return user_service.update_user(db, user_id, body.username, body.nombre, body.role, body.activo, actor, ip, ua)


@router.post("/{user_id}/reset-password")
def reset_password(user_id: int, request: Request, db: Session = Depends(get_db), actor=Depends(require_admin)):
    ip, ua = client_info(request)
    return user_service.reset_password(db, user_id, actor, ip, ua)


@router.delete("/{user_id}")
def delete_user(user_id: int, request: Request, db: Session = Depends(get_db), actor=Depends(require_admin)):
    ip, ua = client_info(request)
    return user_service.delete_user(db, user_id, actor, ip, ua)
