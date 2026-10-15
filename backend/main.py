"""
PUNTO DE ENTRADA PRINCIPAL DEL BACKEND
Universidad Católica de Oriente - Sistema Analítico de Deserción

Re-exporta la aplicación FastAPI desacoplada en Clean Architecture (app.main:app)
manteniendo compatibilidad total con PyInstaller, uvicorn y Docker.
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)