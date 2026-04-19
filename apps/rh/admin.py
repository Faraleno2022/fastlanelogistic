from django.contrib import admin
from .models import Employe, Attendance, HeureSup


@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ("code", "prenom", "nom", "fonction", "telephone",
                    "site_prestation", "camion", "salaire_jour", "actif")
    list_filter = ("fonction", "site_prestation", "actif")
    search_fields = ("code", "prenom", "nom", "telephone")
    ordering = ("code",)
    autocomplete_fields = ("camion",)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("date", "employe", "code", "commentaire")
    list_filter = ("code", "date", "employe__fonction")
    search_fields = ("employe__code", "employe__prenom", "employe__nom")
    date_hierarchy = "date"
    autocomplete_fields = ("employe",)


@admin.register(HeureSup)
class HeureSupAdmin(admin.ModelAdmin):
    list_display = ("date", "employe", "heure_debut", "heure_fin",
                    "nb_heures", "type_hs", "majoration", "montant")
    list_filter = ("type_hs", "date")
    search_fields = ("employe__code", "employe__nom", "motif")
    date_hierarchy = "date"
    autocomplete_fields = ("employe",)
