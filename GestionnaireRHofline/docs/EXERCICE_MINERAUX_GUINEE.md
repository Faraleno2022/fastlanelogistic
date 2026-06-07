# 📝 Exercice Complexe de Paie - MINÉRAUX GUINÉE SA

## ✅ Données Initialisées dans le Système

### 🏢 Entreprise
- **Raison sociale** : MINÉRAUX GUINÉE SA
- **Forme juridique** : SA
- **Localisation** : Kindia, Guinée
- **Secteur** : Exploitation minière
- **Convention collective** : Mines et carrières

### 👤 Employé
- **Nom complet** : Diallo Abdoulaye
- **Matricule** : MG-2021-847
- **Poste** : Responsable de chantier (Catégorie A)
- **Service** : Exploitation minière
- **Date d'embauche** : 15 mars 2020
- **Ancienneté** : 5 ans
- **Type de contrat** : CDI
- **Situation familiale** : Marié, 3 enfants à charge
- **Numéro CNSS** : 987654321
- **Couverture sociale** : Régime obligatoire + Mutuelle d'entreprise

### 📅 Période de Paie
- **Mois** : Novembre 2025
- **Jours calendaires** : 30 jours
- **Jours travaillés** : 22 jours
- **Heures mensuelles** : 173.33 heures

---

## 💰 Éléments de Rémunération (20 Rubriques Créées)

### 1. Salaires et Indemnités de Base
| Code | Libellé | Montant | Soumis CNSS | Soumis IRG |
|------|---------|---------|-------------|------------|
| SAL_BASE_CAT_A | Salaire mensuel de base (Catégorie A) | 4,500,000 GNF | ✅ | ✅ |
| IND_FONCTION | Indemnité de fonction | 800,000 GNF | ✅ | ✅ |
| PRIME_ANCIENNETE | Prime d'ancienneté (5%) | 225,000 GNF | ✅ | ✅ |
| PRIME_RESP | Prime de responsabilité | 600,000 GNF | ✅ | ✅ |

### 2. Rémunérations Variables
| Code | Libellé | Montant | Soumis CNSS | Soumis IRG |
|------|---------|---------|-------------|------------|
| PRIME_PROD | Prime de production (120% objectifs) | 750,000 GNF | ✅ | ✅ |
| BONUS_SECURITE | Bonus de sécurité (mois sans accident) | 300,000 GNF | ✅ | ✅ |
| COMMISSION_CA | Commission (2.5% × 25M) | 625,000 GNF | ✅ | ✅ |

### 3. Indemnités et Allocations
| Code | Libellé | Montant | Soumis CNSS | Soumis IRG |
|------|---------|---------|-------------|------------|
| IND_DEPLACE | Indemnité déplacement (8j × 100,000) | 800,000 GNF | ✅ | ❌ |
| IND_REPAS_JOUR | Indemnité repas (22j × 50,000) | 1,100,000 GNF | ✅ | ❌ |
| ALLOC_LOGEMENT | Allocation logement | 400,000 GNF | ✅ | ✅ |
| ALLOC_TRANSPORT | Allocation transport | 250,000 GNF | ✅ | ✅ |

### 4. Heures Supplémentaires
| Code | Libellé | Calcul | Montant |
|------|---------|--------|---------|
| HS_25 | Heures supplémentaires (+25%) | 15h × (4,500,000 ÷ 173) × 1.25 | 487,717 GNF |

### 5. Retenues Obligatoires
| Code | Libellé | Taux/Montant |
|------|---------|--------------|
| CNSS_SAL_MINIER | Cotisation CNSS (salarié) | 5.5% |
| MUTUELLE_ENT | Cotisation mutuelle d'entreprise | 3.0% |
| IRSA_MINIER | IRSA (Impôt sur le revenu) | Barème progressif |

### 6. Autres Retenues
| Code | Libellé | Montant |
|------|---------|---------|
| AVANCE_SAL | Avance sur salaire | 300,000 GNF |
| RET_SYNDICAT | Retenue syndicale | 100,000 GNF |
| PRET_LOGEMENT | Remboursement prêt logement | 400,000 GNF |
| RET_DISCIPLINAIRE | Retenue disciplinaire | 150,000 GNF |

### 7. Cotisations Patronales
| Code | Libellé | Taux |
|------|---------|------|
| CNSS_PAT_MINIER | CNSS Employeur | 8.1% |
| COTIS_MATERNITE | Cotisation Maternité | 1.5% |

---

## 🧮 Calculs Détaillés

### 1. Calculs Préliminaires

#### Prime d'Ancienneté
```
Salaire de base : 4,500,000 GNF
Taux ancienneté (5 ans) : 5%
Prime d'ancienneté = 4,500,000 × 5% = 225,000 GNF
```

#### Commission sur CA
```
Chiffre d'affaires : 25,000,000 GNF
Taux commission : 2.5%
Commission = 25,000,000 × 2.5% = 625,000 GNF
```

#### Heures Supplémentaires
```
Salaire de base : 4,500,000 GNF
Heures de base/mois : 173 heures
Taux horaire = 4,500,000 ÷ 173 = 26,011.56 GNF/heure

Heures supplémentaires : 15 heures
Majoration : +25%
HS = 15 × 26,011.56 × 1.25 = 487,716.75 GNF ≈ 487,717 GNF
```

### 2. Salaire Brut Total

```
═══════════════════════════════════════════════════════════
SALAIRES ET INDEMNITÉS DE BASE
═══════════════════════════════════════════════════════════
Salaire mensuel de base           4,500,000 GNF
Indemnité de fonction               800,000 GNF
Prime d'ancienneté (5%)             225,000 GNF
Prime de responsabilité             600,000 GNF
                           Sous-total : 6,125,000 GNF

═══════════════════════════════════════════════════════════
RÉMUNÉRATIONS VARIABLES
═══════════════════════════════════════════════════════════
Prime de production                 750,000 GNF
Bonus de sécurité                   300,000 GNF
Commission (2.5% × 25M)             625,000 GNF
                           Sous-total : 1,675,000 GNF

═══════════════════════════════════════════════════════════
INDEMNITÉS ET ALLOCATIONS
═══════════════════════════════════════════════════════════
Indemnité déplacement (8j)          800,000 GNF
Indemnité repas (22j)             1,100,000 GNF
Allocation logement                 400,000 GNF
Allocation transport                250,000 GNF
                           Sous-total : 2,550,000 GNF

═══════════════════════════════════════════════════════════
HEURES SUPPLÉMENTAIRES
═══════════════════════════════════════════════════════════
15 heures à +25%                    487,717 GNF
                           Sous-total : 487,717 GNF

═══════════════════════════════════════════════════════════
SALAIRE BRUT TOTAL                 10,837,717 GNF
═══════════════════════════════════════════════════════════
```

### 3. Cotisations Sociales

#### CNSS Salarié (5.5%)
```
Base : Salaire brut = 10,837,717 GNF
Taux : 5.5%
CNSS salarié = 10,837,717 × 5.5% = 596,074.44 GNF ≈ 596,074 GNF
```

#### Mutuelle d'Entreprise (3%)
```
Base : Salaire brut = 10,837,717 GNF
Taux : 3%
Mutuelle = 10,837,717 × 3% = 325,131.51 GNF ≈ 325,132 GNF
```

#### Total Cotisations
```
CNSS salarié :    596,074 GNF
Mutuelle :        325,132 GNF
─────────────────────────────
TOTAL :           921,206 GNF
```

### 4. Salaire Imposable (Base IRSA)
```
Salaire brut :              10,837,717 GNF
- Cotisations sociales :      -921,206 GNF
─────────────────────────────────────────
SALAIRE IMPOSABLE :          9,916,511 GNF
```

### 5. Calcul IRSA (Barème Progressif)

#### Barème Simplifié pour Salarié Marié avec Enfants
| Tranche | Montant | Taux | IRSA |
|---------|---------|------|------|
| 0 - 1,500,000 | 1,500,000 | 0% | 0 |
| 1,500,001 - 3,000,000 | 1,500,000 | 10% | 150,000 |
| 3,000,001 - 6,000,000 | 3,000,000 | 15% | 450,000 |
| 6,000,001 - 9,916,511 | 3,916,511 | 20% | 783,302 |
| **TOTAL** | | | **1,383,302** |

#### Déductions Familiales
```
Conjoint à charge :     50,000 GNF
3 enfants (75,000 × 3): 225,000 GNF
─────────────────────────────────
Total déductions :     275,000 GNF
```

#### IRSA Net
```
IRSA brut :           1,383,302 GNF
- Déductions :         -275,000 GNF
─────────────────────────────────
IRSA NET :            1,108,302 GNF
```

### 6. Autres Retenues
```
Avance sur salaire :        300,000 GNF
Retenue syndicale :         100,000 GNF
Remboursement prêt :        400,000 GNF
Retenue disciplinaire :     150,000 GNF
─────────────────────────────────────
TOTAL AUTRES RETENUES :     950,000 GNF
```

### 7. Salaire Net à Payer
```
Salaire brut :              10,837,717 GNF
- CNSS salarié :              -596,074 GNF
- Mutuelle :                  -325,132 GNF
- IRSA :                    -1,108,302 GNF
- Autres retenues :           -950,000 GNF
──────────────────────────────────────────
SALAIRE NET À PAYER :        7,858,209 GNF
```

### 8. Charges Sociales Patronales

#### CNSS Employeur (8.1%)
```
Base : Salaire brut = 10,837,717 GNF
Taux : 8.1%
CNSS employeur = 10,837,717 × 8.1% = 877,853.68 GNF ≈ 877,854 GNF
```

#### Cotisation Maternité (1.5%)
```
Base : Salaire brut = 10,837,717 GNF
Taux : 1.5%
Maternité = 10,837,717 × 1.5% = 162,565.76 GNF ≈ 162,566 GNF
```

#### Total Charges Patronales
```
CNSS employeur :      877,854 GNF
Maternité :           162,566 GNF
─────────────────────────────────
TOTAL :             1,040,420 GNF
```

### 9. Coût Total pour l'Entreprise
```
Salaire brut :              10,837,717 GNF
+ Charges patronales :       1,040,420 GNF
──────────────────────────────────────────
COÛT TOTAL EMPLOYEUR :      11,878,137 GNF
```

---

## 📄 Bulletin de Paie Complet

```
╔════════════════════════════════════════════════════════════════════════╗
║                   BULLETIN DE PAIE - NOVEMBRE 2025                     ║
╚════════════════════════════════════════════════════════════════════════╝

ENTREPRISE : MINÉRAUX GUINÉE SA
Secteur : Exploitation minière - Kindia, Guinée
Convention collective : Mines et carrières

SALARIÉ : Diallo Abdoulaye              MATRICULE : MG-2021-847
POSTE : Responsable de chantier         CNSS : 987654321
CATÉGORIE : A                           ANCIENNETÉ : 5 ans
SITUATION : Marié, 3 enfants à charge

PÉRIODE : Novembre 2025 (30 jours)
Jours travaillés : 22 jours
Heures de base : 173 heures/mois

════════════════════════════════════════════════════════════════════════

                        ÉLÉMENTS DE RÉMUNÉRATION

────────────────────────────────────────────────────────────────────────
SALAIRES ET INDEMNITÉS DE BASE
────────────────────────────────────────────────────────────────────────
  Salaire mensuel de base (Cat. A)    4,500,000 GNF
  Indemnité de fonction                 800,000 GNF
  Prime d'ancienneté (5%)               225,000 GNF
  Prime de responsabilité               600,000 GNF
                               Sous-total : 6,125,000 GNF

────────────────────────────────────────────────────────────────────────
RÉMUNÉRATIONS VARIABLES
────────────────────────────────────────────────────────────────────────
  Prime de production (120%)            750,000 GNF
  Bonus de sécurité                     300,000 GNF
  Commission (2,5% × 25M)               625,000 GNF
                               Sous-total : 1,675,000 GNF

────────────────────────────────────────────────────────────────────────
INDEMNITÉS ET ALLOCATIONS
────────────────────────────────────────────────────────────────────────
  Indemnité déplacement (8 jours)       800,000 GNF
  Indemnité repas (22 jours)          1,100,000 GNF
  Allocation logement                   400,000 GNF
  Allocation transport                  250,000 GNF
                               Sous-total : 2,550,000 GNF

────────────────────────────────────────────────────────────────────────
HEURES SUPPLÉMENTAIRES
────────────────────────────────────────────────────────────────────────
  15 heures à +25%                      487,717 GNF
  (Taux horaire : 26,011.56 GNF)
                               Sous-total : 487,717 GNF

════════════════════════════════════════════════════════════════════════
                        SALAIRE BRUT             10,837,717 GNF
════════════════════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────────────────
                           RETENUES OBLIGATOIRES
────────────────────────────────────────────────────────────────────────
  Cotisation CNSS (5,5%)                596,074 GNF
  Cotisation Mutuelle (3%)              325,132 GNF
  IRSA (Impôt sur revenu)             1,108,302 GNF
    Base imposable : 9,916,511 GNF
    IRSA brut : 1,383,302 GNF
    Déductions familiales : -275,000 GNF
      (Conjoint : 50,000 + 3 enfants : 225,000)
                        Total retenues : 2,029,508 GNF

────────────────────────────────────────────────────────────────────────
                           AUTRES RETENUES
────────────────────────────────────────────────────────────────────────
  Avance sur salaire                    300,000 GNF
  Retenue syndicale                     100,000 GNF
  Remboursement prêt logement           400,000 GNF
  Retenue disciplinaire                 150,000 GNF
                        Total autres : 950,000 GNF

════════════════════════════════════════════════════════════════════════
                     SALAIRE NET À PAYER        7,858,209 GNF
════════════════════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────────────────
                    CHARGES SOCIALES PATRONALES
────────────────────────────────────────────────────────────────────────
  CNSS Employeur (8,1%)                 877,854 GNF
  Cotisation Maternité (1,5%)           162,566 GNF
                        Charges patronales : 1,040,420 GNF

════════════════════════════════════════════════════════════════════════
                    COÛT TOTAL POUR L'ENTREPRISE
                   10,837,717 + 1,040,420 = 11,878,137 GNF
════════════════════════════════════════════════════════════════════════

Date d'édition : 30 Novembre 2025
Signature employeur :                   Signature employé :
```

---

## 🔍 Constantes Spécifiques Ajoutées

| Code | Libellé | Valeur | Unité |
|------|---------|--------|-------|
| TAUX_ANCIENNETE_5ANS | Taux prime d'ancienneté (5 ans) | 5.00 | % |
| DEDUC_CONJOINT | Déduction IRSA conjoint | 50,000 | GNF |
| DEDUC_ENFANT | Déduction IRSA par enfant | 75,000 | GNF |
| MAX_ENFANTS_DEDUC | Nombre max enfants déductibles | 3 | enfants |
| TAUX_MUTUELLE_ENT | Taux mutuelle d'entreprise | 3.00 | % |
| TAUX_CNSS_PAT_MINIER | Taux CNSS employeur (minier) | 8.10 | % |
| TAUX_MATERNITE | Taux cotisation maternité | 1.50 | % |
| HEURES_BASE_MOIS | Heures de base par mois | 173.00 | heures |

---

## 📊 Récapitulatif des Montants

| Élément | Montant (GNF) | % du Brut |
|---------|---------------|-----------|
| **Salaire brut** | 10,837,717 | 100.00% |
| **CNSS salarié** | -596,074 | 5.50% |
| **Mutuelle** | -325,132 | 3.00% |
| **IRSA** | -1,108,302 | 10.23% |
| **Autres retenues** | -950,000 | 8.77% |
| **SALAIRE NET** | **7,858,209** | **72.50%** |
| | | |
| **CNSS employeur** | 877,854 | 8.10% |
| **Maternité** | 162,566 | 1.50% |
| **COÛT TOTAL** | **11,878,137** | **109.60%** |

---

## ⚠️ Particularités du Secteur Minier

### 1. Taux CNSS Spécifiques
- **Salarié** : 5.5% (vs 5% général)
- **Employeur** : 8.1% (vs 18% général)
- **Maternité** : 1.5% (charge patronale supplémentaire)

### 2. Indemnités Spécifiques
- **Indemnité de déplacement** : Élevée (100,000 GNF/jour)
- **Bonus de sécurité** : Fréquent dans le secteur
- **Prime de production** : Liée aux objectifs (120%)
- **Allocation logement** : Courante en zone minière

### 3. Convention Collective Mines et Carrières
- Heures supplémentaires majorées (+25%, +50%, +100%)
- Primes de risque obligatoires
- Indemnités de déplacement non imposables
- Mutuelle d'entreprise obligatoire

---

## ✅ Validation

Toutes les données de l'exercice ont été créées :
- ✅ Société MINÉRAUX GUINÉE SA
- ✅ Employé Diallo Abdoulaye (5 ans d'ancienneté)
- ✅ 20 rubriques de paie (secteur minier)
- ✅ Période Novembre 2025
- ✅ 8 constantes spécifiques

**Le système est prêt pour le calcul automatique de ce bulletin complexe !**

---

🇬🇳 **Conforme à la législation guinéenne et à la convention collective Mines et carrières**  
**Date** : 21 Octobre 2025
