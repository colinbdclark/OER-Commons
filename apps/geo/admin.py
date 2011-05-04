from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from geo.models import Country


site.register(Country, ModelAdmin)