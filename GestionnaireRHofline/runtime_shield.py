"""
GestionnaireRH Guinée — Bouclier Anti-Falsification Runtime
=============================================================================
Auteur  : ICG Guinea
Version : 1.0.0

Ce module protège l'application installée contre :
  1. Modification des fichiers .py/.pyc dans le répertoire d'installation
  2. Extraction et décompilation du code (pyinstxtractor, uncompyle6, etc.)
  3. Remplacement de modules par des versions modifiées
  4. Injection de code malveillant
  5. Ouverture et modification des sources dans un éditeur

FONCTIONNEMENT :
  - À l'import, vérifie l'intégrité de l'environnement d'exécution
  - Détecte les outils de reverse-engineering en cours d'exécution
  - Vérifie qu'aucun fichier source .py n'a été ajouté/modifié dans _internal
  - Cross-vérifie que les modules de protection (guardian, licence) sont intacts
  - Bloque l'application si une modification est détectée

AVERTISSEMENT LÉGAL :
  Ce logiciel est la propriété exclusive de ICG Guinea.
  Toute copie, modification, redistribution ou ingénierie inverse
  est strictement interdite.
"""

import os
import sys
import hmac
import hashlib
import struct
import logging
import ctypes
import time
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger('runtime_shield')

# ─── Clé de vérification interne (obfusquée) ──────────────────────────────────
def _sk():
    _p = [82, 117, 110, 116, 105, 109, 101, 83, 104, 105, 101, 108, 100,
          45, 73, 67, 71, 45, 50, 48, 50, 53, 45, 65, 110, 116, 105,
          84, 97, 109, 112, 101, 114]
    return bytes(_p)

_SHIELD_KEY = _sk()
del _sk

# ─── Watermark de vérification ────────────────────────────────────────────────
_SHIELD_WATERMARK = "ICG-Guinea-Shield-v1-AntiTamper-2025"
_SHIELD_HASH = hashlib.sha256(_SHIELD_WATERMARK.encode()).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 : DÉTECTION D'OUTILS DE REVERSE-ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════════

# Noms de processus d'outils de reverse-engineering / débogage
_RE_TOOLS = [
    'pyinstxtractor', 'pyi_archive_viewer', 'pyi_', 'uncompyle6',
    'decompyle3', 'pycdc', 'bytecode_graph', 'xdis', 'unpy2exe',
    'pydecipher', 'pycdas', 'pycdump',
    # Débogueurs / éditeurs Python courants (contexte suspect en production)
    'ida64', 'ida', 'x64dbg', 'x32dbg', 'ollydbg', 'windbg',
    'ghidra', 'radare2', 'r2', 'binary ninja', 'hopper',
    # Outils réseau / interception
    'fiddler', 'charles', 'mitmproxy', 'wireshark',
]

# Extensions de fichiers suspectes dans le répertoire d'installation
_SUSPICIOUS_EXTENSIONS = {
    '.py',       # Sources Python (ne devraient PAS être dans dist)
    '.pyw',      # Sources Python Windows
    '.patch',    # Correctifs
    '.diff',     # Différences
    '.bak',      # Sauvegardes
    '.orig',     # Fichiers originaux
    '.old',      # Anciennes versions
    '.modified', # Fichiers modifiés
}

# Fichiers qui ne doivent JAMAIS exister dans _internal sous forme .py
# (ils doivent être en .pyd compilé Nuitka ou absents)
_MUST_BE_COMPILED = [
    'license_manager.py',
    'project_guardian.py',
    'runtime_shield.py',
]

# Fichiers critiques qui doivent exister (en .pyd ou .pyc, pas .py)
_CRITICAL_MODULES = [
    'license_manager',
    'project_guardian',
    'runtime_shield',
]


def _check_running_processes() -> list:
    """Détecte les processus de reverse-engineering en cours d'exécution."""
    detected = []
    try:
        # Utiliser tasklist via ctypes (plus fiable que subprocess)
        import subprocess
        result = subprocess.run(
            ['tasklist', '/FO', 'CSV', '/NH'],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        processes = result.stdout.lower()
        for tool in _RE_TOOLS:
            if tool.lower() in processes:
                detected.append(tool)
    except Exception:
        pass
    return detected


def _check_debugger_attached() -> bool:
    """Vérifie si un débogueur est attaché au processus."""
    # Méthode 1 : Python trace
    if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
        return True

    # Méthode 2 : Windows API IsDebuggerPresent
    try:
        kernel32 = ctypes.windll.kernel32
        if kernel32.IsDebuggerPresent():
            return True
    except Exception:
        pass

    # Méthode 3 : CheckRemoteDebuggerPresent (détecte les débogueurs distants)
    try:
        kernel32 = ctypes.windll.kernel32
        is_debugged = ctypes.c_int(0)
        kernel32.CheckRemoteDebuggerPresent(
            kernel32.GetCurrentProcess(),
            ctypes.byref(is_debugged)
        )
        if is_debugged.value:
            return True
    except Exception:
        pass

    return False


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 : VÉRIFICATION DE L'INTÉGRITÉ DES FICHIERS D'INSTALLATION
# ═══════════════════════════════════════════════════════════════════════════════

def _get_install_dir() -> Path:
    """Retourne le répertoire d'installation."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def _get_internal_dir() -> Path:
    """Retourne le répertoire _internal de PyInstaller."""
    if getattr(sys, 'frozen', False):
        internal = Path(sys.executable).parent / '_internal'
        if internal.exists():
            return internal
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def _scan_suspicious_files() -> list:
    """
    Scanne le répertoire _internal pour détecter des fichiers .py suspects.
    En mode PyInstaller, les fichiers .py sources NE DEVRAIENT PAS exister
    dans _internal (ils sont compilés en .pyc ou .pyd).
    """
    suspicious = []
    if not getattr(sys, 'frozen', False):
        return suspicious  # En dev, c'est normal d'avoir des .py

    internal = _get_internal_dir()
    if not internal.exists():
        return ['_internal_missing']

    # Vérifier les fichiers qui DOIVENT être compilés (.pyd) pas en .py
    # On ne bloque QUE si le .py existe SANS le .pyd correspondant.
    # Cas normal : seul le .pyd existe (installation correcte)
    # Cas suspect : .py sans .pyd = quelqu'un a décompilé/remplacé le module
    for py_name in _MUST_BE_COMPILED:
        py_path = internal / py_name
        if py_path.exists():
            # Vérifier s'il y a un .pyd correspondant
            mod_base = py_name.replace('.py', '')
            has_pyd = any(
                f.name.startswith(mod_base) and f.suffix == '.pyd'
                for f in internal.iterdir()
                if f.is_file()
            )
            if not has_pyd:
                # .py sans .pyd = falsification (module décompilé ou remplacé)
                suspicious.append(f"source_detected:{py_name}")

    # Scanner les modifications récentes (fichiers modifiés après l'installation)
    exe_path = Path(sys.executable)
    if exe_path.exists():
        exe_mtime = exe_path.stat().st_mtime
        # Vérifier les fichiers .py dans les modules critiques
        critical_dirs = ['core', 'gestionnaire_rh']
        for cdir in critical_dirs:
            dir_path = internal / cdir
            if dir_path.exists():
                for f in dir_path.rglob('*.py'):
                    try:
                        if f.stat().st_mtime > exe_mtime + 60:
                            # Fichier modifié APRÈS le build de l'exe
                            suspicious.append(f"modified_after_build:{f.relative_to(internal)}")
                    except Exception:
                        pass

    return suspicious


def _verify_exe_integrity() -> dict:
    """
    Vérifie l'intégrité de l'exécutable principal.
    Calcule le hash SHA-256 de l'exécutable et le compare au hash stocké.
    """
    result = {'valid': True, 'reason': ''}
    if not getattr(sys, 'frozen', False):
        return result

    exe_path = Path(sys.executable)
    if not exe_path.exists():
        result['valid'] = False
        result['reason'] = 'executable_missing'
        return result

    # Vérifier la taille de l'exécutable (ne doit pas avoir été modifiée significativement)
    internal = _get_internal_dir()
    hash_file = internal / '.exe_signature'
    if hash_file.exists():
        try:
            stored_data = hash_file.read_bytes()
            # Format : signature HMAC (64 bytes hex) | taille originale (8 bytes)
            stored_sig = stored_data[:64].decode('ascii')
            stored_size = struct.unpack('<Q', stored_data[64:72])[0]

            actual_size = exe_path.stat().st_size
            # Tolérance de 0 byte - taille exacte requise
            if actual_size != stored_size:
                result['valid'] = False
                result['reason'] = 'exe_size_modified'
                return result

            # Vérifier le hash
            exe_hash = hashlib.sha256(exe_path.read_bytes()).hexdigest()
            expected_hash = hmac.new(
                _SHIELD_KEY,
                exe_hash.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(expected_hash, stored_sig):
                result['valid'] = False
                result['reason'] = 'exe_hash_modified'
        except Exception:
            # Si le fichier de signature est corrompu, c'est suspect
            result['valid'] = False
            result['reason'] = 'signature_corrupted'
    # Si le fichier de signature n'existe pas encore, on le crée au premier lancement
    # (sera généré par protect_distribution.py)

    return result


def _cross_verify_modules() -> dict:
    """
    Vérifie que les modules de protection sont présents et authentiques.
    Chaque module vérifie les autres (cross-verification).
    """
    result = {'valid': True, 'missing': [], 'tampered': []}

    internal = _get_internal_dir()

    # Vérifier que license_manager existe en tant que .pyd (compilé Nuitka)
    lm_found = False
    if internal.exists():
        for f in internal.iterdir():
            if f.name.startswith('license_manager') and f.suffix == '.pyd':
                lm_found = True
                break
    if not lm_found:
        # Vérifier s'il est importable quand même
        try:
            import importlib
            lm = importlib.import_module('license_manager')
            if not hasattr(lm, '_DEV_SECRET'):
                result['tampered'].append('license_manager')
                result['valid'] = False
        except ImportError:
            result['missing'].append('license_manager')
            result['valid'] = False

    # Vérifier project_guardian
    try:
        import importlib
        pg = importlib.import_module('project_guardian')
        # Vérifier que les fonctions critiques existent
        required_funcs = [
            'is_owner_machine', 'verify_project_integrity',
            'full_security_check', '_WATERMARK_HASH'
        ]
        for func_name in required_funcs:
            if not hasattr(pg, func_name):
                result['tampered'].append(f'project_guardian.{func_name}')
                result['valid'] = False
                break

        # Vérifier que le watermark est authentique
        expected_wm = "© 2025 ICG Guinea - GestionnaireRH - Tous droits réservés - Licence propriétaire"
        expected_hash = hashlib.sha256(expected_wm.encode()).hexdigest()
        if pg._WATERMARK_HASH != expected_hash:
            result['tampered'].append('project_guardian.watermark')
            result['valid'] = False

    except ImportError:
        result['missing'].append('project_guardian')
        result['valid'] = False

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 : DÉTECTION D'ENVIRONNEMENT D'EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

def _detect_extraction_environment() -> dict:
    """
    Détecte si l'application tourne depuis un environnement extrait
    (pyinstxtractor, manual extraction, etc.)
    """
    result = {'extracted': False, 'indicators': []}

    if not getattr(sys, 'frozen', False):
        return result

    install_dir = _get_install_dir()

    # Indicateur 1 : Présence de fichiers typiques d'extraction
    extraction_markers = [
        'pyiboot01_bootstrap.py',  # Laissé par pyinstxtractor
        'pyimod01_archive.py',
        'pyimod02_importers.py',
        'PYZ-00.pyz_extracted',    # Dossier d'extraction PYZ
        'struct.pyc',              # Fichiers extraits du PYZ
        'pyinstxtractor',
        '_pyinstxtractor',
    ]
    for marker in extraction_markers:
        if (install_dir / marker).exists() or (install_dir / '_internal' / marker).exists():
            result['extracted'] = True
            result['indicators'].append(f'marker:{marker}')

    # Indicateur 2 : Présence d'un dossier PYZ extrait
    internal = _get_internal_dir()
    for item in internal.iterdir() if internal.exists() else []:
        if item.is_dir() and 'pyz' in item.name.lower() and 'extract' in item.name.lower():
            result['extracted'] = True
            result['indicators'].append(f'pyz_extracted_dir:{item.name}')

    # Indicateur 3 : Nombre anormal de fichiers .pyc dans _internal
    # (après extraction, il y a beaucoup plus de fichiers)
    if internal.exists():
        pyc_count = sum(1 for _ in internal.rglob('*.pyc'))
        # Si plus de 5000 .pyc dans _internal, c'est probablement une extraction
        if pyc_count > 5000:
            result['extracted'] = True
            result['indicators'].append(f'excessive_pyc:{pyc_count}')

    # Indicateur 4 : Le répertoire d'exécution est un dossier temporaire
    exe_dir = str(install_dir).lower()
    temp_dirs = [
        os.environ.get('TEMP', '').lower(),
        os.environ.get('TMP', '').lower(),
        'appdata\\local\\temp',
        '\\temp\\',
        '\\tmp\\',
    ]
    for td in temp_dirs:
        if td and td in exe_dir:
            result['extracted'] = True
            result['indicators'].append(f'temp_dir:{exe_dir}')
            break

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 : PROTECTION ANTI-MODIFICATION DES FICHIERS .PY
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_file_checksum(filepath: Path) -> str:
    """Génère un checksum HMAC pour un fichier."""
    try:
        content = filepath.read_bytes()
        return hmac.new(_SHIELD_KEY, content, hashlib.sha256).hexdigest()
    except Exception:
        return ''


def _verify_critical_files_checksums() -> dict:
    """
    Vérifie les checksums des fichiers critique à partir du registre de checksums.
    Le registre est créé par protect_distribution.py lors du build.
    """
    result = {'valid': True, 'tampered': [], 'missing_registry': False}

    if not getattr(sys, 'frozen', False):
        return result

    internal = _get_internal_dir()
    registry_path = internal / '.file_checksums'

    if not registry_path.exists():
        # Pas de registre = pas de vérification possible
        # C'est acceptable pour les premiers builds, mais suspect après
        result['missing_registry'] = True
        return result

    try:
        raw = registry_path.read_bytes()
        # Le registre est signé : [signature (64 bytes hex)][data]
        stored_sig = raw[:64].decode('ascii')
        data = raw[64:]

        # Vérifier la signature du registre
        expected_sig = hmac.new(_SHIELD_KEY, data, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(stored_sig, expected_sig):
            result['valid'] = False
            result['tampered'].append('checksum_registry_signature')
            return result

        # Parser le registre (format: filepath|checksum\n)
        entries = data.decode('utf-8').strip().split('\n')
        for entry in entries:
            if '|' not in entry:
                continue
            rel_path, expected_hash = entry.split('|', 1)
            # Ignorer les .pyc dans __pycache__ — Python les régénère
            # automatiquement au runtime avec des timestamps différents.
            # Ce n'est PAS une falsification, c'est le comportement normal.
            if '__pycache__' in rel_path and rel_path.endswith('.pyc'):
                continue
            file_path = internal / rel_path
            if file_path.exists():
                actual_hash = _generate_file_checksum(file_path)
                if not hmac.compare_digest(actual_hash, expected_hash):
                    result['tampered'].append(rel_path)
                    result['valid'] = False
            # Fichier manquant = ne pas bloquer (peut être normal)

    except Exception:
        result['valid'] = False
        result['tampered'].append('checksum_registry_parse_error')

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 : AUTO-DESTRUCTION EN CAS DE FALSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

def _revoke_license_on_tamper():
    """
    En cas de falsification détectée, révoque la licence locale.
    L'utilisateur devra contacter ICG Guinea pour réactiver.
    """
    try:
        import json
        # Créer un fichier de marquage de falsification
        install_dir = _get_install_dir()
        tamper_flag = install_dir / '.tamper_detected'
        tamper_data = {
            'detected_at': datetime.now(timezone.utc).isoformat(),
            'machine': hashlib.sha256(
                (os.environ.get('COMPUTERNAME', '') + str(os.getpid())).encode()
            ).hexdigest()[:16],
        }
        tamper_flag.write_text(json.dumps(tamper_data), encoding='utf-8')

        # Invalider le fichier de licence locale
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            lic_dir = Path(appdata) / 'GestionnaireRH'
            lic_file = lic_dir / 'license.dat'
            if lic_file.exists():
                # Remplacer par un fichier vide signé "revoked"
                revoke_data = hmac.new(
                    _SHIELD_KEY,
                    b'LICENSE_REVOKED_TAMPER_DETECTED',
                    hashlib.sha256
                ).hexdigest()
                lic_file.write_text(f'REVOKED:{revoke_data}', encoding='utf-8')

        logger.critical("TAMPER DETECTED — License revoked")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 : VÉRIFICATION COMPLÈTE (POINT D'ENTRÉE)
# ═══════════════════════════════════════════════════════════════════════════════

def full_shield_check() -> dict:
    """
    Exécute une vérification anti-falsification complète.
    Retourne un rapport détaillé.
    """
    report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'frozen': getattr(sys, 'frozen', False),
        'blocked': False,
        'reason': '',
        'checks': {},
    }

    # En mode développement (non-frozen), on ne bloque pas
    if not getattr(sys, 'frozen', False):
        report['checks']['dev_mode'] = True
        return report

    # ── 1) Vérification anti-débogage ──
    debugger = _check_debugger_attached()
    report['checks']['debugger'] = not debugger
    if debugger:
        # Vérifier si c'est la machine propriétaire
        try:
            from project_guardian import is_owner_machine
            if not is_owner_machine():
                report['blocked'] = True
                report['reason'] = (
                    "ALERTE SÉCURITÉ : Débogueur détecté. "
                    "Le débogage n'est pas autorisé sur cette machine."
                )
                return report
        except ImportError:
            report['blocked'] = True
            report['reason'] = "Module de protection manquant."
            return report

    # ── 2) Détection de tools de reverse-engineering ──
    re_tools = _check_running_processes()
    report['checks']['re_tools'] = re_tools
    if re_tools:
        try:
            from project_guardian import is_owner_machine
            if not is_owner_machine():
                report['blocked'] = True
                report['reason'] = (
                    f"ALERTE SÉCURITÉ : Outils de reverse-engineering détectés : "
                    f"{', '.join(re_tools)}. Ceci est interdit."
                )
                _revoke_license_on_tamper()
                return report
        except ImportError:
            report['blocked'] = True
            report['reason'] = "Module de protection manquant."
            return report

    # ── 3) Détection d'extraction ──
    extraction = _detect_extraction_environment()
    report['checks']['extraction'] = extraction
    if extraction['extracted']:
        report['blocked'] = True
        report['reason'] = (
            "ALERTE SÉCURITÉ : Environnement d'extraction détecté. "
            "L'application a été extraite de son package protégé."
        )
        _revoke_license_on_tamper()
        return report

    # ── 4) Scan de fichiers suspects ──
    suspicious = _scan_suspicious_files()
    report['checks']['suspicious_files'] = suspicious
    if suspicious:
        # Vérifier spécifiquement les sources qui doivent être compilées
        source_detected = [s for s in suspicious if s.startswith('source_detected:')]
        modified_files = [s for s in suspicious if s.startswith('modified_after_build:')]

        if source_detected:
            report['blocked'] = True
            files = [s.split(':')[1] for s in source_detected]
            report['reason'] = (
                f"ALERTE SÉCURITÉ : Fichiers source non autorisés détectés : "
                f"{', '.join(files)}. Ces fichiers doivent être compilés, "
                f"pas en texte clair."
            )
            _revoke_license_on_tamper()
            return report

        if modified_files:
            report['blocked'] = True
            files = [s.split(':')[1] for s in modified_files]
            report['reason'] = (
                f"ALERTE SÉCURITÉ : Fichiers modifiés après le build : "
                f"{', '.join(files)}. Le code a été altéré."
            )
            _revoke_license_on_tamper()
            return report

    # ── 5) Cross-vérification des modules ──
    cross = _cross_verify_modules()
    report['checks']['cross_verification'] = cross
    if not cross['valid']:
        report['blocked'] = True
        details = cross.get('tampered', []) + cross.get('missing', [])
        report['reason'] = (
            f"ALERTE SÉCURITÉ : Modules de protection compromis : "
            f"{', '.join(details)}."
        )
        _revoke_license_on_tamper()
        return report

    # ── 6) Vérification des checksums de fichiers ──
    checksums = _verify_critical_files_checksums()
    report['checks']['file_checksums'] = checksums
    if not checksums['valid']:
        report['blocked'] = True
        report['reason'] = (
            f"ALERTE SÉCURITÉ : Fichiers critiques modifiés : "
            f"{', '.join(checksums.get('tampered', []))}."
        )
        _revoke_license_on_tamper()
        return report

    # ── 7) Vérification de l'exécutable ──
    exe_check = _verify_exe_integrity()
    report['checks']['exe_integrity'] = exe_check
    if not exe_check['valid']:
        report['blocked'] = True
        report['reason'] = (
            f"ALERTE SÉCURITÉ : L'exécutable a été modifié. "
            f"({exe_check.get('reason', 'unknown')})"
        )
        _revoke_license_on_tamper()
        return report

    # ── 8) Vérifier le marqueur de falsification précédente ──
    tamper_flag = _get_install_dir() / '.tamper_detected'
    if tamper_flag.exists():
        report['blocked'] = True
        report['reason'] = (
            "ALERTE SÉCURITÉ : Une falsification a été précédemment détectée. "
            "L'application est définitivement bloquée. "
            "Contactez ICG Guinea pour une réinstallation."
        )
        return report

    return report


def shield_startup_check():
    """
    Vérification rapide au démarrage de l'application.
    Retourne True si OK, False si compromis.
    """
    if not getattr(sys, 'frozen', False):
        return True  # Pas de blocage en mode dev

    try:
        result = full_shield_check()
        if result.get('blocked'):
            logger.critical(
                "SHIELD STARTUP BLOCKED: %s", result.get('reason', '')
            )
            return False
    except Exception as e:
        logger.warning("Shield startup check error: %s", e)

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 : MIDDLEWARE DJANGO POUR VÉRIFICATION CONTINUE
# ═══════════════════════════════════════════════════════════════════════════════

_last_shield_check = 0
_shield_cache_seconds = 300  # Vérification toutes les 5 minutes
_cached_shield_result = None


def periodic_shield_check() -> dict:
    """
    Vérification périodique du bouclier (avec cache pour performance).
    Utilisé par le middleware Django.
    """
    global _last_shield_check, _cached_shield_result

    now = time.time()
    if _cached_shield_result and (now - _last_shield_check) < _shield_cache_seconds:
        return _cached_shield_result

    _cached_shield_result = full_shield_check()
    _last_shield_check = now
    return _cached_shield_result


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 : POINT D'ENTRÉE CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import io
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("\n" + "=" * 60)
    print("  GESTIONNAIRE RH — BOUCLIER ANTI-FALSIFICATION")
    print("  © 2025 ICG Guinea — Tous droits réservés")
    print("=" * 60)

    print(f"\n  Mode frozen  : {getattr(sys, 'frozen', False)}")
    print(f"  Répertoire   : {_get_install_dir()}")

    report = full_shield_check()

    checks = report.get('checks', {})
    print(f"\n  Débogueur    : {'NON ✓' if checks.get('debugger', True) else 'DÉTECTÉ ✗'}")
    re_tools = checks.get('re_tools', [])
    re_msg = 'AUCUN ✓' if not re_tools else 'DÉTECTÉS ✗ ({})'.format(re_tools)
    print(f"  RE Tools     : {re_msg}")
    print(f"  Extraction   : {'NON ✓' if not checks.get('extraction', {}).get('extracted') else 'DÉTECTÉE ✗'}")
    suspicious = checks.get('suspicious_files', [])
    sus_msg = 'OK ✓' if not suspicious else 'SUSPECTS ✗ ({})'.format(suspicious)
    print(f"  Fichiers     : {sus_msg}")
    print(f"  Cross-vérif  : {'OK ✓' if checks.get('cross_verification', {}).get('valid', True) else 'ÉCHEC ✗'}")
    print(f"  Checksums    : {'OK ✓' if checks.get('file_checksums', {}).get('valid', True) else 'ÉCHEC ✗'}")
    print(f"  Exécutable   : {'OK ✓' if checks.get('exe_integrity', {}).get('valid', True) else 'MODIFIÉ ✗'}")

    if report.get('blocked'):
        print(f"\n  ⛔ BLOQUÉ : {report['reason']}")
    else:
        print(f"\n  ✓ Toutes les vérifications sont passées.")
