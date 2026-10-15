"""
ENRUTADOR DE CARGUE DE INFORMACIÓN Y PROGRAMAS
Endpoints: /api/admin/loads, /api/admin/next-expected-period,
/api/admin/upload-period, /api/admin/confirm-new-program, /api/admin/programs
"""

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_payload
from app.services import load_service
from app.program_codes import add_new_program, get_all_official_programs

router = APIRouter(prefix="/admin", tags=["Cargas e Ingesta"])

class NewProgramRequest(BaseModel):
    program_name: str
    full_name: Optional[str] = None

@router.get("/loads")
def get_loads(db: Session = Depends(get_db)):
    return load_service.get_all_loads(db)

@router.get("/next-expected-period")
def get_next_period_info(tipo: str = "matriculados", db: Session = Depends(get_db)):
    next_p = load_service.get_next_expected_period(db, tipo)
    return {"tipo": tipo, "next_period": next_p}

@router.post("/upload-period")
async def upload_period(
    req: Request,
    file: UploadFile = File(...),
    tipo: str = Form(...),
    periodo: str = Form(...),
    confirm_new_program: bool = Form(False),
    db: Session = Depends(get_db),
    user_payload: Optional[dict] = Depends(get_current_user_payload)
):
    contents = await file.read()
    ip = req.client.host if req.client else "127.0.0.1"
    user_agent = req.headers.get("user-agent", "")
    actor_username = user_payload.get("username", "Administrador") if user_payload else "Administrador"
    actor_role = user_payload.get("role", "administrador") if user_payload else "administrador"

    return load_service.process_file_upload(
        db=db,
        file_bytes=contents,
        filename=file.filename,
        tipo=tipo,
        periodo=periodo,
        confirm_new_program=confirm_new_program,
        actor_username=actor_username,
        actor_role=actor_role,
        ip_address=ip,
        user_agent=user_agent
    )

@router.delete("/loads/{load_id}")
def delete_load(
    load_id: int, 
    req: Request, 
    db: Session = Depends(get_db),
    user_payload: Optional[dict] = Depends(get_current_user_payload)
):
    ip = req.client.host if req.client else "127.0.0.1"
    user_agent = req.headers.get("user-agent", "")
    actor_username = user_payload.get("username", "Administrador") if user_payload else "Administrador"
    actor_role = user_payload.get("role", "administrador") if user_payload else "administrador"

    return load_service.delete_load_record(
        db=db,
        load_id=load_id,
        actor_username=actor_username,
        actor_role=actor_role,
        ip_address=ip,
        user_agent=user_agent
    )

@router.post("/confirm-new-program")
def confirm_new_program_endpoint(req: NewProgramRequest):
    registered_name = add_new_program(req.program_name, req.full_name)
    return {
        "status": "success",
        "message": f"El programa '{registered_name}' ha sido agregado exitosamente al directorio oficial de la UCO.",
        "registered_name": registered_name
    }

@router.get("/programs")
def get_programs():
    return get_all_official_programs()
