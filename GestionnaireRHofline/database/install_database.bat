@echo off
REM ============================================
REM Script d'installation de la base de données
REM Gestionnaire RH Guinée
REM ============================================

echo ============================================
echo Installation Base de Donnees RH Guinee
echo ============================================
echo.

REM Configuration
set DB_NAME=gestionnaire_rh
set DB_USER=rh_user
set DB_HOST=localhost
set DB_PORT=5432

REM Vérifier si PostgreSQL est installé
where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: PostgreSQL n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer PostgreSQL et reessayer
    pause
    exit /b 1
)

echo [1/7] Verification de PostgreSQL... OK
echo.

REM Demander le mot de passe postgres
set /p POSTGRES_PWD="Entrez le mot de passe de l'utilisateur postgres: "
echo.

REM Créer la base de données et l'utilisateur
echo [2/7] Creation de la base de donnees et de l'utilisateur...
psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "CREATE DATABASE %DB_NAME%;" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Base de donnees creee avec succes
) else (
    echo La base de donnees existe deja ou erreur de creation
)

set /p DB_PASSWORD="Entrez le mot de passe pour l'utilisateur %DB_USER%: "
psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "CREATE USER %DB_USER% WITH PASSWORD '%DB_PASSWORD%';" 2>nul
psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;" 2>nul
echo.

REM Créer le schéma (tables)
echo [3/7] Creation du schema (tables)...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f schema_complete.sql
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR lors de la creation du schema
    pause
    exit /b 1
)
echo Schema cree avec succes
echo.

REM Créer les vues et index
echo [4/7] Creation des vues et index...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f views_and_indexes.sql
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR lors de la creation des vues et index
    pause
    exit /b 1
)
echo Vues et index crees avec succes
echo.

REM Créer les fonctions et procédures
echo [5/7] Creation des fonctions et procedures...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f functions_procedures.sql
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR lors de la creation des fonctions
    pause
    exit /b 1
)
echo Fonctions et procedures creees avec succes
echo.

REM Insérer les données initiales
echo [6/7] Insertion des donnees initiales...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f data_init_guinee.sql
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR lors de l'insertion des donnees
    pause
    exit /b 1
)
echo Donnees initiales inserees avec succes
echo.

REM Créer le fichier .env pour Django
echo [7/7] Creation du fichier de configuration Django...
(
echo # Configuration Base de Donnees
echo DB_NAME=%DB_NAME%
echo DB_USER=%DB_USER%
echo DB_PASSWORD=%DB_PASSWORD%
echo DB_HOST=%DB_HOST%
echo DB_PORT=%DB_PORT%
echo.
echo # Django
echo SECRET_KEY=votre-cle-secrete-a-changer
echo DEBUG=True
echo ALLOWED_HOSTS=localhost,127.0.0.1
) > ..\.env
echo Fichier .env cree
echo.

echo ============================================
echo Installation terminee avec succes!
echo ============================================
echo.
echo Base de donnees: %DB_NAME%
echo Utilisateur: %DB_USER%
echo Host: %DB_HOST%
echo Port: %DB_PORT%
echo.
echo Prochaines etapes:
echo 1. Verifiez le fichier .env a la racine du projet
echo 2. Executez: python manage.py migrate
echo 3. Executez: python manage.py createsuperuser
echo 4. Executez: python manage.py runserver
echo.
pause
