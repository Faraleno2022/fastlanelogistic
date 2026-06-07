# 🇬🇳 Gestionnaire RH Guinée

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-40%25%20Complete-orange.svg)](STATUS_ACTUEL.txt) conçu spécifiquement pour les entreprises en Guinée, conforme au Code du Travail guinéen et aux réglementations locales (CNSS, IRG, INAM).

---

## 📋 Table des Matières

- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Installation Rapide](#-installation-rapide)
- [Structure du Projet](#-structure-du-projet)
- [Documentation](#-documentation)
- [Captures d'Écran](#-captures-décran)
- [Conformité Légale](#-conformité-légale)
- [Support](#-support)
- [Licence](#-licence)

---

## ✨ Fonctionnalités

### 👥 Gestion des Employés
- ✅ Dossier complet employé (état civil, contact, documents)
- ✅ Gestion des contrats (CDI, CDD, Stage)
- ✅ Historique de carrière (promotions, mutations)
- ✅ Organigramme hiérarchique
- ✅ Génération automatique de matricules

### 💰 Module Paie
- ✅ Calcul automatique des bulletins de paie
- ✅ Conformité CNSS (5% employé, 18% employeur)
- ✅ Calcul IRG selon barème progressif guinéen
- ✅ Cotisation INAM (2,5%)
- ✅ Gestion des primes et indemnités
- ✅ Heures supplémentaires (40%, 60%, 100%)
- ✅ Livre de paie mensuel
- ✅ Cumuls annuels

### ⏰ Temps de Travail
- ✅ Pointages quotidiens
- ✅ Gestion des horaires flexibles
- ✅ Calcul automatique des heures supplémentaires
- ✅ Gestion des congés (26 jours/an)
- ✅ Suivi des absences
- ✅ Arrêts de travail
- ✅ Calendrier des jours fériés guinéens

### 💳 Prêts et Acomptes
- ✅ Demandes d'acomptes
- ✅ Gestion des prêts avec échéanciers
- ✅ Remboursement automatique sur paie
- ✅ Suivi des soldes

### 🎓 Recrutement
- ✅ Publication d'offres d'emploi
- ✅ Gestion des candidatures
- ✅ Planification des entretiens
- ✅ Évaluation des candidats
- ✅ Processus d'embauche

### 📚 Formation et Carrière
- ✅ Suivi des formations
- ✅ Plan de développement
- ✅ Évaluations annuelles
- ✅ Gestion des compétences

### 📊 Déclarations Sociales
- ✅ Déclaration CNSS mensuelle
- ✅ Déclaration IRG mensuelle
- ✅ Déclaration INAM
- ✅ Export XML/Excel pour dépôt

### 📈 Rapports et Statistiques
- ✅ Tableau de bord temps réel
- ✅ Indicateurs RH (effectif, turnover, absentéisme)
- ✅ Pyramide des âges
- ✅ Masse salariale
- ✅ Exports Excel/PDF

### 🔐 Sécurité et Audit
- ✅ Protection contre Force Brute (Django Axes + Defender)
- ✅ Protection CSRF et XSS
- ✅ Protection contre injections SQL
- ✅ Chiffrement des données sensibles (Cryptography)
- ✅ HTTPS et en-têtes de sécurité (HSTS, CSP)
- ✅ Validation stricte des fichiers uploadés
- ✅ Rate limiting et protection DDoS
- ✅ Gestion des utilisateurs et profils
- ✅ Droits d'accès granulaires
- ✅ Logs d'activité et de sécurité complets
- ✅ Historique des modifications
- ✅ Sauvegardes automatiques

---

## 🛠️ Technologies

### Backend
- **Python 3.10+**
- **Django 4.2** - Framework web
- **PostgreSQL 14+** - Base de données
- **Celery** - Tâches asynchrones
- **Redis** - Cache et broker

### Frontend
- **Bootstrap 5** - Framework CSS
- **jQuery** - JavaScript
- **Chart.js** - Graphiques
- **DataTables** - Tables interactives

### Bibliothèques Python
- **psycopg2** - Connecteur PostgreSQL
- **Pillow** - Traitement d'images
- **ReportLab** - Génération PDF
- **openpyxl** - Export Excel
- **django-crispy-forms** - Formulaires
- **django-filter** - Filtres
- **djangorestframework** - API REST

### Sécurité
- **django-axes** - Protection contre force brute
- **django-defender** - Protection supplémentaire
- **django-csp** - Content Security Policy
- **cryptography** - Chiffrement des données
- **bleach** - Sanitization HTML
- **django-ratelimit** - Limitation de requêtes

---

## 🚀 Installation Rapide

### Prérequis

- Python 3.10 ou supérieur
- PostgreSQL 14 ou supérieur
- Git (optionnel)

### Installation en 5 Minutes

```bash
# 1. Cloner le projet
git clone <url-du-depot>
cd GestionnaireRH

# 2. Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Installer la base de données
cd database
install_database.bat  # Windows
# ./install_database.sh  # Linux/Mac

# 5. Configurer Django
cd ..
copy .env.example .env
# Modifier .env avec vos paramètres

# 6. Initialiser Django
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# 7. Lancer le serveur
python manage.py runserver
```

Ouvrir le navigateur : **http://localhost:8000**

📖 **Guide d'installation détaillé** : [docs/GUIDE_INSTALLATION.md](docs/GUIDE_INSTALLATION.md)

---

## 📁 Structure du Projet

```
GestionnaireRH/
├── core/                      # Application principale
│   ├── management/           # Commandes Django personnalisées
│   ├── models.py            # Modèles de base
│   └── views.py             # Vues communes
│
├── employes/                 # Module Employés
│   ├── models.py            # Modèles employés
│   ├── views.py             # Vues CRUD
│   ├── forms.py             # Formulaires
│   └── templates/           # Templates HTML
│
├── paie/                     # Module Paie
│   ├── models.py            # Bulletins, rubriques
│   ├── calcul.py            # Moteur de calcul
│   ├── views.py             # Gestion paie
│   └── templates/           # Templates bulletins
│
├── temps_travail/            # Module Temps
│   ├── models.py            # Pointages, congés
│   ├── views.py             # Gestion temps
│   └── templates/           # Templates temps
│
├── recrutement/              # Module Recrutement
│   ├── models.py            # Offres, candidatures
│   ├── views.py             # Gestion recrutement
│   └── templates/           # Templates recrutement
│
├── formation/                # Module Formation
│   ├── models.py            # Formations, évaluations
│   ├── views.py             # Gestion formation
│   └── templates/           # Templates formation
│
├── dashboard/                # Tableau de bord
│   ├── views.py             # Statistiques
│   └── templates/           # Templates dashboard
│
├── database/                 # Scripts SQL
│   ├── schema_complete.sql  # Structure complète
│   ├── views_and_indexes.sql # Vues et index
│   ├── functions_procedures.sql # Fonctions PL/pgSQL
│   ├── data_init_guinee.sql # Données initiales
│   ├── install_database.bat # Installation auto
│   ├── backup_database.bat  # Sauvegarde
│   └── README.md            # Doc base de données
│
├── docs/                     # Documentation
│   ├── GUIDE_INSTALLATION.md # Guide installation
│   ├── GUIDE_UTILISATEUR.md  # Guide utilisateur
│   └── API.md               # Documentation API
│
├── static/                   # Fichiers statiques
│   ├── css/                 # Styles CSS
│   ├── js/                  # Scripts JavaScript
│   └── img/                 # Images
│
├── media/                    # Fichiers uploadés
│   ├── photos/              # Photos employés
│   ├── documents/           # Documents
│   └── bulletins/           # Bulletins PDF
│
├── gestionnaire_rh/          # Configuration Django
│   ├── settings.py          # Paramètres
│   ├── urls.py              # URLs principales
│   └── wsgi.py              # WSGI
│
├── requirements.txt          # Dépendances Python
├── .env.example             # Exemple configuration
├── manage.py                # CLI Django
└── README.md                # Ce fichier
```

---

## 📚 Documentation

### Guides Complets

- 📖 [Guide d'Installation](docs/GUIDE_INSTALLATION.md) - Installation pas à pas
- 👤 [Guide Utilisateur](docs/GUIDE_UTILISATEUR.md) - Manuel d'utilisation complet
- 🗄️ [Documentation Base de Données](database/README.md) - Structure et fonctions SQL
- 🔌 [Documentation API](docs/API.md) - API REST (à venir)

### Documentation Sécurité

- 🔒 [README Sécurité](README_SECURITE.md) - Guide rapide de sécurité
- 🛡️ [Guide Sécurité Complet](SECURITY.md) - Documentation complète
- 📦 [Installation Sécurité](INSTALLATION_SECURITE.md) - Configuration sécurisée
- 🚀 [Déploiement Sécurisé](DEPLOIEMENT_SECURISE.md) - Guide de déploiement
- 📋 [Protections Implémentées](PROTECTIONS_IMPLEMENTEES.md) - Liste des protections

### Ressources

- [Code du Travail de Guinée](https://www.ilo.org/dyn/natlex/natlex4.detail?p_lang=fr&p_isn=103146)
- [CNSS Guinée](http://www.cnss-guinee.org/)
- [Direction Générale des Impôts](https://dgi.gov.gn/)
- [INAM](http://www.inam.gov.gn/)

---

## 🖼️ Captures d'Écran

### Tableau de Bord
![Dashboard](docs/screenshots/dashboard.png)

### Fiche Employé
![Employé](docs/screenshots/employe.png)

### Bulletin de Paie
![Bulletin](docs/screenshots/bulletin.png)

### Livre de Paie
![Livre Paie](docs/screenshots/livre_paie.png)

---

## ⚖️ Conformité Légale

### Code du Travail Guinéen

Le système respecte intégralement le Code du Travail de Guinée (Loi L/2014/072/CNT) :

- ✅ Durée légale : 40 heures/semaine (173,33 h/mois)
- ✅ Congés annuels : 26 jours ouvrables
- ✅ Heures supplémentaires : Majorations conformes
- ✅ Période d'essai : Selon catégories
- ✅ Préavis de démission/licenciement
- ✅ Indemnités de licenciement

### Cotisations Sociales 2025

#### CNSS (Caisse Nationale de Sécurité Sociale)
- **Employé** : 5% (plafonné à 3 000 000 GNF)
- **Employeur** : 18% (plafonné à 3 000 000 GNF)

#### INAM (Institut National d'Assurance Maladie)
- **Taux** : 2,5% (plafonné à 3 000 000 GNF)

#### IRG (Impôt sur le Revenu)

Barème progressif 2025 :

| Tranche | Borne Inférieure | Borne Supérieure | Taux |
|---------|------------------|------------------|------|
| 1 | 0 GNF | 1 000 000 GNF | 0% |
| 2 | 1 000 001 GNF | 3 000 000 GNF | 5% |
| 3 | 3 000 001 GNF | 6 000 000 GNF | 10% |
| 4 | 6 000 001 GNF | 12 000 000 GNF | 15% |
| 5 | 12 000 001 GNF | 25 000 000 GNF | 20% |
| 6 | > 25 000 000 GNF | - | 25% |

**Abattement** : 20% (plafonné à 300 000 GNF)

### SMIG 2025
- **Salaire Minimum** : 440 000 GNF/mois

---

## 🔄 Mises à Jour

### Version 1.0 (Octobre 2025)
- ✅ Gestion complète des employés
- ✅ Module paie avec calculs conformes
- ✅ Temps de travail et congés
- ✅ Prêts et acomptes
- ✅ Recrutement
- ✅ Formation et carrière
- ✅ Déclarations sociales
- ✅ Rapports et statistiques

### Prochaines Fonctionnalités (v1.1)
- 🔜 Portail employé (self-service)
- 🔜 Application mobile
- 🔜 Signature électronique
- 🔜 Intégration bancaire
- 🔜 Gestion documentaire avancée
- 🔜 BI et analytics avancés

---

## 🤝 Contribution

Ce projet est propriétaire. Pour toute contribution ou suggestion :

1. Créer une issue détaillée
2. Proposer une pull request
3. Contacter l'équipe de développement

### Standards de Code

- **Python** : PEP 8
- **Django** : Best practices Django
- **SQL** : PostgreSQL conventions
- **Git** : Conventional Commits

---

## 🆘 Support

### Assistance Technique

- **Email** : support@votre-entreprise.com
- **Téléphone** : +224 XXX XXX XXX
- **Documentation** : http://docs.votre-entreprise.com
- **Issues** : GitHub Issues (si applicable)

### Heures de Support

- Lundi - Vendredi : 8h00 - 17h00 (GMT)
- Samedi : 9h00 - 13h00 (GMT)
- Urgences : 24/7

### Formation

Formation disponible pour :
- Administrateurs système
- Responsables RH
- Gestionnaires de paie
- Utilisateurs finaux

Contactez-nous pour un devis personnalisé.

---

## 🔒 Sécurité

### Protections Implémentées

Le système intègre des protections de sécurité de niveau entreprise :

| Protection | Technologie | Status |
|------------|-------------|--------|
| **Force Brute** | Django Axes + Defender | ✅ Actif |
| **SQL Injection** | Middleware + ORM | ✅ Actif |
| **XSS** | Middleware + Bleach | ✅ Actif |
| **CSRF** | Django + Cookies sécurisés | ✅ Actif |
| **Clickjacking** | X-Frame-Options | ✅ Actif |
| **DDoS** | Rate Limiting | ✅ Actif |
| **HTTPS** | HSTS + SSL | ✅ Actif |
| **Chiffrement** | Cryptography (Fernet) | ✅ Actif |

**Score de Sécurité : 🔒🔒🔒🔒🔒 (5/5)**

### Signaler une Vulnérabilité

Si vous découvrez une faille de sécurité, **NE PAS** créer d'issue publique.

Contactez directement : security@votre-entreprise.com

### Configuration Rapide

```bash
# 1. Installer les packages de sécurité
pip install -r requirements.txt

# 2. Générer les clés de sécurité
python generate_security_keys.py

# 3. Configurer .env avec les clés générées
cp .env.example .env

# 4. Vérifier la configuration
python check_security.py
python manage.py check --deploy
```

### Documentation Complète

Consultez [README_SECURITE.md](README_SECURITE.md) pour :
- Guide d'installation des protections
- Configuration HTTPS
- Monitoring et logs
- Bonnes pratiques

### Bonnes Pratiques

- ✅ Mots de passe forts obligatoires (8+ caractères, majuscules, chiffres, spéciaux)
- ✅ Blocage automatique après 5 tentatives échouées
- ✅ Chiffrement des données sensibles (Fernet)
- ✅ Sessions sécurisées (1h max, HTTPS uniquement)
- ✅ Sauvegardes quotidiennes automatiques chiffrées
- ✅ Logs d'audit et de sécurité complets
- ✅ Conformité RGPD/Protection des données
- ✅ Validation stricte de toutes les entrées utilisateur

---

## 📄 Licence

**Propriétaire** - Tous droits réservés

Ce logiciel est la propriété exclusive de [Votre Entreprise].
Toute reproduction, distribution ou utilisation non autorisée est strictement interdite.

Pour obtenir une licence d'utilisation, contactez : commercial@votre-entreprise.com

---

## 👥 Équipe

### Développement
- **Chef de Projet** : [Nom]
- **Développeur Backend** : [Nom]
- **Développeur Frontend** : [Nom]
- **DBA** : [Nom]

### Expertise RH
- **Consultant RH** : [Nom]
- **Expert Paie Guinée** : [Nom]
- **Juriste Droit du Travail** : [Nom]

---

## 🙏 Remerciements

- Ministère du Travail de Guinée
- CNSS Guinée
- Direction Générale des Impôts
- INAM
- Tous les utilisateurs beta-testeurs

---

## 📞 Contact

**Votre Entreprise**

- 🌐 Site web : https://www.votre-entreprise.com
- 📧 Email : contact@votre-entreprise.com
- 📱 Téléphone : +224 XXX XXX XXX
- 📍 Adresse : Conakry, Guinée

---

<div align="center">

**Fait avec ❤️ en Guinée 🇬🇳**

© 2025 Votre Entreprise. Tous droits réservés.

</div>
