# -*- mode: python ; coding: utf-8 -*-
"""
GestionnaireRH — Spec PyInstaller pour l'Installateur Windows
==============================================================
Pour compiler :
    venv\Scripts\python.exe -m PyInstaller --clean --noconfirm installer_rh.spec

Produit : dist\Installer_GestionnaireRH.exe
Placer cet exe à côté du dossier dist\GestionnaireRH\ avant distribution.
"""
import os
PROJECT_DIR = SPECPATH

_icon = str(os.path.join(PROJECT_DIR, 'static', 'img', 'logo.ico'))
if not os.path.exists(_icon):
    _icon = None

a = Analysis(
    [os.path.join(PROJECT_DIR, 'installer_rh.py')],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'tkinter.messagebox', '_tkinter',
        'winreg', 'shutil', 'threading', 'pathlib',
        'encodings', 'encodings.utf_8', 'encodings.cp1252',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['django', 'matplotlib', 'numpy', 'pandas', 'scipy',
              'IPython', 'jupyter'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='Installer_GestionnaireRH',
    debug=False, bootloader_ignore_signals=False,
    strip=False, upx=True, upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False, target_arch=None,
    codesign_identity=None, entitlements_file=None,
    icon=_icon,
    onefile=True,
)
