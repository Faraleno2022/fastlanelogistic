from django.contrib import admin
from .models import Parametres


@admin.register(Parametres)
class ParametresAdmin(admin.ModelAdmin):
    list_display = ("societe_nom", "activite", "devise", "prix_carburant", "tarif_bauxite")
    fieldsets = (
        ("Société", {"fields": ("societe_nom", "activite", "devise")}),
        ("Amortissement", {"fields": ("duree_amortissement", "taux_residuel")}),
        ("Tarifs", {"fields": ("prix_carburant", "tarif_bauxite", "taux_tva", "jours_ouvres_mois")}),
    )

    def has_add_permission(self, request):
        return not Parametres.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
