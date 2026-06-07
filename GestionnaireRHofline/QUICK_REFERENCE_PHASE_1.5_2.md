# PHASE 1.5 → PHASE 2 QUICK REFERENCE CARD

## 📖 READ THESE FIRST (In Order)

1. **PHASE_1.5_COMPLETION_SUMMARY.md** - Current session summary (2 min read)
2. **PHASE_1.5_TRANSITION_EXECUTIVE_SUMMARY.md** - Overall status and timeline (5 min read)
3. **PHASE_1.5_FINALIZATION.md** - Detailed Phase 1.5 checklist (5 min read)
4. **PHASE_2_ROADMAP.md** - Week-by-week Phase 2 plan (10 min read)

**Total Read Time**: ~20 minutes to understand full context

---

## 🔧 CRITICAL FILES FOR DEVELOPMENT

### Phase 1 - Foundation (Review for Patterns)

**Models**:
- `comptabilite/models.py` (52 models, all you need)

**Services** (Copy this pattern for Phase 2):
- `comptabilite/services/base_service.py` (160L - FOUNDATION)
- `comptabilite/services/rapprochement_service.py` (200L - EXAMPLE)

**Views** (Reuse these classes):
- `comptabilite/views/base/generic.py` (8 generic views, 80% reuse)
- `comptabilite/views/rapprochements/views.py` (specific implementation example)

**Forms** (Reuse base form):
- `comptabilite/forms/base.py` (base class + 7 examples)

**Mixins** (100% reusable):
- `comptabilite/mixins/views.py` (8 mixins, use in all views)

**Templates** (Reuse base):
- `comptabilite/templates/comptabilite/base.html` (master layout)
- `comptabilite/templates/comptabilite/base/list.html` (list template)
- `comptabilite/templates/comptabilite/base/form.html` (form template)

---

## ✅ PHASE 1.5 STATUS

### COMPLETE (2.5 hours done)
- [x] **Templates** (5 files created)
  - compte_list.html
  - rapprochement_list.html
  - rapprochement_detail.html
  - rapprochement_form.html
  - operation_import.html

- [x] **URLs** (Complete restructure)
  - 50+ routes organized
  - All patterns clear

### PENDING (2.5 hours remaining)
- [ ] **E2E Tests** (1.5h)
  - Write: `tests/comptabilite/test_rapprochements_workflow.py`
  - Test: Create → Import → Lettrage → Finalize
  - Command: `pytest tests/comptabilite/ -v`

- [ ] **Deployment** (1h)
  - Run: `python manage.py migrate comptabilite`
  - Check: `python manage.py check`
  - Test: `python manage.py runserver`

---

## 🚀 STARTING PHASE 2

### STEP 1: Create Models (Week 3 - Day 1-2)
**File**: `comptabilite/models.py` (add to existing)
**Code Template**: See `PHASE_2_WEEK3_IMPLEMENTATION_GUIDE.md` (600+ lines provided)

Models needed:
1. RegimeTVA (tax system)
2. TauxTVA (tax rates)
3. DeclarationTVA (declarations)
4. LigneDeclarationTVA (declaration lines)

**Command**:
```bash
python manage.py makemigrations comptabilite
python manage.py migrate
```

### STEP 2: Create Services (Week 3 - Day 3-5)
**Files**:
- `comptabilite/services/fiscalite_service.py` (NEW)
- `comptabilite/services/calcul_tva_service.py` (NEW)

**Base to Copy**:
```python
from .base_service import BaseComptaService

class FiscaliteService(BaseComptaService):
    def __init__(self, utilisateur):
        super().__init__(utilisateur)
    
    def creer_declaration_tva(self, ...):
        # Business logic here
        pass
```

**Full Code**: See `PHASE_2_WEEK3_IMPLEMENTATION_GUIDE.md`

### STEP 3: Create Tests (Week 3 - End)
**File**: `tests/comptabilite/test_fiscalite_service.py` (NEW)

**Test Pattern**:
```python
from django.test import TestCase
from comptabilite.services.fiscalite_service import FiscaliteService

class FiscaliteServiceTestCase(TestCase):
    def test_creer_declaration(self):
        # Test creation
        pass
    
    def test_calculer_montants(self):
        # Test calculations
        pass
```

### STEP 4: Create Views (Week 4)
**File**: `comptabilite/views/fiscalite/views.py` (NEW)

**Pattern**:
```python
from comptabilite.views.base.generic import ComptaListView, ComptaDetailView

class DeclarationListView(ComptaListView):
    model = DeclarationTVA
    paginate_by = 50
    # That's it! GenericListView handles the rest
```

**Note**: 80% of code reused from base generic views

### STEP 5: Create Forms (Week 4)
**File**: `comptabilite/forms/fiscalite.py` (NEW)

**Pattern**:
```python
from .base import ComptaBaseForm

class DeclarationForm(ComptaBaseForm):
    class Meta:
        model = DeclarationTVA
        fields = ['regime_tva', 'periode_debut', ...]
```

### STEP 6: Create Templates (Week 4-5)
**Files**:
- `comptabilite/templates/comptabilite/fiscalite/declaration_list.html`
- `comptabilite/templates/comptabilite/fiscalite/declaration_detail.html`
- `comptabilite/templates/comptabilite/fiscalite/declaration_form.html`
- `comptabilite/templates/comptabilite/fiscalite/calculator.html`
- `comptabilite/templates/comptabilite/fiscalite/declaration_pdf.html`

**Pattern**: Extend base templates
```html
{% extends "comptabilite/base/list.html" %}

{% block page_header %}
<h1>Déclarations TVA</h1>
{% endblock %}
```

---

## 📚 CODE REUSE CHECKLIST

### For Views
- [ ] Does it inherit from ComptaListView/ComptaDetailView?
- [ ] Does it need custom fields? (Override queryset)
- [ ] Does it need custom filters? (Add to get_queryset)
- [ ] Are permissions checked? (Mixins auto-handle)
- [ ] Is pagination needed? (Included in generic view)

### For Forms
- [ ] Does it inherit from ComptaBaseForm?
- [ ] Are field validations needed? (clean_field methods)
- [ ] Are service calls needed? (In save method)
- [ ] Is multi-tenant check needed? (Mixin handles it)

### For Templates
- [ ] Extend comptabilite/base/list.html or form.html?
- [ ] Use Bootstrap 5 classes?
- [ ] Include error display?
- [ ] Are action buttons needed?
- [ ] Is pagination included? (From parent)

### For Services
- [ ] Inherit from BaseComptaService?
- [ ] Call self.valider() for validation?
- [ ] Call self.enregistrer_audit() for logging?
- [ ] Use @transaction.atomic or self.executer_avec_transaction?
- [ ] Return (object, errors) tuple?

---

## 🔑 KEY PATTERNS TO KNOW

### Pattern 1: Service Layer
```python
# ALWAYS do this
from .base_service import BaseComptaService

class MyService(BaseComptaService):
    def creer_objet(self, ...):
        # Validate
        if not self.valider(conditions):
            return None, self.derniers_avertissements
        
        # Business logic
        obj = MyModel.objects.create(...)
        
        # Audit
        self.enregistrer_audit('CREATE', 'Module', 'Model', obj.id, {})
        
        return obj, []
```

### Pattern 2: Generic Views
```python
# ALWAYS do this
from comptabilite.views.base.generic import ComptaListView

class MyListView(ComptaListView):
    model = MyModel
    paginate_by = 50
    # DONE! Inherits pagination, filtering, auth, audit
```

### Pattern 3: Forms with Service
```python
# ALWAYS do this
from .base import ComptaBaseForm

class MyForm(ComptaBaseForm):
    def save(self, commit=True):
        obj = super().save(commit=False)
        
        # Use service for business logic
        service = MyService(self.request.user)
        obj, errors = service.valider_et_enregistrer(obj)
        
        if commit:
            obj.save()
        return obj
```

### Pattern 4: Templates
```django
{# ALWAYS do this #}
{% extends "comptabilite/base/list.html" %}

{% block page_header %}
  <h1>My Title</h1>
{% endblock %}

{% block table_content %}
  <table class="table">
    {# Your specific columns #}
  </table>
{% endblock %}
```

### Pattern 5: RBAC & Audit
```python
# ALWAYS add to views
from comptabilite.permissions.decorators import comptabilite_required
from comptabilite.mixins.views import AuditMixin

@comptabilite_required
class MyDetailView(AuditMixin, ComptaDetailView):
    model = MyModel
    # Audit automatically logs create/update
    # Permissions automatically checked
```

---

## ⚡ COMMON COMMANDS

### Development
```bash
# Run migrations
python manage.py migrate comptabilite

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Open shell
python manage.py shell
```

### Testing
```bash
# All tests
pytest tests/comptabilite/ -v

# With coverage
pytest tests/comptabilite/ --cov=comptabilite --cov-report=html

# Specific test file
pytest tests/comptabilite/test_rapprochements.py -v

# Specific test class
pytest tests/comptabilite/test_rapprochements.py::RapprochementTestCase -v

# With output
pytest -s tests/comptabilite/
```

### Database
```bash
# Show migrations
python manage.py showmigrations comptabilite

# Check for errors
python manage.py check

# Generate migration
python manage.py makemigrations comptabilite

# Migrate
python manage.py migrate comptabilite

# Rollback
python manage.py migrate comptabilite 0001
```

### Admin
```bash
# Django admin
http://localhost:8000/admin

# Create test data
python manage.py shell < scripts/create_test_data.py
```

---

## 🐛 DEBUGGING CHECKLIST

### If views not showing
- [ ] Is URL pattern correct? (Check comptabilite/urls.py)
- [ ] Is view imported? (Check views/__init__.py)
- [ ] Is model in INSTALLED_APPS? (Check settings.py)
- [ ] Is migration applied? (`python manage.py migrate`)

### If permissions denied
- [ ] Is @comptabilite_required decorator added?
- [ ] Does user have correct role? (Check auth.Group)
- [ ] Is enterprise set? (check request.user.entreprise)
- [ ] Is multi-tenant check correct? (Check EntrepriseFilterMixin)

### If form validation fails
- [ ] Check field types match model
- [ ] Check clean_field methods exist
- [ ] Check service.valider() conditions
- [ ] Check form.is_valid() in view

### If tests fail
- [ ] Is test data created? (setUp method)
- [ ] Are imports correct?
- [ ] Is database transaction rolled back? (TestCase auto-does)
- [ ] Is mock data proper type? (Decimal not float)

---

## 📞 WHEN YOU'RE STUCK

### Problem: "Template not found"
**Solution**: Check TEMPLATES setting in settings.py, verify path

### Problem: "Model not found"
**Solution**: Check models.py and migration 0002, verify field names

### Problem: "Permission denied"
**Solution**: Check user.groups, verify @comptabilite_required decorator

### Problem: "Audit trail not logging"
**Solution**: Check service.enregistrer_audit() call, verify PisteAudit model

### Problem: "Form not working"
**Solution**: Check form.errors in template, verify clean methods

### Problem: "Import error"
**Solution**: Check model imports in views.py, verify app name in imports

---

## ✨ BEST PRACTICES REMINDER

✅ **DO** inherit from base classes (BaseComptaService, ComptaListView)  
✅ **DO** use mixins for cross-cutting concerns  
✅ **DO** call self.valider() in services  
✅ **DO** log everything with audit trail  
✅ **DO** test business logic in services (not views)  
✅ **DO** extend base templates  
✅ **DO** use Bootstrap 5 classes  
✅ **DO** add error handling everywhere  

❌ **DON'T** duplicate service logic  
❌ **DON'T** put business logic in views  
❌ **DON'T** bypass RBAC checks  
❌ **DON'T** forget audit trail  
❌ **DON'T** hardcode enterprise_id  
❌ **DON'T** use float for monetary values (use Decimal)  
❌ **DON'T** ignore multi-tenancy  

---

## 🎯 SUCCESS CRITERIA - PHASE 2 WEEK 3

After following `PHASE_2_WEEK3_IMPLEMENTATION_GUIDE.md`:

- ✅ 4 new models created (RegimeTVA, TauxTVA, DeclarationTVA, LigneDeclarationTVA)
- ✅ 2 services implemented (FiscaliteService, CalculTVAService)
- ✅ Migration 0003 created and applied
- ✅ All models have Meta class with proper configuration
- ✅ All services inherit from BaseComptaService
- ✅ Unit tests written and passing
- ✅ No syntax errors
- ✅ All imports working
- ✅ Database schema correct
- ✅ Signals auto-calculate declarations

---

## 📞 SUPPORT

### Questions About Phase 1
- Check `PHASE_1_FOUNDATION_COMPLETE.md`
- Review code in `comptabilite/services/rapprochement_service.py`
- Look at examples in `comptabilite/views/rapprochements/views.py`

### Questions About Phase 1.5
- Check `PHASE_1.5_FINALIZATION.md`
- Review templates in `comptabilite/templates/`
- Check URLs in `comptabilite/urls.py`

### Questions About Phase 2
- Check `PHASE_2_WEEK3_IMPLEMENTATION_GUIDE.md`
- Copy code examples from guide
- Review RapprochementService as pattern
- Check DeclarationTVA code in guide

### For Specific Issues
1. Check the relevant .md file
2. Search code examples (provided in guides)
3. Review similar implementation (e.g., Rapprochement for Fiscalité)
4. Run tests to validate: `pytest tests/comptabilite/ -v`

---

**Last Updated**: 2025  
**Version**: 1.0  
**Status**: READY FOR PHASE 2 🚀
