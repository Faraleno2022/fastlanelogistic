# 🚀 Guide de Déploiement - Gestionnaire RH Guinée

## 🎯 Vue d'Ensemble

Ce guide vous accompagne dans le déploiement complet de l'application sur PythonAnywhere avec MySQL et Python 3.13.

## ✅ Prérequis

- Compte PythonAnywhere (gratuit ou payant)
- Accès à votre repository GitHub
- Base de données MySQL créée sur PythonAnywhere
- Domaine personnalisé configuré (optionnel)

## 📋 Checklist Avant Déploiement

- [ ] Repository GitHub à jour
- [ ] Base de données MySQL créée
- [ ] Fichier `.env` préparé avec les bonnes informations
- [ ] Domaine configuré (si applicable)

## 🔧 Étape 1 : Configuration Initiale sur PythonAnywhere

### 1.1 Cloner le Repository

```bash
# Se connecter via SSH ou console Bash
cd ~
mkdir -p ETRAGC_SARLU
cd ETRAGC_SARLU

# Cloner le repository
git clone https://github.com/Faraleno2022/gestionrh.git
cd gestionrh
```

### 1.2 Créer l'Environnement Virtuel

```bash
# Créer l'environnement avec Python 3.13
python3.13 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Vérifier la version Python
python --version  # Devrait afficher Python 3.13.x
```

### 1.3 Installer les Dépendances

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Installer spécifiquement mysqlclient si nécessaire
pip install mysqlclient
```

## 🗄️ Étape 2 : Configuration de la Base de Données

### 2.1 Créer la Base MySQL sur PythonAnywhere

1. Aller dans l'onglet **"Databases"**
2. Créer une nouvelle base de données MySQL
3. Nom suggéré : `guineerh_db`
4. Noter les informations de connexion

### 2.2 Créer le Fichier `.env`

```bash
cd ~/ETRAGC_SARLU/gestionrh

# Créer le fichier .env
cat > .env << 'EOF'
# Django Settings
SECRET_KEY=django-insecure-e28efk23bh1@7&1k^luh50mhln3nz_bk34ms-i(8^u_a_!f+aj
DEBUG=False
ALLOWED_HOSTS=www.guineerh.space,guineerh.space,ETRAGCSARLU.pythonanywhere.com,127.0.0.1,localhost

# MySQL Database
DB_ENGINE=mysql
DB_NAME=ETRAGCSARLU$guineerh_db
DB_USER=ETRAGCSARLU
DB_PASSWORD=VOTRE_MOT_DE_PASSE_MYSQL
DB_HOST=ETRAGCSARLU.mysql.pythonanywhere-services.com
DB_PORT=3306

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Application Settings
COMPANY_NAME=ETRAGC SARL

# Security Settings (Production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
EOF

# Remplacer VOTRE_MOT_DE_PASSE_MYSQL par le vrai mot de passe
nano .env
```

### 2.3 Appliquer les Migrations

```bash
# Charger les variables d'environnement
export $(cat .env | xargs)

# Vérifier la configuration
python manage.py check

# Créer les migrations si nécessaire
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

## 📁 Étape 3 : Fichiers Statiques

### 3.1 Collecter les Fichiers Statiques

```bash
# Collecter tous les fichiers statiques
python manage.py collectstatic --noinput
```

### 3.2 Vérifier les Dossiers

```bash
# Vérifier que les dossiers existent
ls -la staticfiles/
ls -la media/
```

## 🌐 Étape 4 : Configuration de l'Application Web

### 4.1 Créer une Nouvelle Application Web

1. Aller dans l'onglet **"Web"**
2. Cliquer sur **"Add a new web app"**
3. Choisir **"Manual configuration"**
4. Sélectionner **Python 3.13**

### 4.2 Configurer le WSGI

Éditer le fichier WSGI (`/var/www/ETRAGCSARLU_pythonanywhere_com_wsgi.py`) :

```python
import os
import sys

# Ajouter le chemin du projet
path = '/home/ETRAGCSARLU/ETRAGC_SARLU/gestionrh'
if path not in sys.path:
    sys.path.insert(0, path)

# Charger les variables d'environnement depuis .env
from pathlib import Path
env_file = Path(path) / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionnaire_rh.settings')

# Application WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 4.3 Configurer l'Environnement Virtuel

Dans l'onglet **"Web"**, section **"Virtualenv"** :
```
/home/ETRAGCSARLU/ETRAGC_SARLU/gestionrh/venv
```

### 4.4 Configurer les Fichiers Statiques

Dans l'onglet **"Web"**, section **"Static files"** :

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/ETRAGCSARLU/ETRAGC_SARLU/gestionrh/staticfiles` |
| `/media/` | `/home/ETRAGCSARLU/ETRAGC_SARLU/gestionrh/media` |

### 4.5 Configurer le Domaine Personnalisé

Si vous avez un domaine (ex: www.guineerh.space) :

1. Dans l'onglet **"Web"**, ajouter le domaine
2. Configurer les DNS chez votre registrar :
   ```
   Type: CNAME
   Name: www
   Value: ETRAGCSARLU.pythonanywhere.com
   ```

## 🔒 Étape 5 : Sécurité et HTTPS

### 5.1 Activer HTTPS

1. Dans l'onglet **"Web"**
2. Section **"Security"**
3. Activer **"Force HTTPS"**

### 5.2 Vérifier les Paramètres CSP

Les paramètres Content Security Policy sont déjà configurés dans `settings.py`.

Si vous rencontrez des avertissements CSP, utilisez le script de correction :

```bash
cd ~/ETRAGC_SARLU/gestionrh
python fix_csp.py
```

## 🔄 Étape 6 : Démarrage et Tests

### 6.1 Recharger l'Application

Dans l'onglet **"Web"**, cliquer sur le bouton **"Reload"** (vert).

### 6.2 Vérifier les Logs

En cas d'erreur, consulter les logs :
- **Error log** : Erreurs Python/Django
- **Server log** : Erreurs du serveur web
- **Access log** : Requêtes HTTP

### 6.3 Tester l'Application

1. Accéder à votre site : `https://www.guineerh.space` ou `https://ETRAGCSARLU.pythonanywhere.com`
2. Tester la page de connexion
3. Se connecter avec le superutilisateur
4. Vérifier toutes les fonctionnalités

## 📊 Étape 7 : Données Initiales (Optionnel)

### 7.1 Créer des Données de Test

```bash
cd ~/ETRAGC_SARLU/gestionrh
python manage.py shell < create_test_data.py
```

### 7.2 Importer des Données Existantes

Si vous avez un fichier de données :

```bash
python manage.py loaddata data.json
```

## 🔧 Maintenance et Mises à Jour

### Mettre à Jour le Code

```bash
cd ~/ETRAGC_SARLU/gestionrh
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
export $(cat .env | xargs)
python manage.py migrate
python manage.py collectstatic --noinput
```

Puis **Reload** dans l'onglet Web.

### Sauvegarder la Base de Données

```bash
# Exporter les données
python manage.py dumpdata --natural-foreign --natural-primary \
  -e contenttypes -e auth.Permission --indent 4 > backup_$(date +%Y%m%d).json

# Télécharger le fichier de sauvegarde
# Via l'interface Files de PythonAnywhere
```

## 🐛 Dépannage

### Erreur 500 - Internal Server Error

1. Vérifier les logs d'erreur
2. Vérifier que `DEBUG=False` dans `.env`
3. Vérifier que `ALLOWED_HOSTS` contient votre domaine
4. Vérifier les permissions des dossiers

### Erreur de Base de Données

1. Vérifier les informations dans `.env`
2. Tester la connexion MySQL :
   ```bash
   mysql -h ETRAGCSARLU.mysql.pythonanywhere-services.com \
         -u ETRAGCSARLU -p ETRAGCSARLU\$guineerh_db
   ```

### Fichiers Statiques Non Chargés

1. Vérifier la configuration dans l'onglet Web
2. Re-collecter les fichiers statiques :
   ```bash
   python manage.py collectstatic --clear --noinput
   ```

### Avertissements CSP

Exécuter le script de correction :
```bash
python fix_csp.py
```

## ✅ Checklist Post-Déploiement

- [ ] Application accessible via HTTPS
- [ ] Page de connexion fonctionne
- [ ] Fichiers statiques chargés (CSS, JS, images)
- [ ] Base de données connectée
- [ ] Superutilisateur créé
- [ ] Aucune erreur dans les logs
- [ ] Toutes les pages principales testées
- [ ] Upload de fichiers fonctionne
- [ ] Génération de PDF fonctionne
- [ ] Emails de test envoyés (si configuré)

## 📚 Ressources

- [Documentation PythonAnywhere](https://help.pythonanywhere.com/)
- [Documentation Django](https://docs.djangoproject.com/)
- [Guide MySQL](./MYSQL_SETUP.md)
- [Configuration Base de Données](./DATABASE_CONFIGURATION.md)

## 🎉 Félicitations !

Votre application Gestionnaire RH Guinée est maintenant déployée et opérationnelle !

**URL de Production** : https://www.guineerh.space

---

**Version** : 1.0.0  
**Date** : 26 Octobre 2025  
**Statut** : ✅ Prêt pour la Production
