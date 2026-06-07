# Fonctionnalités Multi-Entreprise et Réauthentification

## Vue d'ensemble

Ce système permet à plusieurs entreprises de créer et gérer leurs propres comptes dans l'application Gestionnaire RH, avec une fonctionnalité de réauthentification pour renforcer la sécurité.

## Fonctionnalités Principales

### 1. Multi-Entreprise

#### Inscription d'une Entreprise
- **URL**: `/register-entreprise/`
- Chaque entreprise peut créer son propre compte
- Lors de l'inscription, un administrateur d'entreprise est automatiquement créé
- Champs requis:
  - Nom de l'entreprise
  - Email de contact
  - Informations de l'administrateur (nom, prénom, username, email, mot de passe)
  - Plan d'abonnement (gratuit, basique, premium, entreprise)

#### Plans d'Abonnement
- **Gratuit**: 5 utilisateurs maximum
- **Basique**: Personnalisable
- **Premium**: Personnalisable
- **Entreprise**: Personnalisable

#### Isolation des Données
- Chaque entreprise a ses propres utilisateurs
- Les données sont isolées par entreprise
- Un utilisateur ne peut appartenir qu'à une seule entreprise

### 2. Réauthentification

#### Fonctionnement
- Les administrateurs peuvent activer la réauthentification pour certains utilisateurs
- Lorsqu'activée, l'utilisateur voit les menus mais doit entrer son mot de passe avant d'y accéder
- La réauthentification est valide pendant 5 minutes
- Après 5 minutes, l'utilisateur doit se réauthentifier

#### Activation
1. L'administrateur d'entreprise accède à "Gestion des utilisateurs" (`/manage-users/`)
2. Lors de la création ou modification d'un utilisateur, cocher "Exiger une réauthentification pour accéder aux menus"
3. L'utilisateur devra alors se réauthentifier à chaque accès aux sections protégées

#### Utilisation dans le Code
```python
from core.decorators import reauth_required

@reauth_required
def ma_vue_protegee(request):
    # Cette vue nécessitera une réauthentification
    pass
```

### 3. Gestion des Utilisateurs

#### Pour les Administrateurs d'Entreprise
- **URL**: `/manage-users/`
- Créer de nouveaux utilisateurs pour leur entreprise
- Assigner des profils et permissions
- Activer/désactiver la réauthentification par utilisateur
- Voir la liste de tous les utilisateurs de l'entreprise

#### Champs Utilisateur
- Informations de base (nom, prénom, username, email)
- Téléphone
- Profil (niveau d'accès)
- Réauthentification (activée/désactivée)
- Mot de passe

## Modèles de Données

### Entreprise
```python
- id (UUID)
- nom_entreprise
- slug (unique)
- nif
- num_cnss
- adresse, ville, pays
- telephone, email
- logo
- plan_abonnement
- max_utilisateurs
- date_creation
- date_expiration
- actif
```

### Utilisateur (modifié)
```python
# Nouveaux champs:
- entreprise (ForeignKey vers Entreprise)
- est_admin_entreprise (Boolean)
- require_reauth (Boolean)
- last_reauth (DateTime)
```

## Décorateurs Disponibles

### `@reauth_required`
Exige une réauthentification si activée pour l'utilisateur

### `@entreprise_active_required`
Vérifie que l'entreprise de l'utilisateur est active

### Exemple d'utilisation combinée
```python
from core.decorators import reauth_required, entreprise_active_required
from django.contrib.auth.decorators import login_required

@login_required
@entreprise_active_required
@reauth_required
def vue_sensible(request):
    # Vue hautement sécurisée
    pass
```

## URLs Disponibles

| URL | Nom | Description |
|-----|-----|-------------|
| `/register-entreprise/` | `core:register_entreprise` | Inscription d'une nouvelle entreprise |
| `/reauth/` | `core:reauth` | Page de réauthentification |
| `/manage-users/` | `core:manage_users` | Gestion des utilisateurs (admin entreprise) |

## Workflow d'Inscription

1. **Visiteur** → Clique sur "Créer un compte entreprise" sur la page de login
2. **Formulaire** → Remplit les informations de l'entreprise et de l'administrateur
3. **Validation** → Le système crée:
   - L'entreprise avec un slug unique
   - Le profil "Administrateur Entreprise" (si n'existe pas)
   - L'utilisateur administrateur
4. **Connexion automatique** → L'administrateur est connecté automatiquement
5. **Redirection** → Vers le dashboard

## Workflow de Réauthentification

1. **Utilisateur connecté** → Clique sur un menu protégé
2. **Vérification** → Le décorateur `@reauth_required` vérifie:
   - Si `require_reauth` est activé pour cet utilisateur
   - Si la dernière réauthentification date de moins de 5 minutes
3. **Redirection** → Si nécessaire, redirige vers `/reauth/`
4. **Saisie mot de passe** → L'utilisateur entre son mot de passe
5. **Validation** → Si correct, met à jour `last_reauth`
6. **Accès** → Redirige vers la page demandée

## Sécurité

### Isolation des Données
- Chaque requête filtre automatiquement par entreprise
- Un utilisateur ne peut voir que les données de son entreprise

### Validation
- Les slugs d'entreprise sont uniques
- Les emails d'entreprise sont uniques
- Les NIF et numéros CNSS sont uniques
- Validation des mots de passe (minimum 8 caractères)

### Logs
- Toutes les actions sont enregistrées dans `LogActivite`
- Inclut: création d'entreprise, création d'utilisateur, réauthentification

## Administration Django

Accès via `/admin/` pour les superutilisateurs:
- Gestion des entreprises
- Gestion des utilisateurs multi-entreprises
- Modification des plans d'abonnement
- Activation/désactivation d'entreprises

## Migration

Pour appliquer les changements:
```bash
python manage.py makemigrations core
python manage.py migrate core
```

## Exemple d'Utilisation

### Créer une entreprise via le code
```python
from core.models import Entreprise, Utilisateur, ProfilUtilisateur
from django.utils.text import slugify

# Créer l'entreprise
entreprise = Entreprise.objects.create(
    nom_entreprise="Ma Société SARL",
    slug=slugify("Ma Société SARL"),
    email="contact@masociete.gn",
    plan_abonnement="basique",
    max_utilisateurs=10
)

# Créer l'administrateur
profil_admin = ProfilUtilisateur.objects.get(nom_profil="Administrateur Entreprise")
admin = Utilisateur.objects.create_user(
    username="admin_masociete",
    email="admin@masociete.gn",
    password="motdepasse123",
    entreprise=entreprise,
    profil=profil_admin,
    est_admin_entreprise=True
)
```

### Activer la réauthentification pour un utilisateur
```python
user = Utilisateur.objects.get(username="employe1")
user.require_reauth = True
user.save()
```

## Support

Pour toute question ou problème, contactez l'équipe de développement.
