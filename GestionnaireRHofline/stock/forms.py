"""Formulaires du module Stock (Bootstrap + filtrage des FK par entreprise)."""
from django import forms
from .models import (
    Depot, CategorieArticle, Fournisseur, Demandeur, Article,
    EntreeStock, SortieStock, Inventaire, CommandeAchat,
)

_EXCLUDE = ('entreprise', 'cree_par', 'date_creation', 'date_modification')


class BootstrapModelForm(forms.ModelForm):
    """Applique Bootstrap et filtre les ModelChoiceField par entreprise."""

    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            # Filtre les listes déroulantes liées à l'entreprise
            if isinstance(field, forms.ModelChoiceField) and entreprise is not None:
                model = field.queryset.model
                if any(f.name == 'entreprise' for f in model._meta.fields):
                    field.queryset = field.queryset.filter(entreprise=entreprise)
            if isinstance(w, forms.CheckboxInput):
                w.attrs.setdefault('class', 'form-check-input')
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                w.attrs.setdefault('class', 'form-select')
            elif isinstance(w, forms.DateInput):
                w.attrs.setdefault('class', 'form-control'); w.input_type = 'date'
            else:
                w.attrs.setdefault('class', 'form-control')


def _meta(model, **extra):
    attrs = {'model': model, 'exclude': _EXCLUDE}
    attrs.update(extra)
    return type('Meta', (), attrs)


class DepotForm(BootstrapModelForm):
    Meta = _meta(Depot)


class CategorieForm(BootstrapModelForm):
    Meta = _meta(CategorieArticle)


class FournisseurForm(BootstrapModelForm):
    Meta = _meta(Fournisseur)


class DemandeurForm(BootstrapModelForm):
    Meta = _meta(Demandeur)


class ArticleForm(BootstrapModelForm):
    Meta = _meta(Article, exclude=_EXCLUDE + ('quantite_stock',),
                 widgets={'date_expiration': forms.DateInput(attrs={'type': 'date'})})


class EntreeForm(BootstrapModelForm):
    Meta = _meta(EntreeStock)


class SortieForm(BootstrapModelForm):
    Meta = _meta(SortieStock)


class InventaireForm(BootstrapModelForm):
    Meta = _meta(Inventaire, widgets={'notes': forms.Textarea(attrs={'rows': 3})})


class CommandeForm(BootstrapModelForm):
    Meta = _meta(CommandeAchat, widgets={'notes': forms.Textarea(attrs={'rows': 3})})
