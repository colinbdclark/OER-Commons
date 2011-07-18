from common import models
from django.contrib import admin


admin.site.register(models.GeneralSubject, admin.ModelAdmin)
admin.site.register(models.StudentLevel, admin.ModelAdmin)