from datetime import date
from django import forms
from .models import Contrat, Facture


class ContratForm(forms.ModelForm):
    class Meta:
        model = Contrat
        fields = [
            "code", "client", "type_facturation", "tarif",
            "date_debut", "date_fin", "actif", "observations",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: CTR-2026-001", "col": "4"}),
            "client": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: CBG — Compagnie des Bauxites de Guinée", "col": "8"}),
            "type_facturation": forms.Select(attrs={"class": "form-select", "col": "4"}),
            "tarif": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "4"}),
            "date_debut": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "4"}),
            "date_fin": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "4"}),
            "actif": forms.CheckboxInput(attrs={"class": "form-check-input", "col": "2"}),
            "observations": forms.Textarea(attrs={"class": "form-control", "rows": 3, "col": "12"}),
        }
        help_texts = {
            "tarif": "Tarif unitaire en GNF (par tonne, par km, par voyage selon le type)",
            "type_facturation": "Détermine la base de calcul des factures",
            "date_fin": "Optionnel — laissez vide pour un contrat sans date de fin",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date_debut"].initial = date.today()
        self.fields["date_fin"].required = False


class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = [
            "numero", "contrat", "periode_mois", "periode_annee",
            "date_emission", "echeance",
            "bonus", "penalites", "deduction_carburant",
            "taux_tva", "statut", "observations",
        ]
        widgets = {
            "numero": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: FAC-2026-001", "col": "4"}),
            "contrat": forms.Select(attrs={"class": "form-select", "col": "4"}),
            "statut": forms.Select(attrs={"class": "form-select", "col": "4"}),
            "periode_mois": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "12", "col": "3"}),
            "periode_annee": forms.NumberInput(attrs={"class": "form-control", "min": "2020", "col": "3"}),
            "date_emission": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "3"}),
            "echeance": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "3"}),
            "bonus": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "4"}),
            "penalites": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "4"}),
            "deduction_carburant": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "4"}),
            "taux_tva": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "1", "col": "4"}),
            "observations": forms.Textarea(attrs={"class": "form-control", "rows": 3, "col": "12"}),
        }
        help_texts = {
            "periode_mois": "Mois de la prestation (1–12)",
            "periode_annee": "Année de la prestation",
            "bonus": "Bonus en GNF à ajouter au montant brut",
            "penalites": "Pénalités en GNF à déduire",
            "deduction_carburant": "Déduction carburant fourni par le client",
            "taux_tva": "Ex: 0.18 = 18% de TVA",
            "echeance": "Date limite de paiement",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today()
        if not self.instance.pk:
            self.fields["date_emission"].initial = today
            self.fields["periode_mois"].initial = today.month
            self.fields["periode_annee"].initial = today.year
        self.fields["echeance"].required = False
