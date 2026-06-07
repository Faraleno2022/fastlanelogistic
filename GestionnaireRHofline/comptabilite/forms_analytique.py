"""Formulaires pour le module de comptabilité analytique."""

from django import forms

from .models import EcritureComptable, PlanComptable, ExerciceComptable
from .models_analytique import (
    SectionAnalytique,
    CentreCouts,
    CommandeAnalytique,
    CleRepartition,
    ImputationAnalytique,
    BudgetAnalytique,
    AnalyseVariance,
)


class SectionAnalytiqueForm(forms.ModelForm):
    """Formulaire de gestion des sections analytiques."""

    class Meta:
        model = SectionAnalytique
        fields = [
            "code",
            "libelle",
            "description",
            "type_section",
            "section_parent",
            "centre_couts",
            "est_active",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: SEC001"}),
            "libelle": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "type_section": forms.Select(attrs={"class": "form-select"}),
            "section_parent": forms.Select(attrs={"class": "form-select"}),
            "centre_couts": forms.Select(attrs={"class": "form-select"}),
            "est_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entreprise = entreprise

        if entreprise:
            self.fields["section_parent"].queryset = (
                SectionAnalytique.objects.filter(entreprise=entreprise).exclude(pk=self.instance.pk)
            )
            self.fields["centre_couts"].queryset = CentreCouts.objects.filter(
                entreprise=entreprise, est_actif=True
            )
        else:
            self.fields["section_parent"].queryset = SectionAnalytique.objects.none()
            self.fields["centre_couts"].queryset = CentreCouts.objects.none()

        self.fields["section_parent"].required = False
        self.fields["centre_couts"].required = False

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if code and self.entreprise:
            queryset = SectionAnalytique.objects.filter(entreprise=self.entreprise, code=code)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("Ce code est déjà utilisé pour une autre section analytique.")
        return code


class ImputationAnalytiqueForm(forms.ModelForm):
    """Formulaire de saisie des imputations analytiques."""

    class Meta:
        model = ImputationAnalytique
        fields = [
            "date_imputation",
            "periode",
            "libelle",
            "type_imputation",
            "ecriture",
            "compte",
            "centre_couts",
            "section",
            "commande",
            "cle_repartition",
            "pourcentage_repartition",
            "montant_debit",
            "montant_credit",
            "quantite",
            "unite",
        ]
        widgets = {
            "date_imputation": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "periode": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "YYYY-MM"}
            ),
            "libelle": forms.TextInput(attrs={"class": "form-control"}),
            "type_imputation": forms.Select(attrs={"class": "form-select"}),
            "ecriture": forms.Select(attrs={"class": "form-select"}),
            "compte": forms.Select(attrs={"class": "form-select"}),
            "centre_couts": forms.Select(attrs={"class": "form-select"}),
            "section": forms.Select(attrs={"class": "form-select"}),
            "commande": forms.Select(attrs={"class": "form-select"}),
            "cle_repartition": forms.Select(attrs={"class": "form-select"}),
            "pourcentage_repartition": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "montant_debit": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "montant_credit": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "quantite": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.0001"}
            ),
            "unite": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: heures"}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entreprise = entreprise

        if entreprise:
            self.fields["ecriture"].queryset = EcritureComptable.objects.filter(
                entreprise=entreprise
            ).select_related("journal", "exercice").order_by("-date_ecriture")
            self.fields["compte"].queryset = PlanComptable.objects.filter(
                entreprise=entreprise, est_actif=True
            ).order_by("numero_compte")
            self.fields["centre_couts"].queryset = CentreCouts.objects.filter(
                entreprise=entreprise, est_actif=True
            ).order_by("code")
            self.fields["section"].queryset = SectionAnalytique.objects.filter(
                entreprise=entreprise, est_active=True
            ).order_by("code")
            self.fields["commande"].queryset = CommandeAnalytique.objects.filter(
                entreprise=entreprise
            ).order_by("-date_creation")
            self.fields["cle_repartition"].queryset = CleRepartition.objects.filter(
                entreprise=entreprise, est_active=True
            ).order_by("code")
        else:
            self.fields["ecriture"].queryset = EcritureComptable.objects.none()
            self.fields["compte"].queryset = PlanComptable.objects.none()
            self.fields["centre_couts"].queryset = CentreCouts.objects.none()
            self.fields["section"].queryset = SectionAnalytique.objects.none()
            self.fields["commande"].queryset = CommandeAnalytique.objects.none()
            self.fields["cle_repartition"].queryset = CleRepartition.objects.none()

        self.fields["centre_couts"].required = False
        self.fields["section"].required = False
        self.fields["commande"].required = False
        self.fields["cle_repartition"].required = False
        self.fields["pourcentage_repartition"].required = False
        self.fields["quantite"].required = False
        self.fields["unite"].required = False

    def clean(self):
        cleaned_data = super().clean()

        debit = cleaned_data.get("montant_debit") or 0
        credit = cleaned_data.get("montant_credit") or 0
        if debit <= 0 and credit <= 0:
            raise forms.ValidationError(
                "Veuillez saisir un montant au débit ou au crédit pour l'imputation."
            )

        periode = cleaned_data.get("periode")
        if periode:
            if len(periode) != 7 or "-" not in periode:
                self.add_error("periode", "Le format de la période doit être YYYY-MM.")

        return cleaned_data


class BudgetAnalytiqueForm(forms.ModelForm):
    """Formulaire de gestion des budgets analytiques."""

    class Meta:
        model = BudgetAnalytique
        fields = [
            "exercice",
            "type_budget",
            "periode",
            "centre_couts",
            "section",
            "budget_charges",
            "budget_produits",
        ]
        widgets = {
            "exercice": forms.Select(attrs={"class": "form-select"}),
            "type_budget": forms.Select(attrs={"class": "form-select"}),
            "periode": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "YYYY-MM"}
            ),
            "centre_couts": forms.Select(attrs={"class": "form-select"}),
            "section": forms.Select(attrs={"class": "form-select"}),
            "budget_charges": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "budget_produits": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entreprise = entreprise

        if entreprise:
            self.fields["exercice"].queryset = ExerciceComptable.objects.filter(
                entreprise=entreprise
            ).order_by("-date_debut")
            self.fields["centre_couts"].queryset = CentreCouts.objects.filter(
                entreprise=entreprise, est_actif=True
            ).order_by("code")
            self.fields["section"].queryset = SectionAnalytique.objects.filter(
                entreprise=entreprise, est_active=True
            ).order_by("code")
        else:
            self.fields["exercice"].queryset = ExerciceComptable.objects.none()
            self.fields["centre_couts"].queryset = CentreCouts.objects.none()
            self.fields["section"].queryset = SectionAnalytique.objects.none()

        self.fields["centre_couts"].required = False
        self.fields["section"].required = False

    def clean(self):
        cleaned_data = super().clean()

        centre = cleaned_data.get("centre_couts")
        section = cleaned_data.get("section")
        if not centre and not section:
            raise forms.ValidationError(
                "Veuillez sélectionner un centre de coûts ou une section analytique."
            )

        periode = cleaned_data.get("periode")
        if periode:
            if len(periode) != 7 or "-" not in periode:
                self.add_error("periode", "Le format de la période doit être YYYY-MM.")

        return cleaned_data


class AnalyseVarianceForm(forms.ModelForm):
    """Formulaire de saisie des analyses de variance."""

    class Meta:
        model = AnalyseVariance
        fields = [
            "exercice",
            "periode",
            "centre_couts",
            "section",
            "type_ecart",
            "montant_budget",
            "montant_reel",
            "favorable",
            "explication",
            "actions_correctives",
        ]
        widgets = {
            "exercice": forms.Select(attrs={"class": "form-select"}),
            "periode": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "YYYY-MM"}
            ),
            "centre_couts": forms.Select(attrs={"class": "form-select"}),
            "section": forms.Select(attrs={"class": "form-select"}),
            "type_ecart": forms.Select(attrs={"class": "form-select"}),
            "montant_budget": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "montant_reel": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "favorable": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "explication": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "actions_correctives": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entreprise = entreprise

        if entreprise:
            self.fields["exercice"].queryset = ExerciceComptable.objects.filter(
                entreprise=entreprise
            ).order_by("-date_debut")
            self.fields["centre_couts"].queryset = CentreCouts.objects.filter(
                entreprise=entreprise, est_actif=True
            ).order_by("code")
            self.fields["section"].queryset = SectionAnalytique.objects.filter(
                entreprise=entreprise, est_active=True
            ).order_by("code")
        else:
            self.fields["exercice"].queryset = ExerciceComptable.objects.none()
            self.fields["centre_couts"].queryset = CentreCouts.objects.none()
            self.fields["section"].queryset = SectionAnalytique.objects.none()

        self.fields["centre_couts"].required = False
        self.fields["section"].required = False
        self.fields["explication"].required = False
        self.fields["actions_correctives"].required = False

    def clean(self):
        cleaned_data = super().clean()

        centre = cleaned_data.get("centre_couts")
        section = cleaned_data.get("section")
        if not centre and not section:
            raise forms.ValidationError(
                "Veuillez sélectionner un centre de coûts ou une section analytique."
            )

        periode = cleaned_data.get("periode")
        if periode:
            if len(periode) != 7 or "-" not in periode:
                self.add_error("periode", "Le format de la période doit être YYYY-MM.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        budget = instance.montant_budget or 0
        reel = instance.montant_reel or 0
        instance.ecart_montant = reel - budget
        if budget != 0:
            instance.ecart_pourcentage = ((reel - budget) / abs(budget)) * 100
        else:
            instance.ecart_pourcentage = 0
        if commit:
            instance.save()
        return instance
