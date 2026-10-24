"""
MODELOS DE DATOS (SQLAlchemy)

Tablas de seguridad y administración (usuarios, auditoría, parámetros) y tablas
analíticas donde se guardan los registros cargados desde los archivos Excel:
matriculados, primíparos (matriculados nuevos) y graduados.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, String, Text,
)

from app.core.database import Base


def _now():
    return datetime.utcnow()


# -------------------------------------------------------------------
# SEGURIDAD Y ADMINISTRACIÓN
# -------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)   # Cédula o cuenta
    nombre = Column(String(150), default="", nullable=False)
    password = Column(String(255), nullable=False)                            # Hash bcrypt
    role = Column(String(50), default="consultor", nullable=False)            # administrador | consultor
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=False)
    password_changed_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=_now, index=True, nullable=False)
    user_id = Column(Integer, nullable=True)
    username = Column(String(100), index=True, nullable=True)
    user_name = Column(String(150), nullable=True)
    user_role = Column(String(50), nullable=True)
    action = Column(String(50), index=True, nullable=False)
    entity = Column(String(100), index=True, nullable=False)
    entity_id = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)


class SystemParameter(Base):
    __tablename__ = "system_parameters"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(String(255), nullable=False)
    default_value = Column(String(255), nullable=True)
    description = Column(String(255), nullable=False)
    category = Column(String(50), default="GENERAL")
    data_type = Column(String(20), default="STRING")
    is_editable = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=_now, onupdate=_now)
    updated_by = Column(String(100), nullable=True)


# -------------------------------------------------------------------
# CATÁLOGO DE PROGRAMAS (persistente, con nivel de formación)
# -------------------------------------------------------------------
class ProgramCatalog(Base):
    __tablename__ = "program_catalog"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), nullable=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    level = Column(String(20), nullable=False, default="pregrado")             # pregrado | posgrado
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


class ProgramAlias(Base):
    """Variantes de escritura (código, abreviaturas, errores de digitación) que apuntan a un programa."""
    __tablename__ = "program_aliases"

    id = Column(Integer, primary_key=True)
    alias_norm = Column(String(250), unique=True, nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("program_catalog.id", ondelete="CASCADE"), nullable=False)


# -------------------------------------------------------------------
# HISTORIAL DE CARGAS
# -------------------------------------------------------------------
class DataLoadRecord(Base):
    __tablename__ = "data_loads"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)          # matriculados | nuevos | egresados
    periodo = Column(String(50), nullable=False)       # '2018-1' (semestral) o '2018' (egresados anual)
    archivo_nombre = Column(String(255), nullable=False)
    total_rows = Column(Integer, nullable=True)
    uploaded_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=_now)


# -------------------------------------------------------------------
# REGISTROS ANALÍTICOS (una fila por estudiante-programa-periodo)
# -------------------------------------------------------------------
class EnrollmentRecord(Base):
    __tablename__ = "enrollment_records"

    id = Column(Integer, primary_key=True)
    load_id = Column(Integer, ForeignKey("data_loads.id", ondelete="CASCADE"), nullable=False, index=True)
    period_idx = Column(Integer, nullable=False, index=True)       # año*2 + (semestre-1)
    doc_type = Column(String(10), nullable=True)
    document = Column(String(30), nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("program_catalog.id"), nullable=False, index=True)


class NewStudentRecord(Base):
    __tablename__ = "new_student_records"

    id = Column(Integer, primary_key=True)
    load_id = Column(Integer, ForeignKey("data_loads.id", ondelete="CASCADE"), nullable=False, index=True)
    period_idx = Column(Integer, nullable=False, index=True)
    doc_type = Column(String(10), nullable=True)
    document = Column(String(30), nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("program_catalog.id"), nullable=False, index=True)


class GraduateRecord(Base):
    __tablename__ = "graduate_records"

    id = Column(Integer, primary_key=True)
    load_id = Column(Integer, ForeignKey("data_loads.id", ondelete="CASCADE"), nullable=False, index=True)
    period_idx = Column(Integer, nullable=False, index=True)
    document = Column(String(30), nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("program_catalog.id"), nullable=False, index=True)
    grad_date = Column(Date, nullable=True)


Index("ix_enrollment_period_doc", EnrollmentRecord.period_idx, EnrollmentRecord.document)
