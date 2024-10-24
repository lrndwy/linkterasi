from django import template

register = template.Library()

@register.filter
def get_attribute(obj, attr):
    return getattr(obj, attr, '')

@register.filter
def get_bulan_value(obj, bulan):
    return getattr(obj, bulan, '')
