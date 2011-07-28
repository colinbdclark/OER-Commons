from annoying.decorators import ajax_request
from common.models import GeneralSubject, Language
from django import forms
from django.forms.models import ModelForm
from django.http import Http404
from django.template.loader import render_to_string
from materials.models.common import  GradeLevel,\
    GeographicRelevance, MediaFormat, Collection, Keyword
from materials.models.course import Course, CourseMaterialType
from materials.models.material import PENDING_STATE
from materials.views.forms import SubmissionFormBase, AuthorsField, \
    LanguagesField, LicenseTypeFieldRenderer, CC_OLD_LICENSES, LICENSE_TYPES
from materials.views.forms.course import InstitutionField
from utils.decorators import login_required
from utils.forms import AutocompleteListField


class SubmissionForm(SubmissionFormBase, ModelForm):

    url = forms.URLField(widget=forms.HiddenInput())

    title = forms.CharField(widget=forms.TextInput(attrs={"class": "wide"}))

    abstract = forms.CharField(widget=forms.Textarea(attrs={"class": "wide"}))

    institution = InstitutionField(required=False,
                                  widget=forms.TextInput(
                                  attrs={"class": "wide"}))

    authors = AuthorsField(required=False,
                           widget=forms.TextInput(
                           attrs={"class": "wide"}))

    keywords = AutocompleteListField(model=Keyword, label=u"Keywords")

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

    license_custom_url = forms.URLField(label=u"License URL:",
                        required=False,
                        widget=forms.TextInput(attrs={"class": "wide"}))

    license_description = forms.CharField(label=u"License Description:",
                        required=False,
                        help_text=u"Please enter any additional information you might have about the license.",
                        widget=forms.Textarea(attrs={"class": "wide"}))

    copyright_holder = forms.CharField(label=u"License / Copyright Holder:",
                        required=False,
                        help_text=u"Please enter the name of the person or organization owning or managing rights over the resource.",
                        widget=forms.TextInput(attrs={"class": "wide"}))

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
        super(SubmissionForm, self).__init__(*args, **kwargs)
        self.set_initial_license_data()

    class Meta:
        model = Course
        fields = ["title", "url", "abstract", "institution",
                  "authors", "keywords", "general_subjects",
                  "grade_levels", "material_types", "media_formats",
                  "languages", "geographic_relevance",
                  "license_type", "license_cc", "license_cc_old",
                  "license_custom_url", "license_description",
                  "copyright_holder", "license"]


@login_required
@ajax_request
def submit(request):

    if request.method == "POST":

        form = SubmissionForm(request.POST)

        if form.is_valid():
            object = form.save(commit=False)
            object.creator = request.user
            object.workflow_state = PENDING_STATE
            object.collection = Collection.objects.get_or_create(name=u"Individual Authors")[0]
            object.save()
            form.save_m2m()
            total_items_submitted = Course.objects.filter(creator=request.user).count()
            return dict(status="success",
                        message=render_to_string("materials/iframe-submission/success-message.html",
                                                 dict(title=object.title,
                                                      total_items_submitted=total_items_submitted))
                                )
        else:
            return dict(status="error",
                        message=u"Please correct the indicated errors.")

    raise Http404()
