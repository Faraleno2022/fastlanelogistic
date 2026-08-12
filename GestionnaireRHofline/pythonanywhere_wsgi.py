"""
Configuration WSGI pour app.fastlanelogisticgn.com sur PythonAnywhere.
À copier dans le fichier WSGI de la Web App du compte Fastlane.
"""
import os
import sys
from pathlib import Path

# Chemin vers le projet
path = '/home/Fastlane/fastlane_app/GestionnaireRHofline'
if path not in sys.path:
    sys.path.insert(0, path)

os.chdir(path)

# Charger les variables d'environnement depuis .env
env_path = Path(path) / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionnaire_rh.settings')

# Variables de production (si non définies dans .env)
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('DJANGO_EXTRA_ALLOWED_HOSTS', 'app.fastlanelogisticgn.com')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
