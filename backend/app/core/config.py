import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
BASE_BACKEND_PATH = Path(__file__).resolve().parent.parent.parent
BASE_ROOT_PATH = BASE_BACKEND_PATH.parent
load_dotenv(dotenv_path=os.path.join(BASE_BACKEND_PATH, ".env"))

class Settings:
    # -------------------------------------------------------------
    # PROYECTO
    # -------------------------------------------------------------
    PROJECT_NAME: str = "UCO Analytics - Deserción y Permanencia Estudiantil"
    PROJECT_VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"

    # Directorios base
    BACKEND_DIR: str = str(BASE_BACKEND_PATH)
    ROOT_DIR: str = str(BASE_ROOT_PATH)
    FRONTEND_DIST: str = os.path.join(str(BASE_ROOT_PATH), "frontend", "dist")
    USER_UPLOADS_DIR: str = os.getenv("USER_UPLOADS_DIR", os.path.join(str(BASE_BACKEND_PATH), "user_uploads"))
    DATA_DIR: str = os.path.join(str(BASE_ROOT_PATH), "Data")

    # -------------------------------------------------------------
    # BASE DE DATOS: SOPORTE DUAL (SQL SERVER & SQLITE)
    # -------------------------------------------------------------
    # Motor: 'sqlite' para instalación local / offline; 'sqlserver' para servidor en línea
    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite").lower()

    # Configuración SQL Server
    SQLSERVER_HOST: str = os.getenv("SQLSERVER_HOST", "localhost")
    SQLSERVER_PORT: str = os.getenv("SQLSERVER_PORT", "1433")
    SQLSERVER_DATABASE: str = os.getenv("SQLSERVER_DATABASE", "UCO_Analytics")
    SQLSERVER_USER: str = os.getenv("SQLSERVER_USER", "sa")
    SQLSERVER_PASSWORD: str = os.getenv("SQLSERVER_PASSWORD", "")
    SQLSERVER_DRIVER: str = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server")

    # Configuración SQLite Local
    SQLITE_DB_NAME: str = os.getenv("SQLITE_DB_NAME", "datos_uco.db")

    @property
    def DATABASE_URL(self) -> str:
        # Si se especifica una URL explícita en .env, usarla directamente
        custom_url = os.getenv("DATABASE_URL")
        if custom_url:
            return custom_url

        if self.DB_ENGINE == "sqlserver":
            # Conexión SQLAlchemy para Microsoft SQL Server con pyodbc
            driver = self.SQLSERVER_DRIVER.replace(" ", "+")
            return (
                f"mssql+pyodbc://{self.SQLSERVER_USER}:{self.SQLSERVER_PASSWORD}@"
                f"{self.SQLSERVER_HOST}:{self.SQLSERVER_PORT}/{self.SQLSERVER_DATABASE}?"
                f"driver={driver}&TrustServerCertificate=yes"
            )
        else:
            # Por defecto SQLite local
            sqlite_path = os.path.join(self.BACKEND_DIR, self.SQLITE_DB_NAME)
            return f"sqlite:///{sqlite_path}"

    # -------------------------------------------------------------
    # SEGURIDAD Y AUTENTICACIÓN
    # -------------------------------------------------------------
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "uco_super_secure_secret_key_2026_change_in_production_89f3a1e7"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Modo de autenticación: 'LOCAL' (JWT nativo) o 'KEYCLOAK' (SSO Institucional)
    AUTH_MODE: str = os.getenv("AUTH_MODE", "LOCAL").upper()

    # Configuración Keycloak (cuando AUTH_MODE == 'KEYCLOAK')
    KEYCLOAK_SERVER_URL: str = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "uco")
    KEYCLOAK_CLIENT_ID: str = os.getenv("KEYCLOAK_CLIENT_ID", "uco-analytics-app")
    KEYCLOAK_CLIENT_SECRET: str = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

settings = Settings()
