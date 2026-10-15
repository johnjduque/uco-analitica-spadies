"""
SERVICIO DE AUTENTICACIÓN Y SEGURIDAD
Universidad Católica de Oriente - Sistema Analítico de Deserción

Maneja login, validación de contraseñas (Bcrypt con compatibilidad retroactiva PBKDF2),
generación de tokens JWT, migración automática de hash a Bcrypt y trazabilidad en auditoría.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import User
from app.core.security import verify_password, get_password_hash, needs_rehash, create_access_token
from app.core.messages import AppException
from app.services.audit_service import log_audit_event
from app.services.parameter_service import get_parameter_value

logger = logging.getLogger("uco_analytics.auth")

def authenticate_user(
    db: Session,
    username: str,
    password: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Autentica un usuario con su cédula y contraseña.
    Emite un JWT firmado y registra el evento en auditoría.
    """
    clean_username = str(username).strip()
    if not clean_username or not password:
        raise AppException("AUTH_001", technical_detail="Username o password vacíos en petición de login.")

    user = db.query(User).filter(User.username == clean_username).first()

    if not user or not verify_password(password, user.password):
        # Registrar intento fallido en lenguaje institucional
        log_audit_event(
            db=db,
            action="LOGIN_FALLIDO",
            entity="USUARIO",
            entity_id=clean_username,
            username=clean_username,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"Intento fallido de inicio de sesión con documento {clean_username} (contraseña o credenciales incorrectas)."
        )
        raise AppException("AUTH_001", technical_detail=f"Credenciales inválidas para usuario {clean_username}.")

    # Si el hash era del esquema anterior (PBKDF2), actualizarlo automáticamente a Bcrypt
    if needs_rehash(user.password):
        try:
            user.password = get_password_hash(password)
            db.commit()
            logger.info(f"Hash de usuario {user.username} migrado automáticamente al estándar Bcrypt.")
        except Exception as e:
            logger.warning(f"No se pudo rehashear la contraseña: {e}")

    # Generar Token JWT
    token_payload = {
        "sub": user.username,
        "user_id": user.id,
        "username": user.username,
        "name": user.nombre or user.username,
        "role": user.role
    }
    token = create_access_token(token_payload)

    # Registrar login exitoso en lenguaje institucional
    log_audit_event(
        db=db,
        action="LOGIN_EXITOSO",
        entity="USUARIO",
        entity_id=str(user.id),
        user_id=user.id,
        username=user.username,
        user_name=user.nombre or user.username,
        user_role=user.role,
        ip_address=ip_address,
        user_agent=user_agent,
        details="Inicio de sesión exitoso en la plataforma UCO Analytics."
    )

    return {
        "success": True,
        "message": "Sesión iniciada correctamente",
        "token": token,
        "role": user.role,
        "username": user.username,
        "nombre": user.nombre or user.username
    }

def change_password(
    db: Session,
    username: str,
    old_password: str,
    new_password: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cambio de contraseña verificado por el usuario.
    """
    clean_username = str(username).strip()
    if not clean_username:
        raise AppException("USER_003", custom_user_message="La cédula o usuario es requerido.")

    user = db.query(User).filter(User.username == clean_username).first()
    if not user:
        raise AppException("USER_002")

    if not verify_password(old_password, user.password):
        raise AppException("AUTH_004")

    # Validar longitud mínima de contraseña desde catálogo de parámetros
    min_len = get_parameter_value(db, "PASSWORD_MIN_LENGTH", fallback=6)
    clean_new_pass = new_password.strip() if new_password else ""
    if len(clean_new_pass) < min_len:
        raise AppException(
            "AUTH_005",
            custom_user_message=f"La nueva contraseña debe tener al menos {min_len} caracteres."
        )

    user.password = get_password_hash(clean_new_pass)
    db.commit()

    # Registrar en auditoría en lenguaje institucional
    log_audit_event(
        db=db,
        action="CAMBIO_CLAVE",
        entity="USUARIO",
        entity_id=str(user.id),
        user_id=user.id,
        username=user.username,
        user_name=user.nombre or user.username,
        user_role=user.role,
        ip_address=ip_address,
        user_agent=user_agent,
        details="Actualización voluntaria de contraseña de acceso a la plataforma."
    )

    return {
        "success": True,
        "message": "Contraseña actualizada exitosamente."
    }
