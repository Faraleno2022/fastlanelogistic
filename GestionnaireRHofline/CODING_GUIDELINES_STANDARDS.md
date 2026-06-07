# 📐 GESTIONNAIRE RH - CODING GUIDELINES & STANDARDS

**Version**: 2.0  
**Effective**: 2026-01-20 onwards  
**Applies to**: All 12 modules  
**Enforcement**: Code review + Automated linting

---

## 🎯 CORE PRINCIPLES

```
✅ DRY (Don't Repeat Yourself)
   └─ Reuse patterns from Phase 1
   └─ No code duplication across modules
   └─ Extract common logic to base classes

✅ KISS (Keep It Simple Stupid)
   └─ Simple > complex
   └─ Read > re-read
   └─ Obvious intent > clever tricks

✅ SOLID Principles
   └─ Single Responsibility
   └─ Open/Closed
   └─ Liskov Substitution
   └─ Interface Segregation
   └─ Dependency Inversion

✅ Clean Code
   └─ Meaningful names
   └─ Small functions
   └─ No magic numbers
   └─ Comments explain WHY, not WHAT
```

---

## 🐍 PYTHON STYLE GUIDE

### Code Formatting
```python
# Use Black formatter (PEP 8 compliant)
# Line length: 88 characters
# Indentation: 4 spaces (NO TABS)

# Imports: grouped and sorted
from django.db import models
from django.conf import settings
from decimal import Decimal

from ..base_service import BaseComptaService
from .models import MyModel
```

### Naming Conventions
```python
# Classes: PascalCase
class MyService(BaseComptaService):
    pass

# Functions/Methods: snake_case
def calculate_total():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DECIMAL_PLACES = 2

# Private: _leading_underscore
def _internal_method():
    pass

# Django models: singular + descriptive
class Invoice(BaseModel):
    pass

# Django apps: lowercase
app_name = 'comptabilite'

# Django URL names: module-action
urlpatterns = [
    path('invoices/', views.InvoiceListView.as_view(), name='invoice-list'),
]
```

### Max Line Length & Complexity
```
Max line length: 88 characters
Max function length: 30 lines
Max cyclomatic complexity: 10
Max method parameters: 5
Max class size: 200 lines (consider extracting)
```

---

## 🏗️ ARCHITECTURE PATTERNS

### Service Layer Pattern
```python
# ALWAYS follow this pattern in services:

class MyService(BaseComptaService):
    
    def __init__(self, utilisateur: User):
        super().__init__(utilisateur)
        self.service_name = 'MyService'
    
    @transaction.atomic
    def create_object(self, param1, param2):
        """Create an object with validation and audit logging."""
        
        # 1. Validation
        conditions = {
            'param1_valid': bool(param1),
            'param2_positive': param2 > 0,
        }
        self.valider(conditions)
        
        # 2. Early exit on errors
        if self.erreurs:
            return None, self.erreurs
        
        # 3. Creation
        obj = MyModel.objects.create(
            param1=param1,
            param2=param2,
            utilisateur_creation=self.utilisateur,
        )
        
        # 4. Audit logging
        self.enregistrer_audit(
            action='CREATE',
            module='MYMODULE',
            type_objet='MyModel',
            id_objet=str(obj.id),
            details={'param1': param1}
        )
        
        # 5. Return tuple (object, errors)
        return obj, []
```

### View Layer Pattern
```python
# ALWAYS inherit from generic views:

from ..views.generic import BaseListView, BaseDetailView
from ..mixins.views import ComptabiliteAccessMixin
from ..permissions.decorators import require_perms

@method_decorator(login_required, name='dispatch')
@method_decorator(require_perms('comptabilite.view_mymodel'), name='dispatch')
class MyModelListView(ComptabiliteAccessMixin, BaseListView):
    """List all MyModel objects."""
    
    model = MyModel
    paginate_by = 25
    
    def get_queryset(self):
        # ALWAYS filter by user's entreprise
        return super().get_queryset().filter(
            entreprise=self.request.user.entreprise
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = MyService(self.request.user)
        return context
```

### Form Pattern
```python
# ALWAYS inherit from FormBase:

from ..forms.base import FormBase

class MyModelForm(FormBase):
    """Form for MyModel with validation."""
    
    class Meta:
        model = MyModel
        fields = ['field1', 'field2']
        widgets = {
            'field1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter field1'
            }),
        }
    
    def clean(self):
        """Add custom validation."""
        cleaned_data = super().clean()
        
        field1 = cleaned_data.get('field1')
        if field1 and len(field1) < 3:
            self.add_error('field1', 'Minimum 3 characters')
        
        return cleaned_data
```

---

## 💾 DATABASE CONVENTIONS

### Model Fields
```python
# ALWAYS follow these rules:

class MyModel(BaseModel):
    
    # UUID Primary Key (REQUIRED)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Business fields
    code = models.CharField(max_length=20)  # Business identifiers
    nom = models.CharField(max_length=100)  # Human-readable names
    
    # Relationships (ALWAYS use ForeignKey with on_delete)
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='mymodels'  # Plural
    )
    
    # Financial fields (ALWAYS use Decimal)
    montant = models.DecimalField(
        max_digits=15,  # Total digits
        decimal_places=2  # 2 decimals for money
    )
    
    # Dates (ALWAYS use DateField for dates, DateTimeField for timestamps)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    
    # Status/Flags (ALWAYS name clearly)
    actif = models.BooleanField(default=True)
    
    # Audit fields (REQUIRED on all models)
    utilisateur_creation = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='mymodels_created'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    utilisateur_modification = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='mymodels_modified'
    )
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comptabilite_mymodel'
        verbose_name = 'My Model'
        verbose_name_plural = 'My Models'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['entreprise', 'actif']),
            models.Index(fields=['code']),
        ]
        unique_together = ['entreprise', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.nom}"
```

### Migrations
```
# Naming: 000X_{descriptive_name}.py
# Example: 0003_fiscalite_models.py

# NEVER edit existing migrations
# ALWAYS create new migrations for changes
# ALWAYS test migrations locally first
```

---

## ✅ TESTING GUIDELINES

### Test Structure
```python
from django.test import TestCase
from django.contrib.auth.models import User

class MyModelTestCase(TestCase):
    """Tests for MyModel."""
    
    @classmethod
    def setUpTestData(cls):
        """Setup test fixtures ONCE (faster)."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cls.entreprise = Entreprise.objects.create(
            nom='Test',
            siret='00000000000000'
        )
    
    def setUp(self):
        """Setup for each test (if needed)."""
        pass
    
    def test_create_object_valid(self):
        """Test creating object with valid data."""
        service = MyService(self.user)
        obj, errors = service.create_object(
            param1='test',
            param2=100
        )
        
        self.assertIsNotNone(obj)
        self.assertFalse(errors)
        self.assertEqual(obj.param1, 'test')
    
    def test_create_object_invalid_param(self):
        """Test creating object with invalid data."""
        service = MyService(self.user)
        obj, errors = service.create_object(
            param1=None,
            param2=100
        )
        
        self.assertIsNone(obj)
        self.assertTrue(errors)
```

### Coverage Requirements
```
Minimum: 80% code coverage
- Models: 100% (automatic from services)
- Services: 90%+
- Views: 85%+
- Forms: 85%+
- Utils: 90%+

Check with: pytest --cov=comptabilite --cov-report=term
```

---

## 🔐 SECURITY STANDARDS

### Authentication & Authorization
```python
# ALWAYS use decorators for permission checks:

from ..permissions.decorators import require_perms

@require_perms('comptabilite.view_mymodel')
def my_view(request):
    pass

# ALWAYS verify entreprise access:

def get_queryset(self):
    return MyModel.objects.filter(
        entreprise=self.request.user.entreprise
    )
```

### Data Validation
```python
# ALWAYS validate user input:

def my_view(request):
    # Method check
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    # CSRF token (automatic in Django)
    # Input validation
    form = MyForm(request.POST)
    if not form.is_valid():
        return render(request, 'form.html', {'form': form})
    
    # Business validation
    service = MyService(request.user)
    obj, errors = service.create(...)
```

### SQL Injection Prevention
```python
# CORRECT: Use ORM (ALWAYS)
MyModel.objects.filter(code=user_input)

# WRONG: Never concatenate SQL
MyModel.objects.raw(f"SELECT * FROM table WHERE code='{user_input}'")

# Use Q objects for complex queries:
from django.db.models import Q

MyModel.objects.filter(
    Q(code=param1) | Q(nom=param2)
)
```

### Sensitive Data
```python
# NEVER log passwords or tokens
# NEVER expose stack traces to users
# NEVER hardcode API keys (use settings)
# ALWAYS hash passwords (Django does automatically)
# ALWAYS use HTTPS in production
```

---

## 📝 DOCUMENTATION STANDARDS

### Code Comments
```python
# Use comments to explain WHY, not WHAT

# WRONG:
x = 5  # Set x to 5

# CORRECT:
retry_count = 5  # Maximum retries for API calls

# Complex logic explanation:
# Calculate tax amount considering the special case where
# if revenue is below threshold, no tax is due
tax = revenue * rate if revenue > threshold else 0
```

### Docstrings
```python
# Use Google-style docstrings:

def my_function(param1: str, param2: int) -> Tuple[str, List]:
    """
    Short description.
    
    Longer description explaining what the function does,
    any important details, and edge cases.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        (result: str, errors: List[str])
    
    Raises:
        ValueError: If param2 is negative
    
    Example:
        >>> my_function('test', 5)
        ('result', [])
    """
    pass
```

### README Files
```markdown
# Module Name

## Overview
Brief description of what the module does.

## Quick Start
Steps to get started with the module.

## API Reference
Public functions and classes.

## Examples
Code examples for common tasks.

## Testing
How to run tests.

## Contributing
Guidelines for contributing.
```

---

## 🎨 TEMPLATE CONVENTIONS

### Template Inheritance
```html
<!-- Always extend from base_module.html -->
{% extends "comptabilite/base_module.html" %}

{% block title %}My Page{% endblock %}

{% block breadcrumb %}
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
            <li><a href="{% url 'home' %}">Home</a></li>
            <li class="active">Current Page</li>
        </ol>
    </nav>
{% endblock %}

{% block content %}
    <!-- Your content here -->
{% endblock %}

{% block scripts %}
    <script src="{% static 'mymodule/js/script.js' %}"></script>
{% endblock %}
```

### Bootstrap Classes
```html
<!-- Use Bootstrap 5.3 classes -->
<button class="btn btn-primary">Primary</button>
<button class="btn btn-outline-secondary">Secondary</button>
<div class="alert alert-danger">Error message</div>
<table class="table table-hover">
    <thead class="table-light">
        <tr>
            <th>Header</th>
        </tr>
    </thead>
</table>

<!-- Responsive design -->
<div class="row">
    <div class="col-md-8">Main content</div>
    <div class="col-md-4">Sidebar</div>
</div>
```

### Accessibility
```html
<!-- ALWAYS include alt text for images -->
<img src="logo.png" alt="Company logo">

<!-- Use semantic HTML -->
<button>Click me</button>  <!-- NOT <div onclick> -->

<!-- Label form inputs -->
<label for="email">Email:</label>
<input id="email" type="email">

<!-- ARIA attributes for complex components -->
<div role="progressbar" aria-valuenow="70" aria-valuemin="0" aria-valuemax="100">
</div>
```

---

## 🚀 PERFORMANCE OPTIMIZATION

### Database Optimization
```python
# Use select_related() for ForeignKey:
MyModel.objects.select_related('entreprise')

# Use prefetch_related() for M2M and reverse FK:
MyModel.objects.prefetch_related('related_items')

# Use only() to reduce fields:
MyModel.objects.only('id', 'code', 'nom')

# Avoid N+1 queries:
# WRONG:
for obj in MyModel.objects.all():
    print(obj.entreprise.nom)  # Query for EACH object

# CORRECT:
for obj in MyModel.objects.select_related('entreprise'):
    print(obj.entreprise.nom)  # Single query
```

### Caching
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def expensive_view(request):
    pass

# Or in code:
from django.core.cache import cache

cached_data = cache.get('key')
if cached_data is None:
    cached_data = expensive_operation()
    cache.set('key', cached_data, 60 * 5)
```

### API Response Optimization
```python
# Return only necessary fields
class MySerializer:
    fields = ['id', 'code', 'nom']

# Use pagination
paginator = Paginator(queryset, 25)

# Compress responses (automatic with middleware)
```

---

## 🔄 GIT WORKFLOW

### Commit Messages
```
Format: <type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore

Examples:
feat(fiscalite): add TVA calculation service
fix(paie): correct overtime calculation
docs(README): update setup instructions
test(audit): add conformity check tests
```

### Branch Naming
```
feature/module-name-feature
bugfix/issue-name
hotfix/critical-issue
```

### Code Review Checklist
```
- [ ] Tests pass (100%)
- [ ] No duplicate code
- [ ] Follows naming conventions
- [ ] Docstrings present
- [ ] No console errors
- [ ] Security check passed
- [ ] Performance metrics OK
- [ ] Documentation updated
```

---

## 📋 QUALITY GATES

### Before Merging to Main
```
✅ All tests pass
✅ Code coverage ≥ 80%
✅ No critical security issues
✅ Code review approved
✅ Linting passes (Black, Flake8)
✅ Type checking passes (mypy)
✅ Performance benchmarks OK
✅ Documentation complete
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Add hooks
black .
flake8 .
mypy .
pytest --cov
```

---

## 📚 RESOURCES

```
Documentation:
├─ Django docs: https://docs.djangoproject.com/
├─ Python PEP 8: https://pep8.org/
├─ Google Python Style: https://google.github.io/styleguide/pyguide.html
└─ Project Wiki: /docs/

Tools:
├─ Black formatter: black . --line-length 88
├─ Flake8 linter: flake8 .
├─ Pytest: pytest --cov=comptabilite
├─ MyPy type checking: mypy comptabilite/
└─ Coverage report: coverage report
```

---

Generated: 2026-01-20 | Coding Standards v2.0 ✅
