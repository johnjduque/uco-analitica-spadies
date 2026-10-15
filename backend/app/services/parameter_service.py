"""
SERVICIO DE CATÁLOGO DE PARÁMETROS DEL SISTEMA
Universidad Católica de Oriente - Sistema Analítico de Deserción

Permite gestionar variables de configuración dinámicas (criterios SPADIES,
límites de archivos, seguridad de sesiones) sin necesidad de modificar el código fuente.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import SystemParameter
from app.core.messages import AppException
from app.services.audit_service import log_audit_event

logger = logging.getLogger("uco_analytics.parameters")

DEFAULT_PARAMETERS = [
    {
        "key": "SPADIES_CONSECUTIVE_ABSENCE_TERMS",
        "value": "2",
        "default_value": "2",
        "description": "Número de periodos consecutivos de ausencia académica para tipificar a un estudiante como Desertor.",
        "category": "SPADIES",
        "data_type": "INTEGER",
        "is_editable": True
    },
    {
        "key": "MAX_FILE_UPLOAD_MB",
        "value": "50",
        "default_value": "50",
        "description": "Límite máximo permitido en Megabytes (MB) para carga de archivos Excel o CSV.",
        "category": "SISTEMA",
        "data_type": "INTEGER",
        "is_editable": True
    },
    {
        "key": "SESSION_EXPIRATION_MINUTES",
        "value": "60",
        "default_value": "60",
        "description": "Tiempo de inactividad de sesión en minutos antes del cierre automático del token JWT.",
        "category": "SEGURIDAD",
        "data_type": "INTEGER",
        "is_editable": True
    },
    {
        "key": "PASSWORD_MIN_LENGTH",
        "value": "6",
        "default_value": "6",
        "description": "Longitud mínima obligatoria de caracteres para contraseñas de usuarios.",
        "category": "SEGURIDAD",
        "data_type": "INTEGER",
        "is_editable": True
    },
    {
        "key": "ACTIVE_ACADEMIC_YEAR",
        "value": "2024",
        "default_value": "2024",
        "description": "Año académico de referencia activo para la clasificación analítica de permanencia.",
        "category": "SPADIES",
        "data_type": "INTEGER",
        "is_editable": True
    },
    {
        "key": "INSTITUTION_NAME",
        "value": "Universidad Católica de Oriente (UCO)",
        "default_value": "Universidad Católica de Oriente (UCO)",
        "description": "Nombre institucional oficial para encabezados y reportes oficiales.",
        "category": "GENERAL",
        "data_type": "STRING",
        "is_editable": True
    },
    {
        "key": "DEFAULT_PERIOD_START",
        "value": "1-2018",
        "default_value": "1-2018",
        "description": "Periodo académico base para el cómputo inicial de series cronológicas SPADIES.",
        "category": "SPADIES",
        "data_type": "STRING",
        "is_editable": False
    }
]

def seed_default_parameters(db: Session):
    """Inicializa los parámetros por defecto del sistema si aún no existen."""
    for param in DEFAULT_PARAMETERS:
        existing = db.query(SystemParameter).filter(SystemParameter.key == param["key"]).first()
        if not existing:
            new_p = SystemParameter(**param)
            db.add(new_p)
    db.commit()
    logger.info("Catálogo de parámetros del sistema verificado/inicializado.")

def get_all_parameters(db: Session) -> List[Dict[str, Any]]:
    """Retorna la lista de todos los parámetros del sistema."""
    params = db.query(SystemParameter).order_by(SystemParameter.category, SystemParameter.key).all()
    return [
        {
            "id": p.id,
            "key": p.key,
            "value": p.value,
            "default_value": p.default_value,
            "description": p.description,
            "category": p.category,
            "data_type": p.data_type,
            "is_editable": p.is_editable,
            "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M:%S") if p.updated_at else "",
            "updated_by": p.updated_by or "Sistema"
        }
        for p in params
    ]

def get_parameter_value(db: Session, key: str, fallback: Any = None) -> Any:
    """Retorna el valor tipado (int, bool, float, str) de un parámetro según su configuración."""
    param = db.query(SystemParameter).filter(SystemParameter.key == key).first()
    if not param:
        return fallback

    val = param.value
    dt = param.data_type.upper()
    try:
        if dt == "INTEGER":
            return int(val)
        elif dt == "FLOAT":
            return float(val)
        elif dt == "BOOLEAN":
            return val.lower() in ["true", "1", "yes", "si"]
        return str(val)
    except Exception:
        return fallback

def update_parameter(
    db: Session,
    key: str,
    new_value: str,
    current_user_name: str = "Administrador",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Dict[str, Any]:
    """Actualiza un parámetro del sistema y registra la acción en la auditoría."""
    param = db.query(SystemParameter).filter(SystemParameter.key == key).first()
    if not param:
        raise AppException("PARAM_001")

    if not param.is_editable:
        raise AppException("AUTH_003", custom_user_message="Este parámetro es estructural y no puede modificarse.")

    val_str = str(new_value).strip()
    dt = param.data_type.upper()

    # Validar tipo de dato
    try:
        if dt == "INTEGER":
            int(val_str)
        elif dt == "FLOAT":
            float(val_str)
        elif dt == "BOOLEAN":
            if val_str.lower() not in ["true", "false", "1", "0", "si", "no"]:
                raise ValueError()
    except ValueError:
        raise AppException("PARAM_002", technical_detail=f"Casting fallido para clave {key} con valor '{val_str}' a {dt}.")

    old_value = param.value
    param.value = val_str
    param.updated_by = current_user_name
    db.commit()
    db.refresh(param)

    # Registrar en auditoría en lenguaje institucional
    log_audit_event(
        db=db,
        action="EDITAR",
        entity="PARAMETRO",
        entity_id=param.key,
        username=current_user_name,
        user_name=current_user_name,
        user_role="administrador",
        ip_address=ip_address,
        user_agent=user_agent,
        details=f"Actualización del parámetro del sistema '{param.key}' ({param.description}): valor anterior '{old_value}', nuevo valor '{param.value}'."
    )

    return {
        "key": param.key,
        "value": param.value,
        "description": param.description,
        "updated_at": param.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    }
