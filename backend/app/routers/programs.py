"""
CATÁLOGO DE PROGRAMAS
GET /api/programs (usuarios autenticados) · POST/PUT (solo administrador)
"""

from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.routers.deps import client_info
from app.services import program_service

router = APIRouter(prefix="/programs", tags=["Catálogo de programas"])


class ProgramRequest(BaseModel):
    nombre: str = Field(..., max_length=200)
    nivel: str = Field("pregrado", max_length=20)
    codigo: Optional[str] = Field(None, max_length=20)


class ProgramUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    nivel: Optional[str] = Field(None, max_length=20)
    codigo: Optional[str] = Field(None, max_length=20)
    activo: Optional[bool] = None


@router.get("", dependencies=[Depends(get_current_user)])
def list_programs(db: Session = Depends(get_db)):
    return program_service.list_programs(db)


@router.post("")
def create_program(body: ProgramRequest, request: Request, db: Session = Depends(get_db), actor=Depends(require_admin)):
    ip, ua = client_info(request)
    p = program_service.create_program(db, body.nombre, body.nivel, body.codigo, actor=actor, ip=ip, ua=ua)
    return {"id": p.id, "codigo": p.code, "nombre": p.name, "nivel": p.level, "activo": bool(p.is_active)}


@router.put("/{program_id}")
def update_program(program_id: int, body: ProgramUpdate, request: Request, db: Session = Depends(get_db),
                   actor=Depends(require_admin)):
    ip, ua = client_info(request)
    return program_service.update_program(db, program_id, body.nombre, body.nivel, body.codigo, body.activo, actor, ip, ua)
