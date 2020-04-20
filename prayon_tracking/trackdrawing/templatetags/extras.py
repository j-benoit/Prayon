from django import template

register = template.Library()


@register.filter(name='dict_first')
def dict_first(dict):
    # print(dict.values())
    # print(next(iter(dict.values())))
    return next(iter(dict.values()))