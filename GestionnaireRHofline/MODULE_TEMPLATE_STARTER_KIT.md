# 🎨 MODULE TEMPLATE STARTER KIT

**Purpose**: Template standardisé pour créer rapidement les 12 modules
**Used by**: Chaque nouveau module suit ce pattern
**Gain**: 30-40 heures par module (70% réutilisation)

---

## 📦 STRUCTURE TYPE D'UN MODULE

```
comptabilite/{module_name}/
├── __init__.py
├── apps.py                    (Django app config)
├── models.py                  (10-20 modèles)
├── services.py                (3-5 services)
├── views.py                   (5-8 vues)
├── forms.py                   (3-6 formulaires)
├── urls.py                    (routes)
├── admin.py                   (admin interface)
├── signals.py                 (Django signals)
├── tests.py                   (test suite)
├── migrations/
│   ├── __init__.py
│   └── 000X_initial.py
├── templates/{module_name}/
│   ├── base.html              (inherited)
│   ├── list.html              (CRUD list)
│   ├── detail.html            (object detail)
│   ├── form.html              (create/edit)
│   ├── delete.html            (delete confirm)
│   ├── filter_sidebar.html    (reusable)
│   └── ...
└── static/{module_name}/
    ├── css/
    │   └── module.css
    ├── js/
    │   └── module.js
    └── images/

Total: ~900 lines per module (30-40 hours)
```

---

## 📄 FICHIER models.py - TEMPLATE

```python
"""
Module {name} - Modèles
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

# Import des patterns Phase 1
from ..models import (
    PlanComptable, ExerciceComptable, 
    EcritureComptable, Entreprise
)


class BaseModel(models.Model):
    """Modèle parent pour tous les modèles du module"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    utilisateur_creation = models.ForeignKey(
        'auth.User', on_delete=models.PROTECT,
        related_name='{module_name}_created'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    utilisateur_modification = models.ForeignKey(
        'auth.User', on_delete=models.PROTECT,
        related_name='{module_name}_modified'
    )
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Model1(BaseModel):
    """Première entité du module"""
    
    # Business fields
    code = models.CharField(max_length=20)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # FK & Relations
    entreprise = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE,
        related_name='{module_plural}'
    )
    
    # Status & Dates
    actif = models.BooleanField(default=True)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = '{module_underscore}_model1'
        verbose_name = 'Model 1'
        verbose_name_plural = 'Models 1'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['entreprise', 'actif']),
        ]
        unique_together = ['entreprise', 'code']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"
    
    def save(self, *args, **kwargs):
        """Override save pour custom logic si needed"""
        super().save(*args, **kwargs)


# ... 10-20 modèles suivant le même pattern
```

---

## 📄 FICHIER services.py - TEMPLATE

```python
"""
Module {name} - Services métier
"""
from django.db import transaction
from django.contrib.auth.models import User
from decimal import Decimal

from ..services.base_service import BaseComptaService
from .models import Model1, Model2


class {ModuleCapitalCase}Service(BaseComptaService):
    """
    Service métier pour le module {name}
    
    Patterns:
    - Héritage: BaseComptaService
    - Validation: self.valider(conditions)
    - Audit: self.enregistrer_audit()
    - Transaction: @transaction.atomic
    """
    
    def __init__(self, utilisateur: User):
        super().__init__(utilisateur)
        self.service_name = '{ModuleCapitalCase}Service'
    
    @transaction.atomic
    def creer_entite(self, entreprise, code, nom, **kwargs):
        """
        Crée une nouvelle entité
        
        Args:
            entreprise: L'entreprise
            code: Code unique
            nom: Nom de l'entité
        
        Returns:
            (Model1, errors_list)
        """
        try:
            # Validation
            conditions = {
                'entreprise_exists': bool(entreprise),
                'code_unique': not Model1.objects.filter(
                    entreprise=entreprise, code=code
                ).exists(),
                'code_valid': len(code) > 0,
                'nom_valid': len(nom) > 0,
            }
            
            self.valider(conditions)
            
            if self.erreurs:
                return None, self.erreurs
            
            # Création
            entite = Model1.objects.create(
                entreprise=entreprise,
                code=code,
                nom=nom,
                utilisateur_creation=self.utilisateur,
                utilisateur_modification=self.utilisateur,
                **kwargs
            )
            
            # Audit
            self.enregistrer_audit(
                action='CREATE',
                module='{MODULE_NAME}',
                type_objet='Model1',
                id_objet=str(entite.id),
                details={'code': code, 'nom': nom}
            )
            
            return entite, []
            
        except Exception as e:
            self.avertissement(f"Erreur création: {str(e)}")
            return None, self.erreurs
    
    def lister_entites(self, entreprise, actif=True):
        """Liste les entités"""
        return Model1.objects.filter(
            entreprise=entreprise,
            actif=actif
        ).order_by('-date_creation')


# Service(s) additionnels pour calculs/traitements spécifiques
class {ModuleCapitalCase}CalculService(BaseComptaService):
    """Services de calcul/traitement"""
    
    def __init__(self, utilisateur: User):
        super().__init__(utilisateur)
```

---

## 📄 FICHIER views.py - TEMPLATE

```python
"""
Module {name} - Vues
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Imports Phase 1 patterns
from ..views.generic import BaseListView, BaseDetailView
from ..mixins.views import ComptabiliteAccessMixin
from ..permissions.decorators import require_perms

from .models import Model1
from .forms import Model1Form
from .services import {ModuleCapitalCase}Service


@method_decorator(login_required, name='dispatch')
@method_decorator(require_perms('comptabilite.view_{module_underscore}'), name='dispatch')
class Model1ListView(ComptabiliteAccessMixin, BaseListView):
    """Liste des entités"""
    model = Model1
    paginate_by = 25
    template_name = '{module_name}/model1_list.html'
    
    def get_queryset(self):
        return super().get_queryset().filter(
            entreprise=self.request.user.entreprise
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Model 1'
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(require_perms('comptabilite.view_{module_underscore}'), name='dispatch')
class Model1DetailView(ComptabiliteAccessMixin, BaseDetailView):
    """Détail d'une entité"""
    model = Model1
    template_name = '{module_name}/model1_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = {ModuleCapitalCase}Service(self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(require_perms('comptabilite.add_{module_underscore}'), name='dispatch')
class Model1CreateView(ComptabiliteAccessMixin, CreateView):
    """Créer une entité"""
    model = Model1
    form_class = Model1Form
    template_name = '{module_name}/model1_form.html'
    
    def form_valid(self, form):
        service = {ModuleCapitalCase}Service(self.request.user)
        
        obj, errors = service.creer_entite(
            entreprise=self.request.user.entreprise,
            **form.cleaned_data
        )
        
        if errors:
            # Handle errors
            form.add_error(None, str(errors))
            return self.form_invalid(form)
        
        return super().form_valid(form)


# ... UpdateView, DeleteView, etc.
```

---

## 📄 FICHIER forms.py - TEMPLATE

```python
"""
Module {name} - Formulaires
"""
from django import forms
from django.forms import inlineformset_factory

from .models import Model1, Model2
from ..forms.base import FormBase


class Model1Form(FormBase):
    """Formulaire pour Model1"""
    
    class Meta:
        model = Model1
        fields = [
            'code', 'nom', 'description',
            'date_debut', 'date_fin',
            'actif'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code unique'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        
        # Custom validation
        if code and len(code) < 3:
            self.add_error('code', 'Code doit avoir 3+ caractères')
        
        return cleaned_data


# Formset pour relations inline
Model2FormSet = inlineformset_factory(
    Model1, Model2,
    form=Model1Form,
    extra=1,
    can_delete=True
)
```

---

## 📄 FICHIER urls.py - TEMPLATE

```python
"""
Module {name} - URLs
"""
from django.urls import path
from . import views

app_name = '{module_name}'

urlpatterns = [
    # Model1 CRUD
    path(
        'model1/',
        views.Model1ListView.as_view(),
        name='model1-list'
    ),
    path(
        'model1/<uuid:pk>/',
        views.Model1DetailView.as_view(),
        name='model1-detail'
    ),
    path(
        'model1/new/',
        views.Model1CreateView.as_view(),
        name='model1-create'
    ),
    path(
        'model1/<uuid:pk>/edit/',
        views.Model1UpdateView.as_view(),
        name='model1-update'
    ),
    path(
        'model1/<uuid:pk>/delete/',
        views.Model1DeleteView.as_view(),
        name='model1-delete'
    ),
    
    # Model2 nested under Model1
    path(
        'model1/<uuid:model1_pk>/model2/',
        views.Model2ListView.as_view(),
        name='model2-list'
    ),
]
```

---

## 📄 FICHIER tests.py - TEMPLATE

```python
"""
Module {name} - Tests
"""
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date

from .models import Model1, Model2
from .services import {ModuleCapitalCase}Service
from core.models import Entreprise


class Model1TestCase(TestCase):
    """Tests du modèle Model1"""
    
    @classmethod
    def setUpTestData(cls):
        """Données initiales"""
        cls.utilisateur = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        cls.entreprise = Entreprise.objects.create(
            nom='Test Enterprise',
            siret='00000000000000'
        )
    
    def test_create_model1(self):
        """Test création Model1"""
        service = {ModuleCapitalCase}Service(self.utilisateur)
        
        model1, errors = service.creer_entite(
            entreprise=self.entreprise,
            code='TEST001',
            nom='Test Entity'
        )
        
        self.assertIsNotNone(model1)
        self.assertEqual(model1.code, 'TEST001')
        self.assertFalse(errors)


class {ModuleCapitalCase}ServiceTestCase(TestCase):
    """Tests du service"""
    
    def test_service_methods(self):
        """Test méthodes du service"""
        # Setup
        # Test
        # Assert
        pass
```

---

## 🎨 FICHIER template base.html - TEMPLATE

```html
{% extends "comptabilite/base_module.html" %}
{% load custom_filters %}

{% block title %}{Module Name}{% endblock %}

{% block breadcrumb %}
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="{% url 'dashboard' %}">Home</a></li>
            <li class="breadcrumb-item"><a href="{% url 'comptabilite:index' %}">Comptabilité</a></li>
            <li class="breadcrumb-item active">{Module Name}</li>
        </ol>
    </nav>
{% endblock %}

{% block content %}
    <div class="container-fluid">
        <div class="row">
            <!-- Main content -->
            <div class="col-md-9">
                {% block module_content %}
                {% endblock %}
            </div>
            
            <!-- Sidebar -->
            <div class="col-md-3">
                {% include "{module_name}/filter_sidebar.html" %}
            </div>
        </div>
    </div>
{% endblock %}

{% block scripts %}
    <script src="{% static '{module_name}/js/module.js' %}"></script>
{% endblock %}
```

---

## ✅ CHECKLIST CRÉATION NOUVEAU MODULE

```
PRÉ-DÉVELOPPEMENT
☐ Modèle métier documenté
☐ Cas d'usage définis
☐ Dépendances vers autres modules identifiées
☐ Migrations DB planifiées

DEVELOPMENT
☐ apps.py créé
☐ models.py (10-20 modèles)
☐ services.py (3-5 services)
☐ views.py (5-8 vues CBV)
☐ forms.py (3-6 formulaires)
☐ urls.py (routes)
☐ admin.py (admin interface)
☐ signals.py (Django signals)

TEMPLATES
☐ base.html (extends base_module.html)
☐ list.html (CRUD list)
☐ detail.html (object detail)
☐ form.html (create/edit)
☐ delete.html (delete confirm)
☐ filter_sidebar.html (reusable filter)

TESTS
☐ TestCase classes
☐ Service tests
☐ View tests
☐ Form validation tests
☐ 80%+ coverage

INTÉGRATION
☐ URLs inclues dans comptabilite/urls.py
☐ Permissions créées
☐ Groupes assignés
☐ Settings configuration
☐ Migration exécutée

VALIDATION
☐ Tous tests passent
☐ No syntax errors
☐ Code review approuvé
☐ Security scan OK
☐ Performance OK
```

---

## 📊 STATISTIQUES PAR MODULE

```
Component        | Lines | Time | Reuse%
───────────────────────────────────────
models.py        | 300   | 6h   | 80%
services.py      | 250   | 6h   | 90%
views.py         | 200   | 8h   | 85%
forms.py         | 150   | 4h   | 80%
urls.py          | 50    | 1h   | 95%
admin.py         | 100   | 2h   | 85%
tests.py         | 250   | 6h   | 70%
templates/       | 800   | 8h   | 70%
───────────────────────────────────────
TOTAL            | 2,100 | 40h  | 80%
```

---

## 🎯 EXEMPLE: MODULE PAIE

Utilisant ce template:
```
PAIE Module (Phase 3):
├─ Models: Paie, LignePayroll, RubriquePaie, CumulPaie
├─ Services: MoteurCalculPaie, GenerateurBulletin, ExportDonnees
├─ Views: Liste bulletins, détail, génération, export
├─ Forms: BulletinForm, RubriquePaieForm
├─ Templates: liste, détail, form, export preview

Effort: 40 hours (vs 100 without patterns)
Timeline: 1 week
```

---

Generated: 2026-01-20 | Module Template Complete ✅
