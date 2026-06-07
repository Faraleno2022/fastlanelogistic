"""Widgets personnalisés pour les formulaires Django"""
from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class SearchableSelectWidget(forms.Select):
    """
    Widget Select personnalisé avec:
    - Barre de recherche intégrée
    - Hauteur limitée à 15 lignes avec scrollbar
    - Support multi-tenant
    """
    template_name = 'widgets/searchable_select.html'

    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)
        if attrs is None:
            attrs = {}
        # Ajouter les classes Bootstrap
        if 'class' not in attrs:
            attrs['class'] = 'form-select searchable-select'
        else:
            attrs['class'] += ' searchable-select'
        self.attrs = attrs

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['searchable'] = True
        return context


class SearchableSelectMultipleWidget(forms.SelectMultiple):
    """Widget SelectMultiple personnalisé avec recherche"""
    template_name = 'widgets/searchable_select_multiple.html'

    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)
        if attrs is None:
            attrs = {}
        if 'class' not in attrs:
            attrs['class'] = 'form-select searchable-select'
        else:
            attrs['class'] += ' searchable-select'
        self.attrs = attrs

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['searchable'] = True
        return context


class ScrollableSelectWidget(forms.Select):
    """
    Widget Select simplifié avec:
    - Hauteur limitée à 15 lignes
    - Scrollbar visible
    """

    def __init__(self, attrs=None, choices=(), max_height_lines=15):
        super().__init__(attrs, choices)
        self.max_height_lines = max_height_lines
        if attrs is None:
            attrs = {}
        if 'class' not in attrs:
            attrs['class'] = 'form-select scrollable-select'
        else:
            attrs['class'] += ' scrollable-select'
        attrs['data-max-lines'] = str(max_height_lines)
        self.attrs = attrs
