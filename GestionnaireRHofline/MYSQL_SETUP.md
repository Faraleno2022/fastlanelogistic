# 🐬 Configuration MySQL pour Python 3.13

## 🎯 Pourquoi MySQL ?

**Problème** : `psycopg2` (driver PostgreSQL) est incompatible avec Python 3.13.

**Solution** : Utiliser MySQL qui fonctionne parfaitement avec Python 3.13 via `mysqlclient`.

## 📋 Prérequis

### Installation du Driver MySQL

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Installer le driver MySQL
pip install mysqlclient
```

**Note** : Si l'installation échoue, installez les dépendances système :

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

#### macOS
```bash
brew install mysql
pip install mysqlclient
```

#### Windows
```bash
# Télécharger et installer MySQL Connector/C
# Puis installer mysqlclient
pip install mysqlclient
```

## 🔧 Configuration pour PythonAnywhere

### 1. Créer le Fichier `.env`

Sur votre serveur PythonAnywhere :

```bash
cd ~/ETRAGC_SARLU/gestionrh

# Supprimer l'ancien .env si existant
rm -f .env

# Créer le nouveau .env pour MySQL
cat > .env << 'EOF'
SECRET_KEY=django-insecure-e28efk23bh1@7&1k^luh50mhln3nz_bk34ms-i(8^u_a_!f+aj
DEBUG=False
ALLOWED_HOSTS=www.guineerh.space,guineerh.space,ETRAGCSARLU.pythonanywhere.com,127.0.0.1,localhost

# MySQL Configuration
DB_ENGINE=mysql
DB_NAME=ETRAGCSARLU$guineerh_db
DB_USER=ETRAGCSARLU
DB_PASSWORD=FELIXSUZANELENO1994@
DB_HOST=ETRAGCSARLU.mysql.pythonanywhere-services.com
DB_PORT=3306

# Email Configuration (optionnel)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Application Settings
COMPANY_NAME=ETRAGC SARL
EOF
```

### 2. Vérifier la Configuration

```bash
# Afficher le contenu du .env
cat .env

# Charger les variables d'environnement
export $(cat .env | xargs)

# Vérifier qu'elles sont chargées
echo "DB_ENGINE: $DB_ENGINE"
echo "DB_NAME: $DB_NAME"
echo "DB_HOST: $DB_HOST"
```

### 3. Installer mysqlclient

```bash
# Sur PythonAnywhere, mysqlclient est généralement déjà disponible
pip install mysqlclient

# Ou si vous avez un requirements.txt
pip install -r requirements.txt
```

### 4. Exécuter les Migrations

```bash
# Charger les variables d'environnement
export $(cat .env | xargs)

# Tester la connexion
python manage.py check

# Créer les migrations si nécessaire
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

## 🗄️ Configuration MySQL sur PythonAnywhere

### Créer la Base de Données

1. **Aller dans l'onglet "Databases"** sur PythonAnywhere
2. **Créer une nouvelle base de données MySQL**
   - Nom : `guineerh_db` (sera préfixé automatiquement par votre username)
   - Le nom complet sera : `ETRAGCSARLU$guineerh_db`

3. **Noter les informations de connexion** :
   - Host : `ETRAGCSARLU.mysql.pythonanywhere-services.com`
   - Username : `ETRAGCSARLU`
   - Database : `ETRAGCSARLU$guineerh_db`
   - Port : `3306`

## 📝 Structure de Configuration dans `settings.py`

Le fichier `settings.py` a été mis à jour pour supporter MySQL :

```python
from decouple import config

DB_ENGINE = config('DB_ENGINE', default='sqlite')

if DB_ENGINE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='gestionnaire_rh_guinee'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
elif DB_ENGINE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

## 🚀 Déploiement Complet sur PythonAnywhere

### Script de Déploiement Automatique

```bash
#!/bin/bash
# deploy_mysql.sh

cd ~/ETRAGC_SARLU/gestionrh

# 1. Activer l'environnement virtuel
source venv/bin/activate

# 2. Installer les dépendances
pip install mysqlclient python-decouple

# 3. Créer le fichier .env
cat > .env << 'EOF'
SECRET_KEY=django-insecure-e28efk23bh1@7&1k^luh50mhln3nz_bk34ms-i(8^u_a_!f+aj
DEBUG=False
ALLOWED_HOSTS=www.guineerh.space,guineerh.space,ETRAGCSARLU.pythonanywhere.com,127.0.0.1,localhost
DB_ENGINE=mysql
DB_NAME=ETRAGCSARLU$guineerh_db
DB_USER=ETRAGCSARLU
DB_PASSWORD=FELIXSUZANELENO1994@
DB_HOST=ETRAGCSARLU.mysql.pythonanywhere-services.com
DB_PORT=3306
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
COMPANY_NAME=ETRAGC SARL
EOF

# 4. Charger les variables
export $(cat .env | xargs)

# 5. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 6. Appliquer les migrations
python manage.py migrate

echo "✅ Déploiement MySQL terminé!"
```

Rendez-le exécutable et lancez-le :

```bash
chmod +x deploy_mysql.sh
./deploy_mysql.sh
```

## 🔐 Sécurité

### Bonnes Pratiques

1. **Ne jamais commiter le fichier `.env`**
   - ✅ Déjà dans `.gitignore`

2. **Utiliser des mots de passe forts**
   - Changez le SECRET_KEY en production
   - Utilisez un mot de passe complexe pour MySQL

3. **Limiter les accès**
   - Sur PythonAnywhere, seul votre compte peut accéder à votre base MySQL
   - Activez HTTPS (déjà configuré avec `guineerh.space`)

## 🐛 Dépannage

### Erreur : "No module named 'MySQLdb'"

```bash
pip install mysqlclient
```

### Erreur : "Access denied for user"

Vérifiez dans `.env` :
- `DB_USER` doit être votre username PythonAnywhere
- `DB_PASSWORD` doit être le mot de passe MySQL
- `DB_NAME` doit inclure le préfixe `ETRAGCSARLU$`

### Erreur : "Can't connect to MySQL server"

Vérifiez :
- `DB_HOST` : `ETRAGCSARLU.mysql.pythonanywhere-services.com`
- `DB_PORT` : `3306`
- Que la base de données existe sur PythonAnywhere

### Tester la Connexion MySQL

```bash
python manage.py shell
```

Puis dans le shell :

```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT VERSION()")
print(cursor.fetchone())
print("✅ Connexion MySQL réussie!")
```

## 📊 Migration depuis SQLite vers MySQL

Si vous avez déjà des données dans SQLite :

```bash
# 1. Exporter les données de SQLite
python manage.py dumpdata --natural-foreign --natural-primary \
  -e contenttypes -e auth.Permission --indent 4 > data.json

# 2. Modifier .env pour MySQL
# (voir configuration ci-dessus)

# 3. Appliquer les migrations sur MySQL
export $(cat .env | xargs)
python manage.py migrate

# 4. Importer les données
python manage.py loaddata data.json
```

## ✅ Checklist de Configuration MySQL

- [ ] `mysqlclient` installé
- [ ] Base de données MySQL créée sur PythonAnywhere
- [ ] Fichier `.env` créé avec les bonnes informations
- [ ] Variables d'environnement chargées
- [ ] `python manage.py check` réussi
- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Application testée

## 📚 Ressources

- [Django MySQL Documentation](https://docs.djangoproject.com/en/stable/ref/databases/#mysql-notes)
- [PythonAnywhere MySQL Help](https://help.pythonanywhere.com/pages/UsingMySQL/)
- [mysqlclient Documentation](https://github.com/PyMySQL/mysqlclient)

## 🎯 Commandes Rapides

```bash
# Installation complète
pip install mysqlclient python-decouple

# Configuration et migration
export $(cat .env | xargs) && python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Redémarrer l'application (sur PythonAnywhere)
# Aller dans l'onglet "Web" et cliquer sur "Reload"
```

---

**Version** : 1.0.0  
**Date** : 26 Octobre 2025  
**Compatibilité** : Python 3.13 ✅  
**Statut** : ✅ Testé et Fonctionnel
