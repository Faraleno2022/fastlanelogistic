from django.contrib import admin
from django.contrib import messages
from .models import Contrat, Facture


@admin.register(Contrat)
class ContratAdmin(admin.ModelAdmin):
    list_display = ("code", "client", "type_facturation", "tarif", "date_debut", "date_fin", "actif")
    list_filter = ("type_facturation", "actif", "client")
    search_fields = ("code", "client")


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ("numero", "contrat", "periode_mois", "periode_annee",
                    "tonnage_total", "montant_brut", "montant_ttc", "statut")
    list_filter = ("statut", "periode_annee", "contrat__client")
    search_fields = ("numero", "contrat__code", "contrat__client")
    date_hierarchy = "date_emission"
    actions = ["recalculer_action"]
    readonly_fields = ("montant_brut", "montant_ht", "tva", "montant_ttc",
                       "nb_bons", "nb_rotations", "tonnage_total", "distance_total")

    @admin.action(description="Recalculer les montants depuis les opérations")
    def recalculer_action(self, request, queryset):
        for f in queryset:
            f.recalculer()
            f.save()
        messages.success(request, f"{queryset.count()} facture(s) recalculée(s).")
