"""
Commande pour générer les jours fériés légaux de Guinée.
Décret 2022/0526 - 12 jours fériés officiels
"""
from django.core.management.base import BaseCommand
from temps_travail.models import JourFerie
from core.models import Entreprise
from datetime import date


class Command(BaseCommand):
    help = 'Génère les jours fériés légaux de Guinée pour une année donnée'

    def add_arguments(self, parser):
        parser.add_argument(
            '--annee',
            type=int,
            default=2025,
            help='Année pour laquelle générer les jours fériés (défaut: 2025)'
        )
        parser.add_argument(
            '--entreprise',
            type=str,
            help='ID de l\'entreprise (optionnel, génère pour toutes si non spécifié)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Supprimer et recréer les jours fériés existants'
        )

    def handle(self, *args, **options):
        annee = options['annee']
        force = options['force']
        entreprise_id = options.get('entreprise')
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"GÉNÉRATION DES JOURS FÉRIÉS GUINÉE {annee}")
        self.stdout.write(f"{'='*60}\n")
        
        # Jours fériés fixes (dates constantes chaque année)
        feries_fixes = [
            ('Nouvel An', f'{annee}-01-01', 'national'),
            ('Jour de la Seconde République', f'{annee}-04-03', 'national'),
            ('Fête du Travail', f'{annee}-05-01', 'national'),
            ('Journée de l\'Afrique', f'{annee}-05-25', 'national'),
            ('Assomption', f'{annee}-08-15', 'religieux'),
            ('Fête de l\'Indépendance', f'{annee}-10-02', 'national'),
            ('Noël', f'{annee}-12-25', 'religieux'),
        ]
        
        # Jours fériés variables (dates religieuses - à ajuster chaque année)
        feries_variables = {
            2025: [
                ('Laylat al-Qadr (lendemain)', '2025-03-28', 'religieux'),
                ('Aïd el-Fitr', '2025-03-31', 'religieux'),
                ('Lundi de Pâques', '2025-04-21', 'religieux'),
                ('Aïd el-Adha (Tabaski)', '2025-06-07', 'religieux'),
                ('Maouloud (lendemain)', '2025-09-16', 'religieux'),
            ],
            2026: [
                ('Laylat al-Qadr (lendemain)', '2026-03-17', 'religieux'),
                ('Aïd el-Fitr', '2026-03-20', 'religieux'),
                ('Lundi de Pâques', '2026-04-06', 'religieux'),
                ('Aïd el-Adha (Tabaski)', '2026-05-27', 'religieux'),
                ('Maouloud (lendemain)', '2026-09-05', 'religieux'),
            ],
        }
        
        # Combiner les fériés
        feries = feries_fixes.copy()
        if annee in feries_variables:
            feries.extend(feries_variables[annee])
        else:
            self.stdout.write(self.style.WARNING(
                f"⚠ Dates variables non définies pour {annee}. "
                f"Seuls les jours fériés fixes seront créés."
            ))
        
        # Déterminer les entreprises
        if entreprise_id:
            entreprises = Entreprise.objects.filter(id=entreprise_id)
        else:
            entreprises = list(Entreprise.objects.all()) + [None]  # None = global
        
        total_crees = 0
        total_existants = 0
        
        for entreprise in entreprises:
            ent_nom = entreprise.nom_entreprise if entreprise else "Global"
            
            if force:
                # Supprimer les existants
                deleted, _ = JourFerie.objects.filter(
                    annee=annee,
                    entreprise=entreprise
                ).delete()
                if deleted:
                    self.stdout.write(f"  🗑 {deleted} jours fériés supprimés pour {ent_nom}")
            
            for libelle, date_str, type_ferie in feries:
                obj, created = JourFerie.objects.get_or_create(
                    libelle=libelle,
                    annee=annee,
                    entreprise=entreprise,
                    defaults={
                        'date_jour_ferie': date_str,
                        'type_ferie': type_ferie,
                        'recurrent': type_ferie == 'national',
                    }
                )
                
                if created:
                    total_crees += 1
                else:
                    total_existants += 1
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"✅ {total_crees} jours fériés créés"))
        if total_existants:
            self.stdout.write(f"ℹ {total_existants} jours fériés existaient déjà")
        
        # Afficher le calendrier
        self.stdout.write(f"\n📅 CALENDRIER DES JOURS FÉRIÉS {annee}:")
        self.stdout.write("-" * 50)
        
        for libelle, date_str, type_ferie in sorted(feries, key=lambda x: x[1]):
            type_icon = "🇬🇳" if type_ferie == 'national' else "🕌" if type_ferie == 'religieux' else "📍"
            self.stdout.write(f"  {type_icon} {date_str} - {libelle}")
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("ℹ Majoration si travaillé: +100% (double salaire)")
        self.stdout.write(f"{'='*60}\n")
