"""
Commande pour créer le tenant public (schéma public)
À exécuter une seule fois lors de l'initialisation du système
"""
from django.core.management.base import BaseCommand
from django.db import connection
from tenants.models import Client, Domain


class Command(BaseCommand):
    help = 'Crée le tenant public (schéma public) - À exécuter une seule fois'

    def add_arguments(self, parser):
        parser.add_argument('--domain', type=str, default='localhost', 
                          help='Domaine principal du système')

    def handle(self, *args, **options):
        domain_name = options['domain']
        
        # Vérifier si le tenant public existe déjà
        if Client.objects.filter(schema_name='public').exists():
            self.stdout.write(self.style.WARNING('Le tenant public existe déjà.'))
            return
        
        self.stdout.write("Création du tenant public...")
        
        try:
            # Créer le tenant public
            public_tenant = Client.objects.create(
                schema_name='public',
                nom_entreprise='Système GestionnaireRH',
                email='admin@guineerh.space',
                actif=True,
                plan_abonnement='entreprise'
            )
            
            # Créer le domaine principal
            Domain.objects.create(
                domain=domain_name,
                tenant=public_tenant,
                is_primary=True
            )
            
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Tenant public créé!"
                f"\n   Domaine: {domain_name}"
                f"\n"
                f"\n📋 Prochaines étapes:"
                f"\n   1. python manage.py migrate_schemas --shared"
                f"\n   2. python manage.py createsuperuser"
                f"\n   3. Créer des tenants via l'admin ou la commande create_tenant"
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur: {str(e)}"))
