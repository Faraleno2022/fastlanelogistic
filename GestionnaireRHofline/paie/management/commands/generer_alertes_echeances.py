"""
Commande pour générer les alertes d'échéances de déclarations sociales.

Usage:
    python manage.py generer_alertes_echeances
    python manage.py generer_alertes_echeances --mois 12 --annee 2025
    python manage.py generer_alertes_echeances --actualiser
"""
from django.core.management.base import BaseCommand
from datetime import date
from paie.models import AlerteEcheance
from core.models import Entreprise


class Command(BaseCommand):
    help = 'Génère les alertes d\'échéances pour les déclarations sociales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mois',
            type=int,
            help='Mois de la période (1-12). Par défaut: mois en cours'
        )
        parser.add_argument(
            '--annee',
            type=int,
            help='Année de la période. Par défaut: année en cours'
        )
        parser.add_argument(
            '--actualiser',
            action='store_true',
            help='Actualiser toutes les alertes existantes'
        )
        parser.add_argument(
            '--entreprise',
            type=int,
            help='ID de l\'entreprise (par défaut: toutes)'
        )

    def handle(self, *args, **options):
        aujourd_hui = date.today()
        mois = options.get('mois') or aujourd_hui.month
        annee = options.get('annee') or aujourd_hui.year
        actualiser = options.get('actualiser', False)
        entreprise_id = options.get('entreprise')
        
        self.stdout.write(self.style.NOTICE('=' * 60))
        self.stdout.write(self.style.NOTICE('GÉNÉRATION DES ALERTES D\'ÉCHÉANCES'))
        self.stdout.write(self.style.NOTICE('=' * 60))
        
        # Récupérer les entreprises
        if entreprise_id:
            entreprises = Entreprise.objects.filter(id=entreprise_id)
        else:
            entreprises = Entreprise.objects.filter(actif=True)
        
        if not entreprises.exists():
            self.stdout.write(self.style.WARNING('Aucune entreprise trouvée.'))
            return
        
        total_alertes = 0
        
        for entreprise in entreprises:
            self.stdout.write(f'\n📊 Entreprise: {entreprise.nom_entreprise}')
            self.stdout.write('-' * 40)
            
            if actualiser:
                # Actualiser toutes les alertes existantes
                alertes = AlerteEcheance.objects.filter(
                    entreprise=entreprise,
                    statut__in=['a_venir', 'urgent', 'en_retard']
                )
                for alerte in alertes:
                    alerte.actualiser_statut()
                    self._afficher_alerte(alerte)
                    total_alertes += 1
            else:
                # Générer les alertes pour le mois spécifié
                alertes = AlerteEcheance.generer_alertes_mois(entreprise, annee, mois)
                for alerte in alertes:
                    self._afficher_alerte(alerte)
                    total_alertes += 1
        
        # Résumé
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS(f'✅ {total_alertes} alerte(s) générée(s)/actualisée(s)'))
        
        # Afficher les alertes urgentes
        alertes_urgentes = AlerteEcheance.objects.filter(
            statut__in=['urgent', 'en_retard']
        ).order_by('date_echeance')
        
        if alertes_urgentes.exists():
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('⚠️ ALERTES URGENTES:'))
            for alerte in alertes_urgentes:
                self._afficher_alerte(alerte)
        
        self.stdout.write('=' * 60)

    def _afficher_alerte(self, alerte):
        """Affiche une alerte avec le bon style"""
        if alerte.niveau_alerte == 'danger':
            style = self.style.ERROR
        elif alerte.niveau_alerte == 'warning':
            style = self.style.WARNING
        else:
            style = self.style.SUCCESS
        
        self.stdout.write(style(
            f'  {alerte.get_type_echeance_display():25} | '
            f'{alerte.mois:02d}/{alerte.annee} | '
            f'{alerte.get_statut_display():12} | '
            f'{alerte.jours_restants:+3d} jours'
        ))
