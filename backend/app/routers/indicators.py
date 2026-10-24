"""
INDICADORES SPADIES (usuarios autenticados)
GET /api/indicators?nivel=pregrado|posgrado|todos&vista=ies|programa&programas=A|B
GET /api/indicators/programs?nivel=...
GET /api/indicators/export?...   (reporte Excel)
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.routers.deps import client_info
from app.services import indicator_service, report_service
from app.services.audit_service import log_audit_event
from app.services.parameter_service import get_parameter_value

router = APIRouter(prefix="/indicators", tags=["Indicadores"], dependencies=[Depends(get_current_user)])


@router.get("")
def get_indicators(nivel: str = Query("pregrado"), vista: str = Query("ies"),
                   programas: Optional[str] = Query(None, max_length=8000), db: Session = Depends(get_db)):
    return indicator_service.compute(db, nivel, vista, indicator_service.parse_programs(programas))


@router.get("/programs")
def programs_with_data(nivel: str = Query("pregrado"), db: Session = Depends(get_db)):
    return indicator_service.available_programs(db, (nivel or "pregrado").lower())


@router.get("/export")
def export_excel(request: Request, nivel: str = Query("pregrado"), vista: str = Query("ies"),
                 programas: Optional[str] = Query(None, max_length=8000), db: Session = Depends(get_db),
                 user=Depends(get_current_user)):
    progs = indicator_service.parse_programs(programas)
    result = indicator_service.compute(db, nivel, vista, progs)
    label = "Todos los programas" if not progs else (progs[0] if len(progs) == 1 else f"{len(progs)} programas seleccionados")
    content = report_service.build_report(result, get_parameter_value(db, "INSTITUTION_NAME", "UCO"),
                                          user.nombre or user.username, label)
    ip, ua = client_info(request)
    log_audit_event(db, "EXPORTAR", "REPORTE", None, user=user, ip_address=ip, user_agent=ua,
                    details=f"Descarga de reporte Excel de indicadores ({result['filtros']['nivel']}, vista {result['filtros']['vista']}, {label}).")
    fname = f"Indicadores_SPADIES_{result['filtros']['nivel']}_{result['filtros']['vista']}_{datetime.now():%Y%m%d_%H%M}.xlsx"
    return Response(content=content,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})
