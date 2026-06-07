@echo off
title Compilation Nuitka - Modules Critiques GestionnaireRH
chcp 65001 >nul 2>nul

echo ============================================
echo   COMPILATION NUITKA — MODULES CRITIQUES
echo   Protection anti-édition (binaire natif)
echo   © ICG Guinea
echo ============================================
echo.

:: Vérifier que Nuitka est installé
python -m nuitka --version >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] Nuitka non installe!
    echo Installez-le avec: pip install nuitka
    echo.
    echo Alternative: pip install nuitka ordered-set
    pause
    exit /b 1
)
echo [OK] Nuitka detecte
echo.

:: Vérifier que Python dev headers sont disponibles
python -c "import sysconfig; print(sysconfig.get_path('include'))" >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] En-tetes Python non trouvees
    pause
    exit /b 1
)

:: Créer le dossier de sortie
if not exist dist_nuitka mkdir dist_nuitka
echo [OK] Dossier dist_nuitka pret
echo.

:: ═════════════════════════════════════════════════════════════════════════════
:: MODULE 1 : license_manager.py (déjà compilé probablement)
:: ═════════════════════════════════════════════════════════════════════════════
echo [1/3] Compilation de license_manager.py...
if exist dist_nuitka\license_manager*.pyd (
    echo   → Deja compile, verification...
    python -c "import importlib.util; spec = importlib.util.spec_from_file_location('lm', list(__import__('pathlib').Path('dist_nuitka').glob('license_manager*.pyd'))[0]); print('  OK: ', spec.origin)" 2>nul
    if errorlevel 1 (
        echo   → Recompilation necessaire...
        goto compile_lm
    ) else (
        echo   → Module valide, pas de recompilation
        goto skip_lm
    )
)
:compile_lm
python -m nuitka --module ^
    --output-dir=dist_nuitka ^
    --remove-output ^
    --no-pyi-file ^
    --python-flag=no_docstrings ^
    --python-flag=no_asserts ^
    license_manager.py
if errorlevel 1 (
    echo   [ERREUR] Echec compilation license_manager.py
) else (
    echo   [OK] license_manager.py compile en .pyd
)
:skip_lm
echo.

:: ═════════════════════════════════════════════════════════════════════════════
:: MODULE 2 : project_guardian.py
:: ═════════════════════════════════════════════════════════════════════════════
echo [2/3] Compilation de project_guardian.py...
python -m nuitka --module ^
    --output-dir=dist_nuitka ^
    --remove-output ^
    --no-pyi-file ^
    --python-flag=no_docstrings ^
    --python-flag=no_asserts ^
    project_guardian.py
if errorlevel 1 (
    echo   [ERREUR] Echec compilation project_guardian.py
    echo   Le fichier sera protege par compilation .pyc a la place
) else (
    echo   [OK] project_guardian.py compile en .pyd
)
echo.

:: ═════════════════════════════════════════════════════════════════════════════
:: MODULE 3 : runtime_shield.py
:: ═════════════════════════════════════════════════════════════════════════════
echo [3/3] Compilation de runtime_shield.py...
python -m nuitka --module ^
    --output-dir=dist_nuitka ^
    --remove-output ^
    --no-pyi-file ^
    --python-flag=no_docstrings ^
    --python-flag=no_asserts ^
    runtime_shield.py
if errorlevel 1 (
    echo   [ERREUR] Echec compilation runtime_shield.py
    echo   Le fichier sera protege par compilation .pyc a la place
) else (
    echo   [OK] runtime_shield.py compile en .pyd
)
echo.

:: ═════════════════════════════════════════════════════════════════════════════
:: RÉSUMÉ
:: ═════════════════════════════════════════════════════════════════════════════
echo ============================================
echo   COMPILATION TERMINÉE
echo ============================================
echo.
echo Modules compiles dans dist_nuitka/:
echo.
dir /B dist_nuitka\*.pyd 2>nul
echo.
echo Ces fichiers .pyd sont des binaires natifs Windows.
echo Ils ne peuvent PAS etre:
echo   - Ouverts dans un editeur de texte
echo   - Decompiles en code source Python
echo   - Modifies sans les rendre inutilisables
echo.
echo Prochaine etape: Lancez build_complete.bat pour
echo integrer ces modules dans l'executable final.
echo.
pause
