from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from lessons.models import Lesson
from utils.decorators import login_required


class NewLesson(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        lesson, created = Lesson.objects.get_or_create(author=request.user,
                                                       is_new=True)
        return redirect("lessons:edit", lesson_id=lesson.id)