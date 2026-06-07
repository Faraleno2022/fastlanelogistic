@echo off
:: ============================================================
::  Arreter_GestionnaireRH.bat
::  Arrête le serveur GestionnaireRH proprement
::  Auteur : Guinée RH
:: ============================================================

title Arrêt de GestionnaireRH

echo.
echo  ====================================
echo   GestionnaireRH - Arrêt du serveur
echo  ====================================
echo.

:: Vérifier si le processus tourne
tasklist /FI "IMAGENAME eq GestionnaireRH.exe" 2>NUL | find /I "GestionnaireRH.exe" >NUL
if errorlevel 1 (
    echo  GestionnaireRH n'est pas en cours d'execution.
    echo.
    pause
    exit /b 0
)

echo  Arrêt de GestionnaireRH en cours...
taskkill /F /IM GestionnaireRH.exe >NUL 2>&1

if errorlevel 1 (
    echo  ERREUR : Impossible d'arrêter GestionnaireRH.
    echo  Essayez de fermer la fenêtre manuellement.
) else (
    echo  GestionnaireRH a été arrêté avec succès.
)

echo.
pause
