# Guide d'intégration - Phase 1 Foundation

## Étape 1: Intégrer les URLs

Modifier `comptabilite/urls.py` pour ajouter les routes Rapprochements bancaires:

```python
from django.urls import path, include
from . import views

app_name = 'comptabilite'

urlpatterns = [
    # ... URLs existantes ...
    
    # Rapprochements bancaires (Phase 1 Foundation)
    path('rapprochements/', include('comptabilite.views.rapprochements.urls')),
    
    # ... autres modules à venir ...
]
```

## Étape 2: Créer les fichiers __init__.py manquants

```bash
# Views
touch comptabilite/views/__init__.py
touch comptabilite/views/base/__init__.py
touch comptabilite/views/rapprochements/__init__.py

# Forms
touch comptabilite/forms/__init__.py

# Mixins
touch comptabilite/mixins/__init__.py

# Permissions
touch comptabilite/permissions/__init__.py

# Utils
touch comptabilite/utils/__init__.py

# Tests
touch comptabilite/tests/__init__.py
```

## Étape 3: Importer les services dans forms

Modifier `comptabilite/forms/base.py`:

```python
# Ajouter dans __init__ de ComptaBaseForm
from comptabilite.services.rapprochement import RapprochementService
```

## Étape 4: Importer les views dans rapprochements/views.py

Corriger les imports:

```python
# Remplacer:
from ..models import (...)
from .forms.rapprochement import (...)

# Par:
from comptabilite.models import (...)
from comptabilite.forms.base import (...)
```

## Étape 5: Créer les fichiers forms spécifiques

Créer `comptabilite/forms/rapprochement.py`:

```python
# Utiliser les formulaires de base.py
from .base import (
    CompteBancaireForm,
    RapprochementBancaireForm,
    OperationImportForm,
    EcartBancaireForm,
    BulkLettrageForm
)
```

## Étape 6: Vérifier les imports

Faire les vérifications suivantes dans chaque module:

### views/base/generic.py
```python
# Vérifier les imports
from comptabilite.mixins.views import (...)
```

### views/rapprochements/views.py
```python
# Vérifier les imports
from comptabilite.models import (...)
from comptabilite.forms.base import (...)
from comptabilite.views.base.generic import (...)
```

## Étape 7: Créer les __init__ pour les views

Créer `comptabilite/views/base/__init__.py`:
```python
from .generic import (
    ComptaListView,
    ComptaDetailView,
    ComptaCreateView,
    ComptaUpdateView,
    ComptaDeleteView,
    ComptaDashboardView,
    ComptaExportView,
    ComptaAjaxView,
)
```

Créer `comptabilite/views/rapprochements/__init__.py`:
```python
from .views import (
    CompteBancaireListView,
    CompteBancaireDetailView,
    CompteBancaireCreateView,
    CompteBancaireUpdateView,
    CompteBancaireDeleteView,
    RapprochementListView,
    RapprochementDetailView,
    RapprochementCreateView,
    RapprochementUpdateView,
    RapprochementDeleteView,
    OperationImportView,
    LettrageView,
    LettrageAnnulationView,
    RapprochementFinalisationView,
)
```

## Étape 8: Tests

Exécuter les tests:

```bash
python manage.py test comptabilite.tests
```

## Étape 9: Vérifier la migration

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Étape 10: Vérifier les URLs

```bash
python manage.py show_urls | grep comptabilite
```

## Étape 11: Démarrer le serveur

```bash
python manage.py runserver
```

## Étape 12: Tester les vues

Accéder à:
- http://localhost:8000/comptabilite/rapprochements/
- http://localhost:8000/comptabilite/rapprochements/comptes/

---

## Checklist d'intégration

- [ ] URLs intégrées dans comptabilite/urls.py
- [ ] Fichiers __init__.py créés
- [ ] Imports corrigés dans tous les modules
- [ ] Migrations appliquées
- [ ] Tests passent
- [ ] Serveur démarre sans erreur
- [ ] URLs accessibles
- [ ] Admin fonctionne

---

## Dépannage

### ImportError: No module named 'comptabilite.views.base.generic'

→ Créer `comptabilite/views/base/__init__.py`

### AttributeError: 'NoneType' object has no attribute 'entreprise'

→ Ajouter user au formulaire:
```python
form = CompteBancaireForm(user=request.user)
```

### PermissionDenied: Accès refusé au module de comptabilité

→ Vérifier que l'utilisateur a la permission 'comptabilite.view_comptabilite'

---

## Prochaines étapes

1. Créer les templates spécifiques pour rapprochements
2. Tester le workflow complet
3. Passer à Fiscalité (Phase 1)
4. Puis Audit (Phase 1)

