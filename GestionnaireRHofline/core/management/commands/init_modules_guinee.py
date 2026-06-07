"""
Commande pour initialiser les modules stratégiques Guinée
- Devises (GNF, USD, EUR)
- Taux de change
- Barème IRPP
- Déductions fiscales
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date

from core.models import (
    Devise, TauxChange, BaremeIRPP, DeductionFiscale,
    Entreprise
)


class Command(BaseCommand):
    help = 'Initialise les modules stratégiques pour la Guinée (devises, IRPP, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--annee',
            type=int,
            default=2025,
            help='Année pour le barème IRPP (défaut: 2025)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la réinitialisation même si les données existent'
        )

    def handle(self, *args, **options):
        annee = options['annee']
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🇬🇳 INITIALISATION MODULES STRATÉGIQUES GUINÉE'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # 1. Initialiser les devises
        self.init_devises(force)
        
        # 2. Initialiser les taux de change
        self.init_taux_change(force)
        
        # 3. Initialiser le barème IRPP
        self.init_bareme_irpp(annee, force)
        
        # 4. Initialiser les déductions fiscales
        self.init_deductions_fiscales(annee, force)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Initialisation terminée avec succès!'))

    def init_devises(self, force=False):
        """Initialise les devises principales"""
        self.stdout.write('\n📊 Initialisation des devises...')
        
        devises = [
            {'code': 'GNF', 'nom': 'Franc Guinéen', 'symbole': 'GNF', 'est_base': True},
            {'code': 'USD', 'nom': 'Dollar Américain', 'symbole': '$', 'est_base': False},
            {'code': 'EUR', 'nom': 'Euro', 'symbole': '€', 'est_base': False},
            {'code': 'XOF', 'nom': 'Franc CFA', 'symbole': 'FCFA', 'est_base': False},
        ]
        
        for dev in devises:
            devise, created = Devise.objects.update_or_create(
                code=dev['code'],
                defaults={
                    'nom': dev['nom'],
                    'symbole': dev['symbole'],
                    'est_devise_base': dev['est_base'],
                    'actif': True
                }
            )
            status = '✅ Créée' if created else '🔄 Mise à jour'
            self.stdout.write(f"  {status}: {devise.code} - {devise.nom}")

    def init_taux_change(self, force=False):
        """Initialise les taux de change par défaut"""
        self.stdout.write('\n💱 Initialisation des taux de change...')
        
        gnf = Devise.objects.get(code='GNF')
        usd = Devise.objects.get(code='USD')
        eur = Devise.objects.get(code='EUR')
        
        # Taux approximatifs (à mettre à jour régulièrement)
        taux_defaut = [
            {'source': usd, 'cible': gnf, 'taux': Decimal('8600.00')},  # 1 USD = 8600 GNF
            {'source': eur, 'cible': gnf, 'taux': Decimal('9400.00')},  # 1 EUR = 9400 GNF
            {'source': eur, 'cible': usd, 'taux': Decimal('1.09')},     # 1 EUR = 1.09 USD
        ]
        
        today = date.today()
        
        for taux in taux_defaut:
            obj, created = TauxChange.objects.update_or_create(
                devise_source=taux['source'],
                devise_cible=taux['cible'],
                date_taux=today,
                defaults={
                    'taux': taux['taux'],
                    'source': 'Initialisation système'
                }
            )
            status = '✅ Créé' if created else '🔄 Mis à jour'
            self.stdout.write(f"  {status}: 1 {taux['source'].code} = {taux['taux']} {taux['cible'].code}")

    def init_bareme_irpp(self, annee, force=False):
        """Initialise le barème IRPP progressif guinéen"""
        self.stdout.write(f'\n📈 Initialisation du barème IRPP {annee}...')
        
        # Vérifier si le barème existe déjà
        if not force and BaremeIRPP.objects.filter(annee=annee, entreprise__isnull=True).exists():
            self.stdout.write(self.style.WARNING(f'  ⚠ Barème {annee} existe déjà. Utilisez --force pour réinitialiser.'))
            return
        
        # Supprimer l'ancien barème si force
        if force:
            BaremeIRPP.objects.filter(annee=annee, entreprise__isnull=True).delete()
        
        # Barème IRPP Guinée 2025 (barème progressif)
        # Source: Code Général des Impôts de Guinée
        tranches = [
            {'numero': 1, 'min': 0, 'max': 1000000, 'taux': Decimal('0'), 'cumul': Decimal('0')},
            {'numero': 2, 'min': 1000000, 'max': 5000000, 'taux': Decimal('5'), 'cumul': Decimal('0')},
            {'numero': 3, 'min': 5000000, 'max': 10000000, 'taux': Decimal('10'), 'cumul': Decimal('200000')},
            {'numero': 4, 'min': 10000000, 'max': 20000000, 'taux': Decimal('15'), 'cumul': Decimal('700000')},
            {'numero': 5, 'min': 20000000, 'max': 50000000, 'taux': Decimal('20'), 'cumul': Decimal('2200000')},
            {'numero': 6, 'min': 50000000, 'max': None, 'taux': Decimal('25'), 'cumul': Decimal('8200000')},
        ]
        
        for tranche in tranches:
            BaremeIRPP.objects.create(
                entreprise=None,  # Barème global
                annee=annee,
                tranche_numero=tranche['numero'],
                revenu_min=Decimal(str(tranche['min'])),
                revenu_max=Decimal(str(tranche['max'])) if tranche['max'] else None,
                taux=tranche['taux'],
                montant_cumule_precedent=tranche['cumul'],
                actif=True
            )
            max_str = f"{tranche['max']:,}" if tranche['max'] else "∞"
            self.stdout.write(f"  ✅ Tranche {tranche['numero']}: {tranche['min']:,} - {max_str} GNF @ {tranche['taux']}%")

    def init_deductions_fiscales(self, annee, force=False):
        """Initialise les déductions fiscales"""
        self.stdout.write(f'\n👨‍👩‍👧‍👦 Initialisation des déductions fiscales {annee}...')
        
        # Vérifier si les déductions existent déjà
        if not force and DeductionFiscale.objects.filter(annee=annee, entreprise__isnull=True).exists():
            self.stdout.write(self.style.WARNING(f'  ⚠ Déductions {annee} existent déjà. Utilisez --force pour réinitialiser.'))
            return
        
        # Supprimer les anciennes déductions si force
        if force:
            DeductionFiscale.objects.filter(annee=annee, entreprise__isnull=True).delete()
        
        # Déductions fiscales Guinée
        deductions = [
            {
                'type': 'conjoint',
                'montant': Decimal('100000'),
                'plafond': None,
                'max': 1,
                'conditions': 'Conjoint à charge sans revenus propres'
            },
            {
                'type': 'enfant',
                'montant': Decimal('50000'),
                'plafond': Decimal('200000'),
                'max': 4,
                'conditions': 'Enfants à charge de moins de 21 ans ou étudiants de moins de 25 ans'
            },
            {
                'type': 'ascendant',
                'montant': Decimal('50000'),
                'plafond': Decimal('100000'),
                'max': 2,
                'conditions': 'Ascendants à charge sans ressources suffisantes'
            },
            {
                'type': 'handicap',
                'montant': Decimal('100000'),
                'plafond': None,
                'max': None,
                'conditions': 'Personne handicapée à charge avec certificat médical'
            },
        ]
        
        for ded in deductions:
            DeductionFiscale.objects.create(
                entreprise=None,  # Déduction globale
                annee=annee,
                type_deduction=ded['type'],
                montant_deduction=ded['montant'],
                plafond=ded['plafond'],
                nombre_max=ded['max'],
                conditions=ded['conditions'],
                actif=True
            )
            self.stdout.write(f"  ✅ {ded['type'].capitalize()}: {ded['montant']:,} GNF (max: {ded['max'] or 'illimité'})")
