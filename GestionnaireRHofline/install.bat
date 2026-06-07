@echo off
chcp 65001 >nul
title Installation - Gestionnaire RH Guinée

echo ============================================
echo   INSTALLATION - GESTIONNAIRE RH GUINEE
echo ============================================
echo.

:: Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installé!
    echo.
    echo Téléchargez Python depuis: https://www.python.org/downloads/
    echo Cochez "Add Python to PATH" lors de l'installation!
    echo.
    pause
    exit /b 1
)

echo [OK] Python détecté
python --version
echo.

:: Supprimer l'ancien venv s'il existe
if exist venv (
    echo [INFO] Suppression de l'ancien environnement virtuel...
    rmdir /s /q venv
)

:: Créer l'environnement virtuel
echo [INFO] Création de l'environnement virtuel...
python -m venv venv
if errorlevel 1 (
    echo [ERREUR] Impossible de créer l'environnement virtuel
    pause
    exit /b 1
)
echo [OK] Environnement virtuel créé
echo.

:: Activer l'environnement virtuel
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

:: Mettre à jour pip
echo [INFO] Mise à jour de pip...
python -m pip install --upgrade pip >nul 2>&1

:: Installer les dépendances
echo [INFO] Installation des dépendances (cela peut prendre quelques minutes)...
pip install Django==5.2.11 python-decouple pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks django-filter djangorestframework reportlab openpyxl django-import-export django-axes django-cors-headers django-celery-beat whitenoise django-csp requests python-dateutil

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)
echo [OK] Dépendances installées
echo.

:: Créer le dossier logs
if not exist logs mkdir logs

:: Supprimer l'ancienne base de données
if exist db.sqlite3 (
    echo [INFO] Suppression de l'ancienne base de données...
    del /f db.sqlite3
)

:: Appliquer les migrations
echo [INFO] Configuration de la base de données...
python manage.py migrate
if errorlevel 1 (
    echo [ERREUR] Erreur lors de la migration
    pause
    exit /b 1
)
echo [OK] Base de données configurée
echo.

:: Collecter les fichiers statiques
echo [INFO] Collecte des fichiers statiques...
python manage.py collectstatic --noinput >nul 2>&1
echo [OK] Fichiers statiques collectés
echo.

:: Créer le superuser
echo ============================================
echo   CREATION DU COMPTE ADMINISTRATEUR
echo ============================================
echo.
python manage.py createsuperuser

echo.
echo ============================================
echo   INSTALLATION TERMINEE AVEC SUCCES!
echo ============================================
echo.
echo Pour lancer l'application, double-cliquez sur:
echo   start.bat
echo.
echo Ou exécutez manuellement:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Puis ouvrez: http://127.0.0.1:8000/
echo.
pause
