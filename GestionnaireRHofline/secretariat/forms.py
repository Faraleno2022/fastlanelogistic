"""Formulaires du module Secrétariat (classes Bootstrap auto-appliquées)."""
from django import forms
from .models import (
    Courrier, RendezVous, Visiteur, Appel,
    DocumentSecretariat, Tache, Contact, Reunion,
)


class BootstrapModelForm(forms.ModelForm):
    """Applique automatiquement les classes Bootstrap aux widgets."""
    class Meta:
        exclude = ('entreprise', 'cree_par', 'date_creation', 'date_modification')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, (forms.CheckboxInput,)):
                w.attrs.setdefault('class', 'form-check-input')
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                w.attrs.setdefault('class', 'form-select')
            elif isinstance(w, (forms.DateInput,)):
                w.attrs.setdefault('class', 'form-control')
                w.input_type = 'date'
            elif isinstance(w, (forms.DateTimeInput,)):
                w.attrs.setdefault('class', 'form-control')
                w.input_type = 'datetime-local'
            elif isinstance(w, (forms.TimeInput,)):
                w.attrs.setdefault('class', 'form-control')
                w.input_type = 'time'
            else:
                w.attrs.setdefault('class', 'form-control')


def _meta(model, **extra):
    attrs = {'model': model,
             'exclude': ('entreprise', 'cree_par', 'date_creation', 'date_modification')}
    attrs.update(extra)
    return type('Meta', (), attrs)


class CourrierForm(BootstrapModelForm):
    Meta = _meta(Courrier, widgets={'notes': forms.Textarea(attrs={'rows': 3})})


class RendezVousForm(BootstrapModelForm):
    Meta = _meta(RendezVous, widgets={'notes': forms.Textarea(attrs={'rows': 3})})


class VisiteurForm(BootstrapModelForm):
    Meta = _meta(Visiteur)


class AppelForm(BootstrapModelForm):
    Meta = _meta(Appel, widgets={'message': forms.Textarea(attrs={'rows': 3})})


class DocumentForm(BootstrapModelForm):
    Meta = _meta(DocumentSecretariat, widgets={'description': forms.Textarea(attrs={'rows': 3})})


class TacheForm(BootstrapModelForm):
    Meta = _meta(Tache, widgets={'description': forms.Textarea(attrs={'rows': 3})})


class ContactForm(BootstrapModelForm):
    Meta = _meta(Contact)


class ReunionForm(BootstrapModelForm):
    Meta = _meta(Reunion, widgets={
        'participants': forms.Textarea(attrs={'rows': 3}),
        'ordre_du_jour': forms.Textarea(attrs={'rows': 3}),
        'compte_rendu': forms.Textarea(attrs={'rows': 4}),
        'decisions': forms.Textarea(attrs={'rows': 3}),
    })
