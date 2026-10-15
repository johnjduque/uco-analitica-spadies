# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

backend_dir = os.path.abspath(os.path.join(os.getcwd(), 'backend'))
frontend_dir = os.path.abspath(os.path.join(os.getcwd(), 'frontend'))
data_dir = os.path.abspath(os.path.join(os.getcwd(), 'Data'))

datas = [
    (frontend_dir, 'frontend'),
    (data_dir, 'Data')
]

a = Analysis(
    [os.path.join(backend_dir, 'app', 'main.py')],
    pathex=[backend_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'sqlalchemy.ext.baked',
        'pandas',
        'xlrd',
        'openpyxl',
        'pyodbc',
        'jwt',
        'bcrypt',
        'passlib',
        'passlib.handlers.bcrypt',
        'passlib.handlers.pbkdf2',
        'dotenv'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='UcoMapAnalytics',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon=None,
)
