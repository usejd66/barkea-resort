from django import template

from resort.images import responsive_attrs

register = template.Library()


@register.simple_tag
def responsive(static_path, sizes='100vw'):
    """Usage: <img src="{% static p %}"{% responsive p '(min-width: 992px) 33vw, 100vw' %}>"""
    return responsive_attrs(static_path, sizes)
