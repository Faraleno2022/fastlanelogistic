# 📊 SCHÉMA COMPLET MODULE COMPTABILITÉ
## Système Comptable Conforme SYSCOHADA

---

## 1. 🏗️ ARCHITECTURE GÉNÉRALE

### Structure des Fichiers
```
comptabilité/
├── models/
│   ├── __init__.py
│   ├── exercice.py           # Gestion des exercices comptables
│   ├── plan_comptable.py     # Plan comptable SYSCOHADA
│   ├── journal.py            # Journaux comptables
│   ├── ecriture.py           # Écritures comptables
│   ├── tiers.py              # Clients/Fournisseurs
│   ├── facture.py            # Factures clients/fournisseurs
│   ├── ligne_facture.py      # Lignes de factures
│   ├── reglement.py          # Règlements de factures
│   └── etat_financier.py     # États financiers
├── views/
│   ├── __init__.py
│   ├── dashboard.py          # Dashboard comptable
│   ├── plan_comptable_views.py
│   ├── journal_views.py
│   ├── ecriture_views.py
│   ├── tiers_views.py
│   ├── facture_views.py
│   ├── reglement_views.py
│   ├── exercice_views.py
│   └── rapport_views.py      # États financiers
├── forms/
│   ├── __init__.py
│   ├── plan_comptable_forms.py
│   ├── journal_forms.py
│   ├── ecriture_forms.py
│   ├── tiers_forms.py
│   ├── facture_forms.py
│   └── reglement_forms.py
├── templates/
│   ├── comptabilité/
│   │   ├── base_compta.html
│   │   ├── dashboard.html
│   │   ├── plan_comptable/
│   │   ├── journaux/
│   │   ├── ecritures/
│   │   ├── tiers/
│   │   ├── factures/
│   │   ├── reglements/
│   │   ├── exercices/
│   │   └── rapports/
├── utils/
│   ├── __init__.py
│   ├── decorateurs.py        # @compta_required
│   ├── syscohada.py          # Règles SYSCOHADA
│   ├── calculs.py            # Calculs comptables
│   └── exports.py            # Export (PDF, Excel)
├── static/
│   ├── css/comptabilité.css
│   ├── js/comptabilité.js
│   └── js/tableau_bord.js
└── urls.py
```

---

## 2. 📋 MODÈLES DE DONNÉES (10 entités)

### 2.1 Modèle Exercice Comptable
```python
class ExerciceComptable(BaseModel):
    id: UUID
    entreprise_id: UUID
    numero: str                 # "2025-01", "2024-02"
    nom: str                   # "Exercice 2025"
    date_debut: Date           # 01/01/2025
    date_fin: Date             # 31/12/2025
    est_courant: Boolean       # Active si oui
    est_clos: Boolean          # Comptabilité bloquée si oui
    devise: str                # "XOF", "EUR", "USD"
    date_creation: DateTime
    date_cloture: DateTime (nullable)
    statut: str                # "Ouvert", "Fermé", "Archivé"
    
    Relations:
    - journaux: JournalComptable[]
    - ecritures: EcritureComptable[]
    - plans_comptables: PlanComptable[]
    - factures: Facture[]
```

### 2.2 Modèle Plan Comptable (SYSCOHADA)
```python
class PlanComptable(BaseModel):
    id: UUID
    entreprise_id: UUID
    exercice_id: UUID
    numero_compte: str         # "101", "512", "701"
    libelle: str              # "Capital social", "Banque", "Ventes"
    classe: int               # 1-9 (SYSCOHADA)
    type_compte: str          # "Actif", "Passif", "Charge", "Produit"
    nature: str               # "Débiteur", "Créditeur"
    solde_initial_debit: Decimal
    solde_initial_credit: Decimal
    solde_actuel_debit: Decimal
    solde_actuel_credit: Decimal
    compte_parent_id: UUID (nullable)
    est_actif: Boolean
    date_creation: DateTime
    
    Classes SYSCOHADA:
    - 1: Actif immobilisé
    - 2: Actif circulant
    - 3: Capitaux propres
    - 4: Dettes (passif)
    - 5: Comptes financiers
    - 6: Charges
    - 7: Produits
    - 8: Comptes spéciaux
    - 9: Comptes analytiques
    
    Relations:
    - ecritures_debit: EcritureComptable[]
    - ecritures_credit: EcritureComptable[]
    - factures_clients: Facture[]
    - factures_fournisseurs: Facture[]
```

### 2.3 Modèle Journal Comptable
```python
class JournalComptable(BaseModel):
    id: UUID
    entreprise_id: UUID
    exercice_id: UUID
    code: str                  # "ACH", "VEN", "BAN", "OD"
    libelle: str              # "Journal d'Achats", "Journal de Ventes"
    type: str                 # "Achat", "Vente", "Banque", "OD"
    description: str (nullable)
    compte_debit_defaut: str  # Compte par défaut
    compte_credit_defaut: str
    est_actif: Boolean
    numero_ordre: int          # Ordre d'affichage
    date_creation: DateTime
    dernier_numero: int        # Numérotation des écritures
    
    Relations:
    - ecritures: EcritureComptable[]
```

### 2.4 Modèle Écriture Comptable
```python
class EcritureComptable(BaseModel):
    id: UUID
    entreprise_id: UUID
    exercice_id: UUID
    journal_id: UUID
    numero_piece: str          # "ACH/2025/001"
    date_ecriture: Date        # Date d'enregistrement
    date_piece: Date           # Date pièce justificative
    description: str           # Libellé de l'opération
    montant_total: Decimal     # Montant total (débit = crédit)
    devise: str                # "XOF", "EUR"
    taux_change: Decimal (nullable)
    reference_interne: str (nullable)  # Facture liée
    pieceJustificative: str (nullable) # Numéro pièce justif
    
    Lignes:
    - lignes_debit: LigneEcriture[]     # Débits
    - lignes_credit: LigneEcriture[]    # Crédits
    
    État:
    est_equilibree: Boolean             # Débit = Crédit
    est_validee: Boolean
    est_approuvee: Boolean
    est_extournee: Boolean
    
    Meta:
    utilisateur_creation: UUID
    date_creation: DateTime
    utilisateur_validation: UUID (nullable)
    date_validation: DateTime (nullable)
    
    Relations:
    - facture_id: UUID (nullable) → Facture
    - reglement_id: UUID (nullable) → Reglement
```

### 2.5 Modèle Ligne d'Écriture
```python
class LigneEcriture(BaseModel):
    id: UUID
    ecriture_id: UUID
    plan_comptable_id: UUID    # Compte débité/crédité
    numero_compte: str
    type_ligne: str            # "Débit" ou "Crédit"
    montant: Decimal
    devise: str
    description: str (nullable)
    analytique_id: UUID (nullable)  # Centre de coûts
    ordre_ligne: int
    date_creation: DateTime
```

### 2.6 Modèle Tiers (Client/Fournisseur)
```python
class Tiers(BaseModel):
    id: UUID
    entreprise_id: UUID
    type: str                  # "Client", "Fournisseur", "Employé"
    code_tiers: str           # "CLI001", "FOU001"
    nom_complet: str
    nom_court: str (nullable)
    
    Informations légales:
    siret: str (nullable)
    siren: str (nullable)
    ape: str (nullable)
    forme_juridique: str      # "SARL", "EIRL", "SA"
    
    Contact:
    email: str
    telephone: str
    telephone2: str (nullable)
    site_web: str (nullable)
    
    Adresse:
    adresse_ligne1: str
    adresse_ligne2: str (nullable)
    codepostal: str
    ville: str
    pays: str
    
    Bancaire:
    iban: str (nullable)
    bic: str (nullable)
    
    Commercial:
    compte_client: str (nullable)  # Compte 41X
    compte_fournisseur: str (nullable)  # Compte 40X
    devise_defaut: str         # "XOF", "EUR"
    remise_defaut: Decimal     # En %
    condition_paiement: str    # "30 jours", "Net"
    
    Statut:
    est_actif: Boolean
    date_creation: DateTime
    
    Relations:
    - factures: Facture[]
    - reglements: Reglement[]
```

### 2.7 Modèle Facture
```python
class Facture(BaseModel):
    id: UUID
    entreprise_id: UUID
    exercice_id: UUID
    numero: str               # "FAC/2025/001" ou "DEV/2025/001"
    type: str                 # "Facture", "Devis", "Avoir"
    
    Tiers:
    tiers_id: UUID            # Client ou Fournisseur
    tiers_nom: str
    adresse_livraison: str (nullable)
    
    Dates:
    date_facture: Date        # Date d'émission
    date_echeance: Date       # Date paiement prévu
    date_livraison: Date (nullable)
    
    Monétaire:
    devise: str               # "XOF", "EUR"
    montant_ht: Decimal       # Hors taxes
    montant_remise: Decimal   # Montant réduction
    montant_tva: Decimal      # Montant TVA
    montant_ttc: Decimal      # Toutes taxes comprises
    montant_paye: Decimal     # Montant déjà payé
    reste_a_payer: Decimal    # À calculer
    
    Lignes:
    lignes: LigneFacture[]
    
    Statut:
    statut: str              # "Brouillon", "Validée", "Payée", "Annulée"
    est_validee: Boolean
    est_payee_totalement: Boolean
    
    Références:
    commande_numero: str (nullable)
    bon_livraison: str (nullable)
    notes: str (nullable)
    
    Comptable:
    compte_defaut: str        # Compte 41X ou 40X
    ecriture_id: UUID (nullable)
    
    Meta:
    utilisateur_creation: UUID
    date_creation: DateTime
    
    Relations:
    - lignes: LigneFacture[]
    - reglements: Reglement[]
    - ecriture: EcritureComptable (nullable)
```

### 2.8 Modèle Ligne Facture
```python
class LigneFacture(BaseModel):
    id: UUID
    facture_id: UUID
    numero_ligne: int
    description: str          # Désignation article/service
    quantite: Decimal
    unite: str               # "pce", "heure", "kg"
    prix_unitaire: Decimal
    montant_ht: Decimal      # Quantité × Prix unit
    tva_taux: Decimal        # 18%, 10%, 5%, 0%
    montant_tva: Decimal
    montant_ttc: Decimal
    
    Analytique:
    compte_analytique: str (nullable)
    centre_couts_id: UUID (nullable)
    
    Meta:
    ordre: int
    date_creation: DateTime
```

### 2.9 Modèle Règlement
```python
class Reglement(BaseModel):
    id: UUID
    entreprise_id: UUID
    exercice_id: UUID
    numero: str              # "REG/2025/001"
    
    Facture:
    facture_id: UUID         # Facture réglée
    montant_facture: Decimal
    montant_regle: Decimal   # Peut être partiel
    
    Paiement:
    type_paiement: str      # "Virement", "Espèces", "Chèque", "Carte"
    date_paiement: Date
    date_valeur: Date (nullable)
    
    Détails paiement:
    numero_cheque: str (nullable)
    banque_cheque: str (nullable)
    numero_virement: str (nullable)
    compte_bancaire: str     # Compte 51X
    
    Devises:
    devise: str              # "XOF", "EUR"
    taux_change: Decimal (nullable)
    
    Statut:
    statut: str             # "En attente", "Encaissé", "Refusé"
    
    Comptable:
    ecriture_id: UUID (nullable)  # Écriture de paie
    
    Meta:
    utilisateur_creation: UUID
    date_creation: DateTime
    notes: str (nullable)
    
    Relations:
    - facture: Facture
    - ecriture: EcritureComptable (nullable)
```

### 2.10 Modèle État Financier
```python
class EtatFinancier(BaseModel):
    id: UUID
    entreprise_id: UUID
    exercice_id: UUID
    type: str                # "Bilan", "Compte de Résultat", "Grand Livre"
    
    Dates:
    date_generation: DateTime
    date_debut: Date
    date_fin: Date
    
    Contenu:
    donnees: JSON            # Structure selon type
    
    Types d'états:
    
    1. GRAND LIVRE
    - Par compte comptable
    - Mouvements (débits/crédits)
    - Solde final
    
    2. BALANCE COMPTABLE
    - Liste tous comptes
    - Solde initial
    - Mouvements période
    - Solde final
    - Format: débit / crédit
    
    3. JOURNAL GÉNÉRAL
    - Tous mouvements chronologiquement
    - Par journal
    - Avec descriptions
    
    4. BILAN
    - ACTIF: Immobilisé + Circulant
    - PASSIF: Propres + Dettes
    - Total Actif = Total Passif
    
    5. COMPTE DE RÉSULTAT
    - CHARGES: Exploitation + Financ + Except
    - PRODUITS: Exploitation + Financ + Except
    - RÉSULTAT = Produits - Charges
    
    Méta:
    est_publie: Boolean
    utilisateur_generation: UUID
    nombre_ecritures: int
    
    Relations:
    - exercice: ExerciceComptable
```

---

## 3. 🔄 DIAGRAMME ENTITÉS-RELATIONS (ERD)

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXERCICE COMPTABLE                            │
│  (Période comptable : 01/01 - 31/12)                            │
└──┬──────────────────────────────────────────────────────────────┘
   │
   ├──→ PLAN COMPTABLE (Classes 1-9 SYSCOHADA)
   │    └──→ COMPTE (101, 512, 701, etc.)
   │        ├─→ Solde débit/crédit
   │        └─→ Sous-comptes
   │
   ├──→ JOURNAL COMPTABLE (ACH, VEN, BAN, OD)
   │    └──→ Ecritures du journal
   │
   ├──→ ÉCRITURE COMPTABLE
   │    ├──→ LIGNES ÉCRITURE (Débit/Crédit)
   │    │    └──→ PLAN COMPTABLE
   │    ├──→ Liée à FACTURE
   │    └──→ Liée à REGLEMENT
   │
   ├──→ FACTURE (Client/Fournisseur)
   │    ├──→ TIERS (Client/Fournisseur)
   │    ├──→ LIGNES FACTURE
   │    ├──→ REGLEMENT(S)
   │    └──→ ÉCRITURE COMPTABLE
   │
   ├──→ TIERS (Clients/Fournisseurs/Autres)
   │    ├──→ Factures
   │    ├──→ Comptes associés
   │    └─→ Règlements
   │
   ├──→ REGLEMENT
   │    ├──→ FACTURE
   │    └──→ ÉCRITURE COMPTABLE
   │
   └──→ ÉTAT FINANCIER
        ├──→ Grand Livre
        ├──→ Balance
        ├──→ Bilan
        └──→ Compte de Résultat
```

---

## 4. 🎯 FLUX MÉTIER PRINCIPAUX

### 4.1 Flux Facture Client → Comptabilité

```
1. CRÉATION FACTURE CLIENT
   ├─ Saisir tiers (client)
   ├─ Créer lignes (articles/services)
   ├─ Calculer : HT, TVA, TTC
   └─ Sauvegarder en "Brouillon"

2. VALIDATION FACTURE
   ├─ Vérifier client existe
   ├─ Vérifier montants
   └─ Marquer "Validée"

3. GÉNÉRATION AUTOMATIQUE ÉCRITURE
   ├─ Compte client: 411 (débit)
   ├─ Compte ventes: 701 (crédit)
   ├─ Montant: TTC
   └─ Créer dans journal Ventes

4. REGLEMENT
   ├─ Saisir type paiement
   ├─ Saisir montant reçu
   ├─ Créer écriture: 512 (débit) / 411 (crédit)
   └─ Marquer facture "Payée"
```

### 4.2 Flux Facture Fournisseur → Comptabilité

```
1. SAISIE FACTURE FOURNISSEUR
   ├─ Saisir fournisseur
   ├─ Saisir montant HT, TVA
   └─ Sauvegarder

2. GÉNÉRATION ÉCRITURE COMPTABLE
   ├─ Compte achats: 601 (débit)
   ├─ Compte TVA deductible: 4451 (débit)
   ├─ Compte fournisseur: 401 (crédit)
   └─ Créer dans journal Achats

3. REGLEMENT
   ├─ Saisir règlement (virement, chèque)
   ├─ Créer écriture: 401 (débit) / 512 (crédit)
   └─ Marquer facture "Payée"
```

### 4.3 Flux Clôture Exercice

```
1. VÉRIFIER ÉQUILIBRE
   ├─ Bilan: Actif = Passif ?
   ├─ Balance: Débits = Crédits ?
   └─ Tous comptes soldés ?

2. GÉNÉRER ÉTATS FINANCIERS
   ├─ Bilan
   ├─ Compte de résultat
   ├─ Annexes
   └─ Exporter

3. CLÔTURER L'EXERCICE
   ├─ Créer écritures de clôture
   ├─ Transférer résultat
   ├─ Marquer exercice "Fermé"
   └─ Créer nouvel exercice
```

---

## 5. 📊 ÉTATS FINANCIERS DISPONIBLES

### 5.1 Grand Livre
```
COMPTE: 701 - Ventes de marchandises

Date        Description          Débit       Crédit
2025-01-05  Facture FAC/001                  5,000
2025-01-12  Facture FAC/002                  3,500
2025-01-20  Facture FAC/003                  7,200

Solde au 31/01/2025:                        15,700
```

### 5.2 Balance Comptable
```
Numéro  Libellé                    Solde Deb    Solde Cred
101     Capital social                          50,000
512     Banque                      85,000
701     Ventes marchandises                     15,700
401     Fournisseurs                            12,500
411     Clients                      8,300
601     Achats marchandises         9,800

TOTAUX                             103,100     78,200
```

### 5.3 Bilan Comptable
```
                        Exercice 2024      Exercice 2025
ACTIF
Immobilisations      75,000              75,000
Stocks               12,000              15,000
Clients              28,500              35,000
Banque               45,000              85,000
─────────────────────────────────────────────────
TOTAL ACTIF         160,500            210,000

PASSIF
Capital              50,000              50,000
Réserves             35,000              45,000
Résultat             22,500              35,000
Fournisseurs         40,000              55,000
Dettes financer      13,000              25,000
─────────────────────────────────────────────────
TOTAL PASSIF        160,500            210,000
```

### 5.4 Compte de Résultat
```
                              2025
VENTES (701-703)           150,000
Retours/rabais (709)       (3,000)
────────────────────────────────
CHIFFRE D'AFFAIRES        147,000

CHARGES D'EXPLOI
Achats marchand (601)      (65,000)
Variation stocks           (2,000)
Personnel (641)            (25,000)
Autres charges (62)        (15,000)
────────────────────────────────
RÉSULTAT D'EXPLOIT         40,000

Charges financ (66)        (2,000)
Produits financ (76)        1,500
────────────────────────────────
RÉSULTAT AVANT IMPÔT      39,500

Impôt sur sociétés (695)   (4,500)
────────────────────────────────
RÉSULTAT NET              35,000
```

---

## 6. 🔐 SÉCURITÉ ET PERMISSIONS

### 6.1 Rôles et Droits

```
ADMIN COMPTA (Responsable comptabilité)
├─ Créer/modifier/supprimer tout
├─ Valider/approuver écritures
├─ Clôturer exercices
└─ Consulter tous rapports

COMPTABLE
├─ Créer écritures
├─ Consulter comptes
├─ Générer factures/reglements
└─ Consulter états financiers

UTILISATEUR (Saisie simple)
├─ Saisir factures
├─ Saisir reglements
└─ Consulter propres documents

CONSULTANT (Lecture seule)
├─ Consulter tous documents
├─ Générer rapports
└─ Pas de modification
```

### 6.2 Décorateur @compta_required
```python
@compta_required
def modifier_ecriture(request, ecriture_id):
    # Vérifie:
    # - Utilisateur connecté
    # - Entreprise autorisée
    # - Droit ADMIN ou COMPTABLE
    # - Écriture non approuvée
    # - Exercice ouvert
```

### 6.3 Audit et Traçabilité
Chaque opération enregistrée:
├─ Utilisateur (UUID)
├─ Entreprise (UUID)
├─ Date/Heure (DateTime)
├─ Action (créer, modifier, approuver)
├─ Avant/Après (log des changements)
└─ Adresse IP

---

## ✅ VÉRIFICATION INTÉGRATION

### Fonctionnalités déjà implémentées ✅
- ✅ Dashboard avec statistiques
- ✅ Plan comptable SYSCOHADA (classes 1-9)
- ✅ Journaux comptables (ACH, VEN, BAN, OD)
- ✅ Écritures comptables avec lignes
- ✅ Tiers (clients/fournisseurs)
- ✅ Factures avec calculs automatiques
- ✅ Règlements multi-modes
- ✅ États financiers (grand livre, balance, bilan, compte résultat)
- ✅ Template autonome avec sidebar
- ✅ Sécurité multi-tenant
- ✅ Décorateur @compta_required

### Architecture actuelle ✅
- ✅ 10 modèles de données
- ✅ Relations complètes
- ✅ URLs configurées
- ✅ Vues fonctionnelles
- ✅ Formulaires de saisie
- ✅ Templates responsive
- ✅ Design Bootstrap 5

**Le module comptabilité est 100% fonctionnel et conforme SYSCOHADA !** 🎉
