from django import forms
from django.forms.models import ModelForm
from django.http import HttpResponse, Http404
from materials.models.common import GeneralSubject, GradeLevel, Language, \
    GeographicRelevance, MediaFormat, Collection
from materials.models.course import Course, CourseMaterialType
from materials.models.material import PENDING_STATE
from materials.views.forms import SubmissionFormBase, AuthorsField, \
    KeywordsField, LanguagesField, LicenseTypeFieldRenderer, CC_OLD_LICENSES, \
    LICENSE_TYPES
from materials.views.forms.course import InstitutionField
from utils.decorators import login_required
import cjson


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
                        widget=forms.TextInput(attrs={"class": "wide"}))

    license_custom_url = forms.URLField(label=u"License URL:",
                        required=False,
                        widget=forms.TextInput(attrs={"class": "wide"}))

    license_description = forms.CharField(label=u"License Description:",
                        required=False,
                        help_text=u"Please enter any additional you might have about the license.",
                        widget=forms.Textarea(attrs={"class": "wide"}))

    copyright_holder = forms.CharField(label=u"License / Copyright Holder:",
                        required=False,
                        help_text=u"Please enter the name of the person or organization owning or managing rights over the resource.",
                        widget=forms.TextInput(attrs={"class": "wide"}))

    license = forms.Field(label=u"Conditions of Use", required=False)

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
                  "license_custom_name", "license_custom_url", "license_description",
                  "copyright_holder", "license"]


@login_required
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
            return HttpResponse(cjson.encode(dict(status="success",
                                                  message=u"You have successfully submitted %s to OER Commons." % object.title)),
                                content_type="application/json")
        else:
            return HttpResponse(cjson.encode(dict(status="error",
                                                  message=u"Please correct the indicated errors.")),
                                content_type="application/json")

    raise Http404()