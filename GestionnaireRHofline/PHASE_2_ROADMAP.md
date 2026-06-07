# 📅 PHASE 2 ROADMAP - FISCALITÉ & DÉCLARATIONS

## Vue d'ensemble Phase 2

**Objectif**: Implémenter la gestion complète de la fiscalité (TVA, déclarations, régimes)

**Durée estimée**: 60-80 heures = 2 semaines (full-time)

**Démarrage**: Après finalisation Phase 1.5 (fin semaine 1)

**Réutilisation**: ~70% du code Phase 1

---

## 📊 Scope Phase 2

### Cas d'usage prioritaires

```
P0 (Critical):
├── Gestion régimes TVA (Normal, Simplifié, Exempt)
├── Calcul automatique TVA sur écritures
├── Récapitulatifs TVA périodiques (mensuels)
└── Verrouillage exercices (une fois finalisé)

P1 (Important):
├── Génération déclarations (DIVA-DEB)
├── Déclarations retenues à la source
├── Rapports analytiques TVA
└── Export EDI/XML administration

P2 (Nice-to-have):
├── Intégration EDI-commerce (DES)
├── Alerts règles TVA
└── Historique modifications TVA
```

---

## 🏗️ Architecture Phase 2

### Structure des fichiers

```
comptabilite/fiscalite/
├── __init__.py
├── models.py              [~300 L] TVA, Déclarations, Régimes
├── services.py            [~200 L] CalculTVA, GénérationDéclaration
├── views.py               [~150 L] RÉUTILISE 80% Phase 1
├── forms.py               [~100 L] RÉUTILISE Mixins
├── urls.py                [~30 L]
├── signals.py             [~50 L]
├── tests.py               [~200 L]
├── admin.py               [~80 L]
├── apps.py                [~20 L]
└── templates/
    ├── tva/
    │   ├── regime_list.html
    │   ├── regime_form.html
    │   └── tva_recap.html
    └── declarations/
        ├── list.html
        ├── detail.html
        ├── form.html
        └── export.html
```

**Total nouvelle code**: ~500 lignes  
**Réutilisation code Phase 1**: 80% (services, vues, forms, tests)

---

## 📋 Détail des tâches Phase 2

### Semaine 3: Modèles + Services (25 heures)

#### Jour 1: Modèles TVA (8h)
```python
# Models à créer

class RegimeTVA(models.Model):
    """Régime fiscal TVA"""
    code = CharField(max_length=20)  # NORMAL, SIMPLIFIE, EXEMPT
    libelle = CharField(max_length=100)
    taux_defaut = DecimalField()     # 20%, 5.5%, 0%
    entreprise = ForeignKey(Entreprise)
    actif = BooleanField()
    
class TauxTVA(models.Model):
    """Taux TVA applicables"""
    regime = ForeignKey(RegimeTVA)
    code_operation = CharField()      # VENTE, ACHAT, IMPORT, etc.
    taux = DecimalField()
    date_debut = DateField()
    date_fin = DateField(null=True)
    
class DeclarationTVA(models.Model):
    """Déclaration TVA périodique"""
    numero_declaration = CharField()
    exercice = ForeignKey(ExerciceComptable)
    periode_debut = DateField()
    periode_fin = DateField()
    statut = CharField()              # BROUILLON, SOUMISE, ACCEPTEE, REFUSEE
    montant_tva_collecte = DecimalField()
    montant_tva_deductible = DecimalField()
    solde = DecimalField()
    date_depot = DateField(null=True)
    reference_administration = CharField(null=True)
    
class LigneDeclarationTVA(models.Model):
    """Lignes détails déclaration"""
    declaration = ForeignKey(DeclarationTVA)
    code_ligne = CharField()          # 01, 02, 03... (cadres DIVA)
    libelle = CharField()
    montant_ht = DecimalField()
    montant_tva = DecimalField()
    montant_ttc = DecimalField()
```

**Checklist**:
- [ ] Modèles TVA créés
- [ ] Relations définies
- [ ] Migrations générées
- [ ] Admin enregistrés

#### Jour 2-3: Services fiscalité (12h)
```python
# Services à créer

class FiscaliteService(BaseComptaService):
    """Service gestion TVA et déclarations"""
    
    def calculer_tva_ecriture(self, ecriture, regime):
        """Calcule TVA applicable sur une écriture"""
        
    def generer_recap_tva(self, exercice, periode):
        """Génère récapitulatif TVA pour période"""
        
    def creer_declaration_tva(self, exercice, periode):
        """Crée déclaration TVA automatiquement"""
        
    def valider_declaration(self, declaration):
        """Valide avant soumission"""
        
    def exporter_diva(self, declaration):
        """Exporte au format DIVA-DEB"""

class CalculTVAService(BaseComptaService):
    """Calculs TVA complexes"""
    
    def tva_collecte(self, ecritures_vente):
        """Somme TVA sur ventes"""
        
    def tva_deductible(self, ecritures_achat):
        """Somme TVA sur achats"""
        
    def proration(self, montant_total, pct_deductible):
        """Calcul prorata déductibilité"""
```

**Checklist**:
- [ ] FiscaliteService complète
- [ ] CalculTVAService complète
- [ ] Tous les cas d'usage testés
- [ ] Erreurs gérées

#### Jour 4-5: Hooks & Signaux (5h)
```python
# Signaux Phase 2

@receiver(post_save, sender=EcritureComptable)
def on_ecriture_created(sender, instance, created, **kwargs):
    """Applique TVA automatiquement si écriture vente/achat"""
    if created and instance.type_ecriture in ['VENTE', 'ACHAT']:
        service = FiscaliteService(instance.entreprise, instance.utilisateur)
        service.calculer_tva_ecriture(instance, instance.regime_tva)

@receiver(pre_delete, sender=DeclarationTVA)
def on_declaration_deleted(sender, instance, **kwargs):
    """Empêche suppression si soumise"""
    if instance.statut in ['SOUMISE', 'ACCEPTEE']:
        raise ValidationError("Impossible de supprimer une déclaration soumise")
```

**Checklist**:
- [ ] Signaux créés
- [ ] Tests signaux

---

### Semaine 4-5: Vues + Forms (25 heures)

#### Jour 1: Vues TVA (8h)
```python
# Views réutilisant Phase 1

class RegimeTVAListView(ComptaListView):
    model = RegimeTVA
    search_fields = ['code', 'libelle']
    filter_fields = ['actif']
    # 80% réutilisé

class DeclarationTVAListView(ComptaListView):
    model = DeclarationTVA
    search_fields = ['numero_declaration']
    filter_fields = ['statut', 'exercice']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoute statistiques TVA
        context['total_collecte'] = self.get_total_collecte()
        context['total_deductible'] = self.get_total_deductible()
        return context

class DeclarationTVADetailView(ComptaDetailView):
    model = DeclarationTVA
    # Affiche détails + lignes + options export
```

**Checklist**:
- [ ] Toutes vues liste/détail créées
- [ ] Filtres fonctionnels
- [ ] Contexte enrichi

#### Jour 2: Formulaires (6h)
```python
# Forms réutilisant ComptaBaseForm

class RegimeTVAForm(ComptaBaseForm):
    class Meta:
        model = RegimeTVA
        fields = ['code', 'libelle', 'taux_defaut', 'actif']
    
    def clean_code(self):
        # Validation code unique par entreprise

class DeclarationTVAForm(ComptaBaseForm):
    class Meta:
        model = DeclarationTVA
        fields = ['numero_declaration', 'periode_debut', 'periode_fin', 'statut']
    
    def clean(self):
        # Validation dates
        # Vérification périodes chevauchement
```

**Checklist**:
- [ ] Formulaires créés
- [ ] Validations métier
- [ ] Tests formulaires

#### Jour 3: Templates (6h)
```html
<!-- tva/regime_list.html - réutilise list.html Phase 1 -->
{% extends "comptabilite/base/list.html" %}
{% block title %}Régimes TVA{% endblock %}

<!-- declarations/list.html -->
{% extends "comptabilite/base/list.html" %}
{% block filters %}
  <div class="filter-section">
    <select name="statut">
      <option value="">Tous</option>
      <option value="BROUILLON">Brouillon</option>
      <option value="SOUMISE">Soumise</option>
      <option value="ACCEPTEE">Acceptée</option>
    </select>
    <input type="date" name="periode_debut" placeholder="Du">
    <input type="date" name="periode_fin" placeholder="Au">
  </div>
{% endblock %}

<!-- declarations/detail.html -->
{% extends "comptabilite/base/detail.html" %}
{% block content %}
<div class="declaration-detail">
  <h2>Déclaration {{ object.numero_declaration }}</h2>
  
  <section class="recap">
    <h3>Récapitulatif</h3>
    <table>
      <tr><td>TVA Collectée</td><td>{{ object.montant_tva_collecte }}</td></tr>
      <tr><td>TVA Déductible</td><td>{{ object.montant_tva_deductible }}</td></tr>
      <tr><td>Solde</td><td>{{ object.solde }}</td></tr>
    </table>
  </section>
  
  <section class="lignes">
    <h3>Détails</h3>
    <table class="lines-table">
      <tbody>
        {% for ligne in object.lignes.all %}
        <tr>
          <td>{{ ligne.code_ligne }}</td>
          <td>{{ ligne.libelle }}</td>
          <td>{{ ligne.montant_ht }}</td>
          <td>{{ ligne.montant_tva }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </section>
  
  <section class="actions">
    <a href="{% url 'diva-export' object.id %}" class="btn btn-primary">
      Exporter DIVA
    </a>
    <a href="{% url 'pdf-export' object.id %}" class="btn btn-secondary">
      Générer PDF
    </a>
  </section>
</div>
{% endblock %}
```

**Checklist**:
- [ ] Tous les templates créés
- [ ] Bootstrap 5 appliqué
- [ ] Responsive design OK

#### Jour 4-5: Integration (5h)
```python
# URLs Phase 2

urlpatterns = [
    path('fiscalite/regimes/', RegimeTVAListView.as_view(), name='regime-list'),
    path('fiscalite/regimes/create/', RegimeTVACreateView.as_view(), name='regime-create'),
    path('fiscalite/declarations/', DeclarationTVAListView.as_view(), name='declaration-list'),
    path('fiscalite/declarations/<int:pk>/', DeclarationTVADetailView.as_view(), name='declaration-detail'),
    path('api/fiscalite/calc-tva/', ajax_calculer_tva, name='ajax-calc-tva'),
    path('api/fiscalite/export-diva/', ajax_export_diva, name='ajax-export-diva'),
]
```

**Checklist**:
- [ ] URLs intégrées
- [ ] AJAX endpoints OK
- [ ] Navigation menée

---

### Semaine 6: Tests + Documentation (20 heures)

#### Tests (12h)
```python
# Couverture tests

class FiscaliteServiceTest(TestCase):
    def test_calculer_tva(self):
        """TVA calculée correctement"""
    
    def test_generer_declaration(self):
        """Déclaration générée automatiquement"""
    
    def test_export_diva(self):
        """Export DIVA format valide"""

class DeclarationTVATest(TestCase):
    def test_workflow_complet(self):
        """Workflow: Création → Calcul → Soumission → Export"""

class FiscalitePermissionTest(TestCase):
    def test_acces_roles(self):
        """Permissions par rôle vérifiées"""
```

**Checklist**:
- [ ] Coverage > 80%
- [ ] Tous les cas d'usage testés
- [ ] E2E tests passent

#### Documentation (8h)
```markdown
# Phase 2 Fiscalité - Documentation utilisateur

## Manuel TVA
- Création régime TVA
- Configuration taux
- Calcul automatique

## Déclarations
- Génération périodique
- Validation avant soumission
- Export DIVA-DEB

## Rapports
- Récapitulatifs TVA
- Analyse par période
```

**Checklist**:
- [ ] Manuel utilisateur complété
- [ ] Guide admin TVA
- [ ] API documentation
- [ ] Examples réels

---

## 🎯 Métriques de succès Phase 2

| Métrique | Cible | Statut |
|----------|-------|--------|
| Code production-ready | 100% | À valider |
| Réutilisation Phase 1 | > 70% | À valider |
| Test coverage | > 80% | À valider |
| Déclarations générées | Automatique | À valider |
| Export DIVA-DEB | Fonctionnel | À valider |
| Documentation | Complète | À valider |

---

## 📈 Timeline détaillée Phase 2

```
Semaine 3 (40h):
├── Lun-Mar: Modèles + Migrations (8h)
├── Mer-Jeu: Services (12h)
├── Ven: Signaux + Tests unitaires (8h)
└── 💾 Commit: "Phase 2 - Models & Services"

Semaine 4 (40h):
├── Lun-Mar: Vues (8h)
├── Mer: Formulaires (6h)
├── Jeu-Ven: Templates (6h)
├── + Tests intégration (10h)
└── 💾 Commit: "Phase 2 - Views & Forms"

Semaine 5 (20h):
├── Lun-Mer: Tests complets (12h)
├── Jeu-Ven: Documentation + Perf (8h)
└── 💾 Commit: "Phase 2 - Tests & Docs"

Total Phase 2: 100h (2 semaines)
```

---

## 🚀 Progression post-Phase 2

### Immédiate (après livraison):
1. ✅ Déclarations TVA automatiques
2. ✅ Export DIVA-DEB pour administration
3. ✅ Rapports analytiques TVA

### Court terme (semaine 7-8):
1. Audit complet (Phase 3)
2. Verrouillage exercices
3. Piste d'audit financière

### Moyen terme (semaine 9+):
1. Paie intégrée (Phase 4)
2. Immobilisations
3. Stocks
4. Analytique

---

## 📞 Support Phase 2

**Questions sur patterns**?
→ Relire PHASE_1_FOUNDATION_COMPLETE.md (Services, Views, Forms)

**Template code**?
→ Copier RapprochementService, ComptaListView

**Tests**?
→ Utiliser fixtures Phase 1 + Factory pattern

---

## ✅ Checklist Démarrage Phase 2

- [ ] Phase 1 finalisée (5.5h complètes)
- [ ] Code Phase 1 mergé en production
- [ ] Équipe confirmée (2 devs, 1 QA?)
- [ ] Période bloquée au calendrier
- [ ] Accès administration/servers confirmé
- [ ] Outils de monitoring prêts

