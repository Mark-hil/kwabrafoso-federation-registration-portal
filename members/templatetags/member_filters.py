from django import template

register = template.Library()

@register.filter(name='split')
def split(value, key):
    """
    Split the string by the given delimiter and return a list.
    Usage: {{ some_string|split:"," }}
    """
    if not value:
        return []
    try:
        return str(value).split(key)
    except (AttributeError, TypeError):
        return []
