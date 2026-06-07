# 🚀 COMMANDES RAPIDES - Démarrage Application

## 📋 PRÉREQUIS

✅ Python 3.10+ installé  
✅ PostgreSQL 14+ installé et démarré  
✅ Git installé (optionnel)

---

## 🔧 INSTALLATION INITIALE (Première fois uniquement)

### 1. Créer et activer l'environnement virtuel

```powershell
# Windows PowerShell
cd C:\Users\LENO\Desktop\GestionnaireRH
python -m venv venv
.\venv\Scripts\activate
```

```bash
# Linux/Mac
cd /path/to/GestionnaireRH
python3 -m venv venv
source venv/bin/activate
```

### 2. Installer les dépendances

```powershell
pip install -r requirements.txt
```

### 3. Créer la base de données PostgreSQL

```powershell
# Méthode 1 : Script automatique (recommandé)
cd database
.\install_database.bat

# Méthode 2 : Manuel
psql -U postgres
CREATE DATABASE gestionnaire_rh_guinee;
CREATE USER rh_admin WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE gestionnaire_rh_guinee TO rh_admin;
\q

# Exécuter les scripts SQL
psql -U postgres -d gestionnaire_rh_guinee -f schema_complete.sql
psql -U postgres -d gestionnaire_rh_guinee -f views_and_indexes.sql
psql -U postgres -d gestionnaire_rh_guinee -f functions_procedures.sql
psql -U postgres -d gestionnaire_rh_guinee -f data_init_guinee.sql
```

### 4. Créer le fichier .env

```powershell
# Créer le fichier .env à la racine du projet
New-Item .env -ItemType File
```

Contenu du fichier `.env` :
```env
# Django
SECRET_KEY=votre-cle-secrete-django-ici-changez-moi
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données
DB_NAME=gestionnaire_rh_guinee
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe_postgres
DB_HOST=localhost
DB_PORT=5432

# Email (optionnel)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Redis (optionnel pour Celery)
REDIS_URL=redis://localhost:6379/0

# Société
COMPANY_NAME=Votre Entreprise
COMPANY_NIF=123456789
COMPANY_CNSS=987654321
```

### 5. Appliquer les migrations Django

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un superutilisateur

```powershell
python manage.py createsuperuser
# Suivre les instructions :
# - Username: admin
# - Email: admin@example.com
# - Password: (votre mot de passe sécurisé)
```

### 7. Collecter les fichiers statiques

```powershell
python manage.py collectstatic --noinput
```

### 8. Initialiser les données de base (optionnel)

```powershell
python manage.py init_database
```

---

## 🚀 DÉMARRAGE QUOTIDIEN

### 1. Activer l'environnement virtuel

```powershell
# Windows
cd C:\Users\LENO\Desktop\GestionnaireRH
.\venv\Scripts\activate
```

### 2. Lancer le serveur de développement

```powershell
python manage.py runserver
```

### 3. Accéder à l'application

🌐 **Application** : http://localhost:8000  
🔐 **Connexion** : Utilisez le compte créé à l'étape 6  
👨‍💼 **Admin Django** : http://localhost:8000/admin

---

## 📝 COMMANDES UTILES

### Gestion de la base de données

```powershell
# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Voir l'état des migrations
python manage.py showmigrations

# Annuler une migration
python manage.py migrate nom_app numero_migration

# Réinitialiser la base de données (ATTENTION : perte de données)
python manage.py flush
```

### Gestion des utilisateurs

```powershell
# Créer un superutilisateur
python manage.py createsuperuser

# Changer le mot de passe d'un utilisateur
python manage.py changepassword username

# Shell Django interactif
python manage.py shell
```

### Gestion des fichiers statiques

```powershell
# Collecter les fichiers statiques
python manage.py collectstatic

# Collecter sans confirmation
python manage.py collectstatic --noinput

# Effacer les anciens fichiers
python manage.py collectstatic --clear --noinput
```

### Tests

```powershell
# Lancer tous les tests
python manage.py test

# Tester une app spécifique
python manage.py test employes

# Tester avec coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Données de test

```powershell
# Créer des fixtures (sauvegarder données)
python manage.py dumpdata employes.Employe --indent 2 > fixtures/employes.json

# Charger des fixtures
python manage.py loaddata fixtures/employes.json

# Initialiser les données Guinée
python manage.py init_database
```

### Base de données

```powershell
# Backup de la base de données
cd database
.\backup_database.bat

# Restaurer la base de données
.\restore_database.bat

# Accéder à la console PostgreSQL
psql -U postgres -d gestionnaire_rh_guinee
```

### Développement

```powershell
# Lancer le serveur sur un port différent
python manage.py runserver 8080

# Lancer le serveur accessible depuis le réseau
python manage.py runserver 0.0.0.0:8000

# Mode debug avec rechargement automatique
python manage.py runserver --noreload

# Vérifier les problèmes du projet
python manage.py check

# Voir les URLs configurées
python manage.py show_urls
```

### Celery (tâches asynchrones)

```powershell
# Lancer Celery worker
celery -A gestionnaire_rh worker -l info

# Lancer Celery beat (tâches planifiées)
celery -A gestionnaire_rh beat -l info

# Les deux en même temps
celery -A gestionnaire_rh worker -B -l info
```

---

## 🔍 DÉPANNAGE

### Problème : Module non trouvé

```powershell
# Réinstaller les dépendances
pip install -r requirements.txt --upgrade
```

### Problème : Erreur de connexion PostgreSQL

```powershell
# Vérifier que PostgreSQL est démarré
# Windows : Services > PostgreSQL
# Linux : sudo systemctl status postgresql

# Vérifier les paramètres dans .env
# DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
```

### Problème : Migrations en conflit

```powershell
# Voir les migrations
python manage.py showmigrations

# Réinitialiser les migrations d'une app
python manage.py migrate nom_app zero
python manage.py migrate nom_app
```

### Problème : Fichiers statiques non chargés

```powershell
# Recollecte des fichiers statiques
python manage.py collectstatic --clear --noinput

# Vérifier STATIC_ROOT dans settings.py
```

### Problème : Port déjà utilisé

```powershell
# Windows : Trouver le processus
netstat -ano | findstr :8000
taskkill /PID <numero_pid> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

---

## 📊 PREMIERS PAS DANS L'APPLICATION

### 1. Connexion
- Aller sur http://localhost:8000
- Utiliser le compte superutilisateur créé

### 2. Configuration initiale
- Aller dans **Paramètres** > **Société**
- Remplir les informations de votre entreprise
- Créer des **Établissements**
- Créer des **Services**
- Créer des **Postes**

### 3. Créer des profils utilisateurs
- Aller dans **Administration** > **Utilisateurs**
- Créer des profils (RH, Manager, Opérateur)
- Assigner les permissions

### 4. Ajouter des employés
- Aller dans **Employés** > **Nouvel employé**
- Remplir le formulaire (5 onglets)
- Le matricule sera généré automatiquement

### 5. Tester les fonctionnalités
- Rechercher un employé
- Modifier un employé
- Exporter en Excel
- Créer un contrat

---

## 🎯 WORKFLOW TYPIQUE

### Matin
```powershell
cd C:\Users\LENO\Desktop\GestionnaireRH
.\venv\Scripts\activate
python manage.py runserver
```

### Développement
```powershell
# Créer une nouvelle fonctionnalité
python manage.py startapp nouveau_module

# Créer des migrations après modification models.py
python manage.py makemigrations
python manage.py migrate

# Tester
python manage.py test nouveau_module
```

### Fin de journée
```powershell
# Backup de la base de données
cd database
.\backup_database.bat

# Commit Git (si utilisé)
git add .
git commit -m "Description des modifications"
git push
```

---

## 📞 SUPPORT

### Documentation
- 📖 README.md - Vue d'ensemble
- 📘 GUIDE_INSTALLATION.md - Installation détaillée
- 📗 GUIDE_UTILISATEUR.md - Manuel utilisateur
- 📙 DEVELOPPEMENT_SESSION_2.md - Dernières modifications

### Logs
- Logs Django : Console du serveur
- Logs PostgreSQL : C:\Program Files\PostgreSQL\14\data\log\

### Aide
- Django : https://docs.djangoproject.com/
- PostgreSQL : https://www.postgresql.org/docs/
- Bootstrap : https://getbootstrap.com/docs/

---

## ✅ CHECKLIST DÉMARRAGE

- [ ] Environnement virtuel activé
- [ ] Dépendances installées
- [ ] Base de données créée
- [ ] Fichier .env configuré
- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Fichiers statiques collectés
- [ ] Serveur démarré
- [ ] Application accessible sur http://localhost:8000
- [ ] Connexion réussie

---

**🎉 Vous êtes prêt à utiliser l'application !**

Pour toute question : dev@votre-entreprise.com
