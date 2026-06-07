# 🔒 Notes de Sécurité - Content Security Policy (CSP)

## ⚠️ Directive `unsafe-eval` Activée

### Pourquoi ?

La directive `'unsafe-eval'` a été ajoutée à la CSP pour permettre l'évaluation dynamique de code JavaScript. Cela est nécessaire pour certaines bibliothèques tierces qui utilisent :
- `eval()`
- `new Function()`
- `setTimeout([string], ...)`
- `setInterval([string], ...)`

### 📦 Bibliothèques Concernées

Les bibliothèques suivantes peuvent nécessiter `unsafe-eval` :
- **Chart.js** - Graphiques et visualisations
- **Certains plugins Bootstrap** - Composants dynamiques
- **Bibliothèques de templating** - Handlebars, Mustache, etc.
- **Éditeurs WYSIWYG** - TinyMCE, CKEditor, etc.

## 🛡️ Risques de Sécurité

### Risque Principal : Injection de Code

Avec `'unsafe-eval'` activé, si un attaquant parvient à injecter du code JavaScript sur votre site (via XSS), il pourrait :
- Exécuter du code arbitraire via `eval()`
- Créer de nouvelles fonctions dynamiquement
- Contourner certaines protections

### Niveau de Risque

- **Sans `unsafe-eval`** : 🟢 Risque faible
- **Avec `unsafe-eval`** : 🟡 Risque moyen (si autres protections en place)
- **Avec `unsafe-eval` + XSS** : 🔴 Risque élevé

## ✅ Protections Complémentaires en Place

Notre application maintient plusieurs couches de sécurité :

### 1. Protection XSS
```python
# Dans settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### 2. Middleware de Protection
```python
# Middleware actifs
'core.middleware.XSSProtectionMiddleware'
'core.middleware.SQLInjectionProtectionMiddleware'
```

### 3. Validation des Entrées
- Utilisation de Django Forms avec validation
- Échappement automatique des templates Django
- Utilisation de `bleach` pour nettoyer le HTML

### 4. CSRF Protection
```python
CSRF_USE_SESSIONS = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
```

## 🔧 Alternatives à `unsafe-eval`

### Option 1 : Remplacer les Bibliothèques

Si possible, utilisez des bibliothèques qui n'ont pas besoin de `unsafe-eval` :

**Au lieu de** :
- Chart.js → Recharts (React) ou ApexCharts
- Handlebars → Templates Django natifs
- eval() → JSON.parse() pour les données

**Exemple** :
```javascript
// ❌ Mauvais (nécessite unsafe-eval)
var result = eval('2 + 2');

// ✅ Bon (pas besoin de unsafe-eval)
var result = 2 + 2;

// ❌ Mauvais
setTimeout("alert('Hello')", 1000);

// ✅ Bon
setTimeout(function() { alert('Hello'); }, 1000);
```

### Option 2 : CSP par Page

Désactiver `unsafe-eval` globalement et l'activer uniquement sur les pages qui en ont besoin :

```python
# Dans une vue spécifique
from csp.decorators import csp_update

@csp_update(SCRIPT_SRC=("'self'", "'unsafe-eval'"))
def chart_view(request):
    # Cette page peut utiliser eval()
    return render(request, 'charts.html')
```

### Option 3 : Nonces CSP

Utiliser des nonces pour autoriser des scripts spécifiques :

```python
# settings.py
CSP_INCLUDE_NONCE_IN = ['script-src']

# Template
<script nonce="{{ request.csp_nonce }}">
    // Code autorisé
</script>
```

## 📝 Bonnes Pratiques

### ✅ À Faire

1. **Éviter eval() dans votre code**
   ```javascript
   // ❌ Ne jamais faire
   eval(userInput);
   
   // ✅ Toujours faire
   JSON.parse(userInput);
   ```

2. **Valider toutes les entrées utilisateur**
   ```python
   from django import forms
   
   class MyForm(forms.Form):
       data = forms.CharField(max_length=100)
       
       def clean_data(self):
           data = self.cleaned_data['data']
           # Validation personnalisée
           return data
   ```

3. **Utiliser des fonctions au lieu de strings**
   ```javascript
   // ❌ Mauvais
   setTimeout("doSomething()", 1000);
   
   // ✅ Bon
   setTimeout(doSomething, 1000);
   ```

4. **Échapper le HTML**
   ```django
   {# Django échappe automatiquement #}
   {{ user_input }}
   
   {# Si vous devez afficher du HTML #}
   {{ user_input|safe }}  {# Utilisez avec EXTRÊME prudence #}
   ```

### ❌ À Éviter

1. **Ne jamais utiliser eval() avec des données utilisateur**
   ```javascript
   // ❌ DANGEREUX!
   var userCode = getUserInput();
   eval(userCode);  // Peut exécuter n'importe quel code!
   ```

2. **Ne pas désactiver l'échappement sans raison**
   ```django
   {# ❌ Dangereux #}
   {{ user_comment|safe }}
   
   {# ✅ Sûr #}
   {{ user_comment }}
   ```

3. **Ne pas construire du HTML avec des strings**
   ```javascript
   // ❌ Vulnérable à XSS
   element.innerHTML = '<div>' + userInput + '</div>';
   
   // ✅ Sûr
   var div = document.createElement('div');
   div.textContent = userInput;
   element.appendChild(div);
   ```

## 🔍 Audit de Sécurité

### Vérifier l'Utilisation de eval()

```bash
# Rechercher eval() dans votre code
grep -r "eval(" static/
grep -r "new Function" static/
grep -r 'setTimeout.*"' static/
grep -r 'setInterval.*"' static/
```

### Tester la CSP

1. Ouvrir la console du navigateur (F12)
2. Essayer d'exécuter :
   ```javascript
   eval('console.log("test")')
   ```
3. Devrait fonctionner (avec unsafe-eval)

### Vérifier les Violations CSP

Dans la console, chercher :
```
[Report Only] Refused to evaluate a string as JavaScript...
```

## 🎯 Configuration Actuelle

### CSP Active

```python
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': (
            "'self'", 
            "'unsafe-inline'",   # Pour les scripts inline
            "'unsafe-eval'",     # ⚠️ Pour eval() et similaires
            "https://cdn.jsdelivr.net",
            "https://code.jquery.com",
            "https://stackpath.bootstrapcdn.com"
        ),
        'style-src': (
            "'self'", 
            "'unsafe-inline'",   # Pour les styles inline
            "https://cdn.jsdelivr.net",
            "https://fonts.googleapis.com",
            "https://stackpath.bootstrapcdn.com"
        ),
        'font-src': (
            "'self'",
            "https://fonts.gstatic.com",
            "https://cdn.jsdelivr.net"
        ),
        'img-src': ("'self'", "data:", "https:", "blob:"),
        'connect-src': ("'self'",),
        'frame-ancestors': ("'none'",),
        'base-uri': ("'self'",),
        'form-action': ("'self'",),
        'media-src': ("'self'", "data:", "https:"),
        'object-src': ("'none'",),
        'worker-src': ("'self'", "blob:"),
    }
}
```

## 📊 Matrice de Risques

| Directive | Risque | Justification | Alternative |
|-----------|--------|---------------|-------------|
| `'unsafe-inline'` | 🟡 Moyen | Scripts inline nécessaires | Utiliser des nonces |
| `'unsafe-eval'` | 🟡 Moyen | Bibliothèques tierces | Remplacer les bibliothèques |
| CDN externes | 🟢 Faible | Bibliothèques populaires | Auto-héberger |
| `data:` images | 🟢 Faible | Logos, icônes | Fichiers statiques |

## 🔄 Plan d'Amélioration Future

### Phase 1 : Audit (Immédiat)
- [ ] Identifier toutes les utilisations de eval()
- [ ] Lister les bibliothèques qui nécessitent unsafe-eval
- [ ] Documenter les cas d'usage

### Phase 2 : Réduction (Court terme)
- [ ] Remplacer eval() par des alternatives sûres
- [ ] Migrer vers des bibliothèques sans eval()
- [ ] Implémenter des nonces CSP

### Phase 3 : Durcissement (Moyen terme)
- [ ] Retirer unsafe-eval de la CSP globale
- [ ] Utiliser CSP par page si nécessaire
- [ ] Audit de sécurité complet

### Phase 4 : Monitoring (Long terme)
- [ ] Implémenter CSP reporting
- [ ] Analyser les violations CSP
- [ ] Ajuster la politique selon les besoins

## 📚 Ressources

### Documentation
- [MDN - Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [OWASP - CSP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- [Django CSP Documentation](https://django-csp.readthedocs.io/)

### Outils
- [CSP Evaluator](https://csp-evaluator.withgoogle.com/) - Analyser votre CSP
- [Report URI](https://report-uri.com/) - Monitoring des violations CSP
- [CSP Builder](https://csper.io/docs/generating-content-security-policy) - Générer une CSP

## ✅ Checklist de Sécurité

Avant de déployer en production :

- [x] CSP configurée
- [x] `unsafe-eval` documenté
- [x] Protections XSS actives
- [x] CSRF protection activée
- [x] Middleware de sécurité en place
- [ ] Audit du code pour eval()
- [ ] Tests de pénétration
- [ ] Monitoring des violations CSP

## 🚨 En Cas de Problème

Si vous détectez une tentative d'exploitation :

1. **Vérifier les logs**
   ```bash
   tail -f /var/log/django/security.log
   ```

2. **Désactiver temporairement unsafe-eval**
   ```python
   # Dans settings.py, retirer "'unsafe-eval'"
   'script-src': ("'self'", "'unsafe-inline'", ...)
   ```

3. **Analyser les violations CSP**
   - Console du navigateur
   - Logs du serveur
   - Outils de monitoring

4. **Contacter l'équipe de sécurité**

---

**Version** : 1.0.0  
**Date** : 26 Octobre 2025  
**Dernière révision** : 26 Octobre 2025  
**Statut** : ⚠️ `unsafe-eval` Actif - Surveillance Recommandée
