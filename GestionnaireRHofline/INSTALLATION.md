# 📋 Guide d'Installation - Gestionnaire RH Guinée

## Prérequis

- **Windows 7/8/10/11**
- **Python 3.10+** (télécharger sur https://www.python.org/downloads/)
  - ⚠️ **IMPORTANT**: Cochez "Add Python to PATH" lors de l'installation!

---

## 🚀 Installation Rapide (Recommandée)

1. **Copiez le dossier** `GestionnaireRHofline` sur l'ordinateur cible

2. **Double-cliquez sur** `install.bat`
   - L'installation se fait automatiquement
   - Créez votre compte administrateur quand demandé

3. **C'est terminé!**

---

## ▶️ Lancement de l'Application

1. **Double-cliquez sur** `start.bat`
2. Le navigateur s'ouvre automatiquement sur `http://127.0.0.1:8000/`
3. Connectez-vous avec votre compte administrateur

---

## 🔧 Installation Manuelle (Si besoin)

Ouvrez PowerShell ou CMD dans le dossier du projet et exécutez:

```powershell
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\activate

# Installer les dépendances
pip install Django==5.2.11 python-decouple pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks django-filter djangorestframework reportlab openpyxl django-import-export django-axes django-cors-headers django-celery-beat whitenoise django-csp requests python-dateutil

# Configurer la base de données
python manage.py migrate

# Créer un administrateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

---

## 📄 Fonctionnalités Principales

- ✅ **Gestion des employés** - Fiches, contrats, documents
- ✅ **Paie** - Calcul automatique selon législation guinéenne (CNSS, RTS, etc.)
- ✅ **Génération PDF** - Bulletins de paie, attestations, rapports
- ✅ **Temps de travail** - Présences, absences, heures supplémentaires
- ✅ **Congés** - Demandes, validation, soldes
- ✅ **Formation** - Catalogue, inscriptions, suivi
- ✅ **Recrutement** - Offres, candidatures, processus
- ✅ **Comptabilité** - Écritures, journaux, déclarations

---

## 🔒 Mode Offline

Ce système fonctionne **100% hors ligne**:
- Base de données SQLite locale
- Pas besoin d'internet
- Toutes les données restent sur votre ordinateur

---

## ❓ Problèmes Courants

### "Python n'est pas reconnu"
→ Réinstallez Python en cochant "Add Python to PATH"

### "Le port 8000 est déjà utilisé"
→ Fermez l'autre application ou utilisez:
```
python manage.py runserver 8080
```

### "Erreur de migration"
→ Supprimez `db.sqlite3` et relancez `install.bat`

---

## 📞 Support

Pour toute question, contactez l'administrateur système.

---

*Gestionnaire RH Guinée - Version Offline*
