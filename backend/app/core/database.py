import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("uco_analytics.database")

# Configurar motor de base de datos según el motor seleccionado
db_url = settings.DATABASE_URL

if settings.DB_ENGINE == "sqlserver":
    logger.info(f"Conectando a Microsoft SQL Server en {settings.SQLSERVER_HOST}:{settings.SQLSERVER_PORT}/{settings.SQLSERVER_DATABASE}")
    engine = create_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
        pool_pre_ping=True
    )
else:
    logger.info(f"Conectando a base de datos local SQLite: {db_url}")
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Generador de sesiones de base de datos para inyección de dependencias."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
