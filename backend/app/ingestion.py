import os
import re
import glob
import pandas as pd
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from app import models

# Faculty mapping dictionary for UCO programs
PROGRAM_FACULTY_MAP = {
    "Comercio Exterior": "Ciencias Económicas y Administrativas",
    "Contaduría Pública": "Ciencias Económicas y Administrativas",
    "Administración de Empresas": "Ciencias Económicas y Administrativas",
    "Derecho": "Ciencias Jurídicas",
    "Enfermería": "Ciencias de la Salud",
    "Gerontología": "Ciencias de la Salud",
    "Ingeniería de Sistemas": "Ingeniería",
    "Ingeniería Industrial": "Ingeniería",
    "Ingeniería Electrónica": "Ingeniería",
    "Agronomía": "Ciencias Agropecuarias",
    "Zootecnia": "Ciencias Agropecuarias",
    "Psicología": "Ciencias Sociales",
    "Licenciatura en Educación Física, Recreación y Deportes": "Educación",
    "Licenciatura en educación física, recreación y deportes": "Educación",
    "Licenciatura en Lenguas Extranjeras": "Educación",
    "Licenciatura en lenguas extranjeras": "Educación",
    "Licenciatura en Filosofía": "Educación",
    "Maestría en Educación": "Educación",
    "Teología Virtual": "Teología y Humanidades",
}

def normalize_column_name(col: str) -> str:
    """Normalize Excel header strings to a standard form"""
    s = str(col).strip().lower()
    # Remove accents
    s = s.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    return s

def identify_columns(columns: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Identifies document_number, document_type, program, and graduation_date columns from variant headers"""
    doc_num_col = None
    doc_type_col = None
    program_col = None
    grad_date_col = None

    for col in columns:
        norm = normalize_column_name(col)
        if "grado" in norm or "fecha" in norm:
            grad_date_col = col
        elif "tipo" in norm:
            doc_type_col = col
        elif "programa" in norm:
            program_col = col
        elif any(k in norm for k in ["identificacion", "documento", "numero"]):
            if not doc_num_col:
                doc_num_col = col

    return doc_num_col, doc_type_col, program_col, grad_date_col

def extract_period_from_filename(filename: str) -> Tuple[Optional[str], str]:
    """
    Extracts period code like '2018-1' and file type ('matriculados', 'nuevos', 'egresados') from filename
    """
    base = os.path.basename(filename)
    norm = base.lower()

    # Search for period patterns like 1-2018 or 2-2018
    match = re.search(r'([12])\s*[-_]\s*(20\d{2})', norm)
    if match:
        sem, yr = match.groups()
        period_code = f"{yr}-{sem}"
    else:
        # Search for pattern like 2018-1 or 2018-2
        match_rev = re.search(r'(20\d{2})\s*[-_]\s*([12])', norm)
        if match_rev:
            yr, sem = match_rev.groups()
            period_code = f"{yr}-{sem}"
        else:
            # Search for year pattern like 2018
            match_yr = re.search(r'(20\d{2})', norm)
            period_code = match_yr.group(1) if match_yr else None

    if "nuevo" in norm:
        file_type = "nuevos"
    elif "egresad" in norm or "grado" in norm:
        file_type = "egresados"
    else:
        file_type = "matriculados"

    return period_code, file_type

def get_or_create_faculty(db: Session, faculty_name: str) -> models.Faculty:
    fac = db.query(models.Faculty).filter(models.Faculty.name == faculty_name).first()
    if not fac:
        fac = models.Faculty(name=faculty_name)
        db.add(fac)
        db.commit()
        db.refresh(fac)
    return fac

def get_or_create_program(db: Session, program_name: str) -> models.Program:
    prog_clean = program_name.strip()
    prog = db.query(models.Program).filter(models.Program.name.ilike(prog_clean)).first()
    if not prog:
        level = "Postgrado" if "Maestría" in prog_clean or "Especialización" in prog_clean or "Doctorado" in prog_clean else "Pregrado"
        fac_name = PROGRAM_FACULTY_MAP.get(prog_clean, "Facultad General UCO")
        fac = get_or_create_faculty(db, fac_name)
        prog = models.Program(name=prog_clean, level=level, faculty_id=fac.id)
        db.add(prog)
        db.commit()
        db.refresh(prog)
    return prog

def get_or_create_student(db: Session, doc_type: str, doc_num: str, program_id: int) -> models.Student:
    doc_num_str = str(doc_num).strip()
    student = db.query(models.Student).filter(
        models.Student.document_number == doc_num_str,
        models.Student.program_id == program_id
    ).first()
    
    if not student:
        student = models.Student(
            document_type=doc_type if doc_type else "CC",
            document_number=doc_num_str,
            program_id=program_id
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    return student

def process_excel_file(db: Session, file_path: str) -> Dict:
    """Reads and ingests a single Excel file into the SQLite database"""
    period_code, file_type = extract_period_from_filename(file_path)
    
    df = pd.read_excel(file_path)
    doc_num_col, doc_type_col, program_col, grad_date_col = identify_columns(df.columns)

    if not doc_num_col or not program_col:
        raise ValueError(f"No se pudieron identificar las columnas requeridas en {os.path.basename(file_path)}")

    records_processed = 0
    
    for _, row in df.iterrows():
        doc_num = str(row[doc_num_col]).strip()
        if not doc_num or doc_num.lower() == "nan":
            continue
            
        doc_type = str(row[doc_type_col]).strip() if doc_type_col and pd.notna(row[doc_type_col]) else "CC"
        prog_name = str(row[program_col]).strip()
        if not prog_name or prog_name.lower() == "nan":
            continue

        program = get_or_create_program(db, prog_name)
        student = get_or_create_student(db, doc_type, doc_num, program.id)

        if file_type == "egresados":
            grad_date = str(row[grad_date_col]).strip() if grad_date_col and pd.notna(row[grad_date_col]) else ""
            # Compute period from year if needed
            p_code = period_code if period_code and "-" in period_code else (f"{period_code}-1" if period_code else "2018-1")
            
            existing_grad = db.query(models.Graduate).filter(
                models.Graduate.student_id == student.id,
                models.Graduate.program_id == program.id
            ).first()
            
            if not existing_grad:
                grad = models.Graduate(
                    student_id=student.id,
                    program_id=program.id,
                    period_code=p_code,
                    graduation_date=grad_date
                )
                db.add(grad)
        else:
            # File type matriculados or nuevos
            p_code = period_code if period_code else "2018-1"
            is_new = (file_type == "nuevos")
            
            # Check existing enrollment
            existing_enr = db.query(models.Enrollment).filter(
                models.Enrollment.student_id == student.id,
                models.Enrollment.period_code == p_code
            ).first()

            if not existing_enr:
                enr = models.Enrollment(
                    student_id=student.id,
                    program_id=program.id,
                    period_code=p_code,
                    is_new_admission=is_new,
                    is_reentry=False,
                    cohort_code=p_code # Initial assignment
                )
                db.add(enr)
            elif is_new:
                existing_enr.is_new_admission = True

        records_processed += 1

    db.commit()
    
    # Register or update AcademicPeriod
    if period_code and "-" in period_code:
        yr, sem = period_code.split("-")
        period_obj = db.query(models.AcademicPeriod).filter(models.AcademicPeriod.code == period_code).first()
        if not period_obj:
            period_obj = models.AcademicPeriod(code=period_code, year=int(yr), semester=int(sem), is_processed=True)
            db.add(period_obj)
            db.commit()

    return {"file": os.path.basename(file_path), "records": records_processed, "period": period_code, "type": file_type}

def ingest_all_data_folder(db: Session, data_dir: str) -> Dict:
    """Ingests all .xls files from data_dir into SQLite database"""
    xls_files = glob.glob(os.path.join(data_dir, "*.xls")) + glob.glob(os.path.join(data_dir, "*.xlsx"))
    results = []
    
    for file_path in sorted(xls_files):
        try:
            res = process_excel_file(db, file_path)
            results.append(res)
        except Exception as e:
            results.append({"file": os.path.basename(file_path), "error": str(e)})

    # Post-process cohorts & reentries
    post_process_cohorts(db)
    
    return {"ingested_files_count": len(results), "details": results}

def post_process_cohorts(db: Session):
    """
    Computes true cohorts and re-entry flags based on student enrollment timeline.
    If student absent <= 4 semesters -> Reingreso
    If student absent > 4 semesters -> New cohort / New Admission
    """
    students = db.query(models.Student).all()
    
    for student in students:
        enrollments = db.query(models.Enrollment).filter(
            models.Enrollment.student_id == student.id
        ).order_by(models.Enrollment.period_code.asc()).all()

        if not enrollments:
            continue

        initial_cohort = enrollments[0].period_code
        prev_yr, prev_sem = parse_period_code(initial_cohort)

        for i, enr in enumerate(enrollments):
            curr_yr, curr_sem = parse_period_code(enr.period_code)
            
            if i == 0:
                enr.cohort_code = initial_cohort
                continue

            gap_semesters = (curr_yr - prev_yr) * 2 + (curr_sem - prev_sem) - 1
            
            if gap_semesters > 4:
                # Greater than 4 semesters absent -> New cohort / New Admission
                enr.is_new_admission = True
                enr.is_reentry = False
                enr.cohort_code = enr.period_code
                initial_cohort = enr.period_code
            elif gap_semesters > 0:
                # Between 1 and 4 semesters absent -> Reentry
                enr.is_reentry = True
                enr.cohort_code = initial_cohort
            else:
                enr.cohort_code = initial_cohort

            prev_yr, prev_sem = curr_yr, curr_sem

    db.commit()

def parse_period_code(code: str) -> Tuple[int, int]:
    try:
        parts = code.split("-")
        return int(parts[0]), int(parts[1])
    except Exception:
        return 2018, 1

def check_sequence_continuity(db: Session) -> Dict:
    """
    Checks stored academic periods, identifies gaps in history, and suggests next consecutive period.
    """
    periods_objs = db.query(models.AcademicPeriod).order_by(models.AcademicPeriod.year.asc(), models.AcademicPeriod.semester.asc()).all()
    loaded_periods = [p.code for p in periods_objs]

    if not loaded_periods:
        return {
            "loaded_periods": [],
            "missing_periods": [],
            "recommended_next_period": "2018-1"
        }

    first_yr, first_sem = parse_period_code(loaded_periods[0])
    last_yr, last_sem = parse_period_code(loaded_periods[-1])

    expected_sequence = []
    curr_yr, curr_sem = first_yr, first_sem

    while (curr_yr < last_yr) or (curr_yr == last_yr and curr_sem <= last_sem):
        expected_sequence.append(f"{curr_yr}-{curr_sem}")
        if curr_sem == 1:
            curr_sem = 2
        else:
            curr_sem = 1
            curr_yr += 1

    missing_periods = [p for p in expected_sequence if p not in loaded_periods]

    # Calculate recommended next period
    if last_sem == 1:
        next_period = f"{last_yr}-2"
    else:
        next_period = f"{last_yr + 1}-1"

    return {
        "loaded_periods": loaded_periods,
        "missing_periods": missing_periods,
        "recommended_next_period": next_period
    }
