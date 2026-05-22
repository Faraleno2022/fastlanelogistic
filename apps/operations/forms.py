from datetime import date
from django import forms
from .models import (
    BonTransport, Carburant, DepenseAdmin, FicheCarburant, Panne,
    TransportBauxite,
)


class CarburantForm(forms.ModelForm):
    class Meta:
        model = Carburant
        fields = [
            "date", "heure", "camion", "chauffeur", "contrat",
            "km_avant", "km_tableau_bord",
            "litres_avant", "litres_apres",
            "prix_unitaire", "station", "observations",
        ]
        widgets = {
            "date": forms.DateInput(format="%Y-%m-%d", attrs={"class": "form-control", "type": "date", "col": "3"}),
            "heure": forms.TimeInput(attrs={"class": "form-control", "type": "time", "col": "3"}),
            "camion": forms.Select(attrs={"class": "form-select", "col": "3"}),
            "chauffeur": forms.Select(attrs={"class": "form-select", "col": "3"}),
            "contrat": forms.Select(attrs={"class": "form-select", "col": "4",
                                           "title": "Laisser vide pour répartir au prorata entre tous les contrats actifs"}),
            "km_avant": forms.NumberInput(attrs={"class": "form-control", "col": "4"}),
            "km_tableau_bord": forms.NumberInput(attrs={"class": "form-control", "col": "4"}),
            "litres_avant": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "col": "3"}),
            "litres_apres": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "col": "3"}),
            "prix_unitaire": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "3"}),
            "station": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Station CBG-Sangarédi", "col": "3"}),
            "observations": forms.TextInput(attrs={"class": "form-control", "col": "12"}),
        }
        help_texts = {
            "km_avant": "Km relevé au dernier plein (départ de ce trajet)",
            "km_tableau_bord": "Km affiché actuellement sur le tableau de bord",
            "litres_avant": "Niveau jauge avant remplissage",
            "litres_apres": "Niveau jauge après remplissage",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date"].initial = date.today()
        self.fields["contrat"].required = False


class FicheCarburantForm(forms.ModelForm):
    class Meta:
        model = FicheCarburant
        fields = [
            "date", "numero", "chauffeur", "chauffeur_nom", "camion", "plaque",
            "niveau_carburant", "quantite", "heure", "rotation", "observation",
        ]
        widgets = {
            "date": forms.DateInput(format="%Y-%m-%d", attrs={"class": "form-control", "type": "date", "col": "3"}),
            "numero": forms.NumberInput(attrs={"class": "form-control", "min": "0", "col": "2"}),
            "chauffeur": forms.Select(attrs={"class": "form-select", "col": "4"}),
            "chauffeur_nom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom et prénom", "col": "6"}),
            "camion": forms.Select(attrs={"class": "form-select", "col": "4"}),
            "plaque": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: BK 2387 F01", "col": "4"}),
            "niveau_carburant": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "col": "3"}),
            "quantite": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "col": "3"}),
            "heure": forms.TimeInput(attrs={"class": "form-control", "type": "time", "col": "3"}),
            "rotation": forms.NumberInput(attrs={"class": "form-control", "min": "0", "col": "3"}),
            "observation": forms.TextInput(attrs={"class": "form-control", "col": "12"}),
        }
        help_texts = {
            "numero": "Laisser 0 pour générer automatiquement le prochain N° de la date.",
            "niveau_carburant": "Saisir la valeur en pourcentage, sans le signe %.",
            "chauffeur_nom": "Peut être rempli automatiquement si un chauffeur est sélectionné.",
            "plaque": "Peut être remplie automatiquement si un camion est sélectionné.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date"].initial = date.today()
            self.fields["numero"].initial = 0
        self.fields["chauffeur"].required = False
        self.fields["chauffeur_nom"].required = False
        self.fields["camion"].required = False
        self.fields["plaque"].required = False

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("chauffeur") and not cleaned.get("chauffeur_nom"):
            self.add_error("chauffeur_nom", "Renseignez un nom ou sélectionnez un chauffeur.")
        if not cleaned.get("camion") and not cleaned.get("plaque"):
            self.add_error("plaque", "Renseignez une plaque ou sélectionnez un camion.")
        return cleaned


class PanneForm(forms.ModelForm):
    class Meta:
        model = Panne
        fields = [
            "date", "camion", "contrat", "type_panne", "piece_remplacee",
            "fournisseur", "cout_pieces", "cout_main_oeuvre",
            "duree_immobilisation", "observations",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "3"}),
            "camion": forms.Select(attrs={"class": "form-select", "col": "3"}),
            "contrat": forms.Select(attrs={"class": "form-select", "col": "3",
                                           "title": "Laisser vide pour répartir au prorata entre tous les contrats actifs"}),
            "type_panne": forms.Select(attrs={"class": "form-select", "col": "3"}),
            "piece_remplacee": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Pneu AV gauche, filtre huile…", "col": "9"}),
            "fournisseur": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Garage Sidibé", "col": "6"}),
            "cout_pieces": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "3"}),
            "cout_main_oeuvre": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "3"}),
            "duree_immobilisation": forms.NumberInput(attrs={"class": "form-control", "min": "0", "col": "3"}),
            "observations": forms.Textarea(attrs={"class": "form-control", "rows": 2, "col": "12"}),
        }
        help_texts = {
            "cout_pieces": "Montant en GNF",
            "cout_main_oeuvre": "Montant en GNF",
            "duree_immobilisation": "Nombre de jours d'immobilisation du camion",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date"].initial = date.today()
        self.fields["contrat"].required = False


class DepenseAdminForm(forms.ModelForm):
    class Meta:
        model = DepenseAdmin
        fields = [
            "date", "type_depense", "camion", "contrat", "description",
            "reference", "montant", "echeance", "statut",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "3"}),
            "type_depense": forms.Select(attrs={"class": "form-select", "col": "3"}),
            "camion": forms.Select(attrs={"class": "form-select", "col": "3",
                                         "title": "Laisser vide pour une dépense générale non liée à un camion"}),
            "contrat": forms.Select(attrs={"class": "form-select", "col": "3",
                                           "title": "Laisser vide pour répartir au prorata entre tous les contrats actifs"}),
            "statut": forms.Select(attrs={"class": "form-select", "col": "3"}),
            "description": forms.TextInput(attrs={"class": "form-control", "col": "5"}),
            "reference": forms.TextInput(attrs={"class": "form-control", "placeholder": "N° reçu, quittance…", "col": "4"}),
            "montant": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "4"}),
            "echeance": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "4"}),
        }
        help_texts = {
            "camion": "Optionnel — laissez vide pour une dépense générale",
            "montant": "Montant en GNF",
            "echeance": "Date limite de paiement (optionnel)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date"].initial = date.today()
        self.fields["camion"].required = False
        self.fields["contrat"].required = False


class TransportBauxiteForm(forms.ModelForm):
    class Meta:
        model = TransportBauxite
        fields = [
            "date", "camion", "chauffeur", "contrat", "trajet",
            "distance_km", "tonnage", "tarif_unitaire",
            "client", "num_bon", "observations",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "3"}),
            "camion": forms.Select(attrs={"class": "form-select", "col": "3"}),
            "chauffeur": forms.Select(attrs={"class": "form-select", "col": "3"}),
            "contrat": forms.Select(attrs={"class": "form-select", "col": "3",
                                           "title": "Contrat client — détermine la facturation"}),
            "trajet": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Sangarédi → Port Kamsar", "col": "9"}),
            "distance_km": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "col": "3"}),
            "tonnage": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "col": "3"}),
            "tarif_unitaire": forms.NumberInput(attrs={"class": "form-control", "step": "1", "col": "3"}),
            "client": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: CBG", "col": "3"}),
            "num_bon": forms.TextInput(attrs={"class": "form-control", "placeholder": "Généré automatiquement si vide", "col": "4"}),
            "observations": forms.Textarea(attrs={"class": "form-control", "rows": 2, "col": "12"}),
        }
        help_texts = {
            "distance_km": "Distance du trajet en km",
            "tonnage": "Tonnage transporté en tonnes",
            "tarif_unitaire": "Tarif en GNF par tonne",
            "num_bon": "Laissez vide pour génération automatique",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date"].initial = date.today()
        self.fields["contrat"].required = False


class BonTransportForm(forms.ModelForm):
    class Meta:
        model = BonTransport
        fields = [
            "num_bon",
            "date", "camion", "chauffeur", "contrat",
            "prenom", "nom", "telephone", "plaque",
            "remarque", "carte_entree", "lieu_chargement",
            "heure_depart", "heure_pesee_start", "heure_pesee_end",
            "heure_observation_start", "heure_observation_end",
            "quantite_1", "quantite_2", "quantite_3", "quantite_4",
            "quantite", "observation",
        ]
        widgets = {
            "num_bon": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: BT-001", "col": "3"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date", "col": "3"}),
            "camion": forms.Select(attrs={"class": "form-select", "col": "3"}),
            "chauffeur": forms.Select(attrs={"class": "form-select", "col": "3"}),
            "contrat": forms.Select(attrs={"class": "form-select", "col": "3",
                                           "title": "Contrat client de ce bon"}),
            "prenom": forms.TextInput(attrs={"class": "form-control", "col": "4"}),
            "nom": forms.TextInput(attrs={"class": "form-control", "col": "4"}),
            "telephone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+224 6xx xx xx xx", "col": "4"}),
            "plaque": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: RC-1234-A", "col": "4"}),
            "remarque": forms.TextInput(attrs={"class": "form-control", "col": "4"}),
            "carte_entree": forms.TextInput(attrs={"class": "form-control", "col": "4"}),
            "lieu_chargement": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Trémie 3 — Sangarédi", "col": "4"}),
            "heure_depart": forms.TimeInput(attrs={"class": "form-control", "type": "time", "col": "4"}),
            "heure_pesee_start": forms.TimeInput(attrs={"class": "form-control", "type": "time", "col": "4"}),
            "heure_pesee_end": forms.TimeInput(attrs={"class": "form-control", "type": "time", "col": "4"}),
            "heure_observation_start": forms.TimeInput(attrs={"class": "form-control", "type": "time", "col": "4"}),
            "heure_observation_end": forms.TimeInput(attrs={"class": "form-control", "type": "time", "col": "4"}),
            "quantite_1": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "col": "3"}),
            "quantite_2": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "col": "3"}),
            "quantite_3": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "col": "3"}),
            "quantite_4": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "col": "3"}),
            "quantite": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "col": "4", "readonly": "readonly"}),
            "observation": forms.Textarea(attrs={"class": "form-control", "rows": 2, "col": "12"}),
        }
        help_texts = {
            "quantite": "Tonnage pesé en tonnes",
            "heure_pesee_start": "Heure d'entrée sur le pont-bascule",
            "heure_pesee_end": "Heure de sortie du pont-bascule",
            "carte_entree": "N° de carte d'accès au site",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["date"].initial = date.today()
        for field_name in ("num_bon", "prenom", "nom", "plaque", "lieu_chargement", "contrat"):
            self.fields[field_name].required = False

    def clean(self):
        cleaned = super().clean()
        total = sum(cleaned.get(f"quantite_{i}") or 0 for i in range(1, 5))
        if total:
            cleaned["quantite"] = total
        return cleaned
