from django.contrib.admin.options import ModelAdmin
from materials.models.material import PUBLISHED_STATE


def publish(modeladmin, request, queryset):
    for obj in queryset:
        obj.workflow_state = PUBLISHED_STATE
        obj.save()
publish.short_description = u"Publish selected items"


class MaterialAdmin(ModelAdmin):

    def url(self):
        return """<a target="_blank" href="%s">%s</a>""" % (self.url, self.url)
    url.allow_tags = True
    
    list_display = ["title", url, "http_status", "workflow_state", "creator"]
    list_filter = ["workflow_state", "featured", "http_status"]

    actions = [publish]


