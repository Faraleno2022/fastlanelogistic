from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Client, Domain


@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('nom_entreprise', 'schema_name', 'email', 'plan_abonnement', 'actif', 'date_creation')
    list_filter = ('plan_abonnement', 'actif', 'pays')
    search_fields = ('nom_entreprise', 'email', 'nif', 'num_cnss')
    readonly_fields = ('id', 'date_creation', 'schema_name')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'nom_entreprise', 'schema_name', 'logo')
        }),
        ('Coordonnées', {
            'fields': ('email', 'telephone', 'adresse', 'ville', 'pays')
        }),
        ('Identification fiscale', {
            'fields': ('nif', 'num_cnss')
        }),
        ('Abonnement', {
            'fields': ('plan_abonnement', 'max_utilisateurs', 'date_expiration', 'actif')
        }),
        ('Métadonnées', {
            'fields': ('date_creation',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain', 'tenant__nom_entreprise')
