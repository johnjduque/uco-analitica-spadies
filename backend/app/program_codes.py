# Mapeo Oficial de Codificación de Programas de la Universidad Católica de Oriente (UCO)
# Extraído del documento institucional "Codificación de Programas"

OFFICIAL_UCO_PROGRAM_CODES = {
    'TB': 'Trabajo Social',
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
    'DI': 'Especialización en Didáctica del Inglés'
}

import unicodedata
import re

def _normalize_key(s: str) -> str:
    if not s:
        return ""
    s = str(s).strip().lower()
    s = "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# Variaciones comunes de nombres abreviados o variantes textuales
PROGRAM_NAME_VARIATIONS = {
    'Ing. De sistemas': 'Ingeniería de Sistemas',
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
    'Especialización en psicolog\u00eda educativa': 'Especialización en Psicología Evolutiva',
    'Licenciautra en Ciencias Naturales': 'Licenciatura en Ciencias Naturales',
    'Licenciatrura En Filosofía': 'Licenciatura en Filosofía',
    'Licenciatrura En Filosofia': 'Licenciatura en Filosofía',
    'Licenciatrura En Ed. Fisica Recreación y Deportes - Presencial': 'Licenciatura en Educación Física, Recreación y Deportes - Presencial',
    'Técnico en Profesional en Programación Web': 'Técnico Profesional en Programación Web',
    'Tecnico en Profesional en Programacion Web': 'Técnico Profesional en Programación Web',
    'Esp. En Pedagogía y Didáctica': 'Especialización en Pedagogía y Didáctica',
    'Esp. En Logística y Operaciones': 'Especialización en Logística y Operaciones',
    'Esp. En Mercadeo': 'Especialización en Mercadeo',
    'Esp. En Gestión Tributaria': 'Especialización en Gestión Tributaria',
    'Esp. En Gerencia Financiera': 'Especialización en Gerencia Financiera',
    'Esp. En Gestión y Ordenamiento de cuencas': 'Especialización en Gestión y Ordenamiento de Cuencas',
    'Licenciatura en Educación física, recreación y deporte': 'Licenciatura en Educación Física, Recreación y Deportes',
    'Licenciatura en educacion fisica, recreacion y deporte': 'Licenciatura en Educación Física, Recreación y Deportes',
    'Licenciatura en Educación física, recreación y deporte - Presencial': 'Licenciatura en Educación Física, Recreación y Deportes - Presencial',
    'Licenciatura en Educación física, recreación y deporte, Presencial': 'Licenciatura en Educación Física, Recreación y Deportes - Presencial',
    'Licenciatura en Educación física, recreación y deportes, Presencial': 'Licenciatura en Educación Física, Recreación y Deportes - Presencial',
    'Licenciatura en Educación para la primera infancia': 'Licenciatura en Primera Infancia',
    'Licenciatura en educación para la primera infancia': 'Licenciatura en Primera Infancia',
    'IP': 'Licenciatura en Primera Infancia'
}

def is_known_program(code_or_name: str) -> bool:
    """Verifica si un código o nombre de programa ya se encuentra registrado en el catálogo oficial de la UCO."""
    if not code_or_name:
        return False
    clean = str(code_or_name).strip()
    upper = clean.upper()

    if clean in OFFICIAL_UCO_PROGRAM_CODES or upper in OFFICIAL_UCO_PROGRAM_CODES:
        return True
    if clean in PROGRAM_NAME_VARIATIONS:
        return True
    if clean in OFFICIAL_UCO_PROGRAM_CODES.values():
        return True

    # Búsqueda normalizada (insensible a mayúsculas, tildes y espacios)
    norm = _normalize_key(clean)
    for code, name in OFFICIAL_UCO_PROGRAM_CODES.items():
        if _normalize_key(code) == norm or _normalize_key(name) == norm:
            return True
    for var_key in PROGRAM_NAME_VARIATIONS:
        if _normalize_key(var_key) == norm:
            return True

    return False

def add_new_program(code_or_name: str, full_name: str = None) -> str:
    """Añade dinámicamente un nuevo programa o código al catálogo oficial."""
    clean = str(code_or_name).strip()
    target_name = full_name.strip() if full_name else clean

    if len(clean) <= 4:
        OFFICIAL_UCO_PROGRAM_CODES[clean.upper()] = target_name
    else:
        PROGRAM_NAME_VARIATIONS[clean] = target_name
        # Add to values list as well
        if target_name not in OFFICIAL_UCO_PROGRAM_CODES.values():
            OFFICIAL_UCO_PROGRAM_CODES[clean[:4].upper()] = target_name

    return target_name

def translate_program_code(code_or_name: str) -> str:
    """Traduce un código de 2 letras o nombre abreviado al Nombre Oficial Completo del Programa UCO."""
    if not code_or_name:
        return "Desconocido"
    
    clean = str(code_or_name).strip()
    
    # 1. Buscar en códigos oficiales
    if clean in OFFICIAL_UCO_PROGRAM_CODES:
        return OFFICIAL_UCO_PROGRAM_CODES[clean]
    
    upper = clean.upper()
    if upper in OFFICIAL_UCO_PROGRAM_CODES:
        return OFFICIAL_UCO_PROGRAM_CODES[upper]

    # 2. Buscar en variaciones de nombre textual
    if clean in PROGRAM_NAME_VARIATIONS:
        return PROGRAM_NAME_VARIATIONS[clean]

    # 3. Coincidencia exacta con algún valor oficial
    if clean in OFFICIAL_UCO_PROGRAM_CODES.values():
        return clean

    # 4. Búsqueda normalizada
    norm = _normalize_key(clean)
    for code, name in OFFICIAL_UCO_PROGRAM_CODES.items():
        if _normalize_key(code) == norm or _normalize_key(name) == norm:
            return name
    for var_key, target in PROGRAM_NAME_VARIATIONS.items():
        if _normalize_key(var_key) == norm:
            return target

    return clean

def get_all_official_programs() -> list:
    """Devuelve la lista ordenada y sin duplicados de todos los Nombres Oficiales de Programas de la UCO."""
    all_names = set(OFFICIAL_UCO_PROGRAM_CODES.values())
    return sorted(list(all_names))

def find_document_column(columns: list):
    """
    Encuentra con precisión la columna que contiene el número de documento de identidad del estudiante,
    descartando deliberadamente columnas como 'Tipo de documento' (CC, TI, etc.).
    """
    candidates = [c for c in columns if 'tipo' not in str(c).lower()]
    
    # Prioridad 1: 'número'/'numero' AND ('doc'/'ident')
    for c in candidates:
        c_low = str(c).lower()
        if ('número' in c_low or 'numero' in c_low or 'num' in c_low) and ('doc' in c_low or 'ident' in c_low):
            return c
            
    # Prioridad 2: 'cédula' / 'cedula'
    for c in candidates:
        c_low = str(c).lower()
        if 'cedula' in c_low or 'cédula' in c_low:
            return c
            
    # Prioridad 3: 'identificación' / 'identificacion'
    for c in candidates:
        c_low = str(c).lower()
        if 'identificaci' in c_low:
            return c
            
    # Prioridad 4: 'documento'
    for c in candidates:
        c_low = str(c).lower()
        if 'documento' in c_low:
            return c
            
    # Prioridad 5: 'numero' / 'número'
    for c in candidates:
        c_low = str(c).lower()
        if 'numero' in c_low or 'número' in c_low:
            return c
            
    return candidates[0] if candidates else None

def find_program_column(columns: list):
    """Encuentra la columna correspondiente al programa académico."""
    for c in columns:
        if 'programa' in str(c).lower():
            return c
    return None

