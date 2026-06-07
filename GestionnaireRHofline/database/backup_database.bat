@echo off
REM ============================================
REM Script de sauvegarde de la base de données
REM Gestionnaire RH Guinée
REM ============================================

echo ============================================
echo Sauvegarde Base de Donnees RH Guinee
echo ============================================
echo.

REM Configuration
set DB_NAME=gestionnaire_rh
set DB_USER=rh_user
set DB_HOST=localhost
set DB_PORT=5432

REM Créer le dossier de sauvegarde s'il n'existe pas
set BACKUP_DIR=backups
if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

REM Générer le nom du fichier avec la date et l'heure
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%b%%a)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set BACKUP_FILE=%BACKUP_DIR%\backup_%DB_NAME%_%mydate%_%mytime%.sql

echo Date: %date%
echo Heure: %time%
echo Fichier: %BACKUP_FILE%
echo.

REM Demander le mot de passe
set /p DB_PASSWORD="Entrez le mot de passe de %DB_USER%: "
echo.

REM Effectuer la sauvegarde
echo Sauvegarde en cours...
set PGPASSWORD=%DB_PASSWORD%
pg_dump -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -F p -b -v -f %BACKUP_FILE% %DB_NAME%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo Sauvegarde terminee avec succes!
    echo ============================================
    echo Fichier: %BACKUP_FILE%
    
    REM Afficher la taille du fichier
    for %%A in (%BACKUP_FILE%) do echo Taille: %%~zA octets
) else (
    echo.
    echo ERREUR lors de la sauvegarde!
)

echo.
pause
