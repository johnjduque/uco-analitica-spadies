"""
SERVICIO DE INDICADORES

Obtiene los registros desde la base de datos, aplica los filtros (nivel de
formación, vista de cálculo y programas) y ejecuta el motor de indicadores.
Los resultados se guardan en caché hasta que cambien los datos o el catálogo.
"""

import threading
from collections import OrderedDict
from typing import Dict, List, Optional, Sequence, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.messages import AppException
from app.domain import indicators as engine
from app.models import EnrollmentRecord, GraduateRecord, NewStudentRecord, ProgramCatalog
from app.services import ingestion_service, program_service

NIVELES = ("pregrado", "posgrado", "todos")
_lock = threading.Lock()
_cache: Dict = {"version": None, "datasets": {}, "results": OrderedDict(), "students": {}}
_MAX_RESULTS = 64


def invalidate_cache() -> None:
    with _lock:
        _cache["version"] = None
        _cache["datasets"].clear()
        _cache["results"].clear()
        _cache["students"].clear()


def _version(db: Session) -> str:
    return f"{ingestion_service.data_version(db)}|{program_service.catalog_version(db)}"


def _check_version(db: Session) -> str:
    v = _version(db)
    with _lock:
        if _cache["version"] != v:
            _cache["version"] = v
            _cache["datasets"].clear()
            _cache["results"].clear()
            _cache["students"].clear()
    return v


def _rows(db: Session, model, nivel: str) -> List[Tuple[int, str, str]]:
    stmt = (select(model.period_idx, model.document, ProgramCatalog.name)
            .join(ProgramCatalog, ProgramCatalog.id == model.program_id))
    if nivel != "todos":
        stmt = stmt.where(ProgramCatalog.level == nivel)
    return [tuple(r) for r in db.execute(stmt)]


def dataset(db: Session, nivel: str) -> Dict[str, List]:
    _check_version(db)
    with _lock:
        cached = _cache["datasets"].get(nivel)
    if cached is not None:
        return cached
    ds = {
        "enrollments": _rows(db, EnrollmentRecord, nivel),
        "new_students": _rows(db, NewStudentRecord, nivel),
        "graduates": _rows(db, GraduateRecord, nivel),
    }
    with _lock:
        _cache["datasets"][nivel] = ds
    return ds


def _validate(nivel: str, vista: str) -> Tuple[str, str]:
    nivel = (nivel or "pregrado").lower()
    vista = (vista or "ies").lower()
    if nivel not in NIVELES or vista not in engine.VIEWS:
        raise AppException("METR_001")
    return nivel, vista


def parse_programs(raw: Optional[str]) -> Optional[List[str]]:
    if not raw or not raw.strip():
        return None
    items = [p.strip() for p in raw.split("|") if p.strip()]
    return sorted(set(items)) or None


def compute(db: Session, nivel: str = "pregrado", vista: str = "ies",
            programas: Optional[Sequence[str]] = None) -> Dict:
    nivel, vista = _validate(nivel, vista)
    progs = tuple(sorted(set(programas))) if programas else None
    _check_version(db)
    cache_key = (nivel, vista, progs)
    with _lock:
        hit = _cache["results"].get(cache_key)
        if hit is not None:
            _cache["results"].move_to_end(cache_key)
            return hit
    ds = dataset(db, nivel)
    result = engine.compute_indicators(ds["enrollments"], ds["new_students"], ds["graduates"],
                                       view=vista, programs=list(progs) if progs else None)
    status = ingestion_service.load_status(db)
    result["filtros"] = {"nivel": nivel, "vista": vista, "programas": list(progs) if progs else []}
    result["advertencias"] = status["advertencias"]
    with _lock:
        _cache["results"][cache_key] = result
        while len(_cache["results"]) > _MAX_RESULTS:
            _cache["results"].popitem(last=False)
    return result


def available_programs(db: Session, nivel: str) -> List[Dict]:
    """Programas del nivel que tienen al menos una matrícula cargada."""
    stmt = (select(ProgramCatalog.id, ProgramCatalog.name, ProgramCatalog.level)
            .where(ProgramCatalog.id.in_(select(EnrollmentRecord.program_id).distinct()))
            .order_by(ProgramCatalog.name))
    if nivel != "todos":
        stmt = stmt.where(ProgramCatalog.level == nivel)
    return [{"id": i, "nombre": n, "nivel": l} for i, n, l in db.execute(stmt)]


def students_classification(db: Session, nivel: str):
    _check_version(db)
    with _lock:
        cached = _cache["students"].get(nivel)
    if cached is not None:
        return cached
    ds = dataset(db, nivel)
    result = engine.classify_students(ds["enrollments"], ds["graduates"])
    with _lock:
        _cache["students"][nivel] = result
    return result
