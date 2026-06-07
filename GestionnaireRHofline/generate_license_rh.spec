# -*- mode: python ; coding: utf-8 -*-
"""
GestionnaireRH — Spec PyInstaller pour le Générateur de Licences (distributeur)
=================================================================================
Pour compiler :
    venv\Scripts\python.exe -m PyInstaller --clean --noconfirm generate_license_rh.spec

Produit : dist\GenerateurLicencesRH.exe  (outil confidentiel du distributeur)
"""
import os
PROJECT_DIR = SPECPATH

_icon = str(os.path.join(PROJECT_DIR, 'static', 'img', 'logo.ico'))
if not os.path.exists(_icon):
    _icon = None

a = Analysis(
    [os.path.join(PROJECT_DIR, 'generate_license_gui.py')],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=[
        (os.path.join(PROJECT_DIR, 'license_manager.py'), '.'),
    ],
    hiddenimports=[
        'license_manager',
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
        '_tkinter',
        'winreg', 'hmac', 'hashlib', 'json', 'base64', 'uuid',
        'socket', 'platform', 'encodings', 'encodings.utf_8', 'encodings.cp1252',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['django', 'weasyprint', 'reportlab', 'PIL', 'pandas', 'numpy',
              'matplotlib', 'scipy', 'IPython'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='GenerateurLicencesRH',
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
