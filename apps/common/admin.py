from common import models
from django.contrib import admin


admin.site.register(models.StudentLevel, admin.ModelAdmin)


class GradeInline(admin.TabularInline):

    model = models.Grade
    extra = 1


class GradeSubLevelInline(admin.TabularInline):

    model = models.GradeSubLevel
    extra = 1


class GradeLevelAdmin(admin.ModelAdmin):

    list_display = ["name", "start_age", "end_age"]

    inlines = [
        GradeSubLevelInline
    ]


class GradeSubLevelAdmin(admin.ModelAdmin):

    list_display = ["name", "start_age", "end_age"]

    inlines = [
        GradeInline
    ]

class GradeAdmin(admin.ModelAdmin):

    list_display = ["name", "order", "start_age", "end_age"]
    list_editable = ["order"]


admin.site.register(models.GradeLevel, GradeLevelAdmin)
admin.site.register(models.GradeSubLevel, GradeSubLevelAdmin)
admin.site.register(models.Grade, GradeAdmin)
