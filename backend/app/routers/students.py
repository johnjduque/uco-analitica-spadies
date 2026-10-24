"""
CONSULTA DE ESTUDIANTES (usuarios autenticados)
GET /api/students/summary · GET /api/students/{documento}
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.routers.deps import client_info
from app.services import indicator_service, student_service
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/students", tags=["Estudiantes"], dependencies=[Depends(get_current_user)])


@router.get("/summary")
def summary(nivel: str = Query("pregrado"), estado: str = Query("Todos", max_length=20),
            buscar: Optional[str] = Query(None, max_length=100), programas: Optional[str] = Query(None, max_length=8000),
            page: int = Query(1, ge=1), limit: int = Query(25, ge=1, le=200), db: Session = Depends(get_db)):
    return student_service.summary(db, nivel, estado, buscar, indicator_service.parse_programs(programas), page, limit)


@router.get("/{document}")
def detail(document: str, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    data = student_service.detail(db, document)
    ip, ua = client_info(request)
    log_audit_event(db, "CONSULTA", "ESTUDIANTE", data["documento"], user=user, ip_address=ip, user_agent=ua,
                    details="Consulta de trayectoria individual.")
    return data
