from annoying.decorators import JsonResponse
from django import forms
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.generic import View
from lessons.views import LessonViewMixin
from sorl.thumbnail.shortcuts import delete
from utils.decorators import login_required
import json
import time


class LessonImageForm(forms.Form):

    file = forms.FileField()


class LessonImage(LessonViewMixin, View):

    restrict_to_owner = True
    action = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LessonImage, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.action == "upload":
            form = LessonImageForm(request.POST, request.FILES)
            response = dict(status="error", message=u"")
            if form.is_valid():
                if self.lesson.image:
                    delete(self.lesson.image)
                image = form.cleaned_data["file"]
                if image.content_type == "image/jpeg":
                    extension = ".jpg"
                elif image.content_type == "image/png":
                    extension = ".png"
                elif image.content_type == "image/gif":
                    extension = ".gif"
                else:
                    extension = ""
                filename = "%i%s" % (self.lesson.id, extension)
                self.lesson.image.save(filename, image)
                response["status"] = "success"
                response["message"] = u"Your picture is saved."
                response["url"] = self.lesson.get_thumbnail().url + "?" + str(int(time.time()))
            else:
                response["message"] = form.errors["file"][0]
            # We don't use application/json content type here because IE misinterprets it.
            return HttpResponse(json.dumps(response))
        elif self.action == "remove":
            if self.lesson.image:
                delete(self.lesson.image)
                self.lesson.image = None
                self.lesson.save()
            return JsonResponse(dict(status="success",
                                     message=u"Image was removed."))
        raise Http404()
