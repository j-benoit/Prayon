from django import template
from ..check import format_error
register = template.Library()


@register.filter(name='dict_first')
def dict_first(dict):
    # print(dict.values())
    # print(next(iter(dict.values())))
    return next(iter(dict.values()))

@register.filter(name='check_error')
def check_error(text):
    return format_error(text)

@register.filter(name='get_first_key_name')
def get_first_key_name(dict):
    list_key = list(dict.keys())
    return list_key[0]

@register.filter(name='get_key')
def get_key(dict, key):
    return dict[key]