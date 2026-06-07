# TP 4 – Calcul d'un Bulletin de Paie

> **Durée estimée** : 60 minutes  
> **Niveau** : Intermédiaire  
> **Prérequis** : TP 1, 2, 3 complétés, notions de base en paie

---

## 🎯 Objectifs pédagogiques

À la fin de ce TP, vous serez capable de :

1. Comprendre la **structure complète** d'un bulletin de paie guinéen
2. Calculer les **cotisations CNSS** (employé et employeur)
3. Calculer la **RTS** avec le barème progressif et les exonérations
4. Identifier les **indemnités forfaitaires exonérées** (règle des 25%)
5. Vérifier un bulletin de paie manuellement

---

## 📚 Rappel théorique (10 min)

### Structure du calcul de paie

```
┌─────────────────────────────────────────────────────────────────┐
│  SALAIRE BRUT                                                   │
│  = Salaire de base + Primes + Indemnités + Heures Sup           │
├─────────────────────────────────────────────────────────────────┤
│  COTISATIONS CNSS                                               │
│  • Employé: 5% (sur base plafonnée à 2 500 000 GNF)             │
│  • Employeur: 18% (charge patronale)                            │
├─────────────────────────────────────────────────────────────────┤
│  RTS (Retenue à la Source)                                      │
│  ⚠️ Calculée sur: Brut - Indemnités exonérées - CNSS            │
│     puis: - Déductions familiales - Abattement 5%               │
├─────────────────────────────────────────────────────────────────┤
│  NET À PAYER                                                    │
│  = Brut - CNSS Employé - RTS - Autres retenues                  │
└─────────────────────────────────────────────────────────────────┘
```

### ⚠️ Règle CRITIQUE : Indemnités forfaitaires exonérées

> **Les indemnités forfaitaires (transport, logement, repas) sont exonérées de RTS dans la limite de 25% du salaire brut.**
>
> - Si indemnités ≤ 25% du brut → **Entièrement exonérées**
> - Si indemnités > 25% du brut → **Seul l'excédent est imposable**

**Erreur fréquente** : Calculer la RTS sur le brut total sans exclure les indemnités exonérées.

---

## 🧩 EXERCICE PRATIQUE : Calcul complet

### Données de l'employé

| Information | Valeur |
|-------------|--------|
| **Nom** | Mamadou DIALLO |
| **Poste** | Comptable Senior |
| **Ancienneté** | 8 ans |
| **Situation familiale** | Marié, 2 enfants |

### Éléments de salaire du mois

| Rubrique | Montant | Soumis CNSS | Soumis RTS |
|----------|---------|-------------|------------|
| Salaire de base | 5 000 000 GNF | ✅ Oui | ✅ Oui |
| Prime de transport | 500 000 GNF | ❌ Non | ❌ Non (exonérée) |
| Indemnité de logement | 800 000 GNF | ❌ Non | ❌ Non (exonérée) |
| Heures sup (10h à 60%) | À calculer | ✅ Oui | ✅ Oui |

---

## 🧩 ÉTAPE 1 : Calcul des heures supplémentaires (5 min)

### 📋 Barème des majorations (Code du Travail – Art. 221)

| Catégorie | Majoration | Taux effectif |
|-----------|------------|---------------|
| Heures 41 à 48/semaine | **+30%** | 130% du taux horaire |
| Heures au-delà de 48/semaine | **+60%** | 160% du taux horaire |
| Heures de nuit (20h-6h) | **+20%** | 120% du taux horaire |
| Dimanche / Jour férié (jour) | **+60%** | 160% du taux horaire |
| Dimanche / Jour férié (nuit) | **+100%** | 200% du taux horaire |

### Données de l'exercice

- Salaire de base : 5 000 000 GNF
- Heures mensuelles standard : 173,33 heures
- Heures sup effectuées : 10 heures (au-delà de 48h → +60%)

### Calcul

```
Taux horaire = Salaire de base / 173,33
Taux horaire = 5 000 000 / 173,33
Taux horaire = 28 846 GNF

Montant HS = Heures × Taux horaire × Majoration
Montant HS = 10 × 28 846 × 1,60
Montant HS = 461 538 GNF
```

### ✅ Résultat

| Élément | Montant |
|---------|---------|
| Heures supplémentaires (10h × 160%) | **461 538 GNF** |

---

## 🧩 ÉTAPE 2 : Calcul du salaire brut (5 min)

### Addition de tous les gains

```
Salaire de base:          5 000 000 GNF
Prime de transport:         500 000 GNF
Indemnité de logement:      800 000 GNF
Heures supplémentaires:     461 538 GNF
─────────────────────────────────────────
SALAIRE BRUT:             6 761 538 GNF
```

### ✅ Résultat

| Élément | Montant |
|---------|---------|
| **SALAIRE BRUT** | **6 761 538 GNF** |

---

## 🧩 ÉTAPE 3 : Calcul de la CNSS (10 min)

### Paramètres CNSS

| Paramètre | Valeur |
|-----------|--------|
| Plancher | 550 000 GNF |
| **Plafond** | **2 500 000 GNF** |
| Taux employé | 5% |
| Taux employeur | 18% |

### Détermination de la base CNSS

Seuls les éléments avec `soumis_cnss = Oui` sont inclus :

```
Salaire de base:          5 000 000 GNF  ✅
Prime de transport:         500 000 GNF  ❌ (non soumis)
Indemnité de logement:      800 000 GNF  ❌ (non soumis)
Heures supplémentaires:     461 538 GNF  ✅
─────────────────────────────────────────
Base CNSS brute:          5 461 538 GNF
```

### Application du plafond

```
Base CNSS brute: 5 461 538 GNF
Plafond CNSS:    2 500 000 GNF

Comme 5 461 538 > 2 500 000 → Base plafonnée = 2 500 000 GNF
```

### Calcul des cotisations

```
┌─────────────────────────────────────────────────────────────────┐
│  CNSS EMPLOYÉ                                                   │
│  Assiette plafonnée × Taux salarié                              │
│  = 2 500 000 × 5%                                               │
│  = 125 000 GNF ✅                                               │
├─────────────────────────────────────────────────────────────────┤
│  CNSS EMPLOYEUR                                                 │
│  Assiette plafonnée × Taux patronal                             │
│  = 2 500 000 × 18%                                              │
│  = 450 000 GNF ✅                                               │
└─────────────────────────────────────────────────────────────────┘
```

### ✅ Résultat CNSS

| Cotisation | Montant |
|------------|---------|
| CNSS Employé (5%) | **125 000 GNF** |
| CNSS Employeur (18%) | 450 000 GNF |

---

## 🧩 ÉTAPE 4 : Calcul de la RTS (20 min)

### ⚠️ ATTENTION : Exonération des indemnités forfaitaires

**C'est ici que beaucoup font l'erreur !**

### 4.1 Identification des indemnités exonérées

```
Transport:  500 000 GNF
Logement:   800 000 GNF
─────────────────────────
Total:    1 300 000 GNF
```

### 4.2 Vérification du plafond 25%

```
Plafond 25% = Brut × 25%
Plafond 25% = 6 761 538 × 25%
Plafond 25% = 1 690 385 GNF

Indemnités (1 300 000) < Plafond (1 690 385)
→ ✅ Entièrement exonérées de RTS
```

### 4.3 Calcul de la base imposable RTS

```
Base imposable = Brut - Indemnités exonérées
Base imposable = 6 761 538 - 1 300 000
Base imposable = 5 461 538 GNF
```

### 4.4 Déduction de la CNSS employé

```
Base après CNSS = 5 461 538 - 125 000
Base après CNSS = 5 336 538 GNF
```

### 4.5 Déductions familiales

| Déduction | Montant |
|-----------|---------|
| Conjoint (marié) | 100 000 GNF |
| Enfants (2 × 50 000) | 100 000 GNF |
| **Total déductions** | **200 000 GNF** |

```
Base après déductions = 5 336 538 - 200 000
Base après déductions = 5 136 538 GNF
```

### 4.6 Abattement professionnel (5% plafonné à 1 000 000)

```
Abattement = 5% × 5 136 538 = 256 827 GNF
Plafond = 1 000 000 GNF

Comme 256 827 < 1 000 000 → Abattement = 256 827 GNF
```

### 4.7 Base nette imposable

```
Base nette = 5 136 538 - 256 827
Base nette = 4 879 711 GNF
```

### 4.8 Application du barème RTS progressif

| Tranche | De | À | Taux | Montant taxable | RTS |
|---------|-----|-----|------|-----------------|-----|
| 1 | 0 | 1 000 000 | 0% | 1 000 000 | **0 GNF** |
| 2 | 1 000 001 | 3 000 000 | 5% | 2 000 000 | **100 000 GNF** |
| 3 | 3 000 001 | 4 879 711 | 8% | 1 879 711 | **150 377 GNF** |

```
RTS Total = 0 + 100 000 + 150 377 = 250 377 GNF
```

### ✅ Résultat RTS

| Élément | Montant |
|---------|---------|
| **RTS (Retenue à la Source)** | **250 377 GNF** |

---

## 🧩 ÉTAPE 5 : Calcul du net à payer (5 min)

### Formule

```
Net à payer = Brut - CNSS Employé - RTS - Autres retenues
```

### Calcul

```
Brut:                     6 761 538 GNF
- CNSS Employé:             125 000 GNF
- RTS:                      250 377 GNF
- Autres retenues:                0 GNF
─────────────────────────────────────────
NET À PAYER:              6 386 161 GNF
```

### ✅ Résultat final

| Élément | Montant |
|---------|---------|
| **NET À PAYER** | **6 386 161 GNF** |

---

## 📋 RÉCAPITULATIF DU BULLETIN

```
═══════════════════════════════════════════════════════════════════
           BULLETIN DE PAIE - MAMADOU DIALLO
                    JANVIER 2026
═══════════════════════════════════════════════════════════════════

GAINS
───────────────────────────────────────────────────────────────────
Salaire de base                                    5 000 000 GNF
Prime de transport                                   500 000 GNF
Indemnité de logement                                800 000 GNF
Heures supplémentaires (10h × 160%)                  461 538 GNF
───────────────────────────────────────────────────────────────────
SALAIRE BRUT                                       6 761 538 GNF

RETENUES
───────────────────────────────────────────────────────────────────
CNSS Salarié (5% sur plafond 2 500 000)              125 000 GNF
RTS (Retenue à la Source)                            250 377 GNF
───────────────────────────────────────────────────────────────────
TOTAL RETENUES                                       375 377 GNF

═══════════════════════════════════════════════════════════════════
NET À PAYER                                        6 386 161 GNF
═══════════════════════════════════════════════════════════════════

INFORMATION EMPLOYEUR (non visible sur bulletin employé)
───────────────────────────────────────────────────────────────────
CNSS Employeur (18% sur plafond)     2 500 000 × 18% = 450 000 GNF
Versement Forfaitaire (6% sur brut)  6 761 538 × 6%  = 405 692 GNF
Taxe d'Apprentissage (1,5% sur brut) 6 761 538 × 1,5%= 101 423 GNF
───────────────────────────────────────────────────────────────────
TOTAL CHARGES PATRONALES                             957 115 GNF
COÛT TOTAL EMPLOYEUR (Brut + Charges)              7 718 653 GNF
```

---

## 🧠 Ce qu'il faut retenir

### Les 5 points essentiels

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. La CNSS se calcule sur une base PLAFONNÉE (2 500 000 GNF)   │
│ 2. Les indemnités forfaitaires sont EXONÉRÉES de RTS (≤25%)    │
│ 3. La RTS est PROGRESSIVE (6 tranches de 0% à 20%)             │
│ 4. Les déductions familiales RÉDUISENT la base RTS             │
│ 5. L'abattement professionnel est de 5% (plafonné à 1M GNF)    │
└─────────────────────────────────────────────────────────────────┘
```

### ⚠️ Erreur à éviter absolument

> **NE JAMAIS calculer la RTS sur le brut total !**
> 
> Les indemnités forfaitaires (transport, logement, repas) doivent être
> retirées de la base imposable AVANT le calcul de la RTS.

---

## ✅ Checklist de validation

Avant de valider un bulletin, vérifiez :

- [ ] Base CNSS plafonnée à 2 500 000 GNF
- [ ] CNSS employé = 5% de la base plafonnée
- [ ] Indemnités exonérées retirées de la base RTS
- [ ] Plafond 25% vérifié pour les indemnités
- [ ] Déductions familiales appliquées (conjoint + enfants)
- [ ] Abattement 5% calculé et plafonné
- [ ] RTS calculée par tranches progressives
- [ ] Net = Brut - CNSS - RTS - Autres retenues

---

## 📝 Exercices d'application

---

### 📌 EXERCICE 2 : Employé au SMIG (Corrigé)

| Information | Valeur |
|-------------|--------|
| **Nom** | Fatoumata BALDE |
| **Salaire de base** | 550 000 GNF (SMIG) |
| **Situation** | Célibataire, sans enfant |
| **Indemnités** | Aucune |

#### Solution détaillée

```
┌─────────────────────────────────────────────────────────────────┐
│  1. SALAIRE BRUT = 550 000 GNF                                  │
├─────────────────────────────────────────────────────────────────┤
│  2. CNSS SALARIÉ                                                │
│     Base = 550 000 GNF (≥ plancher, < plafond)                  │
│     CNSS = 550 000 × 5% = 27 500 GNF                            │
├─────────────────────────────────────────────────────────────────┤
│  3. BASE RTS                                                    │
│     Base = Brut - CNSS = 550 000 - 27 500 = 522 500 GNF         │
│     Déductions familiales = 0 (célibataire sans enfant)         │
│     Abattement 5% = 522 500 × 5% = 26 125 GNF                   │
│     Base nette imposable = 522 500 - 26 125 = 496 375 GNF       │
├─────────────────────────────────────────────────────────────────┤
│  4. RTS                                                         │
│     496 375 GNF < 1 000 000 GNF → Tranche à 0%                  │
│     ✅ RTS = 0 GNF                                              │
├─────────────────────────────────────────────────────────────────┤
│  5. NET À PAYER                                                 │
│     = 550 000 - 27 500 - 0 = 522 500 GNF                        │
└─────────────────────────────────────────────────────────────────┘
```

| Élément | Montant |
|---------|----------|
| Brut | 550 000 GNF |
| CNSS Salarié | 27 500 GNF |
| RTS | 0 GNF |
| **NET À PAYER** | **522 500 GNF** |

> ✅ **Conforme CGI 2022** : Un salarié au SMIG ne paie pas de RTS (base < 1M GNF)

---

### 📌 EXERCICE 3 : Cadre supérieur (Corrigé)

| Information | Valeur |
|-------------|--------|
| **Nom** | Dr. Ibrahima SYLLA |
| **Poste** | Directeur Financier |
| **Salaire de base** | 25 000 000 GNF |
| **Situation** | Marié, 4 enfants |
| **Indemnités** | Transport 2 000 000 + Logement 4 000 000 |

#### Solution détaillée

```
┌─────────────────────────────────────────────────────────────────┐
│  1. SALAIRE BRUT                                                │
│     = 25 000 000 + 2 000 000 + 4 000 000 = 31 000 000 GNF       │
├─────────────────────────────────────────────────────────────────┤
│  2. CNSS SALARIÉ (plafonnée)                                    │
│     Base brute CNSS = 25 000 000 GNF (salaire seul)             │
│     Plafond = 2 500 000 GNF                                     │
│     CNSS = 2 500 000 × 5% = 125 000 GNF                         │
├─────────────────────────────────────────────────────────────────┤
│  3. VÉRIFICATION PLAFOND 25% INDEMNITÉS                         │
│     Indemnités = 2 000 000 + 4 000 000 = 6 000 000 GNF          │
│     Plafond 25% = 31 000 000 × 25% = 7 750 000 GNF              │
│     6 000 000 < 7 750 000 → ✅ Entièrement exonérées            │
├─────────────────────────────────────────────────────────────────┤
│  4. BASE RTS                                                    │
│     Base = Brut - Indemnités exonérées - CNSS                   │
│     = 31 000 000 - 6 000 000 - 125 000 = 24 875 000 GNF         │
│     Déductions familiales = 100 000 + (4 × 50 000) = 300 000    │
│     Base après déductions = 24 875 000 - 300 000 = 24 575 000   │
│     Abattement 5% = min(24 575 000 × 5%, 1 000 000) = 1 000 000 │
│     Base nette imposable = 24 575 000 - 1 000 000 = 23 575 000  │
├─────────────────────────────────────────────────────────────────┤
│  5. CALCUL RTS PAR TRANCHES                                     │
│                                                                 │
│     Tranche 1: 0 - 1 000 000       × 0%  =          0 GNF       │
│     Tranche 2: 1 000 001 - 3 000 000  × 5%  =    100 000 GNF    │
│     Tranche 3: 3 000 001 - 5 000 000  × 8%  =    160 000 GNF    │
│     Tranche 4: 5 000 001 - 10 000 000 × 10% =    500 000 GNF    │
│     Tranche 5: 10 000 001 - 20 000 000 × 15% = 1 500 000 GNF    │
│     Tranche 6: 20 000 001 - 23 575 000 × 20% =   715 000 GNF    │
│     ─────────────────────────────────────────────────────────   │
│     ✅ RTS TOTAL = 2 975 000 GNF                                │
├─────────────────────────────────────────────────────────────────┤
│  6. NET À PAYER                                                 │
│     = 31 000 000 - 125 000 - 2 975 000 = 27 900 000 GNF         │
└─────────────────────────────────────────────────────────────────┘
```

| Élément | Montant |
|---------|----------|
| Brut | 31 000 000 GNF |
| CNSS Salarié (plafonnée) | 125 000 GNF |
| RTS (6 tranches) | 2 975 000 GNF |
| **NET À PAYER** | **27 900 000 GNF** |

> ✅ **Impact du progressif** : Malgré un brut de 31M, le taux moyen effectif de RTS est ~12% (et non 20%)

---

### 📌 EXERCICE 4 : À vous de jouer !

### Calculez le bulletin de Marie CAMARA

| Information | Valeur |
|-------------|--------|
| Salaire de base | 8 000 000 GNF |
| Prime transport | 600 000 GNF |
| Prime logement | 1 200 000 GNF |
| Situation | Célibataire, 1 enfant |
| Heures sup | 5h à +30% |

**Questions** :
1. Quel est le montant des heures supplémentaires ?
2. Les indemnités dépassent-elles le plafond 25% ?
3. Quelle est la RTS due ? (détaillez par tranche)
4. Quel est le net à payer ?

---

**TP suivant** : [TP 5 – Génération et envoi des bulletins](./TP5_ENVOI_BULLETINS.md)

---

*Document de formation - International Consulting Guinea*  
*Conforme CGI 2022 et Code du Travail guinéen*
