from django.template import Context, Template
from django.template.loader import get_template
from django import template
from models import EmailAddress

register = template.Library()

@register.simple_tag()
def has_verified_email(user):
    return EmailAddress.objects.get_primary(user)
