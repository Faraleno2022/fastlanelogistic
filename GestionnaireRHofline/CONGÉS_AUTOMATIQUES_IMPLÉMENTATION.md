# 🎯 Implémentation Automatique des Congés Acquis

## Vue d'ensemble
Deux solutions pour assurer que les congés acquis sont correctement calculés et remplis pour tous les employés.

---

## 📋 Solution 1: Auto-calcul lors de la génération de bulletin (IMPLÉMENTÉE)

### Fichier modifié
**Location:** `paie/services.py` dans la classe `MoteurCalculPaie`

### Modifications apportées

#### 1️⃣ Ajout de deux méthodes à MoteurCalculPaie (lignes 1248-1373)

```python
def _calculer_anciennete_mois(self, date_embauche, date_ref=None):
    """Calcule l'ancienneté en mois"""
    # Formule: (années_diff × 12) + mois_diff + ajustement_jour
    # Returns: Decimal(0-120+)
```

```python
def _calculer_conges_acquis(self):
    """Calcule automatiquement les congés acquis et crée SoldeConge"""
    # Règle Guinée: 2.5 jours/mois × ancienneté
    # Max: 30 jours/an
    # Crée/met à jour SoldeConge avec ancienneté-based calculation
```

#### 2️⃣ Appel intégré dans generer_bulletin() (ligne 1196)

```python
# ✨ NOUVEAU: Calculer et créer automatiquement les congés acquis
# Cela crée/met à jour le SoldeConge avec ancienneté-based calculation
self._calculer_conges_acquis()
```

### Résultat

**✅ Dorénavant, chaque bulletin généré:**
- Crée ou met à jour automatiquement le SoldeConge de l'employé
- Calcule les congés aquis: `ancienneté_mois × jours_par_mois`
- Respecte la config: `ConfigPaieEntreprise.jours_conges_par_mois` (défaut 2.50)
- S'arrête à 30 jours/an maximum

### Exemple
**Cas FARA LENO (embauche 26/01/2026, bulletin Avril 2026):**
- Ancienneté: 3 mois
- Config: 2.5 jours/mois (Code du Travail)
- Congés acquis = 3 × 2.5 = **7.5 jours** ✅

---

## 📋 Solution 2: Script de remplissage batch (fill_conges_acquis.py)

### Fichier
**Location:** `fill_conges_acquis.py` (workspace root)

### Utilisation
```bash
cd /chemin/vers/gestionrh
source venv/bin/activate
python fill_conges_acquis.py
```

### Sortie attendue
```
════════════════════════════════════════════════════════════════════════════
📊 REMPLISSAGE AUTOMATIQUE DES CONGÉS ACQUIS - CODE DU TRAVAIL GUINÉE
════════════════════════════════════════════════════════════════════════════

🔍 Recherche des employés actifs...
🔍 Nombre d'employés actifs: X

📋 Calcul des congés pour chaque employé...
  ✅ FARA LENO      (26/01/2026): 7.5 j acquis, 0 pris, 7.5 restants
  ✅ DAV JOB        (15/02/2026): 6.0 j acquis, 0 pris, 6.0 restants
  ...

═════════════════════════════════════════════════════════════════════════════
✅ Résumé: X employés mis à jour
   • Nombre de SoldeConge créés: Y
   • Nombre de SoldeConge mis à jour: Z
   • Congés totaux acquis: WWW jours
═════════════════════════════════════════════════════════════════════════════
```

### Avantages
- ✅ Remplissage en batch de tous les employés d'un coup
- ✅ Rapport détaillé avec exemples
- ✅ Multi-entreprise capable
- ✅ Peut être exécuté plusieurs fois sans risque (mise à jour smart)

---

## 📐 Formule de Calcul (Code du Travail Guinée - Article 195)

### Standard
```
Total congés acquis = Ancienneté_mois × 2.5 jours/mois
Maximum = 30 jours/an
```

### Ancienneté en mois
```
ancienneté = (années_diff × 12) + mois_diff + ajustement_jour

Où:
  années_diff  = année_courante - année_embauche
  mois_diff    = mois_courant - mois_embauche
  ajustement   = -1 si jour_courant < jour_embauche, sinon 0
```

### Bonus ancienneté (optionnel, configurable)
Via `ConfigPaieEntreprise`:
- `jours_conges_anciennete`: Nombre de jours supplémentaires
- `tranche_anciennete_annees`: Tous les N ans

**Exemple:** +2 jours tous les 5 ans
```
Bonus = (ancienneté_ans // 5) × 2 jours
```

---

## 🔧 Configuration

### Via l'interface Django admin
**Model:** `ConfigPaieEntreprise`

**Champs pertinents:**
- `jours_conges_par_mois` (Decimal 3,2)
  - Default: 1.50 (Convention)
  - Recommandé Guinée: 2.50 (Code du Travail) ⭐
  - Range: 1.5 - 2.5

- `jours_conges_anciennete` (Integer)
  - Bonus à ajouter (ex: 2)
  - Default: 0 (aucun bonus)

- `tranche_anciennete_annees` (Integer)
  - Fréquence du bonus (ex: 5)
  - Default: 5

### Via Python/Script
```python
from enterprises.models import ConfigPaieEntreprise

config = ConfigPaieEntreprise.objects.get(entreprise=ma_entreprise)

# Appliquer Code du Travail Guinée (2.5 j/mois)
config.appliquer_mode_code_travail()
# Ou directement:
config.jours_conges_par_mois = Decimal('2.50')
config.save()
```

---

## 🧪 Tests de Validation

### 1️⃣ Test du calcul pour un employé spécifique

```python
from paie.services import MoteurCalculPaie
from paie.models import Periode
from employes.models import Employe

emp = Employe.objects.get(id=123)
periode = Periode.objects.get(annee=2026, mois=4)

moteur = MoteurCalculPaie(emp, periode)
moteur.calculer_bulletin()

conges_acquis = moteur._calculer_conges_acquis()
print(f"Congés acquis: {conges_acquis} jours")
```

### 2️⃣ Vérifier que SoldeConge a été créé

```python
from temps_travail.models import SoldeConge

solde = SoldeConge.objects.get(employe=emp, annee=2026)
print(f"Congés acquis: {solde.conges_acquis}")
print(f"Congés pris: {solde.conges_pris}")
print(f"Congés restants: {solde.conges_restants}")  # Calculated property
```

### 3️⃣ Générer un bulletin et vérifier

```bash
python manage.py shell
>>> from paie.services import generer_bulletin_employe
>>> bulletin = generer_bulletin_employe(emp_id=123, annee=2026, mois=4)
>>> print(bulletin)
# Via l'interface web: aller sur le bulletin et vérifier l'onglet "Congés"
```

### 4️⃣ Vérifier via l'interface web

1. Aller à: **Paie > Bulletins de Paie**
2. Générer/régénérer un bulletin
3. Cliquer sur **Afficher** ou **Télécharger PDF**
4. Vérifier que la section "Congés" affiche:
   - ✅ "Congés acquis: X j"
   - ✅ "Congés pris: Y j" (si applicable)
   - ✅ "Solde congés: Z j"

---

## 📊 Résultats Attendus sur Bulletins Existants

### Avant implémentation
```
Congés équis: 0 j        ❌ (incorrecte)
Congés pris:  0 j
Solde congés: 0 j
```

### Après solution 1 (auto-calcul à la génération)
- ✅ Tous les **nouveaux bulletins** auront congés correctes
- ⏳ Bulletins existants: rester à 0 (peuvent être régénérés)

### Après solution 2 (script batch)
- ✅ **Rétroactivement** remplir tous les SoldeConge
- ✅ Tous les bulletins afficheront congés correctes

---

## 📝 Problèmes Résolus

| Anomalie | État Avant | État Après |
|----------|-----------|-----------|
| **Congés acquis = 0** | ❌ Non-conforme | ✅ Calculé automatiquement |
| **FARA LENO** (2 mois) | Affichait 0 j | Affichera 5-7.5 j |
| **DAV JOB** (1.5 mois) | Affichait 0 j | Affichera 3.75 j |

---

## 🚀 Déploiement en Production

### Étapes
1. ✅ Code modifié dans paie/services.py
2. ⏳ Redémarrer application Django (uWSGI)
3. ⏳ Tester un nouveau bulletin via interface
4. ⏳ Exécuter `python fill_conges_acquis.py` pour remplir rétroactivement
5. ✅ Régénérer/afficher bulletins existants → congés correctes

### Commandes
```bash
# Sur production
sudo systemctl restart gunicorn_gestionrh
# ou
sudo systemctl restart uWSGI_gestionrh

# Puis exécuter script
cd /home/guineerh/gestionrh
source venv/bin/activate
python fill_conges_acquis.py
```

---

## ⚠️ Considérations Importantes

### Respect du Code du Travail Guinée
✅ **Implémentée:** Formule officielle 2.5 jours/mois  
✅ **Maximum:** 30 jours/an (cadre légal)  
✅ **Ancienneté progressive:** Chaque mois compté

### Compatibilité
✅ Multi-entreprise (via ConfigPaieEntreprise)  
✅ Configuration flexible (jours_conges_par_mois)  
✅ Historique préservé (n'efface pas conges_pris)

### Performance
✅ Léger: Une seule requête get_or_create par bulletin  
✅ Atomic: Protégé par @transaction.atomic  
✅ Fallback: En cas d'erreur, ne bloque pas le bulletin

---

## 📖 Documentation Supplémentaire

- **Code du Travail Guinée Article 195:** Congés légaux
- **Article 221:** Heures supplémentaires (déjà implémentées)
- **CONFIG ACTUELLE:** `ConfigPaieEntreprise.jours_conges_par_mois`
- **MODÈLES:** `SoldeConge`, `Conge`, `Employe`, `BulletinPaie`

---

## ✅ Checklist de Vérification

- [ ] Modifications dans `paie/services.py` appliquées
- [ ] Deux nouvelles méthodes présentes
- [ ] Appel `self._calculer_conges_acquis()` dans generer_bulletin()
- [ ] Script `fill_conges_acquis.py` disponible (optionnel)
- [ ] Redémarrage application web effectué
- [ ] Test: Générer un nouveau bulletin
- [ ] Vérifier: SoldeConge créé via admin Django
- [ ] Vérifier: Bulletin affiche congés corrects
- [ ] Test: Exécuter script batch (optionnel)
- [ ] Documentation mise à jour

---

**Statut:** ✅ IMPLÉMENTÉE  
**Priorité:** 🔴 HAUTE  
**Conformité:** Code du Travail Guinée Article 195  
**Date:** Avril 2026

