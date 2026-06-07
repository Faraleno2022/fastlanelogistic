@echo off
title Desinstallation - GestionnaireRH

echo ============================================
echo   DESINSTALLATION GESTIONNAIRE RH
echo ============================================
echo.

echo Fermeture de l'application si elle tourne...
taskkill /F /IM GestionnaireRH.exe >nul 2>nul
timeout /t 2 /nobreak >nul

echo.
set /p CONFIRM="Voulez-vous vraiment desinstaller GestionnaireRH ? (O/N): "
if /i not "%CONFIRM%"=="O" (
    echo Desinstallation annulee.
    pause
    exit /b 0
)

echo.
echo Suppression du raccourci Bureau...
del "%USERPROFILE%\Desktop\GestionnaireRH.lnk" >nul 2>nul

echo Suppression des raccourcis Menu Demarrer...
rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\GestionnaireRH" >nul 2>nul

echo Suppression des fichiers de l'application...
echo (Le dossier C:\GestionnaireRH sera supprime)

cd /d "%USERPROFILE%"
rmdir /s /q "C:\GestionnaireRH" >nul 2>nul

echo.
echo ============================================
echo   DESINSTALLATION TERMINEE!
echo ============================================
echo.
echo GestionnaireRH a ete completement supprime.
echo.
pause
