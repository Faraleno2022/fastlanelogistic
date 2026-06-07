# 🔧 Résolution des Problèmes de Formulaires en Production

## 🎯 Symptômes Courants

- ❌ Formulaires sans style (apparence basique HTML)
- ❌ Boutons non stylés
- ❌ Champs de saisie mal alignés
- ❌ Pas de validation visuelle
- ❌ Dropdowns qui ne fonctionnent pas
- ❌ Messages d'erreur non formatés

## 🔍 Diagnostic Rapide

### 1. Vérifier la Console du Navigateur

```
1. Ouvrir votre site en production
2. Appuyer sur F12 (DevTools)
3. Onglet "Console"
4. Chercher les erreurs en rouge
```

**Erreurs communes** :
- `Failed to load resource: net::ERR_BLOCKED_BY_RESPONSE` → Problème CSP
- `404 Not Found` pour CSS/JS → Fichiers statiques non collectés
- `Refused to load stylesheet` → Problème CORS ou CSP

### 2. Vérifier l'Onglet Network

```
1. F12 → Onglet "Network"
2. Recharger la page (Ctrl+R)
3. Filtrer par "CSS" et "JS"
4. Vérifier que tous les fichiers se chargent (status 200)
```

## 🛠️ Solutions par Problème

### Problème 1 : Fichiers Statiques Non Chargés

**Symptôme** : Formulaires sans aucun style

**Solution** :

```bash
# Sur le serveur
cd ~/ETRAGC_SARLU/gestionrh
source venv/bin/activate
export $(cat .env | xargs)

# Collecter les fichiers statiques
python manage.py collectstatic --clear --noinput

# Vérifier les dossiers
ls -la staticfiles/
ls -la static/
```

**Sur PythonAnywhere** :
1. Onglet "Web"
2. Section "Static files"
3. Vérifier les mappings :
   - URL: `/static/` → Directory: `/home/ETRAGCSARLU/ETRAGC_SARLU/gestionrh/staticfiles`
   - URL: `/media/` → Directory: `/home/ETRAGCSARLU/ETRAGC_SARLU/gestionrh/media`

### Problème 2 : Bootstrap Non Chargé

**Symptôme** : Formulaires partiellement stylés

**Diagnostic** :
```javascript
// Dans la console du navigateur (F12)
typeof bootstrap
// Devrait retourner "object", pas "undefined"
```

**Solution** :

Le template `base.html` a été mis à jour avec :
- ✅ Intégrité SRI pour Bootstrap
- ✅ Fallbacks en cas d'échec
- ✅ Scripts de vérification

**Vérifier** :
1. Ouvrir F12 → Console
2. Chercher : `✅ Bootstrap JS chargé`
3. Si `❌ Bootstrap JS non chargé!`, problème CSP

### Problème 3 : Content Security Policy (CSP)

**Symptôme** : Erreurs CSP dans la console

**Solution Automatique** :

```bash
cd ~/ETRAGC_SARLU/gestionrh
python fix_csp.py
```

**Solution Manuelle** :

Vérifier dans `gestionnaire_rh/settings.py` :

```python
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'", 
                      "https://cdn.jsdelivr.net", 
                      "https://code.jquery.com"),
        'style-src': ("'self'", "'unsafe-inline'", 
                     "https://cdn.jsdelivr.net"),
        'img-src': ("'self'", "data:", "https:", "blob:"),
    }
}
```

### Problème 4 : Crispy Forms Non Stylés

**Symptôme** : Formulaires Django sans le style Bootstrap

**Vérifier l'installation** :

```bash
pip show crispy-bootstrap5
# Devrait afficher la version installée
```

**Si non installé** :

```bash
pip install crispy-bootstrap5
```

**Vérifier settings.py** :

```python
INSTALLED_APPS = [
    # ...
    'crispy_forms',
    'crispy_bootstrap5',
    # ...
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
```

**Dans les templates** :

```django
{% load crispy_forms_tags %}

<form method="post">
    {% csrf_token %}
    {{ form|crispy }}
    <button type="submit" class="btn btn-primary">Envoyer</button>
</form>
```

### Problème 5 : jQuery Non Chargé

**Symptôme** : Dropdowns, modals ne fonctionnent pas

**Diagnostic** :

```javascript
// Console du navigateur
typeof jQuery
// Devrait retourner "function"
```

**Solution** :

Le template `base.html` charge maintenant jQuery **avant** Bootstrap.

### Problème 6 : DEBUG=True en Production

**Symptôme** : Fichiers statiques servis par Django (lent)

**Vérifier** :

```bash
cat .env | grep DEBUG
# Devrait afficher: DEBUG=False
```

**Corriger** :

```bash
nano .env
# Changer DEBUG=True en DEBUG=False
```

## 🚀 Script de Correction Automatique

### fix_production.sh

```bash
#!/bin/bash
cd ~/ETRAGC_SARLU/gestionrh
source venv/bin/activate
export $(cat .env | xargs)

# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Créer les dossiers
mkdir -p static staticfiles media

# 3. Collecter les fichiers statiques
python manage.py collectstatic --clear --noinput

# 4. Vérifier la configuration
python manage.py check --deploy

echo "✅ Correction terminée!"
echo "👉 Cliquez 'Reload' sur PythonAnywhere"
```

**Utilisation** :

```bash
cd ~/ETRAGC_SARLU/gestionrh
bash fix_production.sh
```

## 📋 Checklist de Vérification

### Avant de Reload

- [ ] `.env` contient `DEBUG=False`
- [ ] `.env` contient les bons `ALLOWED_HOSTS`
- [ ] Dossier `staticfiles/` existe et contient des fichiers
- [ ] `python manage.py check --deploy` sans erreur
- [ ] CSP configuré correctement

### Après Reload

- [ ] Site accessible (pas d'erreur 500)
- [ ] Page de connexion s'affiche correctement
- [ ] Formulaires stylés avec Bootstrap
- [ ] Boutons cliquables et stylés
- [ ] Dropdowns fonctionnent
- [ ] Messages d'erreur formatés
- [ ] Console du navigateur sans erreurs

## 🔍 Commandes de Diagnostic

### Vérifier les Fichiers Statiques

```bash
# Lister les fichiers collectés
ls -R staticfiles/

# Vérifier la taille
du -sh staticfiles/

# Chercher Bootstrap
find staticfiles/ -name "*bootstrap*"
```

### Vérifier les Dépendances

```bash
pip list | grep -i bootstrap
pip list | grep -i crispy
pip list | grep -i django
```

### Tester la Configuration Django

```bash
python manage.py check
python manage.py check --deploy
python manage.py diffsettings
```

### Vérifier les Permissions

```bash
ls -la staticfiles/
ls -la media/
# Les dossiers doivent être lisibles
```

## 🐛 Problèmes Spécifiques

### Formulaire d'Inscription Entreprise

**Template** : `templates/core/register_entreprise.html`

**Vérifier** :

```django
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form|crispy }}
    <button type="submit" class="btn btn-primary">S'inscrire</button>
</form>
{% endblock %}
```

### Formulaire de Connexion

**Template** : `templates/core/login.html`

**Vérifier** :

```django
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<form method="post">
    {% csrf_token %}
    {{ form|crispy }}
    <button type="submit" class="btn btn-primary">Se connecter</button>
</form>
{% endblock %}
```

## 📞 Support

### Logs à Consulter

Sur PythonAnywhere :
1. **Error log** : Erreurs Python/Django
2. **Server log** : Erreurs serveur web
3. **Access log** : Requêtes HTTP

### Informations à Fournir

Si vous demandez de l'aide :
- URL du site
- Capture d'écran du problème
- Console du navigateur (F12)
- Extrait des logs d'erreur
- Version de Django : `python -c "import django; print(django.VERSION)"`

## ✅ Solution Complète (Tout-en-un)

```bash
#!/bin/bash
# Script de correction complète

cd ~/ETRAGC_SARLU/gestionrh
source venv/bin/activate

# Charger les variables
export $(cat .env | xargs)

# Mettre à jour les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Créer les dossiers
mkdir -p static staticfiles media media/entreprises/logos

# Collecter les fichiers statiques
python manage.py collectstatic --clear --noinput

# Appliquer les migrations
python manage.py migrate

# Vérifier la configuration
python manage.py check --deploy

# Afficher le résumé
echo ""
echo "=========================================="
echo "✅ CORRECTION TERMINÉE"
echo "=========================================="
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Sur PythonAnywhere → Onglet 'Web'"
echo "   2. Cliquer sur 'Reload' 🔄"
echo "   3. Tester: https://www.guineerh.space"
echo "   4. Ouvrir F12 → Console (vérifier les erreurs)"
echo ""
```

Sauvegardez ce script dans `fix_all.sh` et exécutez :

```bash
bash fix_all.sh
```

---

**Version** : 1.0.0  
**Date** : 26 Octobre 2025  
**Statut** : ✅ Guide Complet de Dépannage
