@echo off
title Build Gestionnaire RH - Executable + Installateur

echo ============================================
echo   BUILD GESTIONNAIRE RH v1.1.0
echo   Executable + Installateur Windows
echo ============================================
echo.

python --version
if errorlevel 1 (
    echo [ERREUR] Python non trouve! Installez Python 3.10+
    pause
    exit /b 1
)
echo.

echo [1/5] Collecte des fichiers statiques...
python manage.py collectstatic --noinput
echo.

echo [2/5] Nettoyage des builds precedents...
if exist dist\GestionnaireRH rmdir /s /q dist\GestionnaireRH
if exist build rmdir /s /q build
echo   Nettoyage OK
echo.

echo [3/5] Preparation du dossier data_template...
if not exist installer\data_template mkdir installer\data_template
if not exist installer\data_template\logs mkdir installer\data_template\logs
if not exist installer\data_template\media mkdir installer\data_template\media
echo   data_template OK
echo.

echo [4/5] Build PyInstaller (cela peut prendre 5-10 minutes)...
echo.

pyinstaller --clean --noconfirm --distpath dist --workpath build installer\GestionnaireRH.spec

if errorlevel 1 (
    echo.
    echo [ERREUR] Build PyInstaller echoue!
    echo Verifiez que PyInstaller est installe: pip install pyinstaller
    pause
    exit /b 1
)

echo.
echo   Copie des fichiers supplementaires...
if not exist dist\GestionnaireRH\data mkdir dist\GestionnaireRH\data
if not exist dist\GestionnaireRH\data\logs mkdir dist\GestionnaireRH\data\logs
if not exist dist\GestionnaireRH\data\media mkdir dist\GestionnaireRH\data\media

if not exist dist\GestionnaireRH\templates xcopy /E /I /Y templates dist\GestionnaireRH\templates >nul 2>nul
if not exist dist\GestionnaireRH\static xcopy /E /I /Y static dist\GestionnaireRH\static >nul 2>nul
if not exist dist\GestionnaireRH\staticfiles xcopy /E /I /Y staticfiles dist\GestionnaireRH\staticfiles >nul 2>nul

echo   Build PyInstaller OK
echo.

echo [5/5] Creation de l'installateur Inno Setup...

set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"

if "%ISCC%"=="" (
    echo.
    echo   [ATTENTION] Inno Setup non trouve!
    echo   L'executable portable est pret dans: dist\GestionnaireRH\
    echo.
    echo   Pour creer l'installateur .exe avec raccourci bureau:
    echo   1. Installez Inno Setup depuis: https://jrsoftware.org/isdl.php
    echo   2. Relancez ce script
    echo   OU
    echo   3. Ouvrez installer\inno_setup.iss dans Inno Setup et compilez
    echo.
    goto end
)

"%ISCC%" installer\inno_setup.iss

if errorlevel 1 (
    echo.
    echo [ERREUR] Compilation Inno Setup echouee!
    echo L'executable portable reste disponible dans: dist\GestionnaireRH\
    pause
    exit /b 1
)

echo.
echo   Installateur cree avec succes!

:end
echo.
echo ============================================
echo   BUILD TERMINE AVEC SUCCES!
echo ============================================
echo.
echo Resultats:
echo.
if exist dist\GestionnaireRH\GestionnaireRH.exe echo   [OK] Executable portable: dist\GestionnaireRH\GestionnaireRH.exe
if exist dist\GestionnaireRH_Setup_1.1.0.exe echo   [OK] Installateur: dist\GestionnaireRH_Setup_1.1.0.exe
echo.
echo L'installateur:
echo   - Installe l'application dans Program Files
echo   - Cree un raccourci sur le Bureau
echo   - Cree un raccourci dans le menu Demarrer
echo   - Inclut un desinstallateur propre
echo   - Lance l'application apres installation
echo.
pause
