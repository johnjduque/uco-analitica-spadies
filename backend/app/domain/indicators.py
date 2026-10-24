"""
MOTOR DE INDICADORES DE DESERCIÓN Y PERMANENCIA (metodología SPADIES 3.0)

Funciones puras (sin base de datos) que reciben los registros ya filtrados por
nivel de formación y calculan TDA, TAI, TDC, TDPA y TGA.

Reglas validadas contra las cifras oficiales de SPADIES para la UCO (2018-2024,
error medio < 1 punto porcentual). Ver Documentacion/Formulas_Indicadores_SPADIES.md.

Vistas de cálculo:
- 'ies':      el estudiante se identifica por documento. Cambiar de programa
              dentro de la institución NO es deserción.
- 'programa': el estudiante se identifica por documento + programa. Salir del
              programa (aunque siga en otro) SÍ es deserción del programa.

Definiciones:
- Primíparos de la cohorte c: registros del archivo "Matriculados Nuevos" de c.
- Desertor (TDA): matriculado en t-2, sin matrícula en t-1 ni en t y sin grado a t.
- Ausente (TAI, etiqueta = periodo base t): matriculado en t, sin matrícula en t+1
  y sin grado a t+1.
- Desertor (TDC): primíparo que no vuelve a matricularse y nunca se gradúa
  (estado definitivo con la información disponible). Se asigna al semestre de su
  última matrícula y se acumula. Se requieren 2 periodos posteriores observados
  para confirmar la deserción, por eso los 2 últimos semestres quedan pendientes.
- Graduado (TGA): primíparo con grado registrado hasta el semestre s.
"""

from collections import defaultdict
from typing import Dict, Hashable, Iterable, List, Optional, Sequence, Set, Tuple

from app.domain.periods import label

VIEWS = ("ies", "programa")
ABSENCE_PERIODS = 2          # periodos consecutivos sin matrícula para ser desertor (SPADIES)
WINDOW_PERIODS = 20          # ventana de reporte: últimos 10 años (20 periodos semestrales)
MAX_SEMESTERS = 20           # máximo de semestres de trayectoria mostrados (S1..S20)
_INF = 10 ** 9

Row = Tuple[int, str, str]   # (period_idx, documento, programa)


def _pct(num: int, den: int) -> Optional[float]:
    return round(100.0 * num / den, 2) if den else None


def compute_indicators(
    enrollments: Iterable[Row],
    new_students: Iterable[Row],
    graduates: Iterable[Row],
    view: str = "ies",
    programs: Optional[Sequence[str]] = None,
) -> Dict:
    view = (view or "ies").lower()
    if view not in VIEWS:
        raise ValueError(f"Vista no válida: {view}")
    prog_filter: Optional[Set[str]] = set(programs) if programs else None

    def key(doc: str, prog: str) -> Hashable:
        return doc if view == "ies" else (doc, prog)

    def in_pop(prog: str) -> bool:
        return prog_filter is None or prog in prog_filter

    # --- Matrículas -----------------------------------------------------
    enr_full: Dict[int, Set[Hashable]] = defaultdict(set)   # para detectar ausencias
    enr_pop: Dict[int, Set[Hashable]] = defaultdict(set)    # población del filtro
    last_enr: Dict[Hashable, int] = {}
    for idx, doc, prog in enrollments:
        if view == "programa" and not in_pop(prog):
            continue
        k = key(doc, prog)
        enr_full[idx].add(k)
        if in_pop(prog):
            enr_pop[idx].add(k)
        if last_enr.get(k, -1) < idx:
            last_enr[k] = idx

    if not enr_full:
        return empty_result()

    first, last = min(enr_full), max(enr_full)
    periods = list(range(first, last + 1))
    # Ventana de reporte: los cálculos usan toda la información cargada, pero solo se
    # reportan los últimos WINDOW_PERIODS periodos y hasta MAX_SEMESTERS semestres.
    window_first = max(first, last - WINDOW_PERIODS + 1)
    window = [i for i in periods if i >= window_first]

    # --- Grados (primer periodo de grado por clave) ---------------------
    grad_first: Dict[Hashable, int] = {}
    grads_per_period: Dict[int, Set[Hashable]] = defaultdict(set)
    for idx, doc, prog in graduates:
        if view == "programa" and not in_pop(prog):
            continue
        k = key(doc, prog)
        if idx < grad_first.get(k, _INF):
            grad_first[k] = idx
        if in_pop(prog):
            grads_per_period[idx].add(k)

    # --- Primíparos por cohorte ------------------------------------------
    cohorts: Dict[int, Set[Hashable]] = defaultdict(set)
    for idx, doc, prog in new_students:
        if in_pop(prog) and first <= idx <= last:
            cohorts[idx].add(key(doc, prog))

    def graduated_by(k, i: int) -> bool:
        return grad_first.get(k, _INF) <= i

    # --- TDA ---------------------------------------------------------------
    tda = []
    for i in periods[2:]:
        if i < window_first:
            continue
        base = enr_pop.get(i - 2, set())
        des = sum(1 for k in base if k not in enr_full.get(i - 1, ()) and k not in enr_full.get(i, ()) and not graduated_by(k, i))
        rate = _pct(des, len(base))
        tda.append({"periodo": label(i), "base": len(base), "desertores": des,
                    "tasa": rate, "retencion": None if rate is None else round(100 - rate, 2)})

    # --- TAI (etiqueta = periodo base) --------------------------------------
    tai = []
    for i in window:
        base = enr_pop.get(i, set())
        if i == last:
            tai.append({"periodo": label(i), "base": len(base), "ausentes": None, "tasa": None, "retencion": None})
            continue
        aus = sum(1 for k in base if k not in enr_full.get(i + 1, ()) and not graduated_by(k, i + 1))
        rate = _pct(aus, len(base))
        tai.append({"periodo": label(i), "base": len(base), "ausentes": aus,
                    "tasa": rate, "retencion": None if rate is None else round(100 - rate, 2)})

    # --- TDC / TGA por cohorte --------------------------------------------
    max_sem = min(MAX_SEMESTERS, len(window))
    confirm_limit = last - ABSENCE_PERIODS          # último periodo con deserción confirmable
    tdc_rows, tga_rows = [], []
    agg_des = defaultdict(int); agg_des_den = defaultdict(int); agg_des_n = defaultdict(int)
    agg_grad = defaultdict(int); agg_grad_den = defaultdict(int); agg_grad_n = defaultdict(int)

    for c in window:
        cohort = cohorts.get(c)
        if not cohort:
            continue
        n = len(cohort)
        never_grad_last = [last_enr.get(k, c) for k in cohort if k not in grad_first]
        grad_idx = [grad_first[k] for k in cohort if k in grad_first]
        tdc_vals, tdc_counts, tga_vals, tga_counts = [], [], [], []
        for s in range(1, max_sem + 1):
            i = c + s - 1
            if i > last:
                tdc_vals.append(None); tdc_counts.append(None)
                tga_vals.append(None); tga_counts.append(None)
                continue
            if i <= confirm_limit:
                des = sum(1 for le in never_grad_last if le <= i and le <= confirm_limit)
                tdc_vals.append(_pct(des, n)); tdc_counts.append(des)
                agg_des[s] += des; agg_des_den[s] += n; agg_des_n[s] += 1
            else:
                tdc_vals.append(None); tdc_counts.append(None)
            g = sum(1 for gi in grad_idx if gi <= i)
            tga_vals.append(_pct(g, n)); tga_counts.append(g)
            agg_grad[s] += g; agg_grad_den[s] += n; agg_grad_n[s] += 1
        tdc_rows.append({"cohorte": label(c), "primiparos": n, "valores": tdc_vals, "desertores": tdc_counts})
        tga_rows.append({"cohorte": label(c), "primiparos": n, "valores": tga_vals, "graduados": tga_counts})

    tdpa = [{"semestre": s, "tasa": _pct(agg_des[s], agg_des_den[s]), "desertores": agg_des[s],
             "primiparos": agg_des_den[s], "cohortes": agg_des_n[s]}
            for s in range(1, max_sem + 1) if agg_des_den.get(s)]
    tga = [{"semestre": s, "tasa": _pct(agg_grad[s], agg_grad_den[s]), "graduados": agg_grad[s],
            "primiparos": agg_grad_den[s], "cohortes": agg_grad_n[s]}
           for s in range(1, max_sem + 1) if agg_grad_den.get(s)]

    conteos = [{"periodo": label(i), "matriculados": len(enr_pop.get(i, ())),
                "primiparos": len(cohorts.get(i, ())), "graduados": len(grads_per_period.get(i, ()))}
               for i in window]

    return {
        "periodos": [label(i) for i in window],
        "ventana": {"desde": label(window_first), "hasta": label(last),
                    "periodos": len(window), "max_periodos": WINDOW_PERIODS, "max_semestres": MAX_SEMESTERS},
        "tda": tda,
        "tai": tai,
        "tdc": {"semestres": max_sem, "cohortes": tdc_rows},
        "tdpa": tdpa,
        "tga": tga,
        "tga_cohortes": {"semestres": max_sem, "cohortes": tga_rows},
        "conteos": conteos,
    }


def empty_result() -> Dict:
    return {"periodos": [], "ventana": None, "tda": [], "tai": [], "tdc": {"semestres": 0, "cohortes": []},
            "tdpa": [], "tga": [], "tga_cohortes": {"semestres": 0, "cohortes": []}, "conteos": []}


# -------------------------------------------------------------------
# ESTADO INDIVIDUAL DEL ESTUDIANTE (vista institucional)
# -------------------------------------------------------------------
def classify_students(
    enrollments: Iterable[Row],
    graduates: Iterable[Row],
) -> Tuple[Dict[str, Dict], Optional[int]]:
    """
    Estado SPADIES por documento al último periodo cargado:
    - Graduado: tiene grado posterior o igual a su última matrícula.
    - Activo:   matriculado en el último periodo o en el anterior.
    - Desertor: ausente dos o más periodos consecutivos sin grado.
    Retorna (estados, ultimo_periodo_idx).
    """
    info: Dict[str, Dict] = {}
    last = None
    for idx, doc, prog in enrollments:
        d = info.setdefault(doc, {"ultima": -1, "programa": None, "grado": None, "programa_grado": None})
        if idx >= d["ultima"]:
            d["ultima"], d["programa"] = idx, prog
        last = idx if last is None or idx > last else last
    for idx, doc, prog in graduates:
        d = info.setdefault(doc, {"ultima": -1, "programa": None, "grado": None, "programa_grado": None})
        if d["grado"] is None or idx > d["grado"]:
            d["grado"], d["programa_grado"] = idx, prog
    if last is None:
        return {}, None
    out = {}
    for doc, d in info.items():
        if d["grado"] is not None and d["grado"] >= d["ultima"]:
            estado = "Graduado"
            programa = d["programa_grado"] or d["programa"]
        elif d["ultima"] >= last - 1:
            estado, programa = "Activo", d["programa"]
        else:
            estado, programa = "Desertor", d["programa"]
        out[doc] = {"estado": estado, "programa": programa,
                    "ultimo_periodo": label(d["ultima"]) if d["ultima"] >= 0 else None}
    return out, last


STATE_DEFINITIONS = {
    "Activo": "Estudiante que se encuentra matriculado o que se encontraba matriculado el semestre anterior.",
    "Desertor": "Estudiante que no se observa matriculado por dos o más periodos consecutivos y no registra graduación.",
    "Graduado": "Estudiante que culminó su ciclo académico y obtuvo el título.",
}


def rows_for_programs(rows: Iterable[Row], allowed: Optional[Set[str]]) -> List[Row]:
    if not allowed:
        return list(rows)
    return [r for r in rows if r[2] in allowed]
