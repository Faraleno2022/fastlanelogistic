from datetime import date
from django import forms
from .models import Employe, Attendance, HeureSup


class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = [
            "code", "prenom", "nom", "fonction", "telephone",
            "site_prestation", "camion", "salaire_jour",
            "salaire_base_mensuel", "primes", "taux_charges",
            "date_embauche", "actif",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: EMP-001", "col": "3"}),
            "prenom": forms.TextInput(attrs={"class": "form-control", "col": "3"}),
            "nom": forms.TextInput(attrs={"class": "form-control", "col": "3"}),
            "fonction": forms.Select(attrs={"class": "form-select", "col": "3"}),
            "telephone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+224 6xx xx xx xx", "col": "4"}),
            "site_prestation": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Sangarédi", "col": "4"}),
            "camion": forms.Select(attrs={"class": "form-select", "col": "4"}),
            "salaire_jour": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "3"}),
            "salaire_base_mensuel": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "3"}),
            "primes": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "3"}),
            "taux_charges": forms.NumberInput(attrs={
                "class": "form-control", "step": "0.01", "min": "0", "max": "1", "col": "3",
            }),
            "date_embauche": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "4"}),
            "actif": forms.CheckboxInput(attrs={"class": "form-check-input", "col": "2"}),
        }
        help_texts = {
            "salaire_jour": "Salaire journalier en GNF (utilisé pour le calcul attendance)",
            "taux_charges": "Ex: 0.18 = 18% de charges patronales",
            "primes": "Primes fixes mensuelles en GNF",
            "camion": "Camion affecté (pour les chauffeurs)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["camion"].required = False
        if not self.instance.pk:
            self.fields["date_embauche"].initial = date.today()


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["employe", "date", "code", "commentaire"]
        widgets = {
            "employe": forms.Select(attrs={"class": "form-select", "col": "4"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "4"}),
            "code": forms.Select(attrs={"class": "form-select", "col": "4"}),
            "commentaire": forms.TextInput(attrs={"class": "form-control", "col": "12"}),
        }
        help_texts = {
            "code": "P=Présent | A=Absent | C=Congé | M=Maladie | D=Dimanche travaillé | R=Repos",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date"].initial = date.today()
        # Filtrer uniquement les employés actifs
        self.fields["employe"].queryset = Employe.objects.filter(actif=True).order_by("nom", "prenom")


class HeureSupForm(forms.ModelForm):
    class Meta:
        model = HeureSup
        fields = [
            "employe", "date", "heure_debut", "heure_fin",
            "type_hs", "majoration", "motif", "valide_par",
        ]
        widgets = {
            "employe": forms.Select(attrs={"class": "form-select", "col": "4"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "4"}),
            "type_hs": forms.Select(attrs={"class": "form-select", "col": "4"}),
            "heure_debut": forms.TimeInput(attrs={"class": "form-control", "type": "time", "col": "3"}),
            "heure_fin": forms.TimeInput(attrs={"class": "form-control", "type": "time", "col": "3"}),
            "majoration": forms.NumberInput(attrs={"class": "form-control", "step": "5", "min": "0", "max": "200", "col": "3"}),
            "valide_par": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom du responsable validant", "col": "3"}),
            "motif": forms.Textarea(attrs={"class": "form-control", "rows": 2, "col": "12"}),
        }
        help_texts = {
            "majoration": "% de majoration horaire (ex: 25 pour +25%, 50 pour dimanches)",
            "type_hs": "Le type détermine la majoration recommandée",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date"].initial = date.today()
        self.fields["employe"].queryset = Employe.objects.filter(actif=True).order_by("nom", "prenom")
