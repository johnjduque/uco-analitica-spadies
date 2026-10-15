"""
APLICACIÓN PRINCIPAL FASTAPI (ARQUITECTURA PROFESIONAL UCO)
Universidad Católica de Oriente - Sistema Analítico de Deserción

Integra Clean Architecture, soporte dual de bases de datos (SQL Server & SQLite),
autenticación segura con Bcrypt y JWT, auditoría de cambios (Audit Trail),
catálogo de parámetros y manejo centralizado de excepciones según OWASP.
"""

import os
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.messages import AppException, format_error_response
from app.models import User
from app.core.security import get_password_hash
from app.services import parameter_service

# Routers
from app.routers import auth, users, loads, analytics, audit, parameters

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("uco_analytics.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización segura del sistema al arrancar el servidor."""
    logger.info("=" * 65)
    logger.info(f"Iniciando {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    logger.info(f"Motor de Base de Datos seleccionado: {settings.DB_ENGINE.upper()}")
    logger.info("=" * 65)

    # 1. Crear tablas en Base de Datos (SQL Server o SQLite)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Esquemas de Base de Datos sincronizados exitosamente.")
    except Exception as e:
        logger.error(f"Error sincronizando esquemas de BD: {e}")

    # 2. Inicializar parámetros del sistema y usuario administrador inicial
    db = SessionLocal()
    try:
        # Asegurar columnas si la tabla de usuarios ya existía
        try:
            with engine.connect() as conn:
                if settings.DB_ENGINE == "sqlite":
                    cols = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
                    if "nombre" not in cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN nombre TEXT DEFAULT ''"))
                    if "created_at" not in cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN created_at TIMESTAMP"))
                    if "updated_at" not in cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP"))
                    # data_loads
                    dl_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(data_loads)"))]
                    if "created_at" not in dl_cols:
                        conn.execute(text("ALTER TABLE data_loads ADD COLUMN created_at TIMESTAMP"))
                    conn.commit()
        except Exception as e:
            logger.warning(f"Verificación de esquemas users/data_loads: {e}")

        # Catálogo de Parámetros
        parameter_service.seed_default_parameters(db)

        # Asegurar usuarios genéricos de entorno de pruebas
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                nombre="Administrador Sistema",
                password=get_password_hash("admin123"),
                role="administrador"
            )
            db.add(admin_user)
            logger.info("Usuario genérico 'admin' creado por defecto.")

        consultor_user = db.query(User).filter(User.username == "consultor").first()
        if not consultor_user:
            consultor_user = User(
                username="consultor",
                nombre="Consultor Académico",
                password=get_password_hash("consultor123"),
                role="consultor"
            )
            db.add(consultor_user)
            logger.info("Usuario genérico 'consultor' creado por defecto.")
        db.commit()
    except Exception as e:
        logger.error(f"Error en seed inicial: {e}")
    finally:
        db.close()

    yield
    logger.info("Servidor UCO Analytics detenido de forma segura.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="API RESTful de Alta Disponibilidad para Analítica de Deserción y Permanencia UCO",
    lifespan=lifespan
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# MANEJADOR CENTRALIZADO DE EXCEPCIONES (OWASP COMPLIANT)
# -------------------------------------------------------------------
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    trace_id = str(uuid.uuid4())[:8]
    logger.warning(
        f"[{exc.code}] [TraceID: {trace_id}] Endpoint: {request.method} {request.url.path} | "
        f"Detalle Técnico: {exc.technical_message}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            code=exc.code,
            custom_user_message=exc.user_message,
            trace_id=trace_id
        )
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Si detail es un string estándar de FastAPI
    trace_id = str(uuid.uuid4())[:8]
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": exc.detail,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "trace_id": trace_id
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    trace_id = str(uuid.uuid4())[:8]
    logger.error(
        f"[SYS_001] [TraceID: {trace_id}] Excepción no controlada en {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content=format_error_response(
            code="SYS_001",
            custom_user_message="Ocurrió un inconveniente temporal en el servidor. Comuníquese con soporte técnico indicando el código de seguimiento.",
            trace_id=trace_id
        )
    )

# -------------------------------------------------------------------
# REGISTRO DE ENRUTADORES (/api/...)
# -------------------------------------------------------------------
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(users.bootstrap_router, prefix=settings.API_V1_STR)
app.include_router(loads.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(parameters.router, prefix=settings.API_V1_STR)

# -------------------------------------------------------------------
# SERVIDOR DE ARCHIVOS ESTÁTICOS FRONTEND
# -------------------------------------------------------------------
frontend_dist = settings.FRONTEND_DIST
assets_dir = os.path.join(frontend_dist, "assets")

if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/logo-uco.svg")
def serve_logo():
    p = os.path.join(frontend_dist, "logo-uco.svg")
    if os.path.exists(p):
        return FileResponse(p)
    return FileResponse(os.path.join(settings.ROOT_DIR, "frontend", "public", "logo-uco.svg"))

@app.get("/favicon.svg")
def serve_favicon():
    p = os.path.join(frontend_dist, "favicon.svg")
    if os.path.exists(p):
        return FileResponse(p)
    return FileResponse(os.path.join(settings.ROOT_DIR, "frontend", "public", "favicon.svg"))

@app.get("/")
def serve_root():
    index_path = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "sistema": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "motor_bd": settings.DB_ENGINE.upper(),
        "estado": "Operativo en puerto 8000. Documentación interactiva en /docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
