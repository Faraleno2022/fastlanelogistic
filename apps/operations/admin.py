from django.contrib import admin
from .models import Carburant, Panne, DepenseAdmin, TransportBauxite, BonTransport


@admin.register(Carburant)
class CarburantAdmin(admin.ModelAdmin):
    list_display = ("date", "heure", "camion", "chauffeur",
                    "km_parcourus", "litres_pris", "consommation_100km",
                    "prix_unitaire", "montant_total", "station")
    list_filter = ("camion", "station", "date")
    search_fields = ("camion__code", "camion__immatriculation", "station")
    date_hierarchy = "date"
    autocomplete_fields = ("camion", "chauffeur")


@admin.register(Panne)
class PanneAdmin(admin.ModelAdmin):
    list_display = ("date", "camion", "type_panne", "piece_remplacee",
                    "cout_pieces", "cout_main_oeuvre", "cout_total",
                    "duree_immobilisation")
    list_filter = ("type_panne", "fournisseur", "date")
    search_fields = ("camion__code", "piece_remplacee", "fournisseur")
    date_hierarchy = "date"
    autocomplete_fields = ("camion",)


@admin.register(DepenseAdmin)
class DepenseAdminAdmin(admin.ModelAdmin):
    list_display = ("date", "camion", "type_depense", "description",
                    "montant", "echeance", "statut")
    list_filter = ("type_depense", "statut", "date")
    search_fields = ("description", "reference", "camion__code")
    date_hierarchy = "date"


@admin.register(TransportBauxite)
class TransportBauxiteAdmin(admin.ModelAdmin):
    list_display = ("date", "camion", "chauffeur", "trajet", "distance_km",
                    "tonnage", "tarif_unitaire", "chiffre_affaires",
                    "client", "num_bon")
    list_filter = ("client", "camion", "date")
    search_fields = ("camion__code", "num_bon", "trajet")
    date_hierarchy = "date"
    autocomplete_fields = ("camion", "chauffeur")


@admin.register(BonTransport)
class BonTransportAdmin(admin.ModelAdmin):
    list_display = ("num_bon", "date", "prenom", "nom", "plaque",
                    "lieu_chargement", "heure_depart", "heure_pesee_start",
                    "heure_pesee_end", "quantite")
    list_filter = ("lieu_chargement", "date")
    search_fields = ("num_bon", "plaque", "prenom", "nom")
    date_hierarchy = "date"
    autocomplete_fields = ("camion", "chauffeur")
