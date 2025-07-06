from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key, key)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, key)

@register.filter
def replace(value, args):
    old, new = args.split(',')
    return value.replace(old, new)