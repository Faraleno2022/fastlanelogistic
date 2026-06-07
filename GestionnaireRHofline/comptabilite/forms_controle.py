"""Formulaires pour le module Contrôle Interne & Conformité."""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models_controle import (
    MatriceRisques,
    ProcedureControle,
    TestControle,
    NonConformite,
    DelegationPouvoirs,
    WorkflowApprobation,
    RapportControleInterne,
)


class MatriceRisquesForm(forms.ModelForm):
    """Formulaire pour la matrice des risques."""

    class Meta:
        model = MatriceRisques
        fields = [
            'reference', 'titre', 'description', 'categorie',
            'impact_inherent', 'probabilite_inherente',
            'impact_residuel', 'probabilite_residuelle',
            'processus', 'sous_processus', 'proprietaire',
            'statut', 'strategie_traitement', 'date_revue',
        ]
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'impact_inherent': forms.Select(attrs={'class': 'form-select'}),
            'probabilite_inherente': forms.Select(attrs={'class': 'form-select'}),
            'impact_residuel': forms.Select(attrs={'class': 'form-select'}),
            'probabilite_residuelle': forms.Select(attrs={'class': 'form-select'}),
            'processus': forms.TextInput(attrs={'class': 'form-control'}),
            'sous_processus': forms.TextInput(attrs={'class': 'form-control'}),
            'proprietaire': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'strategie_traitement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_revue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entreprise:
            self.fields['proprietaire'].queryset = entreprise.utilisateurs.filter(is_active=True)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.score_inherent = instance.impact_inherent * instance.probabilite_inherente
        if instance.impact_residuel and instance.probabilite_residuelle:
            instance.score_residuel = instance.impact_residuel * instance.probabilite_residuelle
        if commit:
            instance.save()
        return instance


class ProcedureControleForm(forms.ModelForm):
    """Formulaire pour les procédures de contrôle."""

    class Meta:
        model = ProcedureControle
        fields = [
            'code', 'titre', 'description', 'objectif',
            'type_controle', 'frequence', 'processus',
            'responsable', 'etapes_controle', 'documents_requis',
            'criteres_succes', 'statut', 'date_mise_en_vigueur',
            'prochaine_revue', 'version',
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'objectif': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'type_controle': forms.Select(attrs={'class': 'form-select'}),
            'frequence': forms.Select(attrs={'class': 'form-select'}),
            'processus': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'etapes_controle': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'documents_requis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'criteres_succes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'date_mise_en_vigueur': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'prochaine_revue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entreprise:
            self.fields['responsable'].queryset = entreprise.utilisateurs.filter(is_active=True)


class TestControleForm(forms.ModelForm):
    """Formulaire pour les tests de contrôle."""

    class Meta:
        model = TestControle
        fields = [
            'procedure', 'reference', 'titre', 'description',
            'type_test', 'date_execution', 'resultat', 'score',
            'observations', 'anomalies_detectees', 'recommandations',
        ]
        widgets = {
            'procedure': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'type_test': forms.Select(attrs={'class': 'form-select'}),
            'date_execution': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'resultat': forms.Select(attrs={'class': 'form-select'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'anomalies_detectees': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommandations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entreprise:
            self.fields['procedure'].queryset = ProcedureControle.objects.filter(entreprise=entreprise)


class NonConformiteForm(forms.ModelForm):
    """Formulaire pour les non-conformités."""

    class Meta:
        model = NonConformite
        fields = [
            'reference', 'titre', 'description',
            'niveau_gravite', 'origine', 'test', 'procedure', 'risque',
            'cause_racine', 'impact', 'actions_correctives', 'actions_preventives',
            'responsable_correction', 'date_echeance', 'statut', 'date_detection',
        ]
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'niveau_gravite': forms.Select(attrs={'class': 'form-select'}),
            'origine': forms.Select(attrs={'class': 'form-select'}),
            'test': forms.Select(attrs={'class': 'form-select'}),
            'procedure': forms.Select(attrs={'class': 'form-select'}),
            'risque': forms.Select(attrs={'class': 'form-select'}),
            'cause_racine': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'impact': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'actions_correctives': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'actions_preventives': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsable_correction': forms.Select(attrs={'class': 'form-select'}),
            'date_echeance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'date_detection': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entreprise:
            self.fields['responsable_correction'].queryset = entreprise.utilisateurs.filter(is_active=True)
            self.fields['procedure'].queryset = ProcedureControle.objects.filter(entreprise=entreprise)
            self.fields['risque'].queryset = MatriceRisques.objects.filter(entreprise=entreprise)
            self.fields['test'].queryset = TestControle.objects.filter(procedure__entreprise=entreprise)


class DelegationPouvoirsForm(forms.ModelForm):
    """Formulaire pour les délégations de pouvoirs."""

    class Meta:
        model = DelegationPouvoirs
        fields = [
            'delegant', 'delegataire', 'type_pouvoir', 'domaine',
            'description', 'montant_max', 'conditions',
            'date_debut', 'date_fin', 'statut',
        ]
        widgets = {
            'delegant': forms.Select(attrs={'class': 'form-select'}),
            'delegataire': forms.Select(attrs={'class': 'form-select'}),
            'type_pouvoir': forms.Select(attrs={'class': 'form-select'}),
            'domaine': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'montant_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entreprise:
            utilisateurs = entreprise.utilisateurs.filter(is_active=True)
            self.fields['delegant'].queryset = utilisateurs
            self.fields['delegataire'].queryset = utilisateurs


class RapportControleInterneForm(forms.ModelForm):
    """Formulaire pour les rapports de contrôle interne."""

    class Meta:
        model = RapportControleInterne
        fields = [
            'reference', 'titre', 'type_rapport',
            'date_debut_periode', 'date_fin_periode',
            'resume_executif', 'constats_principaux', 'recommandations',
            'plan_action', 'nb_tests_realises', 'nb_tests_reussis',
            'nb_non_conformites', 'taux_conformite', 'statut',
        ]
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'type_rapport': forms.Select(attrs={'class': 'form-select'}),
            'date_debut_periode': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin_periode': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resume_executif': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'constats_principaux': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'recommandations': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'plan_action': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nb_tests_realises': forms.NumberInput(attrs={'class': 'form-control'}),
            'nb_tests_reussis': forms.NumberInput(attrs={'class': 'form-control'}),
            'nb_non_conformites': forms.NumberInput(attrs={'class': 'form-control'}),
            'taux_conformite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
