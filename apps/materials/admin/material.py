from django.contrib.admin.options import ModelAdmin
from materials.models.material import PUBLISHED_STATE


def publish(modeladmin, request, queryset):
    for obj in queryset:
        obj.workflow_state = PUBLISHED_STATE
        obj.save()
publish.short_description = u"Publish selected items"


class MaterialAdmin(ModelAdmin):

    list_display = ["title", "workflow_state", "creator"]
    list_filter = ["workflow_state", "featured"]

    actions = [publish]


