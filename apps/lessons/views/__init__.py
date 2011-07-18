from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from lessons.models import Lesson


class LessonViewMixin(object):

    restrict_to_owner = False

    def dispatch(self, request, *args, **kwargs):
        self.lesson = get_object_or_404(Lesson, id=int(kwargs["lesson_id"]))
        user = request.user
        if self.restrict_to_owner and user != self.lesson.author:
            return HttpResponseForbidden()
        return super(LessonViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        data = super(LessonViewMixin, self).get_context_data(*args, **kwargs) or {}
        data["lesson"] = self.lesson
        return data