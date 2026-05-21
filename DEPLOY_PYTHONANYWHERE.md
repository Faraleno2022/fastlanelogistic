# Déploiement sur PythonAnywhere (MySQL)

## 1. Uploader le projet
Cloner ou uploader le dossier `fastlane_app/` dans `/home/<user>/fastlane_app/`.

## 2. Virtualenv
```bash
mkvirtualenv fastlane --python=python3.12
pip install -r requirements.txt
```

## 3. Créer la base MySQL
Onglet **Databases** sur PythonAnywhere → créer `fastlane$default`.
Noter l'hôte (`<user>.mysql.pythonanywhere-services.com`).

## 4. Variables d'environnement
Dans l'onglet **Web → WSGI configuration file**, en tête de fichier :

```python
import os
os.environ["DJANGO_SECRET_KEY"] = "..."
os.environ["DJANGO_DEBUG"] = "0"
os.environ["DJANGO_ALLOWED_HOSTS"] = "<user>.pythonanywhere.com"
os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = "https://<user>.pythonanywhere.com"
os.environ["DB_ENGINE"] = "mysql"
os.environ["DB_NAME"] = "<user>$default"
os.environ["DB_USER"] = "<user>"
os.environ["DB_PASSWORD"] = "..."
os.environ["DB_HOST"] = "<user>.mysql.pythonanywhere-services.com"
os.environ["DB_PORT"] = "3306"

import sys
path = "/home/<user>/fastlane_app"
if path not in sys.path:
    sys.path.insert(0, path)

from django.core.wsgi import get_wsgi_application
os.environ["DJANGO_SETTINGS_MODULE"] = "fastlane.settings"
application = get_wsgi_application()
```

## 5. Migrations + superuser + static
```bash
cd ~/fastlane_app
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## 6. Static & Media mappings (onglet Web)
- URL `/static/` → `/home/<user>/fastlane_app/staticfiles`
- URL `/media/`  → `/home/<user>/fastlane_app/media`

## 7. Reload
Cliquer sur **Reload** dans l'onglet Web.

## URLs publiques / privées
- `/` `/a-propos/` `/evenements/` `/appels-offres/` → **public** (pas de lien de connexion)
- `/connexion/` → écran de login
- `/dashboard/` `/flotte/` `/rh/` `/operations/` `/facturation/` → **backoffice** (authentifié)
- `/admin/` → administration Django (superuser)
