from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active(context, url_name):
    try:
        current_url = context['request'].path
        url = reverse(url_name)
        return 'active' if current_url == url else ''
    except NoReverseMatch:
        return ''