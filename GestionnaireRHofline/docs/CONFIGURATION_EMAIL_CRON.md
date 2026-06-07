# Configuration Email et Tâches Automatiques

## 1. Configuration SMTP (Email)

### Variables d'environnement (.env)

Créez ou modifiez le fichier `.env` à la racine du projet:

```env
# Configuration Email SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application
DEFAULT_FROM_EMAIL=noreply@guineerh.space
EMAIL_RH=rh@votre-entreprise.com
```

### Configuration Gmail

Pour utiliser Gmail:

1. Activez la **validation en deux étapes** sur votre compte Google
2. Générez un **mot de passe d'application**:
   - Allez sur https://myaccount.google.com/apppasswords
   - Sélectionnez "Mail" et "Ordinateur Windows"
   - Copiez le mot de passe généré (16 caractères)
3. Utilisez ce mot de passe dans `EMAIL_HOST_PASSWORD`

### Configuration autres fournisseurs

**Outlook/Office 365:**
```env
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

**OVH:**
```env
EMAIL_HOST=ssl0.ovh.net
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_USE_TLS=False
```

### Test de la configuration

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
send_mail(
    'Test GestionnaireRH',
    'Ceci est un test.',
    'noreply@guineerh.space',
    ['votre-email@example.com'],
)
```

---

## 2. Tâches Automatiques (Cron/Planificateur)

### Commandes disponibles

| Commande | Description |
|----------|-------------|
| `python manage.py alertes_rh` | Envoie toutes les alertes RH |
| `python manage.py alertes_rh --type contrats` | Alertes contrats uniquement |
| `python manage.py alertes_rh --dry-run` | Affiche sans envoyer |
| `python manage.py envoyer_notifications` | Notifications automatiques |

### Windows - Planificateur de tâches

#### Option 1: Script automatique

Exécutez en tant qu'administrateur:
```cmd
scripts\setup_task_scheduler.bat
```

#### Option 2: Configuration manuelle

1. Ouvrir **Planificateur de tâches** (taskschd.msc)
2. **Créer une tâche de base**
3. Configuration:
   - **Nom**: GestionnaireRH - Alertes quotidiennes
   - **Déclencheur**: Quotidien à 08:00
   - **Action**: Démarrer un programme
     - Programme: `python`
     - Arguments: `C:\Users\LENO\Desktop\GestionnaireRH\manage.py alertes_rh`
     - Démarrer dans: `C:\Users\LENO\Desktop\GestionnaireRH`

#### Vérifier les tâches

```cmd
schtasks /query /tn "GestionnaireRH\*"
```

### Linux - Crontab

```bash
crontab -e
```

Ajouter:
```cron
# Alertes RH quotidiennes à 8h00
0 8 * * * cd /path/to/GestionnaireRH && python manage.py alertes_rh >> /var/log/rh_alertes.log 2>&1

# Notifications hebdomadaires (lundi 9h00)
0 9 * * 1 cd /path/to/GestionnaireRH && python manage.py envoyer_notifications >> /var/log/rh_notifications.log 2>&1

# Vérification contrats expirant (tous les jours à 7h30)
30 7 * * * cd /path/to/GestionnaireRH && python manage.py alertes_rh --type contrats >> /var/log/rh_contrats.log 2>&1
```

### PythonAnywhere

Dans l'onglet **Tasks**:

| Heure | Commande |
|-------|----------|
| 08:00 | `cd /home/username/GestionnaireRH && python manage.py alertes_rh` |

---

## 3. Types d'alertes

### Alertes automatiques

| Type | Description | Fréquence recommandée |
|------|-------------|----------------------|
| `contrats` | Contrats expirant dans 30 jours | Quotidien |
| `conges` | Demandes de congés en attente | Quotidien |
| `prets` | Prêts en attente + échéances en retard | Quotidien |
| `visites` | Visites médicales à planifier | Hebdomadaire |
| `declarations` | Échéances CNSS/DMU | Quotidien |

### Exemple de sortie

```
=== Alertes RH (2025-12-28) ===

[CONTRATS]
  ⚠ Contrat de DIALLO Mamadou expire dans 5 jour(s) (2026-01-02)
  • Contrat de BARRY Fatoumata expire dans 25 jour(s) (2026-01-22)

[CONGÉS]
  • Demande de congé de SOW Ibrahima en attente depuis 2 jour(s)

[PRÊTS]
  ✓ Aucune alerte prêt

[VISITES MÉDICALES]
  • Visite médicale de CAMARA Aissatou à planifier dans 15 jour(s)

[DÉCLARATIONS]
  • Échéance CNSS dans 8 jour(s) (2026-01-15)

=== Résumé: 5 alerte(s) ===
Email envoyé à rh@entreprise.com
Terminé
```

---

## 4. Dépannage

### Emails non envoyés

1. Vérifiez les variables `.env`
2. Testez avec `--dry-run` d'abord
3. Consultez les logs: `logs/django.log`

### Tâche planifiée ne s'exécute pas

1. Vérifiez que Python est dans le PATH
2. Testez la commande manuellement
3. Vérifiez les permissions du dossier

### Logs

Les logs sont dans `logs/django.log` et incluent:
- Emails envoyés/échoués
- Erreurs de notifications
- Alertes générées
