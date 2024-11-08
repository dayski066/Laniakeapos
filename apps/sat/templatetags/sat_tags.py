from django import template
register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def mod(value, arg):
    return int(value) % arg

@register.filter
def mul(value, arg):
    return int(value) * arg

@register.filter
def divisibleby(value, arg):
    return int(int(value) / arg)