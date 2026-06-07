# 💰 GUIDE : AJOUTER OU RETIRER DES GAINS ET RETENUES

**Date** : 22 Octobre 2025  
**Module** : Paie

---

## 🎯 COMPRENDRE LE SYSTÈME

### **Structure de la Paie**

```
EMPLOYÉ
   ↓
ÉLÉMENTS DE SALAIRE (gains et retenues fixes)
   ↓
BULLETIN DE PAIE (calcul mensuel)
   ↓
LIGNES DE BULLETIN (détail)
```

### **3 Niveaux de Gestion**

1. **Rubriques de Paie** - Catalogue des gains/retenues possibles
2. **Éléments de Salaire** - Gains/retenues assignés à un employé
3. **Lignes de Bulletin** - Montants calculés pour un mois donné

---

## 📋 MÉTHODE 1 : VIA L'INTERFACE ADMIN (Recommandé)

### **A. AJOUTER UN GAIN (Prime, Indemnité)**

#### **Étape 1 : Accéder à l'admin**
```
http://127.0.0.1:8000/admin/paie/elementsalaire/
```

#### **Étape 2 : Cliquer sur "Ajouter élément de salaire"**

#### **Étape 3 : Remplir le formulaire**

**Exemple : Ajouter une prime de transport**

```
┌─────────────────────────────────────────┐
│ EMPLOYÉ ET RUBRIQUE                     │
├─────────────────────────────────────────┤
│ Employé: Diallo Mamadou (COMATEX-001) │
│ Rubrique: PRIME_TRANSPORT              │
├─────────────────────────────────────────┤
│ MONTANT/TAUX                            │
├─────────────────────────────────────────┤
│ Montant: 300000                         │
│ Taux: (vide)                            │
│ Base de calcul: (vide)                  │
├─────────────────────────────────────────┤
│ VALIDITÉ                                │
├─────────────────────────────────────────┤
│ Date début: 01/11/2025                  │
│ Date fin: (vide = permanent)            │
│ ☑ Actif                                 │
│ ☑ Récurrent (chaque mois)               │
└─────────────────────────────────────────┘
```

#### **Étape 4 : Enregistrer**
✅ La prime sera automatiquement ajoutée au prochain bulletin !

---

### **B. AJOUTER UNE RETENUE (Avance, Prêt)**

**Exemple : Ajouter une avance sur salaire**

```
┌─────────────────────────────────────────┐
│ EMPLOYÉ ET RUBRIQUE                     │
├─────────────────────────────────────────┤
│ Employé: Diallo Mamadou                │
│ Rubrique: AVANCE_SAL                    │
├─────────────────────────────────────────┤
│ MONTANT/TAUX                            │
├─────────────────────────────────────────┤
│ Montant: 200000                         │
├─────────────────────────────────────────┤
│ VALIDITÉ                                │
├─────────────────────────────────────────┤
│ Date début: 01/11/2025                  │
│ Date fin: 30/11/2025 (1 mois)          │
│ ☑ Actif                                 │
│ ☐ Récurrent (une seule fois)           │
└─────────────────────────────────────────┘
```

---

### **C. RETIRER UN GAIN OU UNE RETENUE**

#### **Option 1 : Désactiver (Recommandé)**
1. Aller sur `/admin/paie/elementsalaire/`
2. Cliquer sur l'élément à retirer
3. Décocher "Actif"
4. Enregistrer

✅ L'élément ne sera plus calculé mais reste dans l'historique

#### **Option 2 : Définir une date de fin**
1. Aller sur `/admin/paie/elementsalaire/`
2. Cliquer sur l'élément
3. Renseigner "Date fin" = 31/10/2025
4. Enregistrer

✅ L'élément s'arrêtera automatiquement après cette date

#### **Option 3 : Supprimer définitivement**
1. Aller sur `/admin/paie/elementsalaire/`
2. Cocher l'élément à supprimer
3. Action : "Supprimer les éléments de salaire sélectionnés"
4. Confirmer

⚠️ **Attention** : Suppression définitive !

---

## 📋 MÉTHODE 2 : VIA LE SHELL DJANGO

### **A. AJOUTER UN GAIN**

```bash
python manage.py shell
```

```python
from employes.models import Employe
from paie.models import RubriquePaie, ElementSalaire
from datetime import date
from decimal import Decimal

# 1. Récupérer l'employé
employe = Employe.objects.get(matricule='COMATEX-001')

# 2. Récupérer la rubrique
rubrique = RubriquePaie.objects.get(code_rubrique='PRIME_TRANSPORT')

# 3. Créer l'élément de salaire
element = ElementSalaire.objects.create(
    employe=employe,
    rubrique=rubrique,
    montant=Decimal('300000'),  # 300,000 GNF
    date_debut=date(2025, 11, 1),
    actif=True,
    recurrent=True  # Chaque mois
)

print(f"✅ Prime de transport ajoutée : {element}")
```

---

### **B. AJOUTER UNE RETENUE TEMPORAIRE**

```python
# Avance sur salaire (1 mois seulement)
employe = Employe.objects.get(matricule='COMATEX-001')
rubrique = RubriquePaie.objects.get(code_rubrique='AVANCE_SAL')

element = ElementSalaire.objects.create(
    employe=employe,
    rubrique=rubrique,
    montant=Decimal('200000'),
    date_debut=date(2025, 11, 1),
    date_fin=date(2025, 11, 30),  # Fin après 1 mois
    actif=True,
    recurrent=False  # Une seule fois
)

print(f"✅ Avance ajoutée : {element}")
```

---

### **C. AJOUTER UN GAIN AVEC TAUX (Pourcentage)**

```python
# Prime de 10% sur le salaire de base
employe = Employe.objects.get(matricule='COMATEX-001')
rubrique = RubriquePaie.objects.get(code_rubrique='PRIME_ANCIENNETE')

element = ElementSalaire.objects.create(
    employe=employe,
    rubrique=rubrique,
    taux=Decimal('10.00'),  # 10%
    base_calcul='SALAIRE_BASE',  # Calculé sur le salaire de base
    date_debut=date(2025, 11, 1),
    actif=True,
    recurrent=True
)

print(f"✅ Prime d'ancienneté 10% ajoutée : {element}")
```

---

### **D. RETIRER UN ÉLÉMENT**

#### **Désactiver**
```python
element = ElementSalaire.objects.get(id=5)
element.actif = False
element.save()
print("✅ Élément désactivé")
```

#### **Définir une date de fin**
```python
element = ElementSalaire.objects.get(id=5)
element.date_fin = date(2025, 10, 31)
element.save()
print("✅ Date de fin définie")
```

#### **Supprimer**
```python
element = ElementSalaire.objects.get(id=5)
element.delete()
print("✅ Élément supprimé")
```

---

### **E. LISTER LES ÉLÉMENTS D'UN EMPLOYÉ**

```python
employe = Employe.objects.get(matricule='COMATEX-001')

# Tous les éléments actifs
elements = ElementSalaire.objects.filter(
    employe=employe,
    actif=True
)

print(f"\n📋 Éléments de salaire pour {employe.nom_complet}:\n")
for elem in elements:
    type_rub = elem.rubrique.get_type_rubrique_display()
    if elem.montant:
        print(f"  • {elem.rubrique.libelle_rubrique} ({type_rub}): {elem.montant:,.0f} GNF")
    elif elem.taux:
        print(f"  • {elem.rubrique.libelle_rubrique} ({type_rub}): {elem.taux}%")
```

---

## 📋 MÉTHODE 3 : SCRIPT PYTHON

### **Créer un fichier : `gerer_elements_salaire.py`**

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionnaire_rh.settings')
django.setup()

from employes.models import Employe
from paie.models import RubriquePaie, ElementSalaire
from datetime import date
from decimal import Decimal


def ajouter_gain(matricule, code_rubrique, montant, date_debut=None):
    """Ajouter un gain à un employé"""
    try:
        employe = Employe.objects.get(matricule=matricule)
        rubrique = RubriquePaie.objects.get(code_rubrique=code_rubrique)
        
        if date_debut is None:
            date_debut = date.today()
        
        element = ElementSalaire.objects.create(
            employe=employe,
            rubrique=rubrique,
            montant=Decimal(str(montant)),
            date_debut=date_debut,
            actif=True,
            recurrent=True
        )
        
        print(f"✅ {rubrique.libelle_rubrique} ajouté : {montant:,.0f} GNF")
        return element
        
    except Employe.DoesNotExist:
        print(f"❌ Employé {matricule} non trouvé")
    except RubriquePaie.DoesNotExist:
        print(f"❌ Rubrique {code_rubrique} non trouvée")


def ajouter_retenue(matricule, code_rubrique, montant, temporaire=False):
    """Ajouter une retenue à un employé"""
    try:
        employe = Employe.objects.get(matricule=matricule)
        rubrique = RubriquePaie.objects.get(code_rubrique=code_rubrique)
        
        date_debut = date.today()
        date_fin = None
        recurrent = True
        
        if temporaire:
            # Retenue pour 1 mois seulement
            from calendar import monthrange
            dernier_jour = monthrange(date_debut.year, date_debut.month)[1]
            date_fin = date(date_debut.year, date_debut.month, dernier_jour)
            recurrent = False
        
        element = ElementSalaire.objects.create(
            employe=employe,
            rubrique=rubrique,
            montant=Decimal(str(montant)),
            date_debut=date_debut,
            date_fin=date_fin,
            actif=True,
            recurrent=recurrent
        )
        
        print(f"✅ {rubrique.libelle_rubrique} ajouté : {montant:,.0f} GNF")
        if temporaire:
            print(f"   (Temporaire jusqu'au {date_fin})")
        return element
        
    except Employe.DoesNotExist:
        print(f"❌ Employé {matricule} non trouvé")
    except RubriquePaie.DoesNotExist:
        print(f"❌ Rubrique {code_rubrique} non trouvée")


def retirer_element(matricule, code_rubrique):
    """Désactiver un élément de salaire"""
    try:
        employe = Employe.objects.get(matricule=matricule)
        rubrique = RubriquePaie.objects.get(code_rubrique=code_rubrique)
        
        elements = ElementSalaire.objects.filter(
            employe=employe,
            rubrique=rubrique,
            actif=True
        )
        
        count = elements.update(actif=False)
        print(f"✅ {count} élément(s) désactivé(s)")
        
    except Employe.DoesNotExist:
        print(f"❌ Employé {matricule} non trouvé")
    except RubriquePaie.DoesNotExist:
        print(f"❌ Rubrique {code_rubrique} non trouvée")


def lister_elements(matricule):
    """Lister tous les éléments actifs d'un employé"""
    try:
        employe = Employe.objects.get(matricule=matricule)
        
        elements = ElementSalaire.objects.filter(
            employe=employe,
            actif=True
        ).select_related('rubrique')
        
        print(f"\n📋 Éléments de salaire pour {employe.nom_complet}:\n")
        
        gains = []
        retenues = []
        
        for elem in elements:
            info = {
                'libelle': elem.rubrique.libelle_rubrique,
                'montant': elem.montant or 0,
                'taux': elem.taux,
            }
            
            if elem.rubrique.type_rubrique == 'gain':
                gains.append(info)
            else:
                retenues.append(info)
        
        print("💰 GAINS:")
        for gain in gains:
            if gain['montant']:
                print(f"  • {gain['libelle']}: {gain['montant']:,.0f} GNF")
            elif gain['taux']:
                print(f"  • {gain['libelle']}: {gain['taux']}%")
        
        print("\n📉 RETENUES:")
        for retenue in retenues:
            if retenue['montant']:
                print(f"  • {retenue['libelle']}: {retenue['montant']:,.0f} GNF")
            elif retenue['taux']:
                print(f"  • {retenue['libelle']}: {retenue['taux']}%")
        
        total_gains = sum(g['montant'] for g in gains)
        total_retenues = sum(r['montant'] for r in retenues)
        
        print(f"\n📊 TOTAL GAINS: {total_gains:,.0f} GNF")
        print(f"📊 TOTAL RETENUES: {total_retenues:,.0f} GNF")
        
    except Employe.DoesNotExist:
        print(f"❌ Employé {matricule} non trouvé")


# EXEMPLES D'UTILISATION
if __name__ == '__main__':
    print("🎯 GESTION DES GAINS ET RETENUES\n")
    
    # 1. Ajouter une prime de transport
    print("1️⃣ Ajout d'une prime de transport...")
    ajouter_gain('COMATEX-001', 'PRIME_TRANSPORT', 300000)
    
    # 2. Ajouter une avance temporaire
    print("\n2️⃣ Ajout d'une avance temporaire...")
    ajouter_retenue('COMATEX-001', 'AVANCE_SAL', 200000, temporaire=True)
    
    # 3. Lister les éléments
    print("\n3️⃣ Liste des éléments...")
    lister_elements('COMATEX-001')
    
    # 4. Retirer un élément
    print("\n4️⃣ Retrait de la prime de transport...")
    retirer_element('COMATEX-001', 'PRIME_TRANSPORT')
```

### **Exécuter le script**
```bash
python gerer_elements_salaire.py
```

---

## 📊 TYPES DE RUBRIQUES DISPONIBLES

### **GAINS (Augmentent le salaire)**

| Code | Libellé | Type |
|------|---------|------|
| `SAL_BASE` | Salaire de base | Montant fixe |
| `PRIME_TRANSPORT` | Prime de transport | Montant fixe |
| `PRIME_ANCIENNETE` | Prime d'ancienneté | Taux % |
| `PRIME_RESP` | Prime de responsabilité | Montant fixe |
| `PRIME_PROD` | Prime de production | Montant fixe |
| `IND_FONCTION` | Indemnité de fonction | Montant fixe |
| `IND_REPAS` | Indemnité de repas | Montant fixe |
| `ALLOC_LOGEMENT` | Allocation logement | Montant fixe |
| `HS_25` | Heures supplémentaires 25% | Montant calculé |
| `COMMISSION_CA` | Commission sur CA | Montant variable |

### **RETENUES (Diminuent le salaire)**

| Code | Libellé | Type |
|------|---------|------|
| `AVANCE_SAL` | Avance sur salaire | Montant fixe |
| `PRET_LOGEMENT` | Remboursement prêt logement | Montant fixe |
| `RET_SYNDICAT` | Cotisation syndicale | Montant fixe |
| `RET_DISCIPLINAIRE` | Retenue disciplinaire | Montant fixe |
| `CNSS_SAL` | CNSS salarié | Taux % (auto) |
| `IRS_A` | RTS/IRSA | Calculé (auto) |

---

## 💡 CAS D'USAGE COURANTS

### **1. Ajouter une prime mensuelle permanente**
```python
ajouter_gain('COMATEX-001', 'PRIME_TRANSPORT', 300000)
# ✅ Sera ajoutée chaque mois automatiquement
```

### **2. Ajouter une avance ponctuelle**
```python
ajouter_retenue('COMATEX-001', 'AVANCE_SAL', 200000, temporaire=True)
# ✅ Sera retenue ce mois uniquement
```

### **3. Ajouter un remboursement de prêt sur 12 mois**
```python
employe = Employe.objects.get(matricule='COMATEX-001')
rubrique = RubriquePaie.objects.get(code_rubrique='PRET_LOGEMENT')

ElementSalaire.objects.create(
    employe=employe,
    rubrique=rubrique,
    montant=Decimal('400000'),  # 400k/mois
    date_debut=date(2025, 11, 1),
    date_fin=date(2026, 10, 31),  # 12 mois
    actif=True,
    recurrent=True
)
# ✅ 400k seront retenus chaque mois pendant 12 mois
```

### **4. Ajouter une prime d'ancienneté (5% du salaire)**
```python
employe = Employe.objects.get(matricule='COMATEX-001')
rubrique = RubriquePaie.objects.get(code_rubrique='PRIME_ANCIENNETE')

ElementSalaire.objects.create(
    employe=employe,
    rubrique=rubrique,
    taux=Decimal('5.00'),  # 5%
    base_calcul='SALAIRE_BASE',
    date_debut=date(2025, 11, 1),
    actif=True,
    recurrent=True
)
# ✅ 5% du salaire de base sera ajouté chaque mois
```

### **5. Retirer temporairement une prime (congé sans solde)**
```python
element = ElementSalaire.objects.get(
    employe__matricule='COMATEX-001',
    rubrique__code_rubrique='PRIME_TRANSPORT'
)
element.actif = False
element.save()
# ✅ Prime désactivée (peut être réactivée plus tard)
```

---

## ⚠️ POINTS IMPORTANTS

### **1. Montant vs Taux**
- **Montant** : Valeur fixe (ex: 300,000 GNF)
- **Taux** : Pourcentage d'une base (ex: 5% du salaire)

### **2. Récurrent vs Ponctuel**
- **Récurrent** : Appliqué chaque mois (primes régulières)
- **Ponctuel** : Une seule fois (avances, bonus exceptionnels)

### **3. Date de fin**
- **Vide** : Élément permanent
- **Définie** : Élément temporaire (s'arrête automatiquement)

### **4. Actif vs Inactif**
- **Actif** : Pris en compte dans les calculs
- **Inactif** : Ignoré mais conservé dans l'historique

### **5. Ordre de calcul**
Les éléments sont calculés dans l'ordre défini par `ordre_calcul` de la rubrique :
1. Salaire de base
2. Primes et indemnités
3. Heures supplémentaires
4. Cotisations sociales (CNSS)
5. RTS/IRSA
6. Autres retenues

---

## ✅ VÉRIFICATION

### **Après avoir ajouté/retiré un élément**

1. **Vérifier dans l'admin**
   ```
   /admin/paie/elementsalaire/
   ```

2. **Lister les éléments actifs**
   ```python
   lister_elements('COMATEX-001')
   ```

3. **Calculer un bulletin de test**
   ```python
   from paie.services import CalculateurPaie
   from paie.models import PeriodePaie
   
   periode = PeriodePaie.objects.get(mois=11, annee=2025)
   employe = Employe.objects.get(matricule='COMATEX-001')
   
   calc = CalculateurPaie(employe, periode)
   calc.calculer_bulletin()
   
   print(f"Brut: {calc.montants['brut']:,.0f} GNF")
   print(f"Net: {calc.montants['net']:,.0f} GNF")
   ```

---

## 📞 AIDE RAPIDE

### **Commandes Utiles**

```bash
# Lister toutes les rubriques disponibles
python manage.py shell
>>> from paie.models import RubriquePaie
>>> for r in RubriquePaie.objects.filter(actif=True):
...     print(f"{r.code_rubrique}: {r.libelle_rubrique} ({r.type_rubrique})")

# Lister les éléments d'un employé
>>> from employes.models import Employe
>>> from paie.models import ElementSalaire
>>> employe = Employe.objects.get(matricule='COMATEX-001')
>>> for e in ElementSalaire.objects.filter(employe=employe, actif=True):
...     print(e)
```

---

## 🎯 RÉSUMÉ

### **Pour AJOUTER un gain/retenue :**
1. ✅ Via Admin : `/admin/paie/elementsalaire/add/`
2. ✅ Via Shell : `ElementSalaire.objects.create(...)`
3. ✅ Via Script : `python gerer_elements_salaire.py`

### **Pour RETIRER un gain/retenue :**
1. ✅ Désactiver : `actif = False`
2. ✅ Date de fin : `date_fin = ...`
3. ✅ Supprimer : `element.delete()`

### **Pour VÉRIFIER :**
1. ✅ Admin : `/admin/paie/elementsalaire/`
2. ✅ Shell : `lister_elements('MATRICULE')`
3. ✅ Bulletin : Calculer un bulletin de test

---

**Le système est flexible et permet de gérer tous les cas de figure !** 💰

---

**Développé avec ❤️ pour la Guinée**
