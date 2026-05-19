from django import forms
from .models import AppelOffre, ContactMessage, Evenement


def _apply_bootstrap(fields):
    for field in fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault("class", "form-check-input")
        elif isinstance(widget, forms.Select):
            widget.attrs.setdefault("class", "form-select")
        elif isinstance(widget, forms.Textarea):
            widget.attrs.setdefault("class", "form-control")
        else:
            widget.attrs.setdefault("class", "form-control")


class ContactForm(forms.ModelForm):
    # Honeypot anti-spam : champ caché, les bots le remplissent
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ContactMessage
        fields = ["nom", "entreprise", "email", "telephone", "sujet", "message"]
        widgets = {
            "nom": forms.TextInput(attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Votre nom complet",
                "autocomplete": "name",
            }),
            "entreprise": forms.TextInput(attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Nom de votre entreprise (optionnel)",
                "autocomplete": "organization",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control form-control-lg",
                "placeholder": "exemple@domaine.com",
                "autocomplete": "email",
            }),
            "telephone": forms.TextInput(attrs={
                "class": "form-control form-control-lg",
                "placeholder": "+224 6XX XX XX XX",
                "autocomplete": "tel",
            }),
            "sujet": forms.Select(attrs={
                "class": "form-select form-select-lg",
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Décrivez votre demande, votre projet ou votre question...",
            }),
        }
        labels = {
            "nom": "Nom complet *",
            "entreprise": "Entreprise / Organisation",
            "email": "Adresse e-mail *",
            "telephone": "Téléphone",
            "sujet": "Sujet *",
            "message": "Votre message *",
        }

    def clean_website(self):
        # Si le honeypot est rempli, on rejette silencieusement
        data = self.cleaned_data.get("website")
        if data:
            raise forms.ValidationError("Spam détecté.")
        return data

    def clean_message(self):
        msg = (self.cleaned_data.get("message") or "").strip()
        if len(msg) < 10:
            raise forms.ValidationError(
                "Votre message est trop court (minimum 10 caractères)."
            )
        return msg


class EvenementForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = [
            "titre", "date_evenement", "lieu", "resume", "contenu", "image",
            "statut",
        ]
        widgets = {
            "date_evenement": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "resume": forms.Textarea(attrs={"rows": 3, "col": "12"}),
            "contenu": forms.Textarea(attrs={"rows": 8, "col": "12"}),
            "image": forms.ClearableFileInput(attrs={"col": "12"}),
            "statut": forms.Select(attrs={"col": "4"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap(self.fields)


class AppelOffreForm(forms.ModelForm):
    class Meta:
        model = AppelOffre
        fields = [
            "reference", "titre", "objet", "description", "lieu_execution",
            "date_publication", "date_limite", "contact_email",
            "contact_telephone", "document", "statut",
        ]
        widgets = {
            "objet": forms.Textarea(attrs={"rows": 3, "col": "12"}),
            "description": forms.Textarea(attrs={"rows": 8, "col": "12"}),
            "date_publication": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "date_limite": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "document": forms.ClearableFileInput(attrs={"col": "12"}),
            "statut": forms.Select(attrs={"col": "4"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap(self.fields)
