from django import template

register = template.Library()

@register.filter
def get_attribute(obj, attr):
    return getattr(obj, attr, '')

@register.filter
def get_bulan_value(obj, bulan):
    return getattr(obj, bulan, '')

@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr, None)

@register.filter
def split(value, delimiter):
    return value.split(delimiter)
