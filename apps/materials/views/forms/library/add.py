from common.models import GradeLevel, MediaFormat
from core.forms import AutoCreateField, MultipleAutoCreateInput, \
    MultipleAutoCreateField, AutocompleteListWidget
from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.models import ModelForm
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from materials.models.common import GeneralSubject,\
    Language, GeographicRelevance, Keyword
from materials.models.library import LibraryMaterialType, Library
from materials.models.material import PRIVATE_STATE, PUBLISHED_STATE
from materials.views.forms import LICENSE_TYPES, CC_OLD_LICENSES, \
    LicenseTypeFieldRenderer, SubmissionFormBase, LanguagesField
from utils.decorators import login_required


class AddForm(SubmissionFormBase, ModelForm):

    title = forms.CharField(label=u"Title:",
                            widget=forms.TextInput(
                            attrs={"class": "text wide"}),
                            max_length=500)

    url = forms.URLField(label=u"URL Pointer:", initial=u"http://",
                         widget=forms.TextInput(
                         attrs={"class": "text wide"}))

    abstract = forms.CharField(label=u"Abstract:",
                               widget=forms.Textarea(
                               attrs={"class": "text wide"}))

    institution = AutoCreateField(
        "name",
        label=u"Institution:",
        required=False,
        widget=forms.TextInput(attrs={"class": "text wide"})
    )

    collection = AutoCreateField(
        "name",
        label=u"Collection:",
        required=False,
        widget=forms.TextInput(attrs={"class": "text wide"})
    )

    authors = MultipleAutoCreateField(
        "name",
        label=u"Authors:",
        required=False,
        widget=MultipleAutoCreateInput(attrs={"class": "text wide"})
    )

    tech_requirements = forms.CharField(label=u"Notable Hard/Software:",
                                     required=False,
                                     widget=forms.Textarea(
                                     attrs={"class": "text wide"}))

    keywords = MultipleAutoCreateField("name", widget=AutocompleteListWidget(Keyword, "name"), label=u"Keywords")

    general_subjects = forms.ModelMultipleChoiceField(
                                GeneralSubject.objects.all(),
                                label=u"Subject Areas",
                                widget=forms.CheckboxSelectMultiple())

    grade_levels = forms.ModelMultipleChoiceField(GradeLevel.objects.all(),
                                label=u"Grade Levels",
                                widget=forms.CheckboxSelectMultiple())

    languages = LanguagesField(Language.objects.all(),
                                label=u"Language",
                                required=True,
                                initial=Language.objects.get(name=u"English"))

    geographic_relevance = forms.ModelMultipleChoiceField(GeographicRelevance.objects.all(),
                                label=u"Intended Regional Relevance",
                                required=True,
                                widget=forms.CheckboxSelectMultiple(),
                                initial=[GeographicRelevance.objects.get(name=u"All")])

    material_types = forms.ModelMultipleChoiceField(LibraryMaterialType.objects.all(),
                                label=u"Material Types",
                                widget=forms.CheckboxSelectMultiple())

    media_formats = forms.ModelMultipleChoiceField(MediaFormat.objects.all(),
                                label=u"Media Formats",
                                widget=forms.CheckboxSelectMultiple())

    license_type = forms.ChoiceField(choices=LICENSE_TYPES, initial="cc",
                                     widget=forms.RadioSelect(renderer=LicenseTypeFieldRenderer))

    license_cc = forms.URLField(required=False, widget=forms.HiddenInput())

    license_cc_old = forms.ChoiceField(choices=CC_OLD_LICENSES,
                                       required=False,
                                       widget=forms.Select())

    license_custom_url = forms.URLField(label=u"License URL:",
                        required=False,
                        widget=forms.TextInput(attrs={"class": "text wide"}))

    license_description = forms.CharField(label=u"License Description:",
                        required=False,
                        help_text=u"Please enter any additional information you might have about the license.",
                        widget=forms.Textarea(attrs={"class": "text wide"}))

    copyright_holder = forms.CharField(label=u"License / Copyright Holder:",
                        required=False,
                        help_text=u"Please enter the name of the person or organization owning or managing rights over the resource.",
                        widget=forms.TextInput(attrs={"class": "text wide"}))

    license = forms.Field(label=u"Conditions of Use", required=False)

    def clean_url(self):
        value = self.cleaned_data["url"]
        instance = getattr(self, "instance", None)
        qs = Library.objects.filter(url=value)
        if instance and instance.id:
            qs = qs.exclude(id=instance.id)
        if qs.count():
            raise forms.ValidationError(u"This URL is registered already.")
        return value

    def __init__(self, *args, **kwargs):
        super(AddForm, self).__init__(*args, **kwargs)
        self.set_initial_license_data()
        self.fields["collection"].initial = u"Individual Authors"

    class Meta:
        model = Library
        fields = ["title", "url", "abstract", "institution", "collection",
                  "authors", "tech_requirements", "keywords", "general_subjects",
                  "grade_levels", "material_types", "media_formats",
                  "languages", "geographic_relevance",
                  "license_type", "license_cc", "license_cc_old",
                  "license_custom_url", "license_description",
                  "copyright_holder", "license"]


class AddFormStaff(AddForm):

    content_creation_date = forms.DateField(label=u"Content Creation Date:",
                                  input_formats=["%m/%d/%Y"],
                                  required=False,
                                  widget=forms.DateInput(
                                  attrs={"class": "text"},
                                  format="%m/%d/%Y"))

    languages = LanguagesField(Language.objects.all(),
                                label=u"Language",
                                required=True,
                                initial=Language.objects.get(name=u"English"))

    geographic_relevance = forms.ModelMultipleChoiceField(GeographicRelevance.objects.all(),
                                label=u"Intended Regional Relevance",
                                required=True,
                                widget=forms.CheckboxSelectMultiple(),
                                initial=[GeographicRelevance.objects.get(name=u"All")])

    curriculum_standards = forms.CharField(required=False,
                       label=u"Curriculum Standards",
                       widget=forms.Textarea(attrs={"class": "text"}))

    is_homepage = forms.BooleanField(required=False, initial=False,
                         label=u"Is this the home page for the library/collection?",
                                 widget=forms.CheckboxInput())

    featured = forms.BooleanField(required=False, initial=False,
                         label=u"Marked as Featured",
                                 widget=forms.CheckboxInput())

    in_rss = forms.BooleanField(required=False, initial=False,
                         label=u"Include this item in RSS?",
                                 widget=forms.CheckboxInput())

    rss_description = forms.CharField(required=False,
                                   label=u"RSS short description",
                                   widget=forms.Textarea(attrs={"class": "text"}))

    rss_timestamp = forms.SplitDateTimeField(required=False,
                                   input_date_formats=["%m/%d/%Y"],
                                   input_time_formats=["%H:%M"],
                                   label=u"RSS date and time",
                                   widget=forms.SplitDateTimeWidget(
                                            date_format="%m/%d/%Y",
                                            time_format="%H:%M",
                                            attrs={"class": "text"}))

    def __init__(self, *args, **kwargs):
        super(AddForm, self).__init__(*args, **kwargs)
        self.fields["institution"].required = True
        self.set_initial_license_data()

    class Meta:
        model = Library
        fields = ["title", "url", "abstract", "institution", "collection",
                  "content_creation_date", "authors",
                  "tech_requirements", "keywords", "general_subjects",
                  "grade_levels", "material_types", "media_formats", "languages",
                  "geographic_relevance", "curriculum_standards", "is_homepage",
                  "featured", "in_rss", "rss_description", "rss_timestamp",
                  "license_type", "license_cc", "license_cc_old",
                  "license_custom_url", "license_description",
                  "copyright_holder", "license"]


@login_required
def add(request, model=None):

    if request.user.is_staff:
        form_class = AddFormStaff
        template = "materials/forms/library/add-staff.html"
        page_title = u"Add Library or Collection"
    else:
        form_class = AddForm
        template = "materials/forms/library/add.html"
        page_title = u"Contribute Library or Collection"

    breadcrumbs = [
        {"url": model.get_parent_url(), "title": model._meta.verbose_name_plural},
        {"url": reverse("materials:libraries:add"), "title": page_title}
    ]

    if request.method == "POST":
        form = form_class(request.POST)

        if form.is_valid():
            object = form.save(commit=False)
            object.creator = request.user
            if request.user.is_staff:
                object.workflow_state = PUBLISHED_STATE
            else:
                object.workflow_state = PRIVATE_STATE
            object.save()
            form.save_m2m()
            messages.success(request, u"New library was added.")
            return redirect(object)
        else:
            messages.error(request, u"Please correct the indicated errors.")
    else:
        form = form_class()

    return direct_to_template(request, template, locals())
