from django import template

register = template.Library()


@register.filter
def get_item(d, key):
    """Accès à d[key] dans un template (dict indexé par clé dynamique)."""
    try:
        return d.get(key, '')
    except AttributeError:
        return ''
