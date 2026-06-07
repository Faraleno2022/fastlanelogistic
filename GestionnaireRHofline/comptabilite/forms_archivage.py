"""
Formulaires pour le module Documentation & Archivage
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models_archivage import (
    ClassementDocument, PolitiqueRetention, ArchiveDocument,
    MatricePiecesJustificatives, ValidationDocument, SuppressionDocument,
    RapportArchivage
)


class ClassementDocumentForm(forms.ModelForm):
    """Formulaire pour les classements de documents"""
    
    class Meta:
        model = ClassementDocument
        fields = [
            'code', 'libelle', 'type_classement', 'description',
            'parent', 'duree_retention_annees', 'est_actif'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'libelle': forms.TextInput(attrs={'class': 'form-control'}),
            'type_classement': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'duree_retention_annees': forms.NumberInput(attrs={'class': 'form-control'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entreprise:
            self.fields['parent'].queryset = ClassementDocument.objects.filter(
                entreprise=entreprise, est_actif=True
            )


class PolitiqueRetentionForm(forms.ModelForm):
    """Formulaire pour les politiques de rétention"""
    
    class Meta:
        model = PolitiqueRetention
        fields = [
            'type_document', 'description', 'duree_conservation_annees',
            'base_legale', 'reference_legale', 'action_expiration',
            'alerte_avant_expiration_jours', 'est_actif'
        ]
        widgets = {
            'type_document': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duree_conservation_annees': forms.NumberInput(attrs={'class': 'form-control'}),
            'base_legale': forms.Select(attrs={'class': 'form-select'}),
            'reference_legale': forms.TextInput(attrs={'class': 'form-control'}),
            'action_expiration': forms.Select(attrs={'class': 'form-select'}),
            'alerte_avant_expiration_jours': forms.NumberInput(attrs={'class': 'form-control'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ArchiveDocumentForm(forms.ModelForm):
    """Formulaire pour les documents archivés"""
    
    class Meta:
        model = ArchiveDocument
        fields = [
            'classement', 'politique_retention', 'reference', 'titre',
            'description', 'fichier', 'format_fichier', 'date_document',
            'exercice', 'date_expiration', 'statut', 'niveau_confidentialite'
        ]
        widgets = {
            'classement': forms.Select(attrs={'class': 'form-select'}),
            'politique_retention': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
            'format_fichier': forms.Select(attrs={'class': 'form-select'}),
            'date_document': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'exercice': forms.Select(attrs={'class': 'form-select'}),
            'date_expiration': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'niveau_confidentialite': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entreprise:
            self.fields['classement'].queryset = ClassementDocument.objects.filter(
                entreprise=entreprise, est_actif=True
            )
            self.fields['politique_retention'].queryset = PolitiqueRetention.objects.filter(
                entreprise=entreprise, est_actif=True
            )


class MatricePiecesForm(forms.ModelForm):
    """Formulaire pour les matrices de pièces justificatives"""
    
    class Meta:
        model = MatricePiecesJustificatives
        fields = [
            'type_operation', 'description', 'seuil_montant',
            'validation_requise', 'niveaux_validation', 'est_actif'
        ]
        widgets = {
            'type_operation': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'seuil_montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'validation_requise': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'niveaux_validation': forms.NumberInput(attrs={'class': 'form-control'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ValidationDocumentForm(forms.ModelForm):
    """Formulaire pour les validations de documents"""
    
    class Meta:
        model = ValidationDocument
        fields = ['niveau_validation', 'statut', 'commentaire', 'motif_rejet']
        widgets = {
            'niveau_validation': forms.NumberInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'motif_rejet': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class SuppressionDocumentForm(forms.ModelForm):
    """Formulaire pour les demandes de suppression"""
    
    class Meta:
        model = SuppressionDocument
        fields = [
            'document', 'type_suppression', 'motif', 'reference_legale',
            'date_planifiee', 'statut'
        ]
        widgets = {
            'document': forms.Select(attrs={'class': 'form-select'}),
            'type_suppression': forms.Select(attrs={'class': 'form-select'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reference_legale': forms.TextInput(attrs={'class': 'form-control'}),
            'date_planifiee': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entreprise:
            self.fields['document'].queryset = ArchiveDocument.objects.filter(
                entreprise=entreprise
            ).exclude(statut='detruit')


class RapportArchivageForm(forms.ModelForm):
    """Formulaire pour les rapports d'archivage"""
    
    class Meta:
        model = RapportArchivage
        fields = ['type_rapport', 'titre', 'date_debut', 'date_fin', 'resume']
        widgets = {
            'type_rapport': forms.Select(attrs={'class': 'form-select'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resume': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
