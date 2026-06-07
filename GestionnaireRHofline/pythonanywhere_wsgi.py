"""
Configuration WSGI pour PythonAnywhere
À copier dans: /var/www/fastlanelogisticgn_com_wsgi.py
(ou le fichier WSGI généré automatiquement quand vous créez la Web App
 avec le domaine personnalisé fastlanelogisticgn.com sur PythonAnywhere)
"""
import os
import sys
from pathlib import Path

# Chemin vers le projet
path = '/home/guineerh/gestionrh'
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
os.environ.setdefault('SECRET_KEY', 'votre-cle-secrete-de-production-a-changer')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
