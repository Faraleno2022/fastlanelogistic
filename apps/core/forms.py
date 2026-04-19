from django import forms
from .models import Parametres


class ParametresForm(forms.ModelForm):
    class Meta:
        model = Parametres
        fields = [
            "societe_nom", "activite", "devise",
            "duree_amortissement", "taux_residuel",
            "prix_carburant", "tarif_bauxite", "taux_tva",
            "jours_ouvres_mois",
        ]
        widgets = {
            "societe_nom": forms.TextInput(attrs={"class": "form-control"}),
            "activite": forms.TextInput(attrs={"class": "form-control"}),
            "devise": forms.TextInput(attrs={"class": "form-control"}),
            "duree_amortissement": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "30"}),
            "taux_residuel": forms.NumberInput(attrs={"class": "form-control", "step": "0.0001", "min": "0", "max": "1"}),
            "prix_carburant": forms.NumberInput(attrs={"class": "form-control", "step": "1"}),
            "tarif_bauxite": forms.NumberInput(attrs={"class": "form-control", "step": "1"}),
            "taux_tva": forms.NumberInput(attrs={"class": "form-control", "step": "0.0001", "min": "0", "max": "1"}),
            "jours_ouvres_mois": forms.NumberInput(attrs={"class": "form-control", "min": "20", "max": "31"}),
        }
