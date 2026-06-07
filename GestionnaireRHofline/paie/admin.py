from django.contrib import admin
from .models import (
    ParametrePaie, Constante, TrancheRTS, Variable,
    PeriodePaie, RubriquePaie, BulletinPaie, ElementSalaire,
    LigneBulletin, CumulPaie, HistoriquePaie, RegleIndemnite,
    DeclarationEtax
)


@admin.register(ParametrePaie)
class ParametrePaieAdmin(admin.ModelAdmin):
    list_display = ['mois_en_cours', 'annee_en_cours', 'devise', 'type_bulletin_defaut', 'type_paiement_defaut']
    fieldsets = (
        ('Période en cours', {
            'fields': ('mois_en_cours', 'annee_en_cours', 'date_debut_periode', 'date_fin_periode')
        }),
        ('Paramètres de calcul', {
            'fields': ('regulation_active', 'plafond_abattement_irg', 'taux_abattement_irg')
        }),
        ('Configuration', {
            'fields': ('type_bulletin_defaut', 'type_paiement_defaut', 'nombre_max_rubriques', 'devise')
        }),
        ('Acomptes', {
            'fields': ('acompte_regulier_actif', 'acompte_exceptionnel_actif', 'montant_max_acompte_pct')
        }),
        ('Gestion automatique', {
            'fields': ('suppression_auto_non_presents', 'conserver_historique_admin', 'duree_conservation_mois')
        }),
        ('Coordonnées société', {
            'fields': ('nom_societe', 'adresse_societe', 'telephone_societe', 'email_societe', 'nif_societe', 'num_cnss_employeur'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Constante)
class ConstanteAdmin(admin.ModelAdmin):
    list_display = ['code', 'libelle', 'valeur', 'unite', 'categorie', 'actif']
    list_filter = ['categorie', 'type_valeur', 'actif']
    search_fields = ['code', 'libelle']
    fieldsets = (
        (None, {
            'fields': ('code', 'libelle', 'description')
        }),
        ('Valeur', {
            'fields': ('valeur', 'type_valeur', 'unite', 'categorie')
        }),
        ('Validité', {
            'fields': ('date_debut_validite', 'date_fin_validite', 'actif')
        }),
    )


@admin.register(TrancheRTS)
class TrancheRTSAdmin(admin.ModelAdmin):
    list_display = ['numero_tranche', 'borne_inferieure', 'borne_superieure', 'taux_irg', 'annee_validite', 'actif']
    list_filter = ['annee_validite', 'actif']
    ordering = ['annee_validite', 'numero_tranche']


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ['code', 'libelle', 'type_variable', 'portee', 'valeur_defaut', 'actif']
    list_filter = ['type_variable', 'portee', 'actif']
    search_fields = ['code', 'libelle']


@admin.register(PeriodePaie)
class PeriodePaieAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'annee', 'mois', 'date_debut', 'date_fin', 'statut_periode', 'nombre_jours_travailles']
    list_filter = ['annee', 'statut_periode']
    ordering = ['-annee', '-mois']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(entreprise=request.user.entreprise)


@admin.register(RubriquePaie)
class RubriquePaieAdmin(admin.ModelAdmin):
    list_display = ['code_rubrique', 'libelle_rubrique', 'type_rubrique', 'taux_rubrique', 'montant_fixe', 'actif']
    list_filter = ['type_rubrique', 'soumis_cnss', 'soumis_irg', 'actif']
    search_fields = ['code_rubrique', 'libelle_rubrique']
    ordering = ['ordre_calcul']


class LigneBulletinInline(admin.TabularInline):
    model = LigneBulletin
    extra = 0
    readonly_fields = ['rubrique', 'base', 'taux', 'nombre', 'montant', 'ordre']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(BulletinPaie)
class BulletinPaieAdmin(admin.ModelAdmin):
    list_display = ['numero_bulletin', 'employe', 'periode', 'salaire_brut', 'net_a_payer', 'statut_bulletin']
    list_filter = ['annee_paie', 'mois_paie', 'statut_bulletin']
    search_fields = ['numero_bulletin', 'employe__nom', 'employe__prenoms']
    readonly_fields = ['date_calcul', 'numero_bulletin', 'salaire_brut', 'cnss_employe', 'irg', 'net_a_payer', 'cnss_employeur']
    ordering = ['-annee_paie', '-mois_paie']
    inlines = [LigneBulletinInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('numero_bulletin', 'employe', 'periode', 'statut_bulletin')
        }),
        ('Montants calculés', {
            'fields': ('salaire_brut', 'cnss_employe', 'irg', 'net_a_payer', 'cnss_employeur')
        }),
        ('Autres informations', {
            'fields': ('date_calcul', 'observations'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(periode__entreprise=request.user.entreprise)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == 'periode':
            kwargs['queryset'] = PeriodePaie.objects.filter(entreprise=request.user.entreprise)
        if not request.user.is_superuser and db_field.name == 'employe':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(entreprise=request.user.entreprise)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ElementSalaire)
class ElementSalaireAdmin(admin.ModelAdmin):
    list_display = ['employe', 'rubrique', 'montant', 'taux', 'actif', 'recurrent']
    list_filter = ['actif', 'recurrent', 'rubrique__type_rubrique']
    search_fields = ['employe__nom', 'employe__prenoms', 'employe__matricule', 'rubrique__libelle_rubrique']
    ordering = ['employe', 'rubrique__ordre_calcul']
    
    fieldsets = (
        ('Employé et rubrique', {
            'fields': ('employe', 'rubrique')
        }),
        ('Montant/Taux', {
            'fields': ('montant', 'taux', 'base_calcul')
        }),
        ('Validité', {
            'fields': ('date_debut', 'date_fin', 'actif', 'recurrent')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employe__entreprise=request.user.entreprise)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == 'employe':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(entreprise=request.user.entreprise)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(LigneBulletin)
class LigneBulletinAdmin(admin.ModelAdmin):
    list_display = ['bulletin', 'rubrique', 'base', 'taux', 'montant', 'ordre']
    list_filter = ['bulletin__periode', 'rubrique__type_rubrique']
    search_fields = ['bulletin__numero_bulletin', 'rubrique__libelle_rubrique']
    ordering = ['bulletin', 'ordre']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(bulletin__periode__entreprise=request.user.entreprise)


@admin.register(CumulPaie)
class CumulPaieAdmin(admin.ModelAdmin):
    list_display = ['employe', 'annee', 'cumul_brut', 'cumul_net', 'cumul_irg', 'nombre_bulletins']
    list_filter = ['annee']
    search_fields = ['employe__nom', 'employe__prenoms', 'employe__matricule']
    readonly_fields = ['date_creation', 'date_mise_a_jour']
    ordering = ['-annee', 'employe']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employe__entreprise=request.user.entreprise)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == 'employe':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(entreprise=request.user.entreprise)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(HistoriquePaie)
class HistoriquePaieAdmin(admin.ModelAdmin):
    list_display = ['type_action', 'employe', 'periode', 'utilisateur', 'date_action']
    list_filter = ['type_action', 'date_action']
    search_fields = ['employe__nom', 'employe__prenoms', 'description']
    readonly_fields = ['date_action', 'utilisateur', 'adresse_ip']
    ordering = ['-date_action']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(periode__entreprise=request.user.entreprise)


@admin.register(RegleIndemnite)
class RegleIndemniteAdmin(admin.ModelAdmin):
    list_display = ['entreprise', 'type_indemnite', 'categorie_employe', 'seuil_min_pct', 'seuil_max_pct', 'actif']
    list_filter = ['type_indemnite', 'categorie_employe', 'actif']
    search_fields = ['type_indemnite']
    ordering = ['entreprise', 'type_indemnite', 'categorie_employe']

    fieldsets = (
        ('Règle', {
            'fields': ('entreprise', 'type_indemnite', 'categorie_employe')
        }),
        ('Seuils', {
            'fields': ('seuil_min_pct', 'seuil_max_pct')
        }),
        ('Options', {
            'fields': ('justification_requise', 'actif')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(entreprise=request.user.entreprise)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == 'entreprise':
            from core.models import Entreprise
            kwargs['queryset'] = Entreprise.objects.filter(pk=request.user.entreprise_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(DeclarationEtax)
class DeclarationEtaxAdmin(admin.ModelAdmin):
    list_display = ['reference', 'entreprise', 'mois', 'annee', 'statut', 'total_fiscal', 'reference_etax']
    list_filter = ['statut', 'annee', 'mois']
    search_fields = ['reference', 'reference_etax', 'entreprise__nom_entreprise']
    readonly_fields = [
        'reference', 'effectif_declare', 'total_brut', 'total_net', 'total_base_rts',
        'total_rts', 'total_vf', 'total_ta', 'total_onfpp', 'total_fiscal',
        'total_cnss_employe', 'total_cnss_employeur', 'total_cnss', 'total_general',
        'date_generation', 'date_creation', 'date_modification'
    ]
    ordering = ['-annee', '-mois']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(entreprise=request.user.entreprise)
