# 🚀 Guide de Déploiement Sécurisé

## 📋 Prérequis

- Serveur Ubuntu 20.04+ ou Debian 11+
- Accès root ou sudo
- Nom de domaine configuré
- Certificat SSL (Let's Encrypt recommandé)

## 🔧 Installation du Serveur

### 1. Mise à jour du système

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx postgresql redis-server
```

### 2. Création de l'utilisateur applicatif

```bash
sudo adduser --disabled-password --gecos "" rhapp
sudo usermod -aG sudo rhapp
```

### 3. Configuration du firewall

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## 🗄️ Configuration de PostgreSQL

### 1. Créer la base de données

```bash
sudo -u postgres psql

CREATE DATABASE gestionnaire_rh_guinee;
CREATE USER rhuser WITH PASSWORD 'VotreMotDePasseTresFort123!';
ALTER ROLE rhuser SET client_encoding TO 'utf8';
ALTER ROLE rhuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE rhuser SET timezone TO 'Africa/Conakry';
GRANT ALL PRIVILEGES ON DATABASE gestionnaire_rh_guinee TO rhuser;
\q
```

### 2. Sécuriser PostgreSQL

Éditer `/etc/postgresql/*/main/pg_hba.conf` :

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

Redémarrer :

```bash
sudo systemctl restart postgresql
```

## 📦 Déploiement de l'Application

### 1. Cloner le projet

```bash
sudo su - rhapp
cd /home/rhapp
git clone https://github.com/Faraleno2022/guineerh.git
cd guineerh
```

### 2. Créer l'environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 3. Configurer les variables d'environnement

```bash
cp .env.example .env
nano .env
```

Configuration production :

```env
# Django
SECRET_KEY=VotreSecretKeyGenereeAvecLeScript
DEBUG=False
ALLOWED_HOSTS=votredomaine.com,www.votredomaine.com

# Database
DB_ENGINE=postgresql
DB_NAME=gestionnaire_rh_guinee
DB_USER=rhuser
DB_PASSWORD=VotreMotDePasseTresFort123!
DB_HOST=localhost
DB_PORT=5432

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Encryption
ENCRYPTION_KEY=VotreCleDeChiffrementGeneree

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (exemple avec Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Admin
ADMIN_EMAIL=admin@votredomaine.com

# Company
COMPANY_NAME=Votre Entreprise Guinée
COMPANY_NIF=123456789
COMPANY_CNSS=987654321
```

### 4. Préparer l'application

```bash
# Créer les répertoires
mkdir -p logs media staticfiles

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Appliquer les migrations
python manage.py migrate

# Créer le superutilisateur
python manage.py createsuperuser

# Initialiser les données de base
python manage.py init_database
```

## 🔒 Configuration de Gunicorn

### 1. Créer le fichier de configuration

```bash
nano /home/rhapp/guineerh/gunicorn_config.py
```

Contenu :

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = "/home/rhapp/guineerh/logs/gunicorn-access.log"
errorlog = "/home/rhapp/guineerh/logs/gunicorn-error.log"
loglevel = "info"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

### 2. Créer le service systemd

```bash
sudo nano /etc/systemd/system/guineerh.service
```

Contenu :

```ini
[Unit]
Description=Gestionnaire RH Guinée - Gunicorn
After=network.target

[Service]
Type=notify
User=rhapp
Group=rhapp
WorkingDirectory=/home/rhapp/guineerh
Environment="PATH=/home/rhapp/guineerh/venv/bin"
ExecStart=/home/rhapp/guineerh/venv/bin/gunicorn \
    --config /home/rhapp/guineerh/gunicorn_config.py \
    gestionnaire_rh.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 3. Activer et démarrer le service

```bash
sudo systemctl daemon-reload
sudo systemctl enable guineerh
sudo systemctl start guineerh
sudo systemctl status guineerh
```

## 🌐 Configuration de Nginx

### 1. Obtenir un certificat SSL

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votredomaine.com -d www.votredomaine.com
```

### 2. Configurer Nginx

```bash
sudo nano /etc/nginx/sites-available/guineerh
```

Contenu :

```nginx
# Redirection HTTP vers HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name votredomaine.com www.votredomaine.com;
    return 301 https://$server_name$request_uri;
}

# Configuration HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name votredomaine.com www.votredomaine.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/votredomaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votredomaine.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Logs
    access_log /var/log/nginx/guineerh-access.log;
    error_log /var/log/nginx/guineerh-error.log;

    # Client body size
    client_max_body_size 5M;

    # Static files
    location /static/ {
        alias /home/rhapp/guineerh/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/rhapp/guineerh/media/;
        expires 7d;
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }

    location ~ \.env$ {
        deny all;
    }
}
```

### 3. Activer la configuration

```bash
sudo ln -s /etc/nginx/sites-available/guineerh /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔐 Configuration de Fail2Ban

### 1. Installer Fail2Ban

```bash
sudo apt install fail2ban
```

### 2. Créer le filtre Django

```bash
sudo nano /etc/fail2ban/filter.d/django-auth.conf
```

Contenu :

```ini
[Definition]
failregex = ^.* Tentative .* depuis <HOST>
            ^.* bloquée pour IP .* <HOST>
ignoreregex =
```

### 3. Configurer la jail

```bash
sudo nano /etc/fail2ban/jail.local
```

Contenu :

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22

[nginx-http-auth]
enabled = true

[django-auth]
enabled = true
port = http,https
filter = django-auth
logpath = /home/rhapp/guineerh/logs/security.log
maxretry = 5
bantime = 3600
```

### 4. Redémarrer Fail2Ban

```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status
```

## 📊 Configuration des Sauvegardes

### 1. Script de sauvegarde

```bash
sudo nano /usr/local/bin/backup-guineerh.sh
```

Contenu :

```bash
#!/bin/bash

BACKUP_DIR="/backups/guineerh"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/rhapp/guineerh"

# Créer le répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
sudo -u postgres pg_dump gestionnaire_rh_guinee | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup des fichiers media
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" -C $APP_DIR media/

# Backup du fichier .env
cp $APP_DIR/.env "$BACKUP_DIR/env_$DATE.backup"

# Nettoyer les anciennes sauvegardes (garder 30 jours)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.backup" -mtime +30 -delete

echo "Sauvegarde terminée: $DATE"
```

### 2. Rendre le script exécutable

```bash
sudo chmod +x /usr/local/bin/backup-guineerh.sh
```

### 3. Ajouter au crontab

```bash
sudo crontab -e
```

Ajouter :

```
# Sauvegarde quotidienne à 2h du matin
0 2 * * * /usr/local/bin/backup-guineerh.sh >> /var/log/backup-guineerh.log 2>&1
```

## 🔍 Monitoring et Logs

### 1. Consulter les logs

```bash
# Logs de l'application
tail -f /home/rhapp/guineerh/logs/django.log
tail -f /home/rhapp/guineerh/logs/security.log

# Logs Gunicorn
tail -f /home/rhapp/guineerh/logs/gunicorn-error.log

# Logs Nginx
tail -f /var/log/nginx/guineerh-error.log

# Logs système
sudo journalctl -u guineerh -f
```

### 2. Rotation des logs

```bash
sudo nano /etc/logrotate.d/guineerh
```

Contenu :

```
/home/rhapp/guineerh/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 rhapp rhapp
    sharedscripts
    postrotate
        systemctl reload guineerh > /dev/null 2>&1 || true
    endscript
}
```

## 🔄 Mise à Jour de l'Application

```bash
# Se connecter en tant que rhapp
sudo su - rhapp
cd /home/rhapp/guineerh

# Activer l'environnement virtuel
source venv/bin/activate

# Récupérer les dernières modifications
git pull origin main

# Installer les nouvelles dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Appliquer les migrations
python manage.py migrate

# Redémarrer le service
sudo systemctl restart guineerh
```

## ✅ Checklist Post-Déploiement

- [ ] Application accessible via HTTPS
- [ ] Certificat SSL valide
- [ ] Redirection HTTP → HTTPS fonctionnelle
- [ ] Fichiers statiques chargés correctement
- [ ] Base de données connectée
- [ ] Admin Django accessible
- [ ] Logs fonctionnels
- [ ] Sauvegardes configurées
- [ ] Fail2Ban actif
- [ ] Firewall configuré
- [ ] Tests de sécurité effectués

## 🆘 Dépannage

### Service ne démarre pas

```bash
sudo journalctl -u guineerh -n 50
sudo systemctl status guineerh
```

### Erreur 502 Bad Gateway

```bash
# Vérifier que Gunicorn tourne
sudo systemctl status guineerh

# Vérifier les logs
tail -f /home/rhapp/guineerh/logs/gunicorn-error.log
```

### Problème de permissions

```bash
sudo chown -R rhapp:rhapp /home/rhapp/guineerh
sudo chmod -R 755 /home/rhapp/guineerh
```

---

**Dernière mise à jour :** Octobre 2025
