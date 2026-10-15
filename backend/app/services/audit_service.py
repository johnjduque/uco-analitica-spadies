"""
SERVICIO DE AUDITORÍA Y TRAZABILIDAD (AUDIT TRAIL)
Universidad Católica de Oriente - Sistema Analítico de Deserción

Permite registrar todas las operaciones críticas de negocio (crear, editar, eliminar,
cargas de archivos, cambios de contraseña y logins) garantizando trazabilidad completa.
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import AuditLog

logger = logging.getLogger("uco_analytics.audit")

def log_audit_event(
    db: Session,
    action: str,
    entity: str,
    entity_id: Optional[str] = None,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    user_name: Optional[str] = None,
    user_role: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Any] = None
) -> AuditLog:
    """
    Registra un evento de auditoría de forma atómica en la tabla audit_logs.
    """
    details_str = None
    if details is not None:
        if isinstance(details, (dict, list)):
            try:
                details_str = json.dumps(details, ensure_ascii=False)
            except Exception:
                details_str = str(details)
        else:
            details_str = str(details)

    try:
        log_entry = AuditLog(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            username=username,
            user_name=user_name,
            user_role=user_role,
            action=action.upper(),
            entity=entity.upper(),
            entity_id=str(entity_id) if entity_id is not None else None,
            ip_address=ip_address,
            user_agent=user_agent[:250] if user_agent else None,
            details=details_str
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    except Exception as e:
        db.rollback()
        logger.error(f"Error al registrar auditoría [{action} on {entity}]: {str(e)}")
        return None

def get_audit_logs(
    db: Session,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    action_filter: Optional[str] = None,
    entity_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Consulta paginada del historial de auditoría con filtros.
    """
    query = db.query(AuditLog)

    if action_filter and action_filter.upper() != "TODOS":
        query = query.filter(AuditLog.action == action_filter.upper())

    if entity_filter and entity_filter.upper() != "TODOS":
        query = query.filter(AuditLog.entity == entity_filter.upper())

    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.filter(
            (AuditLog.username.ilike(term)) |
            (AuditLog.user_name.ilike(term)) |
            (AuditLog.details.ilike(term)) |
            (AuditLog.entity_id.ilike(term))
        )

    total = query.count()
    offset = (page - 1) * limit
    logs = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 1,
        "items": [
            {
                "id": l.id,
                "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S") if l.timestamp else "",
                "user_id": l.user_id,
                "username": l.username or "Sistema",
                "user_name": l.user_name or l.username or "Sistema",
                "user_role": l.user_role or "N/A",
                "action": l.action,
                "entity": l.entity,
                "entity_id": l.entity_id,
                "ip_address": l.ip_address or "127.0.0.1",
                "user_agent": l.user_agent or "",
                "details": l.details
            }
            for l in logs
        ]
    }
