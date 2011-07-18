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
        student_levels = request.user.get_profile().educator_student_levels
        if created and student_levels.exists():
            lesson.student_levels.add(*list(student_levels))

        return redirect("lessons:edit", lesson_id=lesson.id)