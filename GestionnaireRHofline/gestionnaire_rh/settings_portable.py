"""
Django settings pour mode portable/installable.
Ce fichier est autonome et ne dépend pas des settings de base.
"""
import os
from pathlib import Path

# Répertoires pour mode portable
APP_DIR = Path(os.environ.get('GESTIONNAIRE_RH_APP_DIR', Path(__file__).parent.parent))
DATA_DIR = Path(os.environ.get('GESTIONNAIRE_RH_DATA_DIR', APP_DIR / 'data'))
BASE_DIR = APP_DIR

# Créer les répertoires nécessaires
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / 'logs').mkdir(exist_ok=True)
(DATA_DIR / 'media').mkdir(exist_ok=True)

# Mode production local
DEBUG = False
SECRET_KEY = 'portable-installation-key-change-in-production-env'

# Hosts autorisés pour mode local
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

# Base de données SQLite dans le dossier data
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_DIR / 'gestionnaire_rh.db',
    }
}

# Fichiers statiques
STATIC_ROOT = APP_DIR / 'staticfiles'
STATICFILES_DIRS = [APP_DIR / 'static'] if (APP_DIR / 'static').exists() else []

# Fichiers média dans le dossier data
MEDIA_ROOT = DATA_DIR / 'media'

# Logs dans le dossier data
LOGGING['handlers']['file']['filename'] = DATA_DIR / 'logs' / 'django.log'
LOGGING['handlers']['security_file']['filename'] = DATA_DIR / 'logs' / 'security.log'

# Désactiver les redirections HTTPS pour mode local
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Désactiver HSTS pour mode local
SECURE_HSTS_SECONDS = 0

# Email en mode console pour debug local
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache en mémoire
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Session en base de données
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Désactiver les fonctionnalités nécessitant Redis
DEFENDER_DISABLE_IP_LOCKOUT = True
DEFENDER_DISABLE_USERNAME_LOCKOUT = True

# CSRF trusted origins pour mode local
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# WhiteNoise pour servir les fichiers statiques
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

print(f"[GestionnaireRH] Mode portable activé")
print(f"[GestionnaireRH] Données: {DATA_DIR}")
print(f"[GestionnaireRH] Base de données: {DATABASES['default']['NAME']}")
