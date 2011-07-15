from django.shortcuts import get_object_or_404
from lessons.models import Lesson


class LessonViewMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.lesson = get_object_or_404(Lesson, id=int(kwargs["lesson_id"]))
        return super(LessonViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        data = super(LessonViewMixin, self).get_context_data(*args, **kwargs) or {}
        data["lesson"] = self.lesson
        return data