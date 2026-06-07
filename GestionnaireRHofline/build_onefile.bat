@echo off
chcp 65001 >nul
title Build ONEFILE + Installateur - Gestionnaire RH

echo ============================================
echo   BUILD ONEFILE + INSTALLATEUR
echo   Gestionnaire RH Guinée
echo ============================================
echo.

:: Vérifier Python
python --version
echo.

:: Collecter les fichiers statiques
echo [1/5] Collecte des fichiers statiques...
python manage.py collectstatic --noinput
echo.

:: Vérifications Django
echo [2/5] Vérifications Django...
python manage.py check --no-color
python manage.py makemigrations --check --no-color
echo.

:: Nettoyer les anciens builds onefile
echo [3/5] Nettoyage...
if exist installer\dist_onefile rmdir /s /q installer\dist_onefile
if exist installer\build_onefile rmdir /s /q installer\build_onefile
echo.

:: Build PyInstaller ONEFILE
echo [4/5] Build PyInstaller --onefile (cela peut prendre 10-15 minutes)...
echo.
pyinstaller --clean --noconfirm ^
    --distpath installer\dist_onefile ^
    --workpath installer\build_onefile ^
    installer\GestionnaireRH_onefile.spec

if errorlevel 1 (
    echo.
    echo [ERREUR] Build PyInstaller échoué!
    pause
    exit /b 1
)

:: Vérifier que l'exe existe
if not exist installer\dist_onefile\GestionnaireRH.exe (
    echo [ERREUR] GestionnaireRH.exe non trouvé!
    pause
    exit /b 1
)

echo.
echo [OK] GestionnaireRH.exe créé avec succès!
echo.

:: Tenter de construire l'installateur Inno Setup
echo [5/5] Construction de l'installateur Inno Setup...
set ISCC_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe

if "%ISCC_PATH%"=="" (
    echo.
    echo [INFO] Inno Setup non trouvé sur ce PC.
    echo        Pour créer l'installateur .exe avec raccourci bureau:
    echo        1. Téléchargez Inno Setup: https://jrsoftware.org/isdl.php
    echo        2. Installez-le
    echo        3. Relancez ce script
    echo.
    echo        En attendant, le fichier portable est disponible:
    echo        installer\dist_onefile\GestionnaireRH.exe
) else (
    echo Inno Setup trouvé: %ISCC_PATH%
    mkdir installer\output 2>nul
    "%ISCC_PATH%" installer\inno_setup_onefile.iss
    if errorlevel 1 (
        echo [ERREUR] Inno Setup a échoué!
    ) else (
        echo.
        echo [OK] Installateur créé: installer\output\GestionnaireRH_Setup_1.0.0.exe
    )
)

echo.
echo ============================================
echo   BUILD TERMINE!
echo ============================================
echo.
echo Fichiers générés:
echo   - EXE portable: installer\dist_onefile\GestionnaireRH.exe
if exist installer\output\GestionnaireRH_Setup_1.0.0.exe (
echo   - Installateur: installer\output\GestionnaireRH_Setup_1.0.0.exe
echo.
echo L'installateur crée automatiquement:
echo   - Un raccourci sur le Bureau avec le logo
echo   - Un raccourci dans le menu Démarrer
echo   - Un désinstallateur propre
)
echo.
pause
