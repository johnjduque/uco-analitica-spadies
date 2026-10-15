"""
ENRUTADOR DE CATÁLOGO DE PARÁMETROS DEL SISTEMA
Endpoints: /api/admin/parameters (GET, PUT)
"""

from typing import Optional
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_payload
from app.services import parameter_service

router = APIRouter(prefix="/admin/parameters", tags=["Parámetros del Sistema"])

class UpdateParameterRequest(BaseModel):
    value: str

@router.get("")
def list_parameters(db: Session = Depends(get_db)):
    return parameter_service.get_all_parameters(db)

@router.put("/{key}")
def update_parameter(
    key: str,
    req_body: UpdateParameterRequest,
    req: Request,
    db: Session = Depends(get_db),
    user_payload: Optional[dict] = Depends(get_current_user_payload)
):
    ip = req.client.host if req.client else "127.0.0.1"
    user_agent = req.headers.get("user-agent", "")
    actor_username = user_payload.get("username", "Administrador") if user_payload else "Administrador"

    return parameter_service.update_parameter(
        db=db,
        key=key,
        new_value=req_body.value,
        current_user_name=actor_username,
        ip_address=ip,
        user_agent=user_agent
    )
