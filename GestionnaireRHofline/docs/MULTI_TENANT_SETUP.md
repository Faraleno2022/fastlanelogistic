# Configuration Multi-Tenant avec Django-Tenants

Ce document explique comment configurer et utiliser l'architecture multi-tenant pour GestionnaireRH.

## Concept

Chaque entreprise inscrite obtient **son propre schéma PostgreSQL**, garantissant:
- ✅ **Isolation complète** des données
- ✅ **Performance optimale** (pas de filtrage par entreprise_id)
- ✅ **Sécurité renforcée** (impossible d'accéder aux données d'un autre tenant)
- ✅ **Scalabilité** (ajout facile de nouvelles entreprises)

## Prérequis

1. **PostgreSQL** (obligatoire pour les schémas)
2. **Python 3.10+**
3. **django-tenants** (inclus dans requirements.txt)

## Installation

### 1. Installer PostgreSQL

```bash
# Windows (avec Chocolatey)
choco install postgresql

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

### 2. Créer la base de données

```sql
CREATE DATABASE gestionnaire_rh_guinee;
CREATE USER grh_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE gestionnaire_rh_guinee TO grh_user;
```

### 3. Configurer le fichier .env

```env
DB_ENGINE=postgresql
DB_NAME=gestionnaire_rh_guinee
DB_USER=grh_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
DEFAULT_TENANT_DOMAIN=guineerh.space
```

### 4. Activer les settings multi-tenant

```bash
# Sauvegarder l'ancien fichier
mv gestionnaire_rh/settings.py gestionnaire_rh/settings_backup.py

# Activer les nouveaux settings
mv gestionnaire_rh/settings_tenant.py gestionnaire_rh/settings.py
```

### 5. Appliquer les migrations

```bash
# Installer les dépendances
pip install -r requirements.txt

# Créer les migrations pour l'app tenants
python manage.py makemigrations tenants

# Appliquer les migrations au schéma public
python manage.py migrate_schemas --shared

# Créer le tenant public
python manage.py create_public_tenant --domain=guineerh.space
```

### 6. Créer un super utilisateur

```bash
python manage.py createsuperuser
```

## Utilisation

### Créer une nouvelle entreprise (tenant)

#### Via la commande

```bash
python manage.py create_tenant \
    "Ma Nouvelle Entreprise" \
    "contact@entreprise.com" \
    "admin@entreprise.com" \
    "MotDePasse123!" \
    --admin-nom="DIALLO" \
    --admin-prenoms="Mamadou" \
    --domain="guineerh.space"
```

#### Via l'interface web

1. Accéder à `https://guineerh.space/inscription/`
2. Remplir le formulaire d'inscription
3. Le schéma et l'utilisateur admin sont créés automatiquement

### Accéder à un tenant

Chaque tenant a son propre sous-domaine:
- `entreprise1.guineerh.space`
- `entreprise2.guineerh.space`

### Configuration DNS

Pour la production, configurez un wildcard DNS:

```
*.guineerh.space  →  Votre_IP_Serveur
```

## Structure des schémas

```
PostgreSQL Database: gestionnaire_rh_guinee
├── public (schéma partagé)
│   ├── clients (liste des tenants)
│   ├── domains (domaines des tenants)
│   └── tables partagées...
│
├── entreprise_1 (schéma tenant)
│   ├── employes
│   ├── bulletins_paie
│   ├── conges
│   └── ...
│
├── entreprise_2 (schéma tenant)
│   ├── employes
│   ├── bulletins_paie
│   ├── conges
│   └── ...
│
└── ... (autres tenants)
```

## Commandes utiles

```bash
# Lister tous les tenants
python manage.py list_tenants

# Migrer un tenant spécifique
python manage.py migrate_schemas --tenant=schema_name

# Exécuter une commande pour un tenant
python manage.py tenant_command shell --schema=schema_name

# Supprimer un tenant (⚠️ ATTENTION: supprime toutes les données)
python manage.py delete_tenant schema_name
```

## Développement local

Pour le développement local, utilisez `localhost` avec des ports différents ou modifiez le fichier hosts:

```
# Windows: C:\Windows\System32\drivers\etc\hosts
# Linux/Mac: /etc/hosts

127.0.0.1 guineerh.local
127.0.0.1 entreprise1.guineerh.local
127.0.0.1 entreprise2.guineerh.local
```

## Sauvegarde

```bash
# Sauvegarder tous les schémas
pg_dump -U grh_user gestionnaire_rh_guinee > backup_full.sql

# Sauvegarder un schéma spécifique
pg_dump -U grh_user -n schema_name gestionnaire_rh_guinee > backup_schema.sql
```

## Dépannage

### Erreur "No tenant for hostname"

Le domaine n'est pas associé à un tenant. Vérifiez:
1. Le tenant existe dans la table `clients`
2. Le domaine existe dans la table `domains`
3. Le DNS pointe vers le serveur

### Erreur de migration

```bash
# Réinitialiser les migrations
python manage.py migrate_schemas --shared --fake-initial
```

## Support

Pour toute question, contactez: support@guineerh.space
