from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from materials.models import Course, Library, CommunityItem
from materials.models.common import Country, GeneralSubject, \
    GradeLevel, Language, MediaFormat, GeographicRelevance
from materials.models.community import CommunityType, CommunityTopic
from materials.models.course import CourseMaterialType
from materials.models.library import LibraryMaterialType


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

site.register(Course, ModelAdmin)
site.register(Library, ModelAdmin)
site.register(CommunityItem, ModelAdmin)
