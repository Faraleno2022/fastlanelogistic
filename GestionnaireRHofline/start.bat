@echo off
chcp 65001 >nul
title Gestionnaire RH Guinée

echo ============================================
echo   GESTIONNAIRE RH GUINEE - DEMARRAGE
echo ============================================
echo.

:: Vérifier si le venv existe
if not exist venv (
    echo [ERREUR] L'environnement virtuel n'existe pas!
    echo Veuillez d'abord exécuter install.bat
    pause
    exit /b 1
)

:: Activer l'environnement virtuel
call venv\Scripts\activate.bat

echo [INFO] Démarrage du serveur...
echo.
echo ============================================
echo   APPLICATION DISPONIBLE SUR:
echo   http://127.0.0.1:8000/
echo ============================================
echo.
echo Appuyez sur CTRL+C pour arrêter le serveur
echo.

:: Ouvrir le navigateur automatiquement après 2 secondes
start /b cmd /c "timeout /t 2 >nul && start http://127.0.0.1:8000/"

:: Lancer le serveur
python manage.py runserver

pause
