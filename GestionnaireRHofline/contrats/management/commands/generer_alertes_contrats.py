from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from contrats.models import Contrat, AlerteContrat


class Command(BaseCommand):
    help = 'Génère automatiquement les alertes pour les contrats'

    def add_arguments(self, parser):
        parser.add_argument(
            '--jours-avant',
            type=int,
            default=30,
            help='Nombre de jours avant expiration pour générer l\'alerte'
        )

    def handle(self, *args, **options):
        jours_avant = options['jours_avant']
        date_limite = date.today() + timedelta(days=jours_avant)
        
        # Contrats expirant bientôt
        contrats_expirants = Contrat.objects.filter(
            statut='actif',
            date_fin__lte=date_limite,
            date_fin__gte=date.today()
        )
        
        alertes_creees = 0
        
        for contrat in contrats_expirants:
            # Vérifier si une alerte n'existe pas déjà
            alerte_existante = AlerteContrat.objects.filter(
                contrat=contrat,
                type_alerte='expiration',
                statut='active'
            ).exists()
            
            if not alerte_existante:
                jours_restants = (contrat.date_fin - date.today()).days
                
                AlerteContrat.objects.create(
                    contrat=contrat,
                    type_alerte='expiration',
                    titre=f'Expiration contrat dans {jours_restants} jours',
                    message=f'Le contrat {contrat.numero_contrat} de {contrat.employe.nom_complet} expire le {contrat.date_fin}',
                    date_alerte=date.today(),
                    date_echeance=contrat.date_fin
                )
                alertes_creees += 1
        
        # Fins de période d'essai
        contrats_fin_essai = Contrat.objects.filter(
            statut='actif',
            date_fin_periode_essai__lte=date_limite,
            date_fin_periode_essai__gte=date.today()
        )
        
        for contrat in contrats_fin_essai:
            alerte_existante = AlerteContrat.objects.filter(
                contrat=contrat,
                type_alerte='fin_essai',
                statut='active'
            ).exists()
            
            if not alerte_existante:
                jours_restants = (contrat.date_fin_periode_essai - date.today()).days
                
                AlerteContrat.objects.create(
                    contrat=contrat,
                    type_alerte='fin_essai',
                    titre=f'Fin période d\'essai dans {jours_restants} jours',
                    message=f'La période d\'essai de {contrat.employe.nom_complet} se termine le {contrat.date_fin_periode_essai}',
                    date_alerte=date.today(),
                    date_echeance=contrat.date_fin_periode_essai
                )
                alertes_creees += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'{alertes_creees} alertes créées avec succès')
        )
