"""
Modèles pour la gestion multi-tenant avec django-tenants
Chaque entreprise aura son propre schéma PostgreSQL
"""
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
import uuid


class Client(TenantMixin):
    """
    Modèle Tenant - Chaque entreprise est un tenant avec son propre schéma
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom_entreprise = models.CharField(max_length=200)
    nif = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='NIF')
    num_cnss = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='N° CNSS')
    adresse = models.TextField(blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    pays = models.CharField(max_length=50, default='Guinée')
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    logo = models.ImageField(upload_to='entreprises/logos/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateField(blank=True, null=True, help_text="Date d'expiration de l'abonnement")
    actif = models.BooleanField(default=True)
    plan_abonnement = models.CharField(max_length=50, default='gratuit', choices=[
        ('gratuit', 'Gratuit'),
        ('basique', 'Basique'),
        ('premium', 'Premium'),
        ('entreprise', 'Entreprise'),
    ])
    max_utilisateurs = models.IntegerField(default=5, help_text="Nombre maximum d'utilisateurs")
    
    # Champ requis par django-tenants pour créer le schéma automatiquement
    auto_create_schema = True
    auto_drop_schema = True  # Supprimer le schéma quand le tenant est supprimé
    
    class Meta:
        db_table = 'clients'
        verbose_name = 'Client (Entreprise)'
        verbose_name_plural = 'Clients (Entreprises)'
        ordering = ['nom_entreprise']
    
    def __str__(self):
        return self.nom_entreprise


class Domain(DomainMixin):
    """
    Domaines associés aux tenants
    Chaque tenant peut avoir plusieurs domaines (sous-domaines)
    Exemple: entreprise1.monapp.com, entreprise2.monapp.com
    """
    class Meta:
        db_table = 'domains'
        verbose_name = 'Domaine'
        verbose_name_plural = 'Domaines'
    
    def __str__(self):
        return self.domain
