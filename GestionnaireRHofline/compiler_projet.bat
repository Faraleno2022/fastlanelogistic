@echo off
chcp 65001 >nul
title Compilation Protégée - Gestionnaire RH

echo ============================================
echo   COMPILATION PROTEGEE DU PROJET
echo   (Code source converti en binaire)
echo ============================================
echo.

:: Vérifier la version de Python
python --version 2>&1 | findstr "3.14" >nul
if not errorlevel 1 (
    echo [ERREUR] Python 3.14 détecté - NON COMPATIBLE avec Nuitka!
    echo.
    echo Veuillez installer Python 3.13 ou 3.12:
    echo   https://www.python.org/downloads/release/python-3130/
    echo.
    echo Cochez "Add Python to PATH" lors de l'installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Version Python compatible
python --version
echo.
echo Cette opération va:
echo - Compiler le code Python en binaire C
echo - Rendre le code source illisible
echo - Créer un package protégé (dossier standalone)
echo.
echo ATTENTION: Cette opération peut prendre 30-60 minutes!
echo.
pause

:: Activer l'environnement virtuel
call venv\Scripts\activate.bat

:: Collecter les fichiers statiques
echo [INFO] Collecte des fichiers statiques...
python manage.py collectstatic --noinput

:: Compiler avec Nuitka - MODE STANDALONE (stable pour Django)
echo.
echo [INFO] Compilation avec Nuitka (mode standalone - recommandé pour Django)...
echo.

python -m nuitka ^
    --standalone ^
    --enable-plugin=django ^
    --output-dir=nuitka_build ^
    --include-data-dir=templates=templates ^
    --include-data-dir=static=static ^
    --include-data-dir=staticfiles=staticfiles ^
    --include-data-dir=media=media ^
    --module-parameter=django-settings-module=gestionnaire_rh.settings ^
    run_server.py

if errorlevel 1 (
    echo.
    echo [ERREUR] Compilation Nuitka échouée.
    echo.
    echo Solutions possibles:
    echo 1. Installez Visual Studio Build Tools
    echo 2. Vérifiez que Python 3.13 ou 3.12 est utilisé
    echo 3. Essayez PyInstaller comme alternative
    echo.
    pause
    exit /b 1
)

:: Copier les fichiers nécessaires
echo.
echo [INFO] Copie des fichiers supplémentaires...
copy db.sqlite3 nuitka_build\run_server.dist\ 2>nul
xcopy /E /I /Y media nuitka_build\run_server.dist\media 2>nul
mkdir nuitka_build\run_server.dist\logs 2>nul

:: Créer le lanceur
echo [INFO] Création du lanceur...
(
echo @echo off
echo chcp 65001 ^>nul
echo title Gestionnaire RH Guinée
echo cd /d "%%~dp0"
echo echo ============================================
echo echo   GESTIONNAIRE RH GUINEE
echo echo   http://127.0.0.1:8000/
echo echo ============================================
echo start http://127.0.0.1:8000/
echo run_server.exe
echo pause
) > nuitka_build\run_server.dist\Demarrer.bat

echo.
echo ============================================
echo   COMPILATION TERMINEE AVEC SUCCES!
echo ============================================
echo.
echo Le package protégé se trouve dans:
echo   nuitka_build\run_server.dist\
echo.
echo Pour distribuer:
echo 1. Copiez le dossier "run_server.dist" sur une clé USB
echo 2. Renommez-le en "GestionnaireRH"
echo 3. Le client lance "Demarrer.bat"
echo.
echo Le code source est maintenant PROTEGE (compilé en binaire)
echo.
pause
