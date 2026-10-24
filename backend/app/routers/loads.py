"""
CARGA DE ARCHIVOS (solo administrador)
GET /api/loads · GET /api/loads/status · POST /api/loads · DELETE /api/loads/{id}
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.messages import AppException
from app.core.security import require_admin
from app.routers.deps import client_info
from app.services import ingestion_service
from app.services.parameter_service import get_parameter_value

router = APIRouter(prefix="/loads", tags=["Cargas de datos"], dependencies=[Depends(require_admin)])
_ALLOWED_EXT = (".xls", ".xlsx", ".xlsm", ".csv")


@router.get("")
def list_loads(db: Session = Depends(get_db)):
    return ingestion_service.list_loads(db)


@router.get("/status")
def load_status(db: Session = Depends(get_db)):
    return ingestion_service.load_status(db)


@router.post("")
async def upload(
    request: Request,
    file: UploadFile = File(...),
    tipo: str = Form(...),
    periodo: str = Form(...),
    reemplazar: bool = Form(False),
    decisiones_programas: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    actor=Depends(require_admin),
):
    filename = (file.filename or "archivo").replace("\\", "/").split("/")[-1]
    if not filename.lower().endswith(_ALLOWED_EXT):
        raise AppException("DATA_003")
    max_mb = get_parameter_value(db, "MAX_FILE_UPLOAD_MB", 30)
    limit = max_mb * 1024 * 1024
    chunks, size = [], 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        size += len(chunk)
        if size > limit:
            raise AppException("DATA_009", custom_user_message=f"El archivo supera el máximo permitido de {max_mb} MB.")
        chunks.append(chunk)
    decisions = None
    if decisiones_programas:
        try:
            decisions = json.loads(decisiones_programas)
            if not isinstance(decisions, list):
                raise ValueError
        except ValueError:
            raise AppException("VAL_001", custom_user_message="Formato de decisiones de programas no válido.")
    ip, ua = client_info(request)
    return ingestion_service.process_upload(db, b"".join(chunks), filename, tipo, periodo, reemplazar,
                                            decisions, actor, ip, ua)


@router.delete("/{load_id}")
def delete_load(load_id: int, request: Request, db: Session = Depends(get_db), actor=Depends(require_admin)):
    ip, ua = client_info(request)
    return ingestion_service.delete_load(db, load_id, actor, ip, ua)
