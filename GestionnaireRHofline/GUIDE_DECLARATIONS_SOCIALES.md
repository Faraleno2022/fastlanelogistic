# 📋 GUIDE : EFFECTUER UNE DÉCLARATION SOCIALE

**Date** : 22 Octobre 2025  
**Module** : Paie → Déclarations Sociales

---

## 🎯 OBJECTIF

Générer et soumettre les déclarations sociales mensuelles obligatoires :
- **CNSS** (Caisse Nationale de Sécurité Sociale)
- **RTS** (Impôt sur le Revenu)
- **INAM** (Institut National d'Assurance Maladie)

---

## 📍 ACCÈS

**URL** : `http://127.0.0.1:8000/paie/declarations/`

**Navigation** :
```
Sidebar → RAPPORTS → Déclarations
```

---

## 📊 ÉTAPES POUR EFFECTUER UNE DÉCLARATION

### **ÉTAPE 1 : Calculer les Bulletins du Mois**

**Avant de faire une déclaration, vous devez avoir calculé les bulletins de paie du mois !**

1. **Aller** sur `/paie/periodes/`
2. **Sélectionner** la période (ex: Octobre 2025)
3. **Cliquer** sur "Calculer la Période"
4. ✅ **Tous les bulletins** sont générés

---

### **ÉTAPE 2 : Accéder aux Déclarations**

1. **Aller** sur `/paie/declarations/`
2. **Sélectionner** :
   - Année : 2025
   - Mois : 10 (Octobre)
3. **Cliquer** sur "Filtrer"

---

### **ÉTAPE 3 : Vérifier les Montants**

La page affiche automatiquement :

#### **📊 CNSS**
```
┌────────────────────────────────────┐
│ Nombre de salariés : 45            │
│ Masse salariale : 112,500,000 GNF  │
│ Cotisation employé (5%) : 5,625,000│
│ Cotisation employeur (18%) : 20,250│
│ TOTAL À VERSER : 25,875,000 GNF    │
└────────────────────────────────────┘
```

#### **💰 RTS**
```
┌────────────────────────────────────┐
│ Nombre de salariés : 45            │
│ Masse imposable : 112,500,000 GNF  │
│ RTS retenu : 8,437,500 GNF         │
│ TOTAL À VERSER : 8,437,500 GNF     │
└────────────────────────────────────┘
```

#### **🏥 INAM**
```
┌────────────────────────────────────┐
│ Masse salariale : 112,500,000 GNF  │
│ Taux INAM : 2.5%                   │
│ TOTAL À VERSER : 2,812,500 GNF     │
└────────────────────────────────────┘
```

---

### **ÉTAPE 4 : Exporter la Déclaration**

#### **Option 1 : Imprimer (PDF)**

1. **Cliquer** sur le bouton "Imprimer" en haut à droite
2. **Sélectionner** "Enregistrer au format PDF"
3. **Nommer** le fichier : `Declaration_Octobre_2025.pdf`
4. **Enregistrer**

#### **Option 2 : Exporter Excel** (À AJOUTER)

*Fonctionnalité à développer*

---

### **ÉTAPE 5 : Soumettre aux Organismes**

#### **🏛️ CNSS**

**Délai** : Avant le 15 du mois suivant

**Documents à fournir** :
- ✅ Bordereau de déclaration (PDF généré)
- ✅ Liste nominative des salariés
- ✅ Chèque ou virement : 25,875,000 GNF

**Où soumettre** :
- En ligne : [Site CNSS Guinée]
- Physique : Agence CNSS locale

---

#### **💰 RTS (Trésor Public)**

**Délai** : Avant le 10 du mois suivant

**Documents à fournir** :
- ✅ Déclaration RTS (PDF généré)
- ✅ État récapitulatif par employé
- ✅ Paiement : 8,437,500 GNF

**Où soumettre** :
- Centre des Impôts de rattachement

---

#### **🏥 INAM**

**Délai** : Avant le 15 du mois suivant

**Documents à fournir** :
- ✅ Déclaration INAM (PDF généré)
- ✅ Paiement : 2,812,500 GNF

**Où soumettre** :
- Agence INAM locale

---

## 📋 DÉTAIL DES DÉCLARATIONS

### **1. DÉCLARATION CNSS**

#### **Calcul**

```
Masse Salariale = Somme des salaires bruts
Cotisation Employé = Masse Salariale × 5%
Cotisation Employeur = Masse Salariale × 18%
Total CNSS = Cotisation Employé + Cotisation Employeur
```

#### **Exemple**
```
Masse Salariale : 112,500,000 GNF
Cotisation Employé : 112,500,000 × 5% = 5,625,000 GNF
Cotisation Employeur : 112,500,000 × 18% = 20,250,000 GNF
TOTAL : 25,875,000 GNF
```

#### **Qui paie quoi ?**
- **Employé** : 5% (retenu sur le salaire)
- **Employeur** : 18% (charge patronale)
- **Total versé** : 23% de la masse salariale

---

### **2. DÉCLARATION RTS**

#### **Calcul**

L'RTS est calculé par **tranches progressives** :

```
Tranche 1 : 0 - 1,000,000 GNF → 0%
Tranche 2 : 1,000,001 - 3,000,000 → 5%
Tranche 3 : 3,000,001 - 6,000,000 → 10%
Tranche 4 : 6,000,001 - 12,000,000 → 15%
Tranche 5 : > 12,000,000 → 20%
```

#### **Exemple pour un salaire de 5,000,000 GNF**
```
Tranche 1 : 1,000,000 × 0% = 0
Tranche 2 : 2,000,000 × 5% = 100,000
Tranche 3 : 2,000,000 × 10% = 200,000
RTS Total = 300,000 GNF
```

#### **Qui paie ?**
- **Employé** : 100% (retenu à la source)
- **Employeur** : Reverse au Trésor Public

---

### **3. DÉCLARATION INAM**

#### **Calcul**

```
Cotisation INAM = Masse Salariale × 2.5%
```

#### **Exemple**
```
Masse Salariale : 112,500,000 GNF
Cotisation INAM : 112,500,000 × 2.5% = 2,812,500 GNF
```

#### **Qui paie ?**
- **Employeur** : 2.5% (charge patronale)

---

## 📊 RÉCAPITULATIF MENSUEL

### **Exemple : Octobre 2025**

| Organisme | Base | Taux | Montant | Délai |
|-----------|------|------|---------|-------|
| **CNSS Employé** | 112,500,000 | 5% | 5,625,000 | 15/11 |
| **CNSS Employeur** | 112,500,000 | 18% | 20,250,000 | 15/11 |
| **RTS** | Variable | Variable | 8,437,500 | 10/11 |
| **INAM** | 112,500,000 | 2.5% | 2,812,500 | 15/11 |
| **TOTAL** | - | - | **37,125,000** | - |

---

## 🔄 WORKFLOW COMPLET

```
1. Calculer les Bulletins
   ↓
   /paie/periodes/ → [Calculer]
   ↓
2. Générer les Déclarations
   ↓
   /paie/declarations/ → Filtrer par mois
   ↓
3. Vérifier les Montants
   ↓
   Contrôler CNSS, RTS, INAM
   ↓
4. Exporter les Documents
   ↓
   [Imprimer] → PDF
   ↓
5. Effectuer les Paiements
   ↓
   Virement ou Chèque
   ↓
6. Soumettre aux Organismes
   ↓
   CNSS (15/11), RTS (10/11), INAM (15/11)
   ↓
7. ✅ Déclarations Complètes
```

---

## 📅 CALENDRIER DES DÉCLARATIONS

### **Mensuel**

| Déclaration | Délai | Organisme |
|-------------|-------|-----------|
| **RTS** | 10 du mois suivant | Trésor Public |
| **CNSS** | 15 du mois suivant | CNSS |
| **INAM** | 15 du mois suivant | INAM |

### **Exemple pour Octobre 2025**

- ✅ **10 Novembre** : Verser RTS (8,437,500 GNF)
- ✅ **15 Novembre** : Verser CNSS (25,875,000 GNF)
- ✅ **15 Novembre** : Verser INAM (2,812,500 GNF)

---

## 📄 DOCUMENTS À CONSERVER

### **Pour chaque déclaration**

1. ✅ PDF de la déclaration
2. ✅ Preuve de paiement (reçu, virement)
3. ✅ Liste nominative des employés
4. ✅ Détail des calculs

### **Durée de conservation**

**10 ans minimum** (obligation légale)

---

## ⚠️ PÉNALITÉS EN CAS DE RETARD

### **CNSS**
- Retard de paiement : **Pénalité de 2% par mois**
- Fausse déclaration : **Amende + redressement**

### **RTS**
- Retard de paiement : **Pénalité de 10%**
- Non-déclaration : **Amende fiscale**

### **INAM**
- Retard de paiement : **Pénalité de 1.5% par mois**

---

## ✅ CHECKLIST MENSUELLE

### **Avant le 10 du mois**

- [ ] Calculer tous les bulletins du mois précédent
- [ ] Vérifier les montants CNSS, RTS, INAM
- [ ] Exporter les déclarations en PDF
- [ ] Préparer les virements
- [ ] **Verser l'RTS au Trésor Public**

### **Avant le 15 du mois**

- [ ] **Verser la CNSS**
- [ ] **Verser l'INAM**
- [ ] Soumettre les déclarations en ligne
- [ ] Archiver les preuves de paiement

### **Conservation**

- [ ] Classer les PDF dans le dossier du mois
- [ ] Archiver les reçus de paiement
- [ ] Mettre à jour le registre des déclarations

---

## 💡 CONSEILS PRATIQUES

### **1. Anticipation**
- Calculez les bulletins **avant le 5 du mois**
- Préparez les virements **avant le 8**
- Ne attendez pas la dernière minute !

### **2. Vérification**
- Contrôlez toujours les montants
- Comparez avec le mois précédent
- Vérifiez le nombre d'employés

### **3. Traçabilité**
- Conservez tous les documents
- Numérotez les déclarations
- Tenez un registre mensuel

### **4. Communication**
- Informez la direction des montants
- Prévenez la comptabilité
- Confirmez les paiements

---

## 🆘 EN CAS DE PROBLÈME

### **Montants incohérents**
1. Vérifier les bulletins calculés
2. Contrôler les éléments de salaire
3. Recalculer la période si nécessaire

### **Retard de paiement**
1. Contacter l'organisme immédiatement
2. Expliquer la situation
3. Payer dès que possible + pénalités

### **Erreur de déclaration**
1. Déclaration rectificative
2. Joindre une lettre explicative
3. Régulariser rapidement

---

## 📞 CONTACTS UTILES

### **CNSS Guinée**
- **Téléphone** : [À compléter]
- **Email** : [À compléter]
- **Site web** : [À compléter]

### **Direction Nationale des Impôts**
- **Téléphone** : [À compléter]
- **Email** : [À compléter]

### **INAM**
- **Téléphone** : [À compléter]
- **Email** : [À compléter]

---

## 🎯 RÉSUMÉ RAPIDE

**Pour effectuer une déclaration :**

1. ✅ Calculer les bulletins du mois
2. ✅ Aller sur `/paie/declarations/`
3. ✅ Filtrer par année et mois
4. ✅ Vérifier les montants
5. ✅ Imprimer en PDF
6. ✅ Effectuer les paiements
7. ✅ Soumettre aux organismes
8. ✅ Archiver les documents

**Délais à respecter :**
- 🔴 **10 du mois** : RTS
- 🟡 **15 du mois** : CNSS + INAM

---

**Développé avec ❤️ pour la Guinée**  
*22 Octobre 2025*
