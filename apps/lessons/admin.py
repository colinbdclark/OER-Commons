from django.contrib import admin
from lessons import models


admin.site.register(models.Lesson, admin.ModelAdmin)
admin.site.register(models.Chapter, admin.ModelAdmin)