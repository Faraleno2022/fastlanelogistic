"""
Commande pour créer un tenant (entreprise) avec son schéma PostgreSQL
"""
from django.core.management.base import BaseCommand
from tenants.services import TenantProvisioningService


class Command(BaseCommand):
    help = 'Crée un nouveau tenant (entreprise) avec son schéma et son admin'

    def add_arguments(self, parser):
        parser.add_argument('nom_entreprise', type=str, help='Nom de l\'entreprise')
        parser.add_argument('email', type=str, help='Email de l\'entreprise')
        parser.add_argument('admin_email', type=str, help='Email de l\'administrateur')
        parser.add_argument('admin_password', type=str, help='Mot de passe de l\'administrateur')
        parser.add_argument('--admin-nom', type=str, default='', help='Nom de l\'admin')
        parser.add_argument('--admin-prenoms', type=str, default='', help='Prénoms de l\'admin')
        parser.add_argument('--domain', type=str, default='localhost', help='Domaine de base')

    def handle(self, *args, **options):
        self.stdout.write(f"Création du tenant: {options['nom_entreprise']}...")
        
        try:
            client, domain, admin_user = TenantProvisioningService.create_tenant(
                nom_entreprise=options['nom_entreprise'],
                email=options['email'],
                admin_email=options['admin_email'],
                admin_password=options['admin_password'],
                admin_nom=options.get('admin_nom', ''),
                admin_prenoms=options.get('admin_prenoms', ''),
                base_domain=options.get('domain', 'localhost')
            )
            
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Tenant créé avec succès!"
                f"\n   Nom: {client.nom_entreprise}"
                f"\n   Schéma: {client.schema_name}"
                f"\n   Domaine: {domain.domain}"
                f"\n   Admin: {admin_user.email}"
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur: {str(e)}"))
