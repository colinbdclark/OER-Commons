from django import forms
from django.forms.models import ModelForm
from django.utils.html import strip_tags
from django.views.generic.simple import direct_to_template
from materials.models.common import GeneralSubject, GradeLevel, Language, \
    GeographicRelevance, MediaFormat, CC_LICENSE_URL_RE
from materials.models.course import Course, CourseMaterialType
from materials.models.material import PENDING_STATE
from materials.views.forms import SubmissionFormBase, AuthorsField, \
    KeywordsField, LanguagesField, LicenseTypeFieldRenderer, CC_OLD_LICENSES, \
    LICENSE_TYPES
from materials.views.forms.course import InstitutionField, CollectionField
from materials.views.forms.pyreadability import Readability, \
    ReadabilityException
from urllib2 import URLError
from utils.decorators import login_required
import re
import requests
from django.http import HttpResponse
import cjson


HTTP_USER_AGENT = "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.25 (KHTML, like Gecko) Chrome/12.0.706.0 Safari/534.25" 
VIDEO_URL_RE = re.compile(r"youtube.com|vimeo.com", re.I)
URL_RE = re.compile(r"(https?\://.*?)[\"\s]", re.I)



class URLForm(forms.Form):
    
    url = forms.URLField()
    
    def clean_url(self):
        url = self.cleaned_data['url']
        try:
            response = requests.get(url.encode("utf-8"),
                                    headers={"User-Agent": HTTP_USER_AGENT})
        except URLError:
            raise forms.ValidationError(u"Can't retrieve data from this URL. Please make sure that it is valid.")
        if response.error:
            raise forms.ValidationError(u"Can't retrieve data from this URL. Please make sure that it is valid.")
        url = response.url
        if Course.objects.filter(url=url).exists():
            raise forms.ValidationError(u"A resource with this URL is registered already.")
        self.content = response.content
        return url
            

def fetch_data_from_url(url, content):
    data = {}
    data["url"] = url
    try:
        readable = Readability(url, content)
        data["title"] = readable.get_article_title()
        data["abstract"] = strip_tags(readable.get_article_text()).strip()
    except ReadabilityException:
        pass
    
    if VIDEO_URL_RE.search(url):
        data["media_formats"] = MediaFormat.objects.filter(name="Video")
        
    urls = URL_RE.findall(content)
    OLD_CC_LICENCES = [l[0] for l in CC_OLD_LICENSES[1:]]
    
    for url in urls:
        if CC_LICENSE_URL_RE.match(url):
            url = url.lower()
            if url in OLD_CC_LICENCES:
                data["license_type"] = "cc-old"
                data["license_cc_old"] = url
            else:
                data["license_type"] = "cc"
                data["license_cc"] = url
        
    return data


class SubmissionForm(SubmissionFormBase, ModelForm):    

    url = forms.URLField(widget=forms.HiddenInput())
    
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "wide"}))
    
    abstract = forms.CharField(widget=forms.Textarea(attrs={"class": "wide"}))
    
    institution = InstitutionField(required=False,
                                  widget=forms.TextInput(
                                  attrs={"class": "wide"}))

    collection = CollectionField(required=False,
                                 widget=forms.TextInput(
                                 attrs={"class": "wide"}))

    authors = AuthorsField(required=False,
                           widget=forms.TextInput(
                           attrs={"class": "wide"}))

    keywords = KeywordsField(label=u"Keywords")

    tech_requirements = forms.CharField(label=u"Technical requirements",
                                     required=False,
                                     widget=forms.Textarea(
                                     attrs={"class": "wide"}))

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
        self.fields["collection"].initial = u"Individual Authors"

    class Meta:
        model = Course
        fields = ["title", "url", "abstract", "institution", "collection",
                  "authors", "keywords", "general_subjects",
                  "grade_levels", "material_types", "media_formats", 
                  "languages", "geographic_relevance",
                  "license_type", "license_cc", "license_cc_old",
                  "license_custom_name", "license_custom_url", "license_description",
                  "copyright_holder", "license"]


@login_required
def iframe_submission(request):
    
    if request.method == "GET":
        
        url_form = URLForm(request.REQUEST)
        
        if url_form.is_valid():
            url = url_form.cleaned_data["url"]
            resource_content = url_form.content
            data = fetch_data_from_url(url, resource_content)
            form = SubmissionForm(initial=data)
            return direct_to_template(request, "materials/forms/iframe-submission.html",
                                      dict(form=form))
            
        else:
            return direct_to_template(request, "materials/forms/iframe-submission.html",
                                  dict(url_error = url_form._errors["url"]))
        
        
    if request.method == "POST":
        
        form = SubmissionForm(request.POST)
        
        if form.is_valid():
            object = form.save(commit=False)
            object.creator = request.user
            object.workflow_state = PENDING_STATE
            object.save()
            form.save_m2m()
            return HttpResponse(cjson.encode(dict(status="success",
                                                  message=u"You have successfully submitted %s to OER Commons." % object.title)),
                                content_type="application/json")
        else:
            return HttpResponse(cjson.encode(dict(status="error",
                                                  message=u"Please correct the indicated errors.")),
                                content_type="application/json")
        