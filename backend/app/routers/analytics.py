"""
ENRUTADOR DE ANALÍTICA Y SEGUIMIENTO ESTUDIANTIL
Endpoints: /api/admin/metrics/{indicator},
/api/admin/student-status/{cedula}, /api/admin/student-status-summary
"""

from typing import Optional
from fastapi import APIRouter, Query

from app.services import analytics_service

router = APIRouter(prefix="/admin", tags=["Analítica"])

@router.get("/metrics/{indicator}")
def get_spadies_metrics_endpoint(indicator: str, programs: Optional[str] = None):
    return analytics_service.get_metrics_for_indicator(indicator, programs)

@router.get("/student-status/{cedula}")
def get_student_spadies_status_endpoint(cedula: str):
    return analytics_service.get_student_status_by_cedula(cedula)

@router.get("/student-status-summary")
def get_student_status_summary_endpoint(
    status_filter: str = Query("Todos", alias="status_filter"),
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    return analytics_service.get_student_status_summary(
        status_filter=status_filter,
        search=search,
        page=page,
        limit=limit
    )
