"""
Service pour la création automatique de tenants (entreprises)
"""
from django.db import transaction
from django.utils.text import slugify
from django_tenants.utils import schema_context
from .models import Client, Domain
import uuid


class TenantProvisioningService:
    """
    Service pour provisionner automatiquement un nouveau tenant
    lors de l'inscription d'une entreprise
    """
    
    @staticmethod
    def create_tenant(
        nom_entreprise: str,
        email: str,
        admin_email: str,
        admin_password: str,
        admin_nom: str = '',
        admin_prenoms: str = '',
        telephone: str = None,
        adresse: str = None,
        ville: str = None,
        nif: str = None,
        num_cnss: str = None,
        plan_abonnement: str = 'gratuit',
        base_domain: str = 'localhost'
    ) -> tuple:
        """
        Crée un nouveau tenant avec son schéma et son utilisateur admin
        
        Returns:
            tuple: (client, domain, admin_user)
        """
        # Générer un schema_name unique basé sur le nom
        schema_name = slugify(nom_entreprise).replace('-', '_')[:50]
        
        # S'assurer que le schema_name est unique
        base_schema = schema_name
        counter = 1
        while Client.objects.filter(schema_name=schema_name).exists():
            schema_name = f"{base_schema}_{counter}"
            counter += 1
        
        with transaction.atomic():
            # 1. Créer le tenant (cela crée automatiquement le schéma PostgreSQL)
            client = Client.objects.create(
                nom_entreprise=nom_entreprise,
                schema_name=schema_name,
                email=email,
                telephone=telephone,
                adresse=adresse,
                ville=ville,
                nif=nif,
                num_cnss=num_cnss,
                plan_abonnement=plan_abonnement,
                actif=True
            )
            
            # 2. Créer le domaine pour ce tenant
            domain_name = f"{schema_name}.{base_domain}"
            domain = Domain.objects.create(
                domain=domain_name,
                tenant=client,
                is_primary=True
            )
            
            # 3. Créer l'utilisateur admin dans le schéma du tenant
            admin_user = None
            with schema_context(schema_name):
                from core.models import Utilisateur, ProfilUtilisateur
                
                # Créer le profil admin s'il n'existe pas
                profil_admin, _ = ProfilUtilisateur.objects.get_or_create(
                    nom_profil='Administrateur',
                    defaults={
                        'description': 'Administrateur de l\'entreprise',
                        'niveau_acces': 5,
                        'actif': True
                    }
                )
                
                # Créer l'utilisateur admin
                admin_user = Utilisateur.objects.create_user(
                    username=admin_email,
                    email=admin_email,
                    password=admin_password,
                    first_name=admin_prenoms,
                    last_name=admin_nom,
                    profil=profil_admin,
                    est_admin_entreprise=True,
                    is_staff=True,
                    actif=True
                )
                
                # Initialiser les données par défaut pour le tenant
                TenantProvisioningService._initialize_tenant_data(client)
        
        return client, domain, admin_user
    
    @staticmethod
    def _initialize_tenant_data(client):
        """
        Initialise les données par défaut pour un nouveau tenant
        (éléments de paie, types de congés, etc.)
        """
        from paie.models import ElementSalaire
        from temps_travail.models import TypeConge
        
        # Créer les éléments de salaire par défaut
        elements_defaut = [
            {'code': 'SAL_BASE', 'libelle': 'Salaire de base', 'type_element': 'gain', 'mode_calcul': 'fixe', 'imposable': True, 'cotisable': True, 'obligatoire': True, 'ordre': 1},
            {'code': 'PRIME_TRANSP', 'libelle': 'Prime de transport', 'type_element': 'gain', 'mode_calcul': 'fixe', 'imposable': False, 'cotisable': False, 'ordre': 10},
            {'code': 'PRIME_LOGE', 'libelle': 'Prime de logement', 'type_element': 'gain', 'mode_calcul': 'fixe', 'imposable': False, 'cotisable': False, 'ordre': 11},
            {'code': 'CNSS_EMP', 'libelle': 'CNSS Employé', 'type_element': 'retenue', 'mode_calcul': 'pourcentage', 'taux': 5.0, 'imposable': False, 'cotisable': True, 'obligatoire': True, 'ordre': 50},
            {'code': 'RTS', 'libelle': 'Retenue à la Source', 'type_element': 'retenue', 'mode_calcul': 'bareme', 'imposable': False, 'cotisable': False, 'obligatoire': True, 'ordre': 51},
        ]
        
        for elem in elements_defaut:
            ElementSalaire.objects.get_or_create(
                code=elem['code'],
                defaults=elem
            )
        
        # Créer les types de congés par défaut
        types_conges = [
            {'code': 'ANNUEL', 'libelle': 'Congé annuel', 'duree_max': 30, 'solde_initial': 30},
            {'code': 'MALADIE', 'libelle': 'Congé maladie', 'duree_max': 180, 'solde_initial': 0, 'justificatif_requis': True},
            {'code': 'MATERNITE', 'libelle': 'Congé maternité', 'duree_max': 98, 'solde_initial': 0},
            {'code': 'PATERNITE', 'libelle': 'Congé paternité', 'duree_max': 10, 'solde_initial': 0},
            {'code': 'DECES', 'libelle': 'Congé décès', 'duree_max': 5, 'solde_initial': 0},
            {'code': 'MARIAGE', 'libelle': 'Congé mariage', 'duree_max': 3, 'solde_initial': 0},
        ]
        
        for tc in types_conges:
            TypeConge.objects.get_or_create(
                code=tc['code'],
                defaults=tc
            )
    
    @staticmethod
    def delete_tenant(schema_name: str):
        """
        Supprime un tenant et son schéma
        """
        try:
            client = Client.objects.get(schema_name=schema_name)
            # La suppression du client supprimera automatiquement le schéma
            # grâce à auto_drop_schema = True
            client.delete()
            return True
        except Client.DoesNotExist:
            return False
    
    @staticmethod
    def suspend_tenant(schema_name: str):
        """
        Suspend un tenant (désactive l'accès)
        """
        try:
            client = Client.objects.get(schema_name=schema_name)
            client.actif = False
            client.save()
            return True
        except Client.DoesNotExist:
            return False
    
    @staticmethod
    def reactivate_tenant(schema_name: str):
        """
        Réactive un tenant suspendu
        """
        try:
            client = Client.objects.get(schema_name=schema_name)
            client.actif = True
            client.save()
            return True
        except Client.DoesNotExist:
            return False
