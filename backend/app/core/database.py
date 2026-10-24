"""
CONEXIÓN A BASE DE DATOS (SQLite local o Microsoft SQL Server)
"""

import logging

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger("uco_analytics.database")


def _ensure_sqlserver_database(url) -> None:
    """Crea la base de datos en SQL Server si aún no existe (requiere permiso CREATE DATABASE)."""
    url = make_url(url)
    db_name = url.database
    if not db_name:
        return
    master_url = url.set(database="master")
    tmp = create_engine(master_url, isolation_level="AUTOCOMMIT", pool_pre_ping=True)
    try:
        with tmp.connect() as conn:
            exists = conn.execute(text("SELECT 1 FROM sys.databases WHERE name = :n"), {"n": db_name}).first()
            if not exists:
                safe = db_name.replace("]", "]]")
                conn.execute(text(f"CREATE DATABASE [{safe}]"))
                logger.info("Base de datos SQL Server '%s' creada.", db_name)
    except Exception as exc:  # pragma: no cover - depende del servidor
        logger.warning("No se pudo verificar/crear la base de datos '%s': %s", db_name, exc)
    finally:
        tmp.dispose()


def build_engine(url=None):
    url = url or settings.DATABASE_URL
    url_str = str(url)
    if url_str.startswith("mssql"):
        _ensure_sqlserver_database(url)
        eng = create_engine(
            url,
            pool_size=10,
            max_overflow=20,
            pool_recycle=1800,
            pool_pre_ping=True,
            fast_executemany=True,
        )
    else:
        eng = create_engine(url, connect_args={"check_same_thread": False})

        @event.listens_for(eng, "connect")
        def _sqlite_pragmas(dbapi_conn, _record):  # pragma: no cover - trivial
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            cur.execute("PRAGMA journal_mode=WAL")
            cur.close()

    return eng


engine = build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Sesión de base de datos por petición (inyección de dependencias)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
