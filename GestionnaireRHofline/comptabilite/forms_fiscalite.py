"""Formulaires pour le module de fiscalité."""

from django import forms
from decimal import Decimal

from .models import ExerciceComptable
from .models_fiscalite import (
    DossierFiscalComplet,
    DeclarationIS,
    DeclarationCAT,
    DeclarationCVAE,
    LiasseFiscale,
    DocumentationFiscale,
)


class DossierFiscalForm(forms.ModelForm):
    """Formulaire de gestion des dossiers fiscaux."""

    class Meta:
        model = DossierFiscalComplet
        fields = [
            "exercice",
            "reference",
            "annee_fiscale",
            "date_ouverture",
            "date_cloture_exercice",
            "date_limite_depot",
            "statut",
            "resultat_comptable",
            "resultat_fiscal",
            "observations",
        ]
        widgets = {
            "exercice": forms.Select(attrs={"class": "form-select"}),
            "reference": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: DF-2025"}),
            "annee_fiscale": forms.NumberInput(attrs={"class": "form-control"}),
            "date_ouverture": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "date_cloture_exercice": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "date_limite_depot": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
            "resultat_comptable": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "resultat_fiscal": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "observations": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entreprise = entreprise

        if entreprise:
            self.fields["exercice"].queryset = ExerciceComptable.objects.filter(
                entreprise=entreprise
            ).order_by("-date_debut")
        else:
            self.fields["exercice"].queryset = ExerciceComptable.objects.none()

        self.fields["observations"].required = False

    def clean_annee_fiscale(self):
        annee = self.cleaned_data.get("annee_fiscale")
        if annee and (annee < 2000 or annee > 2100):
            raise forms.ValidationError("L'année fiscale doit être comprise entre 2000 et 2100.")
        return annee


class DeclarationISForm(forms.ModelForm):
    """Formulaire de déclaration IS."""

    class Meta:
        model = DeclarationIS
        fields = [
            "dossier_fiscal",
            "reference",
            "type_declaration",
            "periode_debut",
            "periode_fin",
            "resultat_comptable_brut",
            "reintegrations_amortissements",
            "reintegrations_provisions",
            "reintegrations_amendes",
            "reintegrations_dons_excessifs",
            "autres_reintegrations",
            "deductions_dividendes",
            "deductions_plus_values",
            "deductions_provisions_reglementees",
            "autres_deductions",
            "deficits_anterieurs",
            "taux_is",
            "credits_impot",
            "acomptes_verses",
            "minimum_fiscal",
            "is_minimum_applicable",
            "statut",
        ]
        widgets = {
            "dossier_fiscal": forms.Select(attrs={"class": "form-select"}),
            "reference": forms.TextInput(attrs={"class": "form-control"}),
            "type_declaration": forms.Select(attrs={"class": "form-select"}),
            "periode_debut": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "periode_fin": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "resultat_comptable_brut": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "reintegrations_amortissements": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "reintegrations_provisions": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "reintegrations_amendes": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "reintegrations_dons_excessifs": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "autres_reintegrations": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "deductions_dividendes": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "deductions_plus_values": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "deductions_provisions_reglementees": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "autres_deductions": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "deficits_anterieurs": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "taux_is": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "credits_impot": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "acomptes_verses": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "minimum_fiscal": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "is_minimum_applicable": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entreprise = entreprise

        if entreprise:
            self.fields["dossier_fiscal"].queryset = DossierFiscalComplet.objects.filter(
                entreprise=entreprise
            ).order_by("-annee_fiscale")
        else:
            self.fields["dossier_fiscal"].queryset = DossierFiscalComplet.objects.none()


class DeclarationCATForm(forms.ModelForm):
    """Formulaire de déclaration CAT."""

    class Meta:
        model = DeclarationCAT
        fields = [
            "dossier_fiscal",
            "reference",
            "annee",
            "mois",
            "montant_prestations",
            "taux_cat",
            "exonerations",
            "statut",
        ]
        widgets = {
            "dossier_fiscal": forms.Select(attrs={"class": "form-select"}),
            "reference": forms.TextInput(attrs={"class": "form-control"}),
            "annee": forms.NumberInput(attrs={"class": "form-control"}),
            "mois": forms.Select(attrs={"class": "form-select"}, choices=[
                (i, f"{i:02d}") for i in range(1, 13)
            ]),
            "montant_prestations": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "taux_cat": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "exonerations": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entreprise = entreprise

        if entreprise:
            self.fields["dossier_fiscal"].queryset = DossierFiscalComplet.objects.filter(
                entreprise=entreprise
            ).order_by("-annee_fiscale")
        else:
            self.fields["dossier_fiscal"].queryset = DossierFiscalComplet.objects.none()

        self.fields["dossier_fiscal"].required = False
        self.fields["exonerations"].required = False


class DeclarationCVAEForm(forms.ModelForm):
    """Formulaire de déclaration CVAE."""

    class Meta:
        model = DeclarationCVAE
        fields = [
            "dossier_fiscal",
            "reference",
            "annee",
            "chiffre_affaires",
            "achats",
            "services_exterieurs",
            "autres_charges_externes",
            "taux_cvae",
            "degrevement",
            "cotisation_minimum",
            "statut",
        ]
        widgets = {
            "dossier_fiscal": forms.Select(attrs={"class": "form-select"}),
            "reference": forms.TextInput(attrs={"class": "form-control"}),
            "annee": forms.NumberInput(attrs={"class": "form-control"}),
            "chiffre_affaires": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "achats": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "services_exterieurs": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "autres_charges_externes": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "taux_cvae": forms.NumberInput(attrs={"class": "form-control", "step": "0.0001"}),
            "degrevement": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "cotisation_minimum": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entreprise = entreprise

        if entreprise:
            self.fields["dossier_fiscal"].queryset = DossierFiscalComplet.objects.filter(
                entreprise=entreprise
            ).order_by("-annee_fiscale")
        else:
            self.fields["dossier_fiscal"].queryset = DossierFiscalComplet.objects.none()

        self.fields["dossier_fiscal"].required = False
        self.fields["degrevement"].required = False
        self.fields["cotisation_minimum"].required = False


class LiasseFiscaleForm(forms.ModelForm):
    """Formulaire de liasse fiscale."""

    class Meta:
        model = LiasseFiscale
        fields = [
            "dossier_fiscal",
            "reference",
            "type_liasse",
            "annee",
            "statut",
        ]
        widgets = {
            "dossier_fiscal": forms.Select(attrs={"class": "form-select"}),
            "reference": forms.TextInput(attrs={"class": "form-control"}),
            "type_liasse": forms.Select(attrs={"class": "form-select"}),
            "annee": forms.NumberInput(attrs={"class": "form-control"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entreprise = entreprise

        if entreprise:
            self.fields["dossier_fiscal"].queryset = DossierFiscalComplet.objects.filter(
                entreprise=entreprise
            ).order_by("-annee_fiscale")
        else:
            self.fields["dossier_fiscal"].queryset = DossierFiscalComplet.objects.none()


class DocumentationFiscaleForm(forms.ModelForm):
    """Formulaire de documentation fiscale."""

    class Meta:
        model = DocumentationFiscale
        fields = [
            "dossier_fiscal",
            "type_document",
            "titre",
            "description",
            "fichier",
        ]
        widgets = {
            "dossier_fiscal": forms.Select(attrs={"class": "form-select"}),
            "type_document": forms.Select(attrs={"class": "form-select"}),
            "titre": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "fichier": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entreprise = entreprise

        if entreprise:
            self.fields["dossier_fiscal"].queryset = DossierFiscalComplet.objects.filter(
                entreprise=entreprise
            ).order_by("-annee_fiscale")
        else:
            self.fields["dossier_fiscal"].queryset = DossierFiscalComplet.objects.none()

        self.fields["description"].required = False
