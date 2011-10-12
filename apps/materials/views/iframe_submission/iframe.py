from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from django.utils.text import unescape_entities, truncate_words
from django.views.generic.simple import direct_to_template
from materials.models.common import MediaFormat, CC_LICENSE_URL_RE
from materials.models.course import Course
from materials.views.forms import CC_OLD_LICENSES
from materials.views.iframe_submission.pyreadability import Readability, \
    ReadabilityException
from materials.views.iframe_submission.submission_form import SubmissionForm
from reviews.views import ReviewForm
from urllib2 import URLError
from users.views.login import LoginForm
from utils import reduce_whitespace
import re
import requests


HTTP_USER_AGENT = "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.25 (KHTML, like Gecko) Chrome/12.0.706.0 Safari/534.25"
VIDEO_URL_RE = re.compile(r"youtube.com|vimeo.com", re.I)
URL_RE = re.compile(r"(https?://.*?)[\"\s]", re.I)



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
            self.instance = Course.objects.get(url=url)
            raise forms.ValidationError(u"A resource with this URL is registered already.")
        self.content = response.content
        return url


def fetch_data_from_url(url, content):
    data = {"url": url}
    try:
        readable = Readability(url, content)
        data["title"] = reduce_whitespace(unescape_entities(readable.get_article_title()))
        # Try to get abstract from meta description:
        abstract = reduce_whitespace(unescape_entities(strip_tags(readable.get_meta_description()).strip()))
        if not abstract:
            abstract = reduce_whitespace(unescape_entities(strip_tags(readable.get_article_text()).strip()))
        abstract = truncate_words(abstract, 200)
        data["abstract"] = abstract
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


def iframe(request):
    return direct_to_template(request, "materials/iframe-submission/iframe.html")


def dispatch_iframe(request):

    if not request.user.is_authenticated():
        return direct_to_template(request, "materials/iframe-submission/login.html",
                                  dict(form=LoginForm()))

    url_form = URLForm(request.REQUEST)

    if url_form.is_valid():
        url = url_form.cleaned_data["url"]
        resource_content = url_form.content
        data = fetch_data_from_url(url, resource_content)
        form = SubmissionForm(initial=data)
        return direct_to_template(request, "materials/iframe-submission/submission-form.html",
                                  dict(form=form))

    elif hasattr(url_form, "instance"):
        item = url_form.instance
        content_type = ContentType.objects.get_for_model(item)

        item.identifier = "%s.%s.%i" % (content_type.app_label,
                                        content_type.model,
                                        item.id)


        user = request.user
        user_tags = item.tags.filter(user=user).order_by("slug")
        item_tags = item.tags.all()
        if user_tags:
            item_tags = item_tags.exclude(id__in=user_tags.values_list("id", flat=True))

        review_item_url = reverse("materials:%s:add_review" % item.namespace,
                               kwargs=dict(slug=item.slug))

        review_form = ReviewForm(instance=item,
                                 user=user)

        return direct_to_template(request, "materials/iframe-submission/existing-resource.html",
                                  dict(item=item,
                                       user_tags=user_tags,
                                       item_tags=item_tags,
                                       app_label=content_type.app_label,
                                       model=content_type.model,
                                       review_item_url=review_item_url,
                                       review_form=review_form,
                                       ))
    else:
        return direct_to_template(
            request,
            "materials/iframe-submission/invalid-url.html",
            dict(form=url_form),
        )
