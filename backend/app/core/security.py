import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.messages import AppException
from app.core.database import get_db

import bcrypt
from passlib.hash import pbkdf2_sha256

# Esquema de autenticación Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash almacenado (Bcrypt o PBKDF2)."""
    if not plain_password or not hashed_password:
        return False
    try:
        if pbkdf2_sha256.identify(hashed_password):
            return pbkdf2_sha256.verify(plain_password, hashed_password)
        pwd_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Genera un hash seguro utilizando Bcrypt nativo con salt automático y factor de costo 12."""
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def needs_rehash(hashed_password: str) -> bool:
    """Determina si un hash antiguo (PBKDF2) debe actualizarse automáticamente al nuevo estándar Bcrypt."""
    if not hashed_password:
        return False
    return pbkdf2_sha256.identify(hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Genera un JSON Web Token (JWT) firmado para la sesión del usuario."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "uco-analytics-backend"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decodifica y valida la firma y expiración de un JWT."""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AppException("AUTH_002", technical_detail="Token JWT ha expirado.")
    except jwt.InvalidTokenError as e:
        raise AppException("AUTH_002", technical_detail=f"Firma de JWT no válida: {str(e)}")

def get_current_user_payload(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[Dict[str, Any]]:
    """Extrae la información del usuario autenticado a partir del header Authorization."""
    if not token:
        return None
    return decode_token(token)

def require_authenticated_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Exige que la petición contenga un Bearer Token válido."""
    if not token:
        raise AppException("AUTH_002", custom_user_message="Debe iniciar sesión para acceder a este recurso.")
    return decode_token(token)

def require_admin_role(user_payload: Dict[str, Any] = Depends(require_authenticated_user)) -> Dict[str, Any]:
    """Exige que el usuario autenticado cuente con el rol de Administrador."""
    role = str(user_payload.get("role", "")).lower()
    if role not in ["administrador", "admin"]:
        raise AppException("AUTH_003")
    return user_payload
