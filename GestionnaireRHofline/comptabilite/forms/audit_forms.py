"""
Formulaires pour la gestion de l'audit et de la conformité.

Fournissent:
- Formulaires pour les rapports d'audit
- Formulaires pour les alertes
- Formulaires pour les règles de conformité
- Formulaires de filtrage
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from ..models import (
    RapportAudit, AlerteNonConformite, ReglesConformite
)
from .base import ComptaBaseForm

logger = __import__('logging').getLogger(__name__)


# ============================================================================
# RAPPORT AUDIT FORMS
# ============================================================================

class RapportAuditForm(ComptaBaseForm):
    """Formulaire pour la création/édition de rapports d'audit."""
    
    class Meta:
        model = RapportAudit
        fields = [
            'code', 'titre', 'description',
            'date_debut', 'date_fin',
            'objectifs', 'perimetre',
            'resultats', 'conclusion', 'recommandations',
            'statut', 'niveau_risque_global'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'placeholder': 'ex: AUDIT_2026_001',
                'class': 'form-control',
                'maxlength': '50'
            }),
            'titre': forms.TextInput(attrs={
                'placeholder': 'Titre du rapport d\'audit',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Description du rapport',
                'class': 'form-control',
            }),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'objectifs': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Objectifs de l\'audit',
                'class': 'form-control',
            }),
            'perimetre': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Périmètre de l\'audit',
                'class': 'form-control',
            }),
            'resultats': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Résultats de l\'audit',
                'class': 'form-control',
            }),
            'conclusion': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Conclusion',
                'class': 'form-control',
            }),
            'recommandations': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Recommandations',
                'class': 'form-control',
            }),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'niveau_risque_global': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_code(self):
        """Valide que le code est unique."""
        code = self.cleaned_data.get('code')
        if not code:
            return code
        
        qs = RapportAudit.objects.filter(code=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise ValidationError(_("Un rapport avec ce code existe déjà"))
        return code
    
    def clean(self):
        """Valide les dates."""
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        if date_debut and date_fin and date_fin < date_debut:
            raise ValidationError(
                _("La date de fin doit être après la date de début")
            )
        
        return cleaned_data


# ============================================================================
# ALERTE NON-CONFORMITÉ FORMS
# ============================================================================

class AlerteNonConformiteForm(ComptaBaseForm):
    """Formulaire pour la création/édition d'alertes de non-conformité."""
    
    class Meta:
        model = AlerteNonConformite
        fields = [
            'rapport', 'numero_alerte', 'titre', 'description',
            'severite', 'domaine',
            'plan_action', 'date_correction_prevue',
            'date_correction_reelle', 'statut',
            'responsable_correction', 'observations'
        ]
        widgets = {
            'rapport': forms.Select(attrs={'class': 'form-control'}),
            'numero_alerte': forms.TextInput(attrs={
                'placeholder': 'ex: ALR-2026-001',
                'class': 'form-control',
                'maxlength': '50'
            }),
            'titre': forms.TextInput(attrs={
                'placeholder': 'Titre de l\'alerte',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Description détaillée de l\'anomalie',
                'class': 'form-control',
            }),
            'severite': forms.Select(attrs={'class': 'form-control'}),
            'domaine': forms.TextInput(attrs={
                'placeholder': 'ex: TVA, Comptabilité, Paie',
                'class': 'form-control',
            }),
            'plan_action': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Plan d\'action pour corriger l\'anomalie',
                'class': 'form-control',
            }),
            'date_correction_prevue': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'date_correction_reelle': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'responsable_correction': forms.Select(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Observations supplémentaires',
                'class': 'form-control',
            }),
        }
    
    def clean(self):
        """Valide les dates."""
        cleaned_data = super().clean()
        date_prevue = cleaned_data.get('date_correction_prevue')
        date_reelle = cleaned_data.get('date_correction_reelle')
        
        if date_prevue and date_reelle and date_reelle < date_prevue:
            raise ValidationError(
                _("La date réelle doit être après la date prévue")
            )
        
        return cleaned_data


# ============================================================================
# RÈGLES CONFORMITÉ FORMS
# ============================================================================

class ReglesConformiteForm(ComptaBaseForm):
    """Formulaire pour la création/édition de règles de conformité."""
    
    class Meta:
        model = ReglesConformite
        fields = [
            'code', 'nom', 'description',
            'critere_conformite', 'consequence_non_conformite',
            'documentation_requise',
            'periodicite', 'module_concerne', 'criticite',
            'actif'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'placeholder': 'ex: CONF_TVA_001',
                'class': 'form-control',
                'maxlength': '50'
            }),
            'nom': forms.TextInput(attrs={
                'placeholder': 'Nom de la règle',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Description générale',
                'class': 'form-control',
            }),
            'critere_conformite': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Critère exact à vérifier',
                'class': 'form-control',
            }),
            'consequence_non_conformite': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Conséquences de la non-conformité',
                'class': 'form-control',
            }),
            'documentation_requise': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Documentation requise (optionnel)',
                'class': 'form-control',
            }),
            'periodicite': forms.Select(attrs={'class': 'form-control'}),
            'module_concerne': forms.TextInput(attrs={
                'placeholder': 'ex: TVA, Comptabilité, Paie',
                'class': 'form-control',
            }),
            'criticite': forms.Select(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_code(self):
        """Valide que le code est unique."""
        code = self.cleaned_data.get('code')
        if not code:
            return code
        
        qs = ReglesConformite.objects.filter(code=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise ValidationError(_("Une règle avec ce code existe déjà"))
        return code


# ============================================================================
# FORMULAIRES DE VÉRIFICATION & FILTRAGE
# ============================================================================

class ConformiteCheckForm(forms.Form):
    """Formulaire pour lancer une vérification de conformité."""
    
    modules = forms.MultipleChoiceField(
        label=_("Modules à vérifier"),
        choices=[
            ('TVA', 'TVA'),
            ('COMPTABILITE', 'Comptabilité'),
            ('PAIE', 'Paie'),
            ('TOUS', 'Tous les modules'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        initial=['TOUS']
    )
    
    inclure_regles_inactives = forms.BooleanField(
        label=_("Inclure les règles inactives"),
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    generer_rapport = forms.BooleanField(
        label=_("Générer un rapport"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class RapportAuditFilterForm(forms.Form):
    """Formulaire pour filtrer les rapports d'audit."""
    
    statut = forms.ChoiceField(
        label=_("Statut"),
        choices=[('', '--- Tous les statuts ---')] + list(RapportAudit.STATUT_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_depuis = forms.DateField(
        label=_("À partir du"),
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    date_jusqu_au = forms.DateField(
        label=_("Jusqu'au"),
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    recherche = forms.CharField(
        label=_("Rechercher"),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Code ou titre...',
            'class': 'form-control'
        })
    )
    
    def clean(self):
        """Valide les dates."""
        cleaned_data = super().clean()
        date_depuis = cleaned_data.get('date_depuis')
        date_jusqu_au = cleaned_data.get('date_jusqu_au')
        
        if date_depuis and date_jusqu_au and date_jusqu_au < date_depuis:
            raise ValidationError(
                _("La date de fin doit être après la date de début")
            )
        
        return cleaned_data


class AlerteFilterForm(forms.Form):
    """Formulaire pour filtrer les alertes."""
    
    severite = forms.ChoiceField(
        label=_("Sévérité"),
        choices=[('', '--- Toutes les sévérités ---')] + list(AlerteNonConformite.SEVERITE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    statut = forms.ChoiceField(
        label=_("Statut"),
        choices=[('', '--- Tous les statuts ---')] + list(AlerteNonConformite.STATUT_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    domaine = forms.CharField(
        label=_("Domaine"),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'TVA, Comptabilité, etc.',
            'class': 'form-control'
        })
    )
    
    date_depuis = forms.DateField(
        label=_("À partir du"),
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
