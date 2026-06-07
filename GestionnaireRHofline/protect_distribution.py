"""
GestionnaireRH Guinée — Protection de la Distribution
=============================================================================
Auteur  : ICG Guinea
Version : 1.0.0

Script de POST-BUILD qui protège le dossier de distribution :
  1. Compile les fichiers .py critiques en .pyc (bytecode)
  2. Supprime toutes les sources .py du dossier _internal
  3. Génère les checksums signés des fichiers protégés
  4. Crée la signature de l'exécutable (.exe_signature)
  5. Supprime les caches __pycache__ inutiles

UTILISATION :
  python protect_distribution.py [dist_path]
  
  Par défaut : dist/GestionnaireRH/

IMPORTANT : Ce script doit être exécuté APRÈS le build PyInstaller
            et APRÈS la compilation Nuitka des modules critiques.
"""

import os
import sys
import py_compile
import compileall
import hmac
import hashlib
import struct
import shutil
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# ─── Clé de protection (identique à runtime_shield.py) ────────────────────────
def _sk():
    _p = [82, 117, 110, 116, 105, 109, 101, 83, 104, 105, 101, 108, 100,
          45, 73, 67, 71, 45, 50, 48, 50, 53, 45, 65, 110, 116, 105,
          84, 97, 109, 112, 101, 114]
    return bytes(_p)

_SHIELD_KEY = _sk()


# ─── Fichiers à compiler avec Nuitka (protégés en binaire natif) ──────────────
NUITKA_TARGETS = [
    'license_manager.py',
    'project_guardian.py',
    'runtime_shield.py',
]

# ─── Fichiers Python à compiler en .pyc et supprimer les sources ──────────────
# (Tous les .py dans _internal sauf ceux qui sont déjà en .pyd)
PY_FILES_TO_PROTECT = [
    # Fichiers racine
    'run_server.py',
    'manage.py',
    # Core
    'core/__init__.py',
    'core/admin.py',
    'core/apps.py',
    'core/context_processors.py',
    'core/decorators.py',
    'core/forms.py',
    'core/middleware.py',
    'core/middleware_guardian.py',
    'core/middleware_licence.py',
    'core/models.py',
    'core/models_licence.py',
    'core/urls.py',
    'core/views.py',
    # Gestionnaire RH config
    'gestionnaire_rh/__init__.py',
    'gestionnaire_rh/settings.py',
    'gestionnaire_rh/settings_portable.py',
    'gestionnaire_rh/urls.py',
    'gestionnaire_rh/wsgi.py',
    'gestionnaire_rh/static_middleware.py',
]

# ─── Répertoires Django complets à protéger ────────────────────────────────────
APP_DIRS_TO_PROTECT = [
    'employes',
    'paie',
    'temps_travail',
    'conges',
    'contrats',
    'recrutement',
    'formation',
    'dashboard',
    'payments',
    'portail',
    'comptabilite',
]


def compile_py_to_pyc(py_path: Path) -> bool:
    """Compile un fichier .py en .pyc et retourne True si succès."""
    try:
        pyc_path = py_path.with_suffix('.pyc')
        py_compile.compile(
            str(py_path),
            cfile=str(pyc_path),
            doraise=True,
            optimize=2  # Optimisation maximale (supprime docstrings + asserts)
        )
        return pyc_path.exists()
    except py_compile.PyCompileError as e:
        print(f"  [!] Erreur compilation {py_path}: {e}")
        return False


def protect_internal_directory(dist_path: Path):
    """
    Protège le répertoire _internal d'une distribution PyInstaller.
    - Compile .py → .pyc
    - Supprime les .py sources
    - Génère les checksums
    """
    internal = dist_path / '_internal'
    if not internal.exists():
        print(f"[ERREUR] Répertoire _internal introuvable : {internal}")
        return False

    print("\n" + "=" * 60)
    print("  PROTECTION DE LA DISTRIBUTION")
    print("  © ICG Guinea — Anti-Falsification")
    print("=" * 60)

    stats = {
        'compiled': 0,
        'removed': 0,
        'nuitka_protected': 0,
        'errors': 0,
        'checksums': 0,
    }

    # ══════════════════════════════════════════════════════════════════════════
    # ÉTAPE 1 : Vérifier les modules Nuitka (.pyd)
    # ══════════════════════════════════════════════════════════════════════════
    print("\n[1/5] Vérification des modules Nuitka (.pyd)...")
    for target in NUITKA_TARGETS:
        stem = Path(target).stem
        # Chercher un .pyd correspondant
        pyd_found = False
        for f in internal.iterdir():
            if f.stem.startswith(stem) and f.suffix == '.pyd':
                pyd_found = True
                stats['nuitka_protected'] += 1
                print(f"  ✓ {stem} → {f.name} (binaire natif)")
                break
        
        if not pyd_found:
            py_file = internal / target
            if py_file.exists():
                print(f"  ⚠ {target} — source .py présente (pas de .pyd)")
                print(f"    → Compilation en .pyc comme protection de secours...")
                if compile_py_to_pyc(py_file):
                    py_file.unlink()
                    stats['compiled'] += 1
                    stats['removed'] += 1
                    print(f"    ✓ Compilé et source supprimée")
                else:
                    stats['errors'] += 1
                    print(f"    ✗ Échec de compilation")
            else:
                print(f"  ⚠ {target} — ni .pyd ni .py trouvé")

    # ══════════════════════════════════════════════════════════════════════════
    # ÉTAPE 2 : Compiler et supprimer les fichiers .py listés
    # ══════════════════════════════════════════════════════════════════════════
    print("\n[2/5] Compilation des fichiers Python critiques...")
    for rel_path in PY_FILES_TO_PROTECT:
        py_file = internal / rel_path
        if py_file.exists():
            # Vérifier qu'il n'y a pas déjà un .pyd
            stem = py_file.stem
            pyd_exists = any(
                f.stem.startswith(stem) and f.suffix == '.pyd'
                for f in py_file.parent.iterdir()
            )
            if pyd_exists:
                # Supprimer le .py, le .pyd suffit
                py_file.unlink()
                stats['removed'] += 1
                print(f"  ✓ {rel_path} → supprimé (.pyd existe)")
            else:
                if compile_py_to_pyc(py_file):
                    py_file.unlink()
                    stats['compiled'] += 1
                    stats['removed'] += 1
                    print(f"  ✓ {rel_path} → compilé .pyc, source supprimée")
                else:
                    stats['errors'] += 1
                    print(f"  ✗ {rel_path} → erreur de compilation")

    # ══════════════════════════════════════════════════════════════════════════
    # ÉTAPE 3 : Protéger les répertoires d'applications Django
    # ══════════════════════════════════════════════════════════════════════════
    print("\n[3/5] Protection des applications Django...")
    for app_dir in APP_DIRS_TO_PROTECT:
        app_path = internal / app_dir
        if app_path.exists() and app_path.is_dir():
            py_count = 0
            for py_file in app_path.rglob('*.py'):
                # Ne pas toucher aux migrations (Django en a besoin en .py)
                if 'migrations' in py_file.parts:
                    continue
                # Ne pas toucher aux __init__.py vides (marqueurs de package)
                if py_file.name == '__init__.py' and py_file.stat().st_size < 50:
                    continue
                
                if compile_py_to_pyc(py_file):
                    py_file.unlink()
                    py_count += 1
                    stats['compiled'] += 1
                    stats['removed'] += 1
                else:
                    stats['errors'] += 1
            
            if py_count > 0:
                print(f"  ✓ {app_dir}/ → {py_count} fichiers compilés")
            else:
                print(f"  - {app_dir}/ → rien à compiler")

    # ══════════════════════════════════════════════════════════════════════════
    # ÉTAPE 4 : Générer les checksums des fichiers protégés
    # ══════════════════════════════════════════════════════════════════════════
    print("\n[4/5] Génération des checksums de protection...")
    checksum_entries = []
    
    # Checksums des .pyd et fichiers critiques
    # NOTE: On exclut les .pyc dans __pycache__ car Python les régénère
    # au runtime avec des timestamps différents (faux positifs).
    for f in internal.rglob('*'):
        if not f.is_file():
            continue
        if f.suffix not in ('.pyc', '.pyd', '.json'):
            continue
        # Exclure les .pyc dans __pycache__ (régénérés par Python)
        if '__pycache__' in f.parts and f.suffix == '.pyc':
            continue
        # Exclure les fichiers générés PAR CE SCRIPT (écrits après les checksums)
        if f.name in ('.protection_report.json',):
            continue
        rel = f.relative_to(internal)
        content = f.read_bytes()
        file_hash = hmac.new(_SHIELD_KEY, content, hashlib.sha256).hexdigest()
        checksum_entries.append(f"{rel}|{file_hash}")
        stats['checksums'] += 1

    # Écrire le registre de checksums signé
    registry_data = '\n'.join(checksum_entries).encode('utf-8')
    registry_sig = hmac.new(_SHIELD_KEY, registry_data, hashlib.sha256).hexdigest()
    
    registry_path = internal / '.file_checksums'
    registry_path.write_bytes(registry_sig.encode('ascii') + registry_data)
    print(f"  ✓ {stats['checksums']} checksums générés et signés")

    # ══════════════════════════════════════════════════════════════════════════
    # ÉTAPE 5 : Signature de l'exécutable
    # ══════════════════════════════════════════════════════════════════════════
    print("\n[5/5] Signature de l'exécutable...")
    exe_path = dist_path / 'GestionnaireRH.exe'
    if exe_path.exists():
        exe_content = exe_path.read_bytes()
        exe_size = len(exe_content)
        exe_hash = hashlib.sha256(exe_content).hexdigest()
        exe_sig = hmac.new(_SHIELD_KEY, exe_hash.encode(), hashlib.sha256).hexdigest()

        sig_path = internal / '.exe_signature'
        sig_data = exe_sig.encode('ascii') + struct.pack('<Q', exe_size)
        sig_path.write_bytes(sig_data)
        print(f"  ✓ Exécutable signé (taille: {exe_size:,} bytes)")
    else:
        print(f"  ⚠ Exécutable non trouvé : {exe_path}")

    # ══════════════════════════════════════════════════════════════════════════
    # NETTOYAGE : Supprimer les __pycache__ inutiles
    # ══════════════════════════════════════════════════════════════════════════
    print("\n[Nettoyage] Suppression des caches __pycache__...")
    cache_count = 0
    for cache_dir in internal.rglob('__pycache__'):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
            cache_count += 1
    if cache_count:
        print(f"  ✓ {cache_count} dossiers __pycache__ supprimés")

    # ══════════════════════════════════════════════════════════════════════════
    # RAPPORT FINAL
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("  PROTECTION TERMINÉE")
    print("=" * 60)
    print(f"  Modules Nuitka (.pyd)  : {stats['nuitka_protected']}")
    print(f"  Fichiers compilés      : {stats['compiled']}")
    print(f"  Sources supprimées     : {stats['removed']}")
    print(f"  Checksums générés      : {stats['checksums']}")
    print(f"  Erreurs                : {stats['errors']}")
    print()

    # Vérification finale : compter les .py restants
    remaining_py = list(internal.rglob('*.py'))
    # Exclure les migrations et __init__.py vides
    remaining_py = [
        f for f in remaining_py
        if 'migrations' not in f.parts
        and not (f.name == '__init__.py' and f.stat().st_size < 50)
    ]
    if remaining_py:
        print(f"  ⚠ {len(remaining_py)} fichiers .py restants :")
        for f in remaining_py[:20]:
            print(f"    - {f.relative_to(internal)}")
        if len(remaining_py) > 20:
            print(f"    ... et {len(remaining_py) - 20} autres")
    else:
        print("  ✓ Aucun fichier .py source restant (protection maximale)")

    return stats['errors'] == 0


def generate_protection_report(dist_path: Path) -> dict:
    """Génère un rapport JSON de la protection appliquée."""
    internal = dist_path / '_internal'
    report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'dist_path': str(dist_path),
        'protection_version': '1.0.0',
        'files': {
            'pyd_modules': [],
            'pyc_compiled': [],
            'py_remaining': [],
        }
    }

    if internal.exists():
        for f in internal.rglob('*'):
            if f.is_file():
                rel = str(f.relative_to(internal))
                if f.suffix == '.pyd':
                    report['files']['pyd_modules'].append(rel)
                elif f.suffix == '.pyc':
                    report['files']['pyc_compiled'].append(rel)
                elif f.suffix == '.py':
                    report['files']['py_remaining'].append(rel)

    return report


# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import io
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    # Déterminer le chemin de distribution
    if len(sys.argv) > 1:
        dist_path = Path(sys.argv[1])
    else:
        dist_path = Path(__file__).parent / 'dist' / 'GestionnaireRH'

    if not dist_path.exists():
        print(f"[ERREUR] Répertoire de distribution introuvable : {dist_path}")
        print("Usage : python protect_distribution.py [chemin_vers_dist]")
        sys.exit(1)

    success = protect_internal_directory(dist_path)

    # Sauvegarder le rapport
    report = generate_protection_report(dist_path)
    report_path = dist_path / '_internal' / '.protection_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"\n  Rapport sauvegardé : {report_path}")

    sys.exit(0 if success else 1)
