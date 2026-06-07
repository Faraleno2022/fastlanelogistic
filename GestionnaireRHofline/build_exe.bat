@echo off
chcp 65001 >nul
title Création de l'exécutable - Gestionnaire RH

echo ============================================
echo   CREATION DE L'EXECUTABLE AUTONOME
echo ============================================
echo.

:: Activer l'environnement virtuel
call venv\Scripts\activate.bat

:: Collecter les fichiers statiques
echo [INFO] Collecte des fichiers statiques...
python manage.py collectstatic --noinput

:: Créer l'exécutable
echo [INFO] Création de l'exécutable (cela peut prendre plusieurs minutes)...
pyinstaller --name="GestionnaireRH" ^
    --onedir ^
    --console ^
    --icon=static/img/logo.ico ^
    --add-data="templates;templates" ^
    --add-data="static;static" ^
    --add-data="staticfiles;staticfiles" ^
    --add-data="core;core" ^
    --add-data="employes;employes" ^
    --add-data="paie;paie" ^
    --add-data="temps_travail;temps_travail" ^
    --add-data="conges;conges" ^
    --add-data="contrats;contrats" ^
    --add-data="recrutement;recrutement" ^
    --add-data="formation;formation" ^
    --add-data="dashboard;dashboard" ^
    --add-data="payments;payments" ^
    --add-data="portail;portail" ^
    --add-data="comptabilite;comptabilite" ^
    --add-data="gestionnaire_rh;gestionnaire_rh" ^
    --hidden-import=django ^
    --hidden-import=django.contrib.admin ^
    --hidden-import=django.contrib.auth ^
    --hidden-import=django.contrib.contenttypes ^
    --hidden-import=django.contrib.sessions ^
    --hidden-import=django.contrib.messages ^
    --hidden-import=django.contrib.staticfiles ^
    --hidden-import=reportlab ^
    --hidden-import=PIL ^
    --hidden-import=openpyxl ^
    --collect-all=django ^
    --collect-all=crispy_forms ^
    --collect-all=crispy_bootstrap5 ^
    run_server.py

if errorlevel 1 (
    echo [ERREUR] Erreur lors de la création de l'exécutable
    pause
    exit /b 1
)

:: Copier la base de données et les fichiers nécessaires
echo [INFO] Copie des fichiers supplémentaires...
copy db.sqlite3 dist\GestionnaireRH\ 2>nul
xcopy /E /I /Y media dist\GestionnaireRH\media 2>nul
xcopy /E /I /Y logs dist\GestionnaireRH\logs 2>nul

echo.
echo ============================================
echo   EXECUTABLE CREE AVEC SUCCES!
echo ============================================
echo.
echo L'exécutable se trouve dans: dist\GestionnaireRH\
echo.
echo Pour distribuer:
echo 1. Copiez le dossier dist\GestionnaireRH\ sur une clé USB
echo 2. Sur le PC client, lancez GestionnaireRH.exe
echo.
pause
