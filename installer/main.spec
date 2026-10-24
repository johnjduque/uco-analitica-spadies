# -*- mode: python ; coding: utf-8 -*-
# Empaquetado del ejecutable de escritorio (Windows) con PyInstaller.
# Normalmente se ejecuta con scripts\generar_instalador.bat (doble clic).
# Manual (desde la carpeta installer, con el entorno virtual activo):
#   1. cd ..\frontend && npm ci && npm run build
#   2. cd ..\installer && python -m PyInstaller main.spec --noconfirm
# Resultado: installer\dist\UcoAnalytics.exe

import os
from PyInstaller.utils.hooks import collect_submodules

root_dir = os.path.abspath(os.path.join(SPECPATH, '..'))
backend_dir = os.path.join(root_dir, 'backend')
frontend_dist = os.path.join(root_dir, 'frontend', 'dist')

if not os.path.exists(os.path.join(frontend_dist, 'index.html')):
    raise SystemExit('Falta compilar el frontend: ejecute "npm run build" en la carpeta frontend.')

# Módulos de la versión anterior que pueden seguir en disco si no se ejecutó la limpieza
_OBSOLETE = {'app.auth', 'app.seed', 'app.schemas', 'app.ingestion', 'app.database', 'app.analytics_engine',
             'app.program_codes', 'app.services.load_service', 'app.services.analytics_service', 'app.routers.analytics'}

hidden = (
    collect_submodules('uvicorn')
    + collect_submodules('app', filter=lambda name: name not in _OBSOLETE)
    + ['sqlalchemy.dialects.sqlite', 'sqlalchemy.dialects.mssql', 'pyodbc',
       'openpyxl', 'xlrd', 'bcrypt', 'jwt', 'dotenv', 'multipart', 'python_multipart']
)

a = Analysis(
    [os.path.join(backend_dir, 'desktop_main.py')],
    pathex=[backend_dir],
    binaries=[],
    datas=[(frontend_dist, os.path.join('frontend', 'dist'))],
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'IPython', 'pytest', 'reportlab'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='UcoAnalytics',
    debug=False,
    strip=False,
    upx=False,
    console=True,
    icon=None,
)
