"""PARÁMETROS DEL SISTEMA (solo administrador): GET /api/parameters · PUT /api/parameters/{key}"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.routers.deps import client_info
from app.services import parameter_service

router = APIRouter(prefix="/parameters", tags=["Parámetros"], dependencies=[Depends(require_admin)])


class UpdateParameterRequest(BaseModel):
    value: str = Field(..., max_length=255)


@router.get("")
def list_parameters(db: Session = Depends(get_db)):
    return parameter_service.get_all_parameters(db)


@router.put("/{key}")
def update_parameter(key: str, body: UpdateParameterRequest, request: Request, db: Session = Depends(get_db),
                     actor=Depends(require_admin)):
    ip, ua = client_info(request)
    return parameter_service.update_parameter(db, key, body.value, actor, ip, ua)
