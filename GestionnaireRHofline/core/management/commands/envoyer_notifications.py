"""
Commande de gestion pour envoyer les notifications automatiques.
Usage: python manage.py envoyer_notifications [--type TYPE]
"""
from django.core.management.base import BaseCommand
from core.notifications import NotificationContrat, NotificationAlerte
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Envoie les notifications automatiques (contrats expirant, échéances déclarations)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['contrats', 'declarations', 'all'],
            default='all',
            help='Type de notifications à envoyer'
        )
        parser.add_argument(
            '--jours',
            type=int,
            default=30,
            help='Nombre de jours avant expiration (défaut: 30)'
        )

    def handle(self, *args, **options):
        type_notif = options['type']
        jours = options['jours']
        
        self.stdout.write(self.style.NOTICE(f"Envoi des notifications ({type_notif})..."))
        
        if type_notif in ['contrats', 'all']:
            self.envoyer_alertes_contrats(jours)
        
        if type_notif in ['declarations', 'all']:
            self.envoyer_alertes_declarations()
        
        self.stdout.write(self.style.SUCCESS("Notifications envoyées avec succès"))

    def envoyer_alertes_contrats(self, jours):
        """Envoie les alertes pour les contrats expirant"""
        self.stdout.write(f"  - Vérification des contrats expirant dans {jours} jours...")
        
        result = NotificationContrat.notifier_contrats_expirant(jours_avant=jours)
        
        if result['total'] > 0:
            self.stdout.write(
                self.style.WARNING(f"    {result['total']} contrat(s) expirant, {result.get('envoyes', 0)} email(s) envoyé(s)")
            )
        else:
            self.stdout.write(self.style.SUCCESS("    Aucun contrat expirant"))

    def envoyer_alertes_declarations(self):
        """Envoie les alertes pour les échéances de déclarations"""
        from core.models import Entreprise
        
        self.stdout.write("  - Vérification des échéances de déclarations...")
        
        aujourd_hui = date.today()
        
        # CNSS: 15 du mois suivant
        if aujourd_hui.day >= 10:  # Alerter à partir du 10
            date_limite_cnss = date(aujourd_hui.year, aujourd_hui.month, 15)
            if aujourd_hui.month == 12:
                date_limite_cnss = date(aujourd_hui.year + 1, 1, 15)
            else:
                date_limite_cnss = date(aujourd_hui.year, aujourd_hui.month + 1, 15)
            
            jours_restants = (date_limite_cnss - aujourd_hui).days
            if jours_restants <= 10:
                for entreprise in Entreprise.objects.filter(actif=True):
                    NotificationAlerte.notifier_echeance_declaration(
                        'CNSS',
                        date_limite_cnss,
                        entreprise
                    )
                self.stdout.write(f"    Alerte CNSS envoyée (échéance: {date_limite_cnss})")
        
        # DMU: Fin du mois
        dernier_jour = date(
            aujourd_hui.year if aujourd_hui.month < 12 else aujourd_hui.year + 1,
            aujourd_hui.month + 1 if aujourd_hui.month < 12 else 1,
            1
        ) - timedelta(days=1)
        
        jours_restants = (dernier_jour - aujourd_hui).days
        if jours_restants <= 5:
            for entreprise in Entreprise.objects.filter(actif=True):
                NotificationAlerte.notifier_echeance_declaration(
                    'DMU/DNI',
                    dernier_jour,
                    entreprise
                )
            self.stdout.write(f"    Alerte DMU envoyée (échéance: {dernier_jour})")
        
        self.stdout.write(self.style.SUCCESS("    Vérification terminée"))
