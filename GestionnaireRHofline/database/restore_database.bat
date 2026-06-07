@echo off
REM ============================================
REM Script de restauration de la base de données
REM Gestionnaire RH Guinée
REM ============================================

echo ============================================
echo Restauration Base de Donnees RH Guinee
echo ============================================
echo.

REM Configuration
set DB_NAME=gestionnaire_rh
set DB_USER=rh_user
set DB_HOST=localhost
set DB_PORT=5432

REM Lister les fichiers de sauvegarde disponibles
echo Fichiers de sauvegarde disponibles:
echo.
dir /b backups\*.sql
echo.

REM Demander le fichier à restaurer
set /p BACKUP_FILE="Entrez le nom du fichier de sauvegarde (avec extension .sql): "
set BACKUP_PATH=backups\%BACKUP_FILE%

if not exist %BACKUP_PATH% (
    echo ERREUR: Le fichier %BACKUP_PATH% n'existe pas!
    pause
    exit /b 1
)

echo.
echo ATTENTION: Cette operation va ECRASER toutes les donnees actuelles!
set /p CONFIRM="Etes-vous sur de vouloir continuer? (OUI/NON): "

if /i not "%CONFIRM%"=="OUI" (
    echo Operation annulee.
    pause
    exit /b 0
)

REM Demander le mot de passe
echo.
set /p DB_PASSWORD="Entrez le mot de passe de %DB_USER%: "
echo.

REM Restaurer la base de données
echo Restauration en cours...
set PGPASSWORD=%DB_PASSWORD%

REM Déconnecter tous les utilisateurs
psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%DB_NAME%';" 2>nul

REM Supprimer et recréer la base
psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "DROP DATABASE IF EXISTS %DB_NAME%;" 2>nul
psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "CREATE DATABASE %DB_NAME%;" 2>nul
psql -U postgres -h %DB_HOST% -p %DB_PORT% -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;" 2>nul

REM Restaurer les données
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f %BACKUP_PATH%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo Restauration terminee avec succes!
    echo ============================================
) else (
    echo.
    echo ERREUR lors de la restauration!
)

echo.
pause
