"""
Commande pour initialiser les devises
"""
from django.core.management.base import BaseCommand
from core.models import Devise


class Command(BaseCommand):
    help = 'Initialise les devises pour la Guinée'

    def handle(self, *args, **options):
        self.stdout.write('💱 Initialisation des devises...')
        
        devises = [
            {
                'code': 'GNF',
                'nom': 'Franc Guinéen',
                'symbole': 'GNF',
                'est_devise_base': True,
                'actif': True,
            },
            {
                'code': 'USD',
                'nom': 'Dollar Américain',
                'symbole': '$',
                'est_devise_base': False,
                'actif': True,
            },
            {
                'code': 'EUR',
                'nom': 'Euro',
                'symbole': '€',
                'est_devise_base': False,
                'actif': True,
            },
            {
                'code': 'XOF',
                'nom': 'Franc CFA (BCEAO)',
                'symbole': 'CFA',
                'est_devise_base': False,
                'actif': True,
            },
        ]
        
        for dev_data in devises:
            code = dev_data.pop('code')
            devise, created = Devise.objects.update_or_create(
                code=code,
                defaults=dev_data
            )
            action = 'créée' if created else 'mise à jour'
            self.stdout.write(f'  ✓ {devise.code} - {devise.nom}: {action}')
        
        self.stdout.write(self.style.SUCCESS('✅ Devises initialisées avec succès!'))
