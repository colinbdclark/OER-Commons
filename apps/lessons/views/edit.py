from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from lessons.views import LessonViewMixin
from sentry.views import login_required
from utils.views import OERViewMixin


class EditLesson(LessonViewMixin, OERViewMixin, TemplateView):

    template_name = "lessons/authoring/edit-lesson.html"

    def get_page_title(self):
        if self.lesson.title:
            return u'Edit "%s"' % self.lesson.title
        return u"Edit Lesson"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        result = super(EditLesson, self).dispatch(request, *args, **kwargs)
        if self.lesson.author != self.request.user:
            return HttpResponseForbidden()
        return result

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()

    def get_context_data(self, *args, **kwargs):
        data = super(EditLesson, self).get_context_data(*args, **kwargs)
        return data