"""
APLICACIÓN PRINCIPAL FASTAPI - UCO Analytics

Capas:
  routers/  -> HTTP (validación de entrada y control de acceso por rol)
  services/ -> casos de uso (cargas, indicadores, usuarios, reportes, auditoría)
  domain/   -> reglas puras (periodos, motor de indicadores SPADIES)
  core/     -> configuración, base de datos, seguridad, mensajes
"""

import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.core.messages import AppException, format_error_response
from app.core.migrations import sync_schema
from app.routers import audit, auth, indicators, loads, parameters, programs, students, users
from app.services import auth_service, parameter_service, program_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("uco_analytics.main")


def initialize_database() -> None:
    sync_schema(engine)
    db = SessionLocal()
    try:
        parameter_service.seed_default_parameters(db)
        program_service.seed_catalog(db)
        temp_password = auth_service.ensure_initial_admin(db)
        if temp_password:
            banner = "=" * 70
            logger.warning(
                "\n%s\n  ADMINISTRADOR INICIAL CREADO\n  Usuario: %s\n  Contraseña temporal: %s\n"
                "  Deberá cambiarla en el primer inicio de sesión. Este mensaje no se repetirá.\n%s",
                banner, settings.INITIAL_ADMIN_USERNAME or "admin", temp_password, banner)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Iniciando %s v%s | entorno=%s | BD=%s", settings.PROJECT_NAME, settings.PROJECT_VERSION,
                settings.APP_ENV, settings.DB_ENGINE)
    initialize_database()
    yield
    logger.info("Servidor detenido.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="API de analítica de deserción y permanencia estudiantil (metodología SPADIES 3.0).",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
)

# -------------------------------------------------------------------
# CORS: por defecto solo mismo origen. En desarrollo se permite Vite (5173).
# -------------------------------------------------------------------
cors_origins = list(settings.CORS_ORIGINS)
if not settings.IS_PRODUCTION:
    cors_origins += ["http://localhost:5173", "http://127.0.0.1:5173"]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["Content-Disposition"],
    )


# -------------------------------------------------------------------
# CABECERAS DE SEGURIDAD
# -------------------------------------------------------------------
_CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; "
        "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if not request.url.path.startswith(("/docs", "/openapi.json")):
        response.headers.setdefault("Content-Security-Policy", _CSP)
    if request.url.path.startswith(settings.API_PREFIX):
        response.headers.setdefault("Cache-Control", "no-store")
    return response


# -------------------------------------------------------------------
# MANEJO CENTRALIZADO DE ERRORES (sin exponer detalles internos)
# -------------------------------------------------------------------
def _trace() -> str:
    return uuid.uuid4().hex[:8]


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    trace_id = _trace()
    logger.warning("[%s] [%s] %s %s | %s", exc.code, trace_id, request.method, request.url.path, exc.technical_message)
    return JSONResponse(status_code=exc.status_code,
                        content=format_error_response(exc.code, exc.user_message, trace_id))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    trace_id = _trace()
    logger.info("[VAL_001] [%s] %s %s | %s", trace_id, request.method, request.url.path, exc.errors())
    return JSONResponse(status_code=422, content=format_error_response("VAL_001", None, trace_id))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    trace_id = _trace()
    message = exc.detail if isinstance(exc.detail, str) else "Solicitud no válida."
    return JSONResponse(status_code=exc.status_code,
                        content={"success": False, "detail": message, "message": message,
                                 "error": {"code": f"HTTP_{exc.status_code}", "message": message, "trace_id": trace_id}})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    trace_id = _trace()
    logger.error("[SYS_001] [%s] %s %s: %s", trace_id, request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(status_code=500, content=format_error_response(
        "SYS_001", "Ocurrió un error interno. Comuníquese con soporte indicando el código de seguimiento.", trace_id))


# -------------------------------------------------------------------
# RUTAS DE LA API
# -------------------------------------------------------------------
@app.get(f"{settings.API_PREFIX}/health", tags=["Sistema"])
def health():
    return {"status": "ok", "version": settings.PROJECT_VERSION}


for r in (auth.router, users.router, loads.router, programs.router, indicators.router,
          students.router, audit.router, parameters.router):
    app.include_router(r, prefix=settings.API_PREFIX)


# -------------------------------------------------------------------
# FRONTEND (SPA compilada en frontend/dist)
# -------------------------------------------------------------------
_dist = Path(settings.FRONTEND_DIST).resolve()
if (_dist / "assets").exists():
    app.mount("/assets", StaticFiles(directory=_dist / "assets"), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
def spa(full_path: str):
    if full_path.startswith(settings.API_PREFIX.strip("/") + "/") or full_path == settings.API_PREFIX.strip("/"):
        raise HTTPException(status_code=404, detail="Recurso no encontrado.")
    if full_path:
        candidate = (_dist / full_path).resolve()
        if candidate.is_file() and _dist in candidate.parents:
            return FileResponse(candidate)
    index = _dist / "index.html"
    if index.exists():
        return FileResponse(index, headers={"Cache-Control": "no-cache"})
    return JSONResponse({"sistema": settings.PROJECT_NAME, "estado": "API operativa. Compile el frontend (npm run build)."})
