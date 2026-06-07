"""
Django settings for gestionnaire_rh project with Multi-Tenant support.
Ce fichier étend settings.py pour ajouter la configuration django-tenants.

IMPORTANT: Pour activer le multi-tenant:
1. Installer PostgreSQL
2. Configurer DB_ENGINE=postgresql dans .env
3. Renommer ce fichier en settings.py (après backup de l'original)
4. Exécuter: python manage.py migrate_schemas --shared
5. Créer le tenant public: python manage.py create_tenant
"""

from pathlib import Path
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Domaines autorisés - incluant les sous-domaines pour les tenants
ALLOWED_HOSTS = ['www.guineerh.space', 'guineerh.space', '.guineerh.space', 
                 'guineerh.pythonanywhere.com', 'localhost', '127.0.0.1',
                 '.localhost']  # Le point permet les sous-domaines

# ============================================================================
# CONFIGURATION DJANGO-TENANTS
# ============================================================================

# Applications partagées (dans le schéma public, communes à tous les tenants)
SHARED_APPS = [
    'django_tenants',  # DOIT être en premier
    'tenants',  # Notre app de gestion des tenants
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third party apps partagées
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'widget_tweaks',
    'import_export',
    'rest_framework',
    'corsheaders',
    'axes',
    'csp',
    
    # Core app (contient Utilisateur, ProfilUtilisateur)
    'core',
]

# Applications spécifiques à chaque tenant (dans leur propre schéma)
TENANT_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    
    # Apps métier - données isolées par tenant
    'core',  # Pour les modèles spécifiques tenant
    'employes',
    'paie',
    'temps_travail',
    'recrutement',
    'formation',
    'dashboard',
    'payments',
    'portail',
]

# Toutes les applications installées
INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

# Modèle Tenant
TENANT_MODEL = "tenants.Client"
TENANT_DOMAIN_MODEL = "tenants.Domain"

# Configuration du schéma public
PUBLIC_SCHEMA_NAME = 'public'

# ============================================================================
# MIDDLEWARE
# ============================================================================

MIDDLEWARE = [
    # Django-tenants middleware DOIT être en premier
    'django_tenants.middleware.main.TenantMainMiddleware',
    
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Security middlewares
    'axes.middleware.AxesMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
    'core.middleware.SQLInjectionProtectionMiddleware',
    'core.middleware.XSSProtectionMiddleware',
    'core.middleware.RequestLoggingMiddleware',
]

# ============================================================================
# DATABASE - PostgreSQL REQUIS pour django-tenants
# ============================================================================

DATABASE_ROUTERS = ['django_tenants.routers.TenantSyncRouter']

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': config('DB_NAME', default='gestionnaire_rh_guinee'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# ============================================================================
# URLS
# ============================================================================

ROOT_URLCONF = 'gestionnaire_rh.urls_tenant'
PUBLIC_SCHEMA_URLCONF = 'gestionnaire_rh.urls_public'

# ============================================================================
# TEMPLATES
# ============================================================================

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
                'core.context_processors.company_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestionnaire_rh.wsgi.application'

# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Conakry'
USE_I18N = True
USE_TZ = True

# ============================================================================
# STATIC & MEDIA FILES
# ============================================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# AUTH
# ============================================================================

AUTH_USER_MODEL = 'core.Utilisateur'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'login'

# ============================================================================
# AUTRES CONFIGURATIONS
# ============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Sessions
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True

# CSRF
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# Axes (protection brute force)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_LOCKOUT_TEMPLATE = 'core/lockout.html'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'security': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'security': {
            'handlers': ['security'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Créer le dossier logs s'il n'existe pas
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ============================================================================
# CONFIGURATION MULTI-TENANT ADDITIONNELLE
# ============================================================================

# Afficher le tenant dans la console (debug)
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True

# Domaine par défaut pour les nouveaux tenants
DEFAULT_TENANT_DOMAIN = config('DEFAULT_TENANT_DOMAIN', default='localhost')
