# ✅ CHECKLIST DE VÉRIFICATION PRÉ-DÉMARRAGE

## 🎯 Objectif
Vérifier que tout est correctement configuré avant de lancer l'application.

---

## 📋 CHECKLIST COMPLÈTE

### 1️⃣ ENVIRONNEMENT SYSTÈME

#### Python
```powershell
python --version
```
✅ **Attendu** : Python 3.10.0 ou supérieur  
❌ **Si erreur** : Installer Python depuis https://www.python.org/

#### PostgreSQL
```powershell
psql --version
```
✅ **Attendu** : PostgreSQL 14.0 ou supérieur  
❌ **Si erreur** : Installer PostgreSQL depuis https://www.postgresql.org/

#### Git (optionnel)
```powershell
git --version
```
✅ **Attendu** : git version 2.x.x  
⚠️ **Si erreur** : Optionnel, mais recommandé

---

### 2️⃣ STRUCTURE DU PROJET

#### Vérifier la présence des dossiers principaux
```
GestionnaireRH/
├── ✅ core/
├── ✅ dashboard/
├── ✅ employes/
├── ✅ paie/
├── ✅ temps_travail/
├── ✅ formation/
├── ✅ recrutement/
├── ✅ database/
├── ✅ templates/
├── ✅ static/
├── ✅ media/
├── ✅ docs/
└── ✅ gestionnaire_rh/
```

#### Vérifier les fichiers de configuration
- ✅ `requirements.txt` (19 lignes)
- ✅ `manage.py`
- ✅ `gestionnaire_rh/settings.py`
- ✅ `gestionnaire_rh/urls.py`
- ✅ `.env` (à créer si absent)

---

### 3️⃣ ENVIRONNEMENT VIRTUEL

#### Créer l'environnement virtuel (si pas fait)
```powershell
python -m venv venv
```

#### Activer l'environnement virtuel
```powershell
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

✅ **Vérification** : Vous devriez voir `(venv)` au début de la ligne de commande

#### Vérifier que l'environnement est actif
```powershell
where python
# Devrait pointer vers GestionnaireRH\venv\Scripts\python.exe
```

---

### 4️⃣ DÉPENDANCES PYTHON

#### Installer les dépendances
```powershell
pip install -r requirements.txt
```

#### Vérifier l'installation
```powershell
pip list
```

✅ **Packages attendus** :
- Django==4.2.7
- psycopg2-binary==2.9.9
- Pillow==10.1.0
- django-crispy-forms==2.1
- crispy-bootstrap5==1.0.0
- django-filter==23.5
- reportlab==4.0.7
- openpyxl==3.1.2
- python-dateutil==2.8.2
- django-widget-tweaks==1.5.0
- django-import-export==3.3.5
- celery==5.3.4
- redis==5.0.1
- django-celery-beat==2.5.0
- django-cors-headers==4.3.1
- djangorestframework==3.14.0
- python-decouple==3.8
- gunicorn==21.2.0
- whitenoise==6.6.0

---

### 5️⃣ BASE DE DONNÉES POSTGRESQL

#### Vérifier que PostgreSQL est démarré
```powershell
# Windows
# Services > PostgreSQL > État : Démarré

# Linux
sudo systemctl status postgresql
```

#### Vérifier la connexion PostgreSQL
```powershell
psql -U postgres -c "SELECT version();"
```

✅ **Attendu** : Affiche la version de PostgreSQL  
❌ **Si erreur** : Vérifier que PostgreSQL est démarré

#### Vérifier que la base de données existe
```powershell
psql -U postgres -c "\l" | findstr gestionnaire_rh_guinee
```

✅ **Attendu** : Affiche la base `gestionnaire_rh_guinee`  
❌ **Si absent** : Exécuter `database\install_database.bat`

#### Vérifier les tables
```powershell
psql -U postgres -d gestionnaire_rh_guinee -c "\dt"
```

✅ **Attendu** : Liste de 57 tables  
❌ **Si vide** : Exécuter les scripts SQL

---

### 6️⃣ FICHIER .env

#### Vérifier la présence du fichier .env
```powershell
Test-Path .env
```

✅ **True** : Fichier existe  
❌ **False** : Créer le fichier

#### Contenu minimum requis du .env
```env
# Django
SECRET_KEY=votre-cle-secrete-changez-moi-en-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données
DB_NAME=gestionnaire_rh_guinee
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
```

#### Vérifier les variables
```powershell
# Afficher le contenu (sans les mots de passe)
Get-Content .env | Select-String -Pattern "SECRET_KEY|DB_NAME|DB_USER|DB_HOST"
```

---

### 7️⃣ MIGRATIONS DJANGO

#### Vérifier les migrations
```powershell
python manage.py showmigrations
```

✅ **Attendu** : Liste des migrations avec [X] (appliquées)  
❌ **Si [ ]** : Migrations non appliquées

#### Créer les migrations (si nécessaire)
```powershell
python manage.py makemigrations
```

#### Appliquer les migrations
```powershell
python manage.py migrate
```

✅ **Attendu** : "Applying migrations... OK"

---

### 8️⃣ SUPERUTILISATEUR

#### Vérifier si un superutilisateur existe
```powershell
python manage.py shell
```

Puis dans le shell Python :
```python
from core.models import Utilisateur
print(Utilisateur.objects.filter(is_superuser=True).count())
exit()
```

✅ **> 0** : Au moins un superutilisateur existe  
❌ **0** : Créer un superutilisateur

#### Créer un superutilisateur
```powershell
python manage.py createsuperuser
```

Remplir :
- Username: `admin`
- Email: `admin@example.com`
- Password: `********` (minimum 8 caractères)

---

### 9️⃣ FICHIERS STATIQUES

#### Vérifier le dossier static
```powershell
Test-Path static\css\custom.css
```

✅ **True** : Fichier CSS existe

#### Collecter les fichiers statiques
```powershell
python manage.py collectstatic --noinput
```

✅ **Attendu** : "X static files copied to 'staticfiles'"

#### Vérifier le dossier staticfiles
```powershell
Test-Path staticfiles
```

✅ **True** : Dossier créé

---

### 🔟 VÉRIFICATION FINALE

#### Vérifier la configuration Django
```powershell
python manage.py check
```

✅ **Attendu** : "System check identified no issues (0 silenced)."  
❌ **Si erreurs** : Corriger les problèmes signalés

#### Vérifier les URLs
```powershell
python manage.py show_urls 2>$null
```

✅ **Attendu** : Liste des URLs configurées  
⚠️ **Si erreur "Unknown command"** : Normal, commande optionnelle

---

## 🚀 LANCEMENT DE L'APPLICATION

### Démarrer le serveur
```powershell
python manage.py runserver
```

✅ **Attendu** :
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Accéder à l'application
1. Ouvrir le navigateur
2. Aller sur : http://localhost:8000
3. Vous devriez voir la page de connexion

### Tester la connexion
- Username: `admin`
- Password: (celui créé à l'étape 8)

✅ **Succès** : Redirection vers le dashboard  
❌ **Échec** : Vérifier les credentials

---

## 🧪 TESTS DE FONCTIONNALITÉS

### Test 1 : Dashboard
- ✅ Affichage des statistiques
- ✅ Graphique visible
- ✅ Pas d'erreur JavaScript (F12)

### Test 2 : Menu latéral
- ✅ Tous les liens visibles
- ✅ Clic sur "Employés" fonctionne

### Test 3 : Module Employés
- ✅ Liste des employés s'affiche
- ✅ Bouton "Nouvel employé" visible
- ✅ Formulaire de recherche fonctionne

### Test 4 : Création employé
- ✅ Formulaire s'affiche (5 onglets)
- ✅ Tous les champs visibles
- ✅ Validation fonctionne

### Test 5 : Profil utilisateur
- ✅ Clic sur nom utilisateur en haut
- ✅ "Mon profil" accessible
- ✅ Informations affichées

---

## 🐛 DÉPANNAGE

### Problème : "Module not found"
```powershell
pip install -r requirements.txt --upgrade
```

### Problème : "Connection refused" (PostgreSQL)
1. Vérifier que PostgreSQL est démarré
2. Vérifier les paramètres dans .env
3. Tester la connexion : `psql -U postgres`

### Problème : "No such table"
```powershell
python manage.py migrate
```

### Problème : "Static files not found"
```powershell
python manage.py collectstatic --clear --noinput
```

### Problème : "Port already in use"
```powershell
# Utiliser un autre port
python manage.py runserver 8080
```

### Problème : "CSRF verification failed"
1. Vider le cache du navigateur
2. Vérifier que DEBUG=True dans .env
3. Redémarrer le serveur

---

## 📊 RÉSUMÉ DE VÉRIFICATION

### Checklist rapide
- [ ] Python 3.10+ installé
- [ ] PostgreSQL 14+ installé et démarré
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (19 packages)
- [ ] Base de données créée (57 tables)
- [ ] Fichier .env configuré
- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Fichiers statiques collectés
- [ ] `python manage.py check` OK
- [ ] Serveur démarre sans erreur
- [ ] Page de connexion accessible
- [ ] Connexion réussie
- [ ] Dashboard s'affiche
- [ ] Module Employés fonctionne

### Score de préparation
- **15/15** : ✅ Prêt à démarrer !
- **12-14/15** : ⚠️ Quelques ajustements nécessaires
- **< 12/15** : ❌ Vérifier la configuration

---

## 🎯 PROCHAINES ÉTAPES

Une fois toutes les vérifications passées :

1. ✅ **Configurer la société**
   - Paramètres > Société
   - Remplir les informations

2. ✅ **Créer les structures**
   - Établissements
   - Services
   - Postes

3. ✅ **Ajouter des employés**
   - Employés > Nouvel employé
   - Remplir le formulaire

4. ✅ **Explorer les fonctionnalités**
   - Recherche
   - Filtres
   - Export Excel
   - Profil utilisateur

---

## 📞 SUPPORT

Si vous rencontrez des problèmes :

1. **Consulter la documentation**
   - DEMARRAGE_RAPIDE.txt
   - QUICK_START_COMMANDS.md
   - GUIDE_INSTALLATION.md

2. **Vérifier les logs**
   - Console du serveur Django
   - Logs PostgreSQL

3. **Contacter le support**
   - Email : dev@votre-entreprise.com
   - Téléphone : +224 XXX XXX XXX

---

## ✅ VALIDATION FINALE

Si toutes les vérifications sont passées, vous êtes prêt à utiliser l'application !

**🎉 Félicitations ! L'application est correctement configurée et prête à l'emploi !**

---

*Dernière mise à jour : 19 octobre 2025 - 23h00*  
*Version : 1.0*
