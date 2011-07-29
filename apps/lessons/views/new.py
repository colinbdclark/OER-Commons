from common.models import Language
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from lessons.models import Lesson
from utils.decorators import login_required
import datetime


class NewLesson(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        lesson, created = Lesson.objects.get_or_create(author=request.user,
                                                       is_new=True)
        student_levels = request.user.get_profile().educator_student_levels
        if created:
            if student_levels.exists():
                lesson.student_levels.add(*list(student_levels))
            lesson.language = Language.objects.get(slug="en")
            lesson.instruction_date = datetime.date.today() + datetime.timedelta(days=1)
            lesson.save()

        return redirect("lessons:edit_define", lesson_id=lesson.id)