from django.contrib import admin
from lessons import models


admin.site.register(models.Lesson, admin.ModelAdmin)