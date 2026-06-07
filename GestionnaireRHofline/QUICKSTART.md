# ⚡ Démarrage Rapide - Gestionnaire RH Guinée

## 🚀 Installation en 10 Minutes

### ✅ Prérequis

Avant de commencer, assurez-vous d'avoir :
- ✅ **Python 3.10+** installé
- ✅ **PostgreSQL 14+** installé
- ✅ **Git** (optionnel)

---

## 📦 Étape 1 : Récupérer le Projet (1 min)

```bash
# Option A : Cloner depuis Git
git clone <url-du-depot>
cd GestionnaireRH

# Option B : Extraire l'archive ZIP
# Extraire dans C:\Users\LENO\Desktop\GestionnaireRH
cd GestionnaireRH
```

---

## 🐍 Étape 2 : Environnement Python (2 min)

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Activer (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

**Attendez l'installation des packages...**

---

## 🗄️ Étape 3 : Base de Données (3 min)

### Installation Automatique (Recommandée)

```bash
cd database
install_database.bat
```

Le script vous demandera :
1. **Mot de passe postgres** : Entrez votre mot de passe PostgreSQL
2. **Mot de passe rh_user** : Choisissez un mot de passe (ex: `RH2025!Secure`)

Le script va automatiquement :
- ✅ Créer la base `gestionnaire_rh`
- ✅ Créer l'utilisateur `rh_user`
- ✅ Créer 50+ tables
- ✅ Créer 12 vues
- ✅ Créer 20+ fonctions
- ✅ Insérer les données Guinée 2025
- ✅ Générer le fichier `.env`

---

## ⚙️ Étape 4 : Configuration Django (2 min)

```bash
# Retour à la racine
cd ..

# Vérifier le fichier .env (créé automatiquement)
# Ou copier manuellement si nécessaire
copy .env.example .env
```

**Modifier `.env` si nécessaire :**

```env
DB_NAME=gestionnaire_rh
DB_USER=rh_user
DB_PASSWORD=VotreMotDePasse
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=votre-cle-secrete-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Générer une clé secrète :**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copier la clé générée dans `SECRET_KEY` du fichier `.env`

---

## 🎨 Étape 5 : Initialiser Django (1 min)

```bash
# Migrations Django
python manage.py migrate

# Créer un super utilisateur
python manage.py createsuperuser
```

**Informations demandées :**
- **Login** : admin
- **Email** : admin@exemple.com
- **Nom** : Admin
- **Prénom** : Système
- **Mot de passe** : Choisissez un mot de passe fort

```bash
# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

---

## 🎉 Étape 6 : Lancer l'Application (1 min)

```bash
python manage.py runserver
```

**Ouvrir le navigateur :**

👉 **http://localhost:8000**

---

## 🔐 Première Connexion

1. Aller sur **http://localhost:8000/admin**
2. Se connecter avec :
   - **Login** : admin
   - **Mot de passe** : celui que vous avez créé

---

## 📋 Configuration Initiale

### 1. Créer la Société

1. **Admin** > **Configuration** > **Société** > **Ajouter**
2. Remplir :
   - Raison sociale : `Votre Entreprise SARL`
   - NIF : `123456789A`
   - Numéro CNSS employeur : `CNSS-2025-001`
   - Numéro INAM : `INAM-2025-001`
   - Adresse : `Conakry, Guinée`
   - Téléphone : `+224 XXX XXX XXX`
   - Email : `contact@votre-entreprise.com`
3. **Enregistrer**

### 2. Créer un Établissement

1. **Configuration** > **Établissements** > **Ajouter**
2. Remplir :
   - Code : `SIEGE`
   - Nom : `Siège Social`
   - Type : `Siège`
   - Ville : `Conakry`
3. **Enregistrer**

### 3. Créer des Services

1. **Organisation** > **Services** > **Ajouter**

Exemples :
- **Direction Générale** (DG)
- **Direction des Ressources Humaines** (DRH)
- **Direction Financière** (DF)
- **Direction Commerciale** (DC)
- **Direction Technique** (DT)

### 4. Créer des Postes

1. **Organisation** > **Postes** > **Ajouter**

Exemples :
- **Directeur Général** (Cadre, A1)
- **Responsable RH** (Cadre, B1)
- **Gestionnaire de Paie** (Agent de maîtrise, C1)
- **Assistant RH** (Employé, D1)

### 5. Créer un Employé Test

1. **Employés** > **Nouveau**
2. Remplir les informations minimales :
   - **État civil** : Nom, prénoms, date de naissance, sexe
   - **Identification** : Numéro CNSS
   - **Contact** : Téléphone, email
   - **Professionnel** : Service, poste, date d'embauche, type de contrat
   - **Bancaire** : Mode de paiement
3. **Enregistrer**

### 6. Définir le Salaire

1. Ouvrir la fiche employé
2. Onglet **Salaire** > **Nouvelle grille**
3. Remplir :
   - Date d'effet : Date du jour
   - Salaire de base : `2 000 000 GNF`
   - Prime de fonction : `500 000 GNF`
   - Indemnité de transport : `200 000 GNF`
4. **Enregistrer**

---

## 💰 Premier Calcul de Paie

### 1. Créer une Période de Paie

1. **Paie** > **Périodes** > **Nouvelle période**
2. Sélectionner :
   - Année : 2025
   - Mois : Octobre
3. **Créer**

### 2. Calculer les Bulletins

1. **Paie** > **Bulletins** > **Calculer**
2. Sélectionner la période : Octobre 2025
3. Sélectionner : **Tous les employés**
4. **Lancer le calcul**

Le système calcule automatiquement :
- ✅ Salaire brut
- ✅ CNSS employé (5%)
- ✅ INAM (2,5%)
- ✅ IRG (barème progressif)
- ✅ Net à payer
- ✅ CNSS employeur (18%)

### 3. Consulter le Bulletin

1. **Paie** > **Bulletins**
2. Cliquer sur le bulletin généré
3. Voir le détail complet
4. **Télécharger PDF**

---

## 📊 Explorer les Fonctionnalités

### Tableau de Bord
👉 **http://localhost:8000/dashboard**
- Effectif en temps réel
- Statistiques clés
- Graphiques

### Livre de Paie
👉 **Paie** > **Livre de paie**
- Vue mensuelle complète
- Export Excel/PDF

### Congés
👉 **Temps** > **Congés**
- Demander un congé
- Consulter les soldes
- Calendrier

### Rapports
👉 **Rapports**
- Effectif par service
- Masse salariale
- Taux d'absentéisme
- Pyramide des âges

---

## 🔧 Commandes Utiles

### Développement

```bash
# Lancer le serveur
python manage.py runserver

# Créer un super utilisateur
python manage.py createsuperuser

# Migrations
python manage.py makemigrations
python manage.py migrate

# Shell Django
python manage.py shell

# Tests
python manage.py test
```

### Base de Données

```bash
# Sauvegarde
cd database
backup_database.bat

# Restauration
restore_database.bat

# Connexion psql
psql -U rh_user -d gestionnaire_rh
```

### Production

```bash
# Collecter les statiques
python manage.py collectstatic

# Lancer avec Gunicorn
gunicorn gestionnaire_rh.wsgi:application --bind 0.0.0.0:8000
```

---

## 📚 Documentation Complète

- 📖 [README.md](README.md) - Vue d'ensemble
- 🔧 [GUIDE_INSTALLATION.md](docs/GUIDE_INSTALLATION.md) - Installation détaillée
- 👤 [GUIDE_UTILISATEUR.md](docs/GUIDE_UTILISATEUR.md) - Manuel utilisateur
- 🗄️ [database/README.md](database/README.md) - Documentation BDD
- 📊 [PROJET_RESUME.md](docs/PROJET_RESUME.md) - Résumé complet

---

## 🆘 Problèmes Courants

### Erreur : "psycopg2 not found"

```bash
pip install psycopg2-binary
```

### Erreur : "Connection refused" PostgreSQL

1. Vérifier que PostgreSQL est démarré
2. Vérifier le port dans `.env` (5432 par défaut)
3. Vérifier le mot de passe

### Erreur : "No module named 'django'"

```bash
# Activer l'environnement virtuel
venv\Scripts\activate

# Réinstaller
pip install -r requirements.txt
```

### Erreur : "Static files not found"

```bash
python manage.py collectstatic --noinput
```

### Port 8000 déjà utilisé

```bash
# Utiliser un autre port
python manage.py runserver 8080
```

---

## ✅ Checklist de Vérification

Après l'installation, vérifier :

- [ ] PostgreSQL fonctionne
- [ ] Base de données créée (gestionnaire_rh)
- [ ] Tables créées (50+)
- [ ] Données initiales insérées
- [ ] Environnement virtuel activé
- [ ] Dépendances Python installées
- [ ] Fichier .env configuré
- [ ] Migrations Django appliquées
- [ ] Super utilisateur créé
- [ ] Serveur démarre sans erreur
- [ ] Accès à http://localhost:8000
- [ ] Connexion admin fonctionne
- [ ] Société créée
- [ ] Établissement créé
- [ ] Employé test créé
- [ ] Bulletin de paie généré

---

## 🎯 Prochaines Étapes

1. ✅ **Configurer votre entreprise** (société, établissements)
2. ✅ **Créer la structure** (services, postes)
3. ✅ **Importer les employés** (ou saisie manuelle)
4. ✅ **Définir les salaires**
5. ✅ **Calculer la première paie**
6. ✅ **Former les utilisateurs**
7. ✅ **Mettre en production**

---

## 📞 Support

**Besoin d'aide ?**

- 📧 Email : support@votre-entreprise.com
- 📱 Téléphone : +224 XXX XXX XXX
- 📖 Documentation : http://docs.votre-entreprise.com
- 💬 Chat : Disponible dans l'application

---

## 🎉 Félicitations !

Vous avez installé avec succès le **Gestionnaire RH Guinée** !

Le système est maintenant prêt à gérer :
- 👥 Vos employés
- 💰 Votre paie
- ⏰ Les temps de travail
- 📊 Vos déclarations sociales
- 📈 Vos statistiques RH

**Bonne utilisation ! 🇬🇳**

---

<div align="center">

**Gestionnaire RH Guinée**  
Version 1.0 - Octobre 2025

Conforme au Code du Travail Guinéen  
CNSS | IRG | INAM

</div>
