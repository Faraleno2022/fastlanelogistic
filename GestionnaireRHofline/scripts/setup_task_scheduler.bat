@echo off
REM Script pour configurer le Planificateur de tâches Windows
REM Exécuter en tant qu'administrateur

echo Configuration des tâches planifiées GestionnaireRH
echo ==================================================

REM Tâche quotidienne: Alertes RH à 8h00
schtasks /create /tn "GestionnaireRH\Alertes_Quotidiennes" /tr "python C:\Users\LENO\Desktop\GestionnaireRH\manage.py alertes_rh" /sc daily /st 08:00 /f

REM Tâche hebdomadaire: Notifications le lundi à 9h00
schtasks /create /tn "GestionnaireRH\Notifications_Hebdo" /tr "python C:\Users\LENO\Desktop\GestionnaireRH\manage.py envoyer_notifications" /sc weekly /d MON /st 09:00 /f

echo.
echo Tâches créées avec succès!
echo.
echo Pour vérifier: schtasks /query /tn "GestionnaireRH\*"
echo Pour supprimer: schtasks /delete /tn "GestionnaireRH\Alertes_Quotidiennes" /f

pause
