# MANUEL D'UTILISATION - GESTIONNAIRE RH GUINÉE
## Module Paie & RH Légal - Version 3.0
### Conforme à la législation guinéenne 2025

---

# TABLE DES MATIÈRES

1. [Introduction](#1-introduction)
2. [Cadre Légal](#2-cadre-légal)
3. [Cotisations CNSS](#3-cotisations-cnss)
4. [Retenue sur Traitements et Salaires (RTS)](#4-retenue-sur-traitements-et-salaires-rts)
5. [Charges Patronales](#5-charges-patronales)
6. [Exonérations et Cas Particuliers](#6-exonérations-et-cas-particuliers)
7. [Plafond 25% des Indemnités Forfaitaires](#7-plafond-25-des-indemnités-forfaitaires)
8. [Indemnités de Licenciement](#8-indemnités-de-licenciement)
9. [Préavis et Indemnités Compensatrices](#9-préavis-et-indemnités-compensatrices)
10. [Congé Maternité](#10-congé-maternité)
11. [Allocations Familiales CNSS](#11-allocations-familiales-cnss)
12. [Accidents du Travail](#12-accidents-du-travail)
13. [Jours Fériés Légaux](#13-jours-fériés-légaux)
14. [Exemples de Calcul Complets](#14-exemples-de-calcul-complets)
15. [Déclarations Sociales](#15-déclarations-sociales)
16. [Alertes et Échéances](#16-alertes-et-échéances)
17. [Commandes de Gestion](#17-commandes-de-gestion)

---

# 1. INTRODUCTION

## 1.1 Présentation

Le Gestionnaire RH Guinée est une application complète de gestion des ressources humaines conforme à la législation guinéenne. Ce manuel détaille les méthodes de calcul de la paie selon :

- Le **Code du Travail guinéen**
- Les règlements de la **Caisse Nationale de Sécurité Sociale (CNSS)**
- Le **Code Général des Impôts (CGI)** - Version 2022+
- Les directives de la **Direction Nationale des Impôts (DNI)**

## 1.2 Principes Fondamentaux

### Obligation de Déclaration Universelle

> **IMPORTANT** : En Guinée, **TOUS les salariés doivent être déclarés**, quel que soit leur niveau de salaire.
> Les exonérations concernent uniquement le **calcul des impôts et cotisations**, PAS l'obligation de déclaration.

### Échéances

| Déclaration | Échéance | Pénalité de retard |
|-------------|----------|-------------------|
| CNSS | 15 du mois suivant | 5% par mois |
| RTS | 15 du mois suivant | 100% du montant dû |
| VF | 15 du mois suivant | 100% du montant dû |

---

# 2. CADRE LÉGAL

## 2.1 Références Légales

| Texte | Application |
|-------|-------------|
| Code du Travail | Contrats, salaires, heures supplémentaires |
| Code Général des Impôts 2022 | Barème RTS, VF, Taxe d'Apprentissage |
| Décrets CNSS | Taux, plancher, plafond |
| Arrêtés ministériels | SMIG, indemnités |

## 2.2 Constantes Légales 2025

| Constante | Valeur | Description |
|-----------|--------|-------------|
| SMIG | 550 000 GNF | Salaire Minimum Interprofessionnel Garanti |
| Plancher CNSS | 550 000 GNF | Assiette minimale de cotisation |
| Plafond CNSS | 2 500 000 GNF | Assiette maximale de cotisation |
| Heures légales/semaine | 40 heures | Durée légale du travail |
| Heures légales/mois | 173,33 heures | 40h × 52 semaines / 12 mois |
| Jours ouvrables/mois | 22 jours | Moyenne mensuelle |

## 2.3 Heures Supplémentaires (Code du Travail, Art. 221)

### Barème des Majorations

| Type d'heures | Tranche | Majoration |
|---------------|---------|------------|
| Heures de jour | 4 premières HS/semaine | **+30%** (130%) |
| Heures de jour | Au-delà de 4 HS/semaine | **+60%** (160%) |
| Heures de nuit (20h-6h) | Toutes | **+20%** (120%) |
| Jours fériés (jour) | Toutes | **+60%** (160%) |
| Jours fériés (nuit) | Toutes | **+100%** (200%) |

### Formule de Calcul

```
Taux horaire = Salaire mensuel / 173,33

Heures sup. 30% = Nb heures (4 prem. HS) × Taux horaire × 1,30
Heures sup. 60% = Nb heures (au-delà 4 HS) × Taux horaire × 1,60
Heures nuit 20% = Nb heures nuit × Taux horaire × 1,20
Heures férié jour = Nb heures × Taux horaire × 1,60
Heures férié nuit = Nb heures × Taux horaire × 2,00
```

### Exemple

```
Salaire mensuel : 2 000 000 GNF
Taux horaire : 2 000 000 / 173,33 = 11 539 GNF

Semaine avec 50 heures travaillées :
- 40 heures normales : incluses dans le salaire
- 4 heures (4 prem. HS) à 30% : 4 × 11 539 × 1,30 = 60 003 GNF
- 6 heures (au-delà) à 60% : 6 × 11 539 × 1,60 = 110 774 GNF

Total heures sup. semaine = 170 777 GNF
```

## 2.4 Congés Payés (Code du Travail, Art. 153)

### Droit de Base

| Élément | Valeur |
|---------|--------|
| Acquisition | **1,5 jour ouvrable par mois** |
| Durée annuelle | **18 jours ouvrables** |
| Moins de 18 ans | **2 jours par mois (24 jours/an)** |
| Période de référence | 1er janvier au 31 décembre |

### Majorations pour Ancienneté (+2 jours par tranche de 5 ans)

| Ancienneté | Majoration cumulée |
|------------|---------------------|
| 5 ans | **+2 jours** |
| 10 ans | **+4 jours** |
| 15 ans | **+6 jours** |
| 20 ans | **+8 jours** |
| 25 ans | **+10 jours** |

### Exemple de Calcul

```
Employé avec 12 ans d'ancienneté :

Congés de base : 18 jours (1,5j × 12 mois)
Majoration ancienneté (10 ans) : +4 jours

Total congés annuels = 22 jours ouvrables
```

### Indemnité de Congés Payés

```
Indemnité = (Salaire mensuel × 12) / 12 × (Jours de congé / 30)

Ou méthode du 1/10e :
Indemnité = 10% de la rémunération totale de la période de référence
```

> **Note** : L'indemnité ne peut être inférieure au salaire qu'aurait perçu le salarié s'il avait travaillé.

---

# 3. COTISATIONS CNSS

## 3.1 Taux de Cotisation

| Part | Taux | Répartition |
|------|------|-------------|
| **Employé** | **5%** | Retraite 2,5% + Maladie 2,5% |
| **Employeur** | **18%** | Prestations familiales 6% + AT/MP 4% + Retraite 4% + Maladie 4% |
| **Total** | **23%** | - |

## 3.2 Règle du Plancher et Plafond

### Principe

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ASSIETTE CNSS                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Si Salaire < 550 000 GNF    →  Assiette = 550 000 GNF (plancher)  │
│                                                                      │
│   Si 550 000 ≤ Salaire ≤ 2 500 000 GNF  →  Assiette = Salaire réel  │
│                                                                      │
│   Si Salaire > 2 500 000 GNF  →  Assiette = 2 500 000 GNF (plafond) │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Formule de Calcul

```
Assiette CNSS = MIN( MAX(Salaire_Brut, PLANCHER), PLAFOND )

CNSS Employé = Assiette CNSS × 5%
CNSS Employeur = Assiette CNSS × 18%
```

### Cas Particulier : Salaire Très Faible

Si le salaire brut est inférieur à **10% du plancher** (55 000 GNF), aucune cotisation CNSS n'est prélevée. Cela concerne les cas de congé sans solde ou d'absence prolongée.

## 3.3 Exemples de Calcul CNSS

### Exemple 1 : Salaire sous le plancher (400 000 GNF)

```
Salaire brut         : 400 000 GNF
Plancher CNSS        : 550 000 GNF
Assiette CNSS        : 550 000 GNF (on applique le plancher)

CNSS Employé (5%)    : 550 000 × 5% = 27 500 GNF
CNSS Employeur (18%) : 550 000 × 18% = 99 000 GNF
```

### Exemple 2 : Salaire entre plancher et plafond (1 500 000 GNF)

```
Salaire brut         : 1 500 000 GNF
Assiette CNSS        : 1 500 000 GNF (salaire réel)

CNSS Employé (5%)    : 1 500 000 × 5% = 75 000 GNF
CNSS Employeur (18%) : 1 500 000 × 18% = 270 000 GNF
```

### Exemple 3 : Salaire au-dessus du plafond (8 000 000 GNF)

```
Salaire brut         : 8 000 000 GNF
Plafond CNSS         : 2 500 000 GNF
Assiette CNSS        : 2 500 000 GNF (on applique le plafond)

CNSS Employé (5%)    : 2 500 000 × 5% = 125 000 GNF
CNSS Employeur (18%) : 2 500 000 × 18% = 450 000 GNF
```

---

# 4. RETENUE SUR TRAITEMENTS ET SALAIRES (RTS)

## 4.1 Principe de l'Impôt Progressif

La RTS est un **impôt progressif par tranches**. Chaque tranche de revenu est imposée à son propre taux. Ce n'est pas le revenu total qui est imposé au taux de la tranche la plus élevée.

## 4.2 Barème RTS - CGI 2022 (6 tranches)

| Tranche | Revenus mensuels | Taux | Impôt max de la tranche |
|---------|------------------|------|------------------------|
| 1 | 0 - 1 000 000 GNF | **0%** | 0 GNF |
| 2 | 1 000 001 - 3 000 000 GNF | **5%** | 100 000 GNF |
| 3 | 3 000 001 - 5 000 000 GNF | **8%** | 160 000 GNF |
| 4 | 5 000 001 - 10 000 000 GNF | **10%** | 500 000 GNF |
| 5 | 10 000 001 - 20 000 000 GNF | **15%** | 1 500 000 GNF |
| 6 | Au-delà de 20 000 000 GNF | **20%** | Variable |

> **IMPORTANT** : Ce barème à 6 tranches est le barème officiel du CGI 2022 pour les salaires.

## 4.3 Base Imposable RTS

> **⚠️ ATTENTION** : Les indemnités forfaitaires exonérées (transport, logement, repas) doivent être **retirées du brut** avant le calcul de la base imposable RTS (voir section 7).

```
Base Imposable RTS = Salaire Brut - Indemnités exonérées - CNSS Employé - Déductions
```

### Déductions Possibles

| Déduction | Montant | Condition |
|-----------|---------|-----------|
| Conjoint | 100 000 GNF | Marié(e) |
| Enfant à charge | 50 000 GNF/enfant | Max 4 enfants |
| Abattement professionnel | 5% de la base | Plafonné à 1 000 000 GNF |

## 4.4 Méthode de Calcul RTS

### Algorithme

```
Pour chaque tranche (de la plus basse à la plus haute) :
    Si Base_Imposable >= Borne_Inférieure :
        Montant_dans_tranche = MIN(Base_Imposable, Borne_Supérieure) - Borne_Inférieure + 1
        Impôt_tranche = Montant_dans_tranche × Taux
        RTS_Total += Impôt_tranche
```

### Exemple Détaillé : Base imposable de 7 875 000 GNF

```
┌────────────────────────────────────────────────────────────────────────┐
│ CALCUL RTS DÉTAILLÉ - Base imposable : 7 875 000 GNF                   │
│ Conforme CGI 2022 (6 tranches)                                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│ Tranche 1 (0% sur 0 - 1 000 000 GNF)                                  │
│   Montant : 1 000 000 GNF × 0% = 0 GNF                                │
│                                                                        │
│ Tranche 2 (5% sur 1 000 001 - 3 000 000 GNF)                          │
│   Montant : 2 000 000 GNF × 5% = 100 000 GNF                          │
│                                                                        │
│ Tranche 3 (8% sur 3 000 001 - 5 000 000 GNF)                          │
│   Montant : 2 000 000 GNF × 8% = 160 000 GNF                          │
│                                                                        │
│ Tranche 4 (10% sur 5 000 001 - 7 875 000 GNF)                         │
│   Montant : 2 875 000 GNF × 10% = 287 500 GNF                         │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│ TOTAL RTS = 0 + 100 000 + 160 000 + 287 500 = 547 500 GNF             │
└────────────────────────────────────────────────────────────────────────┘
```

---

# 5. CHARGES PATRONALES

## 5.1 Récapitulatif des Charges Patronales

| Charge | Taux | Assiette | Description |
|--------|------|----------|-------------|
| **CNSS Employeur** | **18%** | Assiette CNSS (550K - 2,5M) | Cotisation sociale |
| **Versement Forfaitaire (VF)** | **6%** | Salaire brut total | Impôt sur la masse salariale |
| **Taxe d'Apprentissage (TA)** | **1,5%** | Salaire brut total | Formation professionnelle |
| **Contribution ONFPP** | **1,5%** | Salaire brut total | 0,5% apprentissage + 1% perfectionnement |
| **TOTAL** | **27%** | Variable | - |

## 5.2 Différence entre Assiettes

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ASSIETTES DE CALCUL                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  CNSS Employeur (18%)                                               │
│  └── Assiette = MIN(MAX(Brut, 550K), 2,5M)  ← Plafonnée             │
│                                                                      │
│  Versement Forfaitaire (6%)                                         │
│  └── Assiette = Salaire Brut Total  ← Non plafonnée                 │
│                                                                      │
│  Taxe d'Apprentissage (1,5%)                                        │
│  └── Assiette = Salaire Brut Total  ← Non plafonnée                 │
│                                                                      │
│  Contribution ONFPP (1,5%)                                          │
│  └── Assiette = Salaire Brut Total  ← Non plafonnée                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 5.3 Exemple de Calcul des Charges Patronales

### Salaire brut : 8 000 000 GNF

```
┌─────────────────────────────────────────────────────────────────────┐
│ CHARGES PATRONALES - Salaire brut : 8 000 000 GNF                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ 1. CNSS Employeur (18%)                                             │
│    Assiette CNSS = 2 500 000 GNF (plafond)                          │
│    CNSS Employeur = 2 500 000 × 18% = 450 000 GNF                   │
│                                                                      │
│ 2. Versement Forfaitaire (6%)                                       │
│    Assiette VF = 8 000 000 GNF (brut total)                         │
│    VF = 8 000 000 × 6% = 480 000 GNF                                │
│                                                                      │
│ 3. Taxe d'Apprentissage (1,5%)                                      │
│    Assiette TA = 8 000 000 GNF (brut total)                         │
│    TA = 8 000 000 × 1,5% = 120 000 GNF                              │
│                                                                      │
│ 4. Contribution ONFPP (1,5%)                                        │
│    ONFPP = 8 000 000 × 1,5% = 120 000 GNF                           │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│ TOTAL CHARGES PATRONALES = 450 000 + 480 000 + 120 000 + 120 000    │
│                          = 1 170 000 GNF                            │
│                                                                      │
│ COÛT TOTAL EMPLOYEUR = 8 000 000 + 1 170 000 = 9 170 000 GNF        │
└─────────────────────────────────────────────────────────────────────┘
```

---

# 6. EXONÉRATIONS ET CAS PARTICULIERS

## 6.1 Exonération RTS pour Stagiaires et Apprentis

### Conditions d'Éligibilité

| Critère | Condition |
|---------|-----------|
| Type de contrat | Stage ou Apprentissage |
| Durée maximale | 12 mois depuis le début du contrat |
| Indemnité maximale | ≤ 1 200 000 GNF/mois |

### Règle de Calcul

```
SI (type_contrat IN ['stage', 'apprentissage'])
   ET (durée_contrat ≤ 12 mois)
   ET (indemnité ≤ 1 200 000 GNF)
ALORS
   RTS = 0 GNF (exonéré)
SINON
   RTS = calcul normal selon barème
```

### Exemple : Stagiaire avec indemnité de 900 000 GNF

```
Type de contrat     : Stage
Durée               : 6 mois (≤ 12 mois ✓)
Indemnité           : 900 000 GNF (≤ 1 200 000 GNF ✓)

→ EXONÉRÉ de RTS

Calcul :
  Salaire brut      : 900 000 GNF
  CNSS Employé      : 550 000 × 5% = 27 500 GNF (plancher appliqué)
  RTS               : 0 GNF (exonéré)
  Net à payer       : 900 000 - 27 500 = 872 500 GNF
```

---

# 7. PLAFOND 25% DES INDEMNITÉS FORFAITAIRES

## 7.1 Principe Fondamental

Les indemnités forfaitaires (logement, transport, panier) sont **exonérées de RTS** dans la limite de **25% du salaire brut**. L'excédent au-delà de ce plafond est **réintégré dans la base imposable RTS**.

> **IMPORTANT** : Cette règle est cruciale pour éviter les redressements fiscaux lors des contrôles de la DNI.

## 7.2 Indemnités Concernées

| Type d'indemnité | Codes rubriques | Exonération |
|------------------|-----------------|-------------|
| Transport | PRIME_TRANSPORT, ALLOC_TRANSPORT | ≤ 25% du brut |
| Logement | ALLOC_LOGEMENT, IND_LOGEMENT | ≤ 25% du brut |
| Repas/Panier | IND_REPAS, PRIME_PANIER | ≤ 25% du brut |

## 7.3 Formule de Calcul Détaillée

### Définitions

```
Salaire brut = Salaire de base + Primes/Indemnités
Plafond exonéré = 25% × Salaire brut
```

### Vérification Mathématique

Pour que les primes soient exactement au plafond de 25% du brut :

```
Primes = 25% × (Salaire de base + Primes)
Primes = 0.25 × Salaire de base + 0.25 × Primes
0.75 × Primes = 0.25 × Salaire de base
Primes = (0.25 / 0.75) × Salaire de base
Primes = 33.33% × Salaire de base
```

> **RÈGLE PRATIQUE** : Pour respecter le plafond de 25% du brut, les indemnités forfaitaires ne doivent pas dépasser **~33% du salaire de base**.

### Algorithme de Calcul

```
1. Calculer le salaire brut = Salaire de base + Indemnités forfaitaires
2. Calculer le plafond = Salaire brut × 25%
3. Comparer les indemnités au plafond :
   - Si Indemnités ≤ Plafond → Tout est exonéré
   - Si Indemnités > Plafond → Excédent réintégré dans base RTS
4. Excédent = Indemnités - Plafond
5. Base imposable RTS = Brut - CNSS + Excédent
```

## 7.4 Exemples Concrets

### Exemple 1 : Conforme (pas de dépassement)

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    EXEMPLE 1 : CONFORME                                ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ Salaire de base           : 3 000 000 GNF                             ║
║ Indemnités forfaitaires   : 1 000 000 GNF                             ║
║   - Transport             : 400 000 GNF                               ║
║   - Logement              : 400 000 GNF                               ║
║   - Panier                : 200 000 GNF                               ║
║ ─────────────────────────────────────────                             ║
║ Salaire brut              : 4 000 000 GNF                             ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ VÉRIFICATION PLAFOND 25%                                              ║
║ ────────────────────────                                              ║
║ Plafond = 4 000 000 × 25% = 1 000 000 GNF                             ║
║ Indemnités = 1 000 000 GNF                                            ║
║                                                                        ║
║ Ratio indemnités/brut = 1 000 000 / 4 000 000 = 25% ✓                 ║
║ Ratio indemnités/base = 1 000 000 / 3 000 000 = 33.33% ✓              ║
║                                                                        ║
║ → CONFORME : Indemnités = Plafond                                     ║
║ → Dépassement = 0 GNF                                                 ║
║ → Aucune réintégration nécessaire                                     ║
║                                                                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Exemple 2 : Avec dépassement (réintégration nécessaire)

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    EXEMPLE 2 : DÉPASSEMENT                             ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ Salaire de base           : 3 000 000 GNF                             ║
║ Indemnités forfaitaires   : 1 500 000 GNF                             ║
║   - Transport             : 600 000 GNF                               ║
║   - Logement              : 600 000 GNF                               ║
║   - Panier                : 300 000 GNF                               ║
║ ─────────────────────────────────────────                             ║
║ Salaire brut              : 4 500 000 GNF                             ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ VÉRIFICATION PLAFOND 25%                                              ║
║ ────────────────────────                                              ║
║ Plafond = 4 500 000 × 25% = 1 125 000 GNF                             ║
║ Indemnités = 1 500 000 GNF                                            ║
║                                                                        ║
║ Ratio indemnités/brut = 1 500 000 / 4 500 000 = 33.33% ⚠️             ║
║ Ratio indemnités/base = 1 500 000 / 3 000 000 = 50% ⚠️                ║
║                                                                        ║
║ → DÉPASSEMENT : Indemnités > Plafond                                  ║
║ → Excédent = 1 500 000 - 1 125 000 = 375 000 GNF                      ║
║ → 375 000 GNF réintégrés dans la base imposable RTS                   ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ IMPACT SUR LE CALCUL RTS                                              ║
║ ────────────────────────                                              ║
║ CNSS Employé = 2 500 000 × 5% = 125 000 GNF (plafond CNSS)            ║
║                                                                        ║
║ Base imposable SANS réintégration :                                   ║
║   = 4 500 000 - 125 000 = 4 375 000 GNF                               ║
║                                                                        ║
║ Base imposable AVEC réintégration :                                   ║
║   = 4 500 000 - 125 000 + 375 000 = 4 750 000 GNF                     ║
║                                                                        ║
║ Différence de RTS (environ) : +30 000 GNF                             ║
║                                                                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Exemple 3 : Calcul du seuil optimal

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    CALCUL DU SEUIL OPTIMAL                             ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ Question : Pour un salaire de base de 3 000 000 GNF, quel est le      ║
║            montant maximum d'indemnités forfaitaires exonérées ?      ║
║                                                                        ║
║ Formule : Primes_max = 33.33% × Salaire de base                       ║
║                                                                        ║
║ Calcul :                                                              ║
║   Primes_max = 3 000 000 × 33.33% = 999 900 GNF ≈ 1 000 000 GNF       ║
║                                                                        ║
║ Vérification :                                                        ║
║   Brut = 3 000 000 + 1 000 000 = 4 000 000 GNF                        ║
║   Plafond 25% = 4 000 000 × 25% = 1 000 000 GNF                       ║
║   Indemnités = 1 000 000 GNF = Plafond ✓                              ║
║                                                                        ║
║ → Pour un salaire de base de 3 000 000 GNF, les indemnités            ║
║   forfaitaires ne doivent pas dépasser 1 000 000 GNF                  ║
║                                                                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 7.5 Tableau de Référence Rapide

| Salaire de base | Primes max (33.33%) | Brut résultant | Plafond 25% |
|-----------------|---------------------|----------------|-------------|
| 1 000 000 GNF | 333 300 GNF | 1 333 300 GNF | 333 325 GNF |
| 2 000 000 GNF | 666 600 GNF | 2 666 600 GNF | 666 650 GNF |
| 3 000 000 GNF | 999 900 GNF | 3 999 900 GNF | 999 975 GNF |
| 4 000 000 GNF | 1 333 200 GNF | 5 333 200 GNF | 1 333 300 GNF |
| 5 000 000 GNF | 1 666 500 GNF | 6 666 500 GNF | 1 666 625 GNF |

---

# 8. INDEMNITÉS DE LICENCIEMENT

## 8.1 Cadre Légal

Selon le Code du Travail guinéen, tout salarié licencié (hors faute lourde) a droit à une indemnité de licenciement calculée en fonction de son ancienneté.

## 8.2 Barème Légal

| Ancienneté | Taux par année |
|------------|----------------|
| 1 à 5 ans | 25% du salaire mensuel moyen |
| 6 à 10 ans | 30% du salaire mensuel moyen |
| Au-delà de 10 ans | 40% du salaire mensuel moyen |

## 8.3 Formule de Calcul

```
Indemnité = Σ (Années dans tranche × Taux × Salaire mensuel moyen)

Salaire mensuel moyen = Moyenne des 12 derniers mois (ou durée du contrat si < 12 mois)
```

## 8.4 Exemple de Calcul

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    INDEMNITÉ DE LICENCIEMENT                           ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ Employé : M. Diallo                                                   ║
║ Ancienneté : 12 ans et 6 mois                                         ║
║ Salaire mensuel moyen : 2 500 000 GNF                                 ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ CALCUL PAR TRANCHES                                                   ║
║ ───────────────────                                                   ║
║                                                                        ║
║ Tranche 1 (1-5 ans) : 5 ans × 25% × 2 500 000                         ║
║   = 5 × 0.25 × 2 500 000 = 3 125 000 GNF                              ║
║                                                                        ║
║ Tranche 2 (6-10 ans) : 5 ans × 30% × 2 500 000                        ║
║   = 5 × 0.30 × 2 500 000 = 3 750 000 GNF                              ║
║                                                                        ║
║ Tranche 3 (11-12.5 ans) : 2.5 ans × 40% × 2 500 000                   ║
║   = 2.5 × 0.40 × 2 500 000 = 2 500 000 GNF                            ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ TOTAL INDEMNITÉ = 3 125 000 + 3 750 000 + 2 500 000                   ║
║                 = 9 375 000 GNF                                       ║
║                                                                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

# 9. PRÉAVIS ET INDEMNITÉS COMPENSATRICES

## 9.1 Durée du Préavis

| Catégorie | Ancienneté < 1 an | Ancienneté ≥ 1 an |
|-----------|-------------------|-------------------|
| Ouvriers/Employés | 15 jours | 1 mois |
| Agents de maîtrise | 1 mois | 2 mois |
| Cadres | 1 mois | 3 mois |

## 9.2 Indemnité Compensatrice de Préavis

Si l'employeur dispense le salarié d'effectuer son préavis, il doit lui verser une indemnité compensatrice.

```
Indemnité compensatrice = Salaire mensuel × Nombre de mois de préavis
```

## 9.3 Exemple

```
Cadre avec 5 ans d'ancienneté, salaire 4 000 000 GNF
Préavis dû : 3 mois
Indemnité compensatrice = 4 000 000 × 3 = 12 000 000 GNF
```

---

# 10. CONGÉ MATERNITÉ

## 10.1 Durée Légale

| Période | Durée |
|---------|-------|
| Congé prénatal | 6 semaines avant accouchement |
| Congé postnatal | 8 semaines après accouchement |
| **Total** | **14 semaines** |

## 10.2 Prolongation pour Maladie

Selon l'Article 153 du Code du Travail :

| Situation | Prolongation |
|-----------|-------------|
| Maladie liée à la grossesse ou l'accouchement | **+21 jours** (3 semaines) |
| Congé non payé optionnel | Jusqu'à **9 mois** supplémentaires |

> **Note** : La prolongation de 21 jours nécessite un certificat médical justifiant la maladie.

## 10.3 Indemnités Journalières CNSS

Pendant le congé maternité, la salariée perçoit des indemnités journalières versées par la CNSS.

```
Indemnité journalière = Salaire journalier moyen des 3 derniers mois
Durée normale = 98 jours (14 semaines)
Durée avec prolongation = 119 jours (14 semaines + 21 jours)
```

## 10.4 Conditions d'Éligibilité

- Être immatriculée à la CNSS
- Avoir cotisé au moins 6 mois dans les 12 mois précédant l'accouchement
- Cesser toute activité salariée pendant le congé

## 10.5 Protection de l'Emploi

- Interdiction de licenciement pendant le congé maternité
- Garantie de retrouver son poste ou un poste équivalent
- Maintien de l'ancienneté pendant le congé

---

# 11. ALLOCATIONS FAMILIALES CNSS

## 11.1 Conditions d'Attribution

| Critère | Condition |
|---------|-----------|
| Enfants à charge | Âge < 18 ans (ou 21 ans si étudiant) |
| Cotisations | Minimum 6 mois de cotisation |
| Limite | Maximum 6 enfants |

## 11.2 Montant des Allocations

```
Allocation mensuelle par enfant = Montant fixé par décret CNSS
(Généralement entre 5 000 et 10 000 GNF par enfant)
```

## 11.3 Procédure de Demande

1. Fournir les actes de naissance des enfants
2. Certificat de scolarité pour les enfants > 18 ans
3. Déclaration sur l'honneur de prise en charge

---

# 12. ACCIDENTS DU TRAVAIL

## 12.1 Définition

Est considéré comme accident du travail :
- Accident survenu par le fait ou à l'occasion du travail
- Accident de trajet (domicile-travail)

## 12.2 Indemnités

| Type | Calcul |
|------|--------|
| Incapacité temporaire | 100% du salaire pendant l'arrêt |
| Incapacité permanente partielle | Rente selon taux d'incapacité |
| Incapacité permanente totale | Rente = 85% du salaire |
| Décès | Rente aux ayants droit |

## 12.3 Déclaration Obligatoire

L'employeur doit déclarer tout accident du travail à la CNSS dans les **48 heures**.

---

# 13. JOURS FÉRIÉS LÉGAUX

## 13.1 Liste des Jours Fériés en Guinée

| Date | Jour férié | Type |
|------|------------|------|
| 1er janvier | Jour de l'An | Fixe |
| 2 octobre | Fête de l'Indépendance | Fixe |
| 1er mai | Fête du Travail | Fixe |
| 25 décembre | Noël | Fixe |
| Variable | Lundi de Pâques | Mobile |
| Variable | Ascension | Mobile |
| Variable | Aïd el-Fitr (Korité) | Mobile |
| Variable | Aïd el-Adha (Tabaski) | Mobile |
| Variable | Mawlid (Maouloud) | Mobile |

## 13.2 Rémunération des Jours Fériés

- **Jour férié non travaillé** : Maintien du salaire
- **Jour férié travaillé** : Majoration de 100% (double salaire)

## 13.3 Commande de Génération

```bash
python manage.py generer_feries_guinee --annee 2025
```

---

# 14. EXEMPLES DE CALCUL COMPLETS

## 14.1 Exemple 1 : Cadre Supérieur (8 000 000 GNF)

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    BULLETIN DE PAIE - EXEMPLE 1                        ║
║                    Cadre Supérieur                                     ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ DONNÉES D'ENTRÉE                                                       ║
║ ────────────────                                                       ║
║ Salaire de base           : 7 500 000 GNF                             ║
║ Prime de responsabilité   : 500 000 GNF                               ║
║ ─────────────────────────────────────────                             ║
║ SALAIRE BRUT              : 8 000 000 GNF                             ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ ÉTAPE 1 : CALCUL CNSS                                                 ║
║ ─────────────────────                                                 ║
║ Assiette CNSS = MIN(8 000 000, 2 500 000) = 2 500 000 GNF (plafond)   ║
║ CNSS Employé = 2 500 000 × 5% = 125 000 GNF                           ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ ÉTAPE 2 : CALCUL BASE IMPOSABLE RTS                                   ║
║ ───────────────────────────────────                                   ║
║ Base imposable = Brut - CNSS Employé                                  ║
║                = 8 000 000 - 125 000 = 7 875 000 GNF                  ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ ÉTAPE 3 : CALCUL RTS (BARÈME PROGRESSIF)                              ║
║ ────────────────────────────────────────                              ║
║                                                                        ║
║ Tranche 1 : 0 - 1 000 000 GNF × 0%                                    ║
║           = 1 000 000 × 0% = 0 GNF                                    ║
║                                                                        ║
║ Tranche 2 : 1 000 001 - 3 000 000 GNF × 5%                            ║
║           = 2 000 000 × 5% = 100 000 GNF                              ║
║                                                                        ║
║ Tranche 3 : 3 000 001 - 5 000 000 GNF × 8%                            ║
║           = 2 000 000 × 8% = 160 000 GNF                              ║
║                                                                        ║
║ Tranche 4 : 5 000 001 - 7 875 000 GNF × 10%                           ║
║           = 2 875 000 × 10% = 287 500 GNF                             ║
║                                                                        ║
║ TOTAL RTS = 0 + 100 000 + 160 000 + 287 500 = 547 500 GNF                       ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ ÉTAPE 4 : CALCUL NET À PAYER                                          ║
║ ────────────────────────────                                          ║
║ Total retenues = CNSS + RTS = 125 000 + 547 500 = 672 500 GNF         ║
║ NET À PAYER = 8 000 000 - 672 500 = 7 327 500 GNF                     ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ CHARGES PATRONALES (non visibles sur le bulletin)                     ║
║ ─────────────────────────────────────────────────                     ║
║ CNSS Employeur    : 2 500 000 × 18% = 450 000 GNF                     ║
║ Versement Forfait.: 8 000 000 × 6%  = 480 000 GNF                     ║
║ Taxe Apprentissage: 8 000 000 × 1,5%= 120 000 GNF                     ║
║ Contribution ONFPP: 8 000 000 × 1,5%= 120 000 GNF                     ║
║ ─────────────────────────────────────────────────                     ║
║ TOTAL CHARGES     : 1 170 000 GNF                                     ║
║                                                                        ║
║ COÛT TOTAL EMPLOYEUR : 8 000 000 + 1 170 000 = 9 170 000 GNF          ║
║                                                                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 7.2 Exemple 2 : Employé Standard (1 500 000 GNF)

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    BULLETIN DE PAIE - EXEMPLE 2                        ║
║                    Employé Standard                                    ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ DONNÉES D'ENTRÉE                                                       ║
║ Salaire de base           : 1 200 000 GNF                             ║
║ Prime de transport        : 200 000 GNF (exonérée RTS)                ║
║ Prime d'ancienneté        : 100 000 GNF                               ║
║ ─────────────────────────────────────────                             ║
║ SALAIRE BRUT              : 1 500 000 GNF                             ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ CALCUL CNSS                                                           ║
║ Assiette CNSS = 1 500 000 GNF (entre plancher et plafond)             ║
║ CNSS Employé = 1 500 000 × 5% = 75 000 GNF                            ║
║                                                                        ║
║ CALCUL RTS (avec exclusion indemnité transport)                       ║
║ Plafond 25% = 1 500 000 × 25% = 375 000 GNF                           ║
║ Transport (200 000) < Plafond (375 000) → Entièrement exonéré         ║
║                                                                        ║
║ Base imposable = Brut - Transport - CNSS                              ║
║                = 1 500 000 - 200 000 - 75 000 = 1 225 000 GNF         ║
║                                                                        ║
║ Tranche 1 : 1 000 000 × 0% = 0 GNF                                    ║
║ Tranche 2 : 225 000 × 5% = 11 250 GNF                                 ║
║ TOTAL RTS = 11 250 GNF                                                ║
║                                                                        ║
║ NET À PAYER = 1 500 000 - 75 000 - 11 250 = 1 413 750 GNF             ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ CHARGES PATRONALES                                                    ║
║ CNSS Employeur    : 1 500 000 × 18% = 270 000 GNF                     ║
║ Versement Forfait.: 1 500 000 × 6%  = 90 000 GNF                      ║
║ Taxe Apprentissage: 1 500 000 × 1,5%= 22 500 GNF                      ║
║ TOTAL CHARGES     : 382 500 GNF                                       ║
║                                                                        ║
║ COÛT TOTAL EMPLOYEUR : 1 882 500 GNF                                  ║
║                                                                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 7.3 Exemple 3 : Stagiaire Exonéré (800 000 GNF)

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    BULLETIN DE PAIE - EXEMPLE 3                        ║
║                    Stagiaire (Exonéré RTS)                            ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ DONNÉES D'ENTRÉE                                                       ║
║ Type de contrat           : Stage                                     ║
║ Durée du stage            : 6 mois (≤ 12 mois ✓)                      ║
║ Indemnité de stage        : 800 000 GNF (≤ 1 200 000 GNF ✓)           ║
║                                                                        ║
║ → ÉLIGIBLE À L'EXONÉRATION RTS                                        ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ CALCUL CNSS                                                           ║
║ Assiette CNSS = 550 000 GNF (plancher appliqué car 800K < 550K ✗)     ║
║ Correction : 800 000 > 550 000, donc Assiette = 800 000 GNF           ║
║ CNSS Employé = 800 000 × 5% = 40 000 GNF                              ║
║                                                                        ║
║ CALCUL RTS                                                            ║
║ RTS = 0 GNF (EXONÉRÉ - Stagiaire éligible)                            ║
║                                                                        ║
║ NET À PAYER = 800 000 - 40 000 = 760 000 GNF                          ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ CHARGES PATRONALES                                                    ║
║ CNSS Employeur    : 800 000 × 18% = 144 000 GNF                       ║
║ Versement Forfait.: 800 000 × 6%  = 48 000 GNF                        ║
║ Taxe Apprentissage: 800 000 × 1,5%= 12 000 GNF                        ║
║ TOTAL CHARGES     : 204 000 GNF                                       ║
║                                                                        ║
║ COÛT TOTAL EMPLOYEUR : 1 004 000 GNF                                  ║
║                                                                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 7.4 Exemple 4 : Employé au SMIG (550 000 GNF)

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    BULLETIN DE PAIE - EXEMPLE 4                        ║
║                    Employé au SMIG                                     ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ DONNÉES D'ENTRÉE                                                       ║
║ Salaire de base (SMIG)    : 550 000 GNF                               ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ CALCUL CNSS                                                           ║
║ Assiette CNSS = 550 000 GNF (= plancher)                              ║
║ CNSS Employé = 550 000 × 5% = 27 500 GNF                              ║
║                                                                        ║
║ CALCUL RTS                                                            ║
║ Base imposable = 550 000 - 27 500 = 522 500 GNF                       ║
║ Tranche 1 : 522 500 × 0% = 0 GNF (< 1 000 000 GNF)                    ║
║ TOTAL RTS = 0 GNF                                                     ║
║                                                                        ║
║ NET À PAYER = 550 000 - 27 500 - 0 = 522 500 GNF                      ║
║                                                                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║ CHARGES PATRONALES                                                    ║
║ CNSS Employeur    : 550 000 × 18% = 99 000 GNF                        ║
║ Versement Forfait.: 550 000 × 6%  = 33 000 GNF                        ║
║ Taxe Apprentissage: 550 000 × 1,5%= 8 250 GNF                         ║
║ TOTAL CHARGES     : 140 250 GNF                                       ║
║                                                                        ║
║ COÛT TOTAL EMPLOYEUR : 690 250 GNF                                    ║
║                                                                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

# 15. DÉCLARATIONS SOCIALES

## 15.1 Types de Déclarations

| Déclaration | Organisme | Contenu | Échéance |
|-------------|-----------|---------|----------|
| CNSS | Caisse Nationale de Sécurité Sociale | Cotisations employé + employeur | 15 du mois suivant |
| RTS | Direction Nationale des Impôts | Retenue sur salaires | 15 du mois suivant |
| VF | Direction Nationale des Impôts | Versement Forfaitaire 6% | 15 du mois suivant |
| DMU | Direction Nationale des Impôts | Déclaration Mensuelle Unique | 15 du mois suivant |

## 15.2 Calcul des Montants à Déclarer

### Déclaration CNSS

```
Total CNSS à verser = Σ (CNSS Employé + CNSS Employeur) pour tous les employés

Exemple pour 10 employés avec masse salariale de 20 000 000 GNF :
- Si tous les salaires sont entre plancher et plafond :
  CNSS Employé total  = 20 000 000 × 5%  = 1 000 000 GNF
  CNSS Employeur total = 20 000 000 × 18% = 3 600 000 GNF
  TOTAL À VERSER = 4 600 000 GNF
```

### Déclaration RTS

```
Total RTS à verser = Σ RTS de tous les employés
```

### Déclaration VF

```
Total VF à verser = Masse salariale brute × 6%
```

---

# 16. ALERTES ET ÉCHÉANCES

## 16.1 Système d'Alertes

L'application génère automatiquement des alertes pour les échéances de déclarations :

| Jours avant échéance | Niveau | Statut |
|---------------------|--------|--------|
| > 5 jours | ℹ️ Information | À venir |
| 3-5 jours | ⚠️ Avertissement | À venir |
| 1-3 jours | ⚠️ Avertissement | Urgent |
| ≤ 1 jour | 🚨 Danger | Urgent |
| Dépassé | 🚨 Danger | En retard |

## 16.2 Pénalités de Retard

| Déclaration | Pénalité |
|-------------|----------|
| CNSS | 5% par mois de retard |
| RTS/VF | 100% du montant dû |

## 16.3 Commande de Génération des Alertes

```bash
# Générer les alertes pour le mois en cours
python manage.py generer_alertes_echeances

# Générer pour un mois spécifique
python manage.py generer_alertes_echeances --mois 12 --annee 2025

# Actualiser toutes les alertes existantes
python manage.py generer_alertes_echeances --actualiser
```

---

# 17. COMMANDES DE GESTION

## 17.1 Commandes Disponibles

| Commande | Description |
|----------|-------------|
| `python manage.py init_paie_guinee` | Initialise les constantes et barèmes |
| `python manage.py update_bareme_rts` | Met à jour le barème RTS |
| `python manage.py update_cnss_constants` | Met à jour les constantes CNSS |
| `python manage.py recalculer_bulletins` | Recalcule les bulletins de paie |
| `python manage.py test_calculs_paie` | Teste l'exactitude des calculs |
| `python manage.py generer_alertes_echeances` | Génère les alertes d'échéances |
| `python manage.py generer_feries_guinee` | Génère les jours fériés légaux de Guinée |

## 17.2 Exemples d'Utilisation

### Recalculer les bulletins d'une période

```bash
# Simulation (dry-run)
python manage.py recalculer_bulletins --periode 12 --annee 2025 --dry-run

# Application réelle
python manage.py recalculer_bulletins --periode 12 --annee 2025
```

### Tester les calculs

```bash
python manage.py test_calculs_paie
```

Résultat attendu :
```
======================================================================
TESTS DE VÉRIFICATION DES CALCULS DE PAIE - GUINÉE
======================================================================
📊 TEST 1: CALCUL CNSS (Plancher/Plafond) - 6/6 ✓
📊 TEST 2: BARÈME RTS CGI 2022 (5 tranches) - 10/10 ✓
📊 TEST 3: CHARGES PATRONALES (CNSS 18% + VF 6% + TA 1,5%) - 3/3 ✓
📊 TEST 4: EXEMPLE COMPLET DU MANUEL (8 000 000 GNF) - 8/8 ✓
📊 TEST 5: EXONÉRATION RTS STAGIAIRES/APPRENTIS - 9/9 ✓
📊 TEST 6: PLAFOND 25% INDEMNITÉS FORFAITAIRES - 6/6 ✓
======================================================================
✅ TOUS LES TESTS RÉUSSIS: 42/42
======================================================================
```

---

# ANNEXES

## A. Tableau Récapitulatif des Taux

| Élément | Taux | Assiette |
|---------|------|----------|
| CNSS Employé | 5% | Plafonnée (550K - 2,5M) |
| CNSS Employeur | 18% | Plafonnée (550K - 2,5M) |
| Versement Forfaitaire | 6% | Brut total |
| Taxe d'Apprentissage | 1,5% | Brut total (CGI 2022) |
| Contribution ONFPP | 1,5% | Brut total |
| RTS Tranche 1 | 0% | 0 - 1M |
| RTS Tranche 2 | 5% | 1M - 5M |
| RTS Tranche 3 | 10% | 5M - 10M |
| RTS Tranche 4 | 15% | 10M - 20M |
| RTS Tranche 5 | 20% | > 20M |

## B. Contacts Utiles

| Organisme | Contact |
|-----------|---------|
| CNSS | www.cnss.gov.gn |
| DNI | www.dni.gov.gn |
| Ministère du Travail | www.travail.gov.gn |

## C. Historique des Versions

| Version | Date | Modifications |
|---------|------|---------------|
| 1.0 | Nov 2025 | Version initiale |
| 1.1 | Déc 2025 | Correction barème RTS, ajout VF/TA |
| 2.0 | Déc 2025 | Exonérations stagiaires, plafond 25%, alertes |
| 3.0 | Déc 2025 | Formule correcte plafond 25% (33% base), indemnités licenciement, préavis, congé maternité, allocations familiales, accidents travail, jours fériés |
| 3.1 | Déc 2025 | Heures supplémentaires, congés payés avec majorations ancienneté, prolongation maternité +21 jours |
| 3.2 | Jan 2026 | Correction barème RTS (5 tranches sans 8%), TA 1,5% (CGI 2022), ajout ONFPP 1,5% |

---

**Document généré par Gestionnaire RH Guinée**
**Version 3.1 - Décembre 2025**
**www.guineerh.space**
