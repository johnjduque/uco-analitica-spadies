from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

# -------------------------------------------------------------------
# MODELO DE USUARIOS Y ROLES
# -------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False) # Cédula
    nombre = Column(String(150), default="", nullable=False)                # Nombre completo
    password = Column(String(255), nullable=False)                          # Hash Bcrypt / PBKDF2
    role = Column(String(50), default="consultor", nullable=False)          # 'administrador' o 'consultor'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Alias de compatibilidad
    @property
    def email(self):
        return self.username

    @property
    def name(self):
        return self.nombre


# -------------------------------------------------------------------
# MODELO DE HISTORIAL Y AUDITORÍA DE CAMBIOS (AUDIT TRAIL)
# -------------------------------------------------------------------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    user_id = Column(Integer, nullable=True)
    username = Column(String(100), index=True, nullable=True)              # Cédula o identificador
    user_name = Column(String(150), nullable=True)                         # Nombre de quien ejecutó la acción
    user_role = Column(String(50), nullable=True)                          # Rol al momento de la acción
    action = Column(String(50), index=True, nullable=False)                # CREAR, EDITAR, ELIMINAR, CARGAR, PURGAR, LOGIN
    entity = Column(String(100), index=True, nullable=False)               # USUARIO, PERIODO, ARCHIVO_DATOS, PARAMETRO
    entity_id = Column(String(100), nullable=True)                         # ID o código del registro afectado
    ip_address = Column(String(50), nullable=True)                         # Dirección IP del cliente
    user_agent = Column(String(255), nullable=True)                        # Navegador / Dispositivo (PC/Móvil)
    details = Column(Text, nullable=True)                                  # Descripción y valores antes/después (JSON o texto)


# -------------------------------------------------------------------
# MODELO DE CATÁLOGO DE PARÁMETROS DEL SISTEMA
# -------------------------------------------------------------------
class SystemParameter(Base):
    __tablename__ = "system_parameters"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)     # Clave única (ej. SPADIES_ABSENCE_TERMS)
    value = Column(String(255), nullable=False)                            # Valor actual
    default_value = Column(String(255), nullable=True)                     # Valor por defecto
    description = Column(String(255), nullable=False)                      # Explicación del parámetro
    category = Column(String(50), default="GENERAL")                       # SPADIES, SEGURIDAD, SISTEMA
    data_type = Column(String(20), default="STRING")                       # STRING, INTEGER, BOOLEAN, FLOAT
    is_editable = Column(Boolean, default=True)                            # Si el administrador puede editarlo desde UI
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100), nullable=True)                        # Último usuario que modificó el parámetro


# -------------------------------------------------------------------
# MODELO DE REGISTRO DE CARGAS DE DATOS (HISTORIAL DE CARGAS)
# -------------------------------------------------------------------
class DataLoadRecord(Base):
    __tablename__ = "data_loads"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)                              # 'matriculados' o 'graduados'
    periodo = Column(String(50), nullable=False)                           # Ej: '2024-1' o '2-2024'
    archivo_nombre = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# -------------------------------------------------------------------
# MODELOS ANALÍTICOS SPADIES (INSTITUCIÓN, PROGRAMAS, ESTUDIANTES)
# -------------------------------------------------------------------
class AcademicPeriod(Base):
    __tablename__ = "academic_periods"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)     # ej. 2018-1, 2018-2
    year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    loaded_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=True)


class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    programs = relationship("Program", back_populates="faculty")


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True, nullable=False)
    level = Column(String(50), nullable=False, default="Pregrado")
    faculty_id = Column(Integer, ForeignKey("faculties.id"), nullable=True)

    faculty = relationship("Faculty", back_populates="programs")
    students = relationship("Student", back_populates="program")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(20), default="CC")
    document_number = Column(String(50), index=True, nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)

    program = relationship("Program", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student")
    graduations = relationship("Graduate", back_populates="student")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    period_code = Column(String(20), index=True, nullable=False)
    is_new_admission = Column(Boolean, default=False)
    is_reentry = Column(Boolean, default=False)
    cohort_code = Column(String(20), index=True, nullable=False)

    student = relationship("Student", back_populates="enrollments")


class Graduate(Base):
    __tablename__ = "graduates"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    period_code = Column(String(20), index=True, nullable=False)
    graduation_date = Column(String(50), nullable=True)

    student = relationship("Student", back_populates="graduations")
