# 🗄️ Configuration de la Base de Données

## Vue d'Ensemble

Le projet utilise **python-decouple** pour gérer les variables d'environnement, permettant une configuration flexible de la base de données sans modifier le code.

## 📋 Prérequis

```bash
pip install python-decouple
```

## 🔧 Configuration

### 1. Créer le Fichier `.env`

Copiez le fichier `.env.example` et renommez-le en `.env` :

```bash
cp .env.example .env
```

### 2. Configurer la Base de Données

Éditez le fichier `.env` et configurez les paramètres selon votre environnement.

## 🗃️ Options de Base de Données

### Option 1: SQLite (Par Défaut - Développement)

**Avantages**:
- ✅ Aucune installation requise
- ✅ Parfait pour le développement
- ✅ Fichier unique portable

**Configuration dans `.env`**:
```env
DB_ENGINE=sqlite
```

Le fichier de base de données sera créé automatiquement à `db.sqlite3`.

### Option 2: PostgreSQL (Recommandé - Production)

**Avantages**:
- ✅ Performance optimale
- ✅ Scalabilité
- ✅ Fonctionnalités avancées
- ✅ Recommandé pour la production

**Installation PostgreSQL**:

#### Windows
```bash
# Télécharger depuis https://www.postgresql.org/download/windows/
# Ou via Chocolatey:
choco install postgresql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### macOS
```bash
brew install postgresql
```

**Configuration dans `.env`**:
```env
DB_ENGINE=postgresql
DB_NAME=gestionnaire_rh_guinee
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe_securise
DB_HOST=localhost
DB_PORT=5432
```

**Créer la Base de Données**:
```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE gestionnaire_rh_guinee;

# Créer un utilisateur dédié (optionnel mais recommandé)
CREATE USER rh_user WITH PASSWORD 'mot_de_passe_securise';

# Donner les permissions
GRANT ALL PRIVILEGES ON DATABASE gestionnaire_rh_guinee TO rh_user;

# Quitter
\q
```

### Option 3: MySQL/MariaDB (✅ Compatible Python 3.13)

**Avantages**:
- ✅ **Compatible avec Python 3.13** (contrairement à PostgreSQL)
- ✅ Largement supporté sur les hébergeurs
- ✅ Excellent pour PythonAnywhere
- ✅ Performance optimale

**Installation du Driver**:
```bash
# Linux (Ubuntu/Debian)
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient

# macOS
brew install mysql
pip install mysqlclient

# Windows ou PythonAnywhere
pip install mysqlclient
```

**Configuration dans `.env`**:
```env
DB_ENGINE=mysql
DB_NAME=gestionnaire_rh_guinee
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=3306
```

**Configuration PythonAnywhere**:
```env
DB_ENGINE=mysql
DB_NAME=VOTRE_USERNAME$guineerh_db
DB_USER=VOTRE_USERNAME
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=VOTRE_USERNAME.mysql.pythonanywhere-services.com
DB_PORT=3306
```

**Le support MySQL est déjà intégré dans `settings.py`** ✅

**Créer la Base de Données**:
```bash
# MySQL local
mysql -u root -p
CREATE DATABASE gestionnaire_rh_guinee CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rh_user'@'localhost' IDENTIFIED BY 'mot_de_passe_securise';
GRANT ALL PRIVILEGES ON gestionnaire_rh_guinee.* TO 'rh_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# PythonAnywhere
# Créer la base via l'interface web dans l'onglet "Databases"
```

## 🚀 Initialisation de la Base de Données

Après avoir configuré votre base de données:

```bash
# 1. Créer les migrations
python manage.py makemigrations

# 2. Appliquer les migrations
python manage.py migrate

# 3. Créer un superutilisateur
python manage.py createsuperuser

# 4. (Optionnel) Charger les données de test
python manage.py shell < create_test_data.py
```

## 📊 Structure de Configuration dans `settings.py`

```python
from decouple import config

# Détection du moteur de base de données
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
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

## 🔐 Sécurité

### Bonnes Pratiques

1. **Ne jamais commiter le fichier `.env`**
   - ✅ Déjà dans `.gitignore`
   - ✅ Contient des informations sensibles

2. **Utiliser des mots de passe forts**
   ```python
   # Générer un mot de passe sécurisé
   import secrets
   print(secrets.token_urlsafe(32))
   ```

3. **Limiter les accès à la base de données**
   - Créer un utilisateur dédié avec permissions limitées
   - Ne pas utiliser le compte `postgres` en production

4. **Chiffrer les connexions**
   ```python
   # Pour PostgreSQL avec SSL
   DATABASES = {
       'default': {
           # ... autres configs
           'OPTIONS': {
               'sslmode': 'require',
           }
       }
   }
   ```

## 🌍 Environnements Multiples

### Développement Local
```env
# .env
DB_ENGINE=sqlite
DEBUG=True
```

### Staging
```env
# .env.staging
DB_ENGINE=postgresql
DB_NAME=gestionnaire_rh_staging
DB_USER=rh_staging_user
DB_PASSWORD=staging_password_secure
DB_HOST=staging-db.example.com
DB_PORT=5432
DEBUG=False
```

### Production
```env
# .env.production
DB_ENGINE=postgresql
DB_NAME=gestionnaire_rh_production
DB_USER=rh_prod_user
DB_PASSWORD=production_password_very_secure
DB_HOST=prod-db.example.com
DB_PORT=5432
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🔄 Migration entre Bases de Données

### De SQLite vers PostgreSQL

```bash
# 1. Exporter les données de SQLite
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > data.json

# 2. Modifier .env pour PostgreSQL
DB_ENGINE=postgresql
# ... autres paramètres

# 3. Créer la nouvelle base de données PostgreSQL
createdb gestionnaire_rh_guinee

# 4. Appliquer les migrations
python manage.py migrate

# 5. Importer les données
python manage.py loaddata data.json
```

## 📦 Sauvegarde et Restauration

### PostgreSQL

**Sauvegarde**:
```bash
# Sauvegarde complète
pg_dump -U postgres gestionnaire_rh_guinee > backup_$(date +%Y%m%d).sql

# Sauvegarde compressée
pg_dump -U postgres gestionnaire_rh_guinee | gzip > backup_$(date +%Y%m%d).sql.gz
```

**Restauration**:
```bash
# Restaurer depuis un fichier SQL
psql -U postgres gestionnaire_rh_guinee < backup_20251026.sql

# Restaurer depuis un fichier compressé
gunzip -c backup_20251026.sql.gz | psql -U postgres gestionnaire_rh_guinee
```

### SQLite

**Sauvegarde**:
```bash
# Simple copie du fichier
cp db.sqlite3 backup_db_$(date +%Y%m%d).sqlite3
```

**Restauration**:
```bash
# Remplacer le fichier actuel
cp backup_db_20251026.sqlite3 db.sqlite3
```

## 🐛 Dépannage

### Erreur: "No module named 'psycopg2'"
```bash
# Installer le driver PostgreSQL
pip install psycopg2-binary
```

### Erreur: "FATAL: password authentication failed"
- Vérifier le mot de passe dans `.env`
- Vérifier que l'utilisateur existe dans PostgreSQL
- Vérifier `pg_hba.conf` pour les méthodes d'authentification

### Erreur: "could not connect to server"
- Vérifier que PostgreSQL est démarré
- Vérifier le HOST et PORT dans `.env`
- Vérifier le pare-feu

### Erreur: "database does not exist"
```bash
# Créer la base de données
createdb -U postgres gestionnaire_rh_guinee
```

## 📚 Ressources

- [Django Database Documentation](https://docs.djangoproject.com/en/stable/ref/databases/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [python-decouple Documentation](https://pypi.org/project/python-decouple/)

## ✅ Checklist de Configuration

- [ ] `python-decouple` installé
- [ ] Fichier `.env` créé depuis `.env.example`
- [ ] Paramètres de base de données configurés
- [ ] Base de données créée (si PostgreSQL/MySQL)
- [ ] Migrations appliquées (`python manage.py migrate`)
- [ ] Superutilisateur créé (`python manage.py createsuperuser`)
- [ ] Données de test chargées (optionnel)
- [ ] Connexion testée avec succès

---

**Version**: 1.0.0  
**Date**: 26 Octobre 2025  
**Statut**: ✅ Documenté
