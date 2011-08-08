from django.contrib import admin
from oer import models


admin.site.register(models.OER, admin.ModelAdmin)
admin.site.register(models.Section, admin.ModelAdmin)