from django.contrib import admin
from .models import Camion


@admin.register(Camion)
class CamionAdmin(admin.ModelAdmin):
    list_display = ("code", "immatriculation", "marque_modele", "capacite_tonnes",
                    "prix_achat", "amortissement_mensuel", "statut")
    list_filter = ("statut", "marque_modele")
    search_fields = ("code", "immatriculation", "marque_modele")
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Identification", {"fields": ("code", "immatriculation", "marque_modele", "capacite_tonnes", "statut")}),
        ("Acquisition & amortissement", {"fields": ("date_acquisition", "prix_achat", "duree_amortissement")}),
        ("Traçabilité", {"fields": ("created_at", "updated_at")}),
    )
