from django import template

register = template.Library()

@register.filter
def split(value, delimiter=","):
    return value.split(delimiter)

@register.filter
def trim(value):
    if isinstance(value, str):
        return value.strip()
    return value