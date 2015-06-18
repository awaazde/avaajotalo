from django import template
from django.conf import settings
from otalo.ao.models import Transaction, Message_forum

register = template.Library()

# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

@register.filter
def lookup(d, key):
    pair = Transaction.TYPE[key]
    return pair[1]
