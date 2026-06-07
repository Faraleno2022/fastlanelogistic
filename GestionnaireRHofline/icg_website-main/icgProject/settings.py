from pathlib import Path
from decouple import config
import dj_database_url
import os
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
if not SECRET_KEY or len(SECRET_KEY) < 20:
    raise ImproperlyConfigured('SECRET_KEY not configured or too short in .env')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    "icguinea.com",
    'www.icguinea.com',
    'icg-6bg2.onrender.com',
]
if DEBUG:
    ALLOWED_HOSTS.extend(['127.0.0.1', 'localhost'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'appli',
]

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

ROOT_URLCONF = 'icgProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'icgProject.wsgi.application'

DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

CLOUDFLARE_R2_BUCKET = config('CLOUDFLARE_R2_BUCKET')
CLOUDFLARE_R2_ACCESS_KEY = config('CLOUDFLARE_R2_ACCESS_KEY')
CLOUDFLARE_R2_SECRET_KEY = config('CLOUDFLARE_R2_SECRET_KEY')
CLOUDFLARE_R2_API_ENDPOINT = config('CLOUDFLARE_R2_API_ENDPOINT')
CLOUDFLARE_R2_PUBLIC_URL = config('CLOUDFLARE_R2_PUBLIC_URL')

AWS_S3_CUSTOM_DOMAIN = f"{CLOUDFLARE_R2_PUBLIC_URL.replace('https://', '')}/{CLOUDFLARE_R2_BUCKET}"
AWS_S3_URL_PROTOCOL = 'https:'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = f"{AWS_S3_URL_PROTOCOL}//{AWS_S3_CUSTOM_DOMAIN}/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CLOUDFLARE_R2_CONFIG_OPTIONS = {
    'bucket_name': CLOUDFLARE_R2_BUCKET,
    'access_key': CLOUDFLARE_R2_ACCESS_KEY,
    'secret_key': CLOUDFLARE_R2_SECRET_KEY,
    'endpoint_url': CLOUDFLARE_R2_API_ENDPOINT,
    'default_acl': 'public-read',
    'file_overwrite': False,
    'signature_version': 's3v4',
    'querystring_auth': False,
    'region_name': None,
}

STORAGES = {
    'default': {
        'BACKEND': 'helpers.cloudflare.storages.MediaFileStorage',
        'OPTIONS': CLOUDFLARE_R2_CONFIG_OPTIONS,
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DEFAULT_FILE_STORAGE = 'helpers.cloudflare.storages.MediaFileStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_AGE = 3600 * 24
SESSION_SAVE_EVERY_REQUEST = True

SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_REFERRER_POLICY = None
X_FRAME_OPTIONS = 'SAMEORIGIN'




# --- NOUVELLE CONFIGURATION DE LOGGING POUR LA PRODUCTION ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'appli': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}