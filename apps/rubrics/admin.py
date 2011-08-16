from django.contrib import admin
from rubrics import models


admin.site.register(models.RubricScoreValue, admin.ModelAdmin)
admin.site.register(models.StandardAlignmentScoreValue, admin.ModelAdmin)


class RubricScoreValueInline(admin.TabularInline):

    model = models.RubricScoreValue
    extra = 0


class RubricAdmin(admin.ModelAdmin):

    inlines = [
        RubricScoreValueInline,
    ]


admin.site.register(models.Rubric, RubricAdmin)
