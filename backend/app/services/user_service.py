"""
SERVICIO DE GESTIÓN DE USUARIOS (RBAC)

- Los usuarios nuevos reciben una contraseña temporal aleatoria que el
  administrador comunica; el sistema obliga a cambiarla en el primer ingreso.
- Siempre debe existir al menos un administrador activo.
"""

import re
from typing import Any, Dict, List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.messages import AppException
from app.core.security import ROLES, generate_temporary_password, get_password_hash
from app.models import User
from app.services.audit_service import iso_utc, log_audit_event

_USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{4,30}$")


def _serialize(u: User) -> Dict[str, Any]:
    return {
        "id": u.id, "username": u.username, "nombre": u.nombre or u.username, "role": u.role,
        "activo": u.is_active is not False, "debe_cambiar_clave": bool(u.must_change_password),
        "ultimo_ingreso": iso_utc(u.last_login_at), "created_at": iso_utc(u.created_at),
    }


def _validate(username: str, nombre: str, role: str):
    username = (username or "").strip()
    nombre = " ".join((nombre or "").split())
    role = (role or "").strip().lower()
    if not _USERNAME_RE.match(username):
        raise AppException("USER_003")
    if len(nombre) < 3:
        raise AppException("VAL_001", custom_user_message="El nombre completo es obligatorio.")
    if role not in ROLES:
        raise AppException("USER_004")
    return username, nombre, role


def _active_admins(db: Session) -> int:
    active = or_(User.is_active.is_(None), User.is_active.is_(True))
    return db.scalar(select(func.count(User.id)).where(User.role == "administrador", active)) or 0


def get_all_users(db: Session) -> List[Dict[str, Any]]:
    return [_serialize(u) for u in db.scalars(select(User).order_by(User.id)).all()]


def create_user(db: Session, username: str, nombre: str, role: str, actor: User, ip=None, ua=None) -> Dict[str, Any]:
    username, nombre, role = _validate(username, nombre, role)
    if db.scalar(select(User).where(User.username == username)):
        raise AppException("USER_001")
    temp = generate_temporary_password()
    user = User(username=username, nombre=nombre, role=role, password=get_password_hash(temp), must_change_password=True)
    db.add(user)
    db.commit()
    log_audit_event(db, "CREAR", "USUARIO", user.id, user=actor, ip_address=ip, user_agent=ua,
                    details=f"Creación del usuario {nombre} ({username}, rol {role}) con contraseña temporal.")
    return {"message": "Usuario creado. Entregue la contraseña temporal al usuario; deberá cambiarla al ingresar.",
            "user": _serialize(user), "temporary_password": temp}


def update_user(db: Session, user_id: int, username: str, nombre: str, role: str, activo: Optional[bool],
                actor: User, ip=None, ua=None) -> Dict[str, Any]:
    user = db.get(User, user_id)
    if not user:
        raise AppException("USER_002")
    username, nombre, role = _validate(username, nombre, role)
    if db.scalar(select(User).where(User.username == username, User.id != user_id)):
        raise AppException("USER_001")
    will_be_admin = role == "administrador" and (activo is not False)
    if user.role == "administrador" and user.is_active is not False and not will_be_admin and _active_admins(db) <= 1:
        raise AppException("USER_005")
    if user.id == actor.id and (not will_be_admin):
        raise AppException("USER_005", custom_user_message="No puede quitarse a sí mismo el rol de administrador ni desactivarse.")
    before = _serialize(user)
    user.username, user.nombre, user.role = username, nombre, role
    if activo is not None:
        user.is_active = bool(activo)
    db.commit()
    log_audit_event(db, "EDITAR", "USUARIO", user.id, user=actor, ip_address=ip, user_agent=ua,
                    details={"antes": {k: before[k] for k in ("username", "nombre", "role", "activo")},
                             "despues": {k: _serialize(user)[k] for k in ("username", "nombre", "role", "activo")}})
    return {"message": "Usuario actualizado exitosamente.", "user": _serialize(user)}


def reset_password(db: Session, user_id: int, actor: User, ip=None, ua=None) -> Dict[str, Any]:
    user = db.get(User, user_id)
    if not user:
        raise AppException("USER_002")
    temp = generate_temporary_password()
    from datetime import datetime
    user.password = get_password_hash(temp)
    user.must_change_password = True
    user.password_changed_at = datetime.utcnow().replace(microsecond=0)   # cierra sesiones abiertas
    db.commit()
    log_audit_event(db, "RESTABLECER_CLAVE", "USUARIO", user.id, user=actor, ip_address=ip, user_agent=ua,
                    details=f"Restablecimiento de contraseña del usuario {user.username} (temporal, cambio obligatorio).")
    return {"message": "Contraseña restablecida. Entregue la contraseña temporal al usuario.", "temporary_password": temp}


def delete_user(db: Session, user_id: int, actor: User, ip=None, ua=None) -> Dict[str, Any]:
    user = db.get(User, user_id)
    if not user:
        raise AppException("USER_002")
    if user.id == actor.id:
        raise AppException("USER_005")
    if user.role == "administrador" and user.is_active is not False and _active_admins(db) <= 1:
        raise AppException("USER_005")
    info = f"{user.nombre or user.username} ({user.username}, rol {user.role})"
    db.delete(user)
    db.commit()
    log_audit_event(db, "ELIMINAR", "USUARIO", user_id, user=actor, ip_address=ip, user_agent=ua,
                    details=f"Eliminación de la cuenta del usuario {info}.")
    return {"message": "Usuario eliminado exitosamente."}
