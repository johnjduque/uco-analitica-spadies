"""
CONFIGURACIÓN CENTRAL DEL SISTEMA
Universidad Católica de Oriente - UCO Analytics

Toda la configuración se toma de variables de entorno (archivo backend/.env en
instalación local, o variables del contenedor en servidor). Ningún secreto vive
en el código fuente.
"""

import os
import sys
import secrets
import logging
from pathlib import Path
from typing import List

from dotenv import load_dotenv

logger = logging.getLogger("uco_analytics.config")

# -------------------------------------------------------------------
# Rutas base (soporta ejecución normal y ejecutable PyInstaller)
# -------------------------------------------------------------------
IS_FROZEN = getattr(sys, "frozen", False)

if IS_FROZEN:
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)))
    EXE_DIR = Path(os.path.dirname(sys.executable))
    BACKEND_DIR = BUNDLE_DIR
    ROOT_DIR = BUNDLE_DIR
else:
    EXE_DIR = None
    BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
    ROOT_DIR = BACKEND_DIR.parent

# El .env se busca junto al ejecutable (instalación) o en backend/ (desarrollo)
_env_candidates = [BACKEND_DIR / ".env"]
if EXE_DIR is not None:
    _env_candidates.insert(0, EXE_DIR / ".env")
for _env in _env_candidates:
    if _env.exists():
        load_dotenv(dotenv_path=_env)
        break


def _writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".perm_test"
        probe.write_text("ok")
        probe.unlink()
        return True
    except Exception:
        return False


def _resolve_persistent_dir() -> Path:
    """Carpeta donde se guardan la BD SQLite y la llave secreta generada."""
    custom = os.getenv("PERSISTENT_DIR")
    if custom:
        p = Path(custom)
        p.mkdir(parents=True, exist_ok=True)
        return p
    if IS_FROZEN:
        if EXE_DIR is not None and _writable(EXE_DIR):
            return EXE_DIR
        p = Path(os.getenv("LOCALAPPDATA", str(Path.home()))) / "UCO_Analytics"
        p.mkdir(parents=True, exist_ok=True)
        return p
    return BACKEND_DIR


def _split_csv(value: str) -> List[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


class Settings:
    PROJECT_NAME: str = "UCO Analytics - Deserción y Permanencia Estudiantil"
    PROJECT_VERSION: str = "3.0.0"
    API_PREFIX: str = "/api"

    # Entorno: 'desarrollo' (local) o 'produccion' (servidor)
    APP_ENV: str = os.getenv("APP_ENV", "desarrollo").strip().lower()

    BACKEND_DIR: str = str(BACKEND_DIR)
    ROOT_DIR: str = str(ROOT_DIR)
    PERSISTENT_DIR: str = str(_resolve_persistent_dir())

    # Servidor de escritorio
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

    # ---------------------------------------------------------------
    # Base de datos: 'sqlite' (local) o 'sqlserver' (servidor)
    # ---------------------------------------------------------------
    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite").strip().lower()
    SQLSERVER_HOST: str = os.getenv("SQLSERVER_HOST", "localhost")
    SQLSERVER_PORT: int = int(os.getenv("SQLSERVER_PORT", "1433"))
    SQLSERVER_DATABASE: str = os.getenv("SQLSERVER_DATABASE", "UCO_Analytics")
    SQLSERVER_USER: str = os.getenv("SQLSERVER_USER", "")
    SQLSERVER_PASSWORD: str = os.getenv("SQLSERVER_PASSWORD", "")
    SQLSERVER_DRIVER: str = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server")
    # 'yes' solo cuando el certificado del servidor es autofirmado (ej. contenedor local)
    SQLSERVER_TRUST_CERT: str = os.getenv("SQLSERVER_TRUST_CERT", "no").strip().lower()
    SQLITE_DB_NAME: str = os.getenv("SQLITE_DB_NAME", "datos_uco.db")

    # ---------------------------------------------------------------
    # Seguridad
    # ---------------------------------------------------------------
    ALGORITHM: str = "HS256"
    # Usuario administrador inicial (solo se usa si no existe ningún usuario)
    INITIAL_ADMIN_USERNAME: str = os.getenv("INITIAL_ADMIN_USERNAME", "admin").strip()
    INITIAL_ADMIN_PASSWORD: str = os.getenv("INITIAL_ADMIN_PASSWORD", "")
    # Orígenes permitidos para CORS (separados por coma). Vacío = solo mismo origen.
    CORS_ORIGINS: List[str] = _split_csv(os.getenv("CORS_ORIGINS", ""))
    # Activa documentación Swagger (/docs). Por defecto solo en desarrollo.
    ENABLE_DOCS: bool = os.getenv("ENABLE_DOCS", "").strip().lower() in ("1", "true", "si", "yes") or \
        os.getenv("APP_ENV", "desarrollo").strip().lower() != "produccion"

    @property
    def IS_PRODUCTION(self) -> bool:
        return self.APP_ENV == "produccion"

    @property
    def FRONTEND_DIST(self) -> str:
        candidates = []
        if IS_FROZEN:
            candidates.append(Path(getattr(sys, "_MEIPASS", "")) / "frontend" / "dist")
            if EXE_DIR is not None:
                candidates.append(EXE_DIR / "frontend" / "dist")
        candidates.append(Path(self.ROOT_DIR) / "frontend" / "dist")
        for c in candidates:
            if c.exists():
                return str(c)
        return str(candidates[-1])

    @property
    def DATABASE_URL(self):
        from sqlalchemy.engine import URL

        custom_url = os.getenv("DATABASE_URL")
        if custom_url:
            return custom_url
        if self.DB_ENGINE == "sqlserver":
            query = {"driver": self.SQLSERVER_DRIVER}
            if self.SQLSERVER_TRUST_CERT in ("yes", "si", "true", "1"):
                query["TrustServerCertificate"] = "yes"
            return URL.create(
                "mssql+pyodbc",
                username=self.SQLSERVER_USER,
                password=self.SQLSERVER_PASSWORD,
                host=self.SQLSERVER_HOST,
                port=self.SQLSERVER_PORT,
                database=self.SQLSERVER_DATABASE,
                query=query,
            )
        return f"sqlite:///{Path(self.PERSISTENT_DIR) / self.SQLITE_DB_NAME}"

    @property
    def SECRET_KEY(self) -> str:
        return _SECRET_KEY


def _load_secret_key(persistent_dir: str, is_production: bool) -> str:
    """
    Orden de prioridad:
    1. Variable de entorno SECRET_KEY (obligatoria en producción).
    2. Archivo .secret_key en la carpeta persistente (instalación local),
       generado automáticamente la primera vez con 64 bytes aleatorios.
    """
    env_key = os.getenv("SECRET_KEY", "").strip()
    weak_defaults = {
        "clave_secreta_super_segura_debe_cambiarse_en_produccion_2026",
        "uco_super_secure_secret_key_2026_change_in_production_89f3a1e7",
        "uco_jwt_super_secret_key_production_2026_89f3a1e7b24c9",
    }
    if env_key and env_key not in weak_defaults and len(env_key) >= 32:
        return env_key
    if is_production:
        raise RuntimeError(
            "SECRET_KEY no configurada o insegura. En producción defina la variable de entorno "
            "SECRET_KEY con al menos 32 caracteres aleatorios (ej: python -c \"import secrets; print(secrets.token_urlsafe(64))\")."
        )
    key_file = Path(persistent_dir) / ".secret_key"
    if key_file.exists():
        key = key_file.read_text(encoding="utf-8").strip()
        if len(key) >= 32:
            return key
    key = secrets.token_urlsafe(64)
    key_file.write_text(key, encoding="utf-8")
    try:
        os.chmod(key_file, 0o600)
    except Exception:
        pass
    if env_key:
        logger.warning("SECRET_KEY del .env es débil o conocida; se generó una llave aleatoria en %s", key_file)
    return key


settings = Settings()
_SECRET_KEY = _load_secret_key(settings.PERSISTENT_DIR, settings.IS_PRODUCTION)
