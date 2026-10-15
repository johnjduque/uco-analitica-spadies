"""
CATÁLOGO CENTRALIZADO DE MENSAJES (TÉCNICOS VS. USUARIO)
Universidad Católica de Oriente - Sistema Analítico de Deserción

Garantiza:
1. No revelar detalles técnicos sensibles al usuario final (evita Information Disclosure - OWASP).
2. Facilitar la labor técnica mediante códigos estandarizados y mensajes de depuración en logs.
3. Respuestas estructuradas uniformes para el Frontend y clientes móviles.
"""

from typing import Dict, Any, Optional

CATALOG: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------
    # AUTENTICACIÓN Y SEGURIDAD (AUTH)
    # -------------------------------------------------------------------
    "AUTH_001": {
        "user_message": "Cédula o contraseña incorrecta. Por favor verifique sus datos.",
        "technical_message": "Falló la autenticación: usuario no existe o hash de contraseña inválido.",
        "status_code": 401
    },
    "AUTH_002": {
        "user_message": "Su sesión ha expirado o no es válida. Por favor inicie sesión nuevamente.",
        "technical_message": "Token JWT expirado, firma inválida o cabecera Authorization ausente.",
        "status_code": 401
    },
    "AUTH_003": {
        "user_message": "No tiene permisos para realizar esta acción. Consulte con el administrador.",
        "technical_message": "Control de acceso RBAC denegado: El rol del usuario no tiene los privilegios requeridos.",
        "status_code": 403
    },
    "AUTH_004": {
        "user_message": "La contraseña actual suministrada no es correcta.",
        "technical_message": "Validación de contraseña anterior fallida en proceso de cambio de clave.",
        "status_code": 400
    },
    "AUTH_005": {
        "user_message": "La nueva contraseña debe tener al menos 6 caracteres.",
        "technical_message": "Violación de política de complejidad de contraseña: longitud mínima no alcanzada.",
        "status_code": 400
    },

    # -------------------------------------------------------------------
    # GESTIÓN DE USUARIOS (USER)
    # -------------------------------------------------------------------
    "USER_001": {
        "user_message": "Ya existe un usuario registrado con esa cédula.",
        "technical_message": "Conflicto de unicidad en base de datos: unique constraint users.username.",
        "status_code": 400
    },
    "USER_002": {
        "user_message": "El usuario solicitado no existe en el sistema.",
        "technical_message": "Registro de usuario no encontrado por ID o username especificado.",
        "status_code": 404
    },
    "USER_003": {
        "user_message": "La cédula debe contener únicamente números y tener al menos 5 dígitos.",
        "technical_message": "Validación de formato fallida: el campo cédula no es numérico o no cumple longitud.",
        "status_code": 400
    },
    "USER_004": {
        "user_message": "El rol seleccionado no es válido. Los roles permitidos son Administrador o Consultor.",
        "technical_message": "Valor de rol inválido recibido fuera de la enumeración permitida.",
        "status_code": 400
    },

    # -------------------------------------------------------------------
    # CARGA E INGESTA DE DATOS (DATA)
    # -------------------------------------------------------------------
    "DATA_001": {
        "user_message": "Secuencia cronológica incorrecta. El periodo cargado no corresponde al orden esperado.",
        "technical_message": "Secuencia cronológica violada: el periodo subido no coincide con next_expected_period.",
        "status_code": 400
    },
    "DATA_002": {
        "user_message": "Este periodo ya fue cargado previamente en el sistema.",
        "technical_message": "Conflicto: registro DataLoadRecord ya existe para el tipo y periodo especificados.",
        "status_code": 400
    },
    "DATA_003": {
        "user_message": "El archivo subido no tiene un formato válido. Debe ser Excel (.xlsx, .xls) o CSV.",
        "technical_message": "Formato de archivo MIME/extensión no soportado para procesamiento de datos.",
        "status_code": 400
    },
    "DATA_004": {
        "user_message": "El archivo no contiene la columna obligatoria de Documento de Identificación.",
        "technical_message": "Estructura de datos inválida: columna de identificación de estudiante no encontrada.",
        "status_code": 400
    },
    "DATA_005": {
        "user_message": "El archivo no contiene la columna obligatoria de Programa Académico.",
        "technical_message": "Estructura de datos inválida: columna de programa académico no detectada en DataFrame.",
        "status_code": 400
    },
    "DATA_006": {
        "user_message": "El archivo de egresados no contiene la columna requerida de Fecha de Grado.",
        "technical_message": "Estructura de datos inválida: columna de fecha/hora de grado ausente en archivo de graduados.",
        "status_code": 400
    },
    "DATA_007": {
        "user_message": "Existen filas en el archivo donde el documento de identidad no es un número válido.",
        "technical_message": "Error de tipo de dato: valores no numéricos detectados en la columna de cédula.",
        "status_code": 400
    },
    "DATA_008": {
        "user_message": "El registro de carga especificado no existe o ya fue eliminado.",
        "technical_message": "DataLoadRecord no encontrado con el ID suministrado.",
        "status_code": 404
    },

    # -------------------------------------------------------------------
    # MÉTRICAS Y CÁLCULOS SPADIES (METR)
    # -------------------------------------------------------------------
    "METR_001": {
        "user_message": "El indicador solicitado no es válido. Opciones: TAI, TDA, TDPA, TDC, TGA.",
        "technical_message": "Indicador SPADIES no reconocido por el motor analítico de métricas.",
        "status_code": 404
    },
    "METR_002": {
        "user_message": "No hay suficientes datos cargados para calcular las métricas seleccionadas.",
        "technical_message": "Insuficiencia de periodos cargados en Data/ o user_uploads/ para generar series SPADIES.",
        "status_code": 400
    },

    # -------------------------------------------------------------------
    # PARÁMETROS DEL SISTEMA (PARAM)
    # -------------------------------------------------------------------
    "PARAM_001": {
        "user_message": "El parámetro solicitado no fue encontrado.",
        "technical_message": "SystemParameter no encontrado en base de datos con la clave indicada.",
        "status_code": 404
    },
    "PARAM_002": {
        "user_message": "El valor ingresado para el parámetro no corresponde con su tipo de dato.",
        "technical_message": "Fallo en casting o validación de tipo de dato del parámetro (INTEGER, BOOLEAN, STRING).",
        "status_code": 400
    },

    # -------------------------------------------------------------------
    # SISTEMA Y BASE DE DATOS (SYS)
    # -------------------------------------------------------------------
    "SYS_001": {
        "user_message": "Ocurrió un error interno en el servidor. Por favor comuníquese con soporte si persiste.",
        "technical_message": "Unhandled internal server error / unhandled exception.",
        "status_code": 500
    },
    "SYS_002": {
        "user_message": "No fue posible conectar con la base de datos (SQL Server / SQLite).",
        "technical_message": "Database connection error / operational error / connection timeout.",
        "status_code": 503
    },
    "SYS_003": {
        "user_message": "Operación completada exitosamente.",
        "technical_message": "Operation completed with success.",
        "status_code": 200
    }
}

class AppException(Exception):
    """Excepción personalizada que vincula un código del catálogo con contexto técnico."""
    def __init__(self, code: str, custom_user_message: Optional[str] = None, technical_detail: Optional[str] = None):
        catalog_item = CATALOG.get(code, CATALOG["SYS_001"])
        self.code = code
        self.user_message = custom_user_message or catalog_item["user_message"]
        self.technical_message = technical_detail or catalog_item["technical_message"]
        self.status_code = catalog_item["status_code"]
        super().__init__(self.user_message)

def format_error_response(code: str, custom_user_message: Optional[str] = None, trace_id: Optional[str] = None) -> Dict[str, Any]:
    catalog_item = CATALOG.get(code, CATALOG["SYS_001"])
    return {
        "success": False,
        "error": {
            "code": code,
            "message": custom_user_message or catalog_item["user_message"],
            "trace_id": trace_id
        }
    }
