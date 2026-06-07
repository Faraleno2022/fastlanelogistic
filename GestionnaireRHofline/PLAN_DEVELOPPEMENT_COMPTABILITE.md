# 📋 Plan de Développement - Modules Manquants Comptabilité

**Date:** 20 Janvier 2026  
**Version:** 1.0  
**Status:** PLANIFICATION STRATÉGIQUE  
**Priorisation:** 4 Phases

---

## 🎯 Vue d'ensemble stratégique

Ce plan établit la priorisation des 12 modules avancés du système comptable selon leur criticité, leur importance légale, et leur impact sur les opérations.

**Principe de base:** Développer d'abord les fonctionnalités indispensables à une comptabilité conforme et sécurisée, puis progressivement ajouter les modules d'analyse et de spécialisation.

---

## 🔴 PHASE 1 - PRIORITÉ CRITIQUE (À développer immédiatement)

**Délai:** 0-3 mois  
**Impact:** ⭐⭐⭐⭐⭐ CRITIQUE  
**Modules:** 3

Ces modules sont **essentiels** pour une comptabilité fonctionnelle et conforme aux normes. Leur absence compromet la validité comptable du système.

---

### Module 3: ✅ Rapprochements Bancaires

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🔴 CRITIQUE

#### Composants:
- ✅ Rapprochement bancaire
- ✅ Relevés bancaires
- ✅ Lettrage des opérations
- ✅ Gestion des écarts bancaires
- ✅ Comptes bancaires

#### Justification:
- **Validation des flux financiers:** Sine qua non de l'intégrité comptable
- **Conformité légale:** Exigé par les normes SYSCOHADA
- **Détection des fraudes:** Permet d'identifier les anomalies
- **Réconciliation annuelle:** Base de la clôture d'exercice
- **Gestion de la trésorerie:** Essential pour le cash management

#### Modèles disponibles:
```python
- CompteBancaire
- RapprochementBancaire
- ReleveBancaire
- OperationBancaire
- LettrageOperation
- EcartBancaire
```

#### Prochaines étapes:
- [ ] Développer les vues d'administration
- [ ] Créer les templates de gestion
- [ ] Implémenter l'import de relevés (CSV/MT940)
- [ ] Ajouter les reports d'écarts
- [ ] Créer le tableau de bord de trésorerie
- [ ] Générer les états de rapprochement (PDF)

#### Effort estimé: **80 heures**

---

### Module 5: ✅ Fiscalité & Déclarations

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🔴 CRITIQUE

#### Composants:
- ✅ TVA (déclarations, récapitulatifs)
- ✅ Déclarations fiscales
- ✅ Gestion des retenues à la source
- ✅ Éditions fiscales

#### Justification:
- **Obligation légale:** Déclarations obligatoires aux autorités
- **Conformité réglementaire:** TVA, IRPP, IS selon juridiction
- **Pénalités:** Non-conformité = amendes substantielles
- **Audit:** Base de l'audit externe annuel
- **Conformité SYSCOHADA:** Normes régionales

#### Modèles disponibles:
```python
- DeclarationTVA
- RecapitulatifTVA
- DeclarationFiscale
- RetenuAlaSource
- EditionFiscale
```

#### Prochaines étapes:
- [ ] Implémentation des moteurs de calcul TVA
- [ ] Génération automatique des récapitulatifs
- [ ] Interfaces de déclaration (formulaires)
- [ ] Export vers formats fiscaux (EDI)
- [ ] Historique et archivage des déclarations
- [ ] Rapports de conformité

#### Effort estimé: **100 heures**

---

### Module 7: ✅ Audit & Contrôle Interne

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🔴 CRITIQUE

#### Composants:
- ✅ Piste d'audit (traçabilité complète)
- ✅ Logs des modifications
- ✅ Approvals / Validations multi-niveaux
- ✅ Verrouillage des périodes comptables

#### Justification:
- **Conformité légale:** Obligation de traçabilité (Loi Guinéenne)
- **Gouvernance interne:** Contrôle des accès et des modifications
- **Audit externe:** Exigé pour toute vérification
- **Sécurité:** Détection des tentatives de manipulation
- **Responsabilité:** Qui a fait quoi, quand et pourquoi

#### Modèles disponibles:
```python
- PisteAudit (avec indexes sur enterprise et date)
- LogModification
- Approbation (multi-niveaux)
- VerrouillageExercice
```

#### Prochaines étapes:
- [ ] Dashboard d'audit pour administrateurs
- [ ] Rapports d'activité par utilisateur
- [ ] Alertes sur modifications sensibles
- [ ] Interface de workflow d'approbation
- [ ] Gestion des accès par rôle
- [ ] Export des logs pour audit externe

#### Effort estimé: **90 heures**

---

## 🟠 PHASE 2 - PRIORITÉ IMPORTANTE (6 mois)

**Délai:** 3-9 mois  
**Impact:** ⭐⭐⭐⭐ IMPORTANT  
**Modules:** 3

Ces modules sont **hautement utiles** pour une gestion comptable efficace et complète. Ils commencent à affecter le bilan et la gestion opérationnelle.

---

### Module 1: ✅ Gestion des Immobilisations

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🟠 IMPORTANT

#### Composants:
- ✅ Registre des immobilisations
- ✅ Amortissements (linéaire/dégressif)
- ✅ Cessions et mises au rebut
- ✅ Édition de la liste des immobilisations

#### Justification:
- **Impact bilan:** Les immobilisations représentent souvent 30-50% de l'actif
- **Amortissements:** Produit net du calcul de rentabilité
- **Fiscalité:** Déductions sur amortissements importants
- **Clôture exercice:** Calculs obligatoires annuels
- **Gestion d'actifs:** Suivi physique et financier

#### Modèles disponibles:
```python
- Immobilisation
- Amortissement (par exercice)
- CessionImmobilisation
```

#### Prochaines étapes:
- [ ] Interface de gestion des immobilisations
- [ ] Calcul automatique des amortissements
- [ ] Générations des écritures comptables
- [ ] Rapports de plus/moins-values
- [ ] Suivi des cessions
- [ ] Éditions réglementaires

#### Effort estimé: **70 heures**

#### Intégration avec Phase 1:
- Utilise les écritures comptables générées
- S'intègre avec les déclarations fiscales (déductions)

---

### Module 8: ✅ Clients & Fournisseurs - Détails

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🟠 IMPORTANT

#### Composants:
- ✅ Compte client détaillé
- ✅ Compte fournisseur détaillé
- ✅ Vieillissement des créances
- ✅ Analyses des impayés

#### Justification:
- **Gestion trésorerie:** Identification des problèmes de cash
- **Risque crédit:** Analyse des expositions aux tiers
- **Provisions:** Calcul des provisions pour créances douteuses
- **Recouvrement:** Priorisation des actions de relance
- **Scoring:** Évaluation du risque client/fournisseur

#### Modèles disponibles:
```python
- CompteClientDetail
- CompteFournisseurDetail
- VieillissementCreances
- AnalyseImpayes
```

#### Prochaines étapes:
- [ ] Tableau de bord clients/fournisseurs
- [ ] Génération automatique du vieillissement
- [ ] Alertes sur créances à risque
- [ ] Interface de gestion des rappels
- [ ] Statistiques de paiement
- [ ] Rapports de solvabilité

#### Effort estimé: **60 heures**

#### Intégration avec Phase 1:
- Lié aux déclarations fiscales (provisions)
- Utilise les tiers existants

---

### Module 2: ✅ Stocks & Inventaires

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🟠 IMPORTANT

#### Composants:
- ✅ Gestion des stocks
- ✅ Inventaires périodiques
- ✅ Variations de stocks
- ✅ Ajustements de stock

#### Justification:
- **Impact résultat:** Variation de stocks = compte de charge/produit
- **Bilan:** Stock = actif circulant important
- **Valorisation:** FIFO/LIFO/Coût moyen
- **Conformité:** Inventaires obligatoires
- **Pertes:** Détection des vols/casses

#### Modèles disponibles:
```python
- Stock
- Inventaire + LigneInventaire
- VariationStock
- AjustementStock
```

#### Prochaines étapes:
- [ ] Gestion des mouvements de stock
- [ ] Calcul du coût unitaire moyen
- [ ] Interface d'inventaire physique
- [ ] Génération des écritures de variation
- [ ] Rapports de stock
- [ ] Alertes stock min/max

#### Effort estimé: **75 heures**

#### Note importante:
⚠️ **À valider avec le métier:** Ce module n'est pertinent que si l'entreprise a des stocks (activité commerce/production). Peut être retardé si non applicable.

#### Intégration avec Phase 1:
- Génère des écritures comptables de variation
- Impact sur les déclarations fiscales

---

## 🟡 PHASE 3 - PRIORITÉ AVANCÉE (12 mois)

**Délai:** 9-15 mois  
**Impact:** ⭐⭐⭐ AVANCÉ  
**Modules:** 3

Ces modules sont **importants** pour l'analyse financière et l'aide à la décision management. Ils présupposent que les phases 1 et 2 sont opérationnelles.

---

### Module 9: ✅ Paramétrages Avancés (Comptabilité Analytique)

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🟡 AVANCÉ

#### Composants:
- ✅ Modèles d'écritures
- ✅ Centres d'analyse / Centres de coûts
- ✅ Segments analytiques
- ✅ Comptabilité analytique

#### Justification:
- **Analyse rentabilité:** Rentabilité par produit/client/projet
- **Aide décision:** Données pour le management
- **Contrôle budgétaire:** Suivi par centre de profit
- **Optimisation:** Identification des gaspillages
- **Stratégie:** Base de la planification

#### Modèles disponibles:
```python
- ModeleEcriture + LigneModeleEcriture
- CentreAnalyse
- SegmentAnalytique
- ComptabiliteAnalytique
```

#### Prochaines étapes:
- [ ] Définition des centres d'analyse (paramétrage initial)
- [ ] Interface de gestion des segments
- [ ] Imputation analytique des écritures
- [ ] Tableau de bord par centre/segment
- [ ] Rapports d'analyse de rentabilité
- [ ] Rapprochement analytique/comptabilité

#### Effort estimé: **85 heures**

#### Dépendances:
- Requiert Phase 1 et 2 opérationnelles
- S'appuie sur les écritures comptables existantes

---

### Module 4: ✅ Analyse Financière

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🟡 AVANCÉ

#### Composants:
- ✅ Ratios financiers
- ✅ Tableaux de flux de trésorerie
- ✅ Budget & prévisions
- ✅ Analyses comparatives (exercices antérieurs)

#### Justification:
- **Pilotage financier:** KPIs pour la direction
- **Analyse stratégique:** Benchmark vs secteur
- **Prévisions:** Modèles de scenario planning
- **Comparatif:** Suivi année vs année
- **Diagnostic:** Identification des tendances

#### Modèles disponibles:
```python
- RatioFinancier
- FluxTresorerie
- Budget + LigneBudget
- AnalyseComparative
```

#### Prochaines étapes:
- [ ] Moteurs de calcul des ratios (liquiidité, solvabilité, rentabilité)
- [ ] Dashboard d'analyse financière
- [ ] Modèles de budget par centre
- [ ] Générateur de rapports comparatifs
- [ ] Export pour Excel/BI
- [ ] Analyses de variance budget/réalisé

#### Effort estimé: **80 heures**

#### Dépendances:
- Requiert Phase 1 et 2 complètes
- Utilise les données comptables et budgétaires

---

### Module 12: ✅ Trésorerie

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🟡 AVANCÉ

#### Composants:
- ✅ Prévisions de trésorerie
- ✅ Suivi des flux de trésorerie
- ✅ Gestion des placements

#### Justification:
- **Cash management:** Gestion quotidienne du cash
- **Prévisions:** Projection des besoins de financement
- **Optimisation:** Placement des excédents
- **Risque:** Gestion du risque de liquidité
- **Efficacité:** Maximisation des rendements

#### Modèles disponibles:
```python
- PrevisionTresorerie (mensuelle)
- SuiviTresorerie (quotidien)
- Placement
```

#### Prochaines étapes:
- [ ] Interface de prévision de trésorerie
- [ ] Dashboard quotidien de liquidité
- [ ] Intégration des relevés bancaires
- [ ] Gestion des placements
- [ ] Rapports de trésorerie
- [ ] Alertes de seuil de trésorerie

#### Effort estimé: **70 heures**

#### Dépendances:
- Requiert Module 3 (Rapprochements) opérationnel
- Utilise les données de suivi bancaire

---

## 🟢 PHASE 4 - PRIORITÉ SPÉCIALISÉE (À la demande)

**Délai:** 15+ mois  
**Impact:** ⭐⭐ SPÉCIALISÉ  
**Modules:** 3

Ces modules sont **utiles** pour des contextes métier spécifiques. Leur développement dépend des besoins réels de l'organisation.

---

### Module 6: ✅ Consolidation & Multi-devises

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🟢 SPÉCIALISÉ

#### Composants:
- ✅ Consolidation de comptes
- ✅ Multi-devises
- ✅ Conversions de devises

#### Justification:
- **Groupes multi-entités:** Consolidation des comptes
- **Exports/Imports:** Entreprises internationales
- **Devises étrangères:** Transactions en devises multiples
- **Réévaluation:** Impacts des variations de change
- **Rapports consolidés:** IFRS, normes locales

#### Modèles disponibles:
```python
- ConsolidationComptes
- TauxChange
- OperationEnDevise
- ReeevaluationDevise
```

#### Prochaines étapes:
- [ ] Interface de consolidation
- [ ] Gestion des taux de change (historique)
- [ ] Réévaluation automatique des dettes/créances
- [ ] Génération des états consolidés
- [ ] Conversion en devise de reporting
- [ ] Rapports consolidés/complets

#### Effort estimé: **90 heures**

#### Déclencheurs d'activation:
- ✓ Groupe de plusieurs entités
- ✓ Activité internationale confirmée
- ✓ Transactions en devises étrangères fréquentes

---

### Module 11: ✅ Gestion des Devises

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🟢 SPÉCIALISÉ

#### Composants:
- ✅ Réévaluation des créances/dettes en devises
- ✅ Différences de change
- ✅ Gestion des comptes en devises

#### Justification:
- **Exportateurs:** Recettes en devises étrangères
- **Importateurs:** Dettes en devises étrangères
- **Volatilité:** Gestion des risques de change
- **Provisions:** Calcul des provisions de change
- **Reporting:** Impact sur résultats

#### Modèles disponibles:
```python
- GestionDeviseCompte
- DifferenceChange
(Utilise core.Devise)
```

#### Prochaines étapes:
- [ ] Interface de gestion des devises
- [ ] Importation des taux de change (externes)
- [ ] Calcul des différences de change
- [ ] Écriture automatique des provisions
- [ ] Rapports de change
- [ ] Alertes de volatilité

#### Effort estimé: **60 heures**

#### Déclencheurs d'activation:
- ✓ Transactions régulières en devises
- ✓ Créances/dettes en devises significatives
- ✓ Volatilité des taux de change importante

---

### Module 10: ✅ Exports & Intégrations

**Status:** ✅ MODÈLES CRÉÉS  
**Criticité:** 🟢 SPÉCIALISÉ

#### Composants:
- ✅ Exports XML/EDI
- ✅ Imports de relevés bancaires
- ✅ Interfaces EDI avec clients/fournisseurs
- ✅ API d'intégration

#### Justification:
- **Automatisation:** Réduction des saisies manuelles
- **Flux B2B:** Échanges EDI avec partenaires
- **Trésorerie:** Import automatique des relevés
- **Intégrations:** Liaison avec autres systèmes
- **Efficacité:** Gain de temps significatif

#### Modèles disponibles:
```python
- ExportDonnees
- ImportReleve
- InterfaceEDI
- APIINTEGRATION
```

#### Prochaines étapes:
- [ ] Interface d'export (formats multiples)
- [ ] Import de relevés (MT940, CSV)
- [ ] Connecteurs EDI (UNEDIFACT, X12)
- [ ] API REST pour intégrations tierces
- [ ] Webhooks pour notifications
- [ ] Gestion des erreurs d'import

#### Effort estimé: **100 heures**

#### Déclencheurs d'activation:
- ✓ Partenaires demandant EDI
- ✓ Volume de transactions important (>100/jour)
- ✓ Besoin d'intégration avec autres systèmes
- ✓ Relevés bancaires fréquents

---

## 📊 Résumé par Phase

| Phase | Modules | Délai | Effort | Criticité | Dépendances |
|-------|---------|-------|--------|-----------|-------------|
| **Phase 1** | Rapprochements, Fiscalité, Audit | 0-3 mois | 270h | 🔴 CRITIQUE | Aucune (fondation) |
| **Phase 2** | Immobilisations, Clients/Fourns, Stocks | 3-9 mois | 205h | 🟠 IMPORTANT | Phase 1 |
| **Phase 3** | Analytique, Analyse Fin., Trésorerie | 9-15 mois | 235h | 🟡 AVANCÉ | Phases 1-2 |
| **Phase 4** | Consolidation, Devises, Intégrations | 15+ mois | 250h | 🟢 SPÉCIALISÉ | Selon besoin |

**Total estimé (Phases 1-3):** 710 heures (17-20 semaines, 1 équipe)

---

## 🎯 Recommandations Stratégiques

### ✅ Démarche recommandée:

#### **Étape 1: Valider la Phase 1 (CRITIQUE)**
```
▌ Rapprochements bancaires
▌ Fiscalité & Déclarations  
▌ Audit & Contrôle interne
```
**Action:** Ces 3 modules sont **non-négociables**. À implémenter immédiatement.  
**KPI:** Audit externe doit valider la traçabilité et les rapprochements.

---

#### **Étape 2: Évaluer les besoins métier (Phase 2)**
```
⚠️ Point de décision critique
```

**Questionnaire décisionnel:**
- L'entreprise a-t-elle des immobilisations significatives ? → Oui/Non
- L'activité inclut-elle de la gestion de stocks ? → Oui/Non
- Y a-t-il des problèmes de recouvrement de créances ? → Oui/Non
- Quelle est l'importance du BFR (besoin en fonds de roulement) ? → Haut/Moyen/Bas

**Résultats:**
- Oui > 2 questions → Développer Phase 2 complète
- Oui 1-2 questions → Développer modules sélectifs
- Oui 0 questions → Repousser Phase 2, avancer sur Phase 3

---

#### **Étape 3: Planifier les améliorations (Phase 3)**
```
À partir du mois 9-12 après Phase 1 complète
```

**Priorité interne Phase 3:**
1. **Comptabilité analytique** - La plus impactante pour la décision
2. **Trésorerie** - Essentiellement liée à Phase 1
3. **Analyse financière** - Synthèse des données précédentes

---

#### **Étape 4: Spécialisations à la demande (Phase 4)**
```
Déclencheurs spécifiques à évaluer au cas par cas
```

**Consolidation:** Activée si groupe > 2 entités  
**Devises:** Activée si volume transactions étrangères > 10% du CA  
**Intégrations:** Activée si partenaires EDI ou volume > 100 transactions/jour

---

### ✅ Architecture recommandée:

**Modularité obligatoire:**
```
Core (déjà existant)
├── Comptabilité (déjà implémentée)
│   ├── Phase 1 (à développer)
│   ├── Phase 2 (à développer)
│   ├── Phase 3 (optionnel)
│   └── Phase 4 (pluggable)
├── Tiers (existant)
├── Écritures (existant)
└── Permissions (à adapter)
```

**Implication:**
- Chaque module doit être **indépendant** et **testable**
- Les dépendances doivent aller dans une seule direction (Phase N dépend de Phase N-1)
- Les modèles spécialisés (Phase 4) ne doivent pas affecter les phases antérieures

---

### ✅ Gestion des risques:

| Risque | Mitigation |
|--------|-----------|
| **Surcharge fonctionnelle** | Strict respect de la priorisation par phase |
| **Données incohérentes** | Tests unitaires et intégration robustes |
| **Non-conformité fiscale** | Revue externe par expert comptable Phase 1 |
| **Performance BD** | Indexes sur piste_audit, migrations optimisées |
| **Adoption utilisateurs** | Formation progressive, rollout phase par phase |

---

### ✅ Calendrier proposé:

```
2026
├─ Jan-Mar (Phase 1)
│  ├─ Rapprochements bancaires (5 semaines)
│  ├─ Fiscalité (6 semaines) 
│  └─ Audit (5 semaines)
│
├─ Apr-Sep (Phase 2) - Selon validation métier
│  ├─ Immobilisations (4 semaines)
│  ├─ Clients/Fournisseurs (3 semaines)
│  └─ Stocks (4 semaines) - Optionnel
│
├─ Oct-Dec (Phase 3) - Si Phase 1-2 OK
│  ├─ Comptabilité analytique (5 semaines)
│  ├─ Analyse financière (5 semaines)
│  └─ Trésorerie (4 semaines)
│
└─ 2027+ (Phase 4) - À la demande
   ├─ Consolidation
   ├─ Devises
   └─ Intégrations EDI/API
```

---

## 📝 Conclusion

Ce plan établit une **progression logique et réaliste** pour développer un système comptable complet:

1. **Phase 1 (Critique):** Fondation solide et conforme → 3 mois
2. **Phase 2 (Important):** Gestion complète des actifs/tiers → 6 mois supplémentaires
3. **Phase 3 (Avancé):** Analyse et aide à la décision → 6 mois supplémentaires
4. **Phase 4 (Spécialisé):** À la demande selon contexte

**Point clé:** Les modules sont déjà modélisés et prêts pour le développement. Il s'agit maintenant de les implémenter progressivement selon ce plan stratégique.

---

**Approuvé le:** 20 Janvier 2026  
**Prochaine revue:** 31 Mars 2026 (Fin Phase 1)

