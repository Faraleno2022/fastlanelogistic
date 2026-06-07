# Guide d'Installation des Protections de Sécurité

## 📦 Installation des Dépendances

### 1. Installer les packages de sécurité

```bash
pip install -r requirements.txt
```

Les nouveaux packages de sécurité installés :
- **django-ratelimit** : Limitation du taux de requêtes
- **django-axes** : Protection contre les attaques par force brute
- **django-csp** : Content Security Policy
- **cryptography** : Chiffrement des données
- **bleach** : Sanitization HTML
- **django-defender** : Protection supplémentaire contre les attaques

## 🔑 Configuration Initiale

### 2. Générer les clés de sécurité

```bash
python generate_security_keys.py
```

Ce script va générer :
- Une SECRET_KEY Django unique
- Une clé de chiffrement (ENCRYPTION_KEY)
- Des mots de passe aléatoires sécurisés

### 3. Configurer les variables d'environnement

Copiez `.env.example` vers `.env` :

```bash
cp .env.example .env
```

Ou sur Windows :
```powershell
Copy-Item .env.example .env
```

Puis éditez `.env` avec les clés générées.

### 4. Créer le répertoire des logs

```bash
mkdir logs
```

## 🗄️ Migrations de Base de Données

### 5. Appliquer les migrations pour Axes et Defender

```bash
python manage.py migrate
```

Cela va créer les tables nécessaires pour :
- `axes_accessattempt` : Tentatives d'accès
- `axes_accesslog` : Logs d'accès
- `defender_accessattempt` : Tentatives bloquées

## ✅ Vérification de la Configuration

### 6. Vérifier la configuration de sécurité Django

```bash
python manage.py check --deploy
```

Cette commande va vérifier :
- Les paramètres de sécurité
- Les configurations HTTPS
- Les en-têtes de sécurité
- Les cookies sécurisés

### 7. Tester les protections

#### Test de protection contre la force brute :
1. Allez sur la page de connexion
2. Essayez de vous connecter 5 fois avec un mauvais mot de passe
3. Vous devriez être bloqué et voir la page "Compte Bloqué"

#### Test de protection CSRF :
1. Essayez de soumettre un formulaire sans token CSRF
2. Vous devriez voir la page d'erreur CSRF personnalisée

#### Test de protection XSS :
1. Essayez de soumettre `<script>alert('XSS')</script>` dans un champ
2. La requête devrait être bloquée

## 🚀 Configuration pour la Production

### 8. Paramètres de production dans `.env`

```env
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### 9. Configurer HTTPS

#### Avec Nginx :

```nginx
server {
    listen 80;
    server_name votredomaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votredomaine.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
}
```

### 10. Configurer le firewall

#### Sur Ubuntu/Debian avec UFW :

```bash
# Autoriser SSH
sudo ufw allow 22/tcp

# Autoriser HTTP et HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activer le firewall
sudo ufw enable
```

### 11. Installer et configurer Fail2Ban

```bash
sudo apt-get install fail2ban

# Créer une configuration pour Django
sudo nano /etc/fail2ban/jail.local
```

Ajouter :

```ini
[django-auth]
enabled = true
port = http,https
filter = django-auth
logpath = /path/to/logs/security.log
maxretry = 5
bantime = 3600
```

## 🔐 Sécurité de la Base de Données

### 12. PostgreSQL (Recommandé pour la production)

```bash
# Installer PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Créer la base de données
sudo -u postgres psql
CREATE DATABASE gestionnaire_rh_guinee;
CREATE USER votre_user WITH PASSWORD 'mot_de_passe_fort';
GRANT ALL PRIVILEGES ON DATABASE gestionnaire_rh_guinee TO votre_user;
\q
```

Configurer dans `.env` :

```env
DB_ENGINE=postgresql
DB_NAME=gestionnaire_rh_guinee
DB_USER=votre_user
DB_PASSWORD=mot_de_passe_fort
DB_HOST=localhost
DB_PORT=5432
```

### 13. Sauvegardes automatiques

Créer un script de sauvegarde :

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup de la base de données
pg_dump gestionnaire_rh_guinee > "$BACKUP_DIR/db_$DATE.sql"

# Backup des fichiers media
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" /path/to/media/

# Garder seulement les 30 dernières sauvegardes
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Ajouter au crontab :

```bash
crontab -e
# Ajouter : Sauvegarde quotidienne à 2h du matin
0 2 * * * /path/to/backup.sh
```

## 📊 Monitoring et Logs

### 14. Consulter les logs de sécurité

```bash
# Logs généraux
tail -f logs/django.log

# Logs de sécurité
tail -f logs/security.log

# Tentatives de connexion bloquées
python manage.py axes_list_attempts

# Réinitialiser les tentatives pour un utilisateur
python manage.py axes_reset username
```

### 15. Analyser les logs

```bash
# Compter les tentatives de connexion échouées
grep "Tentative" logs/security.log | wc -l

# Voir les IPs bloquées
grep "bloquée" logs/security.log | awk '{print $NF}' | sort | uniq -c

# Tentatives d'injection SQL
grep "injection SQL" logs/security.log
```

## 🧪 Tests de Sécurité

### 16. Scanner de vulnérabilités

```bash
# Installer safety
pip install safety

# Scanner les dépendances
safety check

# Scanner avec bandit
pip install bandit
bandit -r . -ll
```

### 17. Test de pénétration basique

```bash
# Installer OWASP ZAP ou utiliser en ligne
# https://www.zaproxy.org/

# Ou utiliser nikto
nikto -h https://votredomaine.com
```

## 📝 Checklist de Sécurité

Avant de mettre en production :

- [ ] DEBUG=False
- [ ] SECRET_KEY unique et sécurisée
- [ ] ENCRYPTION_KEY générée
- [ ] HTTPS configuré avec certificat SSL valide
- [ ] Base de données PostgreSQL avec mot de passe fort
- [ ] Firewall configuré (UFW ou iptables)
- [ ] Fail2Ban installé et configuré
- [ ] Sauvegardes automatiques configurées
- [ ] Logs activés et surveillés
- [ ] Toutes les dépendances à jour
- [ ] Tests de sécurité effectués
- [ ] Documentation à jour
- [ ] Équipe formée sur les bonnes pratiques

## 🆘 Dépannage

### Problème : "CSRF verification failed"

**Solution :**
1. Vérifier que `{% csrf_token %}` est présent dans tous les formulaires
2. Vérifier que les cookies sont activés
3. Vérifier `CSRF_COOKIE_SECURE` (False en développement)

### Problème : "Account locked"

**Solution :**
```bash
# Réinitialiser pour un utilisateur
python manage.py axes_reset username

# Réinitialiser pour une IP
python manage.py axes_reset_ip 192.168.1.1
```

### Problème : Erreur de chiffrement

**Solution :**
1. Vérifier que `ENCRYPTION_KEY` est définie dans `.env`
2. Régénérer la clé si nécessaire
3. Note : Les données chiffrées avec l'ancienne clé seront perdues

## 📞 Support

Pour toute question ou problème :
- Email : support@votreentreprise.com
- Documentation : Voir SECURITY.md

---

**Dernière mise à jour :** Octobre 2025
