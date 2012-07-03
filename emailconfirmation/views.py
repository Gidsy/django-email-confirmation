from django.http import HttpResponseRedirect
from emailconfirmation.models import EmailConfirmation
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse


def confirm_email(request, confirmation_key):
    confirmation_key = confirmation_key.lower()
    email_address = EmailConfirmation.objects.confirm_email(confirmation_key)

    if hasattr(settings, "EMAIL_CONFIRM_REDIRECT_URL"):
        next_url = reverse(settings.EMAIL_CONFIRM_REDIRECT_URL)
    else:
        next_url = reverse('acct_general_settings')

    login_url = reverse('login')

    #if there is no email then its prob expired
    if not email_address:
        try:
            # if we can find a expired email confirmation then send it again and return error message
            confirmation = EmailConfirmation.objects.get(confirmation_key=confirmation_key)
            EmailConfirmation.objects.send_confirmation(confirmation.email_address)
            EmailConfirmation.objects.delete_expired_confirmations()

            messages.warning(request, _("Whoops, that link doesn't seem to be working anymore!"))
            messages.success(request, _("Don't worry, we have sent you a new email. Please check"
                "your email account and use the new confirmation key."))
            if request.user.is_authenticated():
                # if user is logged in we want to show the error message on account page
                return HttpResponseRedirect(next_url)
            else:
                # otherwise we display the error on the login page, prefill the email
                return HttpResponseRedirect("%s?email=%s&next=%s" % (login_url,
                    confirmation.email_address.user.email, next_url))

        except EmailConfirmation.DoesNotExist:
            # if not then it was the wrong, code. the view takes care of that
            if request.user.is_authenticated():
                # if user is logged in we want to show the error message on account page
                # we don't want to resend the confirmation since we did not find an expired one
                messages.warning(request, _("Whoops, that link doesn't work anymore! Re-send the "
                    "confirmation email by logging in with the corresponding account."))
                return HttpResponseRedirect(next_url)
            else:
                # otherwise we display the error on the login page, in this case we can't fill the email
                messages.warning(request, _("Whoops, that link doesn't seem to exist!  Please login "
                    "and re-send the confirmation email."))
                return HttpResponseRedirect("%s?next=%s" % (login_url, next_url))

    # the email was confirmed, now it depends if user is logged in or not and if it was of a different user
    if request.user.is_authenticated():
        if request.user == email_address.user:
            # success, just display message on account page
            messages.success(request, _("Thanks a lot, you've successfully confirmed your email address. Have fun!"))
            return HttpResponseRedirect(next_url)
        else:
            # success, but also display a warning telling the user about the different account
            messages.warning(request, _("The email you confirmed does not belong to the account you are signed in with."))
            messages.success(request, _("Thanks a lot! You succesfully confirmed the email address."))
            return HttpResponseRedirect(next_url)
    else:
        # if user is logged out we go to login page and display success message
        messages.success(request, _("Thanks a lot! You succesfully confirmed your email address."))
        return HttpResponseRedirect("%s?email=%s&next=%s" % (login_url, email_address.user.email, next_url))
