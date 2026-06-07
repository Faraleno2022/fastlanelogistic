# Exemples d'Utilisation de la Réauthentification

## Comment Appliquer la Réauthentification aux Vues

### Exemple 1: Vue Simple

```python
from django.contrib.auth.decorators import login_required
from core.decorators import reauth_required

@login_required
@reauth_required
def vue_sensible(request):
    """Cette vue nécessitera une réauthentification si activée pour l'utilisateur"""
    # Votre code ici
    return render(request, 'mon_template.html')
```

### Exemple 2: Vue avec Plusieurs Décorateurs

```python
from django.contrib.auth.decorators import login_required
from core.decorators import reauth_required, entreprise_active_required, log_access

@login_required
@entreprise_active_required  # Vérifie que l'entreprise est active
@reauth_required            # Demande réauthentification si nécessaire
@log_access("Consultation données sensibles")  # Log l'accès
def donnees_sensibles(request):
    # Code de la vue
    return render(request, 'sensible.html')
```

### Exemple 3: Appliquer à Toutes les Vues d'un Module

Pour appliquer la réauthentification à toutes les vues de paie par exemple:

```python
# Dans paie/views.py
from django.contrib.auth.decorators import login_required
from core.decorators import reauth_required

@login_required
@reauth_required
def liste_bulletins(request):
    # Code...
    pass

@login_required
@reauth_required
def creer_bulletin(request):
    # Code...
    pass

@login_required
@reauth_required
def modifier_bulletin(request, pk):
    # Code...
    pass
```

### Exemple 4: Vue Basée sur les Classes

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from core.decorators import reauth_required

@method_decorator(reauth_required, name='dispatch')
class EmployeListView(LoginRequiredMixin, ListView):
    model = Employe
    template_name = 'employes/liste.html'
```

## Modules Recommandés pour la Réauthentification

### 1. Module Paie (Hautement Sensible)
Toutes les vues de paie devraient avoir `@reauth_required`:
- Création/modification de bulletins
- Consultation des salaires
- Génération de rapports de paie

### 2. Module Employés (Données Personnelles)
- Modification des informations personnelles
- Consultation des dossiers complets
- Gestion des documents

### 3. Module Paramètres
- Modification des paramètres système
- Gestion des utilisateurs
- Configuration de l'entreprise

### 4. Module Rapports
- Rapports financiers
- Exports de données
- Statistiques sensibles

## Configuration par Utilisateur

### Activer pour un Utilisateur Spécifique

```python
# Dans la console Django ou un script
from core.models import Utilisateur

user = Utilisateur.objects.get(username='comptable1')
user.require_reauth = True
user.save()
```

### Activer pour Tous les Utilisateurs d'un Profil

```python
from core.models import Utilisateur, ProfilUtilisateur

# Activer pour tous les comptables
profil_comptable = ProfilUtilisateur.objects.get(nom_profil='Comptable')
Utilisateur.objects.filter(profil=profil_comptable).update(require_reauth=True)
```

### Activer pour Tous les Non-Administrateurs

```python
from core.models import Utilisateur

Utilisateur.objects.filter(
    est_admin_entreprise=False,
    is_superuser=False
).update(require_reauth=True)
```

## Personnalisation du Délai de Réauthentification

Par défaut, la réauthentification est valide pendant 5 minutes. Pour modifier ce délai:

```python
# Dans core/decorators.py, ligne ~278
# Modifier:
if time_since_reauth < timedelta(minutes=5):

# Par exemple, pour 10 minutes:
if time_since_reauth < timedelta(minutes=10):

# Ou pour 30 secondes (très strict):
if time_since_reauth < timedelta(seconds=30):
```

## Tester la Réauthentification

### Test Manuel

1. Créer un utilisateur avec `require_reauth=True`
2. Se connecter avec cet utilisateur
3. Accéder à une vue protégée par `@reauth_required`
4. Vérifier la redirection vers `/reauth/`
5. Entrer le mot de passe
6. Vérifier l'accès à la vue

### Test Automatisé

```python
# Dans tests.py
from django.test import TestCase, Client
from django.urls import reverse
from core.models import Utilisateur, Entreprise

class ReauthTestCase(TestCase):
    def setUp(self):
        # Créer une entreprise
        self.entreprise = Entreprise.objects.create(
            nom_entreprise="Test Corp",
            slug="test-corp",
            email="test@test.com"
        )
        
        # Créer un utilisateur avec réauth activée
        self.user = Utilisateur.objects.create_user(
            username='testuser',
            password='testpass123',
            entreprise=self.entreprise,
            require_reauth=True
        )
        
        self.client = Client()
    
    def test_reauth_required(self):
        # Se connecter
        self.client.login(username='testuser', password='testpass123')
        
        # Accéder à une vue protégée
        response = self.client.get(reverse('paie:liste_bulletins'))
        
        # Devrait rediriger vers reauth
        self.assertRedirects(response, reverse('core:reauth'))
    
    def test_reauth_success(self):
        # Se connecter
        self.client.login(username='testuser', password='testpass123')
        
        # Poster le mot de passe sur la page de réauth
        response = self.client.post(
            reverse('core:reauth'),
            {'password': 'testpass123'}
        )
        
        # Devrait rediriger vers la page demandée
        self.assertEqual(response.status_code, 302)
```

## Bonnes Pratiques

### 1. Appliquer Sélectivement
Ne pas appliquer `@reauth_required` à toutes les vues, seulement aux vues sensibles:
- ✅ Gestion de paie
- ✅ Données personnelles
- ✅ Paramètres système
- ❌ Dashboard général
- ❌ Listes simples
- ❌ Pages d'information

### 2. Combiner avec d'Autres Sécurités
```python
@login_required                    # Authentification de base
@entreprise_active_required        # Entreprise valide
@permission_required('paie.view')  # Permission spécifique
@reauth_required                   # Réauthentification
@log_access("Consultation paie")   # Logging
def vue_ultra_securisee(request):
    pass
```

### 3. Informer les Utilisateurs
Ajouter une note dans l'interface pour les utilisateurs avec réauth activée:

```html
{% if user.require_reauth %}
<div class="alert alert-info">
    <i class="bi bi-shield-check"></i>
    Pour votre sécurité, vous devrez confirmer votre mot de passe 
    avant d'accéder à certaines sections.
</div>
{% endif %}
```

### 4. Logs et Monitoring
Toutes les réauthentifications sont automatiquement loggées dans `LogActivite`.
Surveiller les échecs répétés de réauthentification.

## Désactiver Temporairement

Pour désactiver temporairement la réauthentification (par exemple, pour maintenance):

```python
# Dans settings.py
REAUTH_ENABLED = False

# Puis dans le décorateur (core/decorators.py)
from django.conf import settings

def reauth_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not getattr(settings, 'REAUTH_ENABLED', True):
            return view_func(request, *args, **kwargs)
        
        # Reste du code...
```

## Support Multi-Langue

Pour internationaliser les messages de réauthentification:

```python
from django.utils.translation import gettext as _

messages.warning(request, _("Veuillez vous réauthentifier pour accéder à cette section."))
```

## Questions Fréquentes

**Q: La réauthentification s'applique-t-elle aux API REST?**
R: Oui, mais vous devrez adapter le décorateur pour les vues DRF.

**Q: Que se passe-t-il si l'utilisateur entre un mauvais mot de passe?**
R: Un message d'erreur s'affiche et il peut réessayer. Après plusieurs échecs, Axes peut bloquer le compte.

**Q: La réauthentification persiste-t-elle entre les sessions?**
R: Non, elle est réinitialisée à chaque nouvelle connexion.

**Q: Peut-on avoir différents délais pour différents utilisateurs?**
R: Actuellement non, mais vous pouvez ajouter un champ `reauth_timeout` au modèle Utilisateur.
