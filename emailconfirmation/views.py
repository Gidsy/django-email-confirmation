from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from emailconfirmation.models import EmailConfirmation
from django.conf import settings
from django.contrib import messages


def confirm_email(request, confirmation_key):
    confirmation_key = confirmation_key.lower()
    email_address = EmailConfirmation.objects.confirm_email(confirmation_key)
    
    # if user is logged in check if the confirmed email is attached to his account
    # notify him if not
    if request.user.is_authenticated():
        if request.user != email_address.user:
            messages.warning(request, _("The email you confirmed does not belong to the account you are signed in with."))
                
    if getattr(settings, "EMAIL_CONFIRMATION_REDIRECT_TO_PROFILE", False):
        return HttpResponseRedirect(email_address.user.get_absolute_url)
                
    next = getattr(settings, "EMAIL_CONFIRMATION_REDIRECT_URL", False)
    if next:
        return HttpResponseRedirect(next)
        
    return render_to_response("emailconfirmation/confirm_email.html", {
        "email_address": email_address,
    }, context_instance=RequestContext(request))