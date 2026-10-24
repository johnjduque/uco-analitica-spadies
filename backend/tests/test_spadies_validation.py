"""
VALIDACIÓN DE PUNTA A PUNTA CONTRA LAS CIFRAS OFICIALES DE SPADIES

Carga los archivos reales de la universidad a través de la API (igual que un
usuario) y compara TDA, TAI y TDC (pregrado, vistas IES y Programa) con las
exportaciones oficiales de SPADIES.

Se ejecuta solo si existe la variable de entorno UCO_DATOS_DIR apuntando a la
carpeta Datos_UCO, con esta estructura:
    Datos_UCO/Estudiantes y Egresados/Matriculados S-AAAA.xls(x) y Egresados S-AAAA.xls(x)
    Datos_UCO/EstudiantesNuevos/Matriculados Nuevos S-AAAA.xls(x)
    Datos_UCO/Indicadores/*.csv   (exportaciones de SPADIES)

Ejemplo (Windows PowerShell, desde backend):
    $env:UCO_DATOS_DIR="..\\Datos_UCO"; python -m unittest tests.test_spadies_validation -v
"""

import csv
import os
import re
import unittest
from pathlib import Path

from tests.helpers import admin_headers, client, reset_database, upload

DATA_DIR = os.getenv("UCO_DATOS_DIR")
# Tolerancias (puntos porcentuales de error medio absoluto)
MAX_ERR = {"TDA": 0.6, "TAI": 0.6, "TDC": 1.2}


def _find(folder: Path, stem: str):
    for ext in (".xlsx", ".xls", ".csv"):
        f = folder / f"{stem}{ext}"
        if f.exists():
            return f
    return None


def _spadies_csv(path: Path):
    with open(path, encoding="utf-8-sig") as fh:
        return list(csv.reader(fh, delimiter=";"))


def _pct(v):
    try:
        return float(str(v).strip().rstrip("%"))
    except ValueError:
        return None


@unittest.skipUnless(DATA_DIR and Path(DATA_DIR).exists(), "Defina UCO_DATOS_DIR para validar contra SPADIES")
class SpadiesValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reset_database()
        cls.c = client()
        cls.h = admin_headers(cls.c)
        base = Path(DATA_DIR)
        est, nue = base / "Estudiantes y Egresados", base / "EstudiantesNuevos"
        periods = sorted({m.group(2) + "-" + m.group(1) for f in est.iterdir()
                          for m in [re.match(r"Matriculados (\d)-(\d{4})", f.name)] if m})
        decisiones = []
        for p in periods:
            y, s = p.split("-")
            for tipo, folder, stem in (("matriculados", est, f"Matriculados {s}-{y}"),
                                       ("nuevos", nue, f"Matriculados Nuevos {s}-{y}"),
                                       ("egresados", est, f"Egresados {s}-{y}")):
                f = _find(folder, stem)
                if not f:
                    continue
                content = f.read_bytes()
                r = upload(cls.c, cls.h, tipo, p, f.name, content, decisiones=decisiones or None)
                body = r.json()
                if body.get("status") == "confirmar_programas":
                    # Programas desconocidos: se crean con el nivel sugerido
                    decisiones += [{"nombre": x["nombre"], "accion": "crear", "nivel": x["nivel_sugerido"]} for x in body["programas"]]
                    r = upload(cls.c, cls.h, tipo, p, f.name, content, decisiones=decisiones)
                    body = r.json()
                assert r.status_code == 200 and body.get("status") == "success", f"{f.name}: {r.text[:500]}"
        cls.periods = periods

    def _compare(self, vista: str):
        res = self.c.get(f"/api/indicators?nivel=pregrado&vista={vista}", headers=self.h).json()
        ind = Path(DATA_DIR) / "Indicadores"
        suf = "IES" if vista == "ies" else "Programa"
        errors = {}
        for key, fname, series in (("TDA", f"DesercionAnual-{suf}.csv", res["tda"]),
                                   ("TAI", f"AusenciaIntersemestral-{suf}.csv", res["tai"])):
            rows = _spadies_csv(ind / fname)
            off = dict(zip(rows[0][1:], rows[1][1:]))
            diffs = [abs(x["tasa"] - _pct(off[x["periodo"]])) for x in series
                     if x["tasa"] is not None and x["periodo"] in off and _pct(off[x["periodo"]])]
            errors[key] = sum(diffs) / len(diffs)
        rows = _spadies_csv(ind / f"DesercionPorCohorte-{suf}.csv")
        hdr = rows[0]
        off = {r[0]: dict(zip(hdr[1:], r[1:])) for r in rows[1:]}
        diffs = []
        for c in res["tdc"]["cohortes"]:
            for s, v in enumerate(c["valores"], start=1):
                o = _pct(off.get(c["cohorte"], {}).get(f"S{s}", ""))
                if v is not None and o is not None:
                    diffs.append(abs(v - o))
        errors["TDC"] = sum(diffs) / len(diffs)
        print(f"\nError medio vs SPADIES (pregrado, vista {suf}): " + ", ".join(f"{k} {v:.2f} pp" for k, v in errors.items()))
        for k, v in errors.items():
            self.assertLess(v, MAX_ERR[k], f"{k} vista {suf}: error medio {v:.2f} pp")

    def test_ies_view(self):
        self._compare("ies")

    def test_program_view(self):
        self._compare("programa")


if __name__ == "__main__":
    unittest.main()
