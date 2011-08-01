from annoying.decorators import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from lessons.models import Chapter
from lessons.views import LessonViewMixin
from utils.decorators import login_required
from utils.views import OERViewMixin


class Outline(LessonViewMixin, OERViewMixin, TemplateView):

    template_name = "lessons/authoring/outline.html"
    restrict_to_owner = True

    page_title = u"Outline"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(Outline, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not self.lesson.chapters.all().exists():
            Chapter.objects.create(lesson=self.lesson)
        return super(Outline, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "add-chapter" in request.POST:
            chapter = Chapter.objects.create(lesson=self.lesson)
            return JsonResponse(dict(status="success", id=chapter.id))

        elif "remove-chapter" in request.POST:
            try:
                Chapter.objects.get(lesson=self.lesson, id=int(request.POST["id"])).delete()
            except (ValueError, TypeError, KeyError, Chapter.DoesNotExist):
                return JsonResponse(dict(status="error"))
            return JsonResponse(dict(status="success"))

        return self.get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        data = super(Outline, self).get_context_data(*args, **kwargs)
        data["step_number"] = 3
        return data
