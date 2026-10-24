"""
SINCRONIZACIÓN LIGERA DEL ESQUEMA DE BASE DE DATOS

Crea las tablas nuevas y agrega columnas faltantes a tablas existentes, de forma
compatible con SQLite y SQL Server. Permite actualizar instalaciones anteriores
(v1/v2) sin perder usuarios ni auditoría.
"""

import logging

from sqlalchemy import inspect, text

from app.core.database import Base

logger = logging.getLogger("uco_analytics.migrations")

# Tablas del esquema v2 que nunca se usaron (siempre vacías); se eliminan si están vacías.
_LEGACY_TABLES = ["enrollments", "graduates", "students", "programs", "faculties", "academic_periods"]


def _drop_empty_legacy_tables(engine) -> None:
    insp = inspect(engine)
    existing = set(insp.get_table_names())
    for table in _LEGACY_TABLES:
        if table not in existing:
            continue
        try:
            with engine.begin() as conn:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                if count == 0:
                    conn.execute(text(f"DROP TABLE {table}"))
                    logger.info("Tabla heredada vacía eliminada: %s", table)
        except Exception as exc:
            logger.warning("No se pudo eliminar la tabla heredada %s: %s", table, exc)


def _add_missing_columns(engine) -> None:
    insp = inspect(engine)
    existing_tables = set(insp.get_table_names())
    dialect = engine.dialect
    for table in Base.metadata.sorted_tables:
        if table.name not in existing_tables:
            continue
        current = {c["name"] for c in insp.get_columns(table.name)}
        for column in table.columns:
            if column.name in current:
                continue
            col_type = column.type.compile(dialect=dialect)
            keyword = "ADD" if dialect.name == "mssql" else "ADD COLUMN"
            ddl = f"ALTER TABLE {table.name} {keyword} {column.name} {col_type} NULL"
            with engine.begin() as conn:
                conn.execute(text(ddl))
            logger.info("Columna agregada: %s.%s", table.name, column.name)


def sync_schema(engine) -> None:
    import app.models  # noqa: F401  (registra los modelos en Base.metadata)

    _drop_empty_legacy_tables(engine)
    Base.metadata.create_all(bind=engine)
    _add_missing_columns(engine)
