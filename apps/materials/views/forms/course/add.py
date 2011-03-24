from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.models import ModelForm
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from materials.models.common import GeneralSubject, GradeLevel, MediaFormat, \
    Language, GeographicRelevance, COU_BUCKETS
from materials.models.course import Course, CourseMaterialType, COURSE_OR_MODULE
from materials.models.material import PRIVATE_STATE, PUBLISHED_STATE
from materials.views.forms import AuthorsField, KeywordsField, LICENSE_TYPES, \
    CC_OLD_LICENSES, LicenseTypeFieldRenderer, SubmissionFormBase, LanguagesField
from materials.views.forms.course import InstitutionField, DerivedFields, \
    PrePostRequisitesFields, CollectionField
from utils.decorators import login_required


class AddForm(SubmissionFormBase, ModelForm):

    title = forms.CharField(label=u"Title:",
                            widget=forms.TextInput(
                            attrs={"class": "text wide"}))

    url = forms.URLField(label=u"URL Pointer:", initial=u"http://",
                         widget=forms.TextInput(
                         attrs={"class": "text wide"}))

    abstract = forms.CharField(label=u"Abstract:",
                               widget=forms.Textarea(
                               attrs={"class": "text wide"}))

    institution = InstitutionField(label=u"Institution:",
                                  required=False,
                                  widget=forms.TextInput(
                                  attrs={"class": "text wide"}))

    collection = CollectionField(label=u"Collection:",
                                 required=False,
                                 widget=forms.TextInput(
                                 attrs={"class": "text wide"}))

    authors = AuthorsField(label=u"Authors:", required=False,
                           widget=forms.TextInput(
                           attrs={"class": "text wide"}))

    tech_requirements = forms.CharField(label=u"Notable Hard/Software:",
                                     required=False,
                                     widget=forms.Textarea(
                                     attrs={"class": "text wide"}))

    keywords = KeywordsField(label=u"Keywords")

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

    material_types = forms.ModelMultipleChoiceField(CourseMaterialType.objects.all(),
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

    license_custom_name = forms.CharField(label=u"License Name:",
                        required=False,
                        widget=forms.TextInput(attrs={"class": "text wide"}))

    license_custom_url = forms.URLField(label=u"License URL:",
                        required=False,
                        widget=forms.TextInput(attrs={"class": "text wide"}))

    license_description = forms.CharField(label=u"License Description:",
                        required=False,
                        help_text=u"Please enter any additional you might have about the license.",
                        widget=forms.Textarea(attrs={"class": "text wide"}))

    copyright_holder = forms.CharField(label=u"License / Copyright Holder:",
                        required=False,
                        help_text=u"Please enter the name of the person or organization owning or managing rights over the resource.",
                        widget=forms.TextInput(attrs={"class": "text wide"}))

    license = forms.Field(label=u"Conditions of Use", required=False)

    def clean_url(self):
        value = self.cleaned_data["url"]
        instance = getattr(self, "instance", None)
        qs = Course.objects.filter(url=value)
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
        model = Course
        fields = ["title", "url", "abstract", "institution", "collection",
                  "authors", "tech_requirements", "keywords", "general_subjects",
                  "grade_levels", "material_types", "media_formats", 
                  "languages", "geographic_relevance",
                  "license_type", "license_cc", "license_cc_old",
                  "license_custom_name", "license_custom_url", "license_description",
                  "copyright_holder", "license"]


class AddFormStaff(DerivedFields, PrePostRequisitesFields, AddForm):

    content_creation_date = forms.DateField(label=u"Content Creation Date:",
                                  input_formats=["%m/%d/%Y"],
                                  required=False,
                                  widget=forms.DateInput(
                                  attrs={"class": "text"},
                                  format="%m/%d/%Y"))

    course_or_module = forms.ChoiceField(choices=[(u"", u"-- select one --")] + list(COURSE_OR_MODULE),
                                         required=False,
                                         label=u"Full Course or Module",
                                         widget=forms.Select())

    ocw = forms.BooleanField(required=False, initial=False,
                                label=u"Is this part of an OpenCourseWare Collection?",
                                widget=forms.CheckboxInput())

    derived = forms.BooleanField(required=False, initial=False,
                                 label=u"Is this work modified from preexisiting/parent materials that are not your own?",
                                 widget=forms.CheckboxInput())

    derived_title = forms.CharField(required=False,
                                   label=u"Parent Title",
                                   widget=forms.TextInput(attrs={"class": "text"}))

    derived_url = forms.URLField(required=False,
                                   label=u"Parent URL",
                                   widget=forms.TextInput(attrs={"class": "text"}))

    derived_description = forms.CharField(required=False,
                                       label=u"Why did you decide to make changes to the parent item?",
                                       widget=forms.Textarea(attrs={"class": "text"}))

    derived_from = forms.Field(required=False)

    curriculum_standards = forms.CharField(required=False,
                       label=u"Curriculum Standards",
                       widget=forms.Textarea(attrs={"class": "text"}))

    has_prerequisites = forms.BooleanField(required=False, initial=False,
                         label=u"This course has suggested pre-requisites",
                                 widget=forms.CheckboxInput())

    prerequisite_1_title = forms.CharField(required=False,
                                   label=u"Title",
                                   widget=forms.TextInput(attrs={"class": "text"}))

    prerequisite_1_url = forms.URLField(required=False,
                                   label=u"URL",
                                   widget=forms.TextInput(attrs={"class": "text"}))

    prerequisite_1 = forms.Field(required=False)

    prerequisite_2_title = forms.CharField(required=False,
                                   label=u"Title",
                                   widget=forms.TextInput(attrs={"class": "text"}))

    prerequisite_2_url = forms.URLField(required=False,
                                   label=u"URL",
                                   widget=forms.TextInput(attrs={"class": "text"}))

    prerequisite_2 = forms.Field(required=False)

    has_postrequisites = forms.BooleanField(required=False, initial=False,
                         label=u"This course has suggested post-requisites",
                                 widget=forms.CheckboxInput())

    postrequisite_1_title = forms.CharField(required=False,
                                   label=u"Title",
                                   widget=forms.TextInput(attrs={"class": "text"}))

    postrequisite_1_url = forms.URLField(required=False,
                                   label=u"URL",
                                   widget=forms.TextInput(attrs={"class": "text"}))

    postrequisite_1 = forms.Field(required=False)

    postrequisite_2_title = forms.CharField(required=False,
                                   label=u"Title",
                                   widget=forms.TextInput(attrs={"class": "text"}))

    postrequisite_2_url = forms.URLField(required=False,
                                   label=u"URL",
                                   widget=forms.TextInput(attrs={"class": "text"}))

    postrequisite_2 = forms.Field(required=False)

    featured = forms.BooleanField(required=False, initial=False,
                         label=u"Marked as Top Ten Featured",
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

    cou_bucket = forms.ChoiceField(choices=COU_BUCKETS,
                                   label=u"Condition of Use Bucket",
                                   widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(AddForm, self).__init__(*args, **kwargs)
        self.fields["institution"].required = True
        self.set_initial_derived_data()
        self.set_initial_requisite_data()
        self.set_initial_license_data()

    class Meta:
        model = Course
        fields = ["title", "url", "abstract", "institution", "collection",
                  "content_creation_date", "authors",
                  "tech_requirements", "keywords", "general_subjects",
                  "grade_levels", "material_types", "media_formats", "languages",
                  "geographic_relevance", "course_or_module", "ocw", "derived",
                  "derived_title", "derived_url", "derived_description",
                  "derived_from", "curriculum_standards",
                  "has_prerequisites", "prerequisite_1_title", "prerequisite_1_url",
                  "prerequisite_1", "prerequisite_2_title", "prerequisite_2_url",
                  "prerequisite_2", "has_postrequisites", "postrequisite_1_title", "postrequisite_1_url",
                  "postrequisite_1", "postrequisite_2_title", "postrequisite_2_url",
                  "postrequisite_2",
                  "featured", "in_rss", "rss_description", "rss_timestamp",
                  "license_type", "license_cc", "license_cc_old",
                  "license_custom_name", "license_custom_url", "license_description",
                  "copyright_holder", "cou_bucket", "license"]


@login_required
def add(request, model=None):

    if request.user.is_staff:
        form_class = AddFormStaff
        template = "materials/forms/course/add-staff.html"
        page_title = u"Add Course Related Material"
    else:
        form_class = AddForm
        template = "materials/forms/course/add.html"
        page_title = u"Contribute Course Related Material"

    breadcrumbs = [
        {"url": model.get_parent_url(), "title": model._meta.verbose_name_plural},
        {"url": reverse("materials:courses:add"), "title": page_title}
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
            messages.success(request, u"New course was added.")
            return redirect(object)
        else:
            messages.error(request, u"Please correct the indicated errors.")
    else:
        form = form_class()

    return direct_to_template(request, template, locals())
