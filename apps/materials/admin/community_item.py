from common.models import GeneralSubject
from django import forms
from django.conf import settings
from django.contrib.admin.util import unquote
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.generic.simple import redirect_to
from material import MaterialAdmin
from materials.admin.course import AuthorsFormSet
from materials.admin.fields import LicenseFields
from materials.models.common import Author, GradeLevel, Language, \
    GeographicRelevance, Keyword
from materials.models.community import CommunityType, CommunityTopic, \
    CommunityItem
from materials.views.forms import RSSFields
from utils.forms import AutocompleteListField


COMMUNITY_ITEM_ADD_FIELDS = ["creator", "title", "url", "abstract", "workflow_state",
                     "content_creation_date", "tech_requirements", "keywords",
                     "general_subjects", "grade_levels", "languages",
                     "geographic_relevance", "community_types", "community_topics",
                     "featured", "in_rss", "rss_description", "rss_timestamp",
                     "license_name", "license_url",
                     "license_description", "copyright_holder", "license"]


MAIN_FIELDS_ADD = ["creator", "title", "url", "abstract", "workflow_state",
                   "content_creation_date", "tech_requirements", "keywords",
                   "general_subjects", "grade_levels", "languages",
                   "geographic_relevance",
                   "community_types", "community_topics", "featured"]
MAIN_FIELDS_CHANGE = ["slug"] + MAIN_FIELDS_ADD


class CommunityItemAddForm(forms.ModelForm, LicenseFields, RSSFields):


    creator = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
    title = forms.CharField(widget=forms.TextInput(attrs={"size": 150}))
    url = forms.URLField(widget=forms.TextInput(attrs={"size": 150}))
    abstract = forms.CharField(widget=forms.Textarea(
                                             attrs={"rows": 10, "cols": 108}))
    content_creation_date = forms.DateField(input_formats=["%m/%d/%Y"],
                                            widget=forms.DateInput(
                                              format="%m/%d/%Y"),
                                              required=False)
    tech_requirements = forms.CharField(required=False,
                                        widget=forms.Textarea(
                                              attrs={"rows": 5, "cols": 50}))
    general_subjects = forms.ModelMultipleChoiceField(
                                GeneralSubject.objects.all(),
                                widget=forms.CheckboxSelectMultiple())
    grade_levels = forms.ModelMultipleChoiceField(
                                GradeLevel.objects.all(),
                                widget=forms.CheckboxSelectMultiple())
    languages = forms.ModelMultipleChoiceField(
                                Language.objects.all(),
                                widget=forms.SelectMultiple())
    geographic_relevance = forms.ModelMultipleChoiceField(
                                GeographicRelevance.objects.all(),
                                required=False,
                                widget=forms.CheckboxSelectMultiple())

    community_types = forms.ModelMultipleChoiceField(
                                CommunityType.objects.all(),
                                widget=forms.CheckboxSelectMultiple())

    community_topics = forms.ModelMultipleChoiceField(
                                CommunityTopic.objects.all(),
                                widget=forms.CheckboxSelectMultiple())

    keywords = AutocompleteListField(model=Keyword)

    featured = forms.BooleanField(required=False, initial=False,
                         label=u"Marked as Featured",
                                 widget=forms.CheckboxInput())

    in_rss = forms.BooleanField(required=False, initial=False,
                         label=u"Include this item in RSS?",
                                 widget=forms.CheckboxInput())

    rss_description = forms.CharField(required=False,
                                   label=u"RSS short description",
                                   widget=forms.Textarea({"rows": 5, "cols": 50}))

    rss_timestamp = forms.SplitDateTimeField(required=False,
                                   label=u"RSS date and time",
                                   input_date_formats=["%m/%d/%Y"],
                                   widget=forms.SplitDateTimeWidget(
                                                date_format="%m/%d/%Y"))

    license_name = forms.CharField(widget=forms.TextInput(attrs={"size": 150}))
    license_url = forms.URLField(widget=forms.TextInput(attrs={"size": 150}),
                                 required=False)
    license_description = forms.CharField(widget=forms.Textarea(
                                             attrs={"rows": 5, "cols": 50}),
                                         required=False)
    copyright_holder = forms.CharField(widget=forms.TextInput(attrs={"size": 150}),
                                       required=False)

    license = forms.Field(required=False)

    def clean_url(self):
        value = self.cleaned_data["url"]
        instance = getattr(self, "instance", None)
        qs = CommunityItem.objects.filter(url=value)
        if instance and instance.id:
            qs = qs.exclude(id=instance.id)
        if qs.count():
            raise forms.ValidationError(u"This URL is registered already.")
        return value

    class Meta:
        model = CommunityItem
        fields = COMMUNITY_ITEM_ADD_FIELDS

    def __init__(self, *args, **kwargs):
        super(CommunityItemAddForm, self).__init__(*args, **kwargs)
        self.set_initial_license_data()


class CommunityItemChangeForm(CommunityItemAddForm):

    slug = forms.SlugField()

    class Meta:
        model = CommunityItem
        fields = ["slug"] + COMMUNITY_ITEM_ADD_FIELDS


class CommunityItemAdmin(MaterialAdmin):

    def add_view(self, request, form_url='', extra_context=None):
        model = self.model
        opts = model._meta

        if request.method == "POST":
            if "cancel" in request.POST:
                return redirect_to(request, reverse("admin:materials_communityitem_changelist"))
            form = CommunityItemAddForm(request.POST, initial=dict(creator=request.user))
            authors_formset = AuthorsFormSet(request.POST, prefix="authors", queryset=Author.objects.none())
            if form.is_valid() and authors_formset.is_valid():
                obj = form.save()
                saved_authors = authors_formset.save()
                # TODO: reindex all related objects if author info were changed
                for author in saved_authors:
                    obj.authors.add(author)
                obj.save()
                return self.response_add(request, obj)
        else:
            form = CommunityItemAddForm(initial=dict(creator=request.user))
            authors_formset = AuthorsFormSet(prefix="authors", queryset=Author.objects.none())

        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'form': form,
            'authors_formset': authors_formset,
            'main_fields': MAIN_FIELDS_CHANGE,
            'is_popup': request.REQUEST.has_key('_popup'),
            'show_delete': False,
            'app_label': opts.app_label,
            'media': mark_safe(self.media + forms.Media(js=['%s%s' % (settings.ADMIN_MEDIA_PREFIX, 'js/collapse.min.js')])),
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url, add=True)


    def change_view(self, request, object_id, extra_context=None):
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})


        if request.method == "POST":
            if "cancel" in request.POST:
                return redirect_to(request, reverse("admin:materials_communityitem_changelist"))
            form = CommunityItemAddForm(request.POST, instance=obj)
            authors_formset = AuthorsFormSet(request.POST, prefix="authors", queryset=obj.authors.all())
            if form.is_valid() and authors_formset.is_valid():
                obj = form.save()
                saved_authors = authors_formset.save()
                # TODO: reindex all related objects if author info were changed
                existing_authors = list(obj.authors.all())
                for author in saved_authors:
                    if author not in existing_authors:
                        obj.authors.add(author)
                obj.save()
                return self.response_change(request, obj)
        else:
            form = CommunityItemAddForm(instance=obj)
            authors_formset = AuthorsFormSet(prefix="authors", queryset=obj.authors.all())

        tags = obj.tags.distinct().values_list("name", flat=True)

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'form': form,
            'authors_formset': authors_formset,
            'main_fields': MAIN_FIELDS_CHANGE,
            'tags': tags,
            'object_id': object_id,
            'original': obj,
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
            'media': mark_safe(self.media + forms.Media(js=['%s%s' % (settings.ADMIN_MEDIA_PREFIX, 'js/collapse.min.js')])),
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=obj)
