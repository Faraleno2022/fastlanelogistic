# 📋 Analyse des Besoins - Logiciel de Paie Guinée

## ✅ État Actuel vs Besoins Exprimés

### 1. 🔐 INTERFACE DE CONNEXION

#### ✅ Déjà Implémenté
- [x] Page de connexion fonctionnelle
- [x] Authentification utilisateur
- [x] Gestion des sessions
- [x] Profils utilisateurs avec niveaux d'accès

#### ❌ À Implémenter
- [ ] **Fenêtre de configuration des paramètres de paie**
  - [ ] Période : Début, Fin, Mois en cours, Année, Date du jour
  - [ ] Paramètres de paie : Régulation, Plafond des abattements
  - [ ] Rapport, Rapport TC
  - [ ] Suppression des salariés non présents en clôture annuelle
  - [ ] Gestion des historiques administratifs
  - [ ] Nombre maximum de rubriques composant
  - [ ] Type de bulletin par défaut
  - [ ] Type de paiement (Virement, Chèque, Espèce)
  - [ ] Acomptes (Régulier, Exceptionnel)
  - [ ] Fichier de paie
  - [ ] Modélisation comptable
  - [ ] Devise (GNF)
  - [ ] Rubriques (codes mémos des constantes, codes mémos des rubriques)
  - [ ] Constantes et Intitulés
  - [ ] Coordonnées de la société

---

### 2. 🏠 PAGE D'ACCUEIL

#### ✅ Déjà Implémenté
- [x] Dashboard accessible
- [x] Statistiques de base
- [x] Navigation vers tous les modules

#### ❌ À Implémenter
- [ ] Image de page d'accueil personnalisable
- [ ] Présentation de l'entreprise
- [ ] Accès public (sans authentification)

---

### 3. 📋 MENU LISTE

#### ✅ Déjà Implémenté
- [x] **Création d'un employé**
  - [x] État civil : Matricule, Civilité, Nom de jeune fille
  - [x] Immatriculation : Date de naissance, Commune, Nationalité, Département
  - [x] Contact, Informations professionnelles
- [x] Liste des employés
- [x] Services
- [x] Postes
- [x] Établissements

#### ❌ À Implémenter
- [ ] **Gestion de formation** (modèle existe, interface à créer)
- [ ] **Gestion de carrière** (modèle existe, interface à créer)
- [ ] **Gestion de temps** (modèle à créer)
- [ ] **Liste des constantes**
- [ ] **Liste des rubriques**
- [ ] **Liste des variables**
- [ ] **Liste de nature des événements**
- [ ] **Liste des organisations**
- [ ] **Convention collective**
- [ ] **Caisse de cotisation**
- [ ] **Contrats sociaux**
- [ ] **Table des prêts**
- [ ] **Modélisation comptable**
- [ ] **Gestion des tables**

---

### 4. ⚙️ GESTION

#### ✅ Déjà Implémenté
- [x] Structure de base pour les modules

#### ❌ À Implémenter
- [ ] **Bulletin de salaire**
  - [ ] Création/Modification
  - [ ] Calcul automatique
  - [ ] Génération PDF
  - [ ] Envoi email
- [ ] **Liste des absences**
- [ ] **Arrêt de travail**
- [ ] **Acompte**
- [ ] **Prêt**
- [ ] **Enregistrement des heures**
- [ ] **Saisie en grille**
- [ ] **Calcul des bulletins**
- [ ] **Paiement**
- [ ] **Clôture**

---

### 5. 📊 ÉTATS (RAPPORTS)

#### ✅ Déjà Implémenté
- [x] Dashboard avec graphiques
- [x] Rapports de base

#### ❌ À Implémenter
- [ ] **Livre de paie**
- [ ] **Fiche individuelle**
- [ ] **Mouvement de personnel**
- [ ] **État des absences**
- [ ] **Calendrier**
- [ ] **État des cotisations** (CNSS, INAM, IRG)
- [ ] **État des cumuls**
- [ ] **Déclaration des salaires**

---

## 📊 Récapitulatif de Conformité

### Modules Principaux

| Module | Sous-module | Statut | Priorité |
|--------|-------------|--------|----------|
| **1. Connexion** | Interface de base | ✅ | - |
| | Configuration paramètres paie | ❌ | 🔴 HAUTE |
| **2. Accueil** | Dashboard | ✅ | - |
| | Page publique | ❌ | 🟡 MOYENNE |
| **3. Menu Liste** | Employés | ✅ | - |
| | Constantes | ❌ | 🔴 HAUTE |
| | Rubriques | ❌ | 🔴 HAUTE |
| | Variables | ❌ | 🔴 HAUTE |
| | Organisations | ✅ | - |
| | Prêts | ❌ | 🟢 BASSE |
| **4. Gestion** | Bulletin de salaire | ❌ | 🔴 HAUTE |
| | Absences | ❌ | 🔴 HAUTE |
| | Heures | ❌ | 🔴 HAUTE |
| | Acomptes | ❌ | 🟡 MOYENNE |
| | Prêts | ❌ | 🟡 MOYENNE |
| | Clôture | ❌ | 🔴 HAUTE |
| **5. États** | Livre de paie | ❌ | 🔴 HAUTE |
| | Cotisations | ❌ | 🔴 HAUTE |
| | Déclarations | ❌ | 🔴 HAUTE |

### Taux de Conformité Global

```
Fonctionnalités demandées : 45
Fonctionnalités implémentées : 8
Taux de conformité : 18%
```

---

## 🎯 Plan d'Implémentation Prioritaire

### Phase A : Paramétrage de Base (2 semaines)
**Objectif** : Mettre en place tous les paramètres nécessaires au calcul de paie

1. **Modèles Django à créer**
   - `ParametrePaie` (périodes, plafonds, types)
   - `Constante` (SMIG, plafonds, taux)
   - `RubriquePaie` (gains, retenues, cotisations)
   - `Variable` (variables de calcul)
   - `TrancheIRG` (barème IRG)

2. **Interfaces à créer**
   - Fenêtre de configuration paramètres
   - Gestion des constantes
   - Gestion des rubriques
   - Gestion des variables
   - Configuration société

### Phase B : Temps de Travail (2 semaines)
**Objectif** : Collecter les données nécessaires au calcul

1. **Modèles**
   - `Pointage`
   - `Absence`
   - `ArretTravail`
   - `Conge`
   - `HeureSupplementaire`

2. **Interfaces**
   - Saisie des heures
   - Saisie en grille
   - Gestion des absences
   - Gestion des arrêts

### Phase C : Calcul de Paie (3 semaines)
**Objectif** : Moteur de calcul conforme législation guinéenne

1. **Modèles**
   - `PeriodePaie`
   - `BulletinPaie`
   - `LigneBulletin`
   - `CumulPaie`

2. **Moteur de calcul**
   - Calcul salaire brut
   - Calcul CNSS (5% employé, 18% employeur)
   - Calcul INAM (2.5%)
   - Calcul IRG (barème progressif)
   - Calcul net à payer

3. **Interfaces**
   - Création période
   - Calcul bulletins
   - Validation bulletins
   - Génération PDF

### Phase D : Acomptes et Prêts (1 semaine)
**Objectif** : Gestion des avances et prêts

1. **Modèles**
   - `Acompte`
   - `Pret`
   - `EcheancePret`

2. **Interfaces**
   - Demande acompte
   - Gestion prêts
   - Échéancier

### Phase E : États et Rapports (2 semaines)
**Objectif** : Tous les rapports légaux

1. **Rapports**
   - Livre de paie
   - Fiche individuelle
   - État des cotisations (CNSS, INAM, IRG)
   - Déclaration des salaires
   - État des cumuls
   - Mouvement de personnel

2. **Exports**
   - PDF
   - Excel
   - XML (pour déclarations)

### Phase F : Clôture et Comptabilité (1 semaine)
**Objectif** : Clôture mensuelle et écritures comptables

1. **Fonctionnalités**
   - Clôture période
   - Génération écritures comptables
   - Export vers logiciel comptable
   - Archivage

---

## 📝 Spécifications Techniques Détaillées

### 1. Configuration Paramètres de Paie

```python
class ParametrePaie(models.Model):
    # Période
    date_debut_periode = models.DateField()
    date_fin_periode = models.DateField()
    mois_en_cours = models.IntegerField()
    annee_en_cours = models.IntegerField()
    date_du_jour = models.DateField(auto_now=True)
    
    # Paramètres
    regulation_active = models.BooleanField(default=True)
    plafond_abattement = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Types
    type_bulletin_defaut = models.CharField(max_length=20)
    type_paiement_defaut = models.CharField(max_length=20)
    
    # Limites
    nombre_max_rubriques = models.IntegerField(default=100)
    
    # Devise
    devise = models.CharField(max_length=3, default='GNF')
```

### 2. Constantes de Paie

```python
class Constante(models.Model):
    code = models.CharField(max_length=20, unique=True)
    libelle = models.CharField(max_length=200)
    valeur = models.DecimalField(max_digits=15, decimal_places=4)
    type_valeur = models.CharField(max_length=20)  # Montant, Pourcentage
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    actif = models.BooleanField(default=True)
    
    # Exemples :
    # SMIG = 440000 GNF
    # PLAFOND_CNSS = 3000000 GNF
    # TAUX_CNSS_EMPLOYE = 5.00
    # TAUX_CNSS_EMPLOYEUR = 18.00
    # TAUX_INAM = 2.50
```

### 3. Rubriques de Paie

```python
class RubriquePaie(models.Model):
    code = models.CharField(max_length=20, unique=True)
    libelle = models.CharField(max_length=200)
    type_rubrique = models.CharField(max_length=20)  # GAIN, RETENUE, COTISATION
    nature = models.CharField(max_length=50)  # SALAIRE_BASE, PRIME, CNSS, IRG
    
    # Calcul
    formule = models.TextField(blank=True)
    base_calcul = models.CharField(max_length=50)
    taux = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    montant_fixe = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    plafond = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    
    # Soumissions
    soumis_cnss = models.BooleanField(default=False)
    soumis_irg = models.BooleanField(default=False)
    soumis_inam = models.BooleanField(default=False)
    
    # Affichage
    ordre_calcul = models.IntegerField(default=100)
    ordre_affichage = models.IntegerField(default=100)
    affichage_bulletin = models.BooleanField(default=True)
    
    # Comptabilité
    compte_comptable = models.CharField(max_length=20, blank=True)
```

### 4. Variables de Paie

```python
class Variable(models.Model):
    code = models.CharField(max_length=20, unique=True)
    libelle = models.CharField(max_length=100)
    type_variable = models.CharField(max_length=20)  # NUMERIQUE, TEXTE, BOOLEEN
    portee = models.CharField(max_length=20)  # GLOBAL, EMPLOYE, PERIODE
    valeur_defaut = models.CharField(max_length=100, blank=True)
    
    # Exemples :
    # JOURS_MOIS = 22
    # HEURES_MOIS = 173.33
    # JOURS_CONGES = 26
```

### 5. Bulletin de Paie

```python
class BulletinPaie(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.PROTECT)
    periode = models.ForeignKey(PeriodePaie, on_delete=models.PROTECT)
    numero_bulletin = models.CharField(max_length=50, unique=True)
    
    # Période
    mois_paie = models.IntegerField()
    annee_paie = models.IntegerField()
    
    # Temps
    jours_payes = models.DecimalField(max_digits=5, decimal_places=2)
    heures_normales = models.DecimalField(max_digits=8, decimal_places=2)
    heures_supplementaires = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Montants
    salaire_brut = models.DecimalField(max_digits=15, decimal_places=2)
    base_cnss = models.DecimalField(max_digits=15, decimal_places=2)
    cnss_employe = models.DecimalField(max_digits=15, decimal_places=2)
    inam_employe = models.DecimalField(max_digits=15, decimal_places=2)
    base_irg = models.DecimalField(max_digits=15, decimal_places=2)
    irg = models.DecimalField(max_digits=15, decimal_places=2)
    net_a_payer = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Charges patronales
    cnss_employeur = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Statut
    statut = models.CharField(max_length=20, default='BROUILLON')
    date_calcul = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True)
    date_paiement = models.DateField(null=True)
    
    # Paiement
    mode_paiement = models.CharField(max_length=20)  # VIREMENT, CHEQUE, ESPECE
    reference_paiement = models.CharField(max_length=100, blank=True)
```

---

## 🔧 Fonctionnalités Spécifiques Guinée

### Calcul CNSS
```python
def calculer_cnss(salaire_brut):
    PLAFOND_CNSS = 3000000  # GNF
    TAUX_EMPLOYE = 0.05  # 5%
    TAUX_EMPLOYEUR = 0.18  # 18%
    
    base_cnss = min(salaire_brut, PLAFOND_CNSS)
    cnss_employe = base_cnss * TAUX_EMPLOYE
    cnss_employeur = base_cnss * TAUX_EMPLOYEUR
    
    return base_cnss, cnss_employe, cnss_employeur
```

### Calcul INAM
```python
def calculer_inam(salaire_brut):
    PLAFOND_INAM = 3000000  # GNF
    TAUX_INAM = 0.025  # 2.5%
    
    base_inam = min(salaire_brut, PLAFOND_INAM)
    inam = base_inam * TAUX_INAM
    
    return inam
```

### Calcul IRG (Barème Progressif)
```python
def calculer_irg(salaire_brut, cnss_employe, inam):
    # Base IRG = Brut - CNSS - INAM - Abattement
    ABATTEMENT = 0.20  # 20%
    PLAFOND_ABATTEMENT = 300000  # GNF
    
    abattement = min(salaire_brut * ABATTEMENT, PLAFOND_ABATTEMENT)
    base_irg = salaire_brut - cnss_employe - inam - abattement
    
    # Barème progressif
    tranches = [
        (0, 1000000, 0.00),
        (1000001, 3000000, 0.05),
        (3000001, 6000000, 0.10),
        (6000001, 12000000, 0.15),
        (12000001, 25000000, 0.20),
        (25000001, float('inf'), 0.25)
    ]
    
    irg = 0
    for min_tranche, max_tranche, taux in tranches:
        if base_irg > min_tranche:
            montant_tranche = min(base_irg, max_tranche) - min_tranche
            irg += montant_tranche * taux
    
    return base_irg, irg
```

---

## 📅 Planning d'Implémentation

| Phase | Durée | Priorité | Dépendances |
|-------|-------|----------|-------------|
| A. Paramétrage | 2 sem | 🔴 HAUTE | Aucune |
| B. Temps de travail | 2 sem | 🔴 HAUTE | Phase A |
| C. Calcul paie | 3 sem | 🔴 HAUTE | Phases A, B |
| D. Acomptes/Prêts | 1 sem | 🟡 MOYENNE | Phase C |
| E. États/Rapports | 2 sem | 🔴 HAUTE | Phase C |
| F. Clôture | 1 sem | 🔴 HAUTE | Phase E |

**Durée totale : 11 semaines (2,5 mois)**

---

## ✅ Checklist de Validation

### Avant de commencer le développement
- [ ] Valider les spécifications avec l'utilisateur
- [ ] Confirmer les taux et plafonds 2025
- [ ] Obtenir des exemples de bulletins réels
- [ ] Valider le barème IRG officiel
- [ ] Confirmer les formats de déclarations

### Pendant le développement
- [ ] Tests unitaires pour chaque calcul
- [ ] Validation avec bulletins réels
- [ ] Vérification conformité légale
- [ ] Tests de performance

### Avant la mise en production
- [ ] Formation des utilisateurs
- [ ] Documentation complète
- [ ] Migration des données
- [ ] Tests en conditions réelles

---

**Document créé le** : 21 Octobre 2025  
**Prochaine mise à jour** : Après validation des spécifications

🇬🇳 **Conforme à la législation guinéenne**
