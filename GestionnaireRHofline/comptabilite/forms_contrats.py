"""
Formulaires pour le module Gestion Comptable des Contrats
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models_contrats_comptables import (
    ContratFournisseur, ContratClient, ConditionsPaiement,
    ConditionsLivraison, PointGaranti, PenaliteRetard,
    ReclamationContractuelle, AlerteContrat
)
from .models import Tiers


class ContratFournisseurForm(forms.ModelForm):
    """Formulaire pour les contrats fournisseurs"""
    
    class Meta:
        model = ContratFournisseur
        fields = [
            'fournisseur', 'numero_contrat', 'reference_externe', 'type_contrat',
            'objet', 'description', 'montant_total', 'montant_annuel', 'devise',
            'date_signature', 'date_debut', 'date_fin', 'duree_mois',
            'renouvellement_auto', 'preavis_resiliation_jours', 'statut',
            'responsable', 'document_contrat'
        ]
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'numero_contrat': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_externe': forms.TextInput(attrs={'class': 'form-control'}),
            'type_contrat': forms.Select(attrs={'class': 'form-select'}),
            'objet': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'montant_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'montant_annuel': forms.NumberInput(attrs={'class': 'form-control'}),
            'devise': forms.TextInput(attrs={'class': 'form-control', 'value': 'GNF'}),
            'date_signature': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duree_mois': forms.NumberInput(attrs={'class': 'form-control'}),
            'renouvellement_auto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'preavis_resiliation_jours': forms.NumberInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'document_contrat': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entreprise:
            self.fields['fournisseur'].queryset = Tiers.objects.filter(
                entreprise=entreprise, type_tiers='fournisseur', est_actif=True
            )


class ContratClientForm(forms.ModelForm):
    """Formulaire pour les contrats clients"""
    
    class Meta:
        model = ContratClient
        fields = [
            'client', 'numero_contrat', 'reference_client', 'type_contrat',
            'objet', 'description', 'montant_total', 'montant_annuel', 'devise',
            'date_signature', 'date_debut', 'date_fin', 'duree_mois',
            'renouvellement_auto', 'preavis_resiliation_jours', 'statut',
            'responsable', 'document_contrat'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'numero_contrat': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_client': forms.TextInput(attrs={'class': 'form-control'}),
            'type_contrat': forms.Select(attrs={'class': 'form-select'}),
            'objet': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'montant_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'montant_annuel': forms.NumberInput(attrs={'class': 'form-control'}),
            'devise': forms.TextInput(attrs={'class': 'form-control', 'value': 'GNF'}),
            'date_signature': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duree_mois': forms.NumberInput(attrs={'class': 'form-control'}),
            'renouvellement_auto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'preavis_resiliation_jours': forms.NumberInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'document_contrat': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entreprise:
            self.fields['client'].queryset = Tiers.objects.filter(
                entreprise=entreprise, type_tiers='client', est_actif=True
            )


class ConditionsPaiementForm(forms.ModelForm):
    """Formulaire pour les conditions de paiement"""
    
    class Meta:
        model = ConditionsPaiement
        fields = [
            'mode_paiement', 'echeance', 'delai_paiement_jours',
            'escompte_paiement_anticipe', 'delai_escompte_jours',
            'acompte_requis', 'pourcentage_acompte',
            'paiement_echelonne', 'nombre_echeances', 'conditions_speciales'
        ]
        widgets = {
            'mode_paiement': forms.Select(attrs={'class': 'form-select'}),
            'echeance': forms.Select(attrs={'class': 'form-select'}),
            'delai_paiement_jours': forms.NumberInput(attrs={'class': 'form-control'}),
            'escompte_paiement_anticipe': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'delai_escompte_jours': forms.NumberInput(attrs={'class': 'form-control'}),
            'acompte_requis': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pourcentage_acompte': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'paiement_echelonne': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nombre_echeances': forms.NumberInput(attrs={'class': 'form-control'}),
            'conditions_speciales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PointGarantiForm(forms.ModelForm):
    """Formulaire pour les garanties"""
    
    class Meta:
        model = PointGaranti
        fields = [
            'type_garantie', 'description', 'duree_garantie_mois',
            'date_debut_garantie', 'date_fin_garantie',
            'conditions_application', 'exclusions', 'montant_garanti'
        ]
        widgets = {
            'type_garantie': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duree_garantie_mois': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_debut_garantie': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin_garantie': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'conditions_application': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'exclusions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'montant_garanti': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PenaliteRetardForm(forms.ModelForm):
    """Formulaire pour les pénalités"""
    
    class Meta:
        model = PenaliteRetard
        fields = [
            'type_penalite', 'description', 'mode_calcul', 'taux', 'montant_fixe',
            'plafond_penalite', 'plafond_pourcentage', 'jours_franchise'
        ]
        widgets = {
            'type_penalite': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'mode_calcul': forms.Select(attrs={'class': 'form-select'}),
            'taux': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'montant_fixe': forms.NumberInput(attrs={'class': 'form-control'}),
            'plafond_penalite': forms.NumberInput(attrs={'class': 'form-control'}),
            'plafond_pourcentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'jours_franchise': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ReclamationContractuelleForm(forms.ModelForm):
    """Formulaire pour les réclamations"""
    
    class Meta:
        model = ReclamationContractuelle
        fields = [
            'numero_reclamation', 'type_reclamation', 'priorite',
            'objet', 'description', 'montant_reclame', 'montant_accorde',
            'date_reclamation', 'date_limite_reponse', 'date_resolution',
            'statut', 'resolution', 'responsable', 'pieces_jointes'
        ]
        widgets = {
            'numero_reclamation': forms.TextInput(attrs={'class': 'form-control'}),
            'type_reclamation': forms.Select(attrs={'class': 'form-select'}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'objet': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'montant_reclame': forms.NumberInput(attrs={'class': 'form-control'}),
            'montant_accorde': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_reclamation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_limite_reponse': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_resolution': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'resolution': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'pieces_jointes': forms.FileInput(attrs={'class': 'form-control'}),
        }


class AlerteContratForm(forms.ModelForm):
    """Formulaire pour les alertes"""
    
    class Meta:
        model = AlerteContrat
        fields = ['type_alerte', 'niveau', 'message', 'date_echeance', 'statut']
        widgets = {
            'type_alerte': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_echeance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
