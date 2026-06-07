@echo off
:: ============================================================
::  desinstaller.bat
::  Désinstallation propre de GestionnaireRH
::  Auteur : Guinée RH
:: ============================================================

title Désinstallation de GestionnaireRH

echo.
echo  ====================================
echo   GestionnaireRH - Désinstallation
echo  ====================================
echo.

:: Arrêter le serveur s'il tourne
tasklist /FI "IMAGENAME eq GestionnaireRH.exe" 2>NUL | find /I "GestionnaireRH.exe" >NUL
if not errorlevel 1 (
    echo  Arrêt du serveur GestionnaireRH...
    taskkill /F /IM GestionnaireRH.exe >NUL 2>&1
)

:: Proposer une sauvegarde de la base de données
set "BACKUP_DIR=%USERPROFILE%\Documents\GestionnaireRH_Backup"
if exist "%~dp0db.sqlite3" (
    echo.
    set /p BACKUP_CHOICE="Voulez-vous sauvegarder votre base de données ? (O/N) : "
    if /i "!BACKUP_CHOICE!"=="O" (
        if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
        for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set "D=%%c%%b%%a"
        for /f "tokens=1-2 delims=: " %%a in ("%time%") do set "T=%%a%%b"
        copy "%~dp0db.sqlite3" "%BACKUP_DIR%\db_backup_%D%_%T%.sqlite3" >NUL
        echo  Base de données sauvegardée dans : %BACKUP_DIR%
    )
)

echo.
echo  Suppression du raccourci Bureau...
del /f /q "%PUBLIC%\Desktop\GestionnaireRH.lnk" >NUL 2>&1
del /f /q "%USERPROFILE%\Desktop\GestionnaireRH.lnk" >NUL 2>&1

echo  Suppression des entrées du menu Démarrer...
rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\GestionnaireRH" >NUL 2>&1

echo  Suppression des clés de registre...
reg delete "HKCU\Software\Guinée RH\GestionnaireRH" /f >NUL 2>&1

echo.
echo  Désinstallation terminée.
echo  Les données utilisateur (media, backups) ont été conservées.
echo.
pause
