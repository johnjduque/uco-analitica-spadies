"""
SEGURIDAD: HASH DE CONTRASEÑAS, JWT Y CONTROL DE ACCESO POR ROLES (RBAC)

- Contraseñas con bcrypt (costo 12). Verificación retrocompatible de hashes
  PBKDF2 antiguos, que se migran a bcrypt en el siguiente inicio de sesión.
- Tokens JWT firmados (HS256) con expiración. Un token emitido antes del último
  cambio de contraseña queda invalidado.
- Dependencias de FastAPI:
    get_current_user_allow_pending -> usuario autenticado (aunque deba cambiar clave)
    get_current_user               -> usuario autenticado y con clave definitiva
    require_admin                  -> solo rol administrador
"""

import base64
import calendar
import hashlib
import hmac
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.messages import AppException

ROLES = ("administrador", "consultor")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# -------------------------------------------------------------------
# CONTRASEÑAS
# -------------------------------------------------------------------
def get_password_hash(password: str) -> str:
    pwd = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd, bcrypt.gensalt(rounds=12)).decode("utf-8")


def _ab64_decode(data: str) -> bytes:
    data = data.replace(".", "+")
    return base64.b64decode(data + "=" * (-len(data) % 4))


def _verify_legacy_pbkdf2(password: str, hashed: str) -> bool:
    """Verifica hashes antiguos con formato passlib: $pbkdf2-sha256$rondas$sal$checksum."""
    try:
        _, scheme, rounds, salt, checksum = hashed.split("$")
        if scheme != "pbkdf2-sha256":
            return False
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), _ab64_decode(salt), int(rounds))
        return hmac.compare_digest(dk, _ab64_decode(checksum))
    except Exception:
        return False


def is_legacy_hash(hashed: str) -> bool:
    return bool(hashed) and hashed.startswith("$pbkdf2-sha256$")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    if is_legacy_hash(hashed_password):
        return _verify_legacy_pbkdf2(plain_password, hashed_password)
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
    except Exception:
        return False


def generate_temporary_password(length: int = 12) -> str:
    """Contraseña temporal legible (sin caracteres ambiguos) con letras y dígitos."""
    alphabet = "".join(c for c in string.ascii_letters + string.digits if c not in "0OoIl1")
    while True:
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))
        if any(c.isdigit() for c in pwd) and any(c.isupper() for c in pwd) and any(c.islower() for c in pwd):
            return pwd


def validate_password_policy(password: str, min_length: int, username: str = "") -> Optional[str]:
    """Retorna un mensaje de error si la contraseña no cumple la política, o None si es válida."""
    pwd = password or ""
    if len(pwd) < min_length:
        return f"La contraseña debe tener al menos {min_length} caracteres."
    if not any(c.isalpha() for c in pwd) or not any(c.isdigit() for c in pwd):
        return "La contraseña debe combinar letras y números."
    if username and pwd.strip().lower() == username.strip().lower():
        return "La contraseña no puede ser igual al usuario o cédula."
    return None


# -------------------------------------------------------------------
# JWT
# -------------------------------------------------------------------
def utc_timestamp(dt: datetime) -> int:
    """Segundos epoch de un datetime naive expresado en UTC (independiente de la zona del equipo)."""
    return calendar.timegm(dt.utctimetuple())


def create_access_token(data: Dict[str, Any], expires_minutes: int) -> str:
    now = datetime.utcnow()
    payload = data.copy()
    payload.update({
        "iat": utc_timestamp(now),
        "exp": now + timedelta(minutes=expires_minutes),
        "iss": "uco-analytics",
    })
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "iat", "sub"]}, issuer="uco-analytics",
        )
    except jwt.ExpiredSignatureError:
        raise AppException("AUTH_002", technical_detail="Token JWT expirado.")
    except jwt.InvalidTokenError as exc:
        raise AppException("AUTH_002", technical_detail=f"Token JWT inválido: {exc}")


# -------------------------------------------------------------------
# DEPENDENCIAS DE AUTORIZACIÓN
# -------------------------------------------------------------------
def get_current_user_allow_pending(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Usuario autenticado y activo. Permite usuarios con cambio de clave pendiente."""
    from app.models import User  # import diferido para evitar ciclos

    if not token:
        raise AppException("AUTH_002", custom_user_message="Debe iniciar sesión para acceder a este recurso.")
    payload = decode_token(token)
    try:
        user_id = int(payload.get("uid"))
    except (TypeError, ValueError):
        raise AppException("AUTH_002", technical_detail="Token sin uid válido.")
    user = db.get(User, user_id)
    if not user or user.is_active is False or user.username != payload.get("sub"):
        raise AppException("AUTH_002", technical_detail="Usuario del token inexistente o inactivo.")
    if user.password_changed_at and int(payload.get("iat", 0)) < utc_timestamp(user.password_changed_at):
        raise AppException("AUTH_002", technical_detail="Token emitido antes del último cambio de contraseña.")
    return user


def get_current_user(user=Depends(get_current_user_allow_pending)):
    """Usuario autenticado que ya definió su contraseña personal."""
    if user.must_change_password:
        raise AppException("AUTH_006")
    return user


def require_admin(user=Depends(get_current_user)):
    if (user.role or "").lower() != "administrador":
        raise AppException("AUTH_003", technical_detail=f"Usuario {user.username} con rol {user.role} intentó acción de administrador.")
    return user
