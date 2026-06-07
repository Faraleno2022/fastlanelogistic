# 📚 SCHÉMA PÉDAGOGIQUE DU SYSTÈME GestionnaireRH

**Version** : Janvier 2026  
**Conforme au Code du Travail guinéen et CGI 2022**

---

## 🎯 Objectif pédagogique

À la fin de la formation, l'apprenant doit comprendre :
- Comment les informations RH circulent dans le système
- Quels modules interviennent à chaque étape
- Comment une action RH impacte la paie et les déclarations

---

## 📖 NIVEAU 0 – CONCEPTS DE BASE (Pour débutants)

**👉 À lire avant de commencer**

### Vocabulaire essentiel

| Terme | Définition simple |
|-------|-------------------|
| **Salaire brut** | Tout ce que l'employé gagne avant les retenues |
| **Salaire net** | Ce que l'employé reçoit réellement (brut - retenues) |
| **Retenue salariale** | Ce qu'on déduit du salaire de l'employé (CNSS 5%, RTS) |
| **Charge patronale** | Ce que l'employeur paie EN PLUS du salaire (CNSS 18%, VF, TA) |
| **CNSS** | Caisse Nationale de Sécurité Sociale (retraite, maladie) |
| **RTS** | Retenue à la Source - impôt sur le revenu (anciennement IRG) |
| **DGI** | Direction Générale des Impôts (collecte le RTS) |

### Qui paie quoi ?

```
┌─────────────────────────────────────────────────────────┐
│                    EMPLOYEUR                            │
│  Paie : Salaire brut + CNSS 18% + VF 6% + TA 1,5%      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    EMPLOYÉ reçoit                       │
│  Salaire brut - CNSS 5% - RTS = NET À PAYER            │
└─────────────────────────────────────────────────────────┘
```

### Organismes concernés

| Organisme | Rôle | Ce qu'on lui verse |
|-----------|------|--------------------|
| **CNSS** | Sécurité sociale | Cotisations salarié + employeur |
| **DGI / Trésor** | Impôts | RTS (retenue sur salaire) |
| **ONFPP** | Formation professionnelle | Taxe d'apprentissage |

#### 📌 Message clé
> L'employeur ne garde rien : il collecte les retenues et les reverse aux organismes.

---

## 🏢 NIVEAU 1 – PARAMÉTRAGE DE L'ENTREPRISE

### 📦 Module : `core/`

**👉 Toujours commencer par ici**

#### Modèles de données

| Modèle | Description | Champs clés |
|--------|-------------|-------------|
| `Entreprise` | Identité de l'entreprise | `nom_entreprise`, `nif`, `num_cnss`, `secteur_activite` |
| `Utilisateur` | Comptes utilisateurs | `email`, `profil`, `est_admin_entreprise` |
| `ProfilUtilisateur` | Rôles et droits | `niveau_acces` (1-5: Consultation → Admin) |
| `DroitAcces` | Permissions par module | `module`, `peut_lire`, `peut_creer`, `peut_modifier` |
| `Etablissement` | Sites de l'entreprise | `code_etablissement`, `type` (siège, agence, usine) |
| `Service` | Départements | `code_service`, `nom_service`, `responsable` |
| `Poste` | Postes de travail | `intitule_poste`, `categorie_professionnelle`, `classification` |

#### Configuration paie par entreprise

| Modèle | Description |
|--------|-------------|
| `ConfigurationPaieEntreprise` | **Nouveau** - Taux HS, congés, CNSS configurables |

**Modes disponibles :**
- **Code du Travail** : HS +30%/+60%, Congés 1,5 j/mois
- **Convention Collective** : HS +15%/+25%/+50%, Congés 2,5 j/mois
- **Personnalisé** : Valeurs libres

#### URLs principales
```
/                          → Page d'accueil (landing)
/login/                    → Connexion
/register-entreprise/      → Création entreprise
/structure/                → Gestion établissements/services/postes
/manage-users/             → Gestion utilisateurs
/paie/configuration/       → Configuration paie entreprise
```

#### 📌 Message clé
> Chaque entreprise peut avoir ses propres règles, mais le système garantit la conformité minimale.

---

## 👥 NIVEAU 2 – GESTION DES EMPLOYÉS

### 📦 Module : `employes/`

**👉 Sans employés, pas de paie**

#### Modèles de données

| Modèle | Description | Champs clés |
|--------|-------------|-------------|
| `Employe` | Fiche employé complète | `matricule`, `nom`, `prenoms`, `date_naissance`, `sexe`, `situation_familiale`, `nombre_enfants` |
| `ContratEmploye` | Contrats de travail | `type_contrat` (CDI, CDD, Stage), `date_debut`, `date_fin`, `salaire_base` |
| `AvenantContrat` | Modifications de contrat | `motif`, `nouvelles_conditions` |
| `RuptureContrat` | Fin de contrat | `type_rupture` (démission, licenciement, fin CDD) |
| `CarriereEmploye` | Évolutions de carrière | `type_mouvement` (promotion, mutation), `ancien_salaire`, `nouveau_salaire` |
| `DocumentEmploye` | Pièces justificatives | `type_document` (CV, diplôme, CNI, contrat signé) |

#### Modèles santé & discipline

| Modèle | Description |
|--------|-------------|
| `VisiteMedicale` | Suivi médical | `type_visite`, `date_visite`, `aptitude` |
| `SanctionDisciplinaire` | Sanctions | `type_sanction`, `motif`, `date_sanction` |
| `AccidentTravail` | Accidents | `gravite`, `jours_arret`, `declaration_cnss` |
| `EquipementProtection` | EPI fournis | `type_epi`, `date_attribution` |

#### URLs principales
```
/employes/                        → Liste des employés
/employes/creer/                  → Créer employé
/employes/<id>/                   → Fiche employé
/employes/<id>/contrats/          → Contrats
/employes/<id>/documents/         → Documents
/employes/<id>/carriere/          → Historique carrière
```

#### 📌 Lien pédagogique
> Les informations de ce module alimentent directement la paie (salaire de base, primes, situation familiale pour RTS).

---

## ⏱️ NIVEAU 3 – TEMPS DE TRAVAIL & CONGÉS

### 📦 Module : `temps_travail/`

#### Modèles de données

| Modèle | Description | Champs clés |
|--------|-------------|-------------|
| `Pointage` | Présences quotidiennes | `date_pointage`, `heure_entree`, `heure_sortie`, `heures_travaillees` |
| `Absence` | Absences | `type_absence` (maladie, injustifiée), `duree`, `justificatif` |
| `ArretTravail` | Arrêts maladie | `date_debut`, `date_fin`, `pris_en_charge_cnss` |
| `HeureSupplementaire` | HS détaillées | `type_hs` (normal, nuit, dimanche), `nombre_heures`, `taux_majoration` |
| `HoraireTravail` | Plannings | `heure_debut`, `heure_fin`, `pause_dejeuner` |
| `JourFerie` | Calendrier fériés | `date_jour_ferie`, `type_ferie` (national, religieux) |

**Taux HS selon configuration entreprise :**

| Type | Code du Travail | Convention |
|------|-----------------|------------|
| 4 premières HS | +30% | +15% |
| Au-delà | +60% | +25% |
| Nuit (21h-6h)* | +20% | +50% |
| Dimanche/Férié | +60% | +100% |

*_Plage horaire nuit : 21h-6h selon la plupart des références guinéennes (configurable par entreprise)_

### 📦 Module : `conges/` (App séparée)

| Modèle | Description | Champs clés |
|--------|-------------|-------------|
| `Conge` | Demandes de congé | `type_conge`, `date_debut`, `date_fin`, `nombre_jours`, `statut_demande` |
| `SoldeConge` | Soldes par employé | `conges_acquis`, `conges_pris`, `conges_restants`, `conges_reports` |
| `DroitConge` | Droits annuels | `jours_base`, `jours_anciennete`, `total_droits` |

**Types de congés disponibles :**
- Congé annuel (1,5 ou 2,5 j/mois selon config)
- Congé maternité (14 semaines)
- Congé paternité (3 jours)
- Congé mariage (4 jours)
- Décès conjoint/enfant (5 jours)
- Décès parent (3 jours)

#### URLs principales
```
/temps/pointages/                 → Saisie pointages
/temps/absences/                  → Gestion absences
/temps/heures-sup/                → Heures supplémentaires
/conges/                          → Liste demandes congés
/conges/demander/                 → Nouvelle demande
/conges/soldes/                   → Soldes par employé
```

#### 📌 Lien pédagogique
> Le temps de travail et les congés modifient le salaire brut (absences déduites, HS ajoutées).

---

## 💰 NIVEAU 4 – PAIE (Le cœur du système)

### 📦 Module : `paie/`

**👉 C'est ici que tout se croise**

#### Modèles principaux

| Modèle | Description | Champs clés |
|--------|-------------|-------------|
| `PeriodePaie` | Mois de paie | `annee`, `mois`, `statut_periode` (ouverte → clôturée) |
| `BulletinPaie` | Bulletins générés | `salaire_brut`, `cnss_employe`, `rts`, `net_a_payer` |
| `LigneBulletin` | Détail du bulletin | `rubrique`, `base`, `taux`, `montant` |
| `RubriquePaie` | Éléments de paie | `code_rubrique`, `type` (gain, retenue), `soumis_cnss`, `soumis_rts` |
| `ElementSalaire` | Éléments fixes | `employe`, `rubrique`, `montant` (primes permanentes) |

#### Modèles de calcul

| Modèle | Description |
|--------|-------------|
| `Constante` | Paramètres légaux (SMIG, plafonds) |
| `TrancheRTS` | Barème RTS progressif (6 tranches) |
| `GrilleIndiciaire` | Grilles salariales |
| `ConfigurationPaieEntreprise` | Taux HS/Congés/CNSS par entreprise |

#### Barème RTS - CGI 2022

| Tranche | Revenu mensuel (GNF) | Taux |
|---------|---------------------|------|
| 1 | 0 - 1 000 000 | 0% |
| 2 | 1 000 001 - 3 000 000 | 5% |
| 3 | 3 000 001 - 5 000 000 | 8% |
| 4 | 5 000 001 - 10 000 000 | 10% |
| 5 | 10 000 001 - 20 000 000 | 15% |
| 6 | > 20 000 000 | 20% |

#### Modèles complémentaires

| Modèle | Description |
|--------|-------------|
| `AvanceSalaire` | Avances sur salaire |
| `Pret` | Prêts employés |
| `SaisieArret` | Saisies sur salaire |
| `NoteFrais` | Notes de frais |
| `ArchiveBulletin` | Conservation légale 10 ans |

#### URLs principales
```
/paie/                            → Accueil paie
/paie/periodes/                   → Gestion périodes
/paie/periodes/<id>/calculer/     → Calculer les bulletins
/paie/bulletins/                  → Liste bulletins
/paie/bulletins/<id>/             → Détail bulletin
/paie/bulletins/<id>/imprimer/    → Impression PDF
/paie/livre/                      → Livre de paie
/paie/configuration/              → Config HS/Congés/CNSS
/paie/simulation/                 → Simulateur de paie
/paie/prets/                      → Gestion des prêts
/paie/frais/                      → Notes de frais
```

#### Flux de calcul

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Employé    │────▶│  Éléments   │────▶│   BRUT      │
│  (base +    │     │  variables  │     │             │
│   primes)   │     │  (HS, abs)  │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
     ┌─────────────────────────────────────────┘
     │
     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  CNSS 5%    │────▶│  RTS        │────▶│   NET       │
│  (plafonné) │     │  progressif │     │   À PAYER   │
└─────────────┘     └─────────────┘     └─────────────┘
```

#### 📌 Message clé
> La paie n'invente rien, elle additionne et applique des règles configurables.

---

## 🧾 NIVEAU 5 – DÉCLARATIONS SOCIALES

### 📦 Inclus dans `paie/`

#### Modèles de données

| Modèle | Description | Champs clés |
|--------|-------------|-------------|
| `DeclarationSociale` | Déclarations générées | `type_declaration`, `periode`, `montant_total`, `statut` |
| `LigneDeclaration` | Détail par employé | `employe`, `base`, `cotisation` |
| `AlerteEcheance` | Rappels échéances | `type_echeance`, `date_limite` |
| `TransmissionCNSS` | Historique envois | `date_transmission`, `fichier_xml` |

#### Types de déclarations

| Déclaration | Échéance | Destinataire |
|-------------|----------|--------------|
| CNSS mensuelle | 15 du mois suivant | CNSS |
| RTS mensuelle | 10 ou 15 du mois suivant* | Trésor Public / DGI |
| VF (6%) | Trimestriel | DGI |
| TA (1,5%) | Annuel | ONFPP |

*_Échéance RTS : varie selon les instructions fiscales en vigueur (généralement 10 ou 15 du mois suivant)_

#### URLs principales
```
/paie/declarations/               → Tableau déclarations
/paie/declarations/pdf/           → Export PDF
/paie/export/cnss/excel/          → Export CNSS Excel
/paie/export/dmu/                 → Déclaration Mensuelle Unique
/paie/echeances/                  → Alertes échéances
```

#### 📌 Lien pédagogique
> Sans paie validée → pas de déclaration. Les déclarations sont générées automatiquement.

---

## 📈 NIVEAU 6 – TABLEAUX DE BORD

### 📦 Module : `dashboard/`

#### Indicateurs affichés

| Catégorie | Indicateurs |
|-----------|-------------|
| **Effectif** | Total employés, répartition H/F, CDI/CDD/Stage |
| **Paie** | Masse salariale, bulletins calculés/validés |
| **Temps** | Pointages du jour, congés en cours, absences |
| **Alertes** | Contrats à échéance, visites médicales, documents expirés |

#### URLs principales
```
/dashboard/                       → Tableau de bord principal
```

#### Données calculées
```python
# Statistiques employés
total_employes = Employe.filter(statut='actif').count()
hommes = Employe.filter(sexe='M').count()
femmes = Employe.filter(sexe='F').count()

# Paie du mois
masse_salariale = BulletinPaie.filter(periode=mois_actuel).aggregate(Sum('net_a_payer'))

# Alertes
contrats_a_echeance = ContratEmploye.filter(date_fin__lte=today + 30j)
```

---

## 🎓 NIVEAU 7 – DÉVELOPPEMENT DES TALENTS

### 📦 Module : `formation/`

#### Modèles de données

| Modèle | Description | Champs clés |
|--------|-------------|-------------|
| `CatalogueFormation` | Formations disponibles | `code_formation`, `intitule`, `duree`, `cout` |
| `SessionFormation` | Sessions planifiées | `date_debut`, `date_fin`, `formateur`, `lieu` |
| `InscriptionFormation` | Inscriptions employés | `employe`, `session`, `statut` |
| `EvaluationFormation` | Évaluations | `note_globale`, `commentaires` |
| `PlanFormation` | Plan annuel | `annee`, `budget`, `objectifs` |

#### URLs principales
```
/formation/                       → Catalogue formations
/formation/sessions/              → Sessions planifiées
/formation/inscriptions/          → Inscriptions
/formation/plan/                  → Plan de formation
```

### 📦 Module : `recrutement/`

#### Modèles de données

| Modèle | Description | Champs clés |
|--------|-------------|-------------|
| `OffreEmploi` | Offres publiées | `reference_offre`, `intitule_poste`, `type_contrat`, `salaire_propose` |
| `Candidature` | Candidatures reçues | `nom`, `prenoms`, `cv`, `lettre_motivation`, `statut` |
| `EntretienRecrutement` | Entretiens | `date_entretien`, `type` (téléphonique, visio, présentiel) |
| `TestRecrutement` | Tests | `type_test`, `note`, `observations` |
| `DecisionEmbauche` | Décisions finales | `decision`, `date_embauche_prevue`, `salaire_propose` |

#### Workflow recrutement
```
Offre → Candidatures → Présélection → Entretiens → Tests → Décision → Embauche
```

#### URLs principales
```
/recrutement/                     → Dashboard recrutement
/recrutement/offres/              → Gestion offres
/recrutement/candidatures/        → Candidatures
/recrutement/entretiens/          → Planning entretiens
```

#### 📌 Vision long terme
> Le système accompagne tout le cycle de vie du salarié : recrutement → intégration → formation → évolution → départ.

---

## 🔗 SCHÉMA DES FLUX DE DONNÉES

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONFIGURATION (core)                        │
│  Entreprise → Utilisateurs → Établissements → Services → Postes │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EMPLOYÉS (employes)                        │
│        Fiche → Contrat → Documents → Carrière → Santé           │
└───────────────────┬─────────────────────────┬───────────────────┘
                    │                         │
                    ▼                         ▼
┌───────────────────────────┐   ┌─────────────────────────────────┐
│    TEMPS (temps_travail)  │   │       CONGÉS (conges)           │
│  Pointages → Absences →   │   │  Demandes → Validation → Soldes │
│  Heures Sup               │   │                                 │
└───────────────┬───────────┘   └─────────────┬───────────────────┘
                │                             │
                └──────────────┬──────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        PAIE (paie)                              │
│  Période → Calcul → Bulletin → Validation → Envoi               │
│                                                                 │
│  BRUT = Base + Primes + HS - Absences                          │
│  NET = BRUT - CNSS (5%) - RTS (progressif) - Retenues          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DÉCLARATIONS (paie)                          │
│        CNSS mensuelle → RTS mensuelle → VF/TA                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DASHBOARD (dashboard)                       │
│     Effectif → Masse salariale → Charges → Absentéisme          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 RÉCAPITULATIF PAR MODULE

| Module | Tables | Fonctionnalités clés |
|--------|--------|---------------------|
| `core` | 18 | Multi-entreprise, utilisateurs, structure, config paie |
| `employes` | 12 | Fiches, contrats, carrière, santé, discipline |
| `temps_travail` | 9 | Pointages, absences, HS, horaires |
| `conges` | 3 | Demandes, validation, soldes |
| `paie` | 20 | Bulletins, rubriques, déclarations, prêts, frais |
| `formation` | 5 | Catalogue, sessions, inscriptions, évaluations |
| `recrutement` | 6 | Offres, candidatures, entretiens, décisions |
| `dashboard` | - | Statistiques, alertes, indicateurs |

**Total : ~73 tables métier**

---

## 💡 EXERCICE PÉDAGOGIQUE SUGGÉRÉ

### Scénario de comparaison

> "Configurer deux entreprises : l'une en mode **Code du Travail** (HS +30%/+60%, congés 1,5j/mois), l'autre en mode **Convention Collective** (HS +15%/+25%, congés 2,5j/mois). Calculer la paie d'un employé avec 10 heures supplémentaires et comparer l'impact sur le bulletin."

**Étapes :**
1. Créer entreprise A → `/paie/configuration/` → Appliquer Code du Travail
2. Créer entreprise B → `/paie/configuration/` → Appliquer Convention Collective
3. Créer un employé avec même salaire de base
4. Saisir 10 HS normales
5. Calculer les bulletins
6. Comparer les résultats

---

## ⚠️ ERREURS FRÉQUENTES À ÉVITER

### En formation et en production

| Erreur | Conséquence | Solution |
|--------|-------------|----------|
| **Oublier de configurer l'entreprise avant la paie** | Calculs avec valeurs par défaut | Toujours commencer par `/paie/configuration/` |
| **Confondre charge patronale et retenue salariale** | Mauvaise compréhension des coûts | CNSS 5% = salarié, CNSS 18% = employeur |
| **Modifier un bulletin après validation** | Incohérence avec déclarations | Annuler et recalculer proprement |
| **Créer un employé sans contrat** | Paie impossible | Toujours créer contrat avec date début |
| **Oublier les HS dans la paie** | Sous-paiement de l'employé | Saisir les HS AVANT calcul période |
| **Valider la période sans vérifier** | Erreurs figées | Toujours contrôler avant validation |
| **Confondre brut imposable et brut total** | Erreur RTS | Brut imposable = Brut - éléments exonérés |

### Checklist avant validation de paie

- [ ] Configuration entreprise vérifiée (HS, congés, CNSS)
- [ ] Tous les employés ont un contrat actif
- [ ] Heures supplémentaires saisies
- [ ] Absences déduites
- [ ] Avances/prêts à jour
- [ ] Contrôle visuel des bulletins
- [ ] Comparaison avec mois précédent

---

*Document généré automatiquement - Janvier 2026*  
*GestionnaireRH - Conforme CGI 2022 & Code du Travail guinéen*
