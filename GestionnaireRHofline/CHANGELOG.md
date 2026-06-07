# Changelog - Gestionnaire RH Guinée

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versioning Sémantique](https://semver.org/lang/fr/).

---

## [1.0.0] - 2025-10-19

### 🎉 Version Initiale

#### Ajouté

##### Module Système et Sécurité
- Gestion des utilisateurs avec authentification
- Système de profils et droits d'accès granulaires
- Logs d'activité complets pour audit
- Historique des modifications

##### Module Configuration Entreprise
- Gestion des informations société (NIF, CNSS, INAM)
- Support multi-établissements
- Configuration des paramètres généraux

##### Module Organisation
- Structure hiérarchique des services
- Catalogue des postes avec classifications
- Organigramme dynamique

##### Module Employés
- Dossier complet employé (état civil, contact, documents)
- Gestion des contrats (CDI, CDD, Stage, Temporaire)
- Informations bancaires et Mobile Money
- Génération automatique de matricules
- Photos et documents scannés

##### Module Paie
- Calcul automatique des bulletins de paie
- Conformité CNSS (5% employé, 18% employeur)
- Calcul IRG selon barème progressif guinéen 2025
- Cotisation INAM (2,5%)
- Gestion des primes et indemnités
- Heures supplémentaires avec majorations (40%, 60%, 100%)
- Livre de paie mensuel
- Cumuls mensuels et annuels
- Export PDF des bulletins

##### Module Temps de Travail
- Pointages quotidiens avec validation
- Gestion des horaires flexibles (Normal, Équipe, Nuit)
- Calcul automatique des heures supplémentaires
- Gestion des congés (26 jours/an selon Code du Travail)
- Soldes de congés avec reports
- Suivi des absences
- Arrêts de travail
- Calendrier des jours fériés guinéens 2025

##### Module Prêts et Acomptes
- Demandes d'acomptes avec workflow d'approbation
- 6 types de prêts (Personnel, Scolaire, Logement, Santé, Urgence, Équipement)
- Échéanciers automatiques
- Remboursement automatique sur paie
- Suivi des soldes

##### Module Recrutement
- Publication d'offres d'emploi
- Gestion des candidatures avec CV et lettres
- Planification des entretiens (Téléphonique, Présentiel, Visio)
- Évaluation des candidats
- Processus d'embauche automatisé

##### Module Formation et Carrière
- Suivi des formations (Initiale, Continue, Certification)
- Historique de carrière (Promotions, Mutations, Reclassements)
- Évaluations annuelles
- Plan de développement

##### Module Départs
- 12 types de départ (Démission, Licenciement, Retraite, etc.)
- Calcul automatique des indemnités
- Solde de tout compte
- Génération de certificats de travail

##### Module Sanctions Disciplinaires
- 10 types de sanctions (Avertissement, Blâme, Mise à pied, etc.)
- Procédures de recours
- Impact sur paie et carrière

##### Module Déclarations Sociales
- Déclaration CNSS mensuelle
- Déclaration IRG mensuelle
- Déclaration INAM
- Export XML/Excel pour dépôt
- Suivi des dépôts

##### Module Rapports et Statistiques
- Tableau de bord temps réel
- 24 indicateurs RH prédéfinis
- Pyramide des âges
- Effectif par service/catégorie
- Masse salariale
- Taux d'absentéisme et turnover
- Exports Excel/PDF

##### Base de Données
- 50+ tables PostgreSQL
- 10+ vues optimisées
- 20+ fonctions PL/pgSQL
- 15+ procédures stockées
- Index de performance
- Triggers automatiques

##### Documentation
- README complet
- Guide d'installation détaillé
- Guide utilisateur (80+ pages)
- Documentation base de données
- Scripts d'installation automatisés
- Scripts de sauvegarde/restauration

##### Données Initiales Guinée
- Paramètres de paie 2025
- Tranches IRG 2025
- Jours fériés 2025
- Rubriques de paie standard
- Types de prêts, départs, sanctions
- Horaires de travail
- Indicateurs RH

#### Conformité Légale
- ✅ Code du Travail de Guinée (Loi L/2014/072/CNT)
- ✅ CNSS : Taux et plafonds conformes
- ✅ IRG : Barème progressif 2025
- ✅ INAM : Taux 2,5%
- ✅ SMIG : 440 000 GNF
- ✅ Congés : 26 jours/an
- ✅ Durée légale : 40h/semaine

#### Sécurité
- Authentification sécurisée
- Gestion des droits par profil
- Logs d'audit complets
- Historique des modifications
- Chiffrement des mots de passe
- Protection CSRF/XSS

---

## [À Venir] - Version 1.1

### Prévu

#### Portail Employé
- Consultation du bulletin de paie
- Demandes de congés en ligne
- Consultation du solde de congés
- Demandes d'acomptes/prêts
- Consultation des documents personnels
- Notifications push

#### Application Mobile
- Application Android/iOS
- Pointage mobile avec géolocalisation
- Notifications temps réel
- Consultation des informations RH

#### Signature Électronique
- Signature numérique des contrats
- Signature des bulletins de paie
- Certificats électroniques
- Validation multi-niveaux

#### Intégrations
- Intégration bancaire (virements automatiques)
- API REST complète
- Webhooks
- Export comptable (SAGE, CIEL)

#### Gestion Documentaire
- GED intégrée
- Versioning des documents
- Workflows de validation
- OCR pour numérisation

#### Analytics Avancés
- Tableaux de bord personnalisables
- Prédictions (turnover, absences)
- Analyse comparative
- Rapports interactifs

#### Améliorations
- Mode hors ligne
- Optimisation des performances
- Interface multilingue (Français, Anglais, Pular, Malinké)
- Thèmes personnalisables

---

## Notes de Version

### Version 1.0.0 - Fonctionnalités Principales

Cette première version majeure inclut tous les modules essentiels pour la gestion complète des ressources humaines d'une entreprise en Guinée :

1. **Gestion Employés** : Dossiers complets avec tous les documents
2. **Paie Conforme** : Calculs automatiques selon législation guinéenne
3. **Temps de Travail** : Pointages, congés, absences
4. **Prêts** : Gestion complète avec échéanciers
5. **Recrutement** : Du sourcing à l'embauche
6. **Formation** : Suivi et évaluations
7. **Déclarations** : CNSS, IRG, INAM automatisées
8. **Rapports** : Statistiques et exports

### Technologies Utilisées

- **Backend** : Python 3.10+, Django 4.2
- **Base de données** : PostgreSQL 14+
- **Frontend** : Bootstrap 5, jQuery, Chart.js
- **Tâches asynchrones** : Celery, Redis
- **Génération PDF** : ReportLab
- **Export Excel** : openpyxl

### Installation

Voir [docs/GUIDE_INSTALLATION.md](docs/GUIDE_INSTALLATION.md) pour les instructions complètes.

### Support

- Email : support@votre-entreprise.com
- Documentation : http://docs.votre-entreprise.com
- Téléphone : +224 XXX XXX XXX

---

## Compatibilité

### Navigateurs Supportés
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

### Systèmes d'Exploitation
- ✅ Windows 10/11
- ✅ Linux (Ubuntu 20.04+, Debian 11+)
- ✅ macOS 11+

### Base de Données
- ✅ PostgreSQL 14+
- ✅ PostgreSQL 15
- ✅ PostgreSQL 16

---

## Contributeurs

- **Chef de Projet** : [Nom]
- **Développeurs** : [Noms]
- **Experts RH** : [Noms]
- **Testeurs** : [Noms]

---

## Licence

Propriétaire - Tous droits réservés © 2025 Votre Entreprise

---

**Dernière mise à jour** : 19 octobre 2025
