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

    inlines = [
        GradeSubLevelInline
    ]


class GradeSubLevelAdmin(admin.ModelAdmin):

    inlines = [
        GradeInline
    ]

class GradeAdmin(admin.ModelAdmin):

    list_display = ["name", "order"]
    list_editable = ["order"]


admin.site.register(models.GradeLevel, GradeLevelAdmin)
admin.site.register(models.GradeSubLevel, GradeSubLevelAdmin)
admin.site.register(models.Grade, GradeAdmin)
admin.site.register(models.MediaFormat, admin.ModelAdmin)
