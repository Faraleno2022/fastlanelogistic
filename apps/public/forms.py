from django import forms
from .models import ContactMessage


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
