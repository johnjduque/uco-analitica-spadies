"""
SERVICIO DE GESTIÓN DE USUARIOS
Universidad Católica de Oriente - Sistema Analítico de Deserción

Maneja creación, consulta, modificación y eliminación de usuarios (RBAC)
con contraseñas hasheadas en Bcrypt y auditoría automática de cada acción.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import User
from app.core.security import get_password_hash
from app.core.messages import AppException
from app.services.audit_service import log_audit_event

logger = logging.getLogger("uco_analytics.users")

def get_all_users(db: Session) -> List[Dict[str, Any]]:
    """Consulta la lista de todos los usuarios registrados."""
    users = db.query(User).order_by(User.id).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "nombre": u.nombre or u.username,
            "role": u.role,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else ""
        }
        for u in users
    ]

def create_user(
    db: Session,
    cedula: str,
    nombre: str = "",
    role: str = "consultor",
    actor_username: Optional[str] = "Administrador",
    actor_role: Optional[str] = "administrador",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Crea un nuevo usuario en el sistema.
    La contraseña inicial por defecto es la misma cédula (hasheada en Bcrypt).
    """
    cedula_limpia = str(cedula).strip()
    nombre_limpio = str(nombre).strip() if nombre else ""

    if not cedula_limpia or not cedula_limpia.isdigit():
        raise AppException("USER_003")

    if len(cedula_limpia) < 5:
        raise AppException("USER_003", custom_user_message="La cédula debe tener al menos 5 dígitos.")

    role_clean = role.lower() if role else "consultor"
    if role_clean not in ["administrador", "admin", "consultor"]:
        raise AppException("USER_004")

    # Verificar unicidad
    existing = db.query(User).filter(User.username == cedula_limpia).first()
    if existing:
        raise AppException("USER_001", custom_user_message=f"Ya existe un usuario registrado con la cédula {cedula_limpia}.")

    # Hash inicial Bcrypt
    hashed_password = get_password_hash(cedula_limpia)
    new_user = User(
        username=cedula_limpia,
        nombre=nombre_limpio,
        password=hashed_password,
        role=role_clean
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Registrar en auditoría en lenguaje institucional
    log_audit_event(
        db=db,
        action="CREAR",
        entity="USUARIO",
        entity_id=str(new_user.id),
        username=actor_username,
        user_name=actor_username,
        user_role=actor_role,
        ip_address=ip_address,
        user_agent=user_agent,
        details=f"Creación del usuario {new_user.nombre or new_user.username} (Cédula: {new_user.username}, Rol: {new_user.role.capitalize()}). Clave inicial configurada por defecto."
    )

    return {
        "message": f"Usuario {nombre_limpio or cedula_limpia} (Cédula: {cedula_limpia}) creado exitosamente. La contraseña inicial es su número de cédula.",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "nombre": new_user.nombre,
            "role": new_user.role
        }
    }

def update_user(
    db: Session,
    user_id: int,
    username: str,
    nombre: str = "",
    role: str = "consultor",
    password: Optional[str] = None,
    actor_username: Optional[str] = "Administrador",
    actor_role: Optional[str] = "administrador",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Dict[str, Any]:
    """Actualiza datos de un usuario existente y registra los cambios en auditoría."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppException("USER_002")

    new_username = str(username).strip()
    if not new_username.isdigit():
        raise AppException("USER_003")

    # Verificar si otra cuenta ya tiene esa cédula
    existing = db.query(User).filter(User.username == new_username, User.id != user_id).first()
    if existing:
        raise AppException("USER_001", custom_user_message="Ya existe otro usuario registrado con esa cédula.")

    old_state = {
        "username": user.username,
        "nombre": user.nombre,
        "role": user.role
    }

    user.username = new_username
    user.nombre = str(nombre).strip() if nombre else ""
    user.role = role.lower() if role else "consultor"

    pass_changed = False
    if password and password.strip():
        user.password = get_password_hash(password.strip())
        pass_changed = True

    pass_note = " Se actualizó la contraseña." if pass_changed else ""
    # Registrar en auditoría en lenguaje institucional
    log_audit_event(
        db=db,
        action="EDITAR",
        entity="USUARIO",
        entity_id=str(user.id),
        username=actor_username,
        user_name=actor_username,
        user_role=actor_role,
        ip_address=ip_address,
        user_agent=user_agent,
        details=f"Modificación del perfil de usuario {user.nombre or user.username} (Cédula: {user.username}, Rol: {user.role.capitalize()}).{pass_note}"
    )

    return {"message": "Usuario actualizado exitosamente", "user": {"id": user.id, "username": user.username, "nombre": user.nombre, "role": user.role}}

def delete_user(
    db: Session,
    user_id: int,
    actor_username: Optional[str] = "Administrador",
    actor_role: Optional[str] = "administrador",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Dict[str, Any]:
    """Elimina un usuario y registra el evento en auditoría."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppException("USER_002")

    u_nombre = user.nombre or user.username
    u_cedula = user.username
    u_rol = user.role.capitalize()

    db.delete(user)
    db.commit()

    log_audit_event(
        db=db,
        action="ELIMINAR",
        entity="USUARIO",
        entity_id=str(user_id),
        username=actor_username,
        user_name=actor_username,
        user_role=actor_role,
        ip_address=ip_address,
        user_agent=user_agent,
        details=f"Eliminación de la cuenta del usuario {u_nombre} (Cédula: {u_cedula}, Rol: {u_rol})."
    )

    return {"message": "Usuario eliminado exitosamente"}
