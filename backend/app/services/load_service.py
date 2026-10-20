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

def get_next_expected_load(db: Session) -> Dict[str, str]:
    """
    Calcula estrictamente el siguiente archivo requerido en secuencia alternada:
    Matriculados 1-2018 -> Graduados 1-2018 -> Matriculados 2-2018 -> Graduados 2-2018 ...
    Garantiza que no se pueda avanzar a Matriculados de un nuevo semestre sin haber cargado
    previamente los Graduados del semestre en curso.
    """
    loads = db.query(DataLoadRecord).all()
    loaded_matriculados = set(r.periodo for r in loads if r.tipo == 'matriculados')
    loaded_graduados = set(r.periodo for r in loads if r.tipo == 'graduados')

    year = 2018
    sem = 1
    while year <= 2070:
        p_code = f"{sem}-{year}"
        alt_code = f"{year}-{sem}"
        yr_code = str(year)

        has_mat = (p_code in loaded_matriculados or alt_code in loaded_matriculados or yr_code in loaded_matriculados)
        has_grad = (p_code in loaded_graduados or alt_code in loaded_graduados or yr_code in loaded_graduados)

        # 1. Si falta matriculados del periodo actual, se debe cargar matriculados
        if not has_mat:
            return {"tipo": "matriculados", "periodo": p_code}

        # 2. Si ya se cargó matriculados pero falta graduados del mismo periodo, se exige graduados
        if not has_grad:
            return {"tipo": "graduados", "periodo": p_code}

        # Avanzar al siguiente semestre cronológico
        if sem == 1:
            sem = 2
        else:
            sem = 1
            year += 1

    return {"tipo": "matriculados", "periodo": "2-2070"}

def get_next_expected_period(db: Session, tipo: str) -> str:
    """Compatibilidad: retorna el periodo del siguiente paso esperado."""
    next_req = get_next_expected_load(db)
    return next_req["periodo"]

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
    next_load = get_next_expected_load(db)
    expected_tipo = next_load["tipo"]
    expected_period = next_load["periodo"]

    if tipo != expected_tipo or periodo_clean != expected_period:
        tipo_nombre_req = "Matriculados" if expected_tipo == "matriculados" else "Graduados / Egresados"
        tipo_nombre_actual = "Matriculados" if tipo == "matriculados" else "Graduados / Egresados"
        raise AppException(
            "DATA_001",
            custom_user_message=(
                f"Secuencia cronológica estricta: El sistema exige cargar primero '{tipo_nombre_req}' para el período '{expected_period}'. "
                f"Intentaste cargar '{tipo_nombre_actual}' para '{periodo_clean}'. "
                f"Recuerda que para garantizar el cálculo exacto de los indicadores debe alternarse: "
                f"Matriculados t ➔ Graduados t ➔ Matriculados t+1 ➔ Graduados t+1..."
            )
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

    # Validar coherencia del nombre del archivo para Matriculados
    # Debe contener explícitamente el semestre y el año requeridos (ej: "Matriculados 1-2018")
    if tipo == 'matriculados':
        # periodo_clean es ej: '1-2018'
        sem_req, yr_req = periodo_clean.split('-')
        fn_lower = filename.lower()
        has_yr = yr_req in fn_lower
        has_sem = f"{sem_req}-{yr_req}" in fn_lower or f"{sem_req}_{yr_req}" in fn_lower or f"{sem_req} - {yr_req}" in fn_lower or f"{yr_req}-{sem_req}" in fn_lower or f"matriculados {sem_req}" in fn_lower

        if not (has_yr and has_sem):
            raise AppException(
                "DATA_001",
                custom_user_message=(
                    f"⚠️ Inconsistencia en el nombre del archivo de Matriculados:\n\n"
                    f"El sistema requiere cargar el período '{periodo_clean}', pero el archivo seleccionado se llama '{filename}'.\n\n"
                    f"👉 El nombre del archivo debe contener claramente el semestre y el año correspondiente, "
                    f"por ejemplo: 'Matriculados {periodo_clean}.xlsx' o 'Matriculados_{periodo_clean}.xlsx'."
                )
            )

    # 1. Validación de columnas obligatorias
    cols_found = [str(c).strip() for c in df.columns]
    cols_preview = ", ".join([f"'{c}'" for c in cols_found[:8]])
    if len(cols_found) > 8:
        cols_preview += f" ... y {len(cols_found) - 8} columnas más"

    doc_col = find_document_column(df.columns)
    prog_col = find_program_column(df.columns)

    missing_errors = []

    if not doc_col:
        missing_errors.append(
            f"❌ Columna de Documento de Identificación ausente: El sistema no detectó ninguna columna de número de cédula/documento "
            f"(nombres esperados como: 'Documento', 'Número Documento', 'Cédula', 'Identificación')."
        )

    if not prog_col:
        missing_errors.append(
            f"❌ Columna de Programa Académico ausente: El sistema no detectó ninguna columna correspondiente a la carrera/programa "
            f"(nombres esperados como: 'Programa', 'Nombre Programa', 'Cod Programa')."
        )

    date_cols = []
    if tipo == 'graduados':
        date_cols = [c for c in df.columns if 'fecha' in str(c).lower() or 'grado' in str(c).lower()]
        if not date_cols:
            missing_errors.append(
                f"❌ Columna de Fecha de Grado ausente: Para el archivo de Graduados/Egresados se exige una columna con la fecha u hora de grado "
                f"(nombres esperados como: 'Fecha Grado', 'Fecha de Grado', 'Grado')."
            )

    if missing_errors:
        err_msg = (
            f"⚠️ Estructura incorrecta en el archivo '{filename}':\n\n"
            + "\n".join(missing_errors) + "\n\n"
            + f"📌 Columnas encontradas actualmente en tu archivo ({len(cols_found)} columnas):\n[{cols_preview}].\n\n"
            + "👉 Por favor revisa el encabezado de tu hoja Excel y asegúrate de que contenga las columnas requeridas."
        )
        raise AppException("DATA_004", custom_user_message=err_msg)

    # Validación de fechas de graduación para Egresados/Graduados acorde al periodo requerido
    if tipo == 'graduados' and date_cols:
        target_date_col = date_cols[0]
        sem_req, yr_req = periodo_clean.split('-')
        expected_year = int(yr_req)
        expected_sem = int(sem_req) # 1: enero a junio (meses 1 a 6), 2: julio a diciembre (meses 7 a 12)

        mismatched_dates = []
        for row_idx, raw_val in enumerate(df[target_date_col], start=2):
            if pd.isna(raw_val) or str(raw_val).strip() == '':
                continue
            
            parsed_dt = None
            try:
                parsed_dt = pd.to_datetime(raw_val, errors='coerce', dayfirst=True)
            except Exception:
                pass

            if pd.notna(parsed_dt):
                row_year = parsed_dt.year
                row_sem = 1 if parsed_dt.month <= 6 else 2
                if row_year != expected_year or row_sem != expected_sem:
                    date_str = parsed_dt.strftime('%d/%m/%Y')
                    mismatched_dates.append(f"Fila {row_idx}: fecha '{date_str}' (corresponde a {row_sem}-{row_year})")
                    if len(mismatched_dates) >= 5:
                        break

        if mismatched_dates:
            sem_name = "primer semestre (enero a junio)" if expected_sem == 1 else "segundo semestre (julio a diciembre)"
            err_dates = "\n👉 " + "\n👉 ".join(mismatched_dates)
            raise AppException(
                "DATA_006",
                custom_user_message=(
                    f"⚠️ Inconsistencia en las fechas de graduación del archivo '{filename}':\n\n"
                    f"El sistema está cargando Egresados del período '{periodo_clean}', por lo que todas las fechas de grado deben pertenecer al {sem_name} de {expected_year}.\n\n"
                    f"Se detectaron registros con fechas fuera de este rango:{err_dates}\n\n"
                    f"👉 Por favor verifica que estés subiendo el archivo de egresados correspondiente a {periodo_clean}."
                )
            )

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
            custom_user_message=(
                f"⚠️ Error de tipo de datos en la columna de Documento ('{doc_col}') del archivo '{filename}':\n\n"
                f"Se requiere que todos los números de documento sean exclusivamente valores numéricos dígitos (sin letras, puntos, espacios o símbolos).\n"
                f"Primeros registros no válidos detectados:\n👉 {details_str}.\n\n"
                f"Por favor corrige estos datos en el Excel y vuelve a subir el archivo."
            )
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
