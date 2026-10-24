"""
SERVICIO DE CATÁLOGO DE PROGRAMAS

Catálogo persistente en base de datos con nivel de formación (pregrado/posgrado)
y alias para reconocer las distintas formas en que los archivos escriben un
mismo programa (código de 2 letras, abreviaturas, errores de digitación).
"""

import logging
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.messages import AppException
from app.domain.program_seed import (
    NAME_VARIATIONS, NON_ACADEMIC_CODES, OFFICIAL_PROGRAMS, guess_level, normalize,
)
from app.models import ProgramAlias, ProgramCatalog
from app.services.audit_service import log_audit_event

logger = logging.getLogger("uco_analytics.programs")
LEVELS = ("pregrado", "posgrado")


def _add_alias(db: Session, alias: str, program_id: int, known: Dict[str, int]) -> None:
    norm = normalize(alias)
    if norm and norm not in known:
        db.add(ProgramAlias(alias_norm=norm, program_id=program_id))
        known[norm] = program_id


def seed_catalog(db: Session) -> None:
    """Pobla el catálogo con la codificación oficial si está vacío."""
    if db.scalar(select(func.count(ProgramCatalog.id))):
        return
    known: Dict[str, int] = {}
    by_name: Dict[str, ProgramCatalog] = {}
    for code, name in OFFICIAL_PROGRAMS.items():
        prog = by_name.get(name)
        if prog is None:
            prog = ProgramCatalog(code=code, name=name, level=guess_level(name),
                                  is_active=code not in NON_ACADEMIC_CODES)
            db.add(prog)
            db.flush()
            by_name[name] = prog
            _add_alias(db, name, prog.id, known)
        _add_alias(db, code, prog.id, known)
    for variant, target in NAME_VARIATIONS.items():
        prog = by_name.get(target)
        if prog is None:
            prog = ProgramCatalog(name=target, level=guess_level(target))
            db.add(prog)
            db.flush()
            by_name[target] = prog
            _add_alias(db, target, prog.id, known)
        _add_alias(db, variant, prog.id, known)
    db.commit()
    logger.info("Catálogo de programas inicializado con %d programas.", len(by_name))


def alias_map(db: Session) -> Dict[str, int]:
    """alias normalizado -> id de programa (incluye nombres oficiales)."""
    return {a: pid for a, pid in db.execute(select(ProgramAlias.alias_norm, ProgramAlias.program_id))}


def resolve(raw: str, aliases: Dict[str, int]) -> Optional[int]:
    return aliases.get(normalize(raw))


def list_programs(db: Session) -> List[Dict]:
    rows = db.scalars(select(ProgramCatalog).order_by(ProgramCatalog.level, ProgramCatalog.name)).all()
    return [{"id": p.id, "codigo": p.code, "nombre": p.name, "nivel": p.level, "activo": bool(p.is_active)} for p in rows]


def create_program(db: Session, name: str, level: str, code: Optional[str] = None,
                   aliases: Optional[List[str]] = None, actor=None, ip=None, ua=None,
                   commit: bool = True) -> ProgramCatalog:
    name = " ".join(str(name or "").split())
    if len(name) < 2:
        raise AppException("VAL_001", custom_user_message="El nombre del programa es obligatorio.")
    level = (level or guess_level(name)).lower()
    if level not in LEVELS:
        raise AppException("VAL_001", custom_user_message="El nivel debe ser 'pregrado' o 'posgrado'.")
    db.flush()
    known = alias_map(db)
    if normalize(name) in known:
        raise AppException("PROG_002")
    prog = ProgramCatalog(name=name, level=level, code=(code or None))
    db.add(prog)
    db.flush()
    _add_alias(db, name, prog.id, known)
    if code:
        _add_alias(db, code, prog.id, known)
    for a in aliases or []:
        _add_alias(db, a, prog.id, known)
    if commit:
        db.commit()
    if actor is not None:
        log_audit_event(db, "CREAR", "PROGRAMA", prog.id, user=actor, ip_address=ip, user_agent=ua,
                        details=f"Registro del programa '{name}' en el catálogo (nivel {level}).")
    return prog


def update_program(db: Session, program_id: int, name: Optional[str], level: Optional[str],
                   code: Optional[str], is_active: Optional[bool], actor, ip=None, ua=None) -> Dict:
    prog = db.get(ProgramCatalog, program_id)
    if not prog:
        raise AppException("PROG_001")
    before = {"nombre": prog.name, "nivel": prog.level, "codigo": prog.code, "activo": prog.is_active}
    known = alias_map(db)
    if name and name.strip() and name.strip() != prog.name:
        new_name = " ".join(name.split())
        owner = known.get(normalize(new_name))
        if owner is not None and owner != prog.id:
            raise AppException("PROG_002")
        prog.name = new_name
        _add_alias(db, new_name, prog.id, known)
    if level:
        level = level.lower()
        if level not in LEVELS:
            raise AppException("VAL_001", custom_user_message="El nivel debe ser 'pregrado' o 'posgrado'.")
        prog.level = level
    if code is not None:
        prog.code = code.strip().upper() or None
        if prog.code:
            owner = known.get(normalize(prog.code))
            if owner is not None and owner != prog.id:
                raise AppException("PROG_002", custom_user_message=f"El código {prog.code} ya pertenece a otro programa.")
            _add_alias(db, prog.code, prog.id, known)
    if is_active is not None:
        prog.is_active = bool(is_active)
    db.commit()
    after = {"nombre": prog.name, "nivel": prog.level, "codigo": prog.code, "activo": prog.is_active}
    log_audit_event(db, "EDITAR", "PROGRAMA", prog.id, user=actor, ip_address=ip, user_agent=ua,
                    details={"antes": before, "despues": after})
    return {"id": prog.id, "codigo": prog.code, "nombre": prog.name, "nivel": prog.level, "activo": bool(prog.is_active)}


def catalog_version(db: Session) -> str:
    count, last = db.execute(select(func.count(ProgramCatalog.id), func.max(ProgramCatalog.updated_at))).one()
    return f"{count}:{last}"
