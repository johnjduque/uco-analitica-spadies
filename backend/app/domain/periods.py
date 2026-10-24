"""
PERIODOS ACADÉMICOS

Formato canónico: 'AAAA-S' (ej. '2018-1'), el mismo que usa SPADIES.
Índice entero: año*2 + (semestre-1), consecutivo entre semestres.
Se aceptan también las formas '1-2018', '1_2018', '2018_1' y '2018' (año, solo egresados).
"""

import re
from datetime import date, datetime
from typing import Optional, Tuple

_SEM_FIRST = re.compile(r"^\s*([12])\s*[-_ ]\s*((?:19|20)\d{2})\s*$")
_YEAR_FIRST = re.compile(r"^\s*((?:19|20)\d{2})\s*[-_ ]\s*([12])\s*$")
_YEAR_ONLY = re.compile(r"^\s*((?:19|20)\d{2})\s*$")
# Para detectar periodos dentro de nombres de archivo
_IN_TEXT_SEM_FIRST = re.compile(r"(?<!\d)([12])\s*[-_ ]\s*((?:19|20)\d{2})(?!\d)")
_IN_TEXT_YEAR_FIRST = re.compile(r"(?<!\d)((?:19|20)\d{2})\s*[-_ ]\s*([12])(?!\d)")
_IN_TEXT_YEAR = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")


def parse_period(value: str) -> Tuple[int, Optional[int]]:
    """Retorna (año, semestre). Semestre es None si se indicó solo el año."""
    s = str(value or "")
    m = _YEAR_FIRST.match(s)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = _SEM_FIRST.match(s)
    if m:
        return int(m.group(2)), int(m.group(1))
    m = _YEAR_ONLY.match(s)
    if m:
        return int(m.group(1)), None
    raise ValueError(f"Periodo no válido: '{value}'. Use el formato AAAA-S (ej. 2018-1) o AAAA para egresados anuales.")


def to_index(year: int, semester: int) -> int:
    return year * 2 + (semester - 1)


def from_index(idx: int) -> Tuple[int, int]:
    return idx // 2, idx % 2 + 1


def label(idx: int) -> str:
    y, s = from_index(idx)
    return f"{y}-{s}"


def canonical(value: str) -> str:
    y, s = parse_period(value)
    return str(y) if s is None else f"{y}-{s}"


def index_of(value: str) -> int:
    y, s = parse_period(value)
    if s is None:
        raise ValueError("Se esperaba un periodo semestral (AAAA-S).")
    return to_index(y, s)


def semester_of_date(d: date) -> int:
    """Enero–junio = semestre 1; julio–diciembre = semestre 2."""
    return 1 if d.month <= 6 else 2


def index_of_date(d: date) -> int:
    return to_index(d.year, semester_of_date(d))


def periods_in_text(text: str) -> set:
    """Periodos explícitos (AAAA-S) o años que aparecen en un nombre de archivo."""
    found = set()
    t = str(text or "")
    for m in _IN_TEXT_YEAR_FIRST.finditer(t):
        found.add(f"{m.group(1)}-{m.group(2)}")
    for m in _IN_TEXT_SEM_FIRST.finditer(t):
        found.add(f"{m.group(2)}-{m.group(1)}")
    if not found:
        for m in _IN_TEXT_YEAR.finditer(t):
            found.add(m.group(1))
    return found


_DATE_FORMATS = (
    "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d",
    "%d/%m/%Y", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d-%m-%Y", "%d.%m.%Y",
)


def parse_date(value) -> Optional[date]:
    """
    Interpreta fechas de grado sin ambigüedad:
    - Valores de fecha nativos de Excel se usan tal cual.
    - Texto ISO (AAAA-MM-DD) siempre se lee como año-mes-día.
    - Texto con el día primero (DD/MM/AAAA) se lee con el día primero.
    - Números (serial de Excel) se convierten desde 1899-12-30.
    """
    if value is None:
        return None
    try:
        import pandas as pd
        if pd.isna(value):
            return None
        if isinstance(value, pd.Timestamp):
            return value.date()
    except Exception:
        pass
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)):
        if 20000 < float(value) < 80000:
            from datetime import timedelta
            return date(1899, 12, 30) + timedelta(days=int(value))
        return None
    s = str(value).strip()
    if not s:
        return None
    s = s.replace("T", " ").split(".")[0] if re.match(r"^\d{4}-\d{2}-\d{2}T", s) else s
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    return None
