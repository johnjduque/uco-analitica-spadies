"""
PUNTO DE ENTRADA PARA DESARROLLO
    python main.py        -> servidor en http://127.0.0.1:8000 con recarga automática
En servidor use:  uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
"""

import uvicorn

from app.main import app  # noqa: F401  (expone app para "uvicorn main:app")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
