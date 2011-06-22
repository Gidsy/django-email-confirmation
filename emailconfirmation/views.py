from django.shortcuts import render_to_response
from django.template import RequestContext

from emailconfirmation.models import EmailConfirmation
from django.conf import settings

def confirm_email(request, confirmation_key):
    confirmation_key = confirmation_key.lower()
    email_address = EmailConfirmation.objects.confirm_email(confirmation_key)
    
    next = getattr(settings, "EMAIL_CONFIRMATION_REDIRECT_URL", False)
    if next:
        return HttpResponseRedirect(next)
        
    return render_to_response("emailconfirmation/confirm_email.html", {
        "email_address": email_address,
    }, context_instance=RequestContext(request))