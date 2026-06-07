"""
Formulaires réutilisables pour la comptabilité.

Fournissent:
- Validation par service layer
- Widgets standardisés
- Messages d'erreur clairs
- Support multi-entreprise
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class ComptaBaseForm(forms.ModelForm):
    """Formulaire de base pour tous les modèles comptables."""
    
    class Meta:
        abstract = True
        fields = '__all__'
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.service = None
        
        # Style Bootstrap
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def get_service(self):
        """Retourne le service associé (à override par subclass)."""
        return self.service
    
    def clean(self):
        """Validation générale du formulaire."""
        cleaned_data = super().clean()
        
        # Validation par service si disponible
        if self.service:
            try:
                # À implémenter par subclass
                pass
            except Exception as e:
                raise ValidationError(f"Erreur de validation: {e}")
        
        return cleaned_data


class DecimalMoneyField(forms.DecimalField):
    """Champ décimal pour les montants en devises."""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('max_digits', 12)
        super().__init__(*args, **kwargs)
    
    def prepare_value(self, value):
        if value is None:
            return None
        try:
            return f"{Decimal(str(value)):.2f}"
        except Exception:
            return value


class CompteBancaireForm(ComptaBaseForm):
    """Formulaire pour la création/édition de comptes bancaires."""
    
    solde_initial = DecimalMoneyField(
        label=_("Solde initial"),
        required=False,
        help_text=_("Solde du compte à sa création")
    )
    
    class Meta:
        from ..models import CompteBancaire
        model = CompteBancaire
        fields = ['code', 'libelle', 'iban', 'bic', 'banque',
                  'solde_initial', 'compte_comptable', 'est_actif']
        widgets = {
            'numero_compte': forms.TextInput(attrs={
                'placeholder': '00123456789',
                'pattern': '[0-9]{11,}'
            }),
            'iban': forms.TextInput(attrs={
                'placeholder': 'FR1420041010050500013M02606',
                'pattern': '[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}'
            }),
            'bic': forms.TextInput(attrs={
                'placeholder': 'BNPAFRPP',
                'pattern': '[A-Z0-9]{8,11}'
            }),
            'intitule_tiers': forms.TextInput(),
            'devise': forms.Select(),
            'tiers': forms.Select(),
            'actif': forms.CheckboxInput(),
        }
    
    def clean_numero_compte(self):
        """Valide le format du numéro de compte."""
        numero = self.cleaned_data.get('numero_compte')
        if numero and not numero.isdigit():
            raise ValidationError(_("Le numéro de compte doit contenir uniquement des chiffres"))
        return numero
    
    def clean_iban(self):
        """Valide le format IBAN."""
        iban = self.cleaned_data.get('iban')
        if iban:
            iban = iban.replace(' ', '')
            if len(iban) < 15 or len(iban) > 34:
                raise ValidationError(_("L'IBAN doit contenir entre 15 et 34 caractères"))
            if not iban[2:4].isdigit():
                raise ValidationError(_("Les positions 3-4 de l'IBAN doivent être des chiffres"))
        return iban


class RapprochementBancaireForm(ComptaBaseForm):
    """Formulaire pour la création/édition de rapprochements."""
    
    solde_comptable = DecimalMoneyField(
        label=_("Solde comptable"),
        required=True,
        help_text=_("Solde au débit du compte comptable")
    )
    
    solde_bancaire = DecimalMoneyField(
        label=_("Solde bancaire"),
        required=True,
        help_text=_("Solde fourni par la banque")
    )
    
    class Meta:
        from ..models import RapprochementBancaire
        model = RapprochementBancaire
        fields = ['compte_bancaire', 'date_rapprochement',
                  'solde_comptable', 'solde_bancaire', 'statut', 'notes']
        widgets = {
            'compte_bancaire': forms.Select(),
            'date_rapprochement': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'statut': forms.Select(),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Remarques ou notes sur ce rapprochement...'
            }),
        }
    
    def clean(self):
        """Valide la cohérence du rapprochement."""
        cleaned_data = super().clean()
        
        solde_comptable = cleaned_data.get('solde_comptable')
        solde_bancaire = cleaned_data.get('solde_bancaire')
        compte = cleaned_data.get('compte_bancaire')
        
        if solde_comptable is not None and solde_bancaire is not None:
            if abs(solde_comptable - solde_bancaire) > Decimal('0.01'):
                raise ValidationError(
                    _("Les soldes ne sont pas équilibrés. "
                      "Écart: %(ecart).2f EUR"),
                    code='unbalanced',
                    params={'ecart': abs(solde_comptable - solde_bancaire)}
                )
        
        return cleaned_data


class OperationImportForm(forms.Form):
    """Formulaire pour l'import d'opérations bancaires."""
    
    fichier = forms.FileField(
        label=_("Fichier CSV ou OFX"),
        help_text=_("Format: CSV ou OFX")
    )
    
    format_fichier = forms.ChoiceField(
        label=_("Format du fichier"),
        choices=[
            ('csv', 'CSV'),
            ('ofx', 'OFX'),
            ('mt940', 'MT940'),
        ]
    )
    
    encodage = forms.ChoiceField(
        label=_("Encodage"),
        initial='utf-8',
        choices=[
            ('utf-8', 'UTF-8'),
            ('latin-1', 'Latin-1'),
            ('cp1252', 'Windows-1252'),
        ]
    )
    
    sauter_doublons = forms.BooleanField(
        label=_("Ignorer les doublons"),
        initial=True,
        required=False
    )
    
    def clean_fichier(self):
        """Valide le fichier uploadé."""
        fichier = self.cleaned_data.get('fichier')
        
        if fichier:
            # Vérifie la taille (max 10MB)
            if fichier.size > 10 * 1024 * 1024:
                raise ValidationError(_("Le fichier dépasse 10MB"))
            
            # Vérifie l'extension
            nom = fichier.name.lower()
            if not any(nom.endswith(ext) for ext in ['.csv', '.ofx', '.txt']):
                raise ValidationError(_("Format de fichier non supporté"))
        
        return fichier


class EcartBancaireForm(ComptaBaseForm):
    """Formulaire pour la résolution des écarts bancaires."""
    
    montant = DecimalMoneyField(
        label=_("Montant de l'écart"),
        required=True,
        help_text=_("Montant non rapproché")
    )
    
    class Meta:
        from ..models import EcartBancaire
        model = EcartBancaire
        fields = ['rapprochement', 'type_ecart', 'montant', 'description', 
                  'compte_comptable', 'ecriture', 'est_resolu', 'date_resolution']
        widgets = {
            'rapprochement': forms.Select(),
            'type_ecart': forms.Select(),
            'description': forms.Textarea(attrs={'rows': 3}),
            'compte_comptable': forms.Select(),
            'ecriture': forms.Select(),
            'est_resolu': forms.CheckboxInput(),
            'date_resolution': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean_montant(self):
        """Valide que l'écart est positif."""
        montant = self.cleaned_data.get('montant')
        if montant is not None and montant <= 0:
            raise ValidationError(_("L'écart doit être un montant positif"))
        return montant


class BulkLettrageForm(forms.Form):
    """Formulaire pour le lettrage en masse d'opérations."""
    
    operations = forms.ModelMultipleChoiceField(
        label=_("Opérations à lettrer"),
        queryset=None,  # À définir lors de l'instantiation
        widget=forms.CheckboxSelectMultiple
    )
    
    ecritures = forms.ModelMultipleChoiceField(
        label=_("Écritures comptables"),
        queryset=None,  # À définir lors de l'instantiation
        widget=forms.CheckboxSelectMultiple
    )
    
    def __init__(self, *args, compte_bancaire=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if compte_bancaire:
            from ..models import OperationBancaire, EcritureComptable
            
            self.fields['operations'].queryset = OperationBancaire.objects.filter(
                compte_bancaire=compte_bancaire,
                lettre=False
            )
            
            self.fields['ecritures'].queryset = EcritureComptable.objects.filter(
                entreprise=compte_bancaire.entreprise,
                type_ecriture__in=['OPERATION', 'RAPPROCHEMENT']
            )


class FilterForm(forms.Form):
    """Formulaire de filtrage pour les listes."""
    
    statut = forms.ChoiceField(
        label=_("Statut"),
        choices=[('', '--- Tous ---')],
        required=False
    )
    
    periode_debut = forms.DateField(
        label=_("Du"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    periode_fin = forms.DateField(
        label=_("Au"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    def clean(self):
        """Valide les dates."""
        cleaned_data = super().clean()
        
        debut = cleaned_data.get('periode_debut')
        fin = cleaned_data.get('periode_fin')
        
        if debut and fin and debut > fin:
            raise ValidationError(_("La date de début doit être antérieure à celle de fin"))
        
        return cleaned_data
