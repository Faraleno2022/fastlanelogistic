from django import template

register = template.Library()


@register.filter(name="dictget")
def dictget(d, key):
    """Accès à dict[key] depuis un template Django.
    Utilisation : {{ monDict|dictget:"maClef" }}
    """
    if d is None:
        return ""
    try:
        return d.get(key, "")
    except AttributeError:
        return ""
