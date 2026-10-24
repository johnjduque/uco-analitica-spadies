"""AUDITORÍA (solo administrador): GET /api/audit-logs"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.services import audit_service

router = APIRouter(prefix="/audit-logs", tags=["Auditoría"], dependencies=[Depends(require_admin)])


@router.get("")
def list_audit_logs(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200),
                    search: Optional[str] = Query(None, max_length=100), action: Optional[str] = Query(None, max_length=50),
                    entity: Optional[str] = Query(None, max_length=50), db: Session = Depends(get_db)):
    return audit_service.get_audit_logs(db, page, limit, search, action, entity)
