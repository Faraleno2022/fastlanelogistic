"""
Commande pour initialiser les jours fériés guinéens
"""
from django.core.management.base import BaseCommand
from datetime import date
from temps_travail.models import JourFerie


class Command(BaseCommand):
    help = 'Initialise les jours fériés de la Guinée pour 2025'

    def add_arguments(self, parser):
        parser.add_argument(
            '--annee',
            type=int,
            default=2025,
            help='Année pour laquelle créer les jours fériés'
        )

    def handle(self, *args, **options):
        annee = options['annee']
        self.stdout.write(self.style.SUCCESS(f'🇬🇳 Initialisation des jours fériés Guinée {annee}...'))
        
        jours_feries = [
            # Jours fériés fixes
            {
                'libelle': 'Jour de l\'An',
                'date': date(annee, 1, 1),
                'type_ferie': 'national',
                'recurrent': True
            },
            {
                'libelle': 'Fête du Travail',
                'date': date(annee, 5, 1),
                'type_ferie': 'national',
                'recurrent': True
            },
            {
                'libelle': 'Fête de l\'Indépendance',
                'date': date(annee, 10, 2),
                'type_ferie': 'national',
                'recurrent': True
            },
            {
                'libelle': 'Jour de la République',
                'date': date(annee, 10, 2),
                'type_ferie': 'national',
                'recurrent': True
            },
            {
                'libelle': 'Noël',
                'date': date(annee, 12, 25),
                'type_ferie': 'national',
                'recurrent': True
            },
            
            # Fêtes religieuses musulmanes (dates approximatives pour 2025)
            # Note: Ces dates varient selon le calendrier lunaire
            {
                'libelle': 'Aïd el-Fitr (Fin du Ramadan)',
                'date': date(annee, 3, 30),  # Date approximative
                'type_ferie': 'religieux',
                'recurrent': False,
                'observations': 'Date à confirmer selon calendrier lunaire'
            },
            {
                'libelle': 'Aïd el-Kebir (Tabaski)',
                'date': date(annee, 6, 6),  # Date approximative
                'type_ferie': 'religieux',
                'recurrent': False,
                'observations': 'Date à confirmer selon calendrier lunaire'
            },
            {
                'libelle': 'Mawlid (Naissance du Prophète)',
                'date': date(annee, 9, 5),  # Date approximative
                'type_ferie': 'religieux',
                'recurrent': False,
                'observations': 'Date à confirmer selon calendrier lunaire'
            },
            
            # Fêtes chrétiennes
            {
                'libelle': 'Vendredi Saint',
                'date': date(annee, 4, 18),  # Date approximative pour 2025
                'type_ferie': 'religieux',
                'recurrent': False,
                'observations': 'Date à confirmer selon calendrier chrétien'
            },
            {
                'libelle': 'Lundi de Pâques',
                'date': date(annee, 4, 21),  # Date approximative pour 2025
                'type_ferie': 'religieux',
                'recurrent': False,
                'observations': 'Date à confirmer selon calendrier chrétien'
            },
            {
                'libelle': 'Assomption',
                'date': date(annee, 8, 15),
                'type_ferie': 'religieux',
                'recurrent': True
            },
        ]
        
        count_created = 0
        count_existing = 0
        
        for jour_data in jours_feries:
            jour, created = JourFerie.objects.get_or_create(
                date_jour_ferie=jour_data['date'],
                defaults={
                    'libelle': jour_data['libelle'],
                    'annee': annee,
                    'type_ferie': jour_data['type_ferie'],
                    'recurrent': jour_data['recurrent'],
                    'observations': jour_data.get('observations', '')
                }
            )
            
            if created:
                count_created += 1
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ {jour_data["libelle"]}: {jour_data["date"].strftime("%d/%m/%Y")}'
                ))
            else:
                count_existing += 1
                self.stdout.write(self.style.WARNING(
                    f'  ⚠ {jour_data["libelle"]}: déjà existant'
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Terminé: {count_created} jours fériés créés, {count_existing} déjà existants'
        ))
        self.stdout.write(self.style.WARNING(
            '\n⚠️  Note: Les dates des fêtes religieuses musulmanes et chrétiennes sont approximatives.'
        ))
        self.stdout.write(self.style.WARNING(
            '   Veuillez les vérifier et les ajuster selon le calendrier officiel.'
        ))
