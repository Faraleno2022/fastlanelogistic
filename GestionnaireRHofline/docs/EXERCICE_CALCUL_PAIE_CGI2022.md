# EXERCICE PRATIQUE - CALCUL DE PAIE
## Conforme au Code Général des Impôts (CGI) 2022 et Code du Travail guinéen

---

# INTRODUCTION

Ce document présente un exercice pratique complet de calcul de paie conforme à la législation guinéenne en vigueur. Il est destiné aux gestionnaires de paie, comptables, responsables RH et toute personne souhaitant comprendre le mécanisme de calcul des salaires en République de Guinée.

## Objectifs pédagogiques

A la fin de cet exercice, vous serez capable de :
- Calculer le salaire brut incluant les heures supplémentaires
- Appliquer correctement le barème RTS à 6 tranches du CGI 2022
- Calculer les cotisations CNSS (part salariale et patronale)
- Vérifier la conformité du plafond des indemnités forfaitaires
- Déterminer le net à payer et le coût total employeur

## Références légales

- Code Général des Impôts (CGI) 2022 - Titre II, Chapitre 1 : Retenue à la Source (RTS)
- Code du Travail guinéen - Article 221 : Heures supplémentaires
- Code du Travail guinéen - Article 153 : Congés payés
- Décret relatif aux cotisations CNSS - Taux et plafonds

---

# PARTIE 1 : DONNÉES DE L'EXERCICE

## 1.1 Fiche signalétique de l'employé

### Identité
| Information | Valeur |
|-------------|--------|
| Nom et Prénoms | DIALLO Mamadou |
| Matricule | EMP-2025-001 |
| Date de naissance | 12/05/1985 |
| Lieu de naissance | Conakry |
| Nationalité | Guinéenne |
| N° CNSS | 1234567890 |

### Situation professionnelle
| Information | Valeur |
|-------------|--------|
| Poste occupé | Ingénieur Informatique Senior |
| Service | Direction des Systèmes d'Information |
| Type de contrat | CDI (Contrat à Durée Indéterminée) |
| Date d'embauche | 15/03/2020 |
| Ancienneté | 4 ans et 9 mois |
| Catégorie professionnelle | Cadre - Niveau C3 |
| Convention collective | Secteur Privé - Technologies |

### Situation familiale
| Information | Valeur |
|-------------|--------|
| Situation matrimoniale | Marié(e) |
| Nombre d'enfants à charge | 3 enfants |
| Conjoint(e) à charge | Oui |

## 1.2 Éléments de rémunération - Période : Janvier 2026

### Éléments fixes
| Rubrique | Code | Description | Montant |
|----------|------|-------------|---------|
| Salaire de base | SAL_BASE | Rémunération mensuelle contractuelle | 5 000 000 GNF |
| Prime de responsabilité | PRM_RESP | Prime liée aux fonctions d'encadrement | 500 000 GNF |
| Indemnité de transport | IND_TRANS | Forfait mensuel déplacement domicile-travail | 300 000 GNF |
| Indemnité de logement | IND_LOG | Participation aux frais de logement | 400 000 GNF |

### Éléments variables
| Rubrique | Code | Description | Quantité |
|----------|------|-------------|----------|
| Heures supplémentaires (1ère catégorie) | HS_CAT1 | 4 premières HS par semaine (+30%) | 8 heures |
| Heures supplémentaires (2ème catégorie) | HS_CAT2 | Au-delà de 4 HS par semaine (+60%) | 6 heures |

### Informations complémentaires
| Paramètre | Valeur |
|-----------|--------|
| Jours travaillés dans le mois | 22 jours |
| Heures mensuelles théoriques | 173,33 heures |
| Absences | 0 jour |
| Retards | 0 |

---

# PARTIE 2 : MÉTHODE DE CALCUL DÉTAILLÉE

## ÉTAPE 1 : Calcul du Salaire Brut

### 1.1 Détermination du taux horaire

Le taux horaire est calculé sur la base de 173,33 heures mensuelles (40 heures/semaine × 52 semaines ÷ 12 mois).

**Formule :**
```
Taux horaire = Salaire de base mensuel ÷ Nombre d'heures mensuelles
Taux horaire = 5 000 000 GNF ÷ 173,33 heures
Taux horaire = 28 847 GNF/heure
```

### 1.2 Calcul des heures supplémentaires (Code du Travail Art. 221)

Le Code du Travail guinéen prévoit des majorations différentes selon le nombre d'heures supplémentaires effectuées :

**Barème des majorations :**
| Catégorie | Conditions | Majoration | Taux appliqué |
|-----------|------------|------------|---------------|
| 1ère catégorie | 4 premières HS/semaine | +30% | 130% du taux horaire |
| 2ème catégorie | Au-delà de 4 HS/semaine | +60% | 160% du taux horaire |
| Heures de nuit | Travail entre 20h et 6h | +20% | 120% du taux horaire |
| Jour férié (jour) | Travail un jour férié | +60% | 160% du taux horaire |
| Jour férié (nuit) | Travail nuit d'un jour férié | +100% | 200% du taux horaire |

**Calcul détaillé :**

| Type d'HS | Heures | Taux horaire | Majoration | Calcul | Montant |
|-----------|--------|--------------|------------|--------|---------|
| 1ère catégorie (+30%) | 8h | 28 847 GNF | 130% | 8 × 28 847 × 1,30 | 300 008 GNF |
| 2ème catégorie (+60%) | 6h | 28 847 GNF | 160% | 6 × 28 847 × 1,60 | 276 931 GNF |
| **TOTAL HS** | **14h** | | | | **576 939 GNF** |

### 1.3 Récapitulatif du Salaire Brut

| Élément | Nature | Montant |
|---------|--------|---------|
| Salaire de base | Fixe | 5 000 000 GNF |
| Prime de responsabilité | Fixe | 500 000 GNF |
| Indemnité de transport | Forfaitaire | 300 000 GNF |
| Indemnité de logement | Forfaitaire | 400 000 GNF |
| Heures supplémentaires | Variable | 576 939 GNF |
| **SALAIRE BRUT** | | **6 776 939 GNF** |

---

## ÉTAPE 2 : Vérification du Plafond 25% des Indemnités Forfaitaires

### 2.1 Règle applicable

Selon la réglementation fiscale guinéenne, les indemnités forfaitaires (transport, logement, représentation, etc.) sont exonérées d'impôt sur le revenu (RTS) dans la limite de **25% du salaire brut**. Au-delà de ce plafond, l'excédent est réintégré dans la base imposable.

### 2.2 Calcul de vérification

**Identification des indemnités forfaitaires :**
| Indemnité | Montant |
|-----------|---------|
| Indemnité de transport | 300 000 GNF |
| Indemnité de logement | 400 000 GNF |
| **Total indemnités** | **700 000 GNF** |

**Calcul du plafond :**
```
Plafond 25% = Salaire brut × 25%
Plafond 25% = 6 776 939 × 0,25
Plafond 25% = 1 694 235 GNF
```

**Comparaison :**
```
Total indemnités : 700 000 GNF
Plafond 25% : 1 694 235 GNF
Différence : 994 235 GNF (marge disponible)

Résultat : 700 000 < 1 694 235 → CONFORME ✅
Excédent à réintégrer : 0 GNF
```

---

## ÉTAPE 3 : Calcul des Cotisations CNSS

### 3.1 Réglementation CNSS

La Caisse Nationale de Sécurité Sociale (CNSS) de Guinée prévoit :

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| Plancher | 550 000 GNF | Assiette minimale de cotisation (SMIG) |
| Plafond | 2 500 000 GNF | Assiette maximale de cotisation |
| Taux salarié | 5% | Part retenue sur le salaire de l'employé |
| Taux employeur | 18% | Part versée par l'employeur |

**Décomposition du taux employeur (18%) :**
| Branche | Taux |
|---------|------|
| Prestations familiales | 6% |
| Accidents du travail / Maladies professionnelles | 4% |
| Retraite (vieillesse) | 4% |
| Assurance maladie | 4% |
| **Total** | **18%** |

### 3.2 Détermination de l'assiette CNSS

```
Salaire brut : 6 776 939 GNF
Plafond CNSS : 2 500 000 GNF

Le salaire brut dépasse le plafond CNSS.
→ Assiette CNSS = 2 500 000 GNF (plafond appliqué)
```

### 3.3 Calcul des cotisations

| Cotisation | Assiette | Taux | Calcul | Montant |
|------------|----------|------|--------|---------|
| CNSS Salarié | 2 500 000 GNF | 5% | 2 500 000 × 0,05 | **125 000 GNF** |
| CNSS Employeur | 2 500 000 GNF | 18% | 2 500 000 × 0,18 | **450 000 GNF** |
| **Total CNSS** | | **23%** | | **575 000 GNF** |

---

## ÉTAPE 4 : Calcul du RTS (Retenue à la Source) - CGI 2022

### 4.1 Détermination de la base imposable

```
Base imposable = Salaire brut - Cotisations sociales salariales
Base imposable = 6 776 939 - 125 000
Base imposable = 6 651 939 GNF
```

### 4.2 Barème RTS - CGI 2022 (6 tranches officielles)

Le Code Général des Impôts 2022 de la République de Guinée établit un barème progressif à 6 tranches pour le calcul de la Retenue à la Source (RTS) :

| Tranche | Revenus mensuels (GNF) | Taux | Impôt maximum par tranche |
|---------|------------------------|------|---------------------------|
| 1 | 0 - 1 000 000 | 0% | 0 GNF |
| 2 | 1 000 001 - 3 000 000 | 5% | 100 000 GNF |
| 3 | 3 000 001 - 5 000 000 | 8% | 160 000 GNF |
| 4 | 5 000 001 - 10 000 000 | 10% | 500 000 GNF |
| 5 | 10 000 001 - 20 000 000 | 15% | 1 500 000 GNF |
| 6 | Au-delà de 20 000 000 | 20% | Illimité |

**Note importante :** La tranche 3 à 8% est cruciale et souvent omise dans les anciens systèmes. Elle représente une disposition légale du CGI 2022 qui doit être appliquée.

### 4.3 Calcul détaillé du RTS par tranche

Base imposable : **6 651 939 GNF**

| Tranche | Borne inf. | Borne sup. | Montant imposé | Taux | Calcul | RTS |
|---------|------------|------------|----------------|------|--------|-----|
| 1 | 0 | 1 000 000 | 1 000 000 | 0% | 1 000 000 × 0,00 | 0 GNF |
| 2 | 1 000 001 | 3 000 000 | 2 000 000 | 5% | 2 000 000 × 0,05 | 100 000 GNF |
| 3 | 3 000 001 | 5 000 000 | 2 000 000 | 8% | 2 000 000 × 0,08 | 160 000 GNF |
| 4 | 5 000 001 | 6 651 939 | 1 651 939 | 10% | 1 651 939 × 0,10 | 165 194 GNF |
| 5 | - | - | 0 | 15% | - | 0 GNF |
| 6 | - | - | 0 | 20% | - | 0 GNF |
| **TOTAL** | | | **6 651 939** | | | **425 194 GNF** |

**Vérification :** 1 000 000 + 2 000 000 + 2 000 000 + 1 651 939 = 6 651 939 GNF ✅

---

## ÉTAPE 5 : Calcul des Charges Patronales

### 5.1 Détail des charges patronales

| Charge | Description | Base | Taux | Calcul | Montant |
|--------|-------------|------|------|--------|---------|
| CNSS Employeur | Cotisations sociales patronales | 2 500 000 | 18% | 2 500 000 × 0,18 | 450 000 GNF |
| VF | Versement Forfaitaire (impôt) | 6 776 939 | 6% | 6 776 939 × 0,06 | 406 616 GNF |
| TA | Taxe d'Apprentissage | 6 776 939 | 1,5% | 6 776 939 × 0,015 | 101 654 GNF |
| ONFPP | Contribution formation professionnelle | 6 776 939 | 1,5% | 6 776 939 × 0,015 | 101 654 GNF |
| **TOTAL CHARGES PATRONALES** | | | **27%** | | **1 059 924 GNF** |

**Note :** Le VF et la TA sont calculés sur le brut total, sans plafonnement. La CNSS est plafonnée à 2 500 000 GNF.

---

## ÉTAPE 6 : Calcul du Net à Payer

### 6.1 Formule générale

```
Net à payer = Salaire brut - Cotisations salariales - Impôt (RTS)
```

### 6.2 Application

```
Net à payer = 6 776 939 - 125 000 - 425 194
Net à payer = 6 226 745 GNF
```

---

# PARTIE 3 : RÉCAPITULATIF DU BULLETIN DE PAIE

## 3.1 Bulletin simplifié

### GAINS ET RÉMUNÉRATIONS
| Rubrique | Base | Taux | Montant |
|----------|------|------|---------|
| Salaire de base | 173,33h | - | 5 000 000 GNF |
| Prime de responsabilité | - | - | 500 000 GNF |
| Indemnité de transport | - | - | 300 000 GNF |
| Indemnité de logement | - | - | 400 000 GNF |
| Heures supplémentaires Cat.1 | 8h | 130% | 300 008 GNF |
| Heures supplémentaires Cat.2 | 6h | 160% | 276 931 GNF |
| **TOTAL BRUT** | | | **6 776 939 GNF** |

### RETENUES ET COTISATIONS
| Rubrique | Base | Taux | Montant |
|----------|------|------|---------|
| CNSS Salarié | 2 500 000 | 5% | 125 000 GNF |
| RTS (Impôt sur le revenu) | 6 651 939 | Progressif | 425 194 GNF |
| **TOTAL RETENUES** | | | **550 194 GNF** |

### RÉSUMÉ
| Élément | Montant |
|---------|---------|
| **SALAIRE BRUT** | **6 776 939 GNF** |
| Total cotisations salariales | - 125 000 GNF |
| Total impôts (RTS) | - 425 194 GNF |
| **NET À PAYER** | **6 226 745 GNF** |

## 3.2 Charges patronales (non visibles sur le bulletin)

| Charge | Montant |
|--------|---------|
| CNSS Employeur (18%) | 450 000 GNF |
| Versement Forfaitaire (6%) | 406 616 GNF |
| Taxe d'Apprentissage (1,5%) | 101 654 GNF |
| ONFPP (1,5%) | 101 654 GNF |
| **TOTAL CHARGES PATRONALES** | **1 059 924 GNF** |

## 3.3 Coût total employeur

```
Coût total = Salaire brut + Charges patronales
Coût total = 6 776 939 + 1 059 924
Coût total = 7 836 863 GNF
```

---

# PARTIE 4 : EXERCICES COMPLÉMENTAIRES

## Exercice 2 : Salarié au SMIG

**Données :**
- Salaire de base : 550 000 GNF (SMIG)
- Pas de primes ni d'indemnités
- Pas d'heures supplémentaires

**Solution :**
| Élément | Calcul | Montant |
|---------|--------|---------|
| Brut | - | 550 000 GNF |
| CNSS Salarié | 550 000 × 5% | 27 500 GNF |
| Base RTS | 550 000 - 27 500 | 522 500 GNF |
| RTS | 522 500 < 1 000 000 → 0% | 0 GNF |
| **Net à payer** | 550 000 - 27 500 - 0 | **522 500 GNF** |

## Exercice 3 : Cadre supérieur (salaire > 20M)

**Données :**
- Salaire brut : 25 000 000 GNF

**Solution RTS :**
| Tranche | Montant | Taux | RTS |
|---------|---------|------|-----|
| 1 | 1 000 000 | 0% | 0 |
| 2 | 2 000 000 | 5% | 100 000 |
| 3 | 2 000 000 | 8% | 160 000 |
| 4 | 5 000 000 | 10% | 500 000 |
| 5 | 10 000 000 | 15% | 1 500 000 |
| 6 | 4 875 000 | 20% | 975 000 |
| **Total** | | | **3 235 000 GNF** |

---

# PARTIE 5 : CONFORMITÉ ET RÉFÉRENCES

## 5.1 Tableau de conformité CGI 2022

| Règle légale | Valeur requise | Valeur appliquée | Statut |
|--------------|----------------|------------------|--------|
| Barème RTS 6 tranches | Obligatoire | 6 tranches | ✅ Conforme |
| Tranche 8% (3M-5M) | Obligatoire | Appliquée | ✅ Conforme |
| CNSS plafond | 2 500 000 GNF | 2 500 000 GNF | ✅ Conforme |
| CNSS plancher | 550 000 GNF | 550 000 GNF | ✅ Conforme |
| CNSS salarié | 5% | 5% | ✅ Conforme |
| CNSS employeur | 18% | 18% | ✅ Conforme |
| VF | 6% | 6% | ✅ Conforme |
| TA | 1,5% | 1,5% | ✅ Conforme |
| HS Cat.1 (Art. 221) | +30% | 130% | ✅ Conforme |
| HS Cat.2 (Art. 221) | +60% | 160% | ✅ Conforme |
| Plafond indemnités | 25% du brut | Vérifié | ✅ Conforme |

## 5.2 Références légales

1. **Code Général des Impôts 2022** - République de Guinée
   - Titre II : Impôts sur les revenus
   - Chapitre 1 : Retenue à la Source (RTS)
   - Article XX : Barème progressif

2. **Code du Travail** - République de Guinée
   - Article 221 : Heures supplémentaires et majorations
   - Article 153 : Congés payés annuels
   - Article 154 : Calcul des indemnités de congés

3. **Décrets CNSS**
   - Décret N°XX : Taux de cotisations
   - Décret N°XX : Plafond et plancher

---

# ANNEXES

## Annexe A : Formules de calcul rapide

```
Taux horaire = Salaire base ÷ 173,33
HS Cat.1 = Heures × Taux horaire × 1,30
HS Cat.2 = Heures × Taux horaire × 1,60
CNSS Salarié = MIN(Brut, 2 500 000) × 5%
Base RTS = Brut - CNSS Salarié
VF = Brut × 6%
TA = Brut × 1,5%
```

## Annexe B : Taux récapitulatifs

| Cotisation/Impôt | Taux | Base |
|------------------|------|------|
| CNSS Salarié | 5% | Plafonnée |
| CNSS Employeur | 18% | Plafonnée |
| VF | 6% | Brut total |
| TA | 1,5% | Brut total |
| ONFPP | 1,5% | Brut total |
| **Total charges patronales** | **27%** | |

---

**Document conforme au CGI 2022 et Code du Travail guinéen**

*Généré le 02/01/2026 par GuineeRH.space - Système de Paie Certifié*

*© 2026 GuineeRH.space - Tous droits réservés*
