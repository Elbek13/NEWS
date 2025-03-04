from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key)

@register.filter
def list_get(lst, index):
    return lst[index] if len(lst) > index else None