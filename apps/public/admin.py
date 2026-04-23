from django.contrib import admin
from .models import Evenement, AppelOffre, PageAPropos, ContactMessage


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


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "nom", "entreprise", "sujet", "email",
                    "telephone", "traite")
    list_filter = ("traite", "sujet", "created_at")
    search_fields = ("nom", "entreprise", "email", "telephone", "message")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at", "ip", "user_agent")
    fieldsets = (
        ("Expéditeur", {"fields": ("nom", "entreprise", "email", "telephone")}),
        ("Demande", {"fields": ("sujet", "message")}),
        ("Traitement interne", {"fields": ("traite", "reponse_interne")}),
        ("Métadonnées", {
            "classes": ("collapse",),
            "fields": ("ip", "user_agent", "created_at", "updated_at"),
        }),
    )
    actions = ["marquer_traites"]

    def marquer_traites(self, request, queryset):
        n = queryset.update(traite=True)
        self.message_user(request, f"{n} message(s) marqué(s) comme traité(s).")
    marquer_traites.short_description = "Marquer comme traités"
