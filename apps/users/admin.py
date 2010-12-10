from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from users.models import RegistrationConfirmation


site.register(RegistrationConfirmation, ModelAdmin)
