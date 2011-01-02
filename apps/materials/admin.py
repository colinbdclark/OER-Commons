from django import forms
from django.contrib.admin.options import ModelAdmin, TabularInline, \
    StackedInline
from django.contrib.admin.sites import site
from materials.models import Course, Library, CommunityItem
from materials.models.common import Country, GeneralSubject, GradeLevel, \
    Language, MediaFormat, GeographicRelevance, Keyword, Author
from materials.models.community import CommunityType, CommunityTopic
from materials.models.course import CourseMaterialType
from materials.models.library import LibraryMaterialType
from materials.models.material import PUBLISHED_STATE
from materials.models.microsite import Microsite, Topic
from materials.views.forms import KeywordsField


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
site.register(Author, ModelAdmin)


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


class AdminKeywordsWidget(forms.Textarea):

    def render(self, name, value, attrs=None):
        if isinstance(value, list):
            value = u"\n".join(value)
        return super(AdminKeywordsWidget, self).render(name, value, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        return [v for v in data.get(name, u"").split("\n") if v]


class MicrositeForm(forms.ModelForm):

    keywords = KeywordsField(widget=AdminKeywordsWidget())

    class Meta:
        model = Microsite


class MicrositeAdmin(ModelAdmin):

    form = MicrositeForm


site.register(Microsite, MicrositeAdmin)


class TopicForm(forms.ModelForm):

    keywords = KeywordsField(widget=AdminKeywordsWidget())

    class Meta:
        model = Topic


class TopicAdmin(ModelAdmin):
    list_display = ["name", "parent", "microsite"]
    form = TopicForm


site.register(Topic, TopicAdmin)
