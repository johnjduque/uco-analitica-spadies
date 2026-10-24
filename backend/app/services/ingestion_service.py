"""
SERVICIO DE CARGA E INGESTA DE ARCHIVOS

Tipos de archivo (uno por periodo):
- matriculados: todos los estudiantes matriculados en el semestre.
- nuevos:       estudiantes nuevos (primíparos) del semestre. Definen las cohortes.
- egresados:    graduados. Puede cargarse por semestre (AAAA-S) o por año (AAAA);
                el semestre de cada grado se toma del mes de la fecha de grado.

Reglas de integridad:
- Los periodos de matriculados deben ser consecutivos (sin huecos), hacia adelante
  o hacia atrás, para que los indicadores no confundan un periodo faltante con
  deserción masiva.
- Los nuevos requieren que el periodo de matriculados ya esté cargado.
- Egresados anuales y semestrales del mismo año no pueden coexistir (duplicarían grados).
- Un periodo ya cargado solo se sustituye con la opción "reemplazar".
"""

import csv
import io
import logging
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sqlalchemy import delete, func, insert, select
from sqlalchemy.orm import Session

from app.core.messages import AppException
from app.domain import periods as P
from app.domain.program_seed import guess_level, normalize
from app.models import (
    DataLoadRecord, EnrollmentRecord, GraduateRecord, NewStudentRecord, ProgramCatalog,
)
from app.services import program_service
from app.services.audit_service import iso_utc, log_audit_event

logger = logging.getLogger("uco_analytics.ingestion")

TIPOS = {
    "matriculados": ("Matriculados", EnrollmentRecord),
    "nuevos": ("Matriculados Nuevos", NewStudentRecord),
    "egresados": ("Egresados", GraduateRecord),
}
_DOC_RE = re.compile(r"^[A-Z0-9]{3,20}$")
_THOUSANDS_RE = re.compile(r"^\d{1,3}(\.\d{3})+$")


# -------------------------------------------------------------------
# LECTURA Y DETECCIÓN DE COLUMNAS
# -------------------------------------------------------------------
def _find_columns(headers: List[str]) -> Dict[str, Optional[int]]:
    norm = [normalize(h) for h in headers]
    cols: Dict[str, Optional[int]] = {"doc": None, "tipo_doc": None, "programa": None, "fecha": None}

    for i, h in enumerate(norm):
        if "tipo" in h and ("doc" in h or "ident" in h):
            cols["tipo_doc"] = i
            break

    candidates = [(i, h) for i, h in enumerate(norm) if "tipo" not in h and h]
    rules = [
        lambda h: ("numero" in h or h.startswith("num") or "nro" in h) and ("doc" in h or "ident" in h or "ced" in h),
        lambda h: "cedula" in h,
        lambda h: "identificacion" in h,
        lambda h: "documento" in h,
        lambda h: h in ("numero", "num", "nro", "no", "id"),
    ]
    for rule in rules:
        hit = next((i for i, h in candidates if rule(h)), None)
        if hit is not None:
            cols["doc"] = hit
            break

    prog = [(i, h) for i, h in enumerate(norm) if "programa" in h]
    if prog:
        named = [i for i, h in prog if h == "programa" or "nombre" in h]
        cols["programa"] = named[0] if named else prog[0][0]

    fecha = next((i for i, h in enumerate(norm) if "fecha" in h), None)
    if fecha is None:
        fecha = next((i for i, h in enumerate(norm) if "grado" in h and "programa" not in h and "pregrado" not in h), None)
    cols["fecha"] = fecha
    return cols


def read_table(data: bytes, filename: str) -> Tuple[pd.DataFrame, Dict[str, Optional[int]]]:
    """Lee CSV/XLS/XLSX sin encabezado fijo y ubica la fila de títulos (primeras 15 filas)."""
    name = (filename or "").lower()
    try:
        if name.endswith(".csv"):
            try:
                text = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = data.decode("latin-1")
            try:
                delim = csv.Sniffer().sniff(text[:5000], delimiters=";,\t|").delimiter
            except csv.Error:
                delim = ";" if text.count(";") > text.count(",") else ","
            raw = pd.read_csv(io.StringIO(text), sep=delim, header=None, dtype=str, keep_default_na=False)
        elif name.endswith((".xlsx", ".xlsm")):
            raw = pd.read_excel(io.BytesIO(data), header=None, dtype=object, engine="openpyxl")
        elif name.endswith(".xls"):
            raw = pd.read_excel(io.BytesIO(data), header=None, dtype=object, engine="xlrd")
        else:
            raise AppException("DATA_003")
    except AppException:
        raise
    except Exception as exc:
        raise AppException("DATA_003", technical_detail=f"No se pudo leer '{filename}': {exc}")

    for r in range(min(15, len(raw))):
        headers = ["" if pd.isna(v) else str(v) for v in raw.iloc[r].tolist()]
        cols = _find_columns(headers)
        if cols["doc"] is not None and cols["programa"] is not None:
            df = raw.iloc[r + 1:].reset_index(drop=True)
            df.columns = [h.strip() or f"col_{i}" for i, h in enumerate(headers)]
            return df, cols
    headers = ["" if pd.isna(v) else str(v) for v in (raw.iloc[0].tolist() if len(raw) else [])]
    preview = ", ".join(f"'{h}'" for h in headers[:8] if h)
    raise AppException("DATA_004", custom_user_message=(
        f"No se encontraron las columnas obligatorias en '{filename}'. Se requiere una columna de número de "
        f"documento (ej. 'Número de documento', 'Cédula', 'Identificación') y una de 'Programa'. "
        f"Encabezados encontrados: [{preview}]."))


def clean_document(value: Any) -> Optional[str]:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value)
    s = str(value).strip().upper().replace(" ", "")
    if not s or s in ("NAN", "NONE", "NULL"):
        return None
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]
    if _THOUSANDS_RE.match(s):
        s = s.replace(".", "")
    return s.replace("-", "")


# -------------------------------------------------------------------
# ESTADO DE CARGAS
# -------------------------------------------------------------------
def list_loads(db: Session) -> List[Dict[str, Any]]:
    loads = db.scalars(select(DataLoadRecord).order_by(DataLoadRecord.id.desc())).all()
    return [{"id": l.id, "tipo": l.tipo, "periodo": l.periodo, "archivo_nombre": l.archivo_nombre,
             "registros": l.total_rows, "cargado_por": l.uploaded_by, "created_at": iso_utc(l.created_at)} for l in loads]


def _loaded(db: Session) -> Dict[str, Dict[str, DataLoadRecord]]:
    out: Dict[str, Dict[str, DataLoadRecord]] = {t: {} for t in TIPOS}
    for l in db.scalars(select(DataLoadRecord)).all():
        out.setdefault(l.tipo, {})[l.periodo] = l
    return out


def load_status(db: Session) -> Dict[str, Any]:
    """Tabla de control por periodo y siguiente carga sugerida."""
    loaded = _loaded(db)
    mat = sorted(P.index_of(p) for p in loaded["matriculados"])
    egr = loaded["egresados"]
    rows, warnings = [], []
    suggestion = None
    if mat:
        for i in range(mat[0], mat[-1] + 1):
            lab = P.label(i)
            y, s = P.from_index(i)
            m = loaded["matriculados"].get(lab)
            n = loaded["nuevos"].get(lab)
            e = egr.get(lab) or egr.get(str(y))
            rows.append({
                "periodo": lab,
                "matriculados": m.total_rows if m else None,
                "nuevos": n.total_rows if n else None,
                "egresados": (e.total_rows if e else None),
                "egresados_modo": (None if not e else ("anual" if e.periodo == str(y) else "semestral")),
            })
            if not m:
                warnings.append(f"Falta el archivo de Matriculados del periodo {lab}.")
            if not n:
                warnings.append(f"Falta el archivo de Matriculados Nuevos del periodo {lab}: la cohorte {lab} no se calculará.")
            if not e:
                warnings.append(f"Falta el archivo de Egresados del periodo {lab} (o del año {y}): la graduación quedará subestimada.")
        for r in rows:
            if r["nuevos"] is None and r["matriculados"] is not None:
                suggestion = {"tipo": "nuevos", "periodo": r["periodo"]}
                break
            if r["egresados"] is None:
                suggestion = {"tipo": "egresados", "periodo": r["periodo"]}
                break
        if suggestion is None:
            suggestion = {"tipo": "matriculados", "periodo": P.label(mat[-1] + 1)}
    else:
        suggestion = {"tipo": "matriculados", "periodo": None}
    return {
        "periodos": rows,
        "rango": {"desde": P.label(mat[0]), "hasta": P.label(mat[-1])} if mat else None,
        "siguiente": suggestion,
        "advertencias": warnings,
    }


def data_version(db: Session) -> str:
    count, last = db.execute(select(func.count(DataLoadRecord.id), func.max(DataLoadRecord.id))).one()
    return f"{count}:{last}"


# -------------------------------------------------------------------
# PROCESAMIENTO DE UNA CARGA
# -------------------------------------------------------------------
def _validate_sequence(db: Session, tipo: str, periodo: str, reemplazar: bool) -> Optional[DataLoadRecord]:
    loaded = _loaded(db)
    existing = loaded[tipo].get(periodo)
    if existing and not reemplazar:
        raise AppException("DATA_002", custom_user_message=(
            f"El archivo de {TIPOS[tipo][0]} del periodo {periodo} ya está cargado. "
            f"Si desea sustituirlo, marque la opción 'Reemplazar el archivo existente'."))
    if tipo == "matriculados" and not existing:
        mats = sorted(P.index_of(p) for p in loaded["matriculados"])
        idx = P.index_of(periodo)
        if mats and idx not in (mats[-1] + 1, mats[0] - 1):
            raise AppException("DATA_001", custom_user_message=(
                f"Los periodos de matriculados deben ser consecutivos. Hay cargados de {P.label(mats[0])} a "
                f"{P.label(mats[-1])}; el siguiente permitido es {P.label(mats[-1] + 1)} "
                f"(o {P.label(mats[0] - 1)} para agregar historia anterior)."))
    if tipo == "nuevos" and periodo not in loaded["matriculados"]:
        raise AppException("DATA_001", custom_user_message=(
            f"Primero cargue el archivo de Matriculados del periodo {periodo}; los nuevos deben estar dentro de los matriculados."))
    if tipo == "egresados":
        y, s = P.parse_period(periodo)
        if s is None and any(k in loaded["egresados"] for k in (f"{y}-1", f"{y}-2")):
            raise AppException("DATA_002", custom_user_message=(
                f"Ya hay egresados semestrales cargados para {y}. Elimínelos antes de cargar el archivo anual de {y}."))
        if s is not None and str(y) in loaded["egresados"]:
            raise AppException("DATA_002", custom_user_message=(
                f"Ya está cargado el archivo anual de egresados {y}. Elimínelo antes de cargar egresados semestrales de {y}."))
    return existing


def _resolve_programs(db: Session, raw_programs: Counter, decisions: Dict[str, Dict]) -> Tuple[Dict[str, int], List[Dict]]:
    aliases = program_service.alias_map(db)
    mapping: Dict[str, int] = {}
    pending = []
    for raw, n in raw_programs.items():
        pid = aliases.get(normalize(raw))
        if pid is not None:
            mapping[raw] = pid
            continue
        d = decisions.get(raw) or decisions.get(normalize(raw))
        if d and d.get("accion") == "asociar" and d.get("programa_id"):
            target = db.get(ProgramCatalog, int(d["programa_id"]))
            if not target:
                raise AppException("PROG_001")
            program_service._add_alias(db, raw, target.id, aliases)
            mapping[raw] = target.id
        elif d and d.get("accion") == "crear":
            official = d.get("nombre_oficial") or raw
            prog = program_service.create_program(db, official, d.get("nivel"), commit=False)
            aliases[normalize(official)] = prog.id
            program_service._add_alias(db, raw, prog.id, aliases)
            aliases[normalize(raw)] = prog.id
            mapping[raw] = prog.id
        else:
            pending.append({"nombre": raw, "nivel_sugerido": guess_level(raw), "filas": n})
    return mapping, pending


def process_upload(db: Session, data: bytes, filename: str, tipo: str, periodo: str, reemplazar: bool,
                   decisiones_programas: Optional[List[Dict]], actor, ip=None, ua=None) -> Dict[str, Any]:
    tipo = (tipo or "").strip().lower()
    if tipo not in TIPOS:
        raise AppException("VAL_001", custom_user_message="Tipo de archivo no válido (matriculados, nuevos o egresados).")
    try:
        periodo = P.canonical(periodo)
        year, sem = P.parse_period(periodo)
    except ValueError as exc:
        raise AppException("VAL_001", custom_user_message=str(exc))
    if sem is None and tipo != "egresados":
        raise AppException("VAL_001", custom_user_message="Matriculados y Nuevos se cargan por semestre (AAAA-S).")
    titulo = TIPOS[tipo][0]

    # Coherencia entre el nombre del archivo y el periodo declarado
    in_name = P.periods_in_text(filename)
    if in_name and periodo not in in_name:
        raise AppException("DATA_001", custom_user_message=(
            f"El nombre del archivo '{filename}' indica el periodo {', '.join(sorted(in_name))}, "
            f"pero se está cargando como {titulo} {periodo}. Verifique que sea el archivo correcto."))

    existing = _validate_sequence(db, tipo, periodo, reemplazar)
    df, cols = read_table(data, filename)
    if tipo == "egresados" and cols["fecha"] is None:
        raise AppException("DATA_006", custom_user_message=(
            f"El archivo de egresados '{filename}' debe tener una columna de fecha de grado (ej. 'Fecha y Hora de Grado')."))

    # --- Limpieza de filas ------------------------------------------------
    records, invalid, empty = [], [], 0
    raw_programs: Counter = Counter()
    bad_dates, out_of_range = [], []
    for n_row, row in enumerate(df.itertuples(index=False), start=2):
        doc = clean_document(row[cols["doc"]])
        prog_raw = row[cols["programa"]]
        prog_raw = "" if prog_raw is None or (isinstance(prog_raw, float) and pd.isna(prog_raw)) else " ".join(str(prog_raw).split())
        if not doc and not prog_raw:
            empty += 1
            continue
        if not doc or not _DOC_RE.match(doc):
            invalid.append(f"Fila {n_row}: documento '{row[cols['doc']]}'")
            continue
        if not prog_raw:
            invalid.append(f"Fila {n_row}: programa vacío")
            continue
        rec = {"document": doc, "program_raw": prog_raw}
        if cols["tipo_doc"] is not None and tipo != "egresados":
            t = row[cols["tipo_doc"]]
            rec["doc_type"] = None if t is None or (isinstance(t, float) and pd.isna(t)) else str(t).strip().upper()[:10]
        if tipo == "egresados":
            raw_date = row[cols["fecha"]]
            d = P.parse_date(raw_date)
            if d is None:
                if raw_date is not None and str(raw_date).strip() not in ("", "nan", "NaT", "None"):
                    bad_dates.append(f"Fila {n_row}: '{raw_date}'")
                    continue
                if sem is None:
                    bad_dates.append(f"Fila {n_row}: sin fecha (requerida en el archivo anual)")
                    continue
                idx = P.to_index(year, sem)
            else:
                idx = P.index_of_date(d)
                if d.year != year or (sem is not None and P.semester_of_date(d) != sem):
                    out_of_range.append(f"Fila {n_row}: {d.strftime('%d/%m/%Y')} ({P.label(idx)})")
                    continue
            rec["grad_date"] = d
            rec["period_idx"] = idx
        else:
            rec["period_idx"] = P.to_index(year, sem)
        records.append(rec)
        raw_programs[prog_raw] += 1

    def _fail(code, intro, items):
        raise AppException(code, custom_user_message=intro + "\n👉 " + "\n👉 ".join(items[:5]) +
                           (f"\n… y {len(items) - 5} más." if len(items) > 5 else ""))

    if invalid:
        _fail("DATA_007", f"Hay registros no válidos en '{filename}'. El documento debe tener solo letras y números (3 a 20) y el programa no puede estar vacío:", invalid)
    if bad_dates:
        _fail("DATA_006", f"Hay fechas de grado que no se pudieron interpretar en '{filename}' (use AAAA-MM-DD o DD/MM/AAAA):", bad_dates)
    if out_of_range:
        alcance = f"el año {year}" if sem is None else f"el semestre {periodo} ({'enero-junio' if sem == 1 else 'julio-diciembre'})"
        _fail("DATA_006", f"Hay fechas de grado fuera de {alcance} en '{filename}':", out_of_range)
    if not records:
        raise AppException("DATA_010")

    # --- Programas ----------------------------------------------------------
    decisions = {}
    for d in decisiones_programas or []:
        if d.get("nombre"):
            decisions[d["nombre"]] = d
    mapping, pending = _resolve_programs(db, raw_programs, decisions)
    if pending:
        db.rollback()
        return {"status": "confirmar_programas", "programas": sorted(pending, key=lambda x: -x["filas"]),
                "message": "El archivo contiene programas que no están en el catálogo. Indique si son programas nuevos o variantes de uno existente."}

    # --- Deduplicación --------------------------------------------------------
    seen, rows, dups = set(), [], 0
    for r in records:
        pid = mapping[r["program_raw"]]
        k = (r["document"], pid, r["period_idx"])
        if k in seen:
            dups += 1
            continue
        seen.add(k)
        row = {"period_idx": r["period_idx"], "document": r["document"], "program_id": pid}
        if tipo != "egresados":
            row["doc_type"] = r.get("doc_type")
        else:
            row["grad_date"] = r.get("grad_date")
        rows.append(row)

    # --- Persistencia (transacción única) -----------------------------------
    model = TIPOS[tipo][1]
    try:
        if existing:
            db.execute(delete(model).where(model.load_id == existing.id))
            db.delete(existing)
            db.flush()
        load = DataLoadRecord(tipo=tipo, periodo=periodo, archivo_nombre=filename[:255],
                              total_rows=len(rows), uploaded_by=actor.username)
        db.add(load)
        db.flush()
        for r in rows:
            r["load_id"] = load.id
        for start in range(0, len(rows), 5000):
            db.execute(insert(model), rows[start:start + 5000])
        db.commit()
    except Exception:
        db.rollback()
        raise

    # --- Advertencias informativas ------------------------------------------
    warnings = []
    if empty:
        warnings.append(f"Se omitieron {empty} filas vacías.")
    if dups:
        warnings.append(f"Se omitieron {dups} registros duplicados (mismo documento, programa y periodo).")
    if tipo == "nuevos":
        idx = P.to_index(year, sem)
        enrolled = set(db.scalars(select(EnrollmentRecord.document).where(EnrollmentRecord.period_idx == idx)).all())
        missing = len({r["document"] for r in rows} - enrolled)
        if missing:
            warnings.append(f"{missing} estudiantes nuevos no aparecen en el archivo de Matriculados de {periodo}.")

    log_audit_event(db, "CARGA_DATOS", "ARCHIVO_DATOS", load.id, user=actor, ip_address=ip, user_agent=ua,
                    details=(f"{'Reemplazo' if existing else 'Carga'} de {titulo} {periodo}: {len(rows):,} registros "
                             f"desde '{filename}'."))
    from app.services import indicator_service
    indicator_service.invalidate_cache()
    return {"status": "success", "message": f"{titulo} {periodo} cargado correctamente.",
            "registros": len(rows), "advertencias": warnings, "estado": load_status(db)}


def delete_load(db: Session, load_id: int, actor, ip=None, ua=None) -> Dict[str, Any]:
    load = db.get(DataLoadRecord, load_id)
    if not load:
        raise AppException("DATA_008")
    loaded = _loaded(db)
    if load.tipo == "matriculados":
        mats = sorted(P.index_of(p) for p in loaded["matriculados"])
        idx = P.index_of(load.periodo)
        if len(mats) > 2 and idx not in (mats[0], mats[-1]):
            raise AppException("DATA_001", custom_user_message=(
                f"No se puede eliminar Matriculados {load.periodo} porque dejaría un hueco en la serie. "
                f"Para corregirlo, cárguelo de nuevo con la opción 'Reemplazar el archivo existente'."))
        if load.periodo in loaded["nuevos"]:
            raise AppException("DATA_001", custom_user_message=(
                f"Elimine primero el archivo de Matriculados Nuevos de {load.periodo}."))
    model = TIPOS[load.tipo][1]
    info = f"{TIPOS[load.tipo][0]} {load.periodo} ('{load.archivo_nombre}', {load.total_rows or 0:,} registros)"
    db.execute(delete(model).where(model.load_id == load.id))
    db.delete(load)
    db.commit()
    log_audit_event(db, "PURGA_DATOS", "ARCHIVO_DATOS", load_id, user=actor, ip_address=ip, user_agent=ua,
                    details=f"Eliminación de {info}.")
    from app.services import indicator_service
    indicator_service.invalidate_cache()
    return {"message": "Carga eliminada.", "estado": load_status(db)}
