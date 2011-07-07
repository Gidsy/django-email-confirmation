from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from emailconfirmation.models import EmailConfirmation
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _

def confirm_email(request, confirmation_key):
    confirmation_key = confirmation_key.lower()
    email_address = EmailConfirmation.objects.confirm_email(confirmation_key)
    
    if not email_address: #if there is no email then its prob expired
        try:
            confirmation = EmailConfirmation.objects.get(confirmation_key=\
                                                         confirmation_key)
            if confirmation.key_expired():
                EmailConfirmation.objects.send_confirmation(confirmation.email_address)
                EmailConfirmation.objects.delete_expired_confirmations()
                return render_to_response("emailconfirmation/resent_confirmation.html", {
                }, context_instance=RequestContext(request))
        except EmailConfirmation.DoesNotExist:
            # if not then it was the wrong, code. the view takes care of that
            pass
            
    else:
        # if user is logged in check if the confirmed email is attached to his account
        # notify him if not
        if request.user.is_authenticated():
            if request.user != email_address.user:
                messages.warning(request, _("The email you confirmed does not belong \
                                            to the account you are signed in with."))
        
        redirect_to_profile = getattr(settings, "EMAIL_CONFIRMATION_REDIRECT_TO_PROFILE", False)
        next = getattr(settings, "EMAIL_CONFIRMATION_REDIRECT_URL", False)
        
        if next or redirect_to_profile:
            messages.success(request, \
                         _("You successfully confirmed your email address %(email)s")\
                                                     %{'email':email_address.email})
            if redirect_to_profile:
                return HttpResponseRedirect(email_address.user.get_absolute_url())
                        
            if next:
                return HttpResponseRedirect(next)
        
    return render_to_response("emailconfirmation/confirm_email.html", {
        "email_address": email_address,
    }, context_instance=RequestContext(request))