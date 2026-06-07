# 📋 Récapitulatif des Formules de Paie - Guinée CGI 2022

> **Document de référence rapide** - Toutes les formules exactes et vérifiées

---

## 1. HEURES SUPPLÉMENTAIRES (Code du Travail Art. 221)

### Formule de base
```
Taux horaire = Salaire mensuel ÷ 173,33
```

### Barème des majorations

| Type | Majoration | Taux effectif | Formule |
|------|------------|---------------|---------|
| 4 premières HS/semaine | +30% | 130% | `Heures × Taux horaire × 1,30` |
| Au-delà de 4 HS/semaine | +60% | 160% | `Heures × Taux horaire × 1,60` |
| Heures de nuit (20h-6h) | +20% | 120% | `Heures × Taux horaire × 1,20` |
| Jour férié (jour) | +60% | 160% | `Heures × Taux horaire × 1,60` |
| Jour férié (nuit) | +100% | 200% | `Heures × Taux horaire × 2,00` |

### Exemple
```
Salaire: 2 000 000 GNF
Taux horaire = 2 000 000 ÷ 173,33 = 11 539 GNF

4h HS (+30%) = 4 × 11 539 × 1,30 = 60 003 GNF
6h HS (+60%) = 6 × 11 539 × 1,60 = 110 774 GNF
──────────────────────────────────────────────
Total HS = 170 777 GNF ✅
```

---

## 2. COTISATIONS CNSS

### Paramètres

| Paramètre | Valeur |
|-----------|--------|
| **Plancher** | 550 000 GNF (SMIG) |
| **Plafond** | 2 500 000 GNF |
| **Taux salarié** | 5% |
| **Taux employeur** | 18% |

### Formules
```
Assiette CNSS = min(max(Salaire brut soumis, Plancher), Plafond)

CNSS Salarié = Assiette × 5%
CNSS Employeur = Assiette × 18%
```

### Exemples

| Salaire brut | Assiette CNSS | CNSS Salarié | CNSS Employeur |
|--------------|---------------|--------------|----------------|
| 400 000 GNF | 550 000 GNF | 27 500 GNF | 99 000 GNF |
| 1 500 000 GNF | 1 500 000 GNF | 75 000 GNF | 270 000 GNF |
| 8 000 000 GNF | 2 500 000 GNF | 125 000 GNF | 450 000 GNF |

---

## 3. RTS (Retenue à la Source) - CGI 2022

### Calcul de la base imposable
```
Base imposable = Brut - Indemnités exonérées - CNSS salarié - Déductions familiales - Abattement 5%
```

### Déductions familiales

| Situation | Montant/mois |
|-----------|--------------|
| Conjoint (marié) | 100 000 GNF |
| Par enfant (max 4) | 50 000 GNF |

### Abattement professionnel
```
Abattement = min(Base × 5%, 1 000 000 GNF)
```

### Barème RTS progressif (6 tranches)

| Tranche | De | À | Taux | Montant taxable max | Impôt max tranche |
|---------|-----|---|------|---------------------|-------------------|
| 1 | 0 | 1 000 000 | **0%** | 1 000 000 | 0 GNF |
| 2 | 1 000 001 | 3 000 000 | **5%** | 2 000 000 | 100 000 GNF |
| 3 | 3 000 001 | 5 000 000 | **8%** | 2 000 000 | 160 000 GNF |
| 4 | 5 000 001 | 10 000 000 | **10%** | 5 000 000 | 500 000 GNF |
| 5 | 10 000 001 | 20 000 000 | **15%** | 10 000 000 | 1 500 000 GNF |
| 6 | > 20 000 000 | ∞ | **20%** | illimité | - |

### Exemple de calcul RTS
```
Base nette imposable: 7 875 000 GNF

Tranche 1: 1 000 000 × 0%  =         0 GNF
Tranche 2: 2 000 000 × 5%  =   100 000 GNF
Tranche 3: 2 000 000 × 8%  =   160 000 GNF
Tranche 4: 2 875 000 × 10% =   287 500 GNF
───────────────────────────────────────────
RTS Total = 547 500 GNF ✅
```

---

## 4. CHARGES PATRONALES

### Taux et assiettes

| Charge | Taux | Assiette |
|--------|------|----------|
| CNSS Employeur | **18%** | Plafonnée (550K - 2,5M) |
| Versement Forfaitaire (VF) | **6%** | Brut total |
| Taxe d'Apprentissage (TA) | **1,5%** | Brut total |
| Contribution ONFPP | **1,5%** | Brut total |

### Formules
```
CNSS Employeur = Assiette plafonnée × 18%
VF = Brut total × 6%
TA = Brut total × 1,5%
ONFPP = Brut total × 1,5%

Total Charges = CNSS Employeur + VF + TA + ONFPP
```

### Exemple (Brut = 8 000 000 GNF)
```
CNSS Employeur = 2 500 000 × 18% = 450 000 GNF
VF = 8 000 000 × 6% = 480 000 GNF
TA = 8 000 000 × 1,5% = 120 000 GNF
ONFPP = 8 000 000 × 1,5% = 120 000 GNF
────────────────────────────────────────────
Total Charges = 1 170 000 GNF ✅
```

---

## 5. PLAFOND 25% INDEMNITÉS FORFAITAIRES

### Règle
> Les indemnités forfaitaires (transport, logement, repas) sont exonérées de RTS **dans la limite de 25% du brut**.

### Formules
```
Plafond exonéré = Brut × 25%

Si Indemnités ≤ Plafond → Entièrement exonérées
Si Indemnités > Plafond → Excédent réintégré dans base RTS
```

### Seuil pratique
```
Pour respecter le plafond 25% du brut:
Indemnités max = Salaire de base × 33,33%
```

### Exemple
```
Salaire base: 3 000 000 GNF
Indemnités: 1 500 000 GNF
Brut = 4 500 000 GNF

Plafond 25% = 4 500 000 × 25% = 1 125 000 GNF
Excédent = 1 500 000 - 1 125 000 = 375 000 GNF

→ 375 000 GNF réintégrés dans la base RTS ✅
```

---

## 6. EXONÉRATIONS RTS

### Stagiaires / Apprentis

| Condition | Valeur |
|-----------|--------|
| Type contrat | Stage ou Apprentissage |
| Durée max | 12 mois |
| Indemnité max | 1 200 000 GNF/mois |

```
Si (Contrat = Stage/Apprentissage) 
   ET (Durée ≤ 12 mois) 
   ET (Indemnité ≤ 1 200 000 GNF)
→ RTS = 0 GNF ✅
```

---

## 7. CONGÉS PAYÉS

### Acquisition
```
Droit de base = 1,5 jour ouvrable/mois = 18 jours/an

Majoration ancienneté:
- 5-9 ans: +2 jours
- 10-14 ans: +4 jours
- 15-19 ans: +6 jours
- 20+ ans: +8 jours
```

### Indemnité de congés
```
Indemnité = (Salaire mensuel × 12) ÷ 12 × (Jours de congé ÷ 30)
         = Salaire mensuel × (Jours de congé ÷ 30)
```

---

## 8. INDEMNITÉ DE LICENCIEMENT

### Barème
```
1-5 ans:    25% du salaire moyen × années
6-10 ans:   30% du salaire moyen × années
> 10 ans:   40% du salaire moyen × années
```

### Exemple (12,5 ans, salaire 3 000 000 GNF)
```
5 ans × 3 000 000 × 25% = 3 750 000 GNF
5 ans × 3 000 000 × 30% = 4 500 000 GNF
2,5 ans × 3 000 000 × 40% = 3 000 000 GNF (proratisé: 1 125 000)
──────────────────────────────────────────
Total = 9 375 000 GNF ✅
```

---

## 9. PRÉAVIS

### Durée selon ancienneté

| Ancienneté | Durée préavis |
|------------|---------------|
| < 1 an | 1 mois |
| 1-5 ans | 2 mois |
| > 5 ans | 3 mois |

### Indemnité compensatrice
```
Indemnité = Salaire mensuel × Mois de préavis
```

---

## 10. CONGÉ MATERNITÉ

### Durée
```
Durée normale: 98 jours (14 semaines)
Prolongation possible: +21 jours (complications)
```

### Indemnité journalière CNSS
```
Indemnité = Moyenne 3 derniers mois ÷ 30
```

---

## 📊 FORMULE RÉCAPITULATIVE DU NET À PAYER

```
┌─────────────────────────────────────────────────────────────────────────┐
│  NET À PAYER = BRUT - CNSS Salarié - RTS - Autres retenues              │
│                                                                         │
│  Où:                                                                    │
│  • BRUT = Salaire base + Primes + Indemnités + HS                       │
│  • CNSS Salarié = min(max(Base CNSS, 550K), 2,5M) × 5%                  │
│  • RTS = Calcul progressif sur (Brut - Indemnités exonérées - CNSS -   │
│          Déductions familiales - Abattement 5%)                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

*Document de référence - Conforme CGI 2022 et Code du Travail guinéen*
*Gestionnaire RH Guinée - www.guineerh.space*
