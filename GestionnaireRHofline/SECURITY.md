# Guide de Sécurité - Gestionnaire RH Guinée

## 🔒 Protections Implémentées

### 1. Protection contre les Attaques par Force Brute

**Django Axes & Django Defender**
- Blocage automatique après 5 tentatives de connexion échouées
- Durée de blocage : 1 heure
- Tracking par IP et nom d'utilisateur
- Logs de sécurité pour toutes les tentatives

**Configuration :**
```python
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # heure
DEFENDER_LOGIN_FAILURE_LIMIT = 5
```

### 2. Protection CSRF (Cross-Site Request Forgery)

**Mesures :**
- Tokens CSRF sur tous les formulaires
- Cookies CSRF sécurisés (HttpOnly, Secure, SameSite)
- Validation stricte des origines
- Page d'erreur personnalisée

**Utilisation dans les templates :**
```html
<form method="post">
    {% csrf_token %}
    <!-- Vos champs de formulaire -->
</form>
```

### 3. Protection XSS (Cross-Site Scripting)

**Middleware personnalisé :**
- Détection automatique de scripts malveillants
- Sanitization des entrées utilisateur
- Échappement automatique dans les templates Django
- Bibliothèque Bleach pour le nettoyage HTML

**Utilisation :**
```python
from core.security import DataSanitizer

# Nettoyer du HTML
clean_html = DataSanitizer.sanitize_html(user_input)

# Échapper du texte
safe_text = DataSanitizer.sanitize_input(user_input)
```

### 4. Protection contre les Injections SQL

**Middleware personnalisé :**
- Détection de patterns SQL suspects
- Blocage automatique des requêtes malveillantes
- Logs de toutes les tentatives
- Utilisation de l'ORM Django (protection native)

**Patterns détectés :**
- `UNION SELECT`
- `DROP TABLE`
- `INSERT INTO`
- `OR 1=1`
- Commentaires SQL (`--`, `;--`)

### 5. Sécurité des Sessions

**Configuration :**
```python
SESSION_COOKIE_SECURE = True  # HTTPS uniquement
SESSION_COOKIE_HTTPONLY = True  # Pas accessible en JavaScript
SESSION_COOKIE_SAMESITE = 'Strict'  # Protection CSRF
SESSION_COOKIE_AGE = 3600  # 1 heure
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

### 6. Sécurité HTTPS

**En-têtes de sécurité :**
- `Strict-Transport-Security` (HSTS)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

**Configuration production :**
```python
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 7. Content Security Policy (CSP)

**Protection contre :**
- Injection de scripts
- Clickjacking
- Chargement de ressources non autorisées

**Configuration :**
```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "https://cdn.jsdelivr.net")
CSP_FRAME_ANCESTORS = ("'none'",)
```

### 8. Chiffrement des Données Sensibles

**Utilisation :**
```python
from core.security import DataEncryption

# Chiffrer des données
encrypted = DataEncryption.encrypt_data("données sensibles")

# Déchiffrer
decrypted = DataEncryption.decrypt_data(encrypted)

# Hash (non réversible)
hashed = DataEncryption.hash_sensitive_data("mot de passe")
```

### 9. Validation des Fichiers Uploadés

**Protections :**
- Vérification des extensions autorisées
- Limitation de taille (5MB par défaut)
- Nettoyage des noms de fichiers
- Protection contre la traversée de répertoire

**Utilisation :**
```python
from core.security import FileValidator

# Valider un fichier
FileValidator.validate_uploaded_file(
    uploaded_file,
    file_type='images',
    max_size=5*1024*1024
)
```

### 10. Validation des Mots de Passe

**Exigences :**
- Minimum 8 caractères
- Au moins une majuscule
- Au moins une minuscule
- Au moins un chiffre
- Au moins un caractère spécial

**Utilisation :**
```python
from core.security import PasswordValidator

PasswordValidator.validate_password_strength(password)
```

### 11. Logging de Sécurité

**Fichiers de logs :**
- `logs/django.log` - Logs généraux
- `logs/security.log` - Logs de sécurité

**Événements loggés :**
- Tentatives de connexion échouées
- Tentatives d'injection SQL/XSS
- Accès refusés
- Erreurs de sécurité
- Modifications de compte

### 12. Protection des Données Personnelles (RGPD)

**Mesures :**
- Chiffrement des données sensibles
- Logs d'accès aux données
- Droit à l'oubli (suppression de compte)
- Minimisation des données collectées
- Consentement explicite

## 🚀 Configuration pour la Production

### 1. Variables d'Environnement

Créez un fichier `.env` basé sur `.env.example` :

```bash
# Générer une SECRET_KEY sécurisée
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Générer une clé de chiffrement
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2. Paramètres de Production

Dans `.env` :
```env
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### 3. Base de Données

**PostgreSQL recommandé pour la production :**
```env
DB_ENGINE=postgresql
DB_NAME=gestionnaire_rh_guinee
DB_USER=votre_utilisateur
DB_PASSWORD=mot_de_passe_fort
DB_HOST=localhost
DB_PORT=5432
```

### 4. HTTPS

**Utiliser un certificat SSL :**
- Let's Encrypt (gratuit)
- Certificat commercial
- Cloudflare SSL

### 5. Firewall et Serveur

**Recommandations :**
- Utiliser Nginx ou Apache comme reverse proxy
- Configurer un firewall (UFW, iptables)
- Limiter les ports ouverts
- Utiliser fail2ban pour bloquer les IPs suspectes

## 🛡️ Bonnes Pratiques

### Pour les Développeurs

1. **Ne jamais commiter :**
   - Fichiers `.env`
   - Clés secrètes
   - Mots de passe
   - Données sensibles

2. **Toujours utiliser :**
   - L'ORM Django (pas de SQL brut)
   - Les validateurs de formulaires
   - `{% csrf_token %}` dans les formulaires
   - `@login_required` pour les vues protégées

3. **Valider toutes les entrées :**
   ```python
   from core.security import DataSanitizer
   
   clean_data = DataSanitizer.sanitize_input(user_input)
   ```

### Pour les Administrateurs

1. **Mots de passe :**
   - Utiliser des mots de passe forts
   - Changer régulièrement
   - Ne jamais partager

2. **Mises à jour :**
   - Maintenir Django à jour
   - Mettre à jour les dépendances
   - Appliquer les patches de sécurité

3. **Surveillance :**
   - Consulter régulièrement les logs
   - Surveiller les tentatives de connexion
   - Analyser les patterns suspects

4. **Sauvegardes :**
   - Sauvegardes quotidiennes de la base de données
   - Sauvegardes chiffrées
   - Tester les restaurations

## 🔍 Audit de Sécurité

### Commandes Utiles

```bash
# Vérifier les vulnérabilités des dépendances
pip install safety
safety check

# Scanner de sécurité Django
python manage.py check --deploy

# Analyser les logs de sécurité
tail -f logs/security.log
```

### Checklist de Sécurité

- [ ] DEBUG=False en production
- [ ] SECRET_KEY unique et sécurisée
- [ ] HTTPS activé
- [ ] Certificat SSL valide
- [ ] Base de données sécurisée
- [ ] Mots de passe forts
- [ ] Sauvegardes configurées
- [ ] Logs activés
- [ ] Firewall configuré
- [ ] Mises à jour appliquées

## 📞 Contact Sécurité

En cas de découverte d'une vulnérabilité :
- Email : security@votreentreprise.com
- Ne pas divulguer publiquement
- Fournir des détails techniques

## 📚 Ressources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

**Dernière mise à jour :** Octobre 2025
**Version :** 1.0
