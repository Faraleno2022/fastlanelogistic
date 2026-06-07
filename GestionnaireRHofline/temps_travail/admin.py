from django.contrib import admin
from .models import (
    JourFerie, Conge, SoldeConge, Pointage, Absence,
    ArretTravail, HoraireTravail, AffectationHoraire
)


@admin.register(JourFerie)
class JourFerieAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'date_jour_ferie', 'annee', 'type_ferie', 'recurrent']
    list_filter = ['annee', 'type_ferie', 'recurrent']
    search_fields = ['libelle']
    ordering = ['-date_jour_ferie']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(entreprise=request.user.entreprise)


@admin.register(Conge)
class CongeAdmin(admin.ModelAdmin):
    list_display = ['employe', 'type_conge', 'date_debut', 'date_fin', 'nombre_jours', 'statut_demande']
    list_filter = ['type_conge', 'statut_demande', 'annee_reference']
    search_fields = ['employe__nom', 'employe__prenoms']
    readonly_fields = ['date_demande']
    ordering = ['-date_debut']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employe__entreprise=request.user.entreprise)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == 'employe':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(entreprise=request.user.entreprise)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(SoldeConge)
class SoldeCongeAdmin(admin.ModelAdmin):
    list_display = ['employe', 'annee', 'conges_acquis', 'conges_pris', 'conges_restants', 'conges_reports']
    list_filter = ['annee']
    search_fields = ['employe__nom', 'employe__prenoms']
    readonly_fields = ['date_mise_a_jour']
    ordering = ['-annee', 'employe__nom']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employe__entreprise=request.user.entreprise)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == 'employe':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(entreprise=request.user.entreprise)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Pointage)
class PointageAdmin(admin.ModelAdmin):
    list_display = ['employe', 'date_pointage', 'heure_entree', 'heure_sortie', 'heures_travaillees', 'heures_supplementaires', 'statut_pointage', 'valide']
    list_filter = ['statut_pointage', 'valide', 'date_pointage']
    search_fields = ['employe__nom', 'employe__prenoms']
    ordering = ['-date_pointage']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employe__entreprise=request.user.entreprise)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == 'employe':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(entreprise=request.user.entreprise)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ['employe', 'date_absence', 'type_absence', 'duree_jours', 'justifie', 'impact_paie']
    list_filter = ['type_absence', 'justifie', 'impact_paie']
    search_fields = ['employe__nom', 'employe__prenoms']
    ordering = ['-date_absence']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employe__entreprise=request.user.entreprise)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == 'employe':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(entreprise=request.user.entreprise)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ArretTravail)
class ArretTravailAdmin(admin.ModelAdmin):
    list_display = ['employe', 'type_arret', 'date_debut', 'date_fin', 'duree_jours', 'organisme_payeur', 'prolongation']
    list_filter = ['type_arret', 'organisme_payeur', 'prolongation']
    search_fields = ['employe__nom', 'employe__prenoms', 'numero_certificat']
    ordering = ['-date_debut']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employe__entreprise=request.user.entreprise)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == 'employe':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(entreprise=request.user.entreprise)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(HoraireTravail)
class HoraireTravailAdmin(admin.ModelAdmin):
    list_display = ['code_horaire', 'libelle_horaire', 'heure_debut', 'heure_fin', 'heures_jour', 'type_horaire', 'actif']
    list_filter = ['type_horaire', 'actif']
    search_fields = ['code_horaire', 'libelle_horaire']
    ordering = ['code_horaire']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(entreprise=request.user.entreprise)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not getattr(obj, 'entreprise_id', None):
            obj.entreprise = request.user.entreprise
        super().save_model(request, obj, form, change)


@admin.register(AffectationHoraire)
class AffectationHoraireAdmin(admin.ModelAdmin):
    list_display = ['employe', 'horaire', 'date_debut', 'date_fin', 'actif']
    list_filter = ['actif', 'horaire']
    search_fields = ['employe__nom', 'employe__prenoms']
    ordering = ['-date_debut']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            employe__entreprise=request.user.entreprise,
            horaire__entreprise=request.user.entreprise,
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == 'employe':
            kwargs['queryset'] = db_field.remote_field.model.objects.filter(entreprise=request.user.entreprise)
        if not request.user.is_superuser and db_field.name == 'horaire':
            kwargs['queryset'] = HoraireTravail.objects.filter(entreprise=request.user.entreprise)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
