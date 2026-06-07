@echo off
chcp 65001 >nul 2>&1
title MiseAJour - GestionnaireRH
color 0A

echo ============================================================
echo    MISE A JOUR - GestionnaireRH
echo    Applique les corrections sans toucher la base de donnees
echo    ni les fichiers utilisateur
echo ============================================================
echo.

set "SOURCE=C:\Users\LENO\Desktop\GestionnaireRHofline\dist\GestionnaireRH"
set "DEST=C:\GestionnaireRH"

:: Vérifier que le dossier source existe
if not exist "%SOURCE%\GestionnaireRH.exe" (
    echo [ERREUR] Le build n'existe pas dans %SOURCE%
    echo Veuillez d'abord compiler le projet avec PyInstaller.
    pause
    exit /b 1
)

:: Vérifier que le dossier destination existe
if not exist "%DEST%" (
    echo [ERREUR] Le dossier d'installation %DEST% n'existe pas.
    echo Veuillez d'abord installer l'application avec Installer.bat.
    pause
    exit /b 1
)

echo [1/5] Arret de l'application si elle est en cours...
taskkill /F /IM GestionnaireRH.exe >nul 2>&1
timeout /t 2 /noq >nul

echo [2/5] Sauvegarde des fichiers utilisateur...
:: Sauvegarder la base de données et fichiers utilisateur
if exist "%DEST%\db.sqlite3" (
    copy /Y "%DEST%\db.sqlite3" "%DEST%\db.sqlite3.backup" >nul 2>&1
    echo   [OK] Base de donnees sauvegardee (db.sqlite3.backup)
)
if exist "%DEST%\media" (
    echo   [OK] Dossier media preserve (non touche)
)

echo [3/5] Copie des fichiers de l'application (sans DB ni media)...

:: Copier l'executable principal
copy /Y "%SOURCE%\GestionnaireRH.exe" "%DEST%\GestionnaireRH.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] GestionnaireRH.exe mis a jour
) else (
    echo   [ERREUR] Impossible de copier GestionnaireRH.exe
    echo   L'application est peut-etre encore en cours d'execution.
    pause
    exit /b 1
)

:: Copier le dossier _internal (contient tout le code Python, templates, static, etc.)
:: EXCLURE: db.sqlite3, media/, *.backup
echo   Copie du dossier _internal (code, templates, static)...

:: Créer un fichier d'exclusion temporaire
echo db.sqlite3> "%TEMP%\maj_exclude.txt"
echo db.sqlite3.backup>> "%TEMP%\maj_exclude.txt"
echo *.backup>> "%TEMP%\maj_exclude.txt"

:: Utiliser robocopy pour copier _internal en excluant les fichiers DB
robocopy "%SOURCE%\_internal" "%DEST%\_internal" /E /XF db.sqlite3 db.sqlite3.backup *.log /XD media __pycache__ /NFL /NDL /NJH /NJS /NC /NS >nul 2>&1

if %errorlevel% leq 7 (
    echo   [OK] Dossier _internal mis a jour
) else (
    echo   [ATTENTION] Certains fichiers n'ont pas pu etre copies
)

:: Supprimer le fichier d'exclusion temporaire
del "%TEMP%\maj_exclude.txt" >nul 2>&1

echo [4/5] Restauration de la base de donnees...
:: Vérifier que la DB est toujours là
if exist "%DEST%\db.sqlite3" (
    echo   [OK] Base de donnees intacte
) else if exist "%DEST%\db.sqlite3.backup" (
    copy /Y "%DEST%\db.sqlite3.backup" "%DEST%\db.sqlite3" >nul 2>&1
    echo   [OK] Base de donnees restauree depuis la sauvegarde
) else (
    echo   [INFO] Aucune base de donnees trouvee (premiere installation?)
)

echo [5/5] Verification de la mise a jour...
:: Vérifier les fichiers critiques
set "OK=1"
if not exist "%DEST%\GestionnaireRH.exe" (
    echo   [ERREUR] GestionnaireRH.exe manquant!
    set "OK=0"
)
if not exist "%DEST%\_internal" (
    echo   [ERREUR] Dossier _internal manquant!
    set "OK=0"
)

if "%OK%"=="1" (
    echo.
    echo ============================================================
    echo   MISE A JOUR TERMINEE AVEC SUCCES!
    echo ============================================================
    echo.
    echo   Fichiers mis a jour:
    echo     - GestionnaireRH.exe
    echo     - _internal\ (code, templates, static)
    echo.
    echo   Fichiers preserves:
    echo     - db.sqlite3 (base de donnees)
    echo     - media\ (fichiers utilisateur)
    echo.
    echo   Vous pouvez maintenant relancer l'application.
    echo ============================================================
) else (
    echo.
    echo [ERREUR] La mise a jour a echoue. Verifiez les erreurs ci-dessus.
)

echo.
pause
