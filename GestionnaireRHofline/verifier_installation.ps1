# ============================================================================
# Script de vérification de l'installation - Gestionnaire RH Guinée
# ============================================================================

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  VÉRIFICATION DE L'INSTALLATION - Gestionnaire RH Guinée" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

$score = 0
$total = 15

# ============================================================================
# 1. Vérifier Python
# ============================================================================
Write-Host "[1/15] Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.1[0-9]") {
        Write-Host "  ✅ Python installé : $pythonVersion" -ForegroundColor Green
        $score++
    } else {
        Write-Host "  ⚠️  Python version < 3.10 : $pythonVersion" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Python non installé ou non dans le PATH" -ForegroundColor Red
}

# ============================================================================
# 2. Vérifier PostgreSQL
# ============================================================================
Write-Host "[2/15] Vérification de PostgreSQL..." -ForegroundColor Yellow
try {
    $pgVersion = psql --version 2>&1
    if ($pgVersion -match "psql.*1[4-9]") {
        Write-Host "  ✅ PostgreSQL installé : $pgVersion" -ForegroundColor Green
        $score++
    } else {
        Write-Host "  ⚠️  PostgreSQL version < 14 : $pgVersion" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ PostgreSQL non installé ou non dans le PATH" -ForegroundColor Red
}

# ============================================================================
# 3. Vérifier l'environnement virtuel
# ============================================================================
Write-Host "[3/15] Vérification de l'environnement virtuel..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "  ✅ Environnement virtuel créé" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ❌ Environnement virtuel non créé" -ForegroundColor Red
    Write-Host "     Exécuter : python -m venv venv" -ForegroundColor Gray
}

# ============================================================================
# 4. Vérifier requirements.txt
# ============================================================================
Write-Host "[4/15] Vérification de requirements.txt..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    $reqCount = (Get-Content "requirements.txt" | Measure-Object -Line).Lines
    if ($reqCount -ge 19) {
        Write-Host "  ✅ requirements.txt présent ($reqCount packages)" -ForegroundColor Green
        $score++
    } else {
        Write-Host "  ⚠️  requirements.txt incomplet ($reqCount packages)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ requirements.txt manquant" -ForegroundColor Red
}

# ============================================================================
# 5. Vérifier manage.py
# ============================================================================
Write-Host "[5/15] Vérification de manage.py..." -ForegroundColor Yellow
if (Test-Path "manage.py") {
    Write-Host "  ✅ manage.py présent" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ❌ manage.py manquant" -ForegroundColor Red
}

# ============================================================================
# 6. Vérifier settings.py
# ============================================================================
Write-Host "[6/15] Vérification de settings.py..." -ForegroundColor Yellow
if (Test-Path "gestionnaire_rh\settings.py") {
    Write-Host "  ✅ settings.py présent" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ❌ settings.py manquant" -ForegroundColor Red
}

# ============================================================================
# 7. Vérifier .env
# ============================================================================
Write-Host "[7/15] Vérification du fichier .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "SECRET_KEY" -and $envContent -match "DB_NAME") {
        Write-Host "  ✅ Fichier .env configuré" -ForegroundColor Green
        $score++
    } else {
        Write-Host "  ⚠️  Fichier .env incomplet" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ Fichier .env manquant" -ForegroundColor Red
    Write-Host "     Créer le fichier .env avec les variables nécessaires" -ForegroundColor Gray
}

# ============================================================================
# 8. Vérifier les dossiers principaux
# ============================================================================
Write-Host "[8/15] Vérification de la structure des dossiers..." -ForegroundColor Yellow
$folders = @("core", "dashboard", "employes", "paie", "temps_travail", "templates", "static", "database")
$foldersOK = 0
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        $foldersOK++
    }
}
if ($foldersOK -eq $folders.Count) {
    Write-Host "  ✅ Tous les dossiers principaux présents ($foldersOK/$($folders.Count))" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ⚠️  Dossiers manquants ($foldersOK/$($folders.Count))" -ForegroundColor Yellow
}

# ============================================================================
# 9. Vérifier les templates
# ============================================================================
Write-Host "[9/15] Vérification des templates..." -ForegroundColor Yellow
$templates = @(
    "templates\base.html",
    "templates\core\login.html",
    "templates\dashboard\index.html",
    "templates\employes\list.html"
)
$templatesOK = 0
foreach ($template in $templates) {
    if (Test-Path $template) {
        $templatesOK++
    }
}
if ($templatesOK -eq $templates.Count) {
    Write-Host "  ✅ Templates principaux présents ($templatesOK/$($templates.Count))" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ⚠️  Templates manquants ($templatesOK/$($templates.Count))" -ForegroundColor Yellow
}

# ============================================================================
# 10. Vérifier le CSS personnalisé
# ============================================================================
Write-Host "[10/15] Vérification du CSS..." -ForegroundColor Yellow
if (Test-Path "static\css\custom.css") {
    Write-Host "  ✅ Fichier CSS personnalisé présent" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ❌ Fichier CSS personnalisé manquant" -ForegroundColor Red
}

# ============================================================================
# 11. Vérifier les scripts SQL
# ============================================================================
Write-Host "[11/15] Vérification des scripts SQL..." -ForegroundColor Yellow
$sqlScripts = @(
    "database\schema_complete.sql",
    "database\views_and_indexes.sql",
    "database\functions_procedures.sql",
    "database\data_init_guinee.sql"
)
$sqlOK = 0
foreach ($script in $sqlScripts) {
    if (Test-Path $script) {
        $sqlOK++
    }
}
if ($sqlOK -eq $sqlScripts.Count) {
    Write-Host "  ✅ Scripts SQL présents ($sqlOK/$($sqlScripts.Count))" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ⚠️  Scripts SQL manquants ($sqlOK/$($sqlScripts.Count))" -ForegroundColor Yellow
}

# ============================================================================
# 12. Vérifier la documentation
# ============================================================================
Write-Host "[12/15] Vérification de la documentation..." -ForegroundColor Yellow
$docs = @(
    "README.md",
    "DEMARRAGE_RAPIDE.txt",
    "STATUS_ACTUEL.txt",
    "QUICK_START_COMMANDS.md"
)
$docsOK = 0
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        $docsOK++
    }
}
if ($docsOK -eq $docs.Count) {
    Write-Host "  ✅ Documentation principale présente ($docsOK/$($docs.Count))" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ⚠️  Documentation incomplète ($docsOK/$($docs.Count))" -ForegroundColor Yellow
}

# ============================================================================
# 13. Vérifier les modules Python (si venv activé)
# ============================================================================
Write-Host "[13/15] Vérification des modules Python..." -ForegroundColor Yellow
if ($env:VIRTUAL_ENV) {
    try {
        $djangoVersion = python -c "import django; print(django.get_version())" 2>&1
        if ($djangoVersion -match "4\.2") {
            Write-Host "  ✅ Django installé : $djangoVersion" -ForegroundColor Green
            $score++
        } else {
            Write-Host "  ⚠️  Django version incorrecte : $djangoVersion" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ Django non installé" -ForegroundColor Red
        Write-Host "     Exécuter : pip install -r requirements.txt" -ForegroundColor Gray
    }
} else {
    Write-Host "  ⚠️  Environnement virtuel non activé" -ForegroundColor Yellow
    Write-Host "     Exécuter : .\venv\Scripts\activate" -ForegroundColor Gray
}

# ============================================================================
# 14. Vérifier les fichiers views.py
# ============================================================================
Write-Host "[14/15] Vérification des vues Django..." -ForegroundColor Yellow
$views = @(
    "core\views.py",
    "dashboard\views.py",
    "employes\views.py"
)
$viewsOK = 0
foreach ($view in $views) {
    if (Test-Path $view) {
        $viewsOK++
    }
}
if ($viewsOK -eq $views.Count) {
    Write-Host "  ✅ Vues principales présentes ($viewsOK/$($views.Count))" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ⚠️  Vues manquantes ($viewsOK/$($views.Count))" -ForegroundColor Yellow
}

# ============================================================================
# 15. Vérifier les URLs
# ============================================================================
Write-Host "[15/15] Vérification des URLs..." -ForegroundColor Yellow
$urls = @(
    "gestionnaire_rh\urls.py",
    "core\urls.py",
    "dashboard\urls.py",
    "employes\urls.py"
)
$urlsOK = 0
foreach ($url in $urls) {
    if (Test-Path $url) {
        $urlsOK++
    }
}
if ($urlsOK -eq $urls.Count) {
    Write-Host "  ✅ Fichiers URLs présents ($urlsOK/$($urls.Count))" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ⚠️  Fichiers URLs manquants ($urlsOK/$($urls.Count))" -ForegroundColor Yellow
}

# ============================================================================
# RÉSUMÉ
# ============================================================================
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  RÉSUMÉ DE LA VÉRIFICATION" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

$percentage = [math]::Round(($score / $total) * 100, 0)

Write-Host "Score : $score / $total ($percentage%)" -ForegroundColor White
Write-Host ""

if ($score -eq $total) {
    Write-Host "  🎉 EXCELLENT ! Installation complète et prête !" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Prochaines étapes :" -ForegroundColor White
    Write-Host "  1. Activer l'environnement : .\venv\Scripts\activate" -ForegroundColor Gray
    Write-Host "  2. Lancer le serveur : python manage.py runserver" -ForegroundColor Gray
    Write-Host "  3. Ouvrir http://localhost:8000" -ForegroundColor Gray
} elseif ($score -ge 12) {
    Write-Host "  ✅ BON ! Quelques ajustements nécessaires" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Vérifier les éléments marqués ⚠️ ou ❌ ci-dessus" -ForegroundColor Gray
} else {
    Write-Host "  ❌ ATTENTION ! Configuration incomplète" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Consulter DEMARRAGE_RAPIDE.txt pour l'installation complète" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Pause pour lire les résultats
Write-Host "Appuyez sur une touche pour continuer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
