"""
Commande pour mettre à jour les plans d'abonnement
"""
from django.core.management.base import BaseCommand
from payments.models import PlanAbonnement


class Command(BaseCommand):
    help = 'Met à jour les plans d\'abonnement avec les bons paramètres'

    def handle(self, *args, **options):
        self.stdout.write('📋 Mise à jour des plans d\'abonnement...')
        
        plans = [
            {
                'slug': 'gratuit',
                'nom': 'Gratuit',
                'description': 'Idéal pour découvrir la plateforme',
                'prix_mensuel': 0,
                'prix_annuel': 0,
                'max_utilisateurs': 1,
                'max_employes': 2,
                'module_paie': True,
                'module_conges': True,
                'module_recrutement': False,
                'module_formation': False,
                'support_prioritaire': False,
                'ordre': 1,
            },
            {
                'slug': 'basique',
                'nom': 'Basique',
                'description': 'Pour les petites entreprises',
                'prix_mensuel': 150000,
                'prix_annuel': 1500000,
                'max_utilisateurs': 5,
                'max_employes': 50,
                'module_paie': True,
                'module_conges': True,
                'module_recrutement': False,
                'module_formation': False,
                'support_prioritaire': False,
                'ordre': 2,
            },
            {
                'slug': 'premium',
                'nom': 'Premium',
                'description': 'Pour les entreprises en croissance',
                'prix_mensuel': 350000,
                'prix_annuel': 3500000,
                'max_utilisateurs': 15,
                'max_employes': 200,
                'module_paie': True,
                'module_conges': True,
                'module_recrutement': True,
                'module_formation': True,
                'support_prioritaire': True,
                'ordre': 3,
            },
            {
                'slug': 'entreprise',
                'nom': 'Entreprise',
                'description': 'Solution complète pour grandes entreprises',
                'prix_mensuel': 750000,
                'prix_annuel': 7500000,
                'max_utilisateurs': 50,
                'max_employes': 1000,
                'module_paie': True,
                'module_conges': True,
                'module_recrutement': True,
                'module_formation': True,
                'support_prioritaire': True,
                'ordre': 4,
            },
        ]
        
        for plan_data in plans:
            slug = plan_data.pop('slug')
            plan, created = PlanAbonnement.objects.update_or_create(
                slug=slug,
                defaults={**plan_data, 'actif': True}
            )
            action = 'créé' if created else 'mis à jour'
            self.stdout.write(f'  ✓ {plan.nom}: {action}')
        
        self.stdout.write(self.style.SUCCESS('✅ Plans mis à jour avec succès!'))
