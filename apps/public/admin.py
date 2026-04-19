from django.contrib import admin
from .models import Evenement, AppelOffre, PageAPropos


@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ("titre", "date_evenement", "lieu", "statut", "publie_le")
    list_filter = ("statut", "date_evenement")
    search_fields = ("titre", "lieu", "contenu")
    prepopulated_fields = {"slug": ("titre",)}
    date_hierarchy = "date_evenement"
    fieldsets = (
        (None, {"fields": ("titre", "slug", "date_evenement", "lieu", "image")}),
        ("Contenu", {"fields": ("resume", "contenu")}),
        ("Publication", {"fields": ("statut", "publie_le")}),
    )
    readonly_fields = ("publie_le",)


@admin.register(AppelOffre)
class AppelOffreAdmin(admin.ModelAdmin):
    list_display = ("reference", "titre", "date_publication", "date_limite",
                    "statut")
    list_filter = ("statut", "date_publication")
    search_fields = ("reference", "titre", "objet", "description")
    prepopulated_fields = {"slug": ("reference", "titre")}
    date_hierarchy = "date_publication"
    fieldsets = (
        (None, {"fields": ("reference", "titre", "slug", "statut")}),
        ("Objet", {"fields": ("objet", "description", "lieu_execution")}),
        ("Calendrier", {"fields": ("date_publication", "date_limite")}),
        ("Contact", {"fields": ("contact_email", "contact_telephone")}),
        ("Document", {"fields": ("document",)}),
    )


@admin.register(PageAPropos)
class PageAProposAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("titre", "presentation")}),
        ("Identité", {"fields": ("mission", "vision", "valeurs", "chiffres_cles")}),
        ("Coordonnées", {"fields": ("adresse", "email", "telephone")}),
    )

    def has_add_permission(self, request):
        # Singleton
        return not PageAPropos.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
