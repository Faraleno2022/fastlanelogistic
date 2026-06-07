@echo off
chcp 65001 >nul
title Création du package portable - Gestionnaire RH

echo ============================================
echo   CREATION DU PACKAGE PORTABLE
echo   (Inclut Python embarqué - Pas besoin d'installer Python)
echo ============================================
echo.

set PACKAGE_DIR=GestionnaireRH_Portable
set PYTHON_VERSION=3.11.9
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip

:: Créer le dossier de destination
if exist %PACKAGE_DIR% rmdir /s /q %PACKAGE_DIR%
mkdir %PACKAGE_DIR%

echo [INFO] Téléchargement de Python embarqué...
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile 'python_embed.zip'"

echo [INFO] Extraction de Python...
powershell -Command "Expand-Archive -Path 'python_embed.zip' -DestinationPath '%PACKAGE_DIR%\python' -Force"
del python_embed.zip

echo [INFO] Configuration de Python embarqué...
:: Activer pip dans Python embarqué
powershell -Command "(Get-Content '%PACKAGE_DIR%\python\python311._pth') -replace '#import site', 'import site' | Set-Content '%PACKAGE_DIR%\python\python311._pth'"

:: Télécharger get-pip
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PACKAGE_DIR%\python\get-pip.py'"

:: Installer pip
%PACKAGE_DIR%\python\python.exe %PACKAGE_DIR%\python\get-pip.py --no-warn-script-location
del %PACKAGE_DIR%\python\get-pip.py

echo [INFO] Installation des dépendances...
%PACKAGE_DIR%\python\python.exe -m pip install Django==5.2.11 python-decouple pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks django-filter djangorestframework reportlab openpyxl django-import-export django-axes django-cors-headers whitenoise django-csp requests python-dateutil --no-warn-script-location -q

echo [INFO] Copie des fichiers du projet...
xcopy /E /I /Y core %PACKAGE_DIR%\core
xcopy /E /I /Y employes %PACKAGE_DIR%\employes
xcopy /E /I /Y paie %PACKAGE_DIR%\paie
xcopy /E /I /Y temps_travail %PACKAGE_DIR%\temps_travail
xcopy /E /I /Y conges %PACKAGE_DIR%\conges
xcopy /E /I /Y contrats %PACKAGE_DIR%\contrats
xcopy /E /I /Y recrutement %PACKAGE_DIR%\recrutement
xcopy /E /I /Y formation %PACKAGE_DIR%\formation
xcopy /E /I /Y dashboard %PACKAGE_DIR%\dashboard
xcopy /E /I /Y payments %PACKAGE_DIR%\payments
xcopy /E /I /Y portail %PACKAGE_DIR%\portail
xcopy /E /I /Y comptabilite %PACKAGE_DIR%\comptabilite
xcopy /E /I /Y gestionnaire_rh %PACKAGE_DIR%\gestionnaire_rh
xcopy /E /I /Y templates %PACKAGE_DIR%\templates
xcopy /E /I /Y static %PACKAGE_DIR%\static
xcopy /E /I /Y staticfiles %PACKAGE_DIR%\staticfiles 2>nul
mkdir %PACKAGE_DIR%\media 2>nul
mkdir %PACKAGE_DIR%\logs 2>nul

copy manage.py %PACKAGE_DIR%\
copy db.sqlite3 %PACKAGE_DIR%\ 2>nul

echo [INFO] Création des scripts de lancement...

:: Créer le script de premier lancement
(
echo @echo off
echo chcp 65001 ^>nul
echo title Installation - Gestionnaire RH
echo echo ============================================
echo echo   PREMIERE INSTALLATION
echo echo ============================================
echo echo.
echo cd /d "%%~dp0"
echo if exist db.sqlite3 del db.sqlite3
echo python\python.exe manage.py migrate
echo echo.
echo echo Création du compte administrateur:
echo python\python.exe manage.py createsuperuser
echo echo.
echo echo Installation terminée! Lancez "Demarrer.bat"
echo pause
) > %PACKAGE_DIR%\Installation.bat

:: Créer le script de démarrage
(
echo @echo off
echo chcp 65001 ^>nul
echo title Gestionnaire RH Guinée
echo cd /d "%%~dp0"
echo echo ============================================
echo echo   GESTIONNAIRE RH GUINEE
echo echo   http://127.0.0.1:8000/
echo echo ============================================
echo echo.
echo start http://127.0.0.1:8000/
echo python\python.exe manage.py runserver 127.0.0.1:8000
echo pause
) > %PACKAGE_DIR%\Demarrer.bat

echo.
echo ============================================
echo   PACKAGE PORTABLE CREE AVEC SUCCES!
echo ============================================
echo.
echo Le package se trouve dans: %PACKAGE_DIR%\
echo.
echo Pour distribuer:
echo 1. Copiez le dossier "%PACKAGE_DIR%" sur une clé USB
echo 2. Sur le PC client:
echo    - Lancez "Installation.bat" (première fois uniquement)
echo    - Puis "Demarrer.bat" pour utiliser l'application
echo.
echo Taille approximative: ~200 Mo
echo.
pause
