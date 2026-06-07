# 📊 Schéma Module Comptabilité - GuinéeRH

## 🏗️ Architecture Générale

```
comptabilite/
├── models.py          # Modèles de données
├── views.py           # Vues et logique métier  
├── forms.py           # Formulaires de saisie
├── urls.py            # Routes et URLs
├── admin.py           # Administration Django
├── apps.py            # Configuration application
├── migrations/        # Migrations base de données
└── templates/
    └── comptabilite/
        ├── base_compta.html    # Template principal
        ├── dashboard.html       # Tableau de bord
        ├── plan_comptable/      # Gestion plan comptable
        ├── ecritures/           # Saisie écritures
        ├── factures/            # Gestion factures
        ├── reglements/          # Règlements
        └── etats/               # États financiers
```

---

## 📋 Modèles de Données

### 1. PlanComptable 📚
```python
class PlanComptable(models.Model):
    entreprise = ForeignKey(Entreprise)
    numero_compte = CharField(max_length=20)      # Ex: "101000"
    intitule = CharField(max_length=200)          # Ex: "Capital social"
    classe = CharField(choices=CLASSES)           # 1-9 SYSCOHADA
    compte_parent = ForeignKey('self', null=True) # Structure hiérarchique
    solde_debiteur = DecimalField(default=0.00)
    solde_crediteur = DecimalField(default=0.00)
```

**Classes SYSCOHADA :**
- Classe 1: Comptes de ressources durables
- Classe 2: Comptes d'actif immobilisé  
- Classe 3: Comptes de stocks
- Classe 4: Comptes de tiers
- Classe 5: Comptes de trésorerie
- Classe 6: Comptes de charges
- Classe 7: Comptes de produits
- Classe 8: Comptes des autres charges
- Classe 9: Comptes analytiques

### 2. Journal 📖
```python
class Journal(models.Model):
    entreprise = ForeignKey(Entreprise)
    code_journal = CharField(max_length=10)        # Ex: "AC", "VT"
    libelle = CharField(max_length=100)            # Ex: "Journal des Achats"
    type_journal = CharField(choices=TYPES_JOURNAL) # AC/VT/BA/OD
    periode_debut = DateField()
    periode_fin = DateField()
    est_actif = BooleanField(default=True)
```

**Types Journaux :**
- AC: Achats
- VT: Ventes  
- BA: Banque
- OD: Opérations Diverses

### 3. ExerciceComptable 📅
```python
class ExerciceComptable(models.Model):
    entreprise = ForeignKey(Entreprise)
    libelle = CharField(max_length=50)             # Ex: "Exercice 2024"
    date_debut = DateField()
    date_fin = DateField()
    est_courant = BooleanField(default=False)
    est_cloture = BooleanField(default=False)
```

### 4. ÉcritureComptable ✍️
```python
class EcritureComptable(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    entreprise = ForeignKey(Entreprise)
    journal = ForeignKey(Journal)
    exercice = ForeignKey(ExerciceComptable)
    date_ecriture = DateField()
    reference = CharField(max_length=50)           # Ex: "AC2024-001"
    libelle = CharField(max_length=200)
    montant_total_debit = DecimalField()
    montant_total_credit = DecimalField()
    statut = CharField(choices=STATUTS)            # brouillon/valide/approuve
    date_validation = DateTimeField(null=True)
    valide_par = ForeignKey(Utilisateur, null=True)
```

### 5. LigneEcriture 📝
```python
class LigneEcriture(models.Model):
    ecriture = ForeignKey(EcritureComptable, related_name='lignes')
    compte = ForeignKey(PlanComptable)
    libelle = CharField(max_length=200)
    montant_debit = DecimalField(default=0.00)
    montant_credit = DecimalField(default=0.00)
    ordre = IntegerField(default=0)                 # Ordre d'affichage
```

### 6. Tiers 👥
```python
class Tiers(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    entreprise = ForeignKey(Entreprise)
    code_tiers = CharField(max_length=20)           # Ex: "C001", "F001"
    nom = CharField(max_length=200)
    type_tiers = CharField(choices=TYPES_TIERS)    # client/fournisseur/autre
    adresse = TextField(blank=True)
    telephone = CharField(max_length=20, blank=True)
    email = EmailField(blank=True)
    compte_comptable = ForeignKey(PlanComptable, null=True)
    est_actif = BooleanField(default=True)
```

### 7. Facture 🧾
```python
class Facture(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    entreprise = ForeignKey(Entreprise)
    numero_facture = CharField(max_length=50)       # Ex: "F2024-001"
    tiers = ForeignKey(Tiers)
    date_facture = DateField()
    date_echeance = DateField()
    montant_ht = DecimalField()
    montant_tva = DecimalField()
    montant_ttc = DecimalField()
    statut = CharField(choices=STATUTS_FACTURE)    # brouillon/validee/payee/annulee
    date_validation = DateTimeField(null=True)
    validee_par = ForeignKey(Utilisateur, null=True)
```

### 8. LigneFacture 📋
```python
class LigneFacture(models.Model):
    facture = ForeignKey(Facture, related_name='lignes')
    article = CharField(max_length=200)
    quantite = DecimalField(max_digits=10, decimal_places=2)
    prix_unitaire_ht = DecimalField()
    montant_ht = DecimalField()
    taux_tva = DecimalField()                       # Ex: 18.0
    montant_tva = DecimalField()
    montant_ttc = DecimalField()
```

### 9. Reglement 💰
```python
class Reglement(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    entreprise = ForeignKey(Entreprise)
    facture = ForeignKey(Facture)
    date_reglement = DateField()
    montant = DecimalField()
    mode_reglement = CharField(choices=MODES_REGLEMENT)
    reference_paiement = CharField(max_length=100, blank=True)
    banque = CharField(max_length=200, blank=True)
    statut = CharField(choices=STATUTS_REGLEMENT)  # en_attente/valide/annule
```

### 10. TauxTVA 📊
```python
class TauxTVA(models.Model):
    entreprise = ForeignKey(Entreprise)
    taux = DecimalField(max_digits=5, decimal_places=2)  # Ex: 18.00
    libelle = CharField(max_length=50)                     # Ex: "TVA 18%"
    est_actif = BooleanField(default=True)
```

---

## 🔄 Relations Entre Modèles

```mermaid
erDiagram
    Entreprise ||--o{ PlanComptable : possède
    Entreprise ||--o{ Journal : possède
    Entreprise ||--o{ ExerciceComptable : possède
    Entreprise ||--o{ Tiers : possède
    Entreprise ||--o{ Facture : possède
    Entreprise ||--o{ Reglement : possède
    
    PlanComptable ||--o{ PlanComptable : hiérarchie
    PlanComptable ||--o{ LigneEcriture : utilisé dans
    PlanComptable ||--o{ Tiers : compte par défaut
    
    ExerciceComptable ||--o{ EcritureComptable : contient
    Journal ||--o{ EcritureComptable : utilise
    
    EcritureComptable ||--o{ LigneEcriture : contient
    
    Tiers ||--o{ Facture : émet/reçoit
    Facture ||--o{ LigneFacture : contient
    Facture ||--o{ Reglement : reçoit
```

---

## 🎯 Flux Métier Principaux

### 1. Saisie Écriture Comptable
```
1. Sélectionner exercice et journal
2. Créer écriture (brouillon)
3. Ajouter lignes débit/crédit
4. Vérifier équilibre (débit = crédit)
5. Valider écriture
6. Approuver (si nécessaire)
```

### 2. Cycle Facturation
```
1. Créer facture (brouillon)
2. Ajouter lignes de facturation
3. Calculs automatiques (TVA, totaux)
4. Valider facture
5. Générer écriture comptable automatiquement
6. Suivi règlements
```

### 3. Clôture Exercice
```
1. Vérifier toutes écritures validées
2. Générer balance de fin d'exercice
3. Créer écritures de virement/comptes
4. Clôturer exercice
5. Ouvrir nouvel exercice
```

---

## 📊 États Financiers

### 1. Grand Livre
- Liste toutes les écritures par compte
- Solde cumulé par compte
- Filtres par période et compte

### 2. Balance Comptable
- Tous les comptes avec soldes
- Total débits = Total crédits
- Base pour bilan et compte résultat

### 3. Bilan
- Actif (Classes 1-5)
- Passif (Classes 1-5)  
- Équilibre : Actif = Passif

### 4. Compte de Résultat
- Charges (Classe 6)
- Produits (Classe 7)
- Résultat : Produits - Charges

---

## 🔐 Sécurité et Permissions

### Décorateur `@compta_required`
```python
def compta_required(view_func):
    # Vérifie utilisateur authentifié
    # Vérifie entreprise associée
    # Vérifie accès module comptabilité (has_compta)
```

### Isolation Multi-tenant
- Toutes les requêtes filtrées par `entreprise`
- Impossible d'accéder données autres entreprises
- UUID pour éviter accès direct par ID séquentiel

---

## 🎨 Interface Utilisateur

### Structure Templates
```
base_compta.html
├── Navbar (entreprise + utilisateur)
├── Sidebar (navigation complète)
└── Main content
    ├── Dashboard
    ├── Saisie (écritures, factures, règlements)
    ├── Paramètres (plan comptable, journaux, exercices, tiers)
    └── États (grand livre, balance, bilan, compte résultat)
```

### Design System
- Bootstrap 5
- Thème bleu professionnel
- Icônes Bootstrap Icons
- Responsive mobile
- Animations et transitions fluides

---

## 📈 Fonctionnalités Avancées

### 1. Automatismes
- Génération écritures depuis factures
- Calculs automatiques TVA/totaux
- Équilibrage automatique écritures

### 2. Contrôles
- Équilibre débit/crédit obligatoire
- Périodes comptables contrôlées
- Validation en cascade

### 3. Reporting
- Export PDF/Excel
- Filtres multi-critères
- Graphiques et statistiques

---

## 🚀 Performance et Optimisation

### Indexation Base de Données
```python
class Meta:
    indexes = [
        models.Index(fields=['entreprise', 'numero_compte']),
        models.Index(fields=['entreprise', 'date_ecriture']),
        models.Index(fields=['entreprise', 'statut']),
    ]
```

### Optimisations
- Sélect_related pour FK
- Prefetch_related pour relations multiples
- Pagination sur listes importantes
- Cache pour données fréquemment accédées

---

## 📋 Checklist Déploiement

1. ✅ Migrations appliquées
2. ✅ Fichiers statiques collectés
3. ✅ URLs intégrées projet principal
4. ✅ Permissions configurées
5. ✅ Templates accessibles
6. ✅ Module activé pour entreprises test

---

*Module 100% fonctionnel et prêt pour production* 🎉
