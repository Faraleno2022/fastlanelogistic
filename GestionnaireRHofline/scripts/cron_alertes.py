#!/usr/bin/env python
"""
Script pour exécuter les alertes RH automatiques.
À planifier avec le Planificateur de tâches Windows ou cron Linux.

Windows (Planificateur de tâches):
1. Ouvrir "Planificateur de tâches"
2. Créer une tâche de base
3. Nom: "GestionnaireRH - Alertes quotidiennes"
4. Déclencheur: Quotidien à 8h00
5. Action: Démarrer un programme
   - Programme: python
   - Arguments: C:\\Users\\LENO\\Desktop\\GestionnaireRH\\scripts\\cron_alertes.py
   - Démarrer dans: C:\\Users\\LENO\\Desktop\\GestionnaireRH

Linux (crontab -e):
# Alertes quotidiennes à 8h00
0 8 * * * cd /path/to/GestionnaireRH && python manage.py alertes_rh >> /var/log/rh_alertes.log 2>&1

# Notifications hebdomadaires (lundi 9h00)
0 9 * * 1 cd /path/to/GestionnaireRH && python manage.py envoyer_notifications >> /var/log/rh_notifications.log 2>&1
"""
import os
import sys
import django
from datetime import datetime

# Configurer le chemin Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionnaire_rh.settings')
django.setup()

from django.core.management import call_command


def executer_alertes():
    """Exécute les alertes RH"""
    print(f"[{datetime.now()}] Démarrage des alertes RH...")
    
    try:
        call_command('alertes_rh', '--type', 'all')
        print(f"[{datetime.now()}] Alertes terminées avec succès")
    except Exception as e:
        print(f"[{datetime.now()}] Erreur: {str(e)}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(executer_alertes())
