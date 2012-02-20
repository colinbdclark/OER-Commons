from annoying.decorators import JsonResponse
from authoring.models import Image, Document, Embed, AuthoredMaterial
from cache_utils.decorators import cached
from django.core.files import File
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.defaultfilters import filesizeformat
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django import forms
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin, ProcessFormView
from sorl.thumbnail.shortcuts import get_thumbnail
from utils.decorators import login_required
import json
import os
import random
import re
import requests
import string
import urlparse


IMAGE_CONTENT_TYPE_RE = re.compile(r"^image/(png|p?jpeg|gif)", re.I)
MAX_IMAGE_SIZE = 10485760   # 10 MB

DOCUMENT_CONTENT_TYPE_RE = re.compile(r"^(?:application/.*(?:ms-?word|ms-excel|ms-powepoint|openxmlformats-officedocument|oasis\.opendocument|pdf))", re.I)
MAX_DOCUMENT_SIZE = 104857600   # 100 MB

IMAGE_FILENAME_RE = re.compile("^.+\.(?:png|gif|jpg|jpeg)$", re.I)


class MediaUploadForm(forms.Form):

    file = forms.FileField(required=False)
    url = forms.URLField(required=False)

    error_messages = dict(
        empty_fields=u"Please upload a file or enter an URL.",
        invalid_url=u"Invalid URL.",
        large_image=u"The file is too large. "
            u"Max allowed image size is %s." % filesizeformat(MAX_IMAGE_SIZE),
        large_document=u"The file is too large. "
            u"Max allowed file size is %s." % filesizeformat(MAX_DOCUMENT_SIZE)
    )

    def __init__(self, *args, **kwargs):
        self.media_type = None
        self.embed = None
        super(MediaUploadForm, self).__init__(*args, **kwargs)

    @cached(3600 * 24)
    def tiny_url_services(self):
        return json.loads(requests.get("http://untiny.me/api/1.0/services/?format=json").text).values()

    def clean(self):
        url = self.cleaned_data.get("url")
        file = self.cleaned_data.get("file")

        if not file and not url:
            raise forms.ValidationError(self.error_messages["empty_fields"])

        elif url and not file:
            hostname = urlparse.urlparse(url).hostname
            if hostname in self.tiny_url_services():
                url = json.loads(requests.get(
                    "http://untiny.me/api/1.0/extract",
                    params=dict(url=url, format="json")
                ).text)["org_url"]
            response = requests.head(url)
            if response.error or response.status_code != 200 or "content-type" not in response.headers:
                raise forms.ValidationError(self.error_messages["invalid_url"])
            content_type = response.headers.get("content-type")

            if IMAGE_CONTENT_TYPE_RE.match(content_type):
                # Download the image
                self.media_type = "image"
                content_length = response.headers.get("content-length")
                if not content_type:
                    raise forms.ValidationError(self.error_messages["invalid_url"])
                content_length = int(content_length)
                if content_length and content_length > MAX_IMAGE_SIZE:
                    raise forms.ValidationError(self.error_messages["large_image"])
                response = requests.get(url)
                path = urlparse.urlparse(url).path
                filename = path.split("/")[-1]
                if not IMAGE_FILENAME_RE.match(filename):
                    extension = content_type.split("/")[-1]
                    if extension in ("pjpeg", "jpeg"):
                        extension = "jpg"
                    #noinspection PyUnusedLocal
                    filename = ''.join(
                        random.choice(string.ascii_lowercase + string.digits) for x in xrange(10)
                    ) + extension
                file = File(response.raw, name=filename)
                file._size = content_length
                self.cleaned_data["file"] = file

            elif DOCUMENT_CONTENT_TYPE_RE.match(content_type):
                self.media_type = "document"

            else:
                self.embed = Embed.get_for_url(url)

        else:
            content_type = file.content_type
            size = file._size
            if IMAGE_CONTENT_TYPE_RE.match(content_type):
                if size > MAX_IMAGE_SIZE:
                    raise forms.ValidationError(self.error_messages["large_image"])
                # Validate if it's an image
                forms.ImageField(
                    error_messages=dict(
                        invalid_image=u"The uploaded file is not an image."
                    )
                ).to_python(file)
                self.media_type = "image"

            elif DOCUMENT_CONTENT_TYPE_RE.match(content_type):
                if size > MAX_DOCUMENT_SIZE:
                    raise forms.ValidationError(self.error_messages["large_document"])
                self.media_type = "document"

        return self.cleaned_data


class MediaUpload(SingleObjectMixin, FormMixin, ProcessFormView):

    model = AuthoredMaterial
    form_class = MediaUploadForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        #noinspection PyUnresolvedReferences
        return super(MediaUpload, self).dispatch(request, *args, **kwargs)

    def json_response(self, data):
        # We have to use "text/plain" here because it will be parsed by jquery.fileupload plugin
        return HttpResponse(json.dumps(data), content_type="text/plain")

    def form_valid(self, form):
        object = self.get_object()
        if form.media_type == "image":
            image = Image(material=object, image=form.cleaned_data["file"])
            image.save()
            response = dict(
                status="success",
                type="image",
                thumbnail=get_thumbnail(image.image, "148x110", crop="center", upscale=False).url,
                url=get_thumbnail(image.image, "650x650", upscale=False).url,
                original_url=image.image.url,
                id=image.id,
                name=image.image.name.split(os.path.sep)[-1],
            )
        elif form.media_type == "document":
            if form.cleaned_data["file"]:
                document = Document(material=object, file=form.cleaned_data["file"])
                document.save()
                response = dict(
                    status="success",
                    type="document",
                    name=document.file.name.split(os.path.sep)[-1],
                    url=document.file.url,
                )
            else:
                response = dict(
                    status="success",
                    type="document",
                    name="",
                    url=form.cleaned_data["url"],
                )
        elif form.embed and form.embed.type == "video":
            video = form.embed
            response = dict(
                type="video",
                url=video.url,
                title=video.title or u"",
                thumbnail=video.thumbnail or u""
            )
        else:
            response = dict(
                status="success",
                type="link",
                url=form.cleaned_data["url"],
            )
        return self.json_response(response)

    def form_invalid(self, form):
        return self.json_response(dict(status="error", message=form._errors["__all__"][0]))


class LoadEmbed(View):

    #noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        url = request.POST.get("url")
        if not url:
            return HttpResponseBadRequest("Missing 'url' parameter.")

        embed = Embed.get_for_url(url)
        if not embed:
            return HttpResponseBadRequest("Can't load embed from given URL.")

        html = ""

        if embed.type == "video":
            html = embed.html

        return JsonResponse(dict(
            html=html,
            url=embed.embed_url,
        ))
