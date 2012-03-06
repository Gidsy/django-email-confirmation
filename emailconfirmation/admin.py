from django.contrib import admin
from emailconfirmation.models import EmailAddress, EmailConfirmation


class EmailAddressAdmin(admin.ModelAdmin): 
    list_display = ['email', 'user']
    search_fields = ['email', 'user__username']

admin.site.register(EmailAddress, EmailAddressAdmin)
admin.site.register(EmailConfirmation)
