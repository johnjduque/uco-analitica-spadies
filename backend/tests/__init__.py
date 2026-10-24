"""
Pruebas automáticas de UCO Analytics.

Ejecutar desde la carpeta backend:
    python -m unittest discover -s tests -v
(o con pytest:  python -m pytest tests)

Las pruebas usan una base SQLite temporal y nunca tocan datos reales.
La validación contra SPADIES (test_spadies_validation) se ejecuta solo si se
define la variable UCO_DATOS_DIR con la carpeta Datos_UCO.
"""

import os
import tempfile

_TMP = tempfile.mkdtemp(prefix="uco_tests_")
os.environ["PERSISTENT_DIR"] = _TMP
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_TMP, 'test.db')}"
os.environ["APP_ENV"] = "desarrollo"
os.environ["INITIAL_ADMIN_USERNAME"] = "admin"
os.environ["INITIAL_ADMIN_PASSWORD"] = "Temporal123"
os.environ.pop("SECRET_KEY", None)
