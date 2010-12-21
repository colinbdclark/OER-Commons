from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from materials.models import Course, Library, CommunityItem
from materials.models.common import Country, GeneralSubject, \
    GradeLevel, Language, MediaFormat, GeographicRelevance, Keyword
from materials.models.community import CommunityType, CommunityTopic
from materials.models.course import CourseMaterialType
from materials.models.library import LibraryMaterialType
from materials.models.material import PUBLISHED_STATE


site.register(Country, ModelAdmin)
site.register(GeneralSubject, ModelAdmin)
site.register(GradeLevel, ModelAdmin)
site.register(Language, ModelAdmin)
site.register(CourseMaterialType, ModelAdmin)
site.register(LibraryMaterialType, ModelAdmin)
site.register(MediaFormat, ModelAdmin)
site.register(CommunityType, ModelAdmin)
site.register(CommunityTopic, ModelAdmin)
site.register(GeographicRelevance, ModelAdmin)

site.register(Keyword, ModelAdmin)


def publish(modeladmin, request, queryset):
    for obj in queryset:
        obj.workflow_state = PUBLISHED_STATE
        obj.save()
publish.short_description = u"Publish selected items"


class MaterialAdmin(ModelAdmin):

    list_display = ["title", "workflow_state", "creator"]
    list_filter = ['workflow_state', ]

    actions = [publish]


site.register(Course, MaterialAdmin)
site.register(Library, MaterialAdmin)
site.register(CommunityItem, MaterialAdmin)
