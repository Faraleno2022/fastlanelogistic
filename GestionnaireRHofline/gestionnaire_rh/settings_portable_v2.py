"""
Django settings pour mode portable/installable.
Ce fichier est autonome - version simplifiée pour l'exécutable standalone.
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
DEBUG = True  # True pour voir les erreurs
SECRET_KEY = 'portable-installation-key-guineerh-2024'

# Hosts autorisés pour mode local
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

# Application definition - Version simplifiée sans axes/defender/corsheaders
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third party apps (simplifiés)
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'widget_tweaks',
    'import_export',
    'rest_framework',
    
    # Local apps
    'core',
    'employes',
    'paie',
    'temps_travail',
    'recrutement',
    'formation',
    'dashboard',
    'payments',
]

# Middleware simplifié (sans axes, defender, csp, corsheaders)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gestionnaire_rh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestionnaire_rh.wsgi.application'

# Base de données SQLite dans le dossier data
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_DIR / 'gestionnaire_rh.db',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Conakry'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = APP_DIR / 'staticfiles'
STATICFILES_DIRS = [APP_DIR / 'static'] if (APP_DIR / 'static').exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = DATA_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'core.Utilisateur'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'core:login'

# Email en mode console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Company Settings
COMPANY_NAME = 'Gestionnaire RH Guinée'

# Paie Settings
SMIG_GUINEE = 440000
TAUX_CNSS_EMPLOYE = 5.0
TAUX_CNSS_EMPLOYEUR = 18.0
TAUX_INAM = 2.5
CONGES_ANNUELS = 26
HEURES_MENSUELLES = 173.33
JOURS_TRAVAIL_MOIS = 22

# Security - Mode local simplifié
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Session
SESSION_COOKIE_AGE = 86400  # 24 heures
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Cache en mémoire
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# Authentication Backends - Simplifié
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Logging simplifié
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

print(f"[GestionnaireRH] Mode portable activé")
print(f"[GestionnaireRH] Données: {DATA_DIR}")
print(f"[GestionnaireRH] Base de données: {DATABASES['default']['NAME']}")
