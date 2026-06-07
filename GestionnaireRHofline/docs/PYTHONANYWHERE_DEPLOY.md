# Déploiement sur PythonAnywhere

## Configuration actuelle

- **Domaine**: www.guineerh.space
- **CNAME**: webapp-2809123.pythonanywhere.com
- **Code source**: /home/guineerh/gestionrh
- **Python**: 3.12
- **Environnement virtuel**: /home/guineerh/gestionrh/venv

## Étapes de mise à jour

### 1. Connexion SSH/Console

Ouvrez une console Bash sur PythonAnywhere.

### 2. Mise à jour du code

```bash
cd /home/guineerh/gestionrh
git pull origin main
```

### 3. Activer l'environnement virtuel

```bash
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Configurer le fichier .env

Créez ou modifiez `/home/guineerh/gestionrh/.env`:

```bash
nano .env
```

Contenu:
```env
SECRET_KEY=votre-cle-secrete-unique-generee
DEBUG=False
DB_ENGINE=mysql
DB_NAME=guineerh$gestionnaire_rh
DB_USER=guineerh
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=guineerh.mysql.pythonanywhere-services.com
DB_PORT=3306
ALLOWED_HOSTS=www.guineerh.space,guineerh.space,guineerh.pythonanywhere.com
```

Pour générer une SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Appliquer les migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 7. Fichier WSGI

Modifiez `/var/www/www_guineerh_space_wsgi.py`:

```python
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

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 8. Installer python-dotenv

```bash
pip install python-dotenv
```

### 9. Recharger l'application

Allez dans le dashboard PythonAnywhere → Web → Cliquez sur **Reload**

## Configuration des fichiers statiques

Dans l'onglet Web de PythonAnywhere:

| URL | Répertoire |
|-----|------------|
| `/static/` | `/home/guineerh/gestionrh/staticfiles` |
| `/media/` | `/home/guineerh/gestionrh/media` |

## Base de données MySQL

### Créer la base de données

1. Allez dans **Databases** sur PythonAnywhere
2. Créez une base de données MySQL
3. Nom: `guineerh$gestionnaire_rh`
4. Notez le mot de passe

### Paramètres de connexion

- **Host**: `guineerh.mysql.pythonanywhere-services.com`
- **User**: `guineerh`
- **Database**: `guineerh$gestionnaire_rh`

## Multi-Tenant (PostgreSQL)

⚠️ **Note importante**: L'architecture multi-tenant avec `django-tenants` nécessite **PostgreSQL**, disponible uniquement avec un compte PythonAnywhere payant.

Si vous avez un compte payant avec PostgreSQL:

1. Créez une base PostgreSQL dans l'onglet Databases
2. Modifiez `.env`:
   ```env
   DB_ENGINE=postgresql
   DB_HOST=guineerh-XXXX.postgres.pythonanywhere-services.com
   DB_PORT=XXXXX
   ```
3. Remplacez `settings.py` par `settings_tenant.py`
4. Exécutez les migrations multi-tenant

## Commandes utiles

```bash
# Vérifier les erreurs
python manage.py check --deploy

# Créer un superutilisateur
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Voir les logs
tail -f /var/log/www.guineerh.space.error.log
```

## Dépannage

### Erreur 500

1. Vérifiez les logs: `/var/log/www.guineerh.space.error.log`
2. Vérifiez que DEBUG=False et que ALLOWED_HOSTS est correct
3. Vérifiez la connexion à la base de données

### Static files non chargés

```bash
python manage.py collectstatic --noinput
```

Puis rechargez l'application web.

### Erreur de connexion MySQL

Vérifiez:
- Le mot de passe dans `.env`
- Le host MySQL (doit finir par `.mysql.pythonanywhere-services.com`)
- Que la base de données existe

## Sécurité en production

1. ✅ `DEBUG=False`
2. ✅ `SECRET_KEY` unique et secrète
3. ✅ `HTTPS` forcé (dans l'onglet Web)
4. ✅ `ALLOWED_HOSTS` configuré
5. ✅ Mot de passe base de données fort
