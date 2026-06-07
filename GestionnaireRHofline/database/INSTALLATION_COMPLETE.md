# 🗄️ Installation Complète de la Base de Données

## Guide Pas à Pas - Gestionnaire RH Guinée

---

## 📋 Vue d'Ensemble

Cette base de données PostgreSQL contient **50+ tables**, **10+ vues**, **20+ fonctions** et **15+ procédures stockées** pour gérer l'intégralité des processus RH d'une entreprise en Guinée.

### Modules Inclus

1. ✅ Système et Sécurité (4 tables)
2. ✅ Configuration Entreprise (2 tables)
3. ✅ Organisation (2 tables)
4. ✅ Employés (2 tables)
5. ✅ Formation et Carrière (3 tables)
6. ✅ Temps de Travail (8 tables)
7. ✅ Paie - Paramétrage (6 tables)
8. ✅ Paie - Éléments (2 tables)
9. ✅ Paie - Bulletins (3 tables)
10. ✅ Acomptes et Prêts (4 tables)
11. ✅ Recrutement (3 tables)
12. ✅ Départs (2 tables)
13. ✅ Dashboard & Statistiques (2 tables)
14. ✅ Sanctions (2 tables)
15. ✅ Portail Employé (3 tables)
16. ✅ Comptabilité & Déclarations (4 tables)
17. ✅ Audit & Sauvegarde (2 tables)
18. ✅ Signature Électronique (1 table)

---

## 🚀 Méthode 1 : Installation Automatique (Recommandée)

### Windows

```bash
cd database
install_database.bat
```

Le script va :
1. ✅ Vérifier PostgreSQL
2. ✅ Créer la base de données `gestionnaire_rh`
3. ✅ Créer l'utilisateur `rh_user`
4. ✅ Créer toutes les tables
5. ✅ Créer les vues et index
6. ✅ Créer les fonctions et procédures
7. ✅ Insérer les données initiales Guinée
8. ✅ Générer le fichier `.env` pour Django

### Linux/Mac

```bash
cd database
chmod +x install_database.sh
./install_database.sh
```

---

## 🔧 Méthode 2 : Installation Manuelle

### Étape 1 : Créer la Base de Données

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Dans psql:
CREATE DATABASE gestionnaire_rh
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'fr_FR.UTF-8'
    LC_CTYPE = 'fr_FR.UTF-8'
    TEMPLATE = template0;

# Créer l'utilisateur
CREATE USER rh_user WITH PASSWORD 'VotreMotDePasseSecurise123!';

# Accorder les privilèges
GRANT ALL PRIVILEGES ON DATABASE gestionnaire_rh TO rh_user;

# Se connecter à la base
\c gestionnaire_rh

# Accorder les privilèges sur le schéma public
GRANT ALL ON SCHEMA public TO rh_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rh_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rh_user;

# Quitter
\q
```

### Étape 2 : Créer les Tables

```bash
psql -U rh_user -d gestionnaire_rh -f schema_complete.sql
```

**Note** : Si vous avez le schéma complet dans un seul fichier, sinon exécutez dans l'ordre :

```bash
# Tables de base
psql -U rh_user -d gestionnaire_rh << 'EOF'
-- Copier ici le contenu SQL des tables depuis votre demande initiale
EOF
```

### Étape 3 : Créer les Vues et Index

```bash
psql -U rh_user -d gestionnaire_rh -f views_and_indexes.sql
```

Cela créera :
- ✅ 10 vues principales (v_employes_actifs, v_livre_paie, etc.)
- ✅ 50+ index de performance
- ✅ Commentaires sur les tables

### Étape 4 : Créer les Fonctions et Procédures

```bash
psql -U rh_user -d gestionnaire_rh -f functions_procedures.sql
```

Cela créera :
- ✅ Fonctions de calcul de paie (CNSS, IRG, INAM)
- ✅ Fonctions de gestion des congés
- ✅ Fonctions d'ancienneté
- ✅ Fonctions d'indemnités
- ✅ Procédures de gestion
- ✅ Triggers automatiques

### Étape 5 : Insérer les Données Initiales

```bash
psql -U rh_user -d gestionnaire_rh -f data_init_guinee.sql
```

Cela insèrera :
- ✅ 5 profils utilisateurs
- ✅ 16 paramètres de paie Guinée
- ✅ 6 tranches IRG 2025
- ✅ 8 jours fériés 2025
- ✅ 25 rubriques de paie standard
- ✅ 6 horaires de travail
- ✅ 6 types de prêts
- ✅ 12 types de départ
- ✅ 10 types de sanctions
- ✅ 24 indicateurs RH

### Étape 6 : Vérifier l'Installation

```bash
psql -U rh_user -d gestionnaire_rh
```

Dans psql, exécuter :

```sql
-- Vérifier les tables
SELECT COUNT(*) AS nb_tables 
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- Devrait retourner environ 50 tables

-- Vérifier les vues
SELECT COUNT(*) AS nb_vues 
FROM information_schema.views 
WHERE table_schema = 'public';

-- Devrait retourner environ 10 vues

-- Vérifier les fonctions
SELECT COUNT(*) AS nb_fonctions 
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public';

-- Devrait retourner 20+ fonctions

-- Vérifier les données initiales
SELECT 'Profils: ' || COUNT(*) FROM profils_utilisateurs
UNION ALL
SELECT 'Paramètres: ' || COUNT(*) FROM parametres_paie
UNION ALL
SELECT 'Tranches IRG: ' || COUNT(*) FROM tranches_irg
UNION ALL
SELECT 'Jours fériés: ' || COUNT(*) FROM calendrier_jours_feries
UNION ALL
SELECT 'Rubriques: ' || COUNT(*) FROM rubriques_paie
UNION ALL
SELECT 'Horaires: ' || COUNT(*) FROM horaires_travail;
```

---

## 📊 Structure Créée

### Tables Principales (50+)

#### Système (4)
- `utilisateurs`
- `profils_utilisateurs`
- `droits_acces`
- `logs_activite`

#### Configuration (2)
- `societe`
- `etablissements`

#### Organisation (2)
- `services`
- `postes`

#### Employés (2)
- `employes`
- `contrats_employes`

#### Formation (3)
- `formations_employes`
- `carrieres_employes`
- `evaluations_employes`

#### Temps (8)
- `calendrier_jours_feries`
- `horaires_travail`
- `affectation_horaires`
- `pointages`
- `conges`
- `soldes_conges`
- `absences`
- `arrets_travail`

#### Paie (11)
- `periodes_paie`
- `parametres_paie`
- `tranches_irg`
- `constantes_calcul`
- `rubriques_paie`
- `composants_rubriques`
- `variables_paie`
- `elements_salaire`
- `grilles_salariales`
- `bulletins_paie`
- `lignes_bulletin`
- `cumuls_paie`

#### Prêts (4)
- `acomptes`
- `types_prets`
- `prets`
- `echeances_prets`

#### Recrutement (3)
- `offres_emploi`
- `candidatures`
- `entretiens_recrutement`

#### Départs (2)
- `types_depart`
- `departs_employes`

#### Statistiques (2)
- `indicateurs_rh`
- `valeurs_indicateurs`
- `alertes_rh`

#### Sanctions (2)
- `types_sanctions`
- `sanctions_employes`

#### Portail (3)
- `demandes_employes`
- `notifications_employes`
- `documents_employes`

#### Comptabilité (4)
- `journaux_paie`
- `ecritures_comptables`
- `declarations_sociales`
- `lignes_declarations`

#### Audit (2)
- `sauvegardes`
- `historique_modifications`

#### Signature (1)
- `signatures_documents`

### Vues (10+)

1. `v_employes_actifs` - Employés actifs avec infos complètes
2. `v_livre_paie` - Livre de paie mensuel
3. `v_pyramide_ages` - Répartition par âge
4. `v_effectif_par_service` - Statistiques par service
5. `v_effectif_par_categorie` - Statistiques par catégorie
6. `v_soldes_conges` - Soldes de congés actuels
7. `v_conges_en_cours` - Congés en cours et à venir
8. `v_prets_en_cours` - Prêts actifs
9. `v_absences_mois_courant` - Absences du mois
10. `v_contrats_echeance` - Contrats arrivant à échéance
11. `v_stats_paie_mensuelle` - Statistiques paie
12. `v_turnover_annuel` - Turnover par année

### Fonctions (20+)

#### Calcul Paie
- `calcul_base_cnss()`
- `calcul_cnss_employe()`
- `calcul_cnss_employeur()`
- `calcul_inam()`
- `calcul_abattement_irg()`
- `calcul_irg()`
- `calcul_net_a_payer()`

#### Congés
- `calcul_jours_ouvrables()`
- `verifier_solde_conges()`
- `maj_solde_conges()`

#### Ancienneté
- `calcul_anciennete_annees()`
- `calcul_prime_anciennete()`

#### Indemnités
- `calcul_indemnite_licenciement()`
- `calcul_indemnite_conges()`

#### Utilitaires
- `generer_matricule()`
- `est_en_conge()`
- `calcul_taux_absenteisme()`

### Procédures (5+)

- `init_soldes_conges_annee()` - Initialiser congés annuels
- `generer_alertes_contrats()` - Alertes fin de contrat
- `calculer_cumuls_paie()` - Calcul cumuls mensuels

### Triggers (5+)

- `trg_employe_modification` - MAJ date modification
- `trg_log_employes` - Logger modifications
- `trg_valider_conges` - Valider dates congés
- `trg_maj_solde_conges` - MAJ solde après approbation

---

## 🔐 Sécurité

### Configuration PostgreSQL

Modifier `pg_hba.conf` pour sécuriser l'accès :

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   gestionnaire_rh rh_user                                 md5
host    gestionnaire_rh rh_user         127.0.0.1/32            md5
host    gestionnaire_rh rh_user         ::1/128                 md5
```

### Mot de Passe Fort

Le mot de passe doit contenir :
- ✅ Au moins 12 caractères
- ✅ Majuscules et minuscules
- ✅ Chiffres
- ✅ Caractères spéciaux

Exemple : `RH@Guinee2025!Secure`

### Sauvegardes

Configurer des sauvegardes automatiques :

```bash
# Sauvegarde quotidienne (cron Linux)
0 2 * * * /chemin/vers/database/backup_database.sh

# Sauvegarde hebdomadaire complète
0 3 * * 0 /chemin/vers/database/backup_full.sh
```

---

## 🧪 Tests Post-Installation

### Test 1 : Connexion

```bash
psql -U rh_user -d gestionnaire_rh -c "SELECT version();"
```

### Test 2 : Tables

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

### Test 3 : Données Initiales

```sql
-- Vérifier les paramètres de paie
SELECT code_parametre, libelle_parametre, valeur_numerique 
FROM parametres_paie 
WHERE actif = TRUE;

-- Vérifier les tranches IRG
SELECT numero_tranche, borne_inferieure, borne_superieure, taux_irg 
FROM tranches_irg 
WHERE annee_validite = 2025 
ORDER BY numero_tranche;

-- Vérifier les jours fériés 2025
SELECT libelle, date_jour_ferie, type_ferie 
FROM calendrier_jours_feries 
WHERE annee = 2025 
ORDER BY date_jour_ferie;
```

### Test 4 : Fonctions

```sql
-- Test calcul CNSS
SELECT calcul_cnss_employe(2000000) AS cnss_employe;
-- Devrait retourner 100000 (5% de 2M)

-- Test calcul IRG
SELECT calcul_irg(5000000, 150000, 75000) AS irg;
-- Devrait calculer l'IRG sur la base imposable

-- Test jours ouvrables
SELECT calcul_jours_ouvrables('2025-01-01', '2025-01-31') AS jours;
-- Devrait retourner environ 22 jours
```

### Test 5 : Vues

```sql
-- Test vue employés actifs
SELECT COUNT(*) FROM v_employes_actifs;

-- Test vue pyramide des âges
SELECT * FROM v_pyramide_ages;

-- Test vue effectif par service
SELECT * FROM v_effectif_par_service;
```

---

## 🔄 Maintenance

### Optimisation

```sql
-- Analyser les tables
ANALYZE;

-- Réindexer
REINDEX DATABASE gestionnaire_rh;

-- Nettoyer
VACUUM FULL;
```

### Monitoring

```sql
-- Taille de la base
SELECT pg_size_pretty(pg_database_size('gestionnaire_rh'));

-- Tables les plus volumineuses
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Connexions actives
SELECT * FROM pg_stat_activity 
WHERE datname = 'gestionnaire_rh';
```

---

## 🆘 Dépannage

### Erreur : "database already exists"

```bash
# Supprimer et recréer
psql -U postgres -c "DROP DATABASE IF EXISTS gestionnaire_rh;"
psql -U postgres -c "CREATE DATABASE gestionnaire_rh;"
```

### Erreur : "permission denied"

```sql
-- Accorder tous les droits
GRANT ALL PRIVILEGES ON DATABASE gestionnaire_rh TO rh_user;
GRANT ALL ON SCHEMA public TO rh_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rh_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rh_user;
```

### Erreur : "relation does not exist"

Vérifier l'ordre d'exécution des scripts. Les tables doivent être créées avant les vues et fonctions.

---

## 📞 Support

Pour toute question sur l'installation de la base de données :

- **Email** : db-support@votre-entreprise.com
- **Documentation** : [database/README.md](README.md)
- **Téléphone** : +224 XXX XXX XXX

---

**Installation réussie ! ✅**

Vous pouvez maintenant passer à la configuration de Django.
