"""
SERVICIO DE AUTENTICACIÓN

Inicio de sesión con límite de intentos, emisión de JWT, cambio de contraseña y
creación del administrador inicial.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import rate_limit
from app.core.config import settings
from app.core.messages import AppException
from app.core.security import (
    create_access_token, generate_temporary_password, get_password_hash, is_legacy_hash,
    validate_password_policy, verify_password,
)
from app.models import User
from app.services.audit_service import log_audit_event
from app.services.parameter_service import get_parameter_value

logger = logging.getLogger("uco_analytics.auth")

# Contraseñas por defecto publicadas en versiones anteriores: si siguen en uso se obliga a cambiarlas.
_KNOWN_DEFAULTS = {"admin": "admin123", "consultor": "consultor123"}


def _user_payload(user: User) -> Dict[str, Any]:
    return {"id": user.id, "username": user.username, "nombre": user.nombre or user.username,
            "role": user.role, "must_change_password": bool(user.must_change_password)}


def _issue_token(db: Session, user: User) -> Dict[str, Any]:
    minutes = get_parameter_value(db, "SESSION_EXPIRATION_MINUTES", 60)
    token = create_access_token({"sub": user.username, "uid": user.id, "role": user.role}, minutes)
    return {"token": token, "expires_in": minutes * 60, "user": _user_payload(user)}


def authenticate_user(db: Session, username: str, password: str, ip: str, ua: str) -> Dict[str, Any]:
    clean = (username or "").strip()
    if not clean or not password:
        raise AppException("AUTH_001")
    max_attempts = get_parameter_value(db, "LOGIN_MAX_ATTEMPTS", 5)
    lockout = get_parameter_value(db, "LOGIN_LOCKOUT_MINUTES", 15)
    wait = rate_limit.seconds_locked(ip, clean, max_attempts, lockout)
    if wait:
        raise AppException("AUTH_007", custom_user_message=(
            f"Demasiados intentos fallidos. Intente de nuevo en {max(1, wait // 60)} minuto(s)."))

    user = db.scalar(select(User).where(User.username == clean))
    if not user or user.is_active is False or not verify_password(password, user.password):
        rate_limit.register_failure(ip, clean)
        log_audit_event(db, "LOGIN_FALLIDO", "USUARIO", clean, username=clean, ip_address=ip, user_agent=ua,
                        details="Intento fallido de inicio de sesión (credenciales incorrectas o usuario inactivo).")
        raise AppException("AUTH_001")

    rate_limit.reset(ip, clean)
    if is_legacy_hash(user.password):
        user.password = get_password_hash(password)          # migración automática a bcrypt
    if _KNOWN_DEFAULTS.get(user.username) == password or password == user.username:
        user.must_change_password = True                     # clave por defecto o igual a la cédula
    user.last_login_at = datetime.utcnow()
    db.commit()
    log_audit_event(db, "LOGIN_EXITOSO", "USUARIO", user.id, user=user, ip_address=ip, user_agent=ua,
                    details="Inicio de sesión exitoso.")
    return {"success": True, "message": "Sesión iniciada correctamente", **_issue_token(db, user)}


def change_password(db: Session, user: User, old_password: str, new_password: str, ip: str, ua: str) -> Dict[str, Any]:
    if not verify_password(old_password, user.password):
        raise AppException("AUTH_004")
    min_len = get_parameter_value(db, "PASSWORD_MIN_LENGTH", 8)
    error = validate_password_policy(new_password, min_len, user.username)
    if error:
        raise AppException("AUTH_005", custom_user_message=error)
    if verify_password(new_password, user.password):
        raise AppException("AUTH_005", custom_user_message="La nueva contraseña debe ser distinta de la actual.")
    user.password = get_password_hash(new_password)
    user.must_change_password = False
    user.password_changed_at = datetime.utcnow().replace(microsecond=0)
    db.commit()
    log_audit_event(db, "CAMBIO_CLAVE", "USUARIO", user.id, user=user, ip_address=ip, user_agent=ua,
                    details="Cambio de contraseña realizado por el propio usuario.")
    # Los tokens anteriores quedan invalidados; se entrega uno nuevo.
    return {"success": True, "message": "Contraseña actualizada exitosamente.", **_issue_token(db, user)}


def ensure_initial_admin(db: Session) -> Optional[str]:
    """
    Si no existe ningún usuario, crea el administrador inicial.
    Usa INITIAL_ADMIN_USERNAME / INITIAL_ADMIN_PASSWORD del entorno; si la
    contraseña no está definida, genera una temporal y la retorna para mostrarla
    una sola vez en la consola. Siempre obliga a cambiarla en el primer ingreso.
    """
    if db.scalar(select(func.count(User.id))):
        return None
    password = settings.INITIAL_ADMIN_PASSWORD or generate_temporary_password()
    admin = User(username=settings.INITIAL_ADMIN_USERNAME or "admin", nombre="Administrador del Sistema",
                 password=get_password_hash(password), role="administrador", must_change_password=True)
    db.add(admin)
    db.commit()
    log_audit_event(db, "CREAR", "USUARIO", admin.id, username="Sistema", user_role="sistema",
                    details=f"Creación del administrador inicial '{admin.username}' (debe cambiar la contraseña al ingresar).")
    return None if settings.INITIAL_ADMIN_PASSWORD else password
