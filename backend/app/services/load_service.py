"""
SERVICIO DE INGESTA Y CONTROL DE PERIODOS ACADÉMICOS
Universidad Católica de Oriente - Sistema Analítico de Deserción

Garantiza la secuencia cronológica estricta (1-2018 a 2-2070), valida estructura
y tipos de datos en archivos Excel/CSV, normaliza códigos oficiales y registra trazabilidad.
"""

import os
import io
import logging
import pandas as pd
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models import DataLoadRecord
from app.core.config import settings
from app.core.messages import AppException
from app.services.audit_service import log_audit_event
from app.program_codes import translate_program_code, is_known_program, find_document_column, find_program_column

logger = logging.getLogger("uco_analytics.loads")

def get_all_loads(db: Session) -> List[Dict[str, Any]]:
    """Obtiene el historial de periodos cargados en el sistema."""
    loads = db.query(DataLoadRecord).order_by(DataLoadRecord.id.desc()).all()
    return [
        {
            "id": l.id,
            "tipo": l.tipo,
            "periodo": l.periodo,
            "archivo_nombre": l.archivo_nombre,
            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else ""
        }
        for l in loads
    ]

def get_next_expected_period(db: Session, tipo: str) -> str:
    """Calcula estrictamente el siguiente periodo cronológico requerido (1-2018 a 2-2070)."""
    loaded = db.query(DataLoadRecord).filter(DataLoadRecord.tipo == tipo).all()
    loaded_periods = set(r.periodo for r in loaded)

    year = 2018
    sem = 1
    while year <= 2070:
        code = f"{sem}-{year}"
        alt_code = f"{year}-{sem}"
        yr_code = str(year)
        if code not in loaded_periods and alt_code not in loaded_periods and yr_code not in loaded_periods:
            return code
        if sem == 1:
            sem = 2
        else:
            sem = 1
            year += 1
    return '2-2070'

def process_file_upload(
    db: Session,
    file_bytes: bytes,
    filename: str,
    tipo: str,
    periodo: str,
    confirm_new_program: bool = False,
    actor_username: Optional[str] = "Administrador",
    actor_role: Optional[str] = "administrador",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Dict[str, Any]:
    """Procesa, valida e indexa un archivo Excel o CSV de matrícula o graduación."""
    periodo_clean = periodo.strip()
    expected_period = get_next_expected_period(db, tipo)

    if periodo_clean != expected_period:
        raise AppException(
            "DATA_001",
            custom_user_message=f"Secuencia cronológica incorrecta. El periodo a cargar para {tipo} debe ser estrictamente '{expected_period}'."
        )

    # Validar si ya existe este periodo cargado
    existing = db.query(DataLoadRecord).filter(
        DataLoadRecord.tipo == tipo,
        DataLoadRecord.periodo == periodo_clean
    ).first()
    if existing:
        raise AppException(
            "DATA_002",
            custom_user_message=f"El periodo {periodo_clean} para {tipo} ya se encuentra cargado. Debe eliminarlo en el historial si desea re-cargarlo."
        )

    # Lectura del DataFrame
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise AppException("DATA_003")
    except AppException:
        raise
    except Exception as e:
        raise AppException("DATA_003", technical_detail=f"Error parseando archivo: {str(e)}")

    # 1. Validación de columnas obligatorias
    doc_col = find_document_column(df.columns)
    prog_col = find_program_column(df.columns)

    if not doc_col:
        raise AppException("DATA_004", custom_user_message=f"Estructura inválida: El archivo '{filename}' no contiene la columna obligatoria de Documento de Identificación.")

    if not prog_col:
        raise AppException("DATA_005", custom_user_message=f"Estructura inválida: El archivo '{filename}' no contiene la columna obligatoria de Programa Académico.")

    if tipo == 'graduados':
        date_cols = [c for c in df.columns if 'fecha' in str(c).lower() or 'grado' in str(c).lower()]
        if not date_cols:
            raise AppException("DATA_006", custom_user_message=f"Estructura inválida: El archivo de Egresados/Graduados no contiene la columna de Fecha/Hora de Grado.")

    # 2. Validación de tipo de dato numérico en cédula
    invalid_rows = []
    for idx, val in enumerate(df[doc_col], start=2):
        val_str = str(val).strip().replace('.0', '')
        if val_str and val_str.lower() != 'nan':
            if not val_str.isdigit():
                invalid_rows.append(f"Fila {idx}: '{val}'")
                if len(invalid_rows) >= 5:
                    break

    if invalid_rows:
        details_str = ", ".join(invalid_rows)
        raise AppException(
            "DATA_007",
            custom_user_message=f"Error de tipo de dato: La columna de Documento de Identificación debe contener únicamente números dígitos. Filas con errores: {details_str}."
        )

    # 3. Detección y validación de programa académico / nuevo programa
    unrecognized_programs = set()
    for raw_p in df[prog_col].dropna():
        p_str = str(raw_p).strip()
        if p_str and not is_known_program(p_str):
            unrecognized_programs.add(p_str)

    if unrecognized_programs and not confirm_new_program:
        new_prog_name = list(unrecognized_programs)[0]
        return {
            "status": "new_program_prompt",
            "new_program": new_prog_name,
            "message": f"Se detectó un nuevo programa académico no registrado: '{new_prog_name}'. Requiere confirmación del usuario para ser agregado al directorio de programas de la UCO."
        }

    # Traducir/Normalizar columna de programa
    df[prog_col] = df[prog_col].apply(lambda p: translate_program_code(str(p)))

    # 4. Guardar archivo procesado en USER_UPLOADS_DIR
    user_uploads_dir = settings.USER_UPLOADS_DIR
    os.makedirs(user_uploads_dir, exist_ok=True)

    if tipo == 'matriculados':
        save_filename = f"Matriculados {periodo_clean}.xlsx"
    else:
        save_filename = f"Egresados {periodo_clean}.xlsx"
    
    save_path = os.path.join(user_uploads_dir, save_filename)
    df.to_excel(save_path, index=False)

    total_rows = len(df)

    # Registrar en base de datos
    new_load = DataLoadRecord(tipo=tipo, periodo=periodo_clean, archivo_nombre=filename)
    db.add(new_load)
    db.commit()
    db.refresh(new_load)

    # Registrar en auditoría en lenguaje ubicuo institucional
    log_audit_event(
        db=db,
        action="CARGA_DATOS",
        entity="ARCHIVO_DATOS",
        entity_id=str(new_load.id),
        username=actor_username,
        user_name=actor_username,
        user_role=actor_role,
        ip_address=ip_address,
        user_agent=user_agent,
        details=f"Cargue exitoso de archivo de {tipo.capitalize()} para el período académico {periodo_clean} ({total_rows:,} registros procesados desde '{filename}')."
    )

    next_after = get_next_expected_period(db, tipo)

    return {
        "status": "success",
        "message": f"Cargue de {tipo} ({periodo_clean}) procesado exitosamente.",
        "total_rows": total_rows,
        "next_expected_period": next_after,
        "columns": df.columns.tolist()
    }

def delete_load_record(
    db: Session,
    load_id: int,
    actor_username: Optional[str] = "Administrador",
    actor_role: Optional[str] = "administrador",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Dict[str, Any]:
    """Elimina un registro de carga y su archivo físico, permitiendo su re-carga."""
    load_record = db.query(DataLoadRecord).filter(DataLoadRecord.id == load_id).first()
    if not load_record:
        raise AppException("DATA_008")

    # Eliminar archivo físico de user_uploads si existe
    user_uploads_dir = settings.USER_UPLOADS_DIR
    prefix = "Matriculados" if load_record.tipo == 'matriculados' else "Egresados"
    for ext in [".xlsx", ".xls"]:
        target_file = os.path.join(user_uploads_dir, f"{prefix} {load_record.periodo}{ext}")
        if os.path.exists(target_file):
            try:
                os.remove(target_file)
            except Exception as e:
                logger.warning(f"No se pudo eliminar el archivo físico {target_file}: {e}")

    tipo_nombre = load_record.tipo.capitalize()
    per_nombre = load_record.periodo
    arch_nombre = load_record.archivo_nombre

    db.delete(load_record)
    db.commit()

    # Registrar en auditoría en lenguaje ubicuo institucional
    log_audit_event(
        db=db,
        action="PURGA_DATOS",
        entity="ARCHIVO_DATOS",
        entity_id=str(load_id),
        username=actor_username,
        user_name=actor_username,
        user_role=actor_role,
        ip_address=ip_address,
        user_agent=user_agent,
        details=f"Eliminación física del archivo de {tipo_nombre} del período {per_nombre} ('{arch_nombre}'). El período quedó habilitado nuevamente para cargue."
    )

    return {"message": "Cargue eliminado correctamente. Ya puede subir un nuevo archivo para este periodo."}
