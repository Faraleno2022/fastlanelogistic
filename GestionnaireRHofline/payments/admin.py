from django.contrib import admin
from .models import PlanAbonnement, Transaction, Abonnement


@admin.register(PlanAbonnement)
class PlanAbonnementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prix_mensuel', 'prix_annuel', 'max_utilisateurs', 'max_employes', 'actif', 'ordre']
    list_filter = ['actif', 'module_paie', 'module_recrutement', 'module_formation']
    search_fields = ['nom', 'slug', 'description']
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ['ordre', 'prix_mensuel']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['reference', 'entreprise', 'plan', 'montant', 'statut', 'methode_paiement', 'date_creation']
    list_filter = ['statut', 'type_transaction', 'methode_paiement', 'date_creation']
    search_fields = ['reference', 'entreprise__nom_entreprise', 'token_paydunya']
    readonly_fields = ['id', 'reference', 'date_creation', 'date_paiement']
    date_hierarchy = 'date_creation'
    ordering = ['-date_creation']


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ['entreprise', 'plan', 'date_debut', 'date_fin', 'statut', 'jours_restants']
    list_filter = ['statut', 'plan', 'auto_renouvellement']
    search_fields = ['entreprise__nom_entreprise']
    readonly_fields = ['date_creation', 'date_modification']
    
    def jours_restants(self, obj):
        return obj.jours_restants
    jours_restants.short_description = 'Jours restants'
