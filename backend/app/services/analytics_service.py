"""
SERVICIO DE ANALÍTICA Y SEGUIMIENTO SPADIES
Universidad Católica de Oriente - Sistema Analítico de Deserción

Ejecuta el cómputo de los 5 indicadores oficiales (TDA, TDC, TDPA, TGA, TAI),
búsqueda individual de estudiantes con trayectoria completa y resumen global con clasificación de estados.
"""

import sys
import os
import re
import logging
import pandas as pd
from typing import Dict, Any, List, Optional

from app.core.config import settings
from app.core.messages import AppException
from app.program_codes import translate_program_code, find_document_column, find_program_column
from app.analytics_engine import calculate_spadies_metrics, get_all_dataset_periods, extract_period_from_str, period_index

logger = logging.getLogger("uco_analytics.analytics_service")

def get_extracted_dirs() -> List[str]:
    """Retorna los directorios de datos disponibles dinámicamente."""
    dirs = []
    # 1. Directorio oficial configurado
    if hasattr(settings, 'USER_UPLOADS_DIR') and settings.USER_UPLOADS_DIR and os.path.exists(settings.USER_UPLOADS_DIR):
        dirs.append(settings.USER_UPLOADS_DIR)
    
    # 2. Directorio persistente
    if hasattr(settings, 'PERSISTENT_DIR') and settings.PERSISTENT_DIR:
        p_up = os.path.join(settings.PERSISTENT_DIR, "user_uploads")
        if os.path.exists(p_up) and p_up not in dirs:
            dirs.append(p_up)

    # 3. Junto al ejecutable
    if getattr(sys, 'frozen', False):
        exe_up = os.path.join(os.path.dirname(sys.executable), "user_uploads")
        if os.path.exists(exe_up) and exe_up not in dirs:
            dirs.append(exe_up)

    # 4. En LOCALAPPDATA
    local_app_up = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser("~")), "UCO_Analytics", "user_uploads")
    if os.path.exists(local_app_up) and local_app_up not in dirs:
        dirs.append(local_app_up)

    # 5. En el backend relativo
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    b_up = os.path.join(base_dir, "user_uploads")
    if os.path.exists(b_up) and b_up not in dirs:
        dirs.append(b_up)

    # 6. Carpeta Data si existe
    if hasattr(settings, 'DATA_DIR') and settings.DATA_DIR and os.path.exists(settings.DATA_DIR):
        if settings.DATA_DIR not in dirs:
            dirs.append(settings.DATA_DIR)

    return dirs

# Definición matemática y conceptual oficial del Manual SPADIES 3.0
SPADIES_DEFINITIONS = {
    'Activo': {
        'estado': 'Activo',
        'badge_color': '#047857',
        'bg_color': '#ecfdf5',
        'border_color': '#a7f3d0',
        'icon': '🟢',
        'definicion': 'Estudiante que se encuentra matriculado o que se encontraba matriculado el semestre anterior en un programa académico de pregrado.'
    },
    'Desertor': {
        'estado': 'Desertor',
        'badge_color': '#b91c1c',
        'bg_color': '#fef2f2',
        'border_color': '#fca5a5',
        'icon': '🔴',
        'definicion': 'Estudiante que de manera voluntaria o forzosa no se observa como matriculado por dos o más períodos consecutivos, sin registrar graduación o sin ser retirado por motivos disciplinarios.'
    },
    'Graduado': {
        'estado': 'Graduado',
        'badge_color': '#1d4ed8',
        'bg_color': '#eff6ff',
        'border_color': '#bfdbfe',
        'icon': '🎓',
        'definicion': 'Individuo que ha culminado su ciclo académico y ha obtenido un título de nivel de formación.'
    },
    'Retirado': {
        'estado': 'Retirado',
        'badge_color': '#d97706',
        'bg_color': '#fffbeb',
        'border_color': '#fde68a',
        'icon': '⚠️',
        'definicion': 'Estudiante que se ausenta de un programa académico de una IES en un período por motivos disciplinarios (no académicos).'
    }
}

def get_metrics_for_indicator(indicator: str, programs_filter: Optional[str] = None) -> Dict[str, Any]:
    """Calcula y retorna las series de tiempo para el indicador SPADIES solicitado."""
    selected_list = [p.strip() for p in programs_filter.split(',')] if programs_filter and programs_filter.strip() else None
    metrics = calculate_spadies_metrics(selected_list)
    ind_upper = indicator.upper()

    if ind_upper not in metrics:
        raise AppException("METR_001")

    return {
        "indicator": ind_upper,
        "programs_filter": selected_list or ["TODA LA UNIVERSIDAD"],
        "data": metrics[ind_upper]
    }

def get_student_status_by_cedula(cedula: str) -> Dict[str, Any]:
    """Consulta la trayectoria longitudinal y el estado SPADIES de un estudiante por número de cédula."""
    cedula_str = str(cedula).strip()
    extract_dirs = get_extracted_dirs()

    if not extract_dirs:
        return {
            "found": False,
            "cedula": cedula_str,
            "message": "Aún no se han procesado archivos en el repositorio de cargas."
        }

    history = []
    student_program = None
    graduation_info = None
    is_disciplinarily_withdrawn = False
    all_periods = get_all_dataset_periods()

    # 1. Buscar en Egresados
    processed_egresados = set()
    for extract_dir in extract_dirs:
        for f in sorted(os.listdir(extract_dir)):
            if f.startswith('Egresados') and f.endswith(('.xls', '.xlsx')) and f not in processed_egresados:
                processed_egresados.add(f)
                path = os.path.join(extract_dir, f)
                try:
                    df = pd.read_excel(path)
                    doc_col = find_document_column(df.columns)
                    prog_col = find_program_column(df.columns)
                    if doc_col and prog_col:
                        df['DOC_CLEAN'] = df[doc_col].astype(str).str.strip().str.replace('.0', '', regex=False)
                        match = df[df['DOC_CLEAN'] == cedula_str]
                        if not match.empty:
                            row = match.iloc[0]
                            date_col = [c for c in df.columns if 'fecha' in str(c).lower() or 'grado' in str(c).lower()]
                            degree_date = str(row[date_col[0]]) if date_col else "Registrado"
                            student_program = translate_program_code(str(row[prog_col]))
                            graduation_info = {
                                'archivo': f,
                                'fecha_grado': degree_date,
                                'programa': student_program
                            }
                except Exception:
                    pass

    # 2. Buscar en Matriculados por periodo
    registered_periods = []
    detected_matriculados = []
    processed_matriculados = set()
    for extract_dir in extract_dirs:
        if os.path.exists(extract_dir):
            for f in sorted(os.listdir(extract_dir)):
                if f.startswith('Matriculados') and f.endswith(('.xls', '.xlsx')) and f not in processed_matriculados:
                    processed_matriculados.add(f)
                    p_file = extract_period_from_str(f)
                    if p_file:
                        detected_matriculados.append((p_file, os.path.join(extract_dir, f)))

    # Ordenar cronológicamente
    detected_matriculados = sorted(detected_matriculados, key=lambda x: period_index(x[0]))
    all_periods = [x[0] for x in detected_matriculados] if detected_matriculados else get_all_dataset_periods()

    for p, path in detected_matriculados:
        try:
            df = pd.read_excel(path)
            doc_col = find_document_column(df.columns)
            prog_col = find_program_column(df.columns)
            status_cols = [c for c in df.columns if any(k in str(c).lower() for k in ['estado', 'situacion', 'motivo', 'disciplinario', 'retiro'])]
            if doc_col and prog_col:
                df['DOC_CLEAN'] = df[doc_col].astype(str).str.strip().str.replace('.0', '', regex=False)
                match = df[df['DOC_CLEAN'] == cedula_str]
                if not match.empty:
                    row = match.iloc[0]
                    registered_periods.append(p)
                    prog_name = translate_program_code(str(row[prog_col]))
                    if not student_program:
                        student_program = prog_name
                    for sc in status_cols:
                        val = str(row[sc]).lower()
                        if any(term in val for term in ['disciplinario', 'sancion', 'expulsion', 'disciplina']):
                            is_disciplinarily_withdrawn = True
                    history.append({
                        'periodo': p,
                        'registrado': True,
                        'estado': 'Matriculado',
                        'programa': prog_name
                    })
                else:
                    history.append({
                        'periodo': p,
                        'registrado': False,
                        'estado': 'No Matriculado',
                        'programa': '-'
                    })
        except Exception:
            pass

    if not graduation_info and len(registered_periods) == 0:
        return {
            "found": False,
            "cedula": cedula_str,
            "message": f"No se encontraron registros académicos para el número de cédula {cedula_str}."
        }

    # Evaluar estado SPADIES según manual oficial
    last_two_periods = all_periods[-2:] if len(all_periods) >= 2 else all_periods
    if is_disciplinarily_withdrawn:
        calculated_state = 'Retirado'
    elif any(p in registered_periods for p in last_two_periods):
        calculated_state = 'Activo'
    elif graduation_info:
        calculated_state = 'Graduado'
    else:
        calculated_state = 'Desertor'

    meta = SPADIES_DEFINITIONS[calculated_state]

    return {
        "found": True,
        "cedula": cedula_str,
        "programa": student_program or "Programa UCO",
        "estado_spadies": calculated_state,
        "meta_spadies": meta,
        "graduacion": graduation_info,
        "total_periodos_matriculado": len(registered_periods),
        "ultimo_periodo_registrado": registered_periods[-1] if registered_periods else "N/A",
        "trayectoria": history
    }

def get_student_status_summary(
    status_filter: str = "Todos",
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 50
) -> Dict[str, Any]:
    """Genera el resumen estadístico global por estado SPADIES y retorna el listado filtrado y paginado."""
    extract_dirs = get_extracted_dirs()

    empty_summary = {
        "total_estudiantes": 0,
        "resumen": {
            "Activo": {"cantidad": 0, "porcentaje": "0.00%", "icon": "🟢", "bg": "#ecfdf5", "color": "#047857"},
            "Desertor": {"cantidad": 0, "porcentaje": "0.00%", "icon": "🔴", "bg": "#fef2f2", "color": "#b91c1c"},
            "Graduado": {"cantidad": 0, "porcentaje": "0.00%", "icon": "🎓", "bg": "#eff6ff", "color": "#1d4ed8"},
            "Retirado": {"cantidad": 0, "porcentaje": "0.00%", "icon": "⚠️", "bg": "#fffbeb", "color": "#d97706"}
        },
        "total_filtrados": 0,
        "estudiantes": []
    }

    if not extract_dirs:
        return empty_summary

    # 1. Graduados / Egresados
    graduados = set()
    grad_prog = {}
    processed_egresados = set()
    for extract_dir in extract_dirs:
        if os.path.exists(extract_dir):
            for f in sorted(os.listdir(extract_dir)):
                if (f.startswith('Egresados') or f.startswith('Graduados')) and f.endswith(('.xls', '.xlsx')) and f not in processed_egresados:
                    processed_egresados.add(f)
                    path = os.path.join(extract_dir, f)
                    try:
                        df = pd.read_excel(path)
                        doc_col = find_document_column(df.columns)
                        prog_col = find_program_column(df.columns)
                        if doc_col:
                            df['DOC'] = df[doc_col].astype(str).str.strip().str.replace('.0', '', regex=False)
                            for _, r in df.iterrows():
                                doc = r['DOC']
                                graduados.add(doc)
                                if prog_col:
                                    grad_prog[doc] = translate_program_code(str(r[prog_col]))
                    except Exception:
                        pass

    # 2. Matriculados
    student_periods = {}
    student_prog = {}
    retirados = set()
    detected_matriculados = []
    processed_matriculados = set()

    for extract_dir in extract_dirs:
        if os.path.exists(extract_dir):
            for f in sorted(os.listdir(extract_dir)):
                if f.startswith('Matriculados') and f.endswith(('.xls', '.xlsx')) and f not in processed_matriculados:
                    processed_matriculados.add(f)
                    p_file = extract_period_from_str(f)
                    if p_file:
                        detected_matriculados.append((p_file, os.path.join(extract_dir, f)))

    # Ordenar cronológicamente
    detected_matriculados = sorted(detected_matriculados, key=lambda x: period_index(x[0]))
    all_periods = [x[0] for x in detected_matriculados] if detected_matriculados else get_all_dataset_periods()
    last_two_periods = all_periods[-2:] if len(all_periods) >= 2 else all_periods

    for p, path in detected_matriculados:
        try:
            df = pd.read_excel(path)
            doc_col = find_document_column(df.columns)
            prog_col = find_program_column(df.columns)
            status_cols = [c for c in df.columns if any(k in str(c).lower() for k in ['estado', 'situacion', 'motivo', 'disciplinario', 'retiro'])]
            if doc_col and prog_col:
                df['DOC'] = df[doc_col].astype(str).str.strip().str.replace('.0', '', regex=False)
                df['PROG'] = df[prog_col].apply(translate_program_code)
                for _, r in df.iterrows():
                    doc = r['DOC']
                    pr = r['PROG']
                    if doc not in student_periods:
                        student_periods[doc] = set()
                    student_periods[doc].add(p)
                    student_prog[doc] = pr

                    # Comprobar si registra retiro disciplinario
                    for sc in status_cols:
                        val = str(r[sc]).lower()
                        if any(term in val for term in ['disciplinario', 'sancion', 'expulsion', 'disciplina']):
                            retirados.add(doc)
        except Exception:
            pass

    all_students = set(student_periods.keys()).union(graduados)
    counts = {'Activo': 0, 'Desertor': 0, 'Graduado': 0, 'Retirado': 0}
    full_list = []

    for doc in sorted(list(all_students)):
        pr = student_prog.get(doc) or grad_prog.get(doc) or "Programa UCO"
        p_set = student_periods.get(doc, set())
        
        # Jerarquía SPADIES 3.0:
        # 1. Si tiene retiro disciplinario registrado -> Retirado
        # 2. Si está matriculado en alguno de los últimos dos periodos -> Activo
        # 3. Si no está activo y figura en egresados/graduados -> Graduado
        # 4. Si no está activo ni graduado ni retirado (ausente 2+ periodos) -> Desertor
        if doc in retirados:
            st = 'Retirado'
        elif any(p in p_set for p in last_two_periods):
            st = 'Activo'
        elif doc in graduados:
            st = 'Graduado'
        else:
            st = 'Desertor'

        counts[st] += 1

        full_list.append({
            'cedula': doc,
            'programa': pr,
            'estado': st
        })

    total = len(all_students)
    summary = {
        'Activo': {
            'cantidad': counts['Activo'],
            'porcentaje': f"{(counts['Activo']/total*100):.2f}%" if total > 0 else "0.00%",
            'icon': "🟢", 'bg': "#ecfdf5", 'color': "#047857"
        },
        'Desertor': {
            'cantidad': counts['Desertor'],
            'porcentaje': f"{(counts['Desertor']/total*100):.2f}%" if total > 0 else "0.00%",
            'icon': "🔴", 'bg': "#fef2f2", 'color': "#b91c1c"
        },
        'Graduado': {
            'cantidad': counts['Graduado'],
            'porcentaje': f"{(counts['Graduado']/total*100):.2f}%" if total > 0 else "0.00%",
            'icon': "🎓", 'bg': "#eff6ff", 'color': "#1d4ed8"
        },
        'Retirado': {
            'cantidad': counts['Retirado'],
            'porcentaje': f"{(counts['Retirado']/total*100):.2f}%" if total > 0 else "0.00%",
            'icon': "⚠️", 'bg': "#fffbeb", 'color': "#d97706"
        }
    }

    filtered = full_list
    if status_filter and status_filter.lower() != 'todos':
        filtered = [s for s in filtered if s['estado'].lower() == status_filter.lower()]

    if search and search.strip():
        q = search.strip().lower()
        filtered = [s for s in filtered if q in s['cedula'].lower() or q in s['programa'].lower()]

    start_idx = (page - 1) * limit
    paged_list = filtered[start_idx : start_idx + limit]

    return {
        "total_estudiantes": total,
        "resumen": summary,
        "total_filtrados": len(filtered),
        "page": page,
        "limit": limit,
        "estudiantes": paged_list
    }
