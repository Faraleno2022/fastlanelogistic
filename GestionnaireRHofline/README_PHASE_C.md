# 🚀 Guide d'Utilisation - Phase C : Calcul Automatique de la Paie

## 📋 Introduction

La Phase C implémente le **moteur de calcul automatique de la paie** pour le système de gestion RH. Ce guide vous explique comment utiliser toutes les fonctionnalités développées.

---

## ⚡ Démarrage Rapide

### 1. Initialiser les Éléments de Salaire

```bash
python manage.py init_elements_salaire
```

Cette commande crée automatiquement les éléments de salaire pour les 3 employés de test.

### 2. Calculer la Paie

```bash
# Pour tous les employés actifs
python manage.py calculer_paie --periode 2025-11

# Pour un employé spécifique
python manage.py calculer_paie --periode 2025-11 --employe MG-2021-847
```

### 3. Consulter les Résultats

Accédez à l'interface admin :
```
http://127.0.0.1:8000/admin/
```

Naviguez vers : **Paie → Bulletins de paie**

---

## 📚 Commandes Disponibles

### `calculer_paie`

Calcule automatiquement les bulletins de paie pour une période donnée.

**Syntaxe :**
```bash
python manage.py calculer_paie --periode AAAA-MM [OPTIONS]
```

**Options :**
- `--periode AAAA-MM` : Période de calcul (obligatoire)
- `--employe MATRICULE` : Calculer pour un employé spécifique (optionnel)
- `--recalculer` : Recalculer les bulletins existants (optionnel)

**Exemples :**

```bash
# Calculer pour tous les employés (Novembre 2025)
python manage.py calculer_paie --periode 2025-11

# Calculer pour Diallo Abdoulaye uniquement
python manage.py calculer_paie --periode 2025-11 --employe MG-2021-847

# Recalculer tous les bulletins de la période
python manage.py calculer_paie --periode 2025-11 --recalculer

# Recalculer pour un employé spécifique
python manage.py calculer_paie --periode 2025-11 --employe MG-2021-847 --recalculer
```

**Sortie :**
```
🧮 Calcul de la paie pour Novembre 2025

📊 1 employé(s) à traiter

  ✅ MG-2021-847 - Diallo Abdoulaye
      Brut: 10,837,717 GNF | Net: 8,659,958 GNF

======================================================================

📈 RÉSUMÉ DU CALCUL

  • Bulletins créés: 1

📊 STATISTIQUES PÉRIODE Novembre 2025
  • Total brut: 10,837,717 GNF
  • Total net: 8,659,958 GNF
  • Total IRG: 631,684 GNF
  • Nombre de bulletins: 1

======================================================================
✅ Calcul terminé!
```

### `init_elements_salaire`

Initialise les éléments de salaire pour les employés de test.

**Syntaxe :**
```bash
python manage.py init_elements_salaire
```

**Ce qui est créé :**
- Éléments pour COMATEX SARL (Diallo Mamadou)
- Éléments pour MINÉRAUX GUINÉE SA (Diallo Abdoulaye)
- Éléments pour SGT SA (Camara Moussa)

---

## 🎛️ Interface Admin

### Accès

```
URL : http://127.0.0.1:8000/admin/
User : LENO
Pass : 1994
```

### Menus Disponibles

#### 1. **Paie → Éléments de salaire**

Gérez les éléments de salaire fixes par employé.

**Fonctionnalités :**
- Créer/modifier/supprimer des éléments
- Filtrer par employé, rubrique, statut
- Rechercher par nom d'employé ou code rubrique
- Définir montants fixes ou taux avec base de calcul
- Gérer la validité (date début/fin)
- Activer/désactiver la récurrence

**Exemple :**
```
Employé : Diallo Abdoulaye
Rubrique : SAL_BASE_CAT_A
Montant : 4,500,000 GNF
Date début : 15/03/2020
Actif : Oui
Récurrent : Oui
```

#### 2. **Paie → Bulletins de paie**

Consultez et gérez les bulletins calculés.

**Fonctionnalités :**
- Vue détaillée avec lignes inline
- Montants calculés en lecture seule
- Filtres par période, statut
- Recherche par numéro ou employé
- Changement de statut (brouillon → calculé → validé → payé)

**Informations affichées :**
- Numéro de bulletin
- Employé et période
- Salaire brut
- CNSS salarié
- IRG
- Net à payer
- CNSS employeur
- Date de calcul
- Statut

**Lignes de détail :**
Chaque ligne affiche :
- Rubrique
- Base de calcul
- Taux appliqué
- Nombre/quantité
- Montant calculé

#### 3. **Paie → Cumuls de paie**

Consultez les cumuls annuels par employé.

**Informations :**
- Cumul brut annuel
- Cumul net annuel
- Cumul IRG annuel
- Cumul CNSS (salarié et employeur)
- Nombre de bulletins

**Utilité :**
- Déclarations fiscales annuelles
- Certificats de salaire
- Statistiques RH

#### 4. **Paie → Historique de paie**

Traçabilité complète des opérations.

**Informations :**
- Type d'action (création, modification, validation, etc.)
- Employé et période concernés
- Utilisateur ayant effectué l'action
- Date et heure
- Valeurs avant/après (JSON)
- Adresse IP

---

## 🔧 Workflow Complet

### Étape 1 : Préparation

1. **Créer la période de paie**
   ```
   Admin → Paie → Périodes de paie → Ajouter
   
   Année : 2025
   Mois : 11
   Date début : 01/11/2025
   Date fin : 30/11/2025
   Statut : Ouverte
   Jours travaillés : 22
   Heures mois : 173.33
   ```

2. **Vérifier les constantes**
   ```
   Admin → Paie → Constantes
   
   Vérifier :
   - TAUX_CNSS_SALARIE : 5.50%
   - TAUX_CNSS_EMPLOYEUR : 18.00% (ou 8.10% secteur minier)
   - SMIG : 440,000 GNF
   - Déductions familiales
   ```

3. **Vérifier les éléments de salaire**
   ```
   Admin → Paie → Éléments de salaire
   
   Pour chaque employé, vérifier :
   - Salaire de base
   - Primes récurrentes
   - Allocations
   - Retenues fixes
   ```

### Étape 2 : Calcul

```bash
# Calculer pour tous les employés
python manage.py calculer_paie --periode 2025-11
```

**Ou via l'interface (à venir dans Phase E)**

### Étape 3 : Vérification

1. **Consulter les bulletins**
   ```
   Admin → Paie → Bulletins de paie
   ```

2. **Vérifier les montants**
   - Salaire brut
   - Cotisations sociales
   - IRG
   - Retenues
   - Net à payer

3. **Consulter le détail**
   - Cliquer sur un bulletin
   - Voir toutes les lignes de calcul
   - Vérifier base, taux, montant

### Étape 4 : Validation

1. **Changer le statut**
   ```
   Admin → Bulletin → Statut : "Validé"
   ```

2. **Clôturer la période**
   ```
   Admin → Période → Statut : "Clôturée"
   ```

### Étape 5 : Consultation

1. **Cumuls annuels**
   ```
   Admin → Paie → Cumuls de paie
   ```

2. **Historique**
   ```
   Admin → Paie → Historique de paie
   ```

---

## 🧮 Détails du Calcul

### Processus de Calcul

Le moteur suit ce processus :

```
1. GAINS
   ├─ Récupérer éléments de salaire actifs
   ├─ Calculer chaque élément (montant fixe ou taux × base)
   ├─ Cumuler total gains
   └─ Calculer assiettes (CNSS, IRG)

2. SALAIRE BRUT
   └─ Brut = Total gains

3. COTISATIONS SOCIALES
   ├─ CNSS salarié (5.5% de l'assiette CNSS)
   ├─ CNSS employeur (8.1% ou 18%)
   ├─ Mutuelle (si applicable)
   ├─ Retraite complémentaire (si applicable)
   └─ Fonds solidarité (si applicable)

4. IRG/IRSA
   ├─ Base imposable = Imposable - CNSS - déductions
   ├─ Déductions familiales
   │   ├─ Conjoint : 50,000 à 100,000 GNF
   │   ├─ Enfants locaux : 75,000 à 100,000 GNF/enfant
   │   └─ Enfants étranger : 150,000 GNF/enfant
   ├─ Abattements professionnels (5% plafonné 1M)
   ├─ IRG progressif (barème 5 tranches)
   └─ Crédits d'impôt

5. AUTRES RETENUES
   ├─ Avances sur salaire
   ├─ Prêts
   ├─ Retenues disciplinaires
   └─ Autres

6. SALAIRE NET
   └─ Net = Brut - Total retenues
```

### Assiettes Gérées

Le moteur gère **3 assiettes distinctes** :

1. **Assiette CNSS**
   - Tous les éléments avec `soumis_cnss = True`
   - Exclut : Indemnité de fonction (si accord), remboursements frais

2. **Assiette IRG**
   - Tous les éléments avec `soumis_irg = True`
   - Exclut : Indemnité de représentation (partielle), allocations éducation, etc.

3. **Assiette Brute**
   - Tous les gains (type_rubrique = 'gain')

### Barème IRG 2025

| Tranche | Montant | Taux |
|---------|---------|------|
| 1 | 0 - 2,000,000 | 0% |
| 2 | 2,000,001 - 5,000,000 | 10% |
| 3 | 5,000,001 - 10,000,000 | 15% |
| 4 | 10,000,001 - 20,000,000 | 20% |
| 5 | > 20,000,000 | 25% |

**Calcul progressif :**
```
Exemple : Base imposable = 12,000,000 GNF

Tranche 1 : 2,000,000 × 0% = 0
Tranche 2 : 3,000,000 × 10% = 300,000
Tranche 3 : 5,000,000 × 15% = 750,000
Tranche 4 : 2,000,000 × 20% = 400,000
─────────────────────────────────────
IRG brut = 1,450,000 GNF
```

---

## 📊 Exemples Pratiques

### Exemple 1 : Employé Simple (COMATEX)

**Données :**
- Salaire de base : 2,500,000 GNF
- Prime transport : 300,000 GNF
- Prime risque : 200,000 GNF
- Heures sup : 50,000 GNF
- Indemnité repas : 150,000 GNF
- Avance : 200,000 GNF
- Syndicat : 50,000 GNF

**Calcul :**
```
Brut : 3,200,000 GNF
CNSS (5.5%) : -176,000 GNF
IRG : -228,240 GNF
Avance : -200,000 GNF
Syndicat : -50,000 GNF
─────────────────────
Net : 2,545,760 GNF
```

### Exemple 2 : Employé Complexe (MINÉRAUX GUINÉE)

**Données :**
- Salaire base : 4,500,000 GNF
- Indemnité fonction : 800,000 GNF
- Prime ancienneté : 225,000 GNF
- Prime responsabilité : 600,000 GNF
- Prime production : 750,000 GNF
- Bonus sécurité : 300,000 GNF
- Commission : 625,000 GNF
- Indemnités diverses : 2,550,000 GNF
- Heures sup : 487,717 GNF
- Retenues : 950,000 GNF

**Calcul :**
```
Brut : 10,837,717 GNF
CNSS (5.5%) : -596,074 GNF
IRG : -631,684 GNF
Retenues : -950,000 GNF
─────────────────────
Net : 8,659,958 GNF
```

---

## ❓ FAQ

### Comment ajouter un nouvel employé ?

1. Créer l'employé dans `Admin → Employés`
2. Créer ses éléments de salaire dans `Admin → Paie → Éléments de salaire`
3. Lancer le calcul avec `python manage.py calculer_paie --periode AAAA-MM`

### Comment modifier un élément de salaire ?

1. `Admin → Paie → Éléments de salaire`
2. Trouver l'élément à modifier
3. Modifier le montant ou le taux
4. Recalculer avec `--recalculer`

### Comment gérer une prime exceptionnelle ?

1. Créer une rubrique de type "gain" si elle n'existe pas
2. Créer un élément de salaire avec `recurrent = False`
3. Définir les dates de validité
4. Calculer la paie

### Que faire en cas d'erreur de calcul ?

1. Vérifier les éléments de salaire de l'employé
2. Vérifier les constantes (CNSS, IRG, etc.)
3. Consulter l'historique pour voir les valeurs
4. Recalculer avec `--recalculer`

### Comment voir le détail d'un calcul ?

1. `Admin → Paie → Bulletins de paie`
2. Cliquer sur le bulletin
3. Voir toutes les lignes avec base, taux, montant

---

## 🔐 Sécurité et Traçabilité

### Traçabilité

Chaque opération est enregistrée dans l'historique :
- Qui a fait l'action ?
- Quand ?
- Quelles valeurs avant/après ?
- Depuis quelle adresse IP ?

### Audit

Pour auditer une période :
```
Admin → Paie → Historique de paie
Filtrer par période
```

### Sauvegardes

Les bulletins calculés sont stockés en base de données et ne peuvent pas être modifiés directement. Pour corriger :
1. Modifier les éléments de salaire
2. Recalculer avec `--recalculer`

---

## 📞 Support

Pour toute question :
- Consulter `docs/PHASE_C_CALCUL_PAIE.md` pour la documentation complète
- Voir `STATUS_ACTUEL.md` pour l'état du projet
- Consulter les exercices dans `docs/EXERCICE_*.md`

---

🇬🇳 **Fier d'être Guinéen - Made in Guinea**  
**Version** : 1.0  
**Date** : 22 Octobre 2025
