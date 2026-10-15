"""
ENRUTADOR DE GESTIÓN DE USUARIOS
Endpoints: /api/admin/users (GET, POST, PUT, DELETE), /api/crear-usuario
"""

from typing import Optional
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_payload
from app.services import user_service

router = APIRouter(prefix="/admin/users", tags=["Usuarios"])
bootstrap_router = APIRouter(tags=["Bootstrap Usuarios"])

class CreateUserRequest(BaseModel):
    cedula: str
    nombre: str = ""
    role: str = "consultor"

class UpdateUserRequest(BaseModel):
    username: str
    nombre: str = ""
    password: Optional[str] = None
    role: str = "consultor"

class BootstrapUserRequest(BaseModel):
    username: str
    password: str

@router.get("")
def list_users(db: Session = Depends(get_db)):
    return user_service.get_all_users(db)

@router.post("")
def create_user(
    request: CreateUserRequest, 
    req: Request, 
    db: Session = Depends(get_db),
    user_payload: Optional[dict] = Depends(get_current_user_payload)
):
    ip = req.client.host if req.client else "127.0.0.1"
    user_agent = req.headers.get("user-agent", "")
    actor_username = user_payload.get("username", "Administrador") if user_payload else "Administrador"
    actor_role = user_payload.get("role", "administrador") if user_payload else "administrador"

    return user_service.create_user(
        db=db,
        cedula=request.cedula,
        nombre=request.nombre,
        role=request.role,
        actor_username=actor_username,
        actor_role=actor_role,
        ip_address=ip,
        user_agent=user_agent
    )

@router.put("/{user_id}")
def update_user(
    user_id: int, 
    request: UpdateUserRequest, 
    req: Request, 
    db: Session = Depends(get_db),
    user_payload: Optional[dict] = Depends(get_current_user_payload)
):
    ip = req.client.host if req.client else "127.0.0.1"
    user_agent = req.headers.get("user-agent", "")
    actor_username = user_payload.get("username", "Administrador") if user_payload else "Administrador"
    actor_role = user_payload.get("role", "administrador") if user_payload else "administrador"

    return user_service.update_user(
        db=db,
        user_id=user_id,
        username=request.username,
        nombre=request.nombre,
        role=request.role,
        password=request.password,
        actor_username=actor_username,
        actor_role=actor_role,
        ip_address=ip,
        user_agent=user_agent
    )

@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    req: Request, 
    db: Session = Depends(get_db),
    user_payload: Optional[dict] = Depends(get_current_user_payload)
):
    ip = req.client.host if req.client else "127.0.0.1"
    user_agent = req.headers.get("user-agent", "")
    actor_username = user_payload.get("username", "Administrador") if user_payload else "Administrador"
    actor_role = user_payload.get("role", "administrador") if user_payload else "administrador"

    return user_service.delete_user(
        db=db,
        user_id=user_id,
        actor_username=actor_username,
        actor_role=actor_role,
        ip_address=ip,
        user_agent=user_agent
    )

@bootstrap_router.post("/crear-usuario")
def create_initial_user(request: BootstrapUserRequest, req: Request, db: Session = Depends(get_db)):
    ip = req.client.host if req.client else "127.0.0.1"
    user_agent = req.headers.get("user-agent", "")
    return user_service.create_user(
        db=db,
        cedula=request.username,
        nombre="Administrador Inicial",
        role="administrador",
        actor_username="Sistema Bootstrap",
        actor_role="administrador",
        ip_address=ip,
        user_agent=user_agent
    )
