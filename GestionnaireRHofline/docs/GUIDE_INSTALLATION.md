# Guide d'Installation - Gestionnaire RH Guinée

## 📋 Prérequis

### Logiciels Requis

1. **Python 3.10+**
   - Télécharger depuis [python.org](https://www.python.org/downloads/)
   - Cocher "Add Python to PATH" lors de l'installation

2. **PostgreSQL 14+**
   - Télécharger depuis [postgresql.org](https://www.postgresql.org/download/)
   - Noter le mot de passe de l'utilisateur `postgres`

3. **Git** (optionnel)
   - Pour cloner le projet depuis un dépôt

### Configuration Système Minimale

- **RAM** : 4 GB minimum, 8 GB recommandé
- **Disque** : 2 GB d'espace libre
- **OS** : Windows 10/11, Linux, macOS

---

## 🚀 Installation Rapide

### Étape 1 : Récupérer le Projet

```bash
# Si vous avez Git
git clone <url-du-depot>
cd GestionnaireRH

# Sinon, extraire l'archive ZIP dans un dossier
```

### Étape 2 : Créer l'Environnement Virtuel Python

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate

# Sur Linux/Mac:
source venv/bin/activate
```

### Étape 3 : Installer les Dépendances Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 4 : Installer la Base de Données

#### Option A : Installation Automatique (Windows)

```bash
cd database
install_database.bat
```

Le script vous demandera :
- Le mot de passe de l'utilisateur `postgres`
- Un mot de passe pour le nouvel utilisateur `rh_user`

#### Option B : Installation Manuelle

1. **Créer la base de données**

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Dans psql:
CREATE DATABASE gestionnaire_rh;
CREATE USER rh_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE gestionnaire_rh TO rh_user;
\q
```

2. **Exécuter les scripts SQL**

```bash
cd database

# Créer les tables
psql -U rh_user -d gestionnaire_rh -f schema_complete.sql

# Créer les vues et index
psql -U rh_user -d gestionnaire_rh -f views_and_indexes.sql

# Créer les fonctions
psql -U rh_user -d gestionnaire_rh -f functions_procedures.sql

# Insérer les données initiales
psql -U rh_user -d gestionnaire_rh -f data_init_guinee.sql
```

### Étape 5 : Configurer Django

1. **Copier le fichier d'environnement**

```bash
# À la racine du projet
copy .env.example .env
```

2. **Modifier le fichier `.env`**

```env
# Base de données
DB_NAME=gestionnaire_rh
DB_USER=rh_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (optionnel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre.email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_app
```

3. **Générer une clé secrète Django**

```python
# Dans un terminal Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copier la clé générée dans `SECRET_KEY` du fichier `.env`

### Étape 6 : Initialiser Django

```bash
# Retour à la racine du projet
cd ..

# Appliquer les migrations Django
python manage.py migrate

# Créer un super utilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

### Étape 7 : Lancer le Serveur

```bash
python manage.py runserver
```

Ouvrir le navigateur à l'adresse : **http://localhost:8000**

---

## 🔧 Configuration Avancée

### Configuration de Production

1. **Modifier `.env` pour la production**

```env
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
SECRET_KEY=une-cle-tres-securisee
```

2. **Utiliser Gunicorn**

```bash
pip install gunicorn
gunicorn gestionnaire_rh.wsgi:application --bind 0.0.0.0:8000
```

3. **Configurer Nginx (Linux)**

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /chemin/vers/GestionnaireRH/staticfiles/;
    }

    location /media/ {
        alias /chemin/vers/GestionnaireRH/media/;
    }
}
```

### Configuration Email

Pour activer l'envoi d'emails (notifications, réinitialisation de mot de passe) :

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre.email@gmail.com
EMAIL_HOST_PASSWORD=mot_de_passe_application
DEFAULT_FROM_EMAIL=noreply@votre-domaine.com
```

**Note Gmail** : Créer un "Mot de passe d'application" dans les paramètres de sécurité Google.

### Configuration Celery (Tâches Asynchrones)

1. **Installer Redis**

```bash
# Windows: Télécharger depuis https://github.com/microsoftarchive/redis/releases
# Linux:
sudo apt-get install redis-server
```

2. **Démarrer Celery**

```bash
# Worker
celery -A gestionnaire_rh worker -l info

# Beat (tâches planifiées)
celery -A gestionnaire_rh beat -l info
```

---

## 📊 Initialisation des Données

### Données de Base (Déjà Incluses)

Le script `data_init_guinee.sql` contient :
- ✅ Profils utilisateurs (Admin, RH, Manager, etc.)
- ✅ Paramètres de paie Guinée (SMIG, CNSS, IRG, INAM)
- ✅ Tranches IRG 2025
- ✅ Jours fériés 2025
- ✅ Rubriques de paie standard
- ✅ Types de prêts, départs, sanctions
- ✅ Horaires de travail
- ✅ Indicateurs RH

### Ajouter des Données de Test

```bash
python manage.py init_database
```

Cette commande initialise également les données via Django.

### Créer une Société

1. Se connecter à l'admin : http://localhost:8000/admin
2. Aller dans **Configuration** > **Société**
3. Remplir les informations :
   - Raison sociale
   - NIF (Numéro d'Identification Fiscale)
   - Numéro CNSS employeur
   - Numéro INAM
   - Adresse complète

### Créer des Établissements

1. **Configuration** > **Établissements**
2. Créer au moins un établissement (Siège social)

### Créer des Services

1. **Organisation** > **Services**
2. Créer la structure hiérarchique de l'entreprise

### Créer des Postes

1. **Organisation** > **Postes**
2. Définir les postes avec leurs catégories professionnelles

---

## 🔐 Sécurité

### Checklist de Sécurité

- [ ] Changer le `SECRET_KEY` par défaut
- [ ] Mettre `DEBUG=False` en production
- [ ] Configurer `ALLOWED_HOSTS` correctement
- [ ] Utiliser HTTPS (certificat SSL)
- [ ] Sauvegardes automatiques quotidiennes
- [ ] Mots de passe forts pour la base de données
- [ ] Restreindre l'accès à PostgreSQL (pg_hba.conf)
- [ ] Activer le pare-feu
- [ ] Mettre à jour régulièrement les dépendances

### Sauvegardes

#### Sauvegarde Manuelle

```bash
cd database
backup_database.bat
```

#### Sauvegarde Automatique (Windows Task Scheduler)

1. Ouvrir le Planificateur de tâches
2. Créer une tâche de base
3. Déclencheur : Quotidien à 2h00
4. Action : Démarrer un programme
5. Programme : `C:\chemin\vers\database\backup_database.bat`

#### Restauration

```bash
cd database
restore_database.bat
```

---

## 🐛 Dépannage

### Erreur : "psycopg2 not found"

```bash
pip install psycopg2-binary
```

### Erreur : "Connection refused" PostgreSQL

1. Vérifier que PostgreSQL est démarré
2. Vérifier le port (5432 par défaut)
3. Vérifier `pg_hba.conf` pour autoriser les connexions locales

### Erreur : "No module named 'django'"

```bash
# Vérifier que l'environnement virtuel est activé
venv\Scripts\activate

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur : "Static files not found"

```bash
python manage.py collectstatic --noinput
```

### Performances Lentes

1. Vérifier les index de la base de données
2. Activer le cache Django (Redis/Memcached)
3. Optimiser les requêtes (Django Debug Toolbar)

---

## 📞 Support

### Documentation

- **README.md** : Vue d'ensemble du projet
- **database/README.md** : Documentation de la base de données
- **docs/** : Documentation technique complète

### Logs

Les logs sont disponibles dans :
- Django : Console du serveur
- PostgreSQL : `C:\Program Files\PostgreSQL\14\data\log\`

### Contacts

Pour toute question ou problème :
- Email : support@votre-entreprise.com
- Documentation : http://docs.votre-entreprise.com

---

## ✅ Vérification de l'Installation

Après l'installation, vérifier que tout fonctionne :

1. ✅ Accès à l'interface admin : http://localhost:8000/admin
2. ✅ Connexion avec le super utilisateur
3. ✅ Création d'un employé de test
4. ✅ Génération d'un bulletin de paie
5. ✅ Consultation des rapports
6. ✅ Sauvegarde de la base de données

---

**Installation réussie ! 🎉**

Vous pouvez maintenant commencer à utiliser le Gestionnaire RH Guinée.
