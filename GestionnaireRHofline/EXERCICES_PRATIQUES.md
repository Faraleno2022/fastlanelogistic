# 📚 EXERCICES PRATIQUES - GESTION DES EMPLOYÉS

**Système** : GestionnaireRH Guinée  
**Date** : 22 Octobre 2025

---

## 🎯 OBJECTIF

Maîtriser l'ajout et la gestion complète des employés dans le système avec tous leurs paramètres.

---

## 📋 EXERCICE 1 : DONNÉES DE BASE

### **Contexte**
Enregistrer un nouvel employé : **Mamadou Camara**

### **Données à Saisir**

| Paramètre | Information |
|-----------|-------------|
| Nom | Camara |
| Prénoms | Mamadou |
| Date de naissance | 15/03/1990 |
| Lieu de naissance | Kindia |
| Nationalité | Guinéenne |
| CNI | GN-2015-789456 |
| Téléphone | +224 621 234 567 |
| Adresse | Quartier Almamya, Conakry |
| Situation matrimoniale | Marié |
| Nombre d'enfants | 2 |

### **Étapes dans le Système**

1. **Aller** sur `/employes/nouveau/`
2. **Remplir** l'onglet "Informations Personnelles"
3. **Calculer** l'âge automatiquement (35 ans)
4. **Enregistrer**

### **Questions**
- ✅ Quels documents annexer ?
- ✅ Comment protéger les données sensibles ?
- ✅ Impact de la situation matrimoniale ?

---

## 💼 EXERCICE 2 : DONNÉES CONTRACTUELLES

### **Contexte**
Mamadou Camara est embauché comme **Ingénieur Minier**

### **Données Contractuelles**

| Paramètre | Information |
|-----------|-------------|
| Poste | Ingénieur Minier |
| Département | Exploitation |
| Manager | Fatou Bah |
| Date embauche | 01/11/2025 |
| Type contrat | CDI |
| Période d'essai | 2 mois |
| Niveau études | Bac + 5 |
| Salaire base | 3,500,000 GNF |
| Classification | Cadre |

### **Étapes**

1. **Onglet** "Emploi" dans la fiche employé
2. **Remplir** tous les champs
3. **Calculer** fin période d'essai : 31/12/2025
4. **Générer** le contrat de travail

### **À Vérifier**
- ✅ Salaire ≥ SMIG
- ✅ Période d'essai conforme (2 mois pour cadre)
- ✅ Hiérarchie correcte

---

## 💰 EXERCICE 3 : CONFIGURATION PAIE

### **Contexte**
Configurer les éléments de salaire de Mamadou

### **Éléments à Ajouter**

| Rubrique | Montant | Type |
|----------|---------|------|
| Salaire base | 3,500,000 | Fixe |
| Prime ancienneté | 2% du salaire | Variable |
| Indemnité transport | 150,000 | Fixe |
| Indemnité logement | 500,000 | Fixe |
| CNSS (5%) | Auto | Retenue |
| IRG | Auto | Retenue |

### **Étapes**

1. **Aller** sur `/paie/elements-salaire/employe/<id>/`
2. **Cliquer** "Ajouter un élément"
3. **Pour chaque élément** :
   - Sélectionner la rubrique
   - Saisir le montant
   - ☑ Actif ☑ Récurrent
4. **Enregistrer**

### **Calculs Attendus**

```
Salaire brut = 3,500,000 + 70,000 + 150,000 + 500,000
             = 4,220,000 GNF

CNSS (5%) = 4,220,000 × 5% = 211,000 GNF
IRG = Selon barème progressif
Net à payer = Brut - CNSS - IRG
```

---

## 📅 EXERCICE 4 : CONGÉS ET ABSENCES

### **Contexte**
Configurer les droits aux congés de Mamadou

### **Droits Légaux**

| Type | Durée | Règle |
|------|-------|-------|
| Congé annuel | 2.5 jours/mois | 30 jours/an |
| Congé maladie | Variable | Justificatif requis |
| Congé paternité | 3 jours | Naissance |

### **Calcul pour 2025**

Embauche : 01/11/2025  
Fin année : 31/12/2025  
Mois travaillés : 2 mois

```
Congés acquis = 2 mois × 2.5 jours = 5 jours
```

### **Étapes**

1. Le système calcule automatiquement
2. **Vérifier** dans l'onglet "Congés"
3. **Créer** un solde de congés si nécessaire

---

## 👥 EXERCICE 5 : CAS COMPLEXE - 3 EMPLOYÉS

### **Profil 1 : Ingénieur (Mamadou)**
Voir exercices précédents

### **Profil 2 : Superviseur**

| Champ | Valeur |
|-------|--------|
| Nom | Diallo Aïssatou |
| Poste | Superviseur de Site |
| Embauche | 01/10/2025 |
| Salaire | 2,000,000 GNF |
| Contrat | CDI |
| Avantages | Transport 100,000 + Logement 300,000 |

### **Profil 3 : Agent Administratif**

| Champ | Valeur |
|-------|--------|
| Nom | Koïta Ismaël |
| Poste | Agent Administratif |
| Embauche | 15/11/2025 |
| Salaire | 800,000 GNF |
| Contrat | CDD 12 mois |

### **Hiérarchie**
```
Mamadou (Ingénieur)
    ↓
Aïssatou (Superviseur)
    ↓
Ismaël (Agent)
```

### **Tâches**

1. **Créer** les 3 employés
2. **Configurer** la hiérarchie
3. **Calculer** masse salariale totale
4. **Générer** déclaration CNSS

---

## ⚠️ EXERCICE 6 : GESTION DES ERREURS

### **Scénario A : Doublon**
Tentative d'ajout d'un "Mamadou Camara" existant

**Action** : Le système doit alerter et proposer de voir la fiche existante

### **Scénario B : Données Manquantes**
Adresse non fournie

**Action** : Champ obligatoire → Erreur de validation

### **Scénario C : Salaire < SMIG**
Salaire proposé : 400,000 GNF (< SMIG)

**Action** : Alerte système

### **Scénario D : Chevauchement CDD**
CDD qui se chevauche avec un autre contrat

**Action** : Vérification des dates

---

## ✅ CHECKLIST COMPLÈTE

### **Données Personnelles**
- [ ] Nom, prénoms
- [ ] Date et lieu de naissance
- [ ] Nationalité
- [ ] Pièce d'identité (CNI/Passeport)
- [ ] Contacts (téléphone, email)
- [ ] Adresse complète
- [ ] Situation matrimoniale
- [ ] Nombre d'enfants

### **Données Professionnelles**
- [ ] Matricule (auto-généré)
- [ ] Poste
- [ ] Département
- [ ] Manager direct
- [ ] Date d'embauche
- [ ] Type de contrat (CDI/CDD)
- [ ] Période d'essai
- [ ] Niveau d'études

### **Données Salariales**
- [ ] Salaire de base
- [ ] Primes et indemnités
- [ ] Éléments variables
- [ ] Cotisations CNSS
- [ ] IRG
- [ ] Mode de paiement

### **Congés**
- [ ] Solde initial
- [ ] Règles d'accumulation
- [ ] Types de congés autorisés

### **Documents**
- [ ] Contrat de travail signé
- [ ] Copie CNI
- [ ] Diplômes
- [ ] Certificat médical
- [ ] Photo d'identité

---

## 🎓 CORRECTION TYPE - EXERCICE 3

### **Bulletin de Paie - Mamadou Camara**
**Période** : Novembre 2025

```
GAINS
─────────────────────────────────
Salaire de base          3,500,000
Prime ancienneté (2%)       70,000
Indemnité transport        150,000
Indemnité logement         500,000
─────────────────────────────────
TOTAL BRUT              4,220,000

RETENUES
─────────────────────────────────
CNSS (5%)                 211,000
IRG                       380,000
─────────────────────────────────
TOTAL RETENUES            591,000

NET À PAYER             3,629,000 GNF
```

---

**Consultez le système pour pratiquer !** 🚀
