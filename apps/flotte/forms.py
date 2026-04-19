from datetime import date
from django import forms
from .models import Camion


class CamionForm(forms.ModelForm):
    class Meta:
        model = Camion
        fields = [
            "code", "immatriculation", "marque_modele",
            "capacite_tonnes", "date_acquisition", "prix_achat",
            "duree_amortissement", "statut",
        ]
        widgets = {
            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: CAM-01",
                "col": "4",
            }),
            "immatriculation": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: RC-1234-A",
                "col": "4",
            }),
            "marque_modele": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: SINOTRUK HOWO 371",
                "col": "4",
            }),
            "capacite_tonnes": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.1",
                "col": "3",
            }),
            "date_acquisition": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
                "col": "3",
            }),
            "prix_achat": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "1",
                "col": "3",
            }),
            "duree_amortissement": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "max": "20",
                "col": "3",
            }),
            "statut": forms.Select(attrs={
                "class": "form-select",
                "col": "4",
            }),
        }
        help_texts = {
            "code": "Identifiant unique du camion (ex: CAM-01)",
            "capacite_tonnes": "Capacité de chargement en tonnes",
            "prix_achat": "Montant en GNF",
            "duree_amortissement": "Nombre d'années pour l'amortissement linéaire",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date_acquisition"].initial = date.today()
