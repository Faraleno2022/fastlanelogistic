# 🔒 Protections de Sécurité - Gestionnaire RH Guinée

## ✅ Protections Implémentées

### 🛡️ Protection contre les Attaques

| Type d'Attaque | Protection | Status |
|----------------|------------|--------|
| **Force Brute** | Django Axes + Defender | ✅ Actif |
| **SQL Injection** | Middleware + ORM Django | ✅ Actif |
| **XSS (Cross-Site Scripting)** | Middleware + Sanitization | ✅ Actif |
| **CSRF** | Tokens + Cookies sécurisés | ✅ Actif |
| **Clickjacking** | X-Frame-Options: DENY | ✅ Actif |
| **DDoS** | Rate Limiting | ✅ Actif |
| **Session Hijacking** | Cookies sécurisés + HTTPS | ✅ Actif |
| **Man-in-the-Middle** | HTTPS + HSTS | ✅ Actif |

### 🔐 Sécurité des Données

- ✅ **Chiffrement** : Cryptography (Fernet)
- ✅ **Hashing** : SHA-256 pour données sensibles
- ✅ **Validation** : Sanitization de toutes les entrées
- ✅ **Fichiers** : Validation extension + taille
- ✅ **Mots de passe** : Validation forte (8+ caractères, majuscules, chiffres, spéciaux)

### 📝 Logging et Audit

- ✅ **Logs de sécurité** : `logs/security.log`
- ✅ **Logs généraux** : `logs/django.log`
- ✅ **Tentatives de connexion** : Trackées et loggées
- ✅ **Activités utilisateur** : Enregistrées dans la base

## 🚀 Démarrage Rapide

### 1. Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Générer les clés de sécurité
python generate_security_keys.py

# Créer le fichier .env
cp .env.example .env
# Éditer .env avec vos configurations

# Appliquer les migrations
python manage.py migrate

# Créer le répertoire logs
mkdir logs
```

### 2. Vérification

```bash
# Vérifier la configuration de sécurité
python manage.py check --deploy

# Vérifier les vulnérabilités
pip install safety
safety check
```

### 3. Lancement

```bash
# Développement
python manage.py runserver

# Production (avec Gunicorn)
gunicorn gestionnaire_rh.wsgi:application --bind 0.0.0.0:8000
```

## 📋 Configuration de Sécurité

### Développement (.env)

```env
DEBUG=True
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

### Production (.env)

```env
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

## 🔧 Utilisation des Protections

### Dans les vues

```python
from core.decorators import secure_view, rate_limit, role_required
from core.security import DataSanitizer, FileValidator

@secure_view
@rate_limit(max_requests=10, time_window=60)
def ma_vue(request):
    # Nettoyer les entrées
    clean_data = DataSanitizer.sanitize_input(request.POST.get('data'))
    
    # Valider un fichier
    if 'file' in request.FILES:
        FileValidator.validate_uploaded_file(request.FILES['file'])
    
    # Votre logique...
```

### Dans les templates

```html
<!-- Toujours inclure le token CSRF -->
<form method="post">
    {% csrf_token %}
    <!-- Vos champs -->
</form>
```

## 📊 Monitoring

### Consulter les logs

```bash
# Logs de sécurité en temps réel
tail -f logs/security.log

# Tentatives de connexion bloquées
python manage.py axes_list_attempts

# Réinitialiser un utilisateur bloqué
python manage.py axes_reset username
```

### Statistiques

```bash
# Nombre de tentatives bloquées aujourd'hui
grep "$(date +%Y-%m-%d)" logs/security.log | grep "bloqué" | wc -l

# IPs les plus actives
grep "depuis" logs/security.log | awk '{print $NF}' | sort | uniq -c | sort -rn | head -10
```

## 🆘 En cas de Problème

### Compte bloqué

```bash
# Débloquer un utilisateur
python manage.py axes_reset nom_utilisateur

# Débloquer une IP
python manage.py axes_reset_ip 192.168.1.1
```

### Erreur CSRF

1. Vérifier que `{% csrf_token %}` est dans le formulaire
2. Vérifier que les cookies sont activés
3. En développement : `CSRF_COOKIE_SECURE=False`

### Logs pleins

```bash
# Les logs sont automatiquement rotationnés (15MB max)
# Pour nettoyer manuellement :
> logs/django.log
> logs/security.log
```

## 📚 Documentation Complète

- **[SECURITY.md](SECURITY.md)** : Guide complet de sécurité
- **[INSTALLATION_SECURITE.md](INSTALLATION_SECURITE.md)** : Guide d'installation détaillé

## 🔑 Commandes Utiles

```bash
# Générer une SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Générer une clé de chiffrement
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Vérifier la sécurité
python manage.py check --deploy

# Scanner les vulnérabilités
safety check

# Créer un superutilisateur
python manage.py createsuperuser
```

## ⚠️ Avertissements Importants

1. **Ne jamais commiter le fichier `.env`**
2. **Changer la SECRET_KEY en production**
3. **Activer HTTPS en production**
4. **Sauvegarder régulièrement la base de données**
5. **Surveiller les logs de sécurité**
6. **Mettre à jour les dépendances régulièrement**

## 🎯 Checklist Avant Production

- [ ] `DEBUG=False`
- [ ] SECRET_KEY unique
- [ ] HTTPS activé
- [ ] Certificat SSL valide
- [ ] Base de données PostgreSQL
- [ ] Firewall configuré
- [ ] Sauvegardes automatiques
- [ ] Logs surveillés
- [ ] Tests de sécurité effectués

## 📞 Contact

Pour toute question de sécurité :
- Email : security@votreentreprise.com
- Documentation : Voir fichiers SECURITY.md

---

**Version :** 1.0  
**Dernière mise à jour :** Octobre 2025  
**Niveau de sécurité :** 🔒🔒🔒🔒🔒 (5/5)
