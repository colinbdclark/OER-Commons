from django import forms
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site
from materials.admin.community_item import CommunityItemAdmin
from materials.admin.course import CourseAdmin
from materials.admin.library import LibraryAdmin
from materials.models import Course, Library, CommunityItem
from materials.models.common import GeneralSubject, GradeLevel, \
    Language, MediaFormat, GeographicRelevance, Keyword, Author, Collection
from materials.models.community import CommunityType, CommunityTopic
from materials.models.course import CourseMaterialType
from materials.models.library import LibraryMaterialType
from materials.models.microsite import Microsite, Topic
from utils.forms import AutocompleteListField


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
site.register(Author, ModelAdmin)

site.register(Course, CourseAdmin)
site.register(Library, LibraryAdmin)
site.register(CommunityItem, CommunityItemAdmin)


class AdminKeywordsWidget(forms.Textarea):

    def render(self, name, value, attrs=None):
        if isinstance(value, list):
            value = u"\n".join(value)
        return super(AdminKeywordsWidget, self).render(name, value, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        return [v for v in data.get(name, u"").split("\n") if v]


class MicrositeForm(forms.ModelForm):

    keywords = AutocompleteListField(model=Keyword, widget=AdminKeywordsWidget())

    class Meta:
        model = Microsite


class MicrositeAdmin(ModelAdmin):

    form = MicrositeForm


site.register(Microsite, MicrositeAdmin)


class TopicForm(forms.ModelForm):

    keywords = AutocompleteListField(model=Keyword, widget=AdminKeywordsWidget())

    class Meta:
        model = Topic


class TopicAdmin(ModelAdmin):
    list_display = ["name", "parent", "microsite"]
    form = TopicForm


site.register(Topic, TopicAdmin)


class CollectionAdmin(ModelAdmin):

    search_fields = ["name"]
    list_display = ["name", "disable_alignment_evaluation"]
    list_filter = ["disable_alignment_evaluation"]

site.register(Collection, CollectionAdmin)
