import sys
import os
import re
import pandas as pd
from app.program_codes import translate_program_code, find_document_column, find_program_column
from app.core.config import settings

def get_extracted_dirs():
    """Retorna los directorios donde residen los archivos cargados por el usuario."""
    dirs = []
    # 1. Directorio configurado oficial
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
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    b_up = os.path.join(base_dir, "user_uploads")
    if os.path.exists(b_up) and b_up not in dirs:
        dirs.append(b_up)

    # 6. Carpeta Data si existe
    if hasattr(settings, 'DATA_DIR') and settings.DATA_DIR and os.path.exists(settings.DATA_DIR):
        if settings.DATA_DIR not in dirs:
            dirs.append(settings.DATA_DIR)

    return dirs

def extract_period_from_str(text: str) -> str:
    """Extrae el código de periodo semestral (ej: 1-2018) desde un nombre de archivo o texto"""
    if not text:
        return None
    match = re.search(r'([12])\s*[-_]\s*(20\d{2})', str(text))
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    match_rev = re.search(r'(20\d{2})\s*[-_]\s*([12])', str(text))
    if match_rev:
        return f"{match_rev.group(2)}-{match_rev.group(1)}"
    match_yr = re.search(r'(20\d{2})', str(text))
    if match_yr:
        return f"1-{match_yr.group(1)}" # Por defecto semestre 1 si solo se especifica el año
    return None

def period_index(period_str: str) -> int:
    """Retorna un ordinal entero para comparar periodos de forma cronológica (ej: 1-2018 -> 2018*2+1)"""
    if not period_str:
        return 999999
    p_clean = str(period_str).strip()
    if '-' in p_clean:
        parts = p_clean.split('-')
        if len(parts[0]) == 4: # e.g. 2018-1
            yr, sem = int(parts[0]), int(parts[1])
        else: # e.g. 1-2018
            sem, yr = int(parts[0]), int(parts[1])
        return yr * 2 + sem
    elif p_clean.isdigit():
        return int(p_clean) * 2 + 1
    return 999999

def get_all_dataset_periods():
    """Obtiene dinámicamente la lista ordenada cronológicamente de todos los periodos efectivamente cargados por el usuario."""
    detected_periods = set()
    for ext_dir in get_extracted_dirs():
        if os.path.exists(ext_dir):
            for f in os.listdir(ext_dir):
                if (f.startswith('Matriculados') or f.startswith('Egresados') or f.startswith('Graduados')) and f.endswith(('.xls', '.xlsx')):
                    p = extract_period_from_str(f)
                    if p:
                        detected_periods.add(p)
    return sorted(list(detected_periods), key=period_index)

def is_period_on_or_before(p_grad: str, p_target: str) -> bool:
    """Evalúa si la graduación ocurrió en o antes del periodo objetivo"""
    if not p_grad:
        return False
    return period_index(p_grad) <= period_index(p_target)

def load_all_dataset(selected_programs=None):
    """
    Carga todos los registros de Matriculados y Egresados clasificándolos por periodo semestral.
    Si selected_programs es especificado (lista de nombres de programas),
    se realiza el filtrado respectivo por programa. Si es None o está vacío o contiene "TODA LA UNIVERSIDAD",
    se evalúa el alcance global de toda la Universidad UCO.
    """
    is_global = not selected_programs or any("TODA" in str(p).upper() for p in selected_programs)
    
    # 1. Cargar Graduados/Egresados por Periodo Semestral
    graduados = set() # set de cédulas
    graduados_by_program = {} # prog -> set(cedulas)
    graduados_period = {} # doc -> p_grad (periodo de graduación más antiguo)
    graduados_by_program_period = {} # (doc, prog) -> p_grad

    processed_files = set()

    for ext_dir in get_extracted_dirs():
        if os.path.exists(ext_dir):
            for f in sorted(os.listdir(ext_dir)):
                if (f.startswith('Egresados') or f.startswith('Graduados')) and f.endswith(('.xls', '.xlsx')) and f not in processed_files:
                    processed_files.add(f)
                    path = os.path.join(ext_dir, f)
                    p_file = extract_period_from_str(f)
                    try:
                        df = pd.read_excel(path)
                        doc_col = find_document_column(df.columns)
                        prog_col = find_program_column(df.columns)
                        date_cols = [c for c in df.columns if 'fecha' in str(c).lower() or 'grado' in str(c).lower()]
                        
                        if doc_col and prog_col:
                            date_col = date_cols[0] if date_cols else None

                            df['DOC'] = df[doc_col].astype(str).str.strip().str.replace('.0', '', regex=False)
                            df['PROG'] = df[prog_col].apply(translate_program_code)
                            
                            for _, row in df.iterrows():
                                doc = row['DOC']
                                prog = row['PROG']
                                
                                p_row = p_file
                                if date_col and pd.notna(row[date_col]):
                                    p_row_ext = extract_period_from_str(str(row[date_col]))
                                    if p_row_ext:
                                        p_row = p_row_ext
                                
                                if not p_row:
                                    p_row = '1-2018'

                                graduados.add(doc)
                                if prog not in graduados_by_program:
                                    graduados_by_program[prog] = set()
                                graduados_by_program[prog].add(doc)

                                if doc not in graduados_period or period_index(p_row) < period_index(graduados_period[doc]):
                                    graduados_period[doc] = p_row

                                key = (doc, prog)
                                if key not in graduados_by_program_period or period_index(p_row) < period_index(graduados_by_program_period[key]):
                                    graduados_by_program_period[key] = p_row
                    except Exception:
                        pass

    # 2. Cargar Matriculados por Periodo
    all_periods = get_all_dataset_periods()
    enrollments = {p: [] for p in all_periods}
    students_first_period = {} # doc -> {period: p, prog: prog}
    students_first_period_by_prog = {} # (doc, prog) -> period

    processed_matriculados = set()
    for ext_dir in get_extracted_dirs():
        if os.path.exists(ext_dir):
            for f in sorted(os.listdir(ext_dir)):
                if f.startswith('Matriculados') and f.endswith(('.xls', '.xlsx')) and f not in processed_matriculados:
                    processed_matriculados.add(f)
                    p = extract_period_from_str(f)
                    if not p:
                        continue
                    if p not in enrollments:
                        enrollments[p] = []
                    path = os.path.join(ext_dir, f)
                    try:
                        df = pd.read_excel(path)
                        doc_col = find_document_column(df.columns)
                        prog_col = find_program_column(df.columns)
                        if doc_col and prog_col:
                            df['DOC'] = df[doc_col].astype(str).str.strip().str.replace('.0', '', regex=False)
                            df['PROG'] = df[prog_col].apply(translate_program_code)

                            for _, row in df.iterrows():
                                doc = row['DOC']
                                prog = row['PROG']

                                # Filtrar si no es global
                                if not is_global and selected_programs:
                                    if prog not in selected_programs:
                                        continue

                                enrollments[p].append({'doc': doc, 'prog': prog})

                                if doc not in students_first_period:
                                    students_first_period[doc] = {'period': p, 'prog': prog}

                                if (doc, prog) not in students_first_period_by_prog:
                                    students_first_period_by_prog[(doc, prog)] = p
                    except Exception:
                        pass

    return {
        'all_periods': all_periods,
        'is_global': is_global,
        'graduados': graduados,
        'graduados_by_program': graduados_by_program,
        'graduados_period': graduados_period,
        'graduados_by_program_period': graduados_by_program_period,
        'enrollments': enrollments,
        'students_first_period': students_first_period,
        'students_first_period_by_prog': students_first_period_by_prog
    }

def calculate_spadies_metrics(selected_programs=None):
    """
    Calcula dinámicamente las 5 matrices SPADIES (TDC, TDPA, TDA, TGA, TAI).
    Reglas metodológicas rigurosas implementadas:
    1. Ventana de 10 años / 20 semestres (S1 ... S20).
    2. Exclusión de Graduados: Ningún estudiante graduado se cuenta como desertor ni ausente
       (al graduarse, se borra/anula toda condición previa de deserción).
    3. Seguimiento de Cohorte Multiprograma: Un estudiante en una cohorte de programa A
       se cuenta como desertor en el programa A si se retira, incluso si ingresó a otro programa B.
       En el programa B ingresará como cohorte de B.
    4. Reingreso vs. Nuevo Estudiante: Si un estudiante se retira del mismo programa y reingresa
       antes del quinto semestre (hasta 4 semestres continuos sin matricular), se computa como
       reingreso en su cohorte original (no primíparo nuevo). Si pasan 5 o más semestres, ingresa como nuevo.
    5. TAI (Ausencia Intersemestral): Excluye estrictamente a los nuevos estudiantes (primíparos del periodo actual)
       y a los graduados.
    """
    ds = load_all_dataset(selected_programs)
    all_periods = ds['all_periods']
    
    # Limitar ventana de análisis a 20 semestres (10 años)
    if len(all_periods) > 20:
        all_periods = all_periods[-20:]

    # Ventana de 20 semestres (S1 ... S20)
    SEMESTER_RANGE = range(1, 21)

    # Si no hay periodos cargados, retornar matrices vacías con 20 semestres
    if not all_periods:
        return {
            'TDC': [],
            'TDPA': {f'S{s}': '—' for s in SEMESTER_RANGE},
            'TDA': {'periods': [], 'rows': []},
            'TGA': {f'S{s}': '—' for s in SEMESTER_RANGE},
            'TAI': {'periods': [], 'rows': []}
        }

    is_global = ds['is_global']
    enrollments = ds['enrollments']
    graduados_period = ds['graduados_period']
    graduados_by_program_period = ds['graduados_by_program_period']
    total_graduados_cargados = len(ds['graduados'])

    # Reconstruir las cohortes de primíparos con la regla de Reingreso (antes del 5to semestre sin matricular)
    # y separación por programa si no es global
    # cohort_primiparos: cohorte -> list of dicts: {'doc': doc, 'prog': prog}
    cohort_primiparos = {p: [] for p in all_periods}
    student_program_history = {} # (doc, prog) -> list of periods enrolled

    for p in all_periods:
        current_enrolled = enrollments.get(p, [])
        for entry in current_enrolled:
            doc = entry['doc']
            prog = entry['prog']
            key = (doc, prog)

            if key not in student_program_history:
                student_program_history[key] = [p]
                cohort_primiparos[p].append({'doc': doc, 'prog': prog})
            else:
                prev_p = student_program_history[key][-1]
                student_program_history[key].append(p)
                # Evaluar semestres de ausencia entre matrículas consecutivas
                p_idx_prev = period_index(prev_p)
                p_idx_curr = period_index(p)
                # Cada periodo son 6 meses; la diferencia en semestres es p_idx_curr - p_idx_prev
                diff_semestres = p_idx_curr - p_idx_prev
                # Si estuvo 5 o más semestres por fuera (diff_semestres > 4), ingresa como nuevo estudiante
                if diff_semestres >= 5:
                    cohort_primiparos[p].append({'doc': doc, 'prog': prog})

    # 1. Matriz TDC (Tasa de Deserción por Cohorte) y TGA (Tasa de Graduación)
    tdc_matrix = []
    total_primiparos_by_s = {s_idx: 0 for s_idx in SEMESTER_RANGE}
    total_deserters_by_s = {s_idx: 0 for s_idx in SEMESTER_RANGE}
    total_graduates_by_s = {s_idx: 0 for s_idx in SEMESTER_RANGE}

    for c_idx, cohorte in enumerate(all_periods):
        cohorte_entries = cohort_primiparos[cohorte]
        total_primiparos = len(cohorte_entries)

        row = {'cohorte': cohorte}

        for sem_num in SEMESTER_RANGE:
            target_p_idx = c_idx + (sem_num - 1)
            if target_p_idx >= len(all_periods):
                row[f'S{sem_num}'] = '—'
                continue

            target_period = all_periods[target_p_idx]
            if total_primiparos == 0:
                row[f'S{sem_num}'] = '0.00%'
                continue

            # Semestre 1 de ingreso: por definición SPADIES la deserción es 0.00%
            if sem_num == 1:
                row['S1'] = '0.00%'
                total_primiparos_by_s[1] += total_primiparos
                continue

            deserters_count = 0
            graduates_count = 0

            for entry in cohorte_entries:
                doc = entry['doc']
                prog = entry['prog']

                # Verificar si el estudiante se graduó
                # En alcance institucional o por programa:
                p_grad = graduados_period.get(doc) if is_global else graduados_by_program_period.get((doc, prog))
                
                # Regla 2: Si el estudiante ya se graduó (en o antes de este periodo o en general),
                # SALE COMPLETAMENTE DEL CÁLCULO DE DESERCIÓN (se anula/borra deserción)
                if p_grad and is_period_on_or_before(p_grad, target_period):
                    graduates_count += 1
                    continue

                # Si no está graduado, verificar actividad en los últimos 2 periodos en SU PROGRAMA
                # (o en cualquier programa si es visión global)
                recent_periods = all_periods[max(0, target_p_idx-1): target_p_idx+1]
                was_active = False

                for rp in recent_periods:
                    rp_enrollments = enrollments.get(rp, [])
                    for enr in rp_enrollments:
                        if enr['doc'] == doc:
                            if is_global or enr['prog'] == prog:
                                was_active = True
                                break
                    if was_active:
                        break

                if not was_active:
                    # No activo y no graduado -> se cuenta como desertor de su cohorte
                    deserters_count += 1

            pct_deserters = (deserters_count / total_primiparos) * 100
            row[f'S{sem_num}'] = f"{pct_deserters:.2f}%"

            total_primiparos_by_s[sem_num] += total_primiparos
            total_deserters_by_s[sem_num] += deserters_count
            total_graduates_by_s[sem_num] += graduates_count

        tdc_matrix.append(row)

    # 2. Matriz TDPA (Tasa de Deserción Promedio Acumulada - S1 a S20)
    tdpa_row = {}
    for sem_num in SEMESTER_RANGE:
        denom = total_primiparos_by_s[sem_num]
        if denom > 0:
            pct = (total_deserters_by_s[sem_num] / denom) * 100
            tdpa_row[f'S{sem_num}'] = f"{pct:.2f}%"
        else:
            tdpa_row[f'S{sem_num}'] = '—'

    # 3. Matriz TGA (Tasa de Graduación Acumulada - S1 a S20)
    tga_row = {}
    for sem_num in SEMESTER_RANGE:
        denom = total_primiparos_by_s[sem_num]
        if denom > 0:
            if total_graduados_cargados == 0:
                tga_row[f'S{sem_num}'] = '0.00%'
            else:
                pct = (total_graduates_by_s[sem_num] / denom) * 100
                tga_row[f'S{sem_num}'] = f"{pct:.2f}%"
        else:
            tga_row[f'S{sem_num}'] = '—'

    # 4. Matriz TDA (Tasa de Deserción Anual)
    # TDA_t = (Desertores en t / Matriculados en t-2) * 100
    # Requiere período t-2. Graduados no se cuentan como desertores.
    tda_desercion_vals = []
    tda_retencion_vals = []

    for p_idx, p in enumerate(all_periods):
        if p_idx < 2:
            tda_desercion_vals.append('—')
            tda_retencion_vals.append('—')
            continue

        prev_2_period = all_periods[p_idx - 2]
        base_docs = {e['doc'] for e in enrollments.get(prev_2_period, [])}
        curr_docs = {e['doc'] for e in enrollments.get(p, [])}

        if len(base_docs) == 0:
            tda_desercion_vals.append('0.00%')
            tda_retencion_vals.append('100.00%')
            continue

        deserters = 0
        for doc in base_docs:
            p_grad = graduados_period.get(doc)
            graduated_by_p = is_period_on_or_before(p_grad, p) if p_grad else False
            # Regla de graduación: Si ya se graduó, sale del cálculo de desertores
            if doc not in curr_docs and not graduated_by_p:
                deserters += 1

        tda_pct = (deserters / len(base_docs)) * 100
        ret_pct = max(0.0, 100.0 - tda_pct)

        tda_desercion_vals.append(f"{tda_pct:.2f}%")
        tda_retencion_vals.append(f"{ret_pct:.2f}%")

    tda_matrix = [
        {'tipo': 'TASA DE DESERCIÓN', 'vals': tda_desercion_vals},
        {'tipo': 'TASA DE RETENCIÓN', 'vals': tda_retencion_vals}
    ]

    # 5. Matriz TAI (Tasa de Ausencia Intersemestral)
    # TAI_t = (Ausentes en t / Matriculados en t-1) * 100
    # Regla: NO se tienen en cuenta los nuevos (los primíparos de t no estaban en t-1).
    # Tampoco se cuentan como ausentes los estudiantes que se graduaron.
    tai_ausentismo_vals = []
    tai_retencion_vals = []

    for p_idx, p in enumerate(all_periods):
        if p_idx < 1:
            tai_ausentismo_vals.append('—')
            tai_retencion_vals.append('—')
            continue

        prev_period = all_periods[p_idx - 1]
        base_docs = {e['doc'] for e in enrollments.get(prev_period, [])}
        curr_docs = {e['doc'] for e in enrollments.get(p, [])}

        if len(base_docs) == 0:
            tai_ausentismo_vals.append('0.00%')
            tai_retencion_vals.append('100.00%')
            continue

        absent = 0
        for doc in base_docs:
            p_grad = graduados_period.get(doc)
            graduated_by_p = is_period_on_or_before(p_grad, p) if p_grad else False
            # Si se graduó, no se cuenta como ausente
            if doc not in curr_docs and not graduated_by_p:
                absent += 1

        aus_pct = (absent / len(base_docs)) * 100
        ret_pct = max(0.0, 100.0 - aus_pct)

        tai_ausentismo_vals.append(f"{aus_pct:.2f}%")
        tai_retencion_vals.append(f"{ret_pct:.2f}%")

    tai_matrix = [
        {'tipo': 'TASA DE AUSENTISMO', 'vals': tai_ausentismo_vals},
        {'tipo': 'TASA DE RETENCIÓN', 'vals': tai_retencion_vals}
    ]

    return {
        'TDC': tdc_matrix,
        'TDPA': tdpa_row,
        'TDA': {'periods': all_periods, 'rows': tda_matrix},
        'TGA': tga_row,
        'TAI': {'periods': all_periods, 'rows': tai_matrix}
    }

