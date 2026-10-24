"""
SERVICIO DE AUDITORÍA (AUDIT TRAIL)

Registra las operaciones críticas: inicios de sesión, gestión de usuarios,
cargas y eliminaciones de datos, cambios de parámetros y de catálogo.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from app.models import AuditLog

logger = logging.getLogger("uco_analytics.audit")


def iso_utc(dt: Optional[datetime]) -> Optional[str]:
    """Fecha UTC en ISO-8601 con sufijo Z (el navegador la muestra en hora local)."""
    return dt.replace(microsecond=0).isoformat() + "Z" if dt else None


def log_audit_event(
    db: Session,
    action: str,
    entity: str,
    entity_id: Optional[Any] = None,
    user=None,
    username: Optional[str] = None,
    user_name: Optional[str] = None,
    user_role: Optional[str] = None,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Any] = None,
) -> Optional[AuditLog]:
    if user is not None:
        user_id = user_id or user.id
        username = username or user.username
        user_name = user_name or (user.nombre or user.username)
        user_role = user_role or user.role
    if isinstance(details, (dict, list)):
        details = json.dumps(details, ensure_ascii=False, default=str)
    try:
        entry = AuditLog(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            username=username,
            user_name=user_name,
            user_role=user_role,
            action=action.upper(),
            entity=entity.upper(),
            entity_id=str(entity_id) if entity_id is not None else None,
            ip_address=(ip_address or "")[:50] or None,
            user_agent=(user_agent or "")[:250] or None,
            details=details,
        )
        db.add(entry)
        db.commit()
        return entry
    except Exception as exc:
        db.rollback()
        logger.error("Error registrando auditoría [%s %s]: %s", action, entity, exc)
        return None


def get_audit_logs(db: Session, page: int = 1, limit: int = 50, search: Optional[str] = None,
                   action_filter: Optional[str] = None, entity_filter: Optional[str] = None) -> Dict[str, Any]:
    stmt = select(AuditLog)
    if action_filter and action_filter.upper() != "TODOS":
        stmt = stmt.where(AuditLog.action == action_filter.upper())
    if entity_filter and entity_filter.upper() != "TODOS":
        stmt = stmt.where(AuditLog.entity == entity_filter.upper())
    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(or_(AuditLog.username.ilike(term), AuditLog.user_name.ilike(term),
                              AuditLog.details.ilike(term), AuditLog.entity_id.ilike(term)))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    logs = db.scalars(stmt.order_by(desc(AuditLog.timestamp), desc(AuditLog.id))
                      .offset((page - 1) * limit).limit(limit)).all()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": max(1, (total + limit - 1) // limit),
        "items": [
            {
                "id": l.id,
                "timestamp": iso_utc(l.timestamp),
                "username": l.username or "Sistema",
                "user_name": l.user_name or l.username or "Sistema",
                "user_role": l.user_role or "N/A",
                "action": l.action,
                "entity": l.entity,
                "entity_id": l.entity_id,
                "ip_address": l.ip_address or "",
                "details": l.details,
            }
            for l in logs
        ],
    }
