from django.contrib import admin
from .models import (
    PlanComptable, Journal, ExerciceComptable, EcritureComptable,
    LigneEcriture, Tiers, Facture, LigneFacture, Reglement, TauxTVA, PieceComptable
)


@admin.register(PlanComptable)
class PlanComptableAdmin(admin.ModelAdmin):
    list_display = ['numero_compte', 'intitule', 'classe', 'entreprise', 'est_actif']
    list_filter = ['classe', 'est_actif', 'entreprise']
    search_fields = ['numero_compte', 'intitule']
    ordering = ['numero_compte']


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['code', 'libelle', 'type_journal', 'entreprise', 'est_actif']
    list_filter = ['type_journal', 'est_actif', 'entreprise']
    search_fields = ['code', 'libelle']


@admin.register(ExerciceComptable)
class ExerciceComptableAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'date_debut', 'date_fin', 'statut', 'est_courant', 'entreprise']
    list_filter = ['statut', 'est_courant', 'entreprise']
    search_fields = ['libelle']


class LigneEcritureInline(admin.TabularInline):
    model = LigneEcriture
    extra = 2


@admin.register(EcritureComptable)
class EcritureComptableAdmin(admin.ModelAdmin):
    list_display = ['numero_ecriture', 'date_ecriture', 'libelle', 'journal', 'est_validee', 'entreprise']
    list_filter = ['est_validee', 'journal', 'entreprise']
    search_fields = ['numero_ecriture', 'libelle']
    inlines = [LigneEcritureInline]
    date_hierarchy = 'date_ecriture'


@admin.register(Tiers)
class TiersAdmin(admin.ModelAdmin):
    list_display = ['code', 'raison_sociale', 'type_tiers', 'telephone', 'est_actif', 'entreprise']
    list_filter = ['type_tiers', 'est_actif', 'entreprise']
    search_fields = ['code', 'raison_sociale', 'nif']


class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ['numero', 'type_facture', 'tiers', 'date_facture', 'montant_ttc', 'statut', 'entreprise']
    list_filter = ['type_facture', 'statut', 'entreprise']
    search_fields = ['numero', 'tiers__raison_sociale']
    inlines = [LigneFactureInline]
    date_hierarchy = 'date_facture'


@admin.register(Reglement)
class ReglementAdmin(admin.ModelAdmin):
    list_display = ['numero', 'facture', 'date_reglement', 'montant', 'mode_paiement', 'entreprise']
    list_filter = ['mode_paiement', 'entreprise']
    search_fields = ['numero', 'reference']
    date_hierarchy = 'date_reglement'


@admin.register(TauxTVA)
class TauxTVAAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'taux', 'nature', 'actif', 'date_debut']
    list_filter = ['nature', 'actif', 'regime_tva']


@admin.register(PieceComptable)
class PieceComptableAdmin(admin.ModelAdmin):
    list_display = ['numero', 'type_piece', 'date_piece', 'libelle', 'montant_ttc', 'entreprise']
    list_filter = ['type_piece', 'entreprise']
    search_fields = ['numero', 'libelle']
    date_hierarchy = 'date_piece'
