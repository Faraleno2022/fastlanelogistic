"""
Filtres de template personnalisés pour le formatage des montants et nombres
"""
from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()


@register.filter(name='montant')
def format_montant(value, devise='GNF'):
    """
    Formate un montant avec des espaces comme séparateurs de milliers
    Usage: {{ montant|montant }} ou {{ montant|montant:"EUR" }}
    Exemple: 1234567 -> 1 234 567 GNF
    """
    if value is None or value == '':
        return '0 ' + devise
    
    try:
        # Convertir en nombre
        if isinstance(value, str):
            value = value.replace(',', '.').replace(' ', '')
        
        number = Decimal(str(value))
        
        # Séparer partie entière et décimale
        if number == int(number):
            # Nombre entier
            formatted = format_number_with_spaces(int(number))
        else:
            # Nombre décimal
            parts = str(number).split('.')
            formatted = format_number_with_spaces(int(parts[0]))
            if len(parts) > 1 and int(parts[1]) > 0:
                formatted += ',' + parts[1][:2]
        
        return f"{formatted} {devise}"
    except (ValueError, TypeError, InvalidOperation):
        return str(value)


@register.filter(name='nombre')
def format_nombre(value):
    """
    Formate un nombre avec des espaces comme séparateurs de milliers
    Usage: {{ nombre|nombre }}
    Exemple: 1234567 -> 1 234 567
    """
    if value is None or value == '':
        return '0'
    
    try:
        if isinstance(value, str):
            value = value.replace(',', '.').replace(' ', '')
        
        number = Decimal(str(value))
        
        if number == int(number):
            return format_number_with_spaces(int(number))
        else:
            parts = str(number).split('.')
            formatted = format_number_with_spaces(int(parts[0]))
            if len(parts) > 1 and int(parts[1]) > 0:
                formatted += ',' + parts[1][:2]
            return formatted
    except (ValueError, TypeError):
        return str(value)


@register.filter(name='montant_gnf')
def format_montant_gnf(value):
    """Raccourci pour formater en GNF"""
    return format_montant(value, 'GNF')


@register.filter(name='montant_usd')
def format_montant_usd(value):
    """Raccourci pour formater en USD"""
    return format_montant(value, 'USD')


@register.filter(name='montant_eur')
def format_montant_eur(value):
    """Raccourci pour formater en EUR"""
    return format_montant(value, 'EUR')


def format_number_with_spaces(number):
    """
    Formate un nombre entier avec des espaces comme séparateurs de milliers
    Exemple: 1234567 -> 1 234 567
    """
    if number < 0:
        return '-' + format_number_with_spaces(abs(number))
    
    s = str(int(number))
    groups = []
    while s:
        groups.append(s[-3:])
        s = s[:-3]
    return ' '.join(reversed(groups))


