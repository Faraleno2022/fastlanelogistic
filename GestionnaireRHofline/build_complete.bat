@echo off
cd /d "%~dp0"
title Build GestionnaireRH - Executable Complet

echo ============================================
echo   BUILD GESTIONNAIRE RH v1.1.0
echo   Executable avec raccourci bureau + desinstallateur
echo ============================================
echo.

python --version
if errorlevel 1 (
    echo [ERREUR] Python non trouve! Installez Python 3.10+
    pause
    exit /b 1
)
echo.

echo [1/8] Verification des modules Nuitka compiles...
if not exist dist_nuitka\license_manager*.pyd (
    echo   [!] Modules Nuitka non trouves!
    echo   Lancez d'abord: compile_nuitka.bat
    echo   Les fichiers critiques seront proteges en .pyc uniquement
    echo.
) else (
    echo   Modules Nuitka trouves:
    dir /B dist_nuitka\*.pyd
    echo.
)

echo [2/8] Regeneration du manifest d'integrite...
python -c "from project_guardian import save_integrity_manifest; save_integrity_manifest(); print('  Manifest regenere OK')"
if errorlevel 1 (
    echo [AVERTISSEMENT] Impossible de regenerer le manifest d'integrite
    echo   Verifiez que vous etes sur la machine proprietaire
)
echo.

echo [3/8] Collecte des fichiers statiques...
python manage.py collectstatic --noinput
echo.

echo [4/8] Nettoyage des builds precedents...
if exist dist\GestionnaireRH rmdir /s /q dist\GestionnaireRH
if exist build rmdir /s /q build
echo   Nettoyage OK
echo.

echo [5/8] Preparation du dossier data_template...
if not exist data_template mkdir data_template
if not exist data_template\logs mkdir data_template\logs
if not exist data_template\media mkdir data_template\media
echo   data_template OK
echo.

echo [6/8] Build PyInstaller (cela peut prendre 5-10 minutes)...
echo.

pyinstaller --clean --noconfirm --distpath dist --workpath build GestionnaireRH_build.spec

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

echo   Copie du manifest d'integrite dans _internal...
copy /Y .integrity_manifest.json dist\GestionnaireRH\_internal\.integrity_manifest.json >nul
echo   (Les .pyd Nuitka sont deja dans _internal via PyInstaller — pas de .py a copier)
echo   Manifest copie OK

echo   Creation d'une base de donnees pre-migree pour les nouveaux clients...
if exist dist\GestionnaireRH\db_template.sqlite3 del dist\GestionnaireRH\db_template.sqlite3
python create_db_template.py "dist\GestionnaireRH\db_template.sqlite3"
echo   Base pre-migree OK

echo   Build PyInstaller OK
echo.

echo [7/8] Protection anti-edition de la distribution...
echo   Compilation .pyc + suppression sources + checksums + signature exe...
python protect_distribution.py dist\GestionnaireRH
if errorlevel 1 (
    echo   [AVERTISSEMENT] Protection partielle - verifiez les erreurs ci-dessus
) else (
    echo   Protection anti-edition OK
)
echo.

echo [8/8] Copie des scripts d'installation et desinstallation...
echo.

copy /Y scripts\Installer.bat dist\GestionnaireRH\Installer.bat >nul
copy /Y scripts\Desinstaller.bat dist\GestionnaireRH\Desinstaller.bat >nul

echo   Scripts copies dans dist\GestionnaireRH\
echo.

:end
echo.
echo ============================================
echo   BUILD TERMINE AVEC SUCCES!
echo ============================================
echo.
echo Resultats:
echo.
if exist dist\GestionnaireRH\GestionnaireRH.exe echo   [OK] Executable: dist\GestionnaireRH\GestionnaireRH.exe
if exist dist\GestionnaireRH\Installer.bat echo   [OK] Installateur: dist\GestionnaireRH\Installer.bat
if exist dist\GestionnaireRH\Demarrer.bat echo   [OK] Lanceur: dist\GestionnaireRH\Demarrer.bat
echo.
echo Pour distribuer:
echo 1. Copiez le dossier "dist\GestionnaireRH" sur une clé USB
echo 2. Sur le PC client, executez "Installer.bat"
echo 3. L'application sera installee dans C:\GestionnaireRH avec:
echo    - Raccourci sur le Bureau
echo    - Raccourci dans le menu Demarrer
echo    - Desinstallateur dans le menu Demarrer
echo.
pause
