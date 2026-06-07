from datetime import date
from django import forms

from appli import models


class ContactForm(forms.ModelForm):
    class Meta:
        model = models.Contacts
        fields = ['contact_name', 'contact_email', 'contact_phone_number', 'contact_subject', 'contact_message']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_subject': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_message': forms.Textarea(attrs={'class': 'form-control'}),
        }
        



class EventForm(forms.ModelForm):
    # surcharge le champ event_date pour le rendre de type 'date' et ajouter 'min'
    event_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'hse-input', # Applique directement la classe CSS
            'min': date.today().isoformat() # Définit la date minimale à aujourd'hui
        }),
        label='Date', # Label pour le formulaire
        required=True
    )

    class Meta:
        model = models.Events
        fields = ['event_name', 'event_date', 'event_address', 'event_description', 'event_picture']

        # Personnalisation des widgets pour les autres champs
        widgets = {
            'event_name': forms.TextInput(attrs={'class': 'hse-input', 'placeholder': 'Intitulé de l\'événement'}),
            'event_address': forms.TextInput(attrs={'class': 'hse-input', 'placeholder': 'Ex: Salle Polyvalente'}),
            'event_description': forms.Textarea(attrs={'class': 'hse-input', 'rows': 5, 'placeholder': 'Décrivez l\'événement en détail...'}),
            'event_picture': forms.ClearableFileInput(attrs={'class': 'hse-input-file'}), # Pour l'upload de fichier
        }
        
        
        #Là on met un label pour tous les champs
        # Labels personnalisés (optionnel, mais bonne pratique)
        labels = {
            'event_name': 'Intitulé',
            'event_address': 'Lieu',
            'event_description': 'Description',
            'event_picture': 'Image de l\'événement',
        }