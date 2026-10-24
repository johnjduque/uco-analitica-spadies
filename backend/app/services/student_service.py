"""
SERVICIO DE CONSULTA DE ESTUDIANTES

Resumen por estado SPADIES (Activo, Desertor, Graduado) y trayectoria individual.
"""

from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.messages import AppException
from app.domain import periods as P
from app.domain.indicators import STATE_DEFINITIONS
from app.models import EnrollmentRecord, GraduateRecord, NewStudentRecord, ProgramCatalog
from app.services import indicator_service

ESTADOS = ("Activo", "Desertor", "Graduado")


def summary(db: Session, nivel: str = "pregrado", estado: str = "Todos", buscar: Optional[str] = None,
            programas: Optional[List[str]] = None, page: int = 1, limit: int = 25) -> Dict:
    nivel = (nivel or "pregrado").lower()
    if nivel not in indicator_service.NIVELES:
        raise AppException("METR_001")
    states, last = indicator_service.students_classification(db, nivel)
    allowed = set(programas) if programas else None
    items = [(doc, d) for doc, d in states.items() if allowed is None or d["programa"] in allowed]
    counts = {e: 0 for e in ESTADOS}
    for _, d in items:
        counts[d["estado"]] += 1
    total = len(items)
    resumen = {e: {"cantidad": counts[e], "porcentaje": round(100 * counts[e] / total, 2) if total else 0.0}
               for e in ESTADOS}

    filtered = items
    if estado and estado.lower() != "todos":
        filtered = [(doc, d) for doc, d in filtered if d["estado"].lower() == estado.lower()]
    if buscar and buscar.strip():
        q = buscar.strip().lower()
        filtered = [(doc, d) for doc, d in filtered if q in doc.lower() or q in (d["programa"] or "").lower()]
    filtered.sort(key=lambda x: x[0])
    start = (page - 1) * limit
    page_items = [{"documento": doc, "programa": d["programa"], "estado": d["estado"],
                   "ultimo_periodo": d["ultimo_periodo"]} for doc, d in filtered[start:start + limit]]
    return {
        "nivel": nivel,
        "periodo_corte": P.label(last) if last is not None else None,
        "total_estudiantes": total,
        "resumen": resumen,
        "total_filtrados": len(filtered),
        "page": page,
        "limit": limit,
        "estudiantes": page_items,
        "definiciones": STATE_DEFINITIONS,
    }


def detail(db: Session, document: str) -> Dict:
    doc = (document or "").strip().upper()
    if not doc or len(doc) > 30:
        raise AppException("STU_001")

    def fetch(model, extra=()):
        stmt = (select(model.period_idx, ProgramCatalog.name, ProgramCatalog.level, *extra)
                .join(ProgramCatalog, ProgramCatalog.id == model.program_id)
                .where(model.document == doc))
        return db.execute(stmt).all()

    enr = fetch(EnrollmentRecord)
    new = fetch(NewStudentRecord)
    grads = fetch(GraduateRecord, (GraduateRecord.grad_date,))
    if not enr and not grads:
        raise AppException("STU_001")

    states, last = indicator_service.students_classification(db, "todos")
    st = states.get(doc, {"estado": "Graduado" if grads else "Desertor", "programa": None, "ultimo_periodo": None})

    all_idx = [r[0] for r in enr] + [r[0] for r in grads]
    first = min(all_idx)
    end = max(max(all_idx), last if last is not None else first)
    by_period: Dict[int, Dict] = {}
    for idx, prog, level in enr:
        by_period.setdefault(idx, {"programas": [], "nuevo_en": [], "grados": []})["programas"].append(f"{prog} ({level})")
    for idx, prog, level in new:
        by_period.setdefault(idx, {"programas": [], "nuevo_en": [], "grados": []})["nuevo_en"].append(prog)
    for idx, prog, level, gdate in grads:
        by_period.setdefault(idx, {"programas": [], "nuevo_en": [], "grados": []})["grados"].append(
            {"programa": prog, "fecha": gdate.isoformat() if gdate else None})

    trayectoria = []
    for i in range(first, end + 1):
        d = by_period.get(i, {"programas": [], "nuevo_en": [], "grados": []})
        trayectoria.append({"periodo": P.label(i), "matriculado": bool(d["programas"]),
                            "programas": d["programas"], "nuevo_en": d["nuevo_en"], "grados": d["grados"]})
    return {
        "documento": doc,
        "estado": st["estado"],
        "definicion": STATE_DEFINITIONS[st["estado"]],
        "programa": st["programa"] or (grads[-1][1] if grads else None),
        "periodos_matriculado": len({r[0] for r in enr}),
        "ultimo_periodo": P.label(max(r[0] for r in enr)) if enr else None,
        "periodo_corte": P.label(last) if last is not None else None,
        "grados": [{"periodo": P.label(i), "programa": p, "fecha": g.isoformat() if g else None} for i, p, _, g in sorted(grads)],
        "trayectoria": trayectoria,
    }
