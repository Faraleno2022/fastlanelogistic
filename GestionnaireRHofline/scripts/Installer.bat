@echo off
title Installation - GestionnaireRH

echo ============================================
echo   INSTALLATION GESTIONNAIRE RH
echo ============================================
echo.

set "INSTALL_DIR=C:\GestionnaireRH"
set "SOURCE_DIR=%~dp0"

echo Installation dans %INSTALL_DIR%...
echo.

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Copie des fichiers (cela peut prendre quelques minutes)...
robocopy "%SOURCE_DIR%." "%INSTALL_DIR%" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul 2>nul

if not exist "%INSTALL_DIR%\GestionnaireRH.exe" (
    echo [ERREUR] La copie a echoue! Essayez d'executer en tant qu'administrateur.
    pause
    exit /b 1
)

echo Copie terminee.
echo.

echo Verification des fichiers...
if not exist "%INSTALL_DIR%\_internal\static" (
    echo [ATTENTION] Fichiers statiques manquants, nouvelle tentative...
    robocopy "%SOURCE_DIR%_internal" "%INSTALL_DIR%\_internal" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul 2>nul
)
echo Verification OK.
echo.

echo Creation du raccourci sur le Bureau...
powershell -NoProfile -Command "try { $ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine($ws.SpecialFolders('Desktop'), 'GestionnaireRH.lnk')); $s.TargetPath = 'C:\GestionnaireRH\GestionnaireRH.exe'; $s.WorkingDirectory = 'C:\GestionnaireRH'; $s.IconLocation = 'C:\GestionnaireRH\_internal\static\img\logo.ico,0'; $s.Description = 'GestionnaireRH - Gestion RH Guinee'; $s.Save(); Write-Host '  [OK] Raccourci Bureau cree' } catch { Write-Host '  [ERREUR] Impossible de creer le raccourci Bureau' }"

echo Creation du raccourci dans le menu Demarrer...
powershell -NoProfile -Command "try { $dir = [System.IO.Path]::Combine($env:APPDATA, 'Microsoft\Windows\Start Menu\Programs\GestionnaireRH'); if (!(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }; $ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine($dir, 'GestionnaireRH.lnk')); $s.TargetPath = 'C:\GestionnaireRH\GestionnaireRH.exe'; $s.WorkingDirectory = 'C:\GestionnaireRH'; $s.IconLocation = 'C:\GestionnaireRH\_internal\static\img\logo.ico,0'; $s.Description = 'GestionnaireRH - Gestion RH Guinee'; $s.Save(); $s2 = $ws.CreateShortcut([System.IO.Path]::Combine($dir, 'Desinstaller.lnk')); $s2.TargetPath = 'C:\GestionnaireRH\Desinstaller.bat'; $s2.WorkingDirectory = 'C:\GestionnaireRH'; $s2.Save(); Write-Host '  [OK] Raccourcis Menu Demarrer crees' } catch { Write-Host '  [ERREUR] Impossible de creer les raccourcis Menu Demarrer' }"

echo.
echo ============================================
echo   INSTALLATION TERMINEE!
echo ============================================
echo.
echo L'application est installee dans %INSTALL_DIR%
echo.
echo Raccourcis crees:
echo   - Bureau: GestionnaireRH
echo   - Menu Demarrer: GestionnaireRH
echo   - Menu Demarrer: Desinstaller
echo.
echo Pour lancer: double-cliquez sur le raccourci GestionnaireRH sur le Bureau
echo Pour desinstaller: Menu Demarrer - GestionnaireRH - Desinstaller
echo.
pause
