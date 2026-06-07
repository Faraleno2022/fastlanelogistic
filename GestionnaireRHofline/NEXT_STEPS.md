# 🚀 PROCHAINES ÉTAPES - Gestionnaire RH Guinée

## 📌 Où en sommes-nous ?

**Statut actuel** : 30% complété  
**Fondations** : ✅ Solides (BDD, modèles, dashboard)  
**À faire** : 70% (vues, forms, templates pour tous les modules)

---

## 🎯 PLAN D'ACTION DÉTAILLÉ

### 🔴 PHASE 1 : MODULE EMPLOYÉS (2-3 jours) - PRIORITÉ CRITIQUE

#### Jour 1 : Liste et Recherche
**Créer `employes/views.py`** :
```python
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Employe
from .forms import EmployeForm

class EmployeListView(LoginRequiredMixin, ListView):
    model = Employe
    template_name = 'employes/list.html'
    context_object_name = 'employes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Employe.objects.filter(statut_employe='Actif')
        # Ajouter recherche et filtres
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(prenoms__icontains=search) |
                Q(matricule__icontains=search)
            )
        return queryset.select_related('service', 'poste', 'etablissement')
```

**Créer `employes/urls.py`** :
```python
from django.urls import path
from . import views

app_name = 'employes'

urlpatterns = [
    path('', views.EmployeListView.as_view(), name='list'),
    path('create/', views.EmployeCreateView.as_view(), name='create'),
    path('<int:pk>/', views.EmployeDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.EmployeUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.EmployeDeleteView.as_view(), name='delete'),
]
```

**Créer `templates/employes/list.html`** :
- Barre de recherche
- Filtres (statut, service, type contrat)
- Table DataTables
- Boutons actions (voir, modifier, supprimer)
- Pagination
- Bouton "Nouvel employé"

#### Jour 2 : Formulaire Création
**Créer `employes/forms.py`** :
```python
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column
from .models import Employe

class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['civilite', 'nom', 'prenoms', 'sexe', 'date_naissance',
                  'num_cnss_individuel', 'telephone_principal', 'email_professionnel',
                  'etablissement', 'service', 'poste', 'date_embauche', 'type_contrat']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'date_embauche': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset('État civil',
                Row(
                    Column('civilite', css_class='col-md-2'),
                    Column('nom', css_class='col-md-5'),
                    Column('prenoms', css_class='col-md-5'),
                ),
                Row(
                    Column('sexe', css_class='col-md-4'),
                    Column('date_naissance', css_class='col-md-4'),
                    Column('num_cnss_individuel', css_class='col-md-4'),
                ),
            ),
            Fieldset('Contact',
                Row(
                    Column('telephone_principal', css_class='col-md-6'),
                    Column('email_professionnel', css_class='col-md-6'),
                ),
            ),
            Fieldset('Informations professionnelles',
                Row(
                    Column('etablissement', css_class='col-md-4'),
                    Column('service', css_class='col-md-4'),
                    Column('poste', css_class='col-md-4'),
                ),
                Row(
                    Column('date_embauche', css_class='col-md-6'),
                    Column('type_contrat', css_class='col-md-6'),
                ),
            ),
        )
```

**Créer `templates/employes/form.html`** :
- Formulaire avec Crispy Forms
- Validation côté client
- Boutons Enregistrer/Annuler

#### Jour 3 : Fiche Détaillée
**Créer `templates/employes/detail.html`** :
- En-tête avec photo et infos principales
- Onglets :
  1. Informations générales
  2. Contrats
  3. Salaire
  4. Congés
  5. Formations
  6. Documents
- Boutons actions (modifier, supprimer, imprimer)

---

### 🟡 PHASE 2 : MODULE TEMPS (2 jours)

#### Jour 4 : Pointages
**Créer `temps_travail/views.py`** :
```python
class PointageListView(LoginRequiredMixin, ListView):
    model = Pointage
    template_name = 'temps_travail/pointages_list.html'
    
class PointageCreateView(LoginRequiredMixin, CreateView):
    model = Pointage
    form_class = PointageForm
    template_name = 'temps_travail/pointage_form.html'
```

**Fonctionnalités** :
- Saisie pointage quotidien
- Calcul automatique heures travaillées
- Détection heures supplémentaires
- Validation hiérarchique

#### Jour 5 : Congés
**Créer vues congés** :
- Liste des demandes
- Formulaire demande
- Validation (2 niveaux)
- Calendrier visuel
- Calcul soldes automatique

---

### 🟠 PHASE 3 : MODULE PAIE (3-4 jours)

#### Jour 6-7 : Moteur de Calcul
**Créer `paie/calcul.py`** :
```python
class MoteurCalculPaie:
    """Moteur de calcul des bulletins de paie"""
    
    def __init__(self, employe, periode):
        self.employe = employe
        self.periode = periode
        self.bulletin = None
    
    def calculer(self):
        """Calcule le bulletin complet"""
        # 1. Salaire brut
        brut = self.calculer_brut()
        
        # 2. Base CNSS (plafonné 3M GNF)
        base_cnss = min(brut, 3000000)
        
        # 3. CNSS employé (5%)
        cnss_employe = base_cnss * 0.05
        
        # 4. INAM (2.5%)
        inam = brut * 0.025
        
        # 5. Base IRG
        base_irg = brut - cnss_employe - inam
        
        # 6. Abattement IRG (20%, max 300K)
        abattement = min(base_irg * 0.20, 300000)
        base_irg_nette = base_irg - abattement
        
        # 7. IRG progressif
        irg = self.calculer_irg_progressif(base_irg_nette)
        
        # 8. Net à payer
        net = brut - cnss_employe - inam - irg
        
        # 9. CNSS employeur (18%)
        cnss_employeur = base_cnss * 0.18
        
        return {
            'brut': brut,
            'cnss_employe': cnss_employe,
            'inam': inam,
            'irg': irg,
            'net': net,
            'cnss_employeur': cnss_employeur,
        }
    
    def calculer_irg_progressif(self, base):
        """Calcul IRG selon barème progressif"""
        tranches = [
            (0, 1000000, 0),
            (1000001, 3000000, 0.05),
            (3000001, 6000000, 0.10),
            (6000001, 12000000, 0.15),
            (12000001, 25000000, 0.20),
            (25000001, None, 0.25),
        ]
        
        irg = 0
        remaining = base
        
        for min_val, max_val, taux in tranches:
            if remaining <= 0:
                break
            
            if max_val:
                taxable = min(remaining, max_val - min_val + 1)
            else:
                taxable = remaining
            
            irg += taxable * taux
            remaining -= taxable
        
        return round(irg)
```

#### Jour 8 : Bulletins et PDF
**Créer `paie/pdf.py`** :
- Génération PDF avec ReportLab
- Template bulletin conforme
- Logo société
- Signature

#### Jour 9 : Livre de Paie et Déclarations
- Vue livre de paie mensuel
- Export Excel
- Génération déclarations CNSS/IRG/INAM

---

### 🟢 PHASE 4 : TESTS ET DÉBOGAGE (2 jours)

#### Jour 10 : Tests Unitaires
**Créer tests pour chaque module** :
```python
from django.test import TestCase
from employes.models import Employe

class EmployeModelTest(TestCase):
    def setUp(self):
        self.employe = Employe.objects.create(
            matricule='EMP001',
            nom='DIALLO',
            prenoms='Mamadou',
            # ...
        )
    
    def test_employe_creation(self):
        self.assertEqual(self.employe.matricule, 'EMP001')
    
    def test_age_calculation(self):
        # Test calcul âge
        pass
```

#### Jour 11 : Tests d'Intégration
- Tests des workflows complets
- Tests de calcul de paie
- Tests de validation congés
- Corrections bugs

---

### 🔵 PHASE 5 : DÉPLOIEMENT (1 jour)

#### Jour 12 : Mise en Production
1. Configuration production dans settings.py
2. Collecte des fichiers statiques
3. Migration base de données
4. Tests de charge
5. Formation utilisateurs
6. Documentation déploiement

---

## 📝 CHECKLIST PAR MODULE

### Module Employés
- [ ] views.py (ListView, DetailView, CreateView, UpdateView, DeleteView)
- [ ] urls.py
- [ ] forms.py (EmployeForm, ContratForm)
- [ ] templates/employes/list.html
- [ ] templates/employes/detail.html
- [ ] templates/employes/form.html
- [ ] templates/employes/delete.html
- [ ] Tests unitaires

### Module Temps
- [ ] views.py (Pointages, Congés)
- [ ] urls.py
- [ ] forms.py (PointageForm, CongeForm)
- [ ] templates/temps_travail/pointages_list.html
- [ ] templates/temps_travail/pointage_form.html
- [ ] templates/temps_travail/conges_list.html
- [ ] templates/temps_travail/conge_form.html
- [ ] templates/temps_travail/calendrier.html
- [ ] Tests unitaires

### Module Paie
- [ ] calcul.py (MoteurCalculPaie)
- [ ] views.py (Périodes, Bulletins, Livre)
- [ ] urls.py
- [ ] forms.py
- [ ] pdf.py (Génération bulletins)
- [ ] templates/paie/periodes_list.html
- [ ] templates/paie/bulletins_list.html
- [ ] templates/paie/bulletin_detail.html
- [ ] templates/paie/livre_paie.html
- [ ] templates/paie/declarations.html
- [ ] Tests unitaires (calculs)

---

## 💻 COMMANDES UTILES

```bash
# Créer une nouvelle app Django
python manage.py startapp nom_app

# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver

# Lancer les tests
python manage.py test

# Shell Django
python manage.py shell

# Collecter les fichiers statiques
python manage.py collectstatic

# Créer des fixtures
python manage.py dumpdata app.Model > fixtures/data.json

# Charger des fixtures
python manage.py loaddata fixtures/data.json
```

---

## 📚 RESSOURCES UTILES

### Documentation Django
- https://docs.djangoproject.com/
- https://ccbv.co.uk/ (Class-Based Views)
- https://django-crispy-forms.readthedocs.io/

### Bibliothèques
- Bootstrap 5: https://getbootstrap.com/
- Chart.js: https://www.chartjs.org/
- DataTables: https://datatables.net/
- ReportLab: https://www.reportlab.com/

### Code du Travail Guinée
- Loi L/2014/072/CNT
- CNSS: http://www.cnss-guinee.org/
- DGI: https://dgi.gov.gn/

---

## 🎯 OBJECTIFS FINAUX

1. ✅ Application complète et fonctionnelle
2. ✅ Interface moderne et responsive
3. ✅ Calculs de paie conformes
4. ✅ Workflows de validation
5. ✅ Rapports et statistiques
6. ✅ Exports Excel/PDF
7. ✅ Tests automatisés (>70% coverage)
8. ✅ Documentation complète
9. ✅ Déploiement production
10. ✅ Formation utilisateurs

---

## 📞 SUPPORT

Pour toute question :
- 📧 Email : dev@votre-entreprise.com
- 📱 Téléphone : +224 XXX XXX XXX
- 📖 Documentation : docs/

---

**🚀 Prêt à continuer le développement !**

**Prochaine étape** : Commencer par le module Employés (Jour 1)
