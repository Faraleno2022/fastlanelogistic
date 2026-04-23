"""Django settings for Fastlane Logistic management application."""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Charge les variables depuis .env à la racine du projet (si présent)
_ENV_FILE = BASE_DIR / ".env"
if _ENV_FILE.exists():
    try:
        import environ
        environ.Env.read_env(str(_ENV_FILE))
    except Exception:
        # Fallback minimal parser si django-environ indisponible
        for _line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-me-in-production-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "localhost,127.0.0.1,.pythonanywhere.com",
    ).split(",") if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "https://*.pythonanywhere.com",
    ).split(",") if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    # 3rd party
    "crispy_forms",
    "crispy_bootstrap5",
    "widget_tweaks",
    # apps
    "apps.accounts",
    "apps.core",
    "apps.flotte",
    "apps.rh",
    "apps.operations",
    "apps.facturation",
    "apps.dashboard",
    "apps.public",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fastlane.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_context",
                "apps.public.context_processors.seo_context",
            ],
        },
    },
]

WSGI_APPLICATION = "fastlane.wsgi.application"

# Base de données : SQLite par défaut (dev), MySQL en production (PythonAnywhere).
# Pour activer MySQL, positionner DB_ENGINE=mysql et les variables DB_* ci-dessous.
_DB_ENGINE = os.environ.get("DB_ENGINE", "sqlite").lower()
if _DB_ENGINE in ("mysql", "django.db.backends.mysql"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DB_NAME", ""),
            "USER": os.environ.get("DB_USER", ""),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", "60")),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Conakry"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/connexion/"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "/"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Société
SOCIETE_NOM = "Fastlane Logistic"
SOCIETE_DEVISE = "GNF"
SOCIETE_ACTIVITE = "Transport de Bauxite"

# ===================== SEO / Référencement =====================
SEO_SITE_URL = os.environ.get(
    "SEO_SITE_URL", "https://www.fastlanelogisticgn.com"
).rstrip("/")
SEO_SITE_NAME = "Fastlane Logistic"
SEO_DEFAULT_TITLE = (
    "Fastlane Logistic — Transport de bauxite & logistique minière en Guinée"
)
SEO_DEFAULT_DESCRIPTION = (
    "Fastlane Logistic est une entreprise guinéenne spécialisée dans le "
    "transport général de marchandises et le transport minier (bauxite) sur "
    "les corridors Boké – Kamsar – Conakry. Flotte moderne, chauffeurs "
    "qualifiés, traçabilité complète."
)
SEO_DEFAULT_KEYWORDS = (
    "Fastlane Logistic, transport bauxite Guinée, logistique minière Guinée, "
    "transport Conakry, transport Boké, transport Kamsar, camion bauxite, "
    "transport marchandises Guinée, entreprise transport Guinée, Kolaboui, "
    "corridor minier, Zonda, Auman, appel d'offres transport Guinée"
)
SEO_LOCALE = "fr_FR"
SEO_TWITTER_HANDLE = os.environ.get("SEO_TWITTER_HANDLE", "")
SEO_FB_APP_ID = os.environ.get("SEO_FB_APP_ID", "")
SEO_DEFAULT_OG_IMAGE = "images/home2.png"  # relatif à STATIC_URL
SEO_ORGANIZATION = {
    "name": "Fastlane Logistic",
    "legal_name": "Fastlane Logistic SARL",
    "founding_year": "2020",
    "phone": "+224 000 000 000",
    "email": "contact@fastlanelogisticgn.com",
    "street": "Kipé Centre Émetteur",
    "locality": "Conakry",
    "region": "Conakry",
    "country": "GN",
    "postal": "",
    "areas_served": ["Guinée", "Conakry", "Boké", "Kamsar", "Kolaboui"],
    "social": [
        # Compléter si présence sur ces plateformes :
        # "https://www.facebook.com/fastlanelogistic",
        # "https://www.linkedin.com/company/fastlane-logistic",
    ],
}

# Paramètres métier (modifiables en admin via SingletonParametres)
DEFAULT_DUREE_AMORTISSEMENT = 5  # années
DEFAULT_TAUX_RESIDUEL = 0.10
DEFAULT_PRIX_CARBURANT = 12000  # GNF/L
DEFAULT_TARIF_BAUXITE = 85000  # GNF/T
DEFAULT_TAUX_TVA = 0.18
