from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def intcomma(value):
    """
    Formate un nombre avec des séparateurs de milliers.
    Équivalent du filtre intcomma de Django.
    """
    try:
        value = str(value)
        if '.' in value:
            integer_part, decimal_part = value.split('.')
        else:
            integer_part, decimal_part = value, ''
        
        # Ajouter les séparateurs de milliers
        if len(integer_part) > 3:
            integer_part = '{:,}'.format(int(integer_part))
        
        if decimal_part:
            return f"{integer_part}.{decimal_part}"
        else:
            return integer_part
    except (ValueError, TypeError):
        return value

@register.filter
def intcomma_float(value, arg=None):
    """
    Combine intcomma avec floatformat.
    Usage: {{ value|intcomma_float:"2" }}
    """
    if arg is None:
        return intcomma(value)
    try:
        formatted = floatformat(value, arg)
        return intcomma(formatted)
    except:
        return intcomma(value)
