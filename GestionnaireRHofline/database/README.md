# Base de Données - Gestionnaire RH Guinée

## 📋 Vue d'ensemble

Cette base de données PostgreSQL est conçue pour gérer l'ensemble des processus RH d'une entreprise en Guinée, en conformité avec le Code du Travail guinéen et les réglementations locales (CNSS, IRG, INAM).

## 🏗️ Architecture

La base de données est organisée en **18 modules principaux** :

### 1. **Système et Sécurité**
- Gestion des utilisateurs et authentification
- Profils et droits d'accès par module
- Logs d'activité et audit trail

### 2. **Configuration Entreprise**
- Informations société (NIF, CNSS, INAM)
- Gestion multi-établissements
- Paramètres généraux

### 3. **Organisation**
- Structure hiérarchique des services
- Catalogue des postes
- Organigramme

### 4. **Employés** (Cœur du système)
- Dossier complet employé
- État civil et immatriculation
- Informations professionnelles
- Coordonnées bancaires et Mobile Money
- Gestion des contrats

### 5. **Formation et Carrière**
- Historique des formations
- Mouvements de carrière (promotions, mutations)
- Évaluations annuelles

### 6. **Temps de Travail**
- Calendrier des jours fériés
- Horaires de travail flexibles
- Pointages quotidiens
- Gestion des congés et soldes
- Absences et arrêts de travail

### 7-9. **Module Paie**
- **Paramétrage** : Périodes, paramètres CNSS/IRG/INAM, tranches IRG
- **Éléments salariaux** : Grilles salariales, éléments fixes/variables
- **Bulletins** : Génération, calcul, cumuls mensuels/annuels

### 10. **Acomptes et Prêts**
- Demandes d'acomptes
- Gestion des prêts avec échéanciers
- Suivi des remboursements

### 11. **Recrutement**
- Publication d'offres d'emploi
- Gestion des candidatures
- Entretiens et évaluations

### 12. **Départs**
- Types de départ (démission, licenciement, retraite)
- Calcul des indemnités
- Solde de tout compte

### 13. **Dashboard & Statistiques**
- Indicateurs RH personnalisables
- Alertes automatiques
- Tableaux de bord

### 14. **Sanctions Disciplinaires**
- Types de sanctions
- Historique disciplinaire
- Procédures de recours

### 15. **Portail Employé**
- Demandes en ligne
- Notifications
- Accès aux documents personnels

### 16. **Comptabilité & Déclarations**
- Journaux de paie
- Écritures comptables
- Déclarations CNSS/IRG/INAM

### 17. **Audit & Sauvegarde**
- Sauvegardes automatiques
- Historique des modifications
- Traçabilité complète

### 18. **Signature Électronique**
- Signature des documents
- Certificats numériques
- Validation multi-niveaux

## 📊 Vues Principales

### `v_employes_actifs`
Liste complète des employés actifs avec leurs informations principales.

### `v_livre_paie`
Livre de paie mensuel avec tous les éléments de rémunération.

### `v_pyramide_ages`
Répartition des employés par tranche d'âge et sexe.

### `v_effectif_par_service`
Statistiques d'effectif par service avec moyennes d'âge et d'ancienneté.

## 🔑 Index de Performance

Des index sont créés sur :
- Matricules et identifiants employés
- Dates de pointage et périodes de paie
- Statuts (employé, bulletin, congé)
- Numéros CNSS et identifiants fiscaux

## 🇬🇳 Spécificités Guinée

### Cotisations Sociales
- **CNSS Employé** : 5% (plafonné à 3 000 000 GNF)
- **CNSS Employeur** : 18% (plafonné à 3 000 000 GNF)
- **INAM** : 2,5% (plafonné à 3 000 000 GNF)

### IRG (Impôt sur le Revenu)
Barème progressif par tranches :
- 0 - 1 000 000 GNF : 0%
- 1 000 001 - 3 000 000 GNF : 5%
- 3 000 001 - 6 000 000 GNF : 10%
- 6 000 001 - 12 000 000 GNF : 15%
- 12 000 001 - 25 000 000 GNF : 20%
- Au-delà de 25 000 000 GNF : 25%

Abattement forfaitaire : 20% (plafonné à 300 000 GNF)

### Temps de Travail
- **Durée légale** : 40 heures/semaine (173,33 heures/mois)
- **Congés annuels** : 26 jours ouvrables
- **SMIG** : 440 000 GNF (2025)

### Jours Fériés 2025
- 1er janvier : Jour de l'An
- 21 avril : Lundi de Pâques
- 1er mai : Fête du Travail
- 31 mars : Aïd el-Fitr
- 7 juin : Aïd el-Kebir (Tabaski)
- 5 septembre : Maouloud
- 2 octobre : Fête de l'Indépendance
- 25 décembre : Noël

## 🚀 Installation

### 1. Créer la base de données

```bash
# Connexion à PostgreSQL
psql -U postgres

# Création de la base
CREATE DATABASE gestionnaire_rh;
CREATE USER rh_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE gestionnaire_rh TO rh_user;
```

### 2. Exécuter les scripts SQL

```bash
# Depuis le répertoire database/
psql -U rh_user -d gestionnaire_rh -f schema_complete.sql
```

### 3. Initialiser les données de base (Django)

```bash
# Depuis la racine du projet Django
python manage.py init_database
```

## 📝 Conventions de Nommage

- **Tables** : nom au pluriel en minuscules (ex: `employes`, `bulletins_paie`)
- **Colonnes** : snake_case (ex: `date_embauche`, `salaire_brut`)
- **Clés primaires** : `id_[nom_table_singulier]` (ex: `id_employe`)
- **Clés étrangères** : `id_[table_référencée]` (ex: `id_service`)
- **Contraintes** : 
  - FK : `fk_[table]_[colonne]`
  - Unique : `unique_[description]`

## 🔒 Sécurité

### Bonnes Pratiques
1. **Mots de passe** : Toujours hashés (bcrypt/PBKDF2)
2. **Logs** : Toutes les actions sensibles sont tracées
3. **Droits** : Système de profils avec permissions granulaires
4. **Audit** : Historique complet des modifications
5. **Sauvegarde** : Automatique quotidienne recommandée

### Données Sensibles
- Photos et documents : stockés en BYTEA (chiffrés recommandé)
- Salaires : accès restreint par profil
- Données personnelles : conformité RGPD/protection des données

## 📈 Maintenance

### Sauvegardes Recommandées
```bash
# Sauvegarde complète quotidienne
pg_dump -U rh_user gestionnaire_rh > backup_$(date +%Y%m%d).sql

# Sauvegarde avec compression
pg_dump -U rh_user -Fc gestionnaire_rh > backup_$(date +%Y%m%d).dump
```

### Optimisation
```sql
-- Analyse des tables
ANALYZE;

-- Réindexation
REINDEX DATABASE gestionnaire_rh;

-- Nettoyage
VACUUM FULL;
```

### Monitoring
- Surveiller la taille des tables `logs_activite` et `historique_modifications`
- Archiver les bulletins de paie anciens (> 10 ans)
- Purger les logs après 2 ans (conformité légale)

## 📚 Documentation Complémentaire

- **Code du Travail de Guinée** : Loi L/2014/072/CNT
- **CNSS** : Caisse Nationale de Sécurité Sociale
- **INAM** : Institut National d'Assurance Maladie
- **DGI** : Direction Générale des Impôts (IRG)

## 🤝 Support

Pour toute question ou problème :
1. Consulter la documentation technique
2. Vérifier les logs d'erreur PostgreSQL
3. Contacter l'équipe de développement

## 📄 Licence

Système propriétaire - Tous droits réservés

---

**Version** : 1.0  
**Date** : Octobre 2025  
**Auteur** : Équipe Développement RH Guinée
