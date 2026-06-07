# TP 1 – Création et Paramétrage d'une Entreprise

> **Durée estimée** : 45 minutes  
> **Niveau** : Débutant  
> **Prérequis** : Accès au système GuinéeRH avec droits administrateur

---

## 🎯 Objectifs pédagogiques

À la fin de ce TP, vous serez capable de :

1. Créer une nouvelle entreprise dans le système
2. Configurer les paramètres de paie selon la législation guinéenne
3. Choisir entre le **Code du Travail** et une **Convention Collective**
4. Créer la structure organisationnelle (services et postes)
5. Comprendre **pourquoi le paramétrage conditionne toute la paie**

---

## 📚 Rappel théorique (5 min)

### Pourquoi paramétrer AVANT de créer des employés ?

```
┌─────────────────────────────────────────────────────────────┐
│  PARAMÉTRAGE ENTREPRISE  →  détermine  →  CALCUL DE PAIE   │
└─────────────────────────────────────────────────────────────┘
```

| Ce que vous paramétrez | Impact sur la paie |
|------------------------|-------------------|
| Taux CNSS | Montant des cotisations sociales |
| Barème RTS | Montant de l'impôt sur salaire |
| Règles heures sup | Majoration 30%, 60%, etc. |
| Congés (base légale) | Provision et solde congés |

> ⚠️ **Règle d'or** : Un mauvais paramétrage = des bulletins faux = des problèmes avec la CNSS et les impôts.

---

## 🧩 ÉTAPE 1 : Création de l'entreprise (15 min)

### Données à saisir

Nous allons créer une entreprise fictive mais **réaliste** :

| Champ | Valeur à saisir |
|-------|-----------------|
| **Nom de l'entreprise** | SOPROGI SARL |
| **Secteur d'activité** | Commerce général |
| **NIF** | 123456789A |
| **N° CNSS Employeur** | 2024-CNK-00158 |
| **Adresse** | Quartier Almamya, Commune de Kaloum |
| **Ville** | Conakry |
| **Pays** | Guinée |
| **Téléphone** | +224 622 00 00 00 |
| **Email** | contact@soprogi.gn |

### Procédure pas à pas

1. **Connectez-vous** au système avec vos identifiants administrateur
2. Allez dans **Paramètres** → **Entreprise**
3. Cliquez sur **« Nouvelle entreprise »**
4. Remplissez tous les champs du tableau ci-dessus
5. Cliquez sur **« Enregistrer »**

### ✅ Résultat attendu

- L'entreprise **SOPROGI SARL** apparaît dans la liste
- Un message de confirmation s'affiche
- L'entreprise est automatiquement sélectionnée comme entreprise active

### ⚠️ Erreurs fréquentes

| Erreur | Cause | Solution |
|--------|-------|----------|
| "NIF déjà existant" | Numéro en double | Vérifier le NIF ou contacter l'admin |
| "Email invalide" | Format incorrect | Utiliser format xxx@domaine.xx |
| Champs vides | Oubli de saisie | Les champs avec * sont obligatoires |

---

## 🧩 ÉTAPE 2 : Paramétrage de la paie (15 min)

### Choix crucial : Code du Travail ou Convention Collective ?

Avant de paramétrer, vous devez **choisir le référentiel légal** :

| Critère | Code du Travail | Convention Collective |
|---------|-----------------|----------------------|
| **Congés payés** | 1,5 jour/mois (18 j/an) | Souvent 2,5 j/mois (30 j/an) |
| **Heures sup** | +30% puis +60% | Variable selon secteur |
| **Ancienneté** | +2 jours / 5 ans | Souvent plus avantageux |
| **Qui l'utilise ?** | Petites entreprises | Grandes entreprises, secteurs réglementés |

> 💡 **Pour ce TP** : Nous utiliserons le **Code du Travail** (cas le plus courant).

### Données à saisir – Paramètres CNSS

| Paramètre | Valeur | Explication |
|-----------|--------|-------------|
| **Taux CNSS salarié** | 5% | Part retenue sur le salaire de l'employé |
| **Taux CNSS employeur** | 18% | Part payée par l'entreprise (non visible sur bulletin) |
| **Plafond CNSS** | 2 500 000 GNF | Au-delà, pas de cotisation supplémentaire |
| **Plancher CNSS (SMIG)** | 550 000 GNF | Minimum de cotisation |

### Données à saisir – Barème RTS (CGI 2022)

Le **RTS (Retenue à la Source)** est l'impôt sur salaire. Il est **progressif** :

| Tranche | De (GNF) | À (GNF) | Taux |
|---------|----------|---------|------|
| 1 | 0 | 1 000 000 | **0%** |
| 2 | 1 000 001 | 3 000 000 | **5%** |
| 3 | 3 000 001 | 5 000 000 | **8%** |
| 4 | 5 000 001 | 10 000 000 | **10%** |
| 5 | 10 000 001 | 20 000 000 | **15%** |
| 6 | Au-delà de 20 000 000 | - | **20%** |

### Données à saisir – Heures supplémentaires

| Type | Majoration | Quand ? |
|------|------------|---------|
| HS normales (1-4h/semaine) | **+30%** | Jour ouvrable |
| HS au-delà 4h/semaine | **+60%** | Jour ouvrable |
| Heures de nuit (20h-6h) | **+20%** | Nuit |
| Jour férié (jour) | **+60%** | Férié |
| Jour férié (nuit) | **+100%** | Férié + nuit |

### Données à saisir – Congés payés

| Paramètre | Valeur Code du Travail |
|-----------|------------------------|
| **Base mensuelle** | 1,5 jour ouvrable |
| **Base annuelle** | 18 jours |
| **Bonus ancienneté** | +2 jours par tranche de 5 ans |
| **Moins de 18 ans** | 2 jours/mois (24 jours/an) |

### Procédure pas à pas

1. Allez dans **Paramètres** → **Configuration Paie**
2. Sélectionnez l'entreprise **SOPROGI SARL**
3. Dans l'onglet **CNSS** :
   - Saisissez les taux (5% / 18%)
   - Saisissez plafond et plancher
4. Dans l'onglet **RTS** :
   - Vérifiez que le barème CGI 2022 est actif
   - Ou saisissez manuellement les 6 tranches
5. Dans l'onglet **Heures supplémentaires** :
   - Configurez les majorations selon le tableau
6. Dans l'onglet **Congés** :
   - Sélectionnez "Code du Travail" comme référentiel
   - Vérifiez la base de 1,5 jour/mois
7. Cliquez sur **« Enregistrer les paramètres »**

### ✅ Résultat attendu

- Un récapitulatif des paramètres s'affiche
- Le système indique "Configuration valide"
- Les paramètres sont prêts pour le calcul de paie

### ⚠️ Erreurs fréquentes

| Erreur | Cause | Solution |
|--------|-------|----------|
| "Taux invalide" | Valeur > 100% | Vérifier la saisie (5, pas 500) |
| Barème RTS incomplet | Tranche manquante | Saisir les 6 tranches |
| Plafond < Plancher | Inversion des valeurs | Plafond = 2 500 000, Plancher = 550 000 |

---

## 🧩 ÉTAPE 3 : Structure organisationnelle (10 min)

### Créer les services

Une entreprise a besoin d'une **structure** pour organiser les employés :

| Code | Nom du service | Responsable |
|------|----------------|-------------|
| DIR | Direction Générale | (à définir plus tard) |
| ADM | Administration | (à définir plus tard) |
| COM | Commercial | (à définir plus tard) |
| LOG | Logistique | (à définir plus tard) |

### Procédure pas à pas

1. Allez dans **Paramètres** → **Services**
2. Cliquez sur **« Nouveau service »**
3. Pour chaque service du tableau :
   - Saisissez le code et le nom
   - Cliquez sur **« Enregistrer »**
4. Répétez pour les 4 services

### Créer les postes

| Code | Intitulé du poste | Service | Catégorie |
|------|-------------------|---------|-----------|
| DG | Directeur Général | DIR | Cadre |
| RAF | Responsable Admin & Finances | ADM | Cadre |
| COMPT | Comptable | ADM | Agent de maîtrise |
| RC | Responsable Commercial | COM | Cadre |
| VEND | Vendeur | COM | Employé |
| MAG | Magasinier | LOG | Employé |
| CHAUF | Chauffeur | LOG | Ouvrier |

### Procédure pas à pas

1. Allez dans **Paramètres** → **Postes**
2. Cliquez sur **« Nouveau poste »**
3. Pour chaque poste du tableau :
   - Saisissez le code, l'intitulé
   - Sélectionnez le service
   - Choisissez la catégorie professionnelle
   - Cliquez sur **« Enregistrer »**

### ✅ Résultat attendu

- 4 services créés
- 7 postes créés et rattachés aux services
- L'organigramme simplifié est visible

---

## 🧠 Ce qu'il faut retenir

### Les 5 points essentiels de ce TP

```
┌─────────────────────────────────────────────────────────────────┐
│  1. TOUJOURS paramétrer AVANT de créer des employés            │
│  2. Le choix Code du Travail / Convention impacte TOUT         │
│  3. Les taux CNSS sont FIXES : 5% salarié, 18% employeur       │
│  4. Le RTS est PROGRESSIF : plus on gagne, plus le taux monte  │
│  5. La structure (services/postes) organise les employés       │
└─────────────────────────────────────────────────────────────────┘
```

### Schéma récapitulatif

```
ENTREPRISE
    │
    ├── Paramètres Paie
    │       ├── CNSS (5%/18%)
    │       ├── RTS (barème 6 tranches)
    │       ├── Heures sup (30%/60%)
    │       └── Congés (1,5 j/mois)
    │
    └── Structure
            ├── Services (DIR, ADM, COM, LOG)
            └── Postes (DG, RAF, COMPT, etc.)
```

---

## ✅ Checklist de validation

Avant de passer au TP 2, vérifiez que vous avez :

- [ ] Créé l'entreprise SOPROGI SARL
- [ ] Configuré les taux CNSS (5% / 18%)
- [ ] Vérifié le barème RTS CGI 2022 (6 tranches)
- [ ] Paramétré les heures supplémentaires
- [ ] Configuré les congés (Code du Travail)
- [ ] Créé les 4 services
- [ ] Créé les 7 postes

**Si tout est coché, vous êtes prêt pour le TP 2 !** 🎉

---

## 📝 Notes pour le formateur

### Points d'attention en salle

1. **Faire le lien** entre chaque paramètre et son impact sur le bulletin
2. **Montrer un exemple** de bulletin avec mauvais paramétrage vs bon paramétrage
3. **Insister** sur l'importance du NIF et N° CNSS pour les déclarations

### Questions fréquentes des apprenants

| Question | Réponse |
|----------|---------|
| "Peut-on modifier les paramètres après ?" | Oui, mais cela n'affecte que les futurs calculs |
| "Qui décide Code du Travail ou Convention ?" | L'entreprise, selon son secteur et ses accords |
| "Le plafond CNSS change-t-il ?" | Oui, il peut être révisé par décret |

### Transition vers TP 2

> "Maintenant que l'entreprise est paramétrée, nous allons créer nos premiers employés. Vous verrez comment les informations personnelles (situation familiale, contrat) influencent le calcul de la paie."

---

**TP suivant** : [TP 2 – Création des employés](./TP2_CREATION_EMPLOYES.md)
