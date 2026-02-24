from django import template

register = template.Library()

@register.filter(name='split_allergies')
def split_allergies(value, delimiter=','):
    """Split the allergies string by delimiter and return a list."""
    if not value:
        return []
    return [a.strip() for a in str(value).split(delimiter) if a.strip()]
