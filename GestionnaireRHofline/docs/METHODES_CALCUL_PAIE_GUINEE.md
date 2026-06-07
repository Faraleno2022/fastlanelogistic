# 📊 Méthodes de Calcul du Bulletin de Paie - Guinée

> **Version**: 1.1 (Corrigée)  
> **Dernière mise à jour**: Janvier 2026  
> **Référence légale**: Code Général des Impôts 2022 + Code du Travail guinéen

---

## Table des matières

1. [Structure générale du calcul](#1-structure-générale-du-calcul)
2. [CNSS - Caisse Nationale de Sécurité Sociale](#2-cnss---caisse-nationale-de-sécurité-sociale)
3. [RTS - Retenue à la Source](#3-rts---retenue-à-la-source)
4. [Heures Supplémentaires](#4-heures-supplémentaires)
5. [Indemnités Forfaitaires (Plafond 25%)](#5-indemnités-forfaitaires-plafond-25)
6. [Charges Patronales](#6-charges-patronales)
7. [Congés Payés](#7-congés-payés)
8. [Éléments du Bulletin](#8-éléments-du-bulletin)
9. [Données Requises](#9-données-requises-pour-le-calcul)
10. [Exemple de Calcul Complet (Corrigé)](#10-exemple-de-calcul-complet-corrigé)

---

## 1. Structure Générale du Calcul

```
┌─────────────────────────────────────────────────────────────────┐
│  SALAIRE BRUT                                                   │
│  = Salaire de base + Primes + Indemnités + Heures Sup           │
│  - Retenues absences non payées                                 │
├─────────────────────────────────────────────────────────────────┤
│  COTISATIONS SOCIALES (CNSS)                                    │
│  Employé: 5% (sur base plafonnée)                               │
│  Employeur: 18% (sur base plafonnée)                            │
├─────────────────────────────────────────────────────────────────┤
│  RTS (Retenue à la Source)                                      │
│  ⚠️ ATTENTION: Calculé sur (Brut - Indemnités exonérées)        │
│  puis: - CNSS - Déductions familiales - Abattement              │
├─────────────────────────────────────────────────────────────────┤
│  NET À PAYER                                                    │
│  = Brut - CNSS Employé - RTS - Autres retenues                  │
└─────────────────────────────────────────────────────────────────┘
```

### Ordre de calcul

1. Calculer le **temps de travail** (pointages, absences, congés)
2. Calculer les **gains** (salaire de base, primes, heures sup)
3. Appliquer les **retenues pour absences** non payées
4. Calculer le **salaire brut**
5. Calculer les **cotisations sociales** (CNSS)
6. **⚠️ Identifier les indemnités exonérées** (transport, logement, repas)
7. Calculer la **RTS** sur la base imposable corrigée
8. Calculer les **autres retenues** (avances, prêts, saisies)
9. Calculer le **net à payer**

---

## 2. CNSS - Caisse Nationale de Sécurité Sociale

### 2.1 Paramètres officiels

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| **Plancher (SMIG)** | 550 000 GNF | Assiette minimale de cotisation |
| **Plafond** | 2 500 000 GNF | Assiette maximale de cotisation |
| **Taux Employé** | 5% | Retenu sur le salaire |
| **Taux Employeur** | 18% | Charge patronale (non visible sur bulletin) |

### 2.2 Répartition du taux employeur (18%)

| Branche | Taux |
|---------|------|
| Prestations familiales | 6% |
| Accidents du travail / Maladies professionnelles | 4% |
| Retraite | 4% |
| Assurance maladie | 4% |
| **Total** | **18%** |

### 2.3 Formule de calcul

```python
# Étape 1: Déterminer la base CNSS
base_cnss = somme(éléments où rubrique.soumis_cnss == True)

# Étape 2: Appliquer plancher et plafond
PLANCHER = 550_000  # GNF
PLAFOND = 2_500_000  # GNF

if base_cnss < PLANCHER:
    base_plafonnee = PLANCHER  # On cotise au minimum sur le plancher
elif base_cnss > PLAFOND:
    base_plafonnee = PLAFOND   # On cotise au maximum sur le plafond
else:
    base_plafonnee = base_cnss  # On cotise sur le salaire réel

# Étape 3: Calculer les cotisations
cnss_employe = base_plafonnee × 5%
cnss_employeur = base_plafonnee × 18%
```

---

## 3. RTS - Retenue à la Source

### ⚠️ POINT CRUCIAL : Exclusion des indemnités exonérées

> **Le RTS ne se calcule PAS sur le brut total !**  
> Les indemnités forfaitaires exonérées (transport, logement, repas) doivent être **retirées** de la base avant le calcul RTS.

### 3.1 Barème progressif CGI 2022 (6 tranches)

| Tranche | De (GNF) | À (GNF) | Taux |
|---------|----------|---------|------|
| 1 | 0 | 1 000 000 | **0%** |
| 2 | 1 000 001 | 3 000 000 | **5%** |
| 3 | 3 000 001 | 5 000 000 | **8%** |
| 4 | 5 000 001 | 10 000 000 | **10%** |
| 5 | 10 000 001 | 20 000 000 | **15%** |
| 6 | > 20 000 000 | ∞ | **20%** |

### 3.2 Formule de calcul CORRIGÉE

```python
# ═══════════════════════════════════════════════════════════════
# ÉTAPE 1: Identifier les indemnités forfaitaires exonérées
# ═══════════════════════════════════════════════════════════════
indemnites_exonerees = transport + logement + repas

# Vérifier le plafond 25%
plafond_25 = brut × 25%
if indemnites_exonerees > plafond_25:
    # L'excédent est réintégré dans la base imposable
    montant_exonere = plafond_25
else:
    montant_exonere = indemnites_exonerees

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 2: Calculer la base imposable RTS
# ═══════════════════════════════════════════════════════════════
base_imposable = brut - montant_exonere

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 3: Déduire les cotisations CNSS
# ═══════════════════════════════════════════════════════════════
base_imposable -= cnss_employe

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 4: Appliquer les déductions familiales
# ═══════════════════════════════════════════════════════════════
if situation_matrimoniale == "marié":
    base_imposable -= 100_000  # Déduction conjoint

nb_enfants_deductibles = min(nombre_enfants, 4)
base_imposable -= nb_enfants_deductibles × 50_000

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 5: Appliquer l'abattement professionnel (5% plafonné)
# ═══════════════════════════════════════════════════════════════
abattement = min(base_imposable × 5%, 1_000_000)
base_nette = base_imposable - abattement

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 6: Calculer la RTS par tranches
# ═══════════════════════════════════════════════════════════════
rts_total = 0
reste = base_nette

for tranche in tranches:
    if reste <= 0:
        break
    montant_dans_tranche = min(reste, tranche.borne_sup - tranche.borne_inf)
    rts_tranche = montant_dans_tranche × tranche.taux
    rts_total += rts_tranche
    reste -= montant_dans_tranche
```

### 3.3 Déductions familiales

| Type | Montant | Condition |
|------|---------|-----------|
| **Conjoint** | 100 000 GNF | Situation matrimoniale = Marié(e) |
| **Enfant à charge** | 50 000 GNF/enfant | Maximum 4 enfants déductibles |

### 3.4 Exonérations RTS

| Catégorie | Conditions | Limite |
|-----------|------------|--------|
| **Indemnités forfaitaires** | Transport, logement, repas | ≤ 25% du brut |
| **Stagiaires** | Contrat de stage | ≤ 1 200 000 GNF/mois, max 12 mois |
| **Apprentis** | Contrat d'apprentissage | ≤ 1 200 000 GNF/mois, max 12 mois |
| **1ère tranche** | Tous salariés | ≤ 1 000 000 GNF (taux 0%) |

---

## 4. Heures Supplémentaires

### 4.1 Barème des majorations (Code du Travail Art. 221)

| Type d'heures | Majoration | Taux final | Quand |
|---------------|------------|------------|-------|
| **4 premières HS/semaine** | +30% | 130% | Jour ouvrable |
| **Au-delà 4 HS/semaine** | +60% | 160% | Jour ouvrable |
| **Heures de nuit** | +20% | 120% | 20h00 - 6h00 |
| **Jour férié (jour)** | +60% | 160% | Férié, 6h00-20h00 |
| **Jour férié (nuit)** | +100% | 200% | Férié, 20h00-6h00 |

### 4.2 Formule de calcul

```python
# Calculer le taux horaire de base
heures_mensuelles = 173.33  # 40h × 52 semaines ÷ 12 mois
taux_horaire = salaire_base / heures_mensuelles

# Calculer chaque type d'heures supplémentaires
montant_hs = (
    heures_30 × taux_horaire × 1.30 +
    heures_60 × taux_horaire × 1.60 +
    heures_nuit × taux_horaire × 1.20 +
    heures_ferie_jour × taux_horaire × 1.60 +
    heures_ferie_nuit × taux_horaire × 2.00
)
```

---

## 5. Indemnités Forfaitaires (Plafond 25%)

### 5.1 Règle essentielle

> **Les indemnités forfaitaires sont exonérées de RTS dans la limite de 25% du salaire brut.**  
> Au-delà de ce plafond, l'excédent est réintégré dans la base imposable RTS.

### 5.2 Rubriques concernées

- **Transport** : Prime de transport, Allocation transport
- **Logement** : Indemnité de logement, Allocation logement  
- **Repas** : Prime de panier, Indemnité de repas

### 5.3 Formule

```python
# Total des indemnités forfaitaires
total_indemnites = transport + logement + repas

# Plafond exonéré (25% du brut)
plafond_25 = brut × 25%

# Vérification
if total_indemnites <= plafond_25:
    # Entièrement exonérées
    montant_exonere = total_indemnites
    excedent_a_reintegrer = 0
else:
    # Partiellement exonérées
    montant_exonere = plafond_25
    excedent_a_reintegrer = total_indemnites - plafond_25
```

---

## 6. Charges Patronales

| Charge | Taux | Base de calcul |
|--------|------|----------------|
| **CNSS Employeur** | 18% | Base plafonnée (max 2 500 000 GNF) |
| **Versement Forfaitaire (VF)** | 6% | Brut total |
| **Taxe d'Apprentissage (TA)** | 1,5% | Brut total |
| **Contribution ONFPP** | 1,5% | Brut total |

```python
total_charges = cnss_employeur + vf + ta + onfpp
# Soit environ 25,5% à 27% du brut selon le plafond CNSS
```

---

## 7. Congés Payés

| Critère | Valeur |
|---------|--------|
| **Base mensuelle** | 1,5 jour ouvrable par mois |
| **Base annuelle** | 18 jours ouvrables par an |
| **Moins de 18 ans** | 2 jours par mois (24 jours/an) |
| **Bonus ancienneté** | +2 jours par tranche de 5 ans |

---

## 8. Éléments du Bulletin

### Gains (type_rubrique = 'gain')
- Salaire de base
- Prime d'ancienneté
- Prime de transport *(exonérée RTS)*
- Indemnité de logement *(exonérée RTS)*
- Prime de rendement
- Heures supplémentaires

### Retenues (type_rubrique = 'retenue')
- CNSS Employé (5%)
- RTS (barème progressif)
- Avances sur salaire
- Prêts / Saisies-arrêt

---

## 9. Données Requises pour le Calcul

### Employé
- **Salaire de base** (ElementSalaire)
- **Situation matrimoniale** (marié/célibataire)
- **Nombre d'enfants** (max 4 pour déductions)
- **Type de contrat** (CDI, CDD, Stage, Apprentissage)
- **Date d'embauche** (pour ancienneté)

### Période
- **Mois/Année** de paie
- **Jours ouvrables** du mois
- **Heures mensuelles** (173,33h standard)

---

## 10. Exemple de Calcul Complet (CORRIGÉ)

### Données de l'employé

```
Nom: Mamadou DIALLO
Salaire de base: 5 000 000 GNF
Prime transport: 500 000 GNF (exonérée RTS)
Prime logement: 800 000 GNF (exonérée RTS)
Situation: Marié, 2 enfants
Heures sup (60%): 10 heures
```

### Calcul détaillé

```
═══════════════════════════════════════════════════════════════════
                    BULLETIN DE PAIE - JANVIER 2026
═══════════════════════════════════════════════════════════════════

GAINS
───────────────────────────────────────────────────────────────────
Salaire de base                                    5 000 000 GNF
Prime de transport                                   500 000 GNF
Indemnité de logement                                800 000 GNF
Heures supplémentaires (10h × 28 846 × 160%)         461 538 GNF
───────────────────────────────────────────────────────────────────
SALAIRE BRUT                                       6 761 538 GNF


COTISATIONS SOCIALES (CNSS)
───────────────────────────────────────────────────────────────────
Base CNSS (plafonnée à 2 500 000):                 2 500 000 GNF
CNSS Salarié (5%)                                    125 000 GNF


RTS (RETENUE À LA SOURCE) - CALCUL CORRIGÉ
───────────────────────────────────────────────────────────────────

1. Identification des indemnités exonérées:
   Transport + Logement = 500 000 + 800 000 =      1 300 000 GNF
   Plafond 25% du brut = 6 761 538 × 25% =         1 690 385 GNF
   → Indemnités < Plafond ✅ Entièrement exonérées

2. Base imposable RTS:
   Brut - Indemnités exonérées:
   6 761 538 - 1 300 000 =                         5 461 538 GNF

3. Après CNSS employé:
   5 461 538 - 125 000 =                           5 336 538 GNF

4. Déductions familiales:
   - Conjoint:                                       100 000 GNF
   - Enfants (2 × 50 000):                           100 000 GNF
   Total déductions:                                 200 000 GNF

5. Abattement professionnel:
   5% × 5 336 538 = 266 827 GNF (< 1 000 000)        266 827 GNF

6. BASE NETTE IMPOSABLE:
   5 336 538 - 200 000 - 266 827 =                 4 869 711 GNF

7. Calcul RTS par tranches:
   ┌─────────────────────────────────────────────────────────────┐
   │ Tranche 1: 0 - 1 000 000 (0%)              =           0 GNF│
   │ Tranche 2: 1 000 000 - 3 000 000 (5%)      =     100 000 GNF│
   │ Tranche 3: 3 000 000 - 4 869 711 (8%)      =     149 577 GNF│
   └─────────────────────────────────────────────────────────────┘
───────────────────────────────────────────────────────────────────
RTS TOTAL                                            249 577 GNF


RÉCAPITULATIF
───────────────────────────────────────────────────────────────────
Salaire Brut                                       6 761 538 GNF
- CNSS Salarié (5%)                                  125 000 GNF
- RTS                                                249 577 GNF
═══════════════════════════════════════════════════════════════════
NET À PAYER                                        6 386 961 GNF
═══════════════════════════════════════════════════════════════════


CHARGES PATRONALES (Information)
───────────────────────────────────────────────────────────────────
CNSS Employeur (18% sur plafond)                     450 000 GNF
Versement Forfaitaire (6%)                           405 692 GNF
Taxe d'Apprentissage (1,5%)                          101 423 GNF
───────────────────────────────────────────────────────────────────
TOTAL CHARGES PATRONALES                             957 115 GNF

COÛT TOTAL EMPLOYEUR                               7 718 653 GNF
```

---

## ⚠️ Erreur courante à éviter

> **Ne JAMAIS calculer la RTS directement sur le brut total !**
>
> Les indemnités forfaitaires (transport, logement, repas) sont exonérées 
> de RTS dans la limite de 25% du brut et doivent être retirées de la base 
> imposable AVANT tout calcul.
>
> Cette erreur est fréquente, même chez des professionnels RH expérimentés.

---

## Annexes

### A. Constantes système

| Code | Libellé | Valeur | Unité |
|------|---------|--------|-------|
| PLANCHER_CNSS | Plancher CNSS (SMIG) | 550 000 | GNF |
| PLAFOND_CNSS | Plafond CNSS | 2 500 000 | GNF |
| TAUX_CNSS_EMPLOYE | Taux CNSS salarié | 5,00 | % |
| TAUX_CNSS_EMPLOYEUR | Taux CNSS employeur | 18,00 | % |
| TAUX_VF | Versement Forfaitaire | 6,00 | % |
| TAUX_TA | Taxe d'Apprentissage | 1,50 | % |
| HEURES_MENSUELLES | Heures/mois standard | 173,33 | heures |
| PLAFOND_INDEMNITES_PCT | Plafond indemnités forfaitaires | 25 | % |

### B. Références légales

- **Code Général des Impôts (CGI) 2022** - Barème RTS
- **Code du Travail de Guinée** - Heures supplémentaires (Art. 221)
- **Code du Travail de Guinée** - Congés payés
- **Décrets CNSS** - Taux de cotisation

---

*Document généré par GestionnaireRH - International Consulting Guinea*
