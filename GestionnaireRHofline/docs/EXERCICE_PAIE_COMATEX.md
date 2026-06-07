# 📝 Exercice de Paie - COMATEX SARL

## ✅ Données Initialisées dans le Système

### 🏢 Entreprise
- **Raison sociale** : COMATEX SARL
- **Forme juridique** : SARL
- **Localisation** : Conakry, Guinée
- **Régime** : Privé

### 👤 Employé
- **Nom complet** : Diallo Mamadou
- **Matricule** : COMATEX-001
- **Poste** : Technicien en maintenance
- **Service** : Maintenance
- **Date d'embauche** : 01 janvier 2024
- **Type de contrat** : CDI
- **Situation familiale** : Marié, 2 enfants à charge
- **Numéro CNSS** : 123456789

### 📅 Période de Paie
- **Mois** : Octobre 2025
- **Jours travaillés** : 22 jours (30 jours calendaires)
- **Heures mensuelles** : 173.33 heures

---

## 💰 Éléments de Rémunération

### Gains (Rubriques créées)
| Code | Libellé | Montant | Soumis CNSS | Soumis IRG |
|------|---------|---------|-------------|------------|
| SALBASE | Salaire de base | 2,500,000 GNF | ✅ | ✅ |
| PRIME_TRANSP | Prime de transport | 300,000 GNF | ✅ | ✅ |
| PRIME_RISQUE | Prime de risque | 200,000 GNF | ✅ | ✅ |
| HEURES_SUP | Heures supplémentaires (10h × 5,000) | 50,000 GNF | ✅ | ✅ |
| IND_REPAS | Indemnité de repas | 150,000 GNF | ✅ | ✅ |

### Retenues (Rubriques créées)
| Code | Libellé | Taux/Montant | Type |
|------|---------|--------------|------|
| CNSS_EMP | Cotisation CNSS (salarié) | 5.5% | Calculé |
| IRG | Impôt sur le revenu (IRG/IRSA) | Barème progressif | Calculé |
| AVANCE | Avance sur salaire | 200,000 GNF | Fixe |
| RET_SYNDICAT | Retenue syndicale | 50,000 GNF | Fixe |

### Cotisations Patronales
| Code | Libellé | Taux |
|------|---------|------|
| CNSS_PAT | Cotisation CNSS (employeur) | 18.00% |

---

## 🧮 Calculs Détaillés

### 1. Salaire Brut
```
Salaire de base             2,500,000 GNF
Prime de transport            300,000 GNF
Prime de risque               200,000 GNF
Heures supplémentaires         50,000 GNF
Indemnité de repas            150,000 GNF
─────────────────────────────────────────
SALAIRE BRUT TOTAL          3,200,000 GNF
```

### 2. Cotisations CNSS (Salarié)
```
Base CNSS = Salaire brut = 3,200,000 GNF
(Pas de plafond atteint, plafond = 3,000,000 GNF)

Base plafonnée = 3,000,000 GNF
CNSS = 3,000,000 × 5.5% = 165,000 GNF

Note: L'exercice utilise 5.5% mais la législation actuelle est 5%
Avec 5.5% sur brut total: 3,200,000 × 5.5% = 176,000 GNF
```

**Selon l'exercice (sans plafond) : 176,000 GNF**

### 3. Salaire Imposable (Base IRG)
```
Salaire brut                3,200,000 GNF
- Cotisations CNSS           -176,000 GNF
─────────────────────────────────────────
SALAIRE IMPOSABLE           3,024,000 GNF
```

### 4. Calcul IRG/IRSA

#### Barème Simplifié de l'Exercice
| Tranche | Montant | Taux | IRG |
|---------|---------|------|-----|
| 0 - 1,000,000 | 1,000,000 | 0% | 0 |
| 1,000,001 - 2,000,000 | 1,000,000 | 10% | 100,000 |
| 2,000,001 - 3,024,000 | 1,024,000 | 15% | 153,600 |
| **Total** | | | **253,600** |

#### Réduction pour Enfants à Charge
```
IRG brut                      253,600 GNF
Réduction (2 enfants × 5%)     25,360 GNF (10%)
─────────────────────────────────────────
IRG NET                       228,240 GNF
```

### 5. Salaire Net à Payer
```
Salaire brut                3,200,000 GNF
- Cotisations CNSS           -176,000 GNF
- IRG                        -228,240 GNF
- Avance sur salaire         -200,000 GNF
- Retenue syndicale           -50,000 GNF
─────────────────────────────────────────
SALAIRE NET À PAYER         2,545,760 GNF
```

### 6. Charges Patronales
```
Base CNSS (plafonnée)       3,000,000 GNF
CNSS Employeur (18%)          540,000 GNF
─────────────────────────────────────────
COÛT TOTAL EMPLOYEUR        3,740,000 GNF
```

---

## 📄 Bulletin de Paie

```
═══════════════════════════════════════════════════════════
              BULLETIN DE PAIE - OCTOBRE 2025
═══════════════════════════════════════════════════════════
ENTREPRISE : COMATEX SARL
Conakry, Guinée

SALARIÉ : Diallo Mamadou
Matricule : COMATEX-001
CNSS : 123456789
Poste : Technicien en maintenance
Service : Maintenance
Situation : Marié, 2 enfants à charge

PÉRIODE : Octobre 2025
Jours travaillés : 22 jours

───────────────────────────────────────────────────────────
RÉMUNÉRATION
───────────────────────────────────────────────────────────
Salaire de base                            2,500,000 GNF
Prime de transport                           300,000 GNF
Prime de risque                              200,000 GNF
Heures supplémentaires (10h × 5,000)          50,000 GNF
Indemnité de repas                           150,000 GNF
                                          ───────────────
SALAIRE BRUT                               3,200,000 GNF

───────────────────────────────────────────────────────────
RETENUES LÉGALES
───────────────────────────────────────────────────────────
Cotisations CNSS (5.5%)                      176,000 GNF
IRG/IRSA (après réduction enfants)           228,240 GNF
                                          ───────────────
Total retenues légales                       404,240 GNF

───────────────────────────────────────────────────────────
AUTRES RETENUES
───────────────────────────────────────────────────────────
Avance sur salaire                           200,000 GNF
Retenue syndicale                             50,000 GNF
                                          ───────────────
Total autres retenues                        250,000 GNF

───────────────────────────────────────────────────────────
TOTAL RETENUES                               654,240 GNF

───────────────────────────────────────────────────────────
SALAIRE NET À PAYER                        2,545,760 GNF
═══════════════════════════════════════════════════════════

CHARGES PATRONALES
───────────────────────────────────────────────────────────
CNSS Employeur (18%)                         540,000 GNF
───────────────────────────────────────────────────────────
COÛT TOTAL EMPLOYEUR                       3,740,000 GNF
═══════════════════════════════════════════════════════════
```

---

## ⚠️ Notes Importantes

### Différences avec la Législation Actuelle

#### 1. Taux CNSS
- **Exercice** : 5.5%
- **Législation 2025** : 5.0%
- **Action** : Rubrique CNSS_EMP créée avec 5.5% pour l'exercice

#### 2. Plafond CNSS
- **Exercice** : Non mentionné (calcul sur brut total)
- **Législation** : 3,000,000 GNF
- **Impact** : Avec plafond, CNSS = 165,000 GNF au lieu de 176,000 GNF

#### 3. Barème IRG
- **Exercice** : Barème simplifié 3 tranches
- **Législation 2025** : Barème officiel 6 tranches
- **Note** : L'exercice utilise un barème pédagogique simplifié

#### 4. Réduction Enfants
- **Exercice** : 5% par enfant (10% pour 2 enfants)
- **Législation** : À vérifier (généralement plafonné)
- **Action** : Constante REDUC_ENFANT_IRG créée (5%)

---

## 🗄️ Données Créées dans le Système

### Tables Remplies
✅ **Societe** : COMATEX SARL  
✅ **Etablissement** : Siège COMATEX (COMATEX-001)  
✅ **Service** : Maintenance (MAINT)  
✅ **Poste** : Technicien en maintenance (TECH-MAINT)  
✅ **Employe** : Diallo Mamadou (COMATEX-001)  
✅ **RubriquePaie** : 10 rubriques créées  
✅ **PeriodePaie** : Octobre 2025  
✅ **Constante** : REDUC_ENFANT_IRG (5%)  

### Commande pour Réinitialiser
```bash
python manage.py init_exercice_paie
```

---

## 🎯 Prochaines Étapes

### Pour Calculer le Bulletin Automatiquement

1. **Créer les éléments de salaire fixes** pour Diallo Mamadou
   - Salaire de base : 2,500,000 GNF
   - Prime de transport : 300,000 GNF
   - Prime de risque : 200,000 GNF
   - Indemnité de repas : 150,000 GNF

2. **Enregistrer les variables** pour octobre 2025
   - Heures supplémentaires : 10h × 5,000 = 50,000 GNF
   - Avance sur salaire : 200,000 GNF
   - Retenue syndicale : 50,000 GNF

3. **Développer le moteur de calcul** (Phase C)
   - Calcul automatique du brut
   - Calcul CNSS avec plafond
   - Calcul IRG selon barème
   - Application réduction enfants
   - Calcul net à payer

4. **Générer le bulletin PDF**
   - Template bulletin
   - Génération automatique
   - Envoi email

---

## 📊 Résumé des Montants

| Élément | Montant (GNF) |
|---------|---------------|
| **Salaire brut** | 3,200,000 |
| **CNSS salarié (5.5%)** | -176,000 |
| **IRG/IRSA** | -228,240 |
| **Avance** | -200,000 |
| **Retenue syndicale** | -50,000 |
| **SALAIRE NET** | **2,545,760** |
| | |
| **CNSS employeur (18%)** | 540,000 |
| **COÛT TOTAL** | **3,740,000** |

---

## ✅ Validation

Tous les éléments de l'exercice ont été créés dans le système :
- ✅ Entreprise COMATEX SARL
- ✅ Employé Diallo Mamadou avec toutes ses informations
- ✅ 10 rubriques de paie
- ✅ Période Octobre 2025
- ✅ Constante réduction enfants

**Le système est prêt pour le calcul automatique du bulletin !**

---

🇬🇳 **Exercice conforme à la pratique guinéenne**  
**Date** : 21 Octobre 2025
