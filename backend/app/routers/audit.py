"""
ENRUTADOR DE AUDITORÍA Y TRAZABILIDAD (AUDIT TRAIL)
Endpoints: /api/admin/audit-logs
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import audit_service

router = APIRouter(prefix="/admin/audit-logs", tags=["Auditoría"])

@router.get("")
def list_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    action: Optional[str] = None,
    entity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return audit_service.get_audit_logs(
        db=db,
        page=page,
        limit=limit,
        search=search,
        action_filter=action,
        entity_filter=entity
    )
