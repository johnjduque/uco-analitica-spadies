"""
SERVICIO DE PARÁMETROS DEL SISTEMA

Parámetros configurables desde la aplicación. Todos los que aparecen aquí son
usados efectivamente por el sistema (no hay parámetros decorativos). Las reglas
metodológicas de SPADIES no son parametrizables para garantizar que las cifras
sean comparables con las oficiales.
"""

import logging
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.messages import AppException
from app.models import SystemParameter
from app.services.audit_service import iso_utc, log_audit_event

logger = logging.getLogger("uco_analytics.parameters")

DEFAULT_PARAMETERS = [
    {"key": "MAX_FILE_UPLOAD_MB", "value": "30", "default_value": "30", "category": "SISTEMA", "data_type": "INTEGER",
     "description": "Tamaño máximo (MB) permitido para cada archivo Excel o CSV cargado.", "min": 1, "max": 200},
    {"key": "SESSION_EXPIRATION_MINUTES", "value": "60", "default_value": "60", "category": "SEGURIDAD", "data_type": "INTEGER",
     "description": "Minutos de vigencia de la sesión (token) antes de pedir nuevamente el inicio de sesión.", "min": 5, "max": 720},
    {"key": "PASSWORD_MIN_LENGTH", "value": "8", "default_value": "8", "category": "SEGURIDAD", "data_type": "INTEGER",
     "description": "Longitud mínima de las contraseñas (deben combinar letras y números).", "min": 8, "max": 64},
    {"key": "LOGIN_MAX_ATTEMPTS", "value": "5", "default_value": "5", "category": "SEGURIDAD", "data_type": "INTEGER",
     "description": "Intentos fallidos de inicio de sesión permitidos antes del bloqueo temporal.", "min": 3, "max": 20},
    {"key": "LOGIN_LOCKOUT_MINUTES", "value": "15", "default_value": "15", "category": "SEGURIDAD", "data_type": "INTEGER",
     "description": "Minutos de bloqueo temporal tras superar los intentos fallidos.", "min": 1, "max": 1440},
    {"key": "INSTITUTION_NAME", "value": "Universidad Católica de Oriente (UCO)",
     "default_value": "Universidad Católica de Oriente (UCO)", "category": "GENERAL", "data_type": "STRING",
     "description": "Nombre institucional para encabezados de reportes."},
]
_BOUNDS = {p["key"]: (p.get("min"), p.get("max")) for p in DEFAULT_PARAMETERS}
_OBSOLETE = ("SPADIES_CONSECUTIVE_ABSENCE_TERMS", "ACTIVE_ACADEMIC_YEAR", "DEFAULT_PERIOD_START")


def seed_default_parameters(db: Session) -> None:
    existing = {p.key: p for p in db.scalars(select(SystemParameter)).all()}
    for key in _OBSOLETE:
        if key in existing:
            db.delete(existing[key])
    for param in DEFAULT_PARAMETERS:
        data = {k: v for k, v in param.items() if k not in ("min", "max")}
        current = existing.get(param["key"])
        if current is None:
            db.add(SystemParameter(is_editable=True, **data))
        else:
            current.description = data["description"]
            current.default_value = data["default_value"]
            current.category = data["category"]
            lo, hi = param.get("min"), param.get("max")
            if lo is not None:
                try:
                    v = int(current.value)
                    if v < lo or v > hi:
                        current.value = data["default_value"]
                except ValueError:
                    current.value = data["default_value"]
    db.commit()


def get_all_parameters(db: Session) -> List[Dict[str, Any]]:
    params = db.scalars(select(SystemParameter).order_by(SystemParameter.category, SystemParameter.key)).all()
    return [
        {
            "key": p.key, "value": p.value, "default_value": p.default_value, "description": p.description,
            "category": p.category, "data_type": p.data_type, "is_editable": bool(p.is_editable),
            "min": _BOUNDS.get(p.key, (None, None))[0], "max": _BOUNDS.get(p.key, (None, None))[1],
            "updated_at": iso_utc(p.updated_at), "updated_by": p.updated_by or "Sistema",
        }
        for p in params
    ]


def get_parameter_value(db: Session, key: str, fallback: Any = None) -> Any:
    param = db.scalar(select(SystemParameter).where(SystemParameter.key == key))
    if not param:
        return fallback
    try:
        if param.data_type.upper() == "INTEGER":
            return int(param.value)
        if param.data_type.upper() == "FLOAT":
            return float(param.value)
        if param.data_type.upper() == "BOOLEAN":
            return param.value.lower() in ("true", "1", "si", "yes")
        return str(param.value)
    except Exception:
        return fallback


def update_parameter(db: Session, key: str, new_value: str, actor, ip=None, ua=None) -> Dict[str, Any]:
    param = db.scalar(select(SystemParameter).where(SystemParameter.key == key))
    if not param:
        raise AppException("PARAM_001")
    if not param.is_editable:
        raise AppException("AUTH_003", custom_user_message="Este parámetro es estructural y no puede modificarse.")
    val = str(new_value).strip()
    if param.data_type.upper() == "INTEGER":
        try:
            num = int(val)
        except ValueError:
            raise AppException("PARAM_002")
        lo, hi = _BOUNDS.get(key, (None, None))
        if (lo is not None and num < lo) or (hi is not None and num > hi):
            raise AppException("PARAM_002", custom_user_message=f"El valor debe estar entre {lo} y {hi}.")
        val = str(num)
    elif not val or len(val) > 255:
        raise AppException("PARAM_002", custom_user_message="El valor no puede estar vacío ni superar 255 caracteres.")
    old = param.value
    param.value = val
    param.updated_by = actor.username
    db.commit()
    log_audit_event(db, "EDITAR", "PARAMETRO", param.key, user=actor, ip_address=ip, user_agent=ua,
                    details=f"Parámetro '{param.key}': valor anterior '{old}', nuevo valor '{val}'.")
    return {"key": param.key, "value": param.value}
