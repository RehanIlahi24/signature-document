from django import template

register = template.Library()

@register.filter
def get_filename(value):
    return value.split('/')[-1]