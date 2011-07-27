from django.template import Context, Template
from django.template.loader import get_template
from django import template
from emailconfirmation.models import EmailAddress

register = template.Library()

@register.filter
def has_verified_email(user):
    primary_email = EmailAddress.objects.get_primary(user)
    if primary_email:
        return primary_email.verified
    return False
