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