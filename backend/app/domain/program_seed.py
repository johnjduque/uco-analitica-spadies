"""
CATÁLOGO INICIAL DE PROGRAMAS DE LA UCO
Fuente: documento institucional "Codificación de Programas".

Se usa solo para poblar la tabla program_catalog la primera vez. Después, el
catálogo se administra desde la aplicación (Catálogo de Programas), incluido el
nivel de formación (pregrado/posgrado) de cada programa.
"""

import re
import unicodedata

# Código oficial -> nombre oficial
OFFICIAL_PROGRAMS = {'TB': 'Trabajo Social',
 'LI': 'Licenciatura en Primera Infancia',
 'CI': 'Licenciatura en Lenguas Extranjeras con Énfasis en Inglés',
 'LF': 'Licenciatura en Filosofía',
 'LR': 'Licenciatura en Educación Religiosa',
 'EI': 'Licenciatura en Educación Básica con Énfasis en Educación Religiosa',
 'EL': 'Licenciatura en Educación Campesina y Rural',
 'EM': 'Licenciatura en Matemáticas',
 'EN': 'Licenciatura en Ciencias Naturales',
 'ER': 'Licenciatura en Educación Física, Recreación y Deportes',
 'FE': 'Licenciatura en Filosofía y Educación Religiosa',
 'EP': 'Especialización en Pedagogía y Didáctica',
 'MD': 'Maestría en Educación',
 'CE': 'Licenciatura en Lenguas Extranjeras',
 'AN': 'Agronomía',
 'AT': 'Tecnología Agropecuaria',
 'MS': 'Maestría en Sanidad Vegetal',
 'ZO': 'Zootecnia',
 'CA': 'Ingeniería Ambiental',
 'EW': 'Especialización en Gestión del Software',
 'IE': 'Ingeniería Electrónica',
 'II': 'Ingeniería Industrial',
 'IS': 'Ingeniería de Sistemas',
 'DD': 'Derecho y Ciencias Sociales',
 'DE': 'Derecho',
 'PD': 'Especialización en Probática y Derecho Probatorio',
 'AC': 'Comercio Exterior',
 'AF': 'Administración de Empresas',
 'CC': 'Contaduría Pública',
 'EO': 'Especialización en Logística y Operaciones',
 'GF': 'Especialización en Gerencia Financiera',
 'GT': 'Especialización en Gestión Tributaria',
 'ME': 'Especialización en Mercadeo',
 'MH': 'Maestría en Humanidades',
 'TT': 'Teología',
 'TV': 'Teología Virtual UCN',
 'SE': 'Enfermería',
 'SG': 'Gerontología',
 'CS': 'Comunicación Social',
 'PS': 'Psicología',
 'GC': 'Especialización en Gestión y Ordenamiento de Cuencas',
 'PE': 'Especialización en Psicología Evolutiva',
 'PM': 'Maestría en Psicología',
 'TO': 'Tecnología en Operaciones Financieras',
 'TW': 'Técnico Profesional en Programación Web',
 'GS': 'Especialización en Alta Gerencia para Sistemas Integrados de Gestión',
 'MF': 'Maestría en Salud Familiar',
 'ND': 'Nutrición y Dietética',
 'RE': 'Licenciatura en Educación Física, Recreación y Deportes - Presencial',
 'CH': 'Centro de Humanidades',
 'CN': 'Licenciatura en Ciencias Naturales',
 'DL': 'Departamento de Lenguaje',
 'DP': 'Doctorado en Pedagogía',
 'GM': 'Especialización en Gerencia Estratégica de Mercadeo',
 'LE': 'Bolsa Electivas',
 'MT': 'Maestría en Tributación',
 'PT': 'Especialización en Planificación para el Desarrollo Territorial',
 'RS': 'Especialización en Gerencia de la Responsabilidad Social',
 'TH': 'Especialización en Gerencia Estratégica del Talento Humano',
 'MV': 'Maestría en Educación Virtual',
 'DI': 'Especialización en Didáctica del Inglés'}

# Unidades que aparecen en la codificación pero no son programas de formación
NON_ACADEMIC_CODES = {'CH', 'LE', 'DL'}

# Variantes de escritura frecuentes en los archivos -> nombre oficial
NAME_VARIATIONS = {'Ing. De sistemas': 'Ingeniería de Sistemas',
 'Ing. de sistemas': 'Ingeniería de Sistemas',
 'Ing. Industrial': 'Ingeniería Industrial',
 'Ing. Ambiental': 'Ingeniería Ambiental',
 'Ing. Electrónica': 'Ingeniería Electrónica',
 'Tec. Agropecuaria': 'Tecnología Agropecuaria',
 'Lic. Lenguas Extranjeras': 'Licenciatura en Lenguas Extranjeras',
 'Lic. En Edu. Física, Recreación y Deportes': 'Licenciatura en Educación Física, Recreación y Deportes',
 'Lic. En Filosofía y Edu. Religiosa': 'Licenciatura en Filosofía y Educación Religiosa',
 'Maestría en educación': 'Maestría en Educación',
 'Admon de Empresas': 'Administración de Empresas',
 'Gerontología a distancia': 'Gerontología',
 'Teología a distancia': 'Teología',
 'Teología virtual': 'Teología Virtual UCN',
 'Especialización Probática y Derecho Probatorio': 'Especialización en Probática y Derecho Probatorio',
 'Especialización en Probatica y Derecho Probatorio': 'Especialización en Probática y Derecho Probatorio',
 'Especialización en Psicología educativa': 'Especialización en Psicología Evolutiva',
 'Especialización en Psicología Educativa': 'Especialización en Psicología Evolutiva',
 'Especialización en psicología educativa': 'Especialización en Psicología Evolutiva',
 'Licenciautra en Ciencias Naturales': 'Licenciatura en Ciencias Naturales',
 'Licenciatrura En Filosofía': 'Licenciatura en Filosofía',
 'Licenciatrura En Filosofia': 'Licenciatura en Filosofía',
 'Licenciatrura En Ed. Fisica Recreación y Deportes - Presencial': 'Licenciatura en Educación Física, '
                                                                   'Recreación y Deportes - Presencial',
 'Técnico en Profesional en Programación Web': 'Técnico Profesional en Programación Web',
 'Tecnico en Profesional en Programacion Web': 'Técnico Profesional en Programación Web',
 'Esp. En Pedagogía y Didáctica': 'Especialización en Pedagogía y Didáctica',
 'Esp. En Logística y Operaciones': 'Especialización en Logística y Operaciones',
 'Esp. En Mercadeo': 'Especialización en Mercadeo',
 'Esp. En Gestión Tributaria': 'Especialización en Gestión Tributaria',
 'Esp. En Gerencia Financiera': 'Especialización en Gerencia Financiera',
 'Esp. En Gestión y Ordenamiento de cuencas': 'Especialización en Gestión y Ordenamiento de Cuencas',
 'Licenciatura en Educación física, recreación y deporte': 'Licenciatura en Educación Física, Recreación y '
                                                           'Deportes',
 'Licenciatura en educacion fisica, recreacion y deporte': 'Licenciatura en Educación Física, Recreación y '
                                                           'Deportes',
 'Licenciatura en Educación física, recreación y deporte - Presencial': 'Licenciatura en Educación Física, '
                                                                        'Recreación y Deportes - Presencial',
 'Licenciatura en Educación física, recreación y deporte, Presencial': 'Licenciatura en Educación Física, '
                                                                       'Recreación y Deportes - Presencial',
 'Licenciatura en Educación física, recreación y deportes, Presencial': 'Licenciatura en Educación Física, '
                                                                        'Recreación y Deportes - Presencial',
 'Licenciatura en Educación para la primera infancia': 'Licenciatura en Primera Infancia',
 'Licenciatura en educación para la primera infancia': 'Licenciatura en Primera Infancia',
 'IP': 'Licenciatura en Primera Infancia',
 'Especialización en alta gerenca para sistemas integrados de gestión': 'Especialización en Alta Gerencia '
                                                                        'para Sistemas Integrados de Gestión',
 'Lic. En Ed. Básica con énfasis en Ed. Religiosa': 'Licenciatura en Educación Básica con Énfasis en '
                                                    'Educación Religiosa',
 'Maestría en Educación Virtual UCN': 'Maestría en Educación Virtual',
 'Esp. En Gestión de Software': 'Especialización en Gestión del Software',
 'Especialización en didáctica del Ingles': 'Especialización en Didáctica del Inglés'}

_POSGRADO_PREFIXES = ("especializ", "maestr", "doctor", "esp ", "esp.", "mag ")


def normalize(text: str) -> str:
    """Minúsculas, sin tildes, sin puntuación y con espacios simples (para comparar nombres)."""
    s = str(text or "").strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def guess_level(name: str) -> str:
    """Nivel de formación sugerido a partir del nombre del programa."""
    n = normalize(name)
    return "posgrado" if n.startswith(tuple(normalize(p) for p in _POSGRADO_PREFIXES)) else "pregrado"
