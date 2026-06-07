# Optimisations de Performance - Gestionnaire RH Guinée

## Résumé des Optimisations Implémentées

Ce document résume toutes les optimisations de performance implémentées dans le système.

---

## 1. Index de Base de Données

### Modèle `Employe` (employes)
```python
indexes = [
    ('entreprise', 'statut_employe'),  # Requêtes filtrées par entreprise+statut
    ('entreprise', 'nom'),              # Recherche par nom
    ('statut_employe',),                # Filtrage par statut
    ('service',),                       # Filtrage par service
    ('type_contrat',),                  # Filtrage par type contrat
    ('date_embauche',),                 # Tri par ancienneté
]
```

### Modèle `BulletinPaie` (paie)
```python
indexes = [
    ('periode', 'statut_bulletin'),     # Liste bulletins par période
    ('employe', 'annee_paie', 'mois_paie'),  # Historique employé
    ('statut_bulletin',),               # Filtrage par statut
    ('annee_paie', 'mois_paie'),        # Tri chronologique
]
```

### Modèle `ElementSalaire` (paie)
```python
indexes = [
    ('employe', 'actif'),               # Éléments actifs par employé
    ('employe', 'date_debut', 'date_fin'),  # Validité temporelle
    ('rubrique',),                      # Jointure rubrique
]
```

### Modèle `LigneBulletin` (paie)
```python
indexes = [
    ('bulletin',),                      # Lignes par bulletin
    ('rubrique',),                      # Jointure rubrique
]
```

---

## 2. Configuration du Cache

### Settings (`gestionnaire_rh/settings.py`)
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'gestionnaire-rh-cache',
        'TIMEOUT': 3600,  # 1 heure
        'OPTIONS': {
            'MAX_ENTRIES': 5000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# Sessions cachées
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
```

### Pour Production avec Redis (optionnel)
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'TIMEOUT': 3600,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    }
}
```

---

## 3. Service de Cache (`paie/cache_service.py`)

### Données Cachées
| Type de données | Durée de cache | Clé |
|----------------|----------------|-----|
| Constantes | 1 heure | `paie:constantes` |
| Rubriques actives | 1 heure | `paie:rubriques` |
| Tranches RTS | 1 heure | `paie:tranches:{annee}` |
| Devise de base | 30 minutes | `paie:devises:base` |
| Éléments employé | 5 minutes | `paie:elements:{id}:{annee}:{mois}` |

### Utilisation
```python
from paie.cache_service import PayrollCacheService

# Récupérer les constantes (avec cache)
constantes = PayrollCacheService.get_constantes()

# Préchauffer le cache avant calcul massif
PayrollCacheService.warmup_cache(annee=2024)

# Invalider le cache si nécessaire
PayrollCacheService.invalidate_all()
```

---

## 4. Service de Calcul en Masse (`paie/services_bulk.py`)

### `BulkPayrollService`
- **Préchauffe le cache** avant calcul
- **Prefetch optimisé** des employés avec relations
- **Traitement par batch** (50 employés à la fois)
- **Suppression bulk** des anciens bulletins

### Utilisation
```python
from paie.services_bulk import BulkPayrollService

bulk_service = BulkPayrollService(periode, entreprise)
result = bulk_service.calculer_tous_bulletins(utilisateur)

# result = {
#     'bulletins_crees': 150,
#     'erreurs': [],
#     'temps_execution': 12.5,  # secondes
#     'employes_total': 150,
# }
```

### `PayrollStatsService`
- Statistiques agrégées en une seule requête
- Évite les N+1 queries

---

## 5. Managers Optimisés (`paie/managers.py`)

### QuerySets Chaînables
```python
# Bulletins avec toutes les relations préchargées
BulletinPaie.objects.complet().pour_entreprise(entreprise)

# Éléments actifs avec rubrique
ElementSalaire.objects.actifs().avec_rubrique().pour_employe(employe)

# Périodes avec stats
PeriodePaie.objects.pour_entreprise(entreprise).avec_stats_bulletins()
```

### Méthodes Disponibles

**BulletinPaie**
- `.avec_employe()` - Select related employe + établissement + service
- `.avec_periode()` - Select related période
- `.avec_lignes()` - Prefetch lignes avec rubriques
- `.complet()` - Toutes les relations
- `.pour_entreprise(e)` - Filtre entreprise
- `.valides()` / `.calcules()` - Filtres statut

**ElementSalaire**
- `.actifs()` - Éléments actifs
- `.avec_rubrique()` - Select related rubrique
- `.valides_pour_date(date)` - Valides à une date
- `.gains()` / `.retenues()` - Par type

---

## 6. Optimisations Middleware

### Déjà Présentes
```python
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Assets statiques
    'django.middleware.gzip.GZipMiddleware',       # Compression GZip
    # ...
]
```

### Connexions DB Persistantes (Production)
```python
if not DEBUG:
    DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
```

---

## 7. Bonnes Pratiques d'Utilisation

### Dans les Vues
```python
# ❌ ÉVITER - N+1 queries
bulletins = BulletinPaie.objects.filter(periode=p)
for b in bulletins:
    print(b.employe.nom)  # Requête à chaque itération!

# ✅ CORRECT - Une seule requête
bulletins = BulletinPaie.objects.filter(periode=p).select_related('employe')
for b in bulletins:
    print(b.employe.nom)  # Déjà chargé!

# ✅ ENCORE MIEUX - Utiliser le manager
bulletins = BulletinPaie.objects.avec_employe().pour_periode(p)
```

### Pour les Agrégations
```python
# ❌ ÉVITER
total = sum(b.net_a_payer for b in bulletins)

# ✅ CORRECT
total = bulletins.aggregate(Sum('net_a_payer'))['net_a_payer__sum']
```

---

## 8. Métriques de Performance Attendues

| Opération | Avant | Après | Amélioration |
|-----------|-------|-------|--------------|
| Calcul 100 bulletins | ~60s | ~15s | **4x plus rapide** |
| Chargement liste employés | ~2s | ~0.3s | **6x plus rapide** |
| Dashboard | ~3s | ~0.5s | **6x plus rapide** |
| Détail bulletin | ~1s | ~0.2s | **5x plus rapide** |

---

## 9. Commandes de Maintenance

### Préchauffer le cache
```bash
python manage.py shell -c "from paie.cache_service import PayrollCacheService; PayrollCacheService.warmup_cache()"
```

### Vider le cache
```bash
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

### Analyser les requêtes (debug)
```python
from django.db import connection
print(len(connection.queries))  # Nombre de requêtes
```

---

## 10. Fichiers Modifiés

| Fichier | Type |
|---------|------|
| `gestionnaire_rh/settings.py` | Configuration cache |
| `paie/cache_service.py` | **Nouveau** - Service cache |
| `paie/services_bulk.py` | **Nouveau** - Calcul en masse |
| `paie/managers.py` | **Nouveau** - QuerySets optimisés |
| `paie/services.py` | Utilisation du cache |
| `paie/views.py` | Service bulk pour calcul |
| `paie/models.py` | Index + Managers |
| `employes/models.py` | Index |

---

*Document généré le 04/01/2026*
