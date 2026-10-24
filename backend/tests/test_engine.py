"""Pruebas unitarias del motor de indicadores y de periodos (sin base de datos)."""

import unittest
from datetime import date

import tests  # noqa: F401
from app.domain import periods as P
from app.domain.indicators import classify_students, compute_indicators

IS, II = "Ingeniería de Sistemas", "Ingeniería Industrial"


def idx(p):
    return P.index_of(p)


class PeriodTests(unittest.TestCase):
    def test_parse_formats(self):
        self.assertEqual(P.canonical("1-2018"), "2018-1")
        self.assertEqual(P.canonical("2018_2"), "2018-2")
        self.assertEqual(P.canonical("2018"), "2018")
        with self.assertRaises(ValueError):
            P.canonical("2018-3")

    def test_index_roundtrip(self):
        self.assertEqual(P.label(P.index_of("2024-2")), "2024-2")
        self.assertEqual(P.index_of("2019-1") - P.index_of("2018-2"), 1)

    def test_date_semester(self):
        self.assertEqual(P.label(P.index_of_date(date(2020, 12, 10))), "2020-2")
        self.assertEqual(P.label(P.index_of_date(date(2020, 6, 30))), "2020-1")
        self.assertEqual(P.label(P.index_of_date(date(2019, 7, 1))), "2019-2")

    def test_parse_date_iso_text_is_not_day_first(self):
        # Error de la versión anterior: '2021-03-12' se leía como 3 de diciembre
        self.assertEqual(P.parse_date("2021-03-12"), date(2021, 3, 12))
        self.assertEqual(P.parse_date("12/03/2021"), date(2021, 3, 12))
        self.assertEqual(P.parse_date("2021-03-12 16:00:00"), date(2021, 3, 12))
        self.assertIsNone(P.parse_date(""))

    def test_periods_in_filename(self):
        self.assertEqual(P.periods_in_text("Matriculados Nuevos 1-2018.xls"), {"2018-1"})
        self.assertEqual(P.periods_in_text("Egresados 2019.xls"), {"2019"})
        self.assertEqual(P.periods_in_text("Matriculados_2024_2.xlsx"), {"2024-2"})
        self.assertEqual(P.periods_in_text("datos.xlsx"), set())


class EngineTests(unittest.TestCase):
    def setUp(self):
        # Periodos 2020-1 .. 2022-1 (5 periodos)
        e = []
        def enr(p, doc, prog=IS):
            e.append((idx(p), doc, prog))
        for p in ["2020-1", "2020-2", "2021-1", "2021-2", "2022-1"]:
            enr(p, "D")                                    # siempre activo
        for p in ["2020-1", "2020-2", "2021-1", "2021-2"]:
            enr(p, "C")                                    # falta solo en 2022-1 (ausente, no desertor)
        for p in ["2020-1", "2020-2", "2021-1"]:
            enr(p, "B")                                    # abandona tras 2021-1 (desertor)
        for p in ["2020-1", "2020-2"]:
            enr(p, "A")                                    # se gradúa en 2020-2
        enr("2020-1", "X"); enr("2020-2", "X", II); enr("2021-1", "X", II)   # cambia de programa y abandona
        self.enr = e
        self.new = [(idx("2020-1"), d, IS) for d in ("A", "B", "C", "D", "X")]
        self.grad = [(idx("2020-2"), "A", IS)]

    def test_tda_requires_absence_in_t_minus_1_and_t(self):
        r = compute_indicators(self.enr, self.new, self.grad, view="ies")
        tda = {x["periodo"]: x for x in r["tda"]}
        # 2021-2: base 2020-2 = {A,B,C,D,X}; nadie lleva 2 periodos ausente (B y X están en 2021-1)
        self.assertEqual(tda["2021-2"]["desertores"], 0)
        # 2022-1: base 2021-1 = {B,C,D,X}; B y X ausentes en 2021-2 y 2022-1; C solo falta en 2022-1
        self.assertEqual(tda["2022-1"]["desertores"], 2)
        self.assertEqual(tda["2022-1"]["tasa"], 50.0)

    def test_tai_label_is_base_period(self):
        r = compute_indicators(self.enr, self.new, self.grad, view="ies")
        tai = {x["periodo"]: x for x in r["tai"]}
        # base 2020-2 -> no vuelven en 2021-1: A (graduado, no cuenta) -> 0
        self.assertEqual(tai["2020-2"]["ausentes"], 0)
        # base 2021-1 = {B,C,D,X} -> ausentes en 2021-2: B, X
        self.assertEqual(tai["2021-1"]["ausentes"], 2)
        self.assertIsNone(tai["2022-1"]["tasa"])          # último periodo sin siguiente observado

    def test_tdc_definitive_and_assigned_to_last_enrollment(self):
        r = compute_indicators(self.enr, self.new, self.grad, view="ies")
        row = r["tdc"]["cohortes"][0]
        self.assertEqual(row["cohorte"], "2020-1")
        self.assertEqual(row["primiparos"], 5)
        # B y X abandonan con última matrícula en 2021-1 (S3); confirmable hasta 2022-1-2 = 2021-1
        self.assertEqual(row["desertores"][:3], [0, 0, 2])
        self.assertIsNone(row["valores"][3])               # S4 aún no confirmable

    def test_program_view_counts_program_change_as_dropout(self):
        ies = compute_indicators(self.enr, self.new, self.grad, view="ies")
        prog = compute_indicators(self.enr, self.new, self.grad, view="programa")
        t_ies = {x["periodo"]: x for x in ies["tai"]}["2020-1"]["ausentes"]
        t_prog = {x["periodo"]: x for x in prog["tai"]}["2020-1"]["ausentes"]
        self.assertEqual(t_ies, 0)
        self.assertEqual(t_prog, 1)                        # X sale de Sistemas

    def test_tga_counts_graduates_of_cohort(self):
        r = compute_indicators(self.enr, self.new, self.grad, view="ies")
        tga = {x["semestre"]: x for x in r["tga"]}
        self.assertEqual(tga[1]["graduados"], 0)
        self.assertEqual(tga[2]["graduados"], 1)
        self.assertEqual(tga[2]["tasa"], 20.0)

    def test_program_filter_in_ies_view(self):
        r = compute_indicators(self.enr, self.new, self.grad, view="ies", programs=[II])
        conteo = {x["periodo"]: x["matriculados"] for x in r["conteos"]}
        self.assertEqual(conteo["2020-2"], 1)
        self.assertEqual(r["tdc"]["cohortes"], [])          # nadie ingresó como nuevo a Industrial

    def test_student_states(self):
        states, last = classify_students(self.enr, self.grad)
        self.assertEqual(P.label(last), "2022-1")
        self.assertEqual(states["A"]["estado"], "Graduado")
        self.assertEqual(states["B"]["estado"], "Desertor")
        self.assertEqual(states["C"]["estado"], "Activo")   # ausente un solo periodo
        self.assertEqual(states["D"]["estado"], "Activo")

    def test_window_last_10_years_and_20_semesters(self):
        # 15 años de datos (30 periodos): un estudiante permanente y una cohorte por periodo
        first = idx("2010-1")
        enr, new = [], []
        for i in range(first, first + 30):
            enr.append((i, "P", IS))
            enr.append((i, f"N{i}", IS))
            new.append((i, f"N{i}", IS))
        r = compute_indicators(enr, new, [], view="ies")
        self.assertEqual(len(r["periodos"]), 20)
        self.assertEqual(r["periodos"][0], "2015-1")
        self.assertEqual(r["periodos"][-1], "2024-2")
        self.assertEqual(r["ventana"]["desde"], "2015-1")
        self.assertEqual([x["periodo"] for x in r["tda"]][0], "2015-1")
        self.assertEqual(len(r["tda"]), 20)
        self.assertEqual(len(r["tai"]), 20)
        self.assertEqual(len(r["conteos"]), 20)
        self.assertEqual(r["tdc"]["cohortes"][0]["cohorte"], "2015-1")
        self.assertEqual(len(r["tdc"]["cohortes"]), 20)
        self.assertTrue(all(len(c["valores"]) <= 20 for c in r["tdc"]["cohortes"]))
        self.assertLessEqual(max(x["semestre"] for x in r["tdpa"]), 20)
        self.assertLessEqual(max(x["semestre"] for x in r["tga"]), 20)
        # La ausencia en el primer periodo de la ventana usa información anterior a la ventana
        self.assertEqual({x["periodo"]: x["base"] for x in r["tda"]}["2015-1"], 2)

    def test_empty(self):
        r = compute_indicators([], [], [])
        self.assertEqual(r["periodos"], [])


if __name__ == "__main__":
    unittest.main()
